import shopify
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

load_dotenv(r"D:\myProjects\asset\credentials.env")

shop_url = os.getenv("SHOP_URL")       # Example: "yourstore.myshopify.com"
access_token = os.getenv("ACCESS_TOKEN")
api_version = os.getenv("API_VERSION")  # Example: "2025-07"

session = shopify.Session(shop_url, api_version, access_token)
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










# import os
# from dotenv import load_dotenv
# import requests
# from datetime import datetime
# from dateutil import tz

# # -----------------------------
# # Helper function to convert IST to UTC (Shopify expects UTC ISO 8601 format)
# # -----------------------------
# def ist_to_utc(ist_datetime_str):
#     """
#     Convert IST datetime string (YYYY-MM-DD HH:MM:SS) to UTC ISO 8601 format.
#     Example input: "2025-08-22 12:23:00"
#     """
#     ist_zone = tz.gettz("Asia/Kolkata")
#     utc_zone = tz.UTC

#     # Parse IST datetime string
#     ist_time = datetime.strptime(ist_datetime_str, "%Y-%m-%d %H:%M:%S")
#     ist_time = ist_time.replace(tzinfo=ist_zone)

#     # Convert to UTC and return Shopify format (ISO 8601)
#     utc_time = ist_time.astimezone(utc_zone)
#     return utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")


# # -----------------------------
# # Load credentials from .env file
# # -----------------------------
# load_dotenv(r"D:\myProjects\asset\credentials.env")

# SHOP_URL = os.getenv("SHOP_URL")       # Example: "yourstore.myshopify.com"
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
# API_VERSION = os.getenv("API_VERSION")  # Example: "2025-07"

# headers = {
#     "X-Shopify-Access-Token": ACCESS_TOKEN,
#     "Content-Type": "application/json"
# }

# # -----------------------------
# # Enter IST date/time for filtering
# # -----------------------------
# # Example: Orders from 1 Aug 2025 00:00 IST to 22 Aug 2025 12:23 IST
# created_at_min_ist = "2025-08-01 00:00:00"
# created_at_max_ist = "2025-08-22 11:53:00"

# # Convert IST to UTC for Shopify API
# created_at_min = ist_to_utc(created_at_min_ist)
# created_at_max = ist_to_utc(created_at_max_ist)

# # -----------------------------
# # Fetch orders from Shopify API
# # -----------------------------
# url = (
#     f"https://{SHOP_URL}/admin/api/{API_VERSION}/orders.json"
#     f"?status=any&created_at_min={created_at_min}&created_at_max={created_at_max}&limit=10"
# )

# response = requests.get(url, headers=headers)

# # -----------------------------
# # Display results
# # -----------------------------
# if response.status_code == 200:
#     orders = response.json().get("orders", [])
#     if not orders:
#         print("No orders found in the given date range.")
#     else:
#         for order in orders:
#             # Convert created_at (UTC) to IST for display
#             utc_time = datetime.strptime(order['created_at'], "%Y-%m-%dT%H:%M:%S%z")
#             ist_time = utc_time.astimezone(tz.gettz("Asia/Kolkata"))
#             ist_time_str = ist_time.strftime("%Y-%m-%d %H:%M:%S")

#             print(f"Order ID: {order['id']} | Email: {order.get('email')} | "
#                   f"Total: {order['total_price']} | Created At (IST): {ist_time_str}")
# else:
#     print("Error:", response.status_code, response.text)



