# create_module.py
import os
import requests
from dotenv import load_dotenv
import shopify
import base64


# Load credentials
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION") or "2025-01"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LOCATION_ID = os.getenv("LOCATION_ID")  # Add your location ID in the .env file

# Common headers
REST_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}"
GRAPHQL_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# -------------------- Create Customer --------------------
def create_customer():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    phone = input("Enter phone (with country code): ")
    address1 = input("Enter address line 1: ")
    city = input("Enter city: ")
    province = input("Enter state/province: ")
    country = input("Enter country: ")
    zip_code = input("Enter ZIP/pincode: ")

    data = {
        "customer": {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "verified_email": True,
            "addresses": [
                {
                    "address1": address1,
                    "city": city,
                    "province": province,
                    "country": country,
                    "zip": zip_code
                }
            ]
        }
    }

    resp = requests.post(f"{REST_URL}/customers.json", json=data, headers=HEADERS)
    if resp.status_code == 201:
        return "✅ Customer created successfully!"
    else:
        return "❌ Failed to create customer:", resp.json()

# -------------------- Create Order --------------------
def create_order():
    email = input("Enter customer email: ")
    resp = requests.get(f"{REST_URL}/customers/search.json?query=email:{email}", headers=HEADERS).json()
    if not resp.get("customers"):
        print("❌ Customer not found.")
        return
    customer = resp["customers"][0]
    customer_id = customer["id"]

    use_default = input("Use default shipping address? (yes/no): ").strip().lower()
    if use_default == "yes" and customer.get("default_address"):
        shipping_address = customer["default_address"]
    else:
        shipping_address = {
            "first_name": input("First name: "),
            "last_name": input("Last name: "),
            "address1": input("Address: "),
            "city": input("City: "),
            "province": input("State: "),
            "country": input("Country: "),
            "zip": input("ZIP: "),
            "phone": input("Phone: ")
        }

    line_items = []
    while True:
        sku = input("Enter product SKU (or 'done'): ").strip()
        if sku.lower() == "done":
            break
        query = """
        query($sku: String!) {
          productVariants(first: 1, query: $sku) {
            edges {
              node {
                id
                sku
                title
                product { title }
              }
            }
          }
        }
        """
        resp = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query, "variables": {"sku": sku}}).json()
        edges = resp.get("data", {}).get("productVariants", {}).get("edges", [])
        if not edges:
            print(f"❌ No variant found for SKU: {sku}")
            continue
        variant_id = int(edges[0]["node"]["id"].split("/")[-1])
        quantity = int(input(f"Enter quantity for SKU {sku}: "))
        line_items.append({"variant_id": variant_id, "quantity": quantity})

    if not line_items:
        return "❌ No products added."

    order_data = {
        "order": {
            "customer": {"id": customer_id},
            "line_items": line_items,
            "shipping_address": shipping_address,
            "financial_status": "pending"
        }
    }
    order_resp = requests.post(f"{REST_URL}/orders.json", headers=HEADERS, json=order_data).json()
    if "order" in order_resp:
        return f"✅ Order created successfully! ID: {order_resp['order']['id']}"
    else:
        return "❌ Failed to create order:", order_resp

# -------------------- Add Products --------------------
def create_product():
    # Move logic from add_products.py here
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
        # print(f"✅ Product created successfully! ID: {new_product.id}")

        # Set inventory properly
        inventory_item_id = new_product.variants[0].inventory_item_id
        url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/inventory_levels/set.json"
        headers = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}
        data = {"location_id": LOCATION_ID, "inventory_item_id": inventory_item_id, "available": quantity}
        resp = requests.post(url, json=data, headers=headers)
        # print("Inventory update response:", resp.json())
        return f"✅ Product created successfully! ID: {new_product.id} and inventory set."

    else:
        return "❌ Failed to create product:", new_product.errors.full_messages()


# -------------------- Create Collection --------------------
def create_manual_collection():
    title = input("Enter manual collection name: ")
    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/custom_collections.json"
    payload = {
        "custom_collection": {
            "title": title
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        data = response.json()
        return f"✅ Manual collection '{title}' created successfully! ID: {data['custom_collection']['id']}"
    else:
        return "❌ Failed to create manual collection:", response.status_code

def create_smart_collection():
    title = input("Enter smart collection name: ")

    # Ask condition details
    print("\nAvailable columns: title, type, vendor, tag")
    column = input("Enter column to filter on: ").strip()

    print("\nAvailable relations: equals, not_equals, greater_than, less_than, starts_with, ends_with, contains")
    relation = input("Enter relation: ").strip()

    condition = input("Enter condition value: ").strip()

    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/smart_collections.json"
    payload = {
        "smart_collection": {
            "title": title,
            "rules": [
                {
                    "column": column,
                    "relation": relation,
                    "condition": condition
                }
            ],
            "disjunctive": False  # False = AND logic, True = OR logic
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        data = response.json()
        return f"✅ Smart collection '{title}' created successfully! ID: {data['smart_collection']['id']}"
    else:
        return "❌ Failed to create smart collection:", response.status_code



