import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_NAME = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

df = pd.read_excel(r"D:\myProjects\ElitesecomTasks\I-O Files\shopify_products.xlsx")

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

for index, row in df.iterrows():
    sku = row["SKU"]
    new_qty = int(row["inventory quantity"])

    # Step 1: Get all products to find the variant with this SKU
    products_url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/products.json?limit=250"
    products = requests.get(products_url, headers=headers).json().get("products", [])

    variant_id = None
    inventory_item_id = None

    for product in products:
        for variant in product["variants"]:
            if variant["sku"] == sku:
                variant_id = variant["id"]
                inventory_item_id = variant["inventory_item_id"]
                break
        if variant_id:
            break

    if not variant_id:
        print(f"SKU {sku} not found, skipping...")
        continue

    # Step 2: Update inventory level
    inventory_url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/inventory_levels/set.json"
    payload = {
        "location_id": 70693552199,  # replace with your location ID
        "inventory_item_id": inventory_item_id,
        "available": new_qty
    }

    res = requests.post(inventory_url, headers=headers, json=payload)
    print(f"Updated SKU {sku} (variant {variant_id}) to {new_qty}, status: {res.status_code}")
