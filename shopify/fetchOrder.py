import requests
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# Fetch latest orders
url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/orders.json?status=any&limit=5"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    orders = response.json()["orders"]
    for order in orders:
        print(f"Order ID: {order['id']} | Email: {order.get('email')} | Total: {order['total_price']}")
else:
    print("Error:", response.status_code, response.text)
