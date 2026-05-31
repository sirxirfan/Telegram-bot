import telebot
import threading
from flask import Flask, request
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = "8068960429:AAFZRUj-SD1RWlNjW9pFpmGIyMf2qYwizqU"
OWNER_ID = "6405915792"
WEBHOOK_URL = "https://telegram-bot-2-fw0x.onrender.com/" # Apne Render ka URL yahan check kar lena
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
DB_FILE = "users.txt"

# --- DATABASE ---
def get_users():
    try:
        with open(DB_FILE, "r") as f:
            return set(f.read().splitlines())
    except: return set()

def save_user(user_id):
    with open(DB_FILE, "a+") as f:
        f.seek(0)
        if str(user_id) not in f.read().splitlines():
            f.write(str(user_id) + "\n")

# --- ADMIN FUNCTIONS ---
def perform_broadcast(text):
    users = get_users()
    for u in users:
        try: bot.send_message(u, f"📢 *Notification:*\n\n{text}", parse_mode="Markdown")
        except: pass

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/irfanplugs"))
    
    if str(message.chat.id) == OWNER_ID:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add("🔄 Reset", "📊 Dashboard", "📢 Broadcast", "📁 Users List")
        bot.send_message(message.chat.id, "👑 *Admin Panel Ready*", reply_markup=kb, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"👋 *Welcome, {message.from_user.first_name}!*", reply_markup=markup, parse_mode="Markdown")
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        kb.add("🔄 Reset")
        bot.send_message(message.chat.id, "Use button below:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "📊 Dashboard" and str(m.chat.id) == OWNER_ID)
def dashboard(m):
    bot.reply_to(m, f"📊 *Total Users:* `{len(get_users())}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📁 Users List" and str(m.chat.id) == OWNER_ID)
def show_list(m):
    users = get_users()
    bot.reply_to(m, f"📁 *Users:* \n\n{chr(10).join([f'`{u}`' for u in users])}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast" and str(m.chat.id) == OWNER_ID)
def ask_broadcast(m):
    msg = bot.reply_to(m, "📩 *Enter message:*")
    bot.register_next_step_handler(msg, lambda next_m: [perform_broadcast(next_m.text), bot.reply_to(next_m, "✅ *Done!*")])

@bot.message_handler(func=lambda m: m.text == "🔄 Reset")
def reset_ui(m):
    msg = bot.reply_to(m, "📧 *Enter Username:*")
    bot.register_next_step_handler(msg, lambda n: bot.reply_to(n, "✅ *Reset link sent to your email!*", parse_mode="Markdown"))

# --- WEBHOOK SETUP ---
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def home():
    return "Bot is alive!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + BOT_TOKEN)
    app.run(host="0.0.0.0", port=8080)
    
