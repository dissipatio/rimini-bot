from airtable_helper import get_step

step = get_step("1_1_r")
if step:
    print("SUCCESS! Step found:")
    print("Text:", step["fields"].get("TXT_rus"))
else:
    print("ERROR: Step not found")
