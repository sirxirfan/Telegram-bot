import telebot
import requests
import os
from telebot import types
import logging
from flask import Flask
from threading import Thread

# -------------------------
# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Environment variable for BOT_TOKEN
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

bot = telebot.TeleBot(BOT_TOKEN)
CHANNEL_USERNAME = "@irfanplugs"
OWNER_ID = 6405915792  # Your Telegram ID

# Users who joined
joined_users = {}

# -------------------------
# Keep-alive server for Railway / Replit
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# -------------------------
# /start command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Notify owner
    bot.send_message(OWNER_ID, f"New user started the bot!\nUser ID: {user_id}\nUsername: {message.from_user.username or 'None'}\nChat ID: {chat_id}")

    if str(user_id) not in joined_users:
        markup = types.InlineKeyboardMarkup(row_width=2)
        join_button = types.InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        check_button = types.InlineKeyboardButton("✅ Check Join", callback_data="check_join")
        reset_button = types.InlineKeyboardButton("🔄 Reset Link", callback_data="reset_link")
        markup.add(join_button, check_button, reset_button)
        bot.send_message(chat_id, f"Please join {CHANNEL_USERNAME} to use the bot!", reply_markup=markup)
    else:
        bot.send_message(chat_id, "You're verified! Use /reset or the button below to request a password reset link.")

# -------------------------
# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == "check_join":
        try:
            member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                joined_users[str(user_id)] = True
                bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                      text="✅ Verified! You can now request a password reset link.")
            else:
                bot.answer_callback_query(call.id, "❌ You haven't joined the channel yet. Please join and try again.")
        except Exception as e:
            logger.error(f"Membership error for user_id {user_id}: {str(e)}")
            bot.answer_callback_query(call.id, f"Error checking membership: {str(e)}")

    elif call.data == "reset_link":
        if str(user_id) not in joined_users:
            bot.answer_callback_query(call.id, f"Please join {CHANNEL_USERNAME} and use /start first.")
            return
        bot.send_message(chat_id, "Send your Instagram username or email to request a password reset link.")
        bot.register_next_step_handler(call.message, process_reset)

# -------------------------
# /reset command
@bot.message_handler(commands=['reset'])
def reset(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if str(user_id) not in joined_users:
        bot.send_message(chat_id, f"Please join {CHANNEL_USERNAME} and use /start to verify first.")
        return

    bot.send_message(chat_id, "Send your Instagram username or email to request a password reset link.")
    bot.register_next_step_handler(message, process_reset)

# -------------------------
# Process reset
def process_reset(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    query = message.text.strip()

    if str(user_id) not in joined_users:
        bot.send_message(chat_id, "Please verify by joining the channel first.")
        return

    api_url = f"https://insta-pass-reset-eternal.vercel.app/?username={query}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "Password reset link sent.":
                email = data.get("email", "your associated email")
                bot.send_message(chat_id, f"✅ Reset link sent to {email}! Check spam if not received.")
                return
        bot.send_message(chat_id, "❌ Error: Could not send reset link. Try again or check input.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}. Try again later.")

# -------------------------
# Start bot
bot.infinity_polling()
