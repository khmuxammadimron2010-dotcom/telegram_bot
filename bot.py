import asyncio
import logging
from datetime import datetime, date
from telegram import Bot
from telegram.error import TelegramError, RetryAfter

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Put your new Bot Token here (after revoking the old one via @BotFather)
BOT_TOKEN = "8807049304:AAFhDhi4bNfUwSnhNIS9BwDpTF7ktzmD9u4"

# Channel username
CHANNEL_ID = "@khakimov_vip"

# Target date (August 24, 2026)
TARGET_DATE = date(2026, 8, 24)

# Interval set to 5 seconds to prevent Telegram API rate-limit bans
UPDATE_INTERVAL = 5


def format_time_difference(total_seconds, target_date):
    if total_seconds <= 0:
        return "🎉 *THE TIME HAS COME!* 🎉"
    
    days = total_seconds // 86400
    remaining = total_seconds % 86400
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    seconds = remaining % 60
    
    return (
        f"⏰ *LIVE COUNTDOWN*\n\n"
        f"📅 *Target Date:* {target_date.strftime('%d/%m/%Y')}\n"
        f"⏳ *Time Remaining:*\n"
        f"   🔵 {days} days\n"
        f"   🟢 {hours:02d} hours\n"
        f"   🟡 {minutes:02d} minutes\n"
        f"   🔴 {seconds:02d} seconds\n\n"
        f"`{'█' * (seconds % 10)}{'░' * (10 - (seconds % 10))}`\n\n"
        f"_Updating live..._"
    )


async def main():
    bot = Bot(token=BOT_TOKEN)

    # Calculate initial countdown text
    now = datetime.now()
    target_datetime = datetime.combine(TARGET_DATE, datetime.min.time())
    initial_seconds = int((target_datetime - now).total_seconds())
    initial_text = format_time_difference(initial_seconds, TARGET_DATE)

    # 1. Post initial message to @khakimov_vip
    try:
        message = await bot.send_message(
            chat_id=CHANNEL_ID,
            text=initial_text,
            parse_mode="Markdown"
        )
        message_id = message.message_id
        print(f"✅ Posted initial message to {CHANNEL_ID} (Message ID: {message_id})")
    except Exception as e:
        print(f"❌ Failed to post! Check if bot is Admin in {CHANNEL_ID}. Error: {e}")
        return

    # 2. Continuous editing loop
    while True:
        await asyncio.sleep(UPDATE_INTERVAL)
        
        now = datetime.now()
        difference = target_datetime - now
        total_seconds = int(difference.total_seconds())
        
        new_text = format_time_difference(total_seconds, TARGET_DATE)

        try:
            await bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=message_id,
                text=new_text,
                parse_mode="Markdown"
            )
            print("Updated channel message...")
        except RetryAfter as e:
            print(f"Rate limited by Telegram. Waiting {e.retry_after}s...")
            await asyncio.sleep(e.retry_after)
        except TelegramError as e:
            if "message is not modified" not in str(e).lower():
                logger.error(f"Error editing message: {e}")

        if total_seconds <= 0:
            print("Countdown reached!")
            break


if __name__ == "__main__":
    asyncio.run(main())
