import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8050209143:AAEnYueWC6mhSUYV1CPvly2cPIy6Lw-QFsA")
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "patvBjUGIlZOMCahU.2b6888a08beba9e7108df6309ea283f25cc4e0586d0f93374481b06d8d9854cf")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "appzKuV9PSlgNXy9c")
SESSIONS_TABLE = os.environ.get("SESSIONS_TABLE", "tblVuemWbrbhr1nTz")
BOT_TABLE = os.environ.get("BOT_TABLE", "tblJFjNJfR2Zt1wiT")
FIELD_CHAT_ID = os.environ.get("FIELD_CHAT_ID", "chat_id")
FIELD_CURRENT_STEP = os.environ.get("FIELD_CURRENT_STEP", "current_step")
FIELD_LANGUAGE = os.environ.get("FIELD_LANGUAGE", "language")

FFIRST_STEP = {
    "rus": "1_1_r",
    "eng": "1_1_r",
    "ita": "1_1_r",
}