Import telebot
import threading
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = "8068960429:AAFZRUj-SD1RWlNjW9pFpmGIyMf2qYwizqU"
OWNER_ID = "6405915792"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
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

# --- FAST BROADCAST ---
def send_msg(user, text):
    try: bot.send_message(user, f"📢 *Notification:*\n\n{text}", parse_mode="Markdown")
    except: pass

def perform_broadcast(text):
    users = get_users()
    for u in users:
        threading.Thread(target=send_msg, args=(u, text)).start()

# --- KEYBOARDS ---
def get_user_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("🔄 Reset")
    return kb

def get_admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("🔄 Reset", "📊 Dashboard", "📢 Broadcast", "📁 Users List")
    return kb

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    save_user(user_id)
    
    # Inline button for Channel
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/irfanplugs"))
    
    if str(user_id) == OWNER_ID:
        # Admin Panel Menu
        bot.send_message(user_id, "👑 *Admin Panel Ready*", reply_markup=get_admin_kb(), parse_mode="Markdown")
    else:
        # Welcome message + Attached Button
        welcome_text = f"👋 *Welcome, {message.from_user.first_name}!*\n\nYou can join our channel for updates."
        bot.send_message(user_id, welcome_text, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(user_id, "Use the '🔄 Reset' button below.", reply_markup=get_user_kb())

@bot.message_handler(func=lambda m: m.text == "📊 Dashboard" and str(m.chat.id) == OWNER_ID)
def dashboard(m):
    users = get_users()
    bot.reply_to(m, f"📊 *Live Analytics*\n\n👥 Total Users: `{len(users)}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📁 Users List" and str(m.chat.id) == OWNER_ID)
def show_list(m):
    users = get_users()
    if not users: bot.reply_to(m, "📂 No users found.")
    else:
        user_list = "\n".join([f"`{u}`" for u in users])
        bot.reply_to(m, f"📁 *Registered Users:*\n\n{user_list}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast" and str(m.chat.id) == OWNER_ID)
def ask_broadcast(m):
    msg = bot.reply_to(m, "📩 *Enter broadcast message:*")
    bot.register_next_step_handler(msg, lambda next_m: [perform_broadcast(next_m.text), bot.reply_to(next_m, "✅ *Broadcast Completed!*")])

@bot.message_handler(func=lambda m: m.text == "🔄 Reset")
def reset_ui(m):
    msg = bot.reply_to(m, "📧 *Enter Username or Email*")
    bot.register_next_step_handler(msg, lambda next_m: bot.reply_to(next_m, "✅ *Reset link sent successfully!*", parse_mode="Markdown"))

# Sabse neeche ka code ye kar do:
print("🚀 Bot is running fast...")
while True:
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Error occurred: {e}")
        import time
        time.sleep(5) # 5 second wait karke restart hoga
        
