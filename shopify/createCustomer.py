import os
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def create_customer():
    # Take input from user
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    phone = input("Enter phone (with country code, e.g. +91xxxxxxxxxx): ")

    address1 = input("Enter address line 1: ")
    city = input("Enter city: ")
    province = input("Enter state/province: ")
    country = input("Enter country (e.g. India): ")
    zip_code = input("Enter ZIP/pincode: ")

    # API endpoint
    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/customers.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    # Data payload
    data = {
        "customer": {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "verified_email": True,
            "addresses": [
                {
                    "address1": address1,
                    "city": city,
                    "province": province,
                    "country": country,
                    "zip": zip_code
                }
            ]
        }
    }

    # API call
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 201:
        print("✅ Customer created successfully!")
        # print(resp.json())
    else:
        print("❌ Failed to create customer:", resp.json())

if __name__ == "__main__":
    create_customer()
