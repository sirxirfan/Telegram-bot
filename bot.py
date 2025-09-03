import telebot
from telebot import types

BOT_TOKEN = "7449484539:AAHkYeeSDJ92cT7wrYZBWZTWx4b_K-flbEM"
CHANNEL_ID = "@irfanplugs"

bot = telebot.TeleBot(BOT_TOKEN)

# Function to check if user is member of channel
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_member(user_id):
        # Agar user join kar chuka hai to menu dikhayenge
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📢 Channel", url="https://t.me/irfanplugs")
        btn2 = types.InlineKeyboardButton("✨ Say Hello", callback_data="hello")
        markup.add(btn1, btn2)
        
        bot.send_message(message.chat.id, "✅ You are verified!\nChoose an option below:", reply_markup=markup)
    else:
        # Agar join nahi kiya hai to force join
        markup = types.InlineKeyboardMarkup()
        join_btn = types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/irfanplugs")
        check_btn = types.InlineKeyboardButton("✅ I've Joined", callback_data="check")
        markup.add(join_btn, check_btn)
        
        bot.send_message(message.chat.id, "❌ You must join our channel first!", reply_markup=markup)

# Button handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if call.data == "check":
        if is_member(user_id):
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("📢 Channel", url="https://t.me/irfanplugs")
            btn2 = types.InlineKeyboardButton("✨ Say Hello", callback_data="hello")
            markup.add(btn1, btn2)
            bot.send_message(call.message.chat.id, "✅ Verified! Welcome to the bot menu:", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined yet!")
    elif call.data == "hello":
        bot.send_message(call.message.chat.id, "Hello from your bot! 😎")

print("Bot is running...")
bot.infinity_polling()
