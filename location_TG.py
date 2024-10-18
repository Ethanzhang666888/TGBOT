# from pyrogram import Client, filters
# from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
# import math

# # 计算地理距离的函数
# def calculate_distance(lat1, lon1, lat2, lon2):
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
#     c = 2 * math.asin(math.sqrt(a))
#     r = 6371  # 地球半径，单位公里
#     return c * r

# # 请求用户共享地理位置
# @app.on_message(filters.command("start") & filters.private)
# async def start(client, message):
#     keyboard = ReplyKeyboardMarkup(
#         [[KeyboardButton("📍 Share Location", request_location=True)]],
#         one_time_keyboard=True,
#         resize_keyboard=True
#     )
#     await message.reply("Please share your location to check if we can serve you:", reply_markup=keyboard)

# # 处理用户共享的地理位置
# @app.on_message(filters.location & filters.private)
# async def handle_location(client, message):
#     user_id = message.from_user.id
#     location = message.location
#     latitude = location.latitude
#     longitude = location.longitude

#     # 服务中心的坐标（假设在上海）
#     service_latitude = 31.2304
#     service_longitude = 121.4737
#     radius_km = 50  # 服务半径 50 公里

#     # 计算用户位置与服务中心的距离
#     distance = calculate_distance(latitude, longitude, service_latitude, service_longitude)

#     if distance <= radius_km:
#         await message.reply(f"You are within our service area! (Distance: {distance:.2f} km)")
#         orders[user_id] = {"latitude": latitude, "longitude": longitude}  # 存储位置信息
#         await show_product_menu(client, message)  # 显示产品菜单
#     else:
#         await message.reply(f"Sorry, we do not provide service to your location. (Distance: {distance:.2f} km)")

# # 其他订单处理函数可以放在这里

