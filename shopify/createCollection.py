import requests
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_NAME = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def create_manual_collection():
    title = input("Enter manual collection name: ")
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/custom_collections.json"
    payload = {
        "custom_collection": {
            "title": title
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Manual collection '{title}' created successfully! ID: {data['custom_collection']['id']}")
    else:
        print("❌ Failed to create manual collection:", response.status_code)
        print(response.text)


def create_smart_collection():
    title = input("Enter smart collection name: ")

    # Ask condition details
    print("\nAvailable columns: title, type, vendor, tag")
    column = input("Enter column to filter on: ").strip()

    print("\nAvailable relations: equals, not_equals, greater_than, less_than, starts_with, ends_with, contains")
    relation = input("Enter relation: ").strip()

    condition = input("Enter condition value: ").strip()

    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/smart_collections.json"
    payload = {
        "smart_collection": {
            "title": title,
            "rules": [
                {
                    "column": column,
                    "relation": relation,
                    "condition": condition
                }
            ],
            "disjunctive": False  # False = AND logic, True = OR logic
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Smart collection '{title}' created successfully! ID: {data['smart_collection']['id']}")
    else:
        print("❌ Failed to create smart collection:", response.status_code)
        print(response.text)


if __name__ == "__main__":
    choice = input("Do you want to create a Manual or Smart collection? (manual/smart): ").lower()

    if choice == "manual":
        create_manual_collection()
    elif choice == "smart":
        create_smart_collection()
    else:
        print("❌ Invalid choice. Please type 'manual' or 'smart'.")
