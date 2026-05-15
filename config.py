import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8050209143:AAHuFLyYIlJvRp4G0Vt3dht4EK3F4Jt85Z0")
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "patvBjUGIlZOMCahU.ead6ff52146fcb02a3948d0c39742ca52029724f7096f9abaa53ebae1f6a6afa")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "appzKuV9PSlgNXy9c")
SESSIONS_TABLE = os.environ.get("SESSIONS_TABLE", "tblVuemWbrbhr1nTz")
BOT_TABLE = os.environ.get("BOT_TABLE", "tblJFjNJfR2Zt1wiT")
FIELD_CHAT_ID = os.environ.get("FIELD_CHAT_ID", "chat_id")
FIELD_CURRENT_STEP = os.environ.get("FIELD_CURRENT_STEP", "current_step")
FIELD_LANGUAGE = os.environ.get("FIELD_LANGUAGE", "language")
