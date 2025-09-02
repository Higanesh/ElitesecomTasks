import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION") or "2025-01"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LOCATION_ID = os.getenv("LOCATION_ID")  # for restocking returned items

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def refund_and_return(order_id: str):
    # 1. Calculate refund
    calc_url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/orders/{order_id}/refunds/calculate.json"
    calc_payload = {
        "refund": {
            "shipping": {"full_refund": True},
            "refund_line_items": []  # empty = refund all line items automatically
        }
    }

    calc_resp = requests.post(calc_url, headers=headers, json=calc_payload)
    if calc_resp.status_code != 200:
        print("❌ Refund calculation failed:", calc_resp.json())
        return

    refund_details = calc_resp.json().get("refund")
    print("✅ Refund calculated")

    # 2. Create refund
    refund_url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/orders/{order_id}/refunds.json"
    create_resp = requests.post(refund_url, headers=headers, json={"refund": refund_details})

    if create_resp.status_code == 201:
        refund_obj = create_resp.json()
        print(f"✅ Refund created successfully! Refund ID: {refund_obj['refund']['id']}")
    else:
        print("❌ Failed to create refund:", create_resp.json())

    # 3. (Optional) Create return in Shopify (GraphQL)
    graphql_url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
    graphql_query = {
        "query": """
        mutation returnCreate($input: ReturnInput!) {
          returnCreate(return: $input) {
            return {
              id
              order { id }
            }
            userErrors { field message }
          }
        }
        """,
        "variables": {
            "input": {
                "orderId": f"gid://shopify/Order/{order_id}"
            }
        }
    }

    g_resp = requests.post(graphql_url, headers=headers, json=graphql_query)
    g_data = g_resp.json()

    if "errors" in g_data or g_data.get("data", {}).get("returnCreate", {}).get("userErrors"):
        print("⚠️ Return creation failed:", g_data)
    else:
        print("✅ Return created:", g_data["data"]["returnCreate"]["return"]["id"])

if __name__ == "__main__":
    order_id = input("Enter Shopify Order ID: ")
    refund_and_return(order_id)
