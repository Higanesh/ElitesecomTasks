import requests
import os
from dotenv import load_dotenv

load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_NAME = os.getenv("SHOP_URL")  # like "yourstore.myshopify.com"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def get_orders(limit=15, page_info=None):
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json?limit={limit}"
    if page_info:
        url += f"&page_info={page_info}"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    orders = data.get("orders", [])

    # Shopify includes pagination info in Link headers
    links = response.headers.get("Link", "")
    next_page = None
    prev_page = None

    if 'rel="next"' in links:
        next_page = links.split("page_info=")[1].split(">")[0].split("&")[0]
    if 'rel="previous"' in links:
        prev_page = links.split("page_info=")[1].split(">")[0].split("&")[0]

    return orders, next_page, prev_page


# 👉 Example usage
orders, next_page, prev_page = get_orders(limit=15)

print(f"Fetched {len(orders)} orders")
for o in orders:
    print(f"Order ID: {o['id']} | Customer: {o.get('customer', {}).get('first_name')}")

print("\nNext page cursor:", next_page)
print("Previous page cursor:", prev_page)
