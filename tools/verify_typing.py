import asyncio
import time
from computer_driver import ComputerDriver

driver = ComputerDriver()

async def run_diagnostic():
    print("🚀 MEMULAI TES DIAGNOSTIK KETIK 2.0 (SUPER-FOCUS)")
    print("Target: Menguji ketahanan input dengan sistem Super-Focus baru.")

    # 1. Pastikan Trae Terbuka & Fokus
    print("🔍 Mencari jendela Trae...")
    if driver.ensure_focus():
        print("✅ Jendela Trae ditemukan.")
        time.sleep(2)
        
        # 2. Buka Builder via Driver (Agar menggunakan logic keyDown/keyUp baru)
        print("⌨️ Mencoba membuka Builder (Ctrl+I)...")
        driver.execute_action("HOTKEY", ["ctrl", "i"])
        time.sleep(2)
        
        # 3. Klik Area Input Builder (Estimasi 1920x1080)
        # Kami menggunakan koordinat grid (90%, 93%) agar konsisten
        print("🖱️ Mencoba fokus ke kotak input...")
        driver.execute_action("CLICK", [90, 93])
        time.sleep(1)
        
        # 4. Mencoba Mengetik via Driver (Super-Focus & Human-Like)
        test_text = "HALO TRAE - TES KONEKSI BOT 2.0"
        print(f"⌨️ Mencoba mengetik: '{test_text}'")
        driver.execute_action("TYPE", [test_text])
        
        # 5. Mencoba Submit
        print("⌨️ Mencoba Submit (Ctrl+Enter)...")
        driver.execute_action("HOTKEY", ["ctrl", "enter"])
        
        print("\n✅ TES SELESAI.")
        print("Silakan lapor: Apakah sekarang teks 'HALO TRAE' muncul?")
    else:
        print("❌ Gagal menemukan jendela Trae.")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
