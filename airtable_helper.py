
from pyairtable import Api
import config
 
api = Api(config.AIRTABLE_API_KEY)
sessions_table = api.table(config.AIRTABLE_BASE_ID, config.SESSIONS_TABLE)
bot_table = api.table(config.AIRTABLE_BASE_ID, config.BOT_TABLE)
 
 
def get_lang_fields(language):
    """
    Returns a dict telling the bot which Airtable column to read
    for each piece of language-specific content.
    """
    mapping = {
        "rus": {
            "step":    "Step_rus",
            "txt":     "TXT_rus",
            "next":    "next_step_rus",
            "buttons": "button_options",
            "answers": "correct_answers",
        },
        "eng": {
            "step":    "Step_eng",
            "txt":     "TXT_eng",
            "next":    "next_step_eng",
            "buttons": "button_options",
            "answers": "correct_answers_eng",
        },
        "ita": {
            "step":    "Step_ita",
            "txt":     "TXT_ita",
            "next":    "next_step_ita",
            "buttons": "button_options",
            "answers": "correct_answers_ita",
        },
    }
    return mapping.get(language, mapping["rus"])
 
 
def get_session(chat_id):
    records = sessions_table.all(formula=f"{{{config.FIELD_CHAT_ID}}} = '{chat_id}'")
    return records[0] if records else None
 
 
def upsert_session(chat_id, step_id, record_id=None, language=None):
    data = {config.FIELD_CURRENT_STEP: step_id}
    if language:
        data[config.FIELD_LANGUAGE] = language
    if record_id:
        sessions_table.update(record_id, data)
    else:
        data[config.FIELD_CHAT_ID] = str(chat_id)
        sessions_table.create(data)
 
 
def get_step(step_id, language="rus"):
    fields = get_lang_fields(language)
    step_field = fields["step"]
    records = bot_table.all(formula=f"{{{step_field}}} = '{step_id}'")
    return records[0] if records else None
