import os
import shopify
import requests
import base64
import pandas as pd
from dotenv import load_dotenv

# ===============================
# Load credentials
# ===============================
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LOCATION_ID = os.getenv("LOCATION_ID")

# ===============================
# Start Shopify session
# ===============================
session = shopify.Session(f"https://{SHOP_URL}/admin/api/{API_VERSION}", API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# ===============================
# Read Excel file
# ===============================
excel_file = r"D:\myProjects\ElitesecomTasks\I-O Files\new_products.xlsx"  # <-- Update path
df = pd.read_excel(excel_file)

# Expected columns in Excel:
# Title | Description | Vendor | ProductType | Price | SKU | Quantity | ImagePath

for index, row in df.iterrows():
    print(f"\n📦 Creating product {index+1}: {row['Title']}")

    try:
        # Create product
        new_product = shopify.Product()
        new_product.title = str(row["Title"])
        new_product.body_html = str(row["Description"])
        new_product.vendor = str(row["Vendor"])
        new_product.product_type = str(row["ProductType"])

        # Variant
        variant = shopify.Variant()
        variant.price = str(row["Price"])
        variant.sku = str(row["SKU"])
        variant.inventory_management = "shopify"
        new_product.variants = [variant]

        # Image upload
        images = []
        image_path = str(row["ImagePath"])
        if os.path.exists(image_path):  # Local file
            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode("utf-8")
            images.append({"attachment": encoded_image, "filename": os.path.basename(image_path)})
        elif image_path.startswith("http"):  # Public URL
            images.append({"src": image_path})

        new_product.images = images

        # Save product
        if new_product.save():
            print(f"✅ Product created: {new_product.title} (ID: {new_product.id})")

            # Update inventory
            inventory_item_id = new_product.variants[0].inventory_item_id
            url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/inventory_levels/set.json"
            headers = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}
            data = {
                "location_id": LOCATION_ID,
                "inventory_item_id": inventory_item_id,
                "available": int(row["Quantity"]),
            }
            resp = requests.post(url, json=data, headers=headers)
            print("Inventory response:", resp.json())
        else:
            print(f"❌ Failed to create product {row['Title']}: {new_product.errors.full_messages()}")

    except Exception as e:
        print(f"⚠️ Error with product {row['Title']}: {str(e)}")

# ===============================
# Clear session
# ===============================
shopify.ShopifyResource.clear_session()
