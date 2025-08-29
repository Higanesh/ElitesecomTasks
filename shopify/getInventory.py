import os
import shopify
import requests
from dotenv import load_dotenv

# -----------------------------
# Load credentials from .env
# -----------------------------
load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_URL = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

BASE_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}"
HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# -----------------------------
# Start Shopify API session
# -----------------------------
session = shopify.Session(f"https://{SHOP_URL}/admin/api/{API_VERSION}", API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# -----------------------------
# Test connection
# -----------------------------
shop = shopify.Shop.current()
print("✅ Connected to Shopify Store:", shop.name)

# -----------------------------
# Function to fetch all products with SKUs and stock
# -----------------------------
def list_sku_with_stock():
    next_page = shopify.Product.find(limit=250)

    while next_page:
        for product in next_page:
            for variant in product.variants:
                sku = (variant.sku or "").strip()
                if not sku:
                    continue

                inventory_item_id = variant.inventory_item_id
                # Get inventory stock for each variant
                url = f"{BASE_URL}/inventory_levels.json?inventory_item_ids={inventory_item_id}"
                res = requests.get(url, headers=HEADERS)
                if res.status_code == 200:
                    levels = res.json().get("inventory_levels", [])
                    stock = levels[0].get("available", 0) if levels else 0
                    print(f"Product: {product.title} | SKU: {sku} | Stock: {stock}")
                else:
                    print(f"❌ Failed to fetch inventory for SKU {sku}")

        # Move to next page using cursor-based pagination
        if hasattr(next_page, 'has_next_page') and next_page.has_next_page():
            next_page = next_page.next_page()
        else:
            break

# -----------------------------
# Run function
# -----------------------------
list_sku_with_stock()
