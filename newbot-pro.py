import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import queue
import threading


   
API_ID = "24583730"
API_HASH = "cc02358562bc1ebf7999106298defb21"
BOT_TOKEN = "7234753304:AAFY9BKOqjPETb6rpngE1GY6IqHqWfglyEk"
SERVICE_CITY = "London"  
CHANNEL_USERNAME = "-1002422479020"  
CUSTOMER_SERVICE = "@Ethan666888"  


app = Client("bot_b", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

orders = {}
user_addresses = {}  

order_queue = queue.Queue()

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
   
    if user_id not in user_addresses:
        await message.reply("welcome! Please provide your address to verify the service scope:")
    else:
        await show_help_menu(client, message)  

@app.on_message(filters.text & filters.private)
async def check_address(client, message):
    user_id = message.from_user.id
    address = message.text.lower()

    if SERVICE_CITY.lower() in address:
        user_addresses[user_id] = address  
        orders[user_id] = {"address": address, "items": []}  
        await show_help_menu(client, message)  
    else:
        await message.reply("Due to the scope of our business address, we are unable to provide services to you. If you have any special needs, please contact our live customer service.")

async def show_help_menu(client, message):
    buttons = [
        [InlineKeyboardButton("Order Menu", callback_data="show_order_menu"),
         InlineKeyboardButton("Contact Customer Service", url=f"https://t.me/{CUSTOMER_SERVICE}")]
    ]
    await message.reply("Please choose an option:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("show_order_menu"))
async def show_product_menu(client, callback_query):
    buttons = [
        [InlineKeyboardButton("Product 1", callback_data="product1"), InlineKeyboardButton("Product 2", callback_data="product2")],
        [InlineKeyboardButton("Product 3", callback_data="product3"), InlineKeyboardButton("Product 4", callback_data="product4")],
        [InlineKeyboardButton("Product 5", callback_data="product5"), InlineKeyboardButton("Product 6", callback_data="product6")],
        [InlineKeyboardButton("Product 7", callback_data="product7"), InlineKeyboardButton("Product 8", callback_data="product8")],
        [InlineKeyboardButton("Product 9", callback_data="product9"), InlineKeyboardButton("Product 10", callback_data="product10")]
        
    ]
    await callback_query.message.edit_text("Please select a product:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("product"))
async def select_product(client, callback_query):
    product = callback_query.data
    user_id = callback_query.from_user.id
  
    if user_id not in orders:
        orders[user_id] = {"items": []}  
  
    orders[user_id]["current_product"] = product
   
    buttons = [
        [InlineKeyboardButton("Quantity 1", callback_data="quantity_1"), InlineKeyboardButton("Quantity 2", callback_data="quantity_2")],
        [InlineKeyboardButton("Quantity 3", callback_data="quantity_3"), InlineKeyboardButton("Quantity 4", callback_data="quantity_4")],
        [InlineKeyboardButton("Quantity 5", callback_data="quantity_5"), InlineKeyboardButton("Quantity 6", callback_data="quantity_6")],
        [InlineKeyboardButton("Quantity 7", callback_data="quantity_7"), InlineKeyboardButton("Quantity 8", callback_data="quantity_8")],
        [InlineKeyboardButton("Quantity 9", callback_data="quantity_9"), InlineKeyboardButton("Quantity 10", callback_data="quantity_10")]
    ]
    await callback_query.message.edit_text("Please select the quantity:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("quantity"))
async def select_quantity(client, callback_query):
    quantity = callback_query.data.split("_")[1]  
    
    user_id = callback_query.from_user.id
   
    try:
        quantity = int(quantity)  
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
    except ValueError as e:
        await callback_query.message.reply("Error: Invalid quantity selected.")
        return
  
    if user_id not in orders or "current_product" not in orders[user_id]:
        await callback_query.message.reply("Error: You need to select a product first.")
        return
 
    product = orders[user_id].pop("current_product")
    orders[user_id]["items"].append({"product": product, "quantity": quantity})
    
    current_items = ', '.join(f"{item['quantity']} x {item['product']}" for item in orders[user_id]["items"])
    await callback_query.message.edit_text(f"Your order: {current_items}. Do you need anything else?", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("Need More", callback_data="need_more"), 
                                                 InlineKeyboardButton("Do Not Need", callback_data="do_not_need")]
                                            ]))

@app.on_callback_query(filters.regex("need_more"))
async def need_more(client, callback_query):
    user_id = callback_query.from_user.id
    
    await show_product_menu(client, callback_query)

@app.on_callback_query(filters.regex("do_not_need"))
async def do_not_need(client, callback_query):
    user_id = callback_query.from_user.id
    
    order_queue.put(user_id)
    
    await callback_query.message.edit_text(f"Your order has been placed. Please contact customer service {CUSTOMER_SERVICE} in the channel to obtain the payment link.")

def process_orders():
    while True:
        user_id = order_queue.get()
        if user_id in orders:
            order_info = orders[user_id]
            address = order_info.get("address")  

            if not address:
                continue  
         
            order_summary = []  
            for item in order_info["items"]:
                product = item["product"]
                quantity = item["quantity"]
                order_summary.append(f"User ID: {user_id}, Address: {address}, Product: {product}, Quantity: {quantity}")
           
            if order_summary:
                summary_message = "\n".join(order_summary)
                app.send_message(CHANNEL_USERNAME, f"New Orders:\n{summary_message}")

                app.send_message(CUSTOMER_SERVICE, f"New Orders:\n{summary_message}")

                app.send_message(user_id, f"New Orders:\n{summary_message}")          
            
            orders.pop(user_id, None)

order_thread = threading.Thread(target=process_orders, daemon=True)
order_thread.start()

app.run()
