import sqlite3
from pyrogram import Client, filters




# Your bot API details
API_ID = "24583730"
API_HASH = "cc02358562bc1ebf7999106298defb21"
BOT_TOKEN = "7234753304:AAFY9BKOqjPETb6rpngE1GY6IqHqWfglyEk"
SERVICE_CITY = "上海"  # Example service city, update as necessary
CHANNEL_USERNAME = "@PinDaoA1"  # Channel where the order will be sent
CUSTOMER_SERVICE = "@Ethan666888"  # Customer service contact
CUSTOMER = "1665269506"


app = Client("bot_b", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# async def test_send_message():
#     async with app:
#         try:
#             await app.send_message("@PinDaoA1", "测试消息")
#             print("消息发送成功！")
#         except Exception as e:
#             print(f"发送消息失败: {e}")


# app.run(test_send_message())


async def send_test_message():
    async with app:
        try:
            user_id = CUSTOMER  # 替换为实际的用户 ID
            await app.send_message(user_id, "测试消息")
            print("消息发送成功！")
        except Exception as e:
            print(f"发送消息失败: {e}")

app.run(send_test_message())
