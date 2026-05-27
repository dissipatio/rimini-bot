import os
from dotenv import load_dotenv

load_dotenv()  # reads your local .env file automatically

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
SESSIONS_TABLE = os.environ.get("SESSIONS_TABLE", "tblVuemWbrbhr1nTz")
BOT_TABLE = os.environ.get("BOT_TABLE", "tblJFjNJfR2Zt1wiT")
FIELD_CHAT_ID = os.environ.get("FIELD_CHAT_ID", "chat_id")
FIELD_CURRENT_STEP = os.environ.get("FIELD_CURRENT_STEP", "current_step")
FIELD_LANGUAGE = os.environ.get("FIELD_LANGUAGE", "language")

FIRST_STEP = {
    "rus": "1_1_r",
    "eng": "1_1_r",
    "ita": "1_1_r",
}