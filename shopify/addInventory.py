import requests
import pandas as pd
import os
from dotenv import load_dotenv

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv(r"D:\myProjects\asset\credentials.env")  # Update path to your .env

SHOP_NAME = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")
LOCATION_ID = os.getenv("LOCATION_ID")

BASE_URL = f"https://{SHOP_NAME}/admin/api/{API_VERSION}"
HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# ------------------------------
# Fetch all existing products and build SKU lookup
# ------------------------------
def build_sku_lookup():
    """
    Fetch all products and variants from Shopify.
    Returns a dictionary: SKU -> inventory_item_id
    """
    sku_lookup = {}
    url = f"{BASE_URL}/products.json?limit=250"
    res = requests.get(url, headers=HEADERS)
    
    if res.status_code != 200:
        print("❌ Failed to fetch products")
        return sku_lookup

    products = res.json().get("products", [])
    for product in products:
        for variant in product.get("variants", []):
            sku = variant.get("sku", "").strip()
            if sku:  # Only add if SKU exists
                sku_lookup[sku] = variant["inventory_item_id"]
    return sku_lookup

# ------------------------------
# Get current inventory for a SKU
# ------------------------------
def get_current_inventory(inventory_item_id):
    url = f"{BASE_URL}/inventory_levels.json?inventory_item_ids={inventory_item_id}&location_ids={LOCATION_ID}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200 and res.json().get("inventory_levels"):
        return res.json()["inventory_levels"][0]["available"]
    return 0

# ------------------------------
# Update inventory
# ------------------------------
def update_inventory(inventory_item_id, new_quantity):
    url = f"{BASE_URL}/inventory_levels/set.json"
    payload = {
        "location_id": LOCATION_ID,
        "inventory_item_id": inventory_item_id,
        "available": new_quantity
    }
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code == 200

# ------------------------------
# Main function to push inventory from Excel
# ------------------------------
def push_inventory_from_excel(filename):
    df = pd.read_excel(filename)
    df.columns = df.columns.str.strip().str.lower()  # Normalize columns

    # Build SKU lookup from Shopify
    sku_lookup = build_sku_lookup()
    if not sku_lookup:
        print("❌ No SKUs found in Shopify.")
        return

    for _, row in df.iterrows():
        title = row.get("title", "")
        sku = str(row.get("sku", "")).strip()
        quantity_to_add = row.get("inventory quantity", 0)

        if not sku or pd.isna(quantity_to_add):
            continue

        if sku not in sku_lookup:
            print(f"❌ SKU not found in Shopify, skipping: {sku}")
            continue

        inventory_item_id = sku_lookup[sku]
        current_stock = get_current_inventory(inventory_item_id)
        new_stock = current_stock + int(quantity_to_add)

        success = update_inventory(inventory_item_id, new_stock)
        if success:
            print(f"✅ Updated SKU {sku}: {current_stock} -> {new_stock}")
        else:
            print(f"❌ Failed to update SKU {sku}")

# ------------------------------
# Run the script
# ------------------------------
if __name__ == "__main__":
    push_inventory_from_excel(r"D:\myProjects\ElitesecomTasks\I-O Files\shopify_products.xlsx")
