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
        [InlineKeyboardButton("Quantity 1", callback_data="quantity1"), InlineKeyboardButton("Quantity 2", callback_data="quantity2")],
        [InlineKeyboardButton("Quantity 3", callback_data="quantity3"), InlineKeyboardButton("Quantity 4", callback_data="quantity4")],
        [InlineKeyboardButton("Quantity 5", callback_data="quantity5"), InlineKeyboardButton("Quantity 6", callback_data="quantity6")],
        [InlineKeyboardButton("Quantity 7", callback_data="quantity7"), InlineKeyboardButton("Quantity 8", callback_data="quantity8")],
        [InlineKeyboardButton("Quantity 9", callback_data="quantity9"), InlineKeyboardButton("Quantity 10", callback_data="quantity10")]
    ]
    await callback_query.message.edit_text("Please select the quantity:", reply_markup=InlineKeyboardMarkup(buttons))

# Step 5: Handle quantity selection and complete the order
@app.on_callback_query(filters.regex("quantity"))
async def select_quantity(client, callback_query):
    quantity = callback_query.data
    user_id = callback_query.from_user.id

    # Ensure the user has already selected a product and initialized an order
    if user_id not in orders or "current_product" not in orders[user_id]:
        await callback_query.message.reply("Error: You need to select a product first.")
        return

    # Add the selected product and quantity to the items list
    product = orders[user_id].pop("current_product")
    orders[user_id]["items"].append({"product": product, "quantity": quantity})

    # Ask if they need anything else
    buttons = [
        [InlineKeyboardButton("Need More", callback_data="need_more"), InlineKeyboardButton("Do Not Need", callback_data="do_not_need")]
    ]
    await callback_query.message.edit_text("Your product has been added. Do you need anything else?", reply_markup=InlineKeyboardMarkup(buttons))

# Step 6: Handle the "Need More" and "Do Not Need" options
@app.on_callback_query(filters.regex("need_more"))
async def need_more(client, callback_query):
    # Repeat product selection without sending new messages
    await show_product_menu(client, callback_query.message)

@app.on_callback_query(filters.regex("do_not_need"))
async def do_not_need(client, callback_query):
    user_id = callback_query.from_user.id

    # Add order to the queue
    order_queue.put(user_id)

    # Final message to user
    await callback_query.message.edit_text(f"Your order has been placed. Please contact customer service {CUSTOMER_SERVICE} in the channel to obtain the payment link.")

# Function to process orders from the queue
def process_orders():
    while True:
        user_id = order_queue.get()
        if user_id in orders:
            order_info = orders[user_id]
            address = order_info["address"]

            # Create a new SQLite connection in this thread
            conn = sqlite3.connect('orders.db')
            c = conn.cursor()

            for item in order_info["items"]:
                product = item["product"]
                quantity = item["quantity"]

                # Store order in the database
                c.execute("INSERT INTO orders (user_id, address, product, quantity) VALUES (?, ?, ?, ?)",
                          (user_id, address, product, quantity))
                conn.commit()

                # Send order details to the channel
                app.send_message(
                    CHANNEL_USERNAME,
                    f"New order:\nUser ID: {user_id}\nAddress: {address}\nProduct: {product}\nQuantity: {quantity}"
                )

            # Close the SQLite connection
            conn.close()

            # Optionally, clear the user's order data
            orders.pop(user_id, None)

# Start the order processing thread
order_thread = threading.Thread(target=process_orders, daemon=True)
order_thread.start()

app.run()
