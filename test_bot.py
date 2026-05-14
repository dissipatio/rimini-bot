from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import config

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"GOT MESSAGE: {update.message.text}")
    await update.message.reply_text("I got your message!")

app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, echo))
print("Test bot running...")
app.run_polling()
