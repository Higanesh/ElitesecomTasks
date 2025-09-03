# from shopify_module import * 

# # Create a new customer
# new_customer = create_customer()
# print(new_customer)

# # create a new order
# new_order = create_module.create_order()
# print(new_order)

# # Create a new product
# new_product = create_module.create_product()
# shopify.ShopifyResource.clear_session()
# print(new_product)
# print("closed session")

# # Create a new manual collection
# new_manual_collection = create_module.create_manual_collection()
# print(new_manual_collection)

# # create a new smart collection
# new_smart_collection = create_module.create_smart_collection()
# print(new_smart_collection)

# # get listing of products
# get_listing = products_and_orders.get_listing()
# print(get_listing)

# # push inventory from excel to shopify
# push_inventory = products_and_orders.push_inventory()
# print(push_inventory)

# # fetch products by date range
# fetch_products = products_and_orders.fetch_products_by_date()
# print(fetch_products)

# # return and refund a specific order
# order_input = input("Enter Shopify Order Number (e.g. 1035) or Order ID: ").strip()
# order = return_and_refund.get_order(order_input)

# if order:
#     return_and_refund.create_return(order)
#     return_and_refund.create_refund(order)
# else:
#     print("Order not found.")