# return_webhook.py
from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("\n===== New Return/Refund Event =====")

        # Print the full payload (for debugging)
        print(json.dumps(data, indent=2))

        # Extract and print useful fields
        order_id = data.get("order_id")
        order_name = data.get("name")
        total_price = data.get("total_price")
        customer = data.get("customer", {})
        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()

        print(f"Order ID: {order_id}")
        print(f"Order Name: {order_name}")
        print(f"Customer: {customer_name}")
        print(f"Total Price: {total_price}")

        print("Products:")
        for item in data.get("line_items", []):
            print(f" - {item['name']} (SKU: {item.get('sku')}) Qty: {item['quantity']} Price: {item['price']}")

        return "OK", 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return "Error", 500

if __name__ == "__main__":
    app.run(port=5000)
