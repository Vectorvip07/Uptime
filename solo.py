import os
import time
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
import telebot

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_BOT_TOKEN"  # Get from @BotFather
ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID") or "YOUR_ADMIN_ID"     # Your Telegram ID
bot = telebot.TeleBot(BOT_TOKEN)

# Uptime tracking
bot_start_time = datetime.now()
active_chats = set()
uptime_thread = None

def format_uptime(uptime):
    """Format uptime into human-readable string"""
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts)

def uptime_monitor():
    """Send uptime updates every minute to active chats"""
    while True:
        try:
            current_time = datetime.now()
            uptime = current_time - bot_start_time
            formatted_uptime = format_uptime(uptime)
            
            message = (
                "🤖 Bot Status Update\n\n"
                f"⏱ Uptime: {formatted_uptime}\n"
                f"🕒 Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"👥 Active users: {len(active_chats)}"
            )
            
            # Send to all active chats
            for chat_id in list(active_chats):
                try:
                    bot.send_message(chat_id, message)
                except Exception as e:
                    print(f"Failed to send to {chat_id}: {e}")
                    active_chats.discard(chat_id)
                    
        except Exception as e:
            print(f"Uptime monitor error: {e}")
        
        time.sleep(60)  # Wait 1 minute

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start command"""
    active_chats.add(message.chat.id)
    uptime = datetime.now() - bot_start_time
    
    bot.reply_to(
        message,
        f"🤖 Hello! I'm your Telegram bot\n\n"
        f"⏱ Uptime: {format_uptime(uptime)}\n"
        f"🚀 Started at: {bot_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "You'll now receive automatic updates every minute.\n"
        "Use /uptime to check current status anytime.\n"
        "Use /stop to disable updates."
    )

@bot.message_handler(commands=['uptime'])
def send_uptime(message):
    """Handle /uptime command"""
    uptime = datetime.now() - bot_start_time
    bot.reply_to(
        message,
        f"⏱ Bot has been running for {format_uptime(uptime)}\n"
        f"🕒 Started at: {bot_start_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

@bot.message_handler(commands=['stop'])
def stop_updates(message):
    """Handle /stop command"""
    if message.chat.id in active_chats:
        active_chats.remove(message.chat.id)
        bot.reply_to(message, "🔕 You'll no longer receive updates")
    else:
        bot.reply_to(message, "ℹ️ You're not currently receiving updates")

def fake_web_server():
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Bot is running!"

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=fake_web_server).start()
    uptime_thread = threading.Thread(target=uptime_monitor, daemon=True)
    uptime_thread.start()
    bot.send_message(
        ADMIN_ID,
        f"🤖 Bot started at {bot_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "Ready to receive commands!"
    )
    bot.infinity_polling()