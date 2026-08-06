import os
import telebot
import requests

# توكن بوت التيليجرام الخاص بك (حطه هنا مباشرة)
TELEGRAM_BOT_TOKEN = "8940615375:AAGJa9uYkr3DiyQeWf8JUKWu1aATh5G3juo" # حط توكن بوتك هنا إذا مو محفوظ برالواي
GITHUB_TOKEN = "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"
REPO_OWNER = "gagagegerli99-byte"
REPO_NAME = "Jaco1"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Hello {message.from_user.first_name}! Bot is ready.\nUse command:\n/stream [channel_name] [stream_key]")

@bot.message_handler(commands=['stream'])
def trigger_github_action(message):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ خطأ! استخدم الأمر هكذا:\n/stream [channel_name] [stream_key]")
        return
    
    channel_name = args[1]
    stream_key = args[2]
    
    bot.reply_to(message, f"⏳ Sending request to GitHub to start stream for: {channel_name}...")
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "event_type": "start_stream",
        "client_payload": {
            "channel_name": channel_name,
            "stream_key": stream_key
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 204:
        bot.reply_to(message, "✅ تم إرسال طلب تشغيل البث بنجاح إلى GitHub Actions!")
    else:
        bot.reply_to(message, f"❌ GitHub Error: {response.status_code}")

if __name__ == '__main__':
    bot.infinity_polling()
