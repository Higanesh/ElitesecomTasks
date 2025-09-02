import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load Shopify credentials
load_dotenv(r"D:\myProjects\asset\credentials.env")
SHOP_NAME = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/products.json?limit=250"

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
products = response.json().get("products", [])
if not products:
    print("⚠️ No products found in Shopify store.")
else:
    rows = []
    for product in products:
        for variant in product.get("variants", []):
            rows.append({
                "Title": product["title"],
                "SKU": variant["sku"],
                "Inventory Quantity": variant["inventory_quantity"]
            })

    df = pd.DataFrame(rows)

    # Export to Excel
    output_file = r"D:\myProjects\ElitesecomTasks\I-O Files\shopify_products.xlsx"
    try:
        df.to_excel(output_file, index=False)
        print(f"✅ Exported to {output_file}")
    except Exception as e:
        print(f"❌ Failed to write Excel file: {e}")
