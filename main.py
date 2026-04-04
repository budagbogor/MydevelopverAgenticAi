import flet as ft
from gui_app import main_launcher
import logging
import sys
import os
from telegram_bot import TelegramBot
from config import TELEGRAM_BOT_TOKEN

LOCK_FILE = "bot.lock"

def main():
    # Setup logging awal
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # 🛡️ PROTEKSI LOCK FILE (Anti-Dual Instance)
    if os.path.exists(LOCK_FILE):
        print("\n" + "="*50)
        print(f"⚠️  WARNING: {LOCK_FILE} ditemukan!")
        print("Bot sepertinya sudah berjalan di jendela lain.")
        print("Jika Anda yakin tidak ada bot yang jalan, hapus file ini manual.")
        print("="*50 + "\n")
        sys.exit(1)

    try:
        # Buat Lock File
        with open(LOCK_FILE, "w") as f:
            f.write("running")
        
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
            
    finally:
        # 🧼 PEMBERSIHAN OTOMATIS SAAT KELUAR
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
                print(f"🛑 {LOCK_FILE} telah dibersihkan. Selesai.")
            except:
                pass

if __name__ == '__main__':
    main()