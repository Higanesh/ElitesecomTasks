import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_NAME = os.getenv("SHOP_URL")  # should be like "yourshopname.myshopify.com" or just "yourshopname"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json"

# Headers for Shopify API authentication
headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# List of statuses we want to fetch
statuses = ["refunded", "partially_refunded"]

all_orders = []

for status in statuses:
    params = {
        "financial_status": status,  # fetch refunded and partially refunded orders
        "status": "any"              # include closed/archived orders
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # raise error if request fails
    data = response.json()

    all_orders.extend(data.get("orders", []))

# Print order details
for order in all_orders:
    print(f"Order ID: {order['id']}")
    print(f"Order Name: {order['name']}")
    customer = order.get("customer", {})
    print(f"Customer Name: {customer.get('first_name', '')} {customer.get('last_name', '')}")
    print(f"Total Amount Refunded: {order['total_price']}")
    print("Products:")
    for item in order.get("line_items", []):
        print(f"  - {item['quantity']}x {item['name']}")
    print("-" * 40)
