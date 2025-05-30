import logging
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = "7699253029:AAHljsbBWy50_7wC_nylLoJZbNwtTz6EqkM"  # Replace with your bot token
CHAT_ID = 8186031426  # Replace with your Telegram chat ID (for alerts)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_instagram_banned(username):
    """Check if an Instagram account is banned (returns True/False/None)"""
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url)

    if response.status_code == 404:
        return True  # Account is likely banned
    elif response.status_code == 200:
        return False  # Account is active
    else:
        return None  # Uncertain status

async def ban(update: Update, context: CallbackContext):
    """Command: Check if an Instagram account is banned"""
    if not context.args:
        await update.message.reply_text("Usage: !ban <username>")
        return
    
    username = context.args[0]
    banned = is_instagram_banned(username)

    if banned is None:
        await update.message.reply_text(f"⚠️ Could not verify {username}'s status.")
    elif banned:
        await update.message.reply_text(f"🚨 {username} appears to be BANNED on Instagram!")
    else:
        await update.message.reply_text(f"✅ {username} is active on Instagram.")

async def unban(update: Update, context: CallbackContext):
    """Command: Check if an Instagram account is unbanned"""
    if not context.args:
        await update.message.reply_text("Usage: !unban <username>")
        return
    
    username = context.args[0]
    banned = is_instagram_banned(username)

    if banned is None:
        await update.message.reply_text(f"⚠️ Could not verify {username}'s status.")
    elif banned:
        await update.message.reply_text(f"❌ {username} is still banned.")
    else:
        await update.message.reply_text(f"🎉 {username} is UNBANNED and active on Instagram!")

async def monitor_instagram(application):
    """Background task: Monitors Instagram accounts for bans/unbans"""
    usernames = ["example_user1", "example_user2"]  # Add usernames to monitor
    last_status = {user: is_instagram_banned(user) for user in usernames}

    await asyncio.sleep(10)  # Delay before first check

    while True:
        for username in usernames:
            current_status = is_instagram_banned(username)

            if current_status is not None and current_status != last_status[username]:
                message = f"🚨 {username} has been BANNED!" if current_status else f"🎉 {username} has been UNBANNED!"
                await application.bot.send_message(chat_id=CHAT_ID, text=message)

            last_status[username] = current_status

        await asyncio.sleep(300)  # Check every 5 minutes

def main():
    """Main function to start the Telegram bot"""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))

    # Start monitoring in the background
    app.job_queue.run_once(lambda _: asyncio.create_task(monitor_instagram(app)), 1)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
