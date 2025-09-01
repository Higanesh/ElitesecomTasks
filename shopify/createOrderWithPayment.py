import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION") or "2025-01"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Common headers
rest_headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}
graphql_url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
rest_url = f"https://{SHOP_URL}/admin/api/{API_VERSION}"

# -------- Step 1: Check customer by email --------
email = input("Enter customer email: ")

resp = requests.get(
    f"{rest_url}/customers/search.json?query=email:{email}",
    headers=rest_headers
).json()

if not resp.get("customers"):
    print("❌ Customer not found. Please add the customer first.")
    exit()

customer = resp["customers"][0]
customer_id = customer["id"]
print(f"✅ Customer found: {customer['first_name']} {customer['last_name']} (ID: {customer_id})")

# -------- Step 2: Choose shipping address --------
use_default = input("Do you want to use the default shipping address? (yes/no): ").strip().lower()

if use_default == "yes" and customer.get("default_address"):
    shipping_address = customer["default_address"]
    print(f"✅ Using default shipping address: {shipping_address['address1']}, {shipping_address['city']}")
else:
    shipping_address = {
        "first_name": input("Enter shipping first name: "),
        "last_name": input("Enter shipping last name: "),
        "address1": input("Enter shipping address: "),
        "city": input("Enter city: "),
        "province": input("Enter state/province: "),
        "country": input("Enter country: "),
        "zip": input("Enter postal code: "),
        "phone": input("Enter phone number: ")
    }

# -------- Step 3: Collect multiple products --------
line_items = []

while True:
    sku = input("Enter product SKU (or type 'done' to finish): ").strip()
    if sku.lower() == "done":
        break

    # Find variant by SKU using GraphQL
    query = """
    query($sku: String!) {
      productVariants(first: 1, query: $sku) {
        edges {
          node {
            id
            sku
            title
            product {
              title
            }
          }
        }
      }
    }
    """
    resp = requests.post(
        graphql_url,
        headers=rest_headers,
        json={"query": query, "variables": {"sku": sku}}
    ).json()

    edges = resp.get("data", {}).get("productVariants", {}).get("edges", [])
    if not edges:
        print(f"❌ No variant found for SKU: {sku}")
        continue

    variant = edges[0]["node"]
    variant_gid = variant["id"]
    variant_id = int(variant_gid.split("/")[-1])
    print(f"✅ Found: {variant['title']} ({variant['product']['title']}) - Variant ID {variant_id}")

    quantity = int(input(f"Enter quantity for SKU {sku}: "))
    line_items.append({"variant_id": variant_id, "quantity": quantity})

if not line_items:
    print("❌ No products added. Exiting.")
    exit()

# -------- Step 4: Create order --------
order_payload = {
    "order": {
        "customer": {"id": customer_id},
        "line_items": line_items,
        "shipping_address": shipping_address,
        "financial_status": "pending"  # create order in pending status
    }
}

order_resp = requests.post(
    f"{rest_url}/orders.json",
    headers=rest_headers,
    json=order_payload
).json()

if "order" not in order_resp:
    print("❌ Failed to create order:", order_resp)
    exit()

order_obj = order_resp["order"]
order_id = order_obj["id"]

print(f"✅ Order created successfully! Order ID: {order_id}")

# --- Debug: print order keys ---
print("DEBUG ORDER DATA KEYS:", list(order_obj.keys()))

# --- Get order total safely ---
order_total = None
if "current_total_price" in order_obj:
    order_total = order_obj["current_total_price"]
elif "total_price" in order_obj:
    order_total = order_obj["total_price"]
elif "current_total_price_set" in order_obj:
    order_total = order_obj["current_total_price_set"]["shop_money"]["amount"]
elif "total_price_set" in order_obj:
    order_total = order_obj["total_price_set"]["shop_money"]["amount"]

if not order_total:
    raise ValueError("❌ Could not find total price in order response")

print(f"✅ Order total found: {order_total}")

# --- Update payment status ---
# Step 1: Fetch order transactions (to get parent transaction ID if required)
transactions_resp = requests.get(
    f"{rest_url}/orders/{order_id}/transactions.json",
    headers=rest_headers
).json()

parent_transaction_id = None
if "transactions" in transactions_resp and transactions_resp["transactions"]:
    parent_transaction_id = transactions_resp["transactions"][0]["id"]

# Step 2: Capture payment (mark as paid)
payment_url = f"{rest_url}/orders/{order_id}/transactions.json"
payment_payload = {
    "transaction": {
        "kind": "capture",
        "status": "success",
        "amount": order_total,
        "currency": order_obj["currency"]
    }
}

# Attach parent transaction ID if available
if parent_transaction_id:
    payment_payload["transaction"]["parent_id"] = parent_transaction_id

payment_response = requests.post(payment_url, headers=rest_headers, json=payment_payload)

if payment_response.status_code == 201:
    print("✅ Payment captured successfully. Order marked as PAID.")
else:
    print(f"❌ Payment capture failed: {payment_response.status_code}")
    print(payment_response.text)


# --- Fulfillment Update ---
# Step 1: Get fulfillment orders
fo_resp = requests.get(
    f"{rest_url}/orders/{order_id}/fulfillment_orders.json",
    headers=rest_headers
).json()

if "fulfillment_orders" not in fo_resp or not fo_resp["fulfillment_orders"]:
    print("❌ No fulfillment orders found. Cannot fulfill order.")
    exit()

fulfillment_order_id = fo_resp["fulfillment_orders"][0]["id"]

# Step 2: Fulfill order
fulfillment_data = {
    "fulfillment": {
        "message": "Order fulfilled via API",
        "notify_customer": True,
        "line_items_by_fulfillment_order": [
            {"fulfillment_order_id": fulfillment_order_id}
        ]
    }
}

fulfill_resp_raw = requests.post(
    f"{rest_url}/fulfillments.json",
    headers=rest_headers,
    json=fulfillment_data
)

print("Fulfillment Status Code:", fulfill_resp_raw.status_code)
print("Fulfillment Response Text:", fulfill_resp_raw.text)

try:
    fulfill_resp = fulfill_resp_raw.json()
    if "fulfillment" in fulfill_resp:
        print("✅ Order fulfilled successfully.")
    else:
        print("⚠️ Fulfillment failed:", fulfill_resp)
except Exception:
    print("❌ Could not parse JSON response for fulfillment.")
