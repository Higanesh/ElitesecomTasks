import os
import shopify
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Initialize Shopify Session
session = shopify.Session(f"https://{SHOP_URL}/admin/api/{API_VERSION}", API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# Create a new product
new_product = shopify.Product()
new_product.title = "water bottle"
new_product.body_html = "<strong>Amazing product description</strong>"
new_product.vendor = "MyVendor"
new_product.product_type = "Accessories"

# Add a variant (price, SKU, inventory)
variant = shopify.Variant()
variant.price = "50.00"
variant.sku = "SKU234"
variant.inventory_management = "shopify"
variant.inventory_quantity = 50
new_product.variants = [variant]

# Save product to Shopify
if new_product.save():
    print(f"Product created successfully! ID: {new_product.id}")
else:
    print("Failed to create product:")
    print(new_product.errors.full_messages())

# Close the session
shopify.ShopifyResource.clear_session()
