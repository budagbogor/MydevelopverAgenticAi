import flet as ft
from gui_app import main_launcher
import logging
import sys
from telegram_bot import TelegramBot
from config import TELEGRAM_BOT_TOKEN

def main():
    # Setup logging awal
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Cek mode eksekusi (CLI vs GUI)
    if "--cli" in sys.argv:
        print("🌌 Starting DarkSky Agent in CLI Mode...")
        if not TELEGRAM_BOT_TOKEN:
            print("❌ Error: TELEGRAM_BOT_TOKEN tidak ditemukan di file .env")
            return
        bot = TelegramBot(TELEGRAM_BOT_TOKEN)
        bot.run()
    else:
        print("🌌 Starting DarkSky Desktop Engine (GUI)...")
        ft.app(target=main_launcher)

if __name__ == '__main__':
    main()