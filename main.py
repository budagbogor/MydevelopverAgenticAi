import logging
from telegram_bot import TelegramBot
from config import TELEGRAM_BOT_TOKEN

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN tidak ditemukan di file .env")
        return

    print("🚀 Mencoba menjalankan bot...")
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()

if __name__ == '__main__':
    main()