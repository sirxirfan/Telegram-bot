import telebot

TOKEN = "7449484539:AAHkYeeSDJ92cT7wrYZBWZTWx4b_K-flbEM"
CHANNEL = "@irfanplugs"

bot = telebot.TeleBot(TOKEN)

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.from_user.id):
        bot.reply_to(message, "✅ Aap channel join kar chuke ho, ab bot use kar sakte ho!")
    else:
        bot.reply_to(message, f"❌ Pehle channel join karo: {CHANNEL}")

bot.polling()
