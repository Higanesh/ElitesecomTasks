import os
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv(r"D:\myProjects\asset\credentials.env")

SHOP_NAME = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

BASE_URL = f"https://{SHOP_NAME}/admin/api/{API_VERSION}"
headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def get_order(order_input):
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}

    # Case 1: User typed "#1033"
    if order_input.startswith("#"):
        url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json?name={order_input}&status=any"
        res = requests.get(url, headers=headers)
        data = res.json()
        if data.get("orders"):
            return data["orders"][0]
        else:
            return None

    # Case 2: User typed 1033 (no #)
    if order_input.isdigit():
        # Try order_number match
        url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json?name=%23{order_input}&status=any"
        res = requests.get(url, headers=headers)
        data = res.json()
        if data.get("orders"):
            return data["orders"][0]

    # Case 3: User typed Shopify order ID (long number)
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders/{order_input}.json"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("order")

    return None

def create_return(order):
    """Try to create a return (if API enabled)."""
    order_id = order["id"]
    payload = {
        "return": {
            "order_id": order_id,
            "line_items": [{"line_item_id": li["id"], "quantity": li["quantity"]} for li in order["line_items"]],
        }
    }
    url = f"{BASE_URL}/returns.json"
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code == 201:
        print(f"✅ Return created successfully for order {order['name']}")
        return resp.json()
    else:
        print(f"⚠️ Return not created (maybe API not enabled): {resp.status_code} {resp.text}")
        return None


def create_refund(order):
    """Refund all items of the order with location & restock_type per item."""
    order_id = order["id"]

    # Get location_id
    location_id = order.get("location_id")
    if not location_id:
        loc_resp = requests.get(f"{BASE_URL}/locations.json", headers=headers)
        if loc_resp.status_code == 200:
            locations = loc_resp.json().get("locations", [])
            if locations:
                location_id = locations[0]["id"]

    # Prepare refund line items
    refund_line_items = []
    for item in order["line_items"]:
        refund_line_items.append({
            "line_item_id": item["id"],
            "quantity": item["quantity"],
            "restock_type": "return",
            "location_id": location_id
        })

    # Get original transaction
    trans_resp = requests.get(f"{BASE_URL}/orders/{order_id}/transactions.json", headers=headers)
    transactions = trans_resp.json().get("transactions", [])

    if transactions:
        parent_txn = transactions[0]
        parent_txn_id = parent_txn.get("id")
        gateway = parent_txn.get("gateway", "manual")

        refund_payload = {
            "refund": {
                "notify": False,
                "refund_line_items": refund_line_items,
                "transactions": [
                    {
                        "kind": "refund",
                        "parent_id": parent_txn_id,  # ✅ only if transaction exists
                        "amount": order["total_price"],
                        "gateway": gateway
                    }
                ]
            }
        }
    else:
        # No transaction → Only restock items
        print("⚠️ No payment transaction found, only restocking items (no money refunded).")
        refund_payload = {
            "refund": {
                "notify": False,
                "refund_line_items": refund_line_items
            }
        }

    url = f"{BASE_URL}/orders/{order_id}/refunds.json"
    resp = requests.post(url, headers=headers, json=refund_payload)

    if resp.status_code == 201:
        print(f"✅ Refund created successfully for order {order['name']}")
        return resp.json()
    else:
        print(f"❌ Refund failed: {resp.status_code} {resp.text}")
        return None
