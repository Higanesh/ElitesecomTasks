import os
import shopify
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_URL = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

# Start Shopify API session
session = shopify.Session(f"https://{SHOP_URL}/admin/api/{API_VERSION}", API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# Test connection by fetching store info
shop = shopify.Shop.current()
print("✅ Connected to Shopify Store:", shop.name)

# ✅ Fetch first 5 products
products = shopify.Product.find(limit=10)
for product in products:
    print(product.id, product.title, product.variants[0].price)
