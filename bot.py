import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from airtable_helper import get_session, upsert_session, get_step
import config

logging.basicConfig(level=logging.INFO)


def get_yandex_direct_url(public_url):
    """Convert Yandex Disk sharing link to direct download URL"""
    api_url = f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_url}'
    r = requests.get(api_url)
    data = r.json()
    return data.get("href")


async def send_step(chat_id, step_id, context):
    step = get_step(step_id)
    if not step:
        await context.bot.send_message(chat_id=chat_id, text="Step not found.")
        return
    fields = step["fields"]
    text = fields.get("TXT_rus", "...")
    step_category = fields.get("step_category", "")
    button_options = fields.get("button_options", "")
    next_step = fields.get("next_step_rus", "")
    images_linked = fields.get("images_linked", "")
    files_linked = fields.get("files_linked", "")

    print(f"DEBUG send_step: id={step_id} category={step_category} buttons={button_options} next={next_step}")

    # Build reply markup based on step type
    reply_markup = None

    if step_category == "question" and button_options and "_r" in button_options:
        button_ids = [b.strip() for b in button_options.split(",")]
        keyboard = []
        for btn_id in button_ids:
            btn_step = get_step(btn_id)
            if btn_step:
                btn_text = btn_step["fields"].get("TXT_rus", btn_id)
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=btn_id)])
        reply_markup = InlineKeyboardMarkup(keyboard)

    elif step_category == "info":
        advance_to = button_options.strip() if button_options else next_step
        if advance_to:
            next_step_data = get_step(advance_to)
            if next_step_data:
                btn_text = next_step_data["fields"].get("TXT_rus", "Далее ➡️")
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, callback_data=advance_to)]])

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

    # Send text with reply markup
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode="HTML")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: handle_message called!")
    chat_id = update.message.chat.id
    user_input = update.message.text.strip()
    print(f"DEBUG: chat_id={chat_id} input={user_input}")

    if user_input == "/start":
        upsert_session(chat_id, "1_1_r")
        await send_step(chat_id, "1_1_r", context)
        return

    session = get_session(chat_id)
    if not session:
        await context.bot.send_message(chat_id=chat_id, text="Please send /start to begin.")
        return

    record_id = session["id"]
    current_step_id = session["fields"].get(config.FIELD_CURRENT_STEP)
    print(f"DEBUG: current_step={current_step_id}")

    current_step = get_step(current_step_id)
    if not current_step:
        print("DEBUG: step not found!")
        return

    fields = current_step["fields"]
    step_category = fields.get("step_category", "")
    correct_answers = fields.get("correct_answers", "")
    correct_next = fields.get("correct_next_step", "")
    wrong_next = fields.get("wrong_next_step", "")
    button_options = fields.get("button_options", "")

    print(f"DEBUG: category={step_category} correct_answers={correct_answers} correct_next={correct_next} wrong_next={wrong_next}")

    if step_category in ("question", "start") and not button_options:
        if user_input.lower() in [a.strip().lower() for a in correct_answers.split(",")]:
            print("DEBUG: correct answer!")
            upsert_session(chat_id, correct_next, record_id)
            await send_step(chat_id, correct_next, context)
        else:
            print("DEBUG: wrong answer!")
            if wrong_next:
                await send_step(chat_id, wrong_next, context)
    elif step_category in ("info", "answer", "help", "error"):
        next_step = fields.get("next_step_rus", "")
        print(f"DEBUG: auto-advancing to next_step={next_step}")
        if next_step:
            upsert_session(chat_id, next_step, record_id)
            await send_step(chat_id, next_step, context)
    else:
        next_step = fields.get("next_step_rus", "")
        print(f"DEBUG: next_step={next_step}")
        if next_step:
            upsert_session(chat_id, next_step, record_id)
            await send_step(chat_id, next_step, context)


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: handle_button called!")
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    button_step_id = query.data
    print(f"DEBUG: button pressed: {button_step_id}")

    button_step = get_step(button_step_id)
    if not button_step:
        print("DEBUG: button step not found!")
        return

    fields = button_step["fields"]
    step_category = fields.get("step_category", "")
    next_step = fields.get("next_step_rus", "")

    print(f"DEBUG: button category={step_category} next_step={next_step}")

    session = get_session(chat_id)
    record_id = session["id"] if session else None

    if next_step:
        upsert_session(chat_id, next_step, record_id)
        await send_step(chat_id, next_step, context)
    else:
        upsert_session(chat_id, button_step_id, record_id)
        await send_step(chat_id, button_step_id, context)


app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))
app.add_handler(CallbackQueryHandler(handle_button))

print("Bot is running...")
app.run_polling()