import shopify
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(r"D:\myProjects\asset\credentials.env")

shop_url = os.getenv("SHOP_URL")
access_token = os.getenv("ACCESS_TOKEN")
api_version = os.getenv("API_VERSION")

# Create and activate Shopify session
session = shopify.Session(shop_url, api_version, access_token)
shopify.ShopifyResource.activate_session(session)

# Convert IST to UTC for filtering
ist = timezone(timedelta(hours=5, minutes=30))
start_time_ist = datetime(2025, 8, 22, 0, 0, tzinfo=ist)
end_time_ist = datetime(2025, 8, 23, 23, 59, tzinfo=ist)

start_time_utc = start_time_ist.astimezone(timezone.utc)
end_time_utc = end_time_ist.astimezone(timezone.utc)

# Fetch orders
orders = shopify.Order.find(
    created_at_min=start_time_utc.isoformat(),
    created_at_max=end_time_utc.isoformat(),
    status='any',
    limit=10
)

# Print with confirmation logic
for order in orders:
    # Determine confirmation status
    is_cod = any("cash on delivery" in pg.lower() for pg in order.payment_gateway_names or [])
    is_paid = order.financial_status in ["paid", "partially_paid"]
    is_cancelled = bool(order.cancelled_at)

    if is_paid:
        confirmed_status = "Confirmed (Paid)"
    elif is_cod and not is_cancelled:
        confirmed_status = "Confirmed (COD)"
    else:
        confirmed_status = "Not Confirmed"

    # Format date without +05:30
    created_at = datetime.fromisoformat(order.created_at.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")

    print(f"Order ID: {order.id} | Email: {order.email or 'N/A'} | Total: {order.total_price} | Created: {created_at} | Status: {confirmed_status}")
