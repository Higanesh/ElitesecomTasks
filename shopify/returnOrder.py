import requests

# 🔐 Replace with your store and token
SHOP_DOMAIN = 'glearn.myshopify.com'
ACCESS_TOKEN = 'f8bf365e2cfa4203d860e03038e4b955'
API_VERSION = '2025-07'

GRAPHQL_URL = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/graphql.json"

HEADERS = {
    'X-Shopify-Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

# Step 1: Get recent orders
def get_recent_orders():
    query = '''
    {
      orders(first: 5, query: "financial_status:paid") {
        edges {
          node {
            id
            name
          }
        }
      }
    }
    '''
    response = requests.post(GRAPHQL_URL, json={'query': query}, headers=HEADERS)
    data = response.json()

    if 'errors' in data:
        raise Exception(data['errors'])

    return [edge['node'] for edge in data['data']['orders']['edges']]

# Step 2: For each order, fetch return requests
def get_return_requests(order_gid):
    query = f'''
    {{
      order(id: "{order_gid}") {{
        returnRequests(first: 10) {{
          edges {{
            node {{
              id
              status
              createdAt
              updatedAt
              returnLineItems(first: 10) {{
                edges {{
                  node {{
                    quantity
                    lineItem {{
                      name
                      sku
                      quantity
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    response = requests.post(GRAPHQL_URL, json={'query': query}, headers=HEADERS)
    data = response.json()

    if 'errors' in data:
        raise Exception(data['errors'])

    return data['data']['order']['returnRequests']['edges']

# Main function
def main():
    try:
        orders = get_recent_orders()
        print(f"Found {len(orders)} recent paid orders.\n")

        for order in orders:
            print(f"🔎 Checking returns for order: {order['name']}")
            return_requests = get_return_requests(order['id'])

            if not return_requests:
                print("  ↳ No return requests.\n")
                continue

            for edge in return_requests:
                request = edge['node']
                print(f"  ✅ Return Request ID: {request['id']}")
                print(f"     Status: {request['status']}")
                print(f"     Created At: {request['createdAt']}")
                print(f"     Line Items:")

                for item_edge in request['returnLineItems']['edges']:
                    item = item_edge['node']
                    line_item = item['lineItem']
                    print(f"       - {line_item['name']} (SKU: {line_item['sku']})")
                    print(f"         Returned Quantity: {item['quantity']}")
                print()

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
