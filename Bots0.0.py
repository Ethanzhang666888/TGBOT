from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Your bot API details
API_ID = "24583730"
API_HASH = "cc02358562bc1ebf7999106298defb21"
BOT_TOKEN = "7504661150:AAElhsvrixOjnIHlurT66fEfed3RggJYlcw"
GROUP_CHAT_ID = -1002488290395  # Replace with the actual group chat ID you got


# This set will store the user IDs of users who have already been greeted
greeted_users = set()

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Automatically greet new users and show buttons when they join the group
@app.on_message(filters.new_chat_members & filters.chat(GROUP_CHAT_ID))
async def welcome(client, message):
    new_member = message.from_user
    
    # Only greet users who haven't been greeted before
    if new_member.id not in greeted_users:
        greeted_users.add(new_member.id)
        # Send the welcome message
        await client.send_message(GROUP_CHAT_ID, f"Welcome to the group, {new_member.mention}!")
        
        # Display buttons to join other groups
        buttons = [
            [InlineKeyboardButton("Group 1", url="https://t.me/+qlKflkRn0zc3ZWU1"), InlineKeyboardButton("Group 2", url="https://t.me/+UCjXoJP4LRhmZTI1")],
            [InlineKeyboardButton("Group 3", url="https://t.me/group3"), InlineKeyboardButton("Group 4", url="https://t.me/group4")],
            [InlineKeyboardButton("Group 5", url="https://t.me/group5"), InlineKeyboardButton("Group 6", url="https://t.me/group6")],
            [InlineKeyboardButton("Group 7", url="https://t.me/group7"), InlineKeyboardButton("Group 8", url="https://t.me/group8")],
            [InlineKeyboardButton("Group 9", url="https://t.me/group9"), InlineKeyboardButton("Group 10", url="https://t.me/group10")],
        ]
        await client.send_message(GROUP_CHAT_ID, "You can join other groups by clicking the buttons below:",
                                  reply_markup=InlineKeyboardMarkup(buttons))

# Command to show the group selection buttons again
@app.on_message(filters.command("groups", prefixes="/") & filters.chat(GROUP_CHAT_ID))
async def show_group_buttons(client, message):
    buttons = [
        [InlineKeyboardButton("Group 1", url="https://t.me/+qlKflkRn0zc3ZWU1"), InlineKeyboardButton("Group 2", url="https://t.me/+UCjXoJP4LRhmZTI1")],
        [InlineKeyboardButton("Group 3", url="https://t.me/group3"), InlineKeyboardButton("Group 4", url="https://t.me/group4")],
        [InlineKeyboardButton("Group 5", url="https://t.me/group5"), InlineKeyboardButton("Group 6", url="https://t.me/group6")],
        [InlineKeyboardButton("Group 7", url="https://t.me/group7"), InlineKeyboardButton("Group 8", url="https://t.me/group8")],
        [InlineKeyboardButton("Group 9", url="https://t.me/group9"), InlineKeyboardButton("Group 10", url="https://t.me/group10")],
    ]
    await message.reply("Here are the groups you can join:", reply_markup=InlineKeyboardMarkup(buttons))


app.run()

