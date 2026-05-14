import requests
import config

headers = {
    "Authorization": f"Bearer {config.AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get("https://api.airtable.com/v0/meta/bases", headers=headers)
data = response.json()

print("Bases I can access:")
for base in data.get("bases", []):
    name = base["name"]
    bid = base["id"]
    print(f"  Name: {name}  ID: {bid}")
