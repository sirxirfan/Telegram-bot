from telebot import TeleBot, types

API_TOKEN = "7449484539:AAHkYeeSDJ92cT7wrYZBWZTWx4b_K-flbEM"
CHANNEL_ID = "@irfanplugs"

bot = TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
    except Exception as e:
        bot.reply_to(message, "⚠️ Bot ko channel ka admin banao tabhi ye work karega!")
        return
    
    if status in ["member", "administrator", "creator"]:
        bot.reply_to(message, "✅ Aap channel join kar chuke ho! Welcome 🙌")
    else:
        markup = types.InlineKeyboardMarkup()
        join_btn = types.InlineKeyboardButton("📢 Channel Join Karo", url=f"https://t.me/{CHANNEL_ID[1:]}")
        check_btn = types.InlineKeyboardButton("✅ Check", callback_data="check")
        markup.add(join_btn)
        markup.add(check_btn)
        bot.reply_to(message, "❌ Pehle channel join karo, tabhi bot use kar sakte ho!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def callback_check(call):
    user_id = call.from_user.id
    status = bot.get_chat_member(CHANNEL_ID, user_id).status
    if status in ["member", "administrator", "creator"]:
        bot.edit_message_text("✅ Verified! Ab aap bot use kar sakte ho 🙌", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Abhi tak join nahi kiya!")

print("🤖 Bot chal raha hai...")
bot.polling()
