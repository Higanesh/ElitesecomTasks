import os
import shopify
import requests
import base64
from dotenv import load_dotenv

# Load credentials
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LOCATION_ID = os.getenv("LOCATION_ID")  # Add your location ID in the .env file

# Start Shopify session
session = shopify.Session(f"https://{SHOP_URL}/admin/api/{API_VERSION}", API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# User input
title = input("Enter product title: ")
description = input("Enter product description: ")
vendor = input("Enter vendor name: ")
product_type = input("Enter product type: ")
price = input("Enter price: ")
sku = input("Enter SKU: ")
quantity = int(input("Enter inventory quantity: "))
image_path = input("Enter image path (local or public URL): ")

# Create product
new_product = shopify.Product()
new_product.title = title
new_product.body_html = description
new_product.vendor = vendor
new_product.product_type = product_type

variant = shopify.Variant()
variant.price = price
variant.sku = sku
variant.inventory_management = "shopify"
new_product.variants = [variant]

# Handle image upload
images = []
if os.path.exists(image_path):  # Local file
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")
    images.append({"attachment": encoded_image, "filename": os.path.basename(image_path)})
else:  # Public URL
    images.append({"src": image_path})

new_product.images = images

# Save product
if new_product.save():
    print(f"✅ Product created successfully! ID: {new_product.id}")

    # Set inventory properly
    inventory_item_id = new_product.variants[0].inventory_item_id
    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/inventory_levels/set.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}
    data = {"location_id": LOCATION_ID, "inventory_item_id": inventory_item_id, "available": quantity}
    resp = requests.post(url, json=data, headers=headers)
    print("Inventory update response:", resp.json())

else:
    print("❌ Failed to create product:", new_product.errors.full_messages())

shopify.ShopifyResource.clear_session()
