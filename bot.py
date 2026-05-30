import logging
import os
import time
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from airtable_helper import get_session, upsert_session, get_step, get_lang_fields
import config

logging.basicConfig(level=logging.INFO)

# Navigation between steps (next_step_*, correct_next_step, wrong_next_step)
# is language-independent — there's only one quest graph. Text per language
# is selected via get_lang_fields(), but the wiring between steps is universal.
NAV_NEXT_FIELD = "next_step_rus"


def get_yandex_direct_url(public_url):
    """Convert Yandex Disk sharing link to direct download URL"""
    api_url = f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_url}'
    r = requests.get(api_url)
    data = r.json()
    return data.get("href")


async def send_step(chat_id, step_id, context, language="rus"):
    step = get_step(step_id, language)
    if not step:
        await context.bot.send_message(chat_id=chat_id, text="Step not found.")
        return

    lf = get_lang_fields(language)
    fields = step["fields"]
    text = fields.get(lf["txt"], "...")
    button_options = fields.get(lf["buttons"], "")
    effect_id = fields.get("effect_id") or None
    images_linked = fields.get(lf.get("images", "images_linked"), "")
    files_linked = fields.get(lf.get("files", "files_linked"), "")
    step_category = fields.get("step_category", "")
    next_step_auto = fields.get(NAV_NEXT_FIELD, "")

    # Send image if present
    if images_linked:
        try:
            direct_url = get_yandex_direct_url(images_linked)
            if direct_url:
                await context.bot.send_photo(chat_id=chat_id, photo=direct_url)
        except Exception as e:
            print(f"DEBUG: image error: {e}")

    # Send file if present
    if files_linked:
        try:
            direct_url = get_yandex_direct_url(files_linked)
            if direct_url:
                await context.bot.send_document(chat_id=chat_id, document=direct_url)
        except Exception as e:
            print(f"DEBUG: file error: {e}")

    # Send text with buttons or plain
    if button_options:
        button_ids = [b.strip() for b in button_options.split(",")]
        keyboard = []
        for btn_id in button_ids:
            btn_step = get_step(btn_id, language)
            if btn_step:
                btn_text = btn_step["fields"].get(lf["txt"], btn_id)
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"{language}|{btn_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode="HTML", message_effect_id=effect_id)
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", message_effect_id=effect_id)

    # Auto-advance for info_auto steps — wait 5 seconds then send next step automatically
    if step_category == "info_auto" and next_step_auto:
        await asyncio.sleep(5)
        session = get_session(chat_id)
        record_id = session["id"] if session else None
        upsert_session(chat_id, next_step_auto, record_id)
        await send_step(chat_id, next_step_auto, context, language)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_input = update.message.text.strip()

    print(f"DEBUG message: chat_id={chat_id}, text={user_input}")

    if user_input == "/start":
        keyboard = [
            [InlineKeyboardButton("ENG English",    callback_data="lang|eng")],
            [InlineKeyboardButton("ITA Italiano",   callback_data="lang|ita")],
            [InlineKeyboardButton("UKR Українська", callback_data="lang|ukr")],
            [InlineKeyboardButton("DEU Deutsch",    callback_data="lang|deu")],
            [InlineKeyboardButton("RUS Русский",    callback_data="lang|rus")],
            [InlineKeyboardButton("FRA Français",    callback_data="lang|fra")],
            [InlineKeyboardButton("HUN Magyar",    callback_data="lang|hun")],
]
        await update.message.reply_text(
            "🌍 Choose your language",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    try:
        session = get_session(chat_id)
        if not session:
            await context.bot.send_message(chat_id=chat_id, text="Send /start to begin.")
            return

        language = session["fields"].get(config.FIELD_LANGUAGE, "rus")
        lf = get_lang_fields(language)
        record_id = session["id"]
        current_step_id = session["fields"].get(config.FIELD_CURRENT_STEP)
        print(f"DEBUG message: language={language}, current_step={current_step_id}")

        current_step = get_step(current_step_id, language)
        if not current_step:
            print(f"DEBUG: step {current_step_id} not found for language {language}")
            return

        fields = current_step["fields"]
        step_category = fields.get("step_category", "")

        # Pick the language-specific correct-answers column, with fallback
        answers_field = lf.get("answers", "correct_answers")
        correct_answers = fields.get(answers_field, "")
        # Fallback for language-neutral answers (numbers, Latin words, emoji-only)
        if not correct_answers:
            correct_answers = fields.get("correct_answers", "")

        correct_next = fields.get("correct_next_step", "")
        wrong_next = fields.get("wrong_next_step", "")

        print(f"DEBUG message: category={step_category}, answers_field={answers_field}, correct_answers={correct_answers}")

        if step_category == "question" and not fields.get(lf["buttons"]):
            if user_input.lower() in [a.strip().lower() for a in correct_answers.split(",") if a.strip()]:
                upsert_session(chat_id, correct_next, record_id)
                await send_step(chat_id, correct_next, context, language)
            else:
                if wrong_next:
                    await send_step(chat_id, wrong_next, context, language)
        else:
            # Universal navigation — same step graph across all languages
            # info_auto steps ignore user input while auto-chaining is in progress
            next_step = fields.get(NAV_NEXT_FIELD, "")
            if next_step and step_category != "info_auto":
                upsert_session(chat_id, next_step, record_id)
                await send_step(chat_id, next_step, context, language)

    except Exception as e:
        print(f"ERROR in handle_message: {e}")
        import traceback
        traceback.print_exc()


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    data = query.data

    print(f"DEBUG button: data={data}, chat_id={chat_id}")

    if data.startswith("lang|"):
        language = data.split("|")[1]
        first_step = config.FIRST_STEP.get(language, "1_1_r")
        print(f"DEBUG lang selected: {language}, first_step={first_step}")
        session = get_session(chat_id)
        record_id = session["id"] if session else None
        upsert_session(chat_id, first_step, record_id, language=language)
        await send_step(chat_id, first_step, context, language)
        return

    if "|" in data:
        language, button_step_id = data.split("|", 1)
    else:
        session = get_session(chat_id)
        language = session["fields"].get(config.FIELD_LANGUAGE, "rus") if session else "rus"
        button_step_id = data

    button_step = get_step(button_step_id, language)
    if not button_step:
        return

    fields = button_step["fields"]
    # Universal navigation — same step graph across all languages
    next_step = fields.get(NAV_NEXT_FIELD, "")

    session = get_session(chat_id)
    record_id = session["id"] if session else None

    if next_step:
        upsert_session(chat_id, next_step, record_id)
        await send_step(chat_id, next_step, context, language)
    else:
        upsert_session(chat_id, button_step_id, record_id)
        await send_step(chat_id, button_step_id, context, language)


time.sleep(2)

app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))
app.add_handler(CallbackQueryHandler(handle_button))

print("Bot is running...")

PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if WEBHOOK_URL:
    print(f"Starting webhook on port {PORT}, url={WEBHOOK_URL}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )
else:
    print("Starting polling...")
    app.run_polling(drop_pending_updates=True)
