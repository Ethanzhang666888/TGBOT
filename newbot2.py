import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import queue
import threading

# Your bot API details
API_ID = "24583730"
API_HASH = "cc02358562bc1ebf7999106298defb21"
BOT_TOKEN = "7234753304:AAFY9BKOqjPETb6rpngE1GY6IqHqWfglyEk"
SERVICE_CITY = "Shanghai"  # Example service city, update as necessary
CHANNEL_USERNAME = "@PinDaoA1"  # Channel where the order will be sent
CUSTOMER_SERVICE = "@Ethan666888"  # Customer service contact

app = Client("bot_b", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# This dictionary stores the order information per user
orders = {}

# Order queue
order_queue = queue.Queue()

# Step 1: Ask for the address
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("Welcome! Please provide your address to check if we can serve you:")

# Step 2: Verify the address
@app.on_message(filters.text & filters.private)
async def check_address(client, message):
    user_id = message.from_user.id
    address = message.text.lower()

    if SERVICE_CITY.lower() in address:
        orders[user_id] = {"address": address, "items": []}  # Store the address and initialize items list
        # Show product menu if within service area
        await show_product_menu(client, message)
    else:
        await message.reply("Sorry, we cannot provide service to your area.")

# Step 3: Show the product selection menu
async def show_product_menu(client, message):
    buttons = [
        [InlineKeyboardButton("Product 1", callback_data="product1"), InlineKeyboardButton("Product 2", callback_data="product2")],
        [InlineKeyboardButton("Product 3", callback_data="product3"), InlineKeyboardButton("Product 4", callback_data="product4")],
        [InlineKeyboardButton("Product 5", callback_data="product5"), InlineKeyboardButton("Product 6", callback_data="product6")],
        [InlineKeyboardButton("Product 7", callback_data="product7"), InlineKeyboardButton("Product 8", callback_data="product8")],
        [InlineKeyboardButton("Product 9", callback_data="product9"), InlineKeyboardButton("Product 10", callback_data="product10")]
    ]
    await message.reply("Please select a product:", reply_markup=InlineKeyboardMarkup(buttons))

# Step 4: Handle product selection and initialize the order
@app.on_callback_query(filters.regex("product"))
async def select_product(client, callback_query):
    product = callback_query.data
    user_id = callback_query.from_user.id

    # Ensure that the user has an entry in the orders dictionary
    if user_id not in orders:
        orders[user_id] = {"items": []}  # Initialize if not already present

    # Store selected product temporarily
    orders[user_id]["current_product"] = product

    # Show quantity options
    buttons = [
        [InlineKeyboardButton("Quantity 1", callback_data="quantity_1"), InlineKeyboardButton("Quantity 2", callback_data="quantity_2")],
        [InlineKeyboardButton("Quantity 3", callback_data="quantity_3"), InlineKeyboardButton("Quantity 4", callback_data="quantity_4")],
        [InlineKeyboardButton("Quantity 5", callback_data="quantity_5"), InlineKeyboardButton("Quantity 6", callback_data="quantity_6")],
        [InlineKeyboardButton("Quantity 7", callback_data="quantity_7"), InlineKeyboardButton("Quantity 8", callback_data="quantity_8")],
        [InlineKeyboardButton("Quantity 9", callback_data="quantity_9"), InlineKeyboardButton("Quantity 10", callback_data="quantity_10")]
    ]
    await callback_query.message.edit_text("Please select the quantity:", reply_markup=InlineKeyboardMarkup(buttons))

# Step 5: Handle quantity selection and complete the order
@app.on_callback_query(filters.regex("quantity"))
async def select_quantity(client, callback_query):
    quantity = callback_query.data.split("_")[1]  # Extract the quantity number
    # quantity = callback_query.data
    user_id = callback_query.from_user.id

    # Validate quantity
    try:
        quantity = int(quantity)  # Convert to integer
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
    except ValueError as e:
        await callback_query.message.reply("Error: Invalid quantity selected.")
        return

    # Ensure the user has already selected a product and initialized an order
    if user_id not in orders or "current_product" not in orders[user_id]:
        await callback_query.message.reply("Error: You need to select a product first.")
        return

    # Add the selected product and quantity to the items list
    product = orders[user_id].pop("current_product")
    orders[user_id]["items"].append({"product": product, "quantity": quantity})

    # Provide feedback on the current order
    current_items = ', '.join(f"{item['quantity']} x {item['product']}" for item in orders[user_id]["items"])
    await callback_query.message.edit_text(f"Your order: {current_items}. Do you need anything else?", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("Need More", callback_data="need_more"), 
                                                 InlineKeyboardButton("Do Not Need", callback_data="do_not_need")]
                                            ]))

# Step 6: Handle the "Need More" and "Do Not Need" options
@app.on_callback_query(filters.regex("need_more"))
async def need_more(client, callback_query):
    user_id = callback_query.from_user.id

    # Assuming show_product_menu displays the product selection and quantity options
    await show_product_menu(client, callback_query.message)

    # After showing the menu, the user can select another product and quantity

@app.on_callback_query(filters.regex("do_not_need"))
async def do_not_need(client, callback_query):
    user_id = callback_query.from_user.id

    # Add order to the queue
    order_queue.put(user_id)

    # Final message to user
    await callback_query.message.edit_text(f"Your order has been placed. Please contact customer service {CUSTOMER_SERVICE} in the channel to obtain the payment link.")


# Function to process orders from the queue
def process_orders():
    order_summary = []  # 创建一个列表来汇总所有订单
    while True:
        user_id = order_queue.get()
        if user_id in orders:
            order_info = orders[user_id]
            address = order_info["address"]

            # 汇总订单信息
            for item in order_info["items"]:
                product = item["product"]
                quantity = item["quantity"]
                order_summary.append(f"User ID: {user_id}, Address: {address}, Product: {product}, Quantity: {quantity}")

            # Optionally, clear the user's order data
            orders.pop(user_id, None)

        # 当处理完所有订单后，发送汇总信息
        if not order_queue.empty():
            continue
        
        # 发送汇总的订单信息
        if order_summary:
            summary_message = "\n".join(order_summary)
            app.send_message(CHANNEL_USERNAME, f"New Orders:\n{summary_message}")

        # 清空汇总列表以备下次使用
        order_summary.clear()

# Start the order processing thread
order_thread = threading.Thread(target=process_orders, daemon=True)
order_thread.start()


app.run()







# # This dictionary stores the order information per user
# orders = {}

# # Step 3: Show the product selection menu
# async def show_product_menu(client, message):
#     buttons = [
#         [InlineKeyboardButton("Product 1", callback_data="product1"), InlineKeyboardButton("Product 2", callback_data="product2")],
#         [InlineKeyboardButton("Product 3", callback_data="product3"), InlineKeyboardButton("Product 4", callback_data="product4")],
#         [InlineKeyboardButton("Product 5", callback_data="product5"), InlineKeyboardButton("Product 6", callback_data="product6")],
#         [InlineKeyboardButton("Product 7", callback_data="product7"), InlineKeyboardButton("Product 8", callback_data="product8")],
#         [InlineKeyboardButton("Finish Order", callback_data="finish_order")]  # Add a button to finish the order
#     ]
#     await message.reply("Please select a product:", reply_markup=InlineKeyboardMarkup(buttons))

# # Step 4: Handle product selection and initialize the order
# @app.on_callback_query(filters.regex("product"))
# async def select_product(client, callback_query):
#     user_id = callback_query.from_user.id
#     product_selected = callback_query.data

#     if user_id not in orders:
#         orders[user_id] = {"address": "", "products": []}  # Initialize order for the user

#     orders[user_id]["products"].append(product_selected)  # Store the selected product
#     await callback_query.answer(f"You have selected {product_selected}.")
    
#     # Show the product menu again for more selections
#     await show_product_menu(client, callback_query.message)

# # Step 5: Finish the order and send to the channel
# @app.on_callback_query(filters.regex("finish_order"))
# async def finish_order(client, callback_query):
#     user_id = callback_query.from_user.id

#     if user_id in orders and orders[user_id]["products"]:
#         order_info = orders[user_id]
#         products_list = ', '.join(order_info["products"])  # Create a string of selected products

#         # Create a message with order details
#         message = f"New Order:\n\nAddress: {order_info['address']}\nProducts: {products_list}\nCustomer Service: {CUSTOMER_SERVICE}"

#         # Send the order details to the designated channel
#         await client.send_message(CHANNEL_USERNAME, message)

#         # Inform the user
#         await callback_query.message.reply("Your order has been placed! We will contact you shortly.")
#         # Clear the user's order
#         del orders[user_id]
#     else:
#         await callback_query.answer("You have no products in your order.")

# # Run the bot
# app.run()
