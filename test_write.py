from pyairtable import Api
import config

api = Api(config.AIRTABLE_API_KEY)
table = api.table(config.AIRTABLE_BASE_ID, config.SESSIONS_TABLE)

try:
    result = table.create({
        config.FIELD_CHAT_ID: "test123",
        config.FIELD_CURRENT_STEP: "1_1_r",
        config.FIELD_LANGUAGE: "rus"
    })
    print("SUCCESS! Record created:", result["id"])
except Exception as e:
    print("ERROR:", e)
