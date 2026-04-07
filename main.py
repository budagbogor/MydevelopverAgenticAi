import flet as ft
from gui_app import main_launcher
import logging
import sys
import os
import socket
from telegram_bot import TelegramBot
from config import TELEGRAM_BOT_TOKEN

LOCK_FILE = "bot.lock"

def main():
    # Setup logging awal
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # 🛡️ PROTEKSI PORT LOCK (Antar-Terminal Connection)
    try:
        # Mencoba membuat socket lokal di port khusus (18523)
        # Jika port ini terpakai, berarti bot sudah jalan di jendela lain.
        # Port ini dipilih karena jarang digunakan oleh aplikasi umum.
        _socket_lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket_lock.bind(('127.0.0.1', 18523))
        # Jangan tutup socket ini! Ia harus tetap 'terpakai' selama bot jalan.
    except socket.error:
        print("\n" + "!"*50)
        print("🛑 ERROR: Bot sedang berjalan di jendela lain!")
        print("Tutup jendela bot yang sudah ada terlebih dahulu.")
        print("!"*50 + "\n")
        sys.exit(1)

    # 🧼 Pembersihan lock file legacy (jika ada)
    if os.path.exists(LOCK_FILE): 
        try: os.remove(LOCK_FILE)
        except: pass

    try:
        # Cek mode eksekusi (CLI vs GUI)
        if "--help" in sys.argv or "-h" in sys.argv:
            print("\n🌌 DarkSky Agentic AI - Help Menu")
            print("-" * 30)
            print("Usage: python main.py [options]")
            print("\nOptions:")
            print("  --cli      Run in Telegram Bot Mode (Autonomous)")
            print("  --help     Show this help message")
            print("\nIf no options are provided, the GUI Desktop Engine will start.\n")
            return

        if "--cli" in sys.argv:
            print("🌌 Starting DarkSky Agent in CLI Mode...")
            if not TELEGRAM_BOT_TOKEN:
                print("❌ Error: TELEGRAM_BOT_TOKEN mismatch in .env")
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