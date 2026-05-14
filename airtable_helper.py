from pyairtable import Api
import config

api = Api(config.AIRTABLE_API_KEY)
sessions_table = api.table(config.AIRTABLE_BASE_ID, config.SESSIONS_TABLE)
bot_table = api.table(config.AIRTABLE_BASE_ID, config.BOT_TABLE)


def get_session(chat_id):
    """Find user's current step in Sessions table"""
    records = sessions_table.all(
    formula=f'{{{config.FIELD_CHAT_ID}}} = "{chat_id}"'
)
    
    if records:
        # Delete duplicates, keep only the first
        if len(records) > 1:
            for duplicate in records[1:]:
                sessions_table.delete(duplicate["id"])
        return records[0]
    return None


def upsert_session(chat_id, new_step, record_id=None):
    fields = {
        "chat_id": str(chat_id),
        "current_step": new_step,
        "language": "rus"
    }
    if record_id:
        sessions_table.update(record_id, fields)
    else:
        existing = get_session(chat_id)
        if existing:
            sessions_table.update(existing["id"], fields)
        else:
            sessions_table.create(fields)


def get_step(step_id):
    """Fetch a step row from Bot table"""
    records = bot_table.all(
        formula=f'{{Step_rus}} = "{step_id}"',
        max_records=1
    )
    if records:
        return records[0]
    return None
