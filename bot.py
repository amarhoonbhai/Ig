import logging
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

# --- Configuration ---
TOKEN = "7699253029:AAHljsbBWy50_7wC_nylLoJZbNwtTz6EqkM"  # Replace with your bot token
CHAT_ID = 8186031426  # Replace with your Telegram chat ID (for alerts)
USERNAMES_TO_MONITOR = ["example_user1", "example_user2"]  # Replace with actual usernames

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Core Function ---
def is_instagram_banned(username):
    """Check if an Instagram account is banned (True), active (False), or unknown (None)."""
    url = f"https://www.instagram.com/{username}/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return True
        elif response.status_code == 200:
            return False
        else:
            return None
    except Exception as e:
        logger.error(f"Error checking {username}: {e}")
        return None

# --- Bot Commands ---
async def ban(update: Update, context: CallbackContext):
    """Command: /ban <username> — Check if the IG account is banned"""
    if not context.args:
        await update.message.reply_text("Usage: /ban <username>")
        return

    username = context.args[0]
    status = is_instagram_banned(username)

    if status is None:
        await update.message.reply_text(f"⚠️ Could not verify {username}'s status.")
    elif status:
        await update.message.reply_text(f"🚨 {username} appears to be BANNED on Instagram!")
    else:
        await update.message.reply_text(f"✅ {username} is active on Instagram.")

async def unban(update: Update, context: CallbackContext):
    """Command: /unban <username> — Check if the IG account is unbanned"""
    if not context.args:
        await update.message.reply_text("Usage: /unban <username>")
        return

    username = context.args[0]
    status = is_instagram_banned(username)

    if status is None:
        await update.message.reply_text(f"⚠️ Could not verify {username}'s status.")
    elif status:
        await update.message.reply_text(f"❌ {username} is still banned.")
    else:
        await update.message.reply_text(f"🎉 {username} is UNBANNED and active on Instagram!")

# --- Background Monitor Task ---
async def monitor_instagram(application):
    """Monitor predefined Instagram usernames and alert on status change."""
    last_status = {user: is_instagram_banned(user) for user in USERNAMES_TO_MONITOR}
    await asyncio.sleep(10)

    while True:
        for username in USERNAMES_TO_MONITOR:
            current_status = is_instagram_banned(username)
            if current_status is not None and current_status != last_status[username]:
                msg = f"🚨 {username} has been BANNED!" if current_status else f"🎉 {username} is now UNBANNED!"
                await application.bot.send_message(chat_id=CHAT_ID, text=msg)
                last_status[username] = current_status

        await asyncio.sleep(300)  # Check every 5 minutes

# --- Main Bot Runner ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))

    # Background task setup
    app.job_queue.run_once(lambda _: asyncio.create_task(monitor_instagram(app)), 1)

    print("Bot is running...")
    app.run_polling()

# --- Start ---
if __name__ == "__main__":
    main()
