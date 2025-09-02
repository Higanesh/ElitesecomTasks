# products_and_orders.py
import os
import requests
from dotenv import load_dotenv
import shopify
import base64
import pandas as pd
from datetime import datetime, timezone, timedelta

# Load credentials
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION") or "2025-01"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LOCATION_ID = os.getenv("LOCATION_ID")  # Add your location ID in the .env file

# Common headers
REST_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}"
GRAPHQL_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
PRODUCT_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}/products.json?limit=250"

HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def get_listing():
    response = requests.get(PRODUCT_URL, headers=HEADERS)
    products = response.json().get("products", [])
    if not products:
        print("⚠️ No products found in Shopify store.")
    else:
        rows = []
        for product in products:
            for variant in product.get("variants", []):
                rows.append({
                    "Title": product["title"],
                    "SKU": variant["sku"],
                    "Inventory Quantity": variant["inventory_quantity"]
                })

        df = pd.DataFrame(rows)

        # Export to Excel
        output_file = r"D:\myProjects\ElitesecomTasks\I-O Files\shopify_products.xlsx"
        try:
            df.to_excel(output_file, index=False)
            print(f"✅ Exported to {output_file}")
        except Exception as e:
            print(f"❌ Failed to write Excel file: {e}")


def push_inventory():

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

def fetch_products_by_date():
    session = shopify.Session(SHOP_URL, API_VERSION, ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)

    # 2. Fetch orders between IST times
    # Convert IST (GMT+5:30) to UTC
    ist = timezone(timedelta(hours=5, minutes=30))
    start_time_ist = datetime(2025, 8, 22, 0, 0, tzinfo=ist)
    end_time_ist = datetime(2025, 8, 22, 11, 52, tzinfo=ist)

    # Convert IST to UTC automatically
    start_time_utc = start_time_ist.astimezone(timezone.utc)
    end_time_utc = end_time_ist.astimezone(timezone.utc)

    orders = shopify.Order.find(
        created_at_min=start_time_utc.isoformat(),
        created_at_max=end_time_utc.isoformat(),
        status='any',
        limit=10
    )

    # 3. Print orders
    for order in orders:
        # Parse created_at and format without timezone
        created_at = datetime.fromisoformat(order.created_at).replace(tzinfo=None)
        formatted_created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Order ID: {order.id} | Email: {order.email} | Total: {order.total_price} | Created: {formatted_created_at}")


