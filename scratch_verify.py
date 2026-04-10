import sys
import os
import time
import asyncio

# Ensure we are in the right directory
current_dir = os.getcwd()
sys.path.append(current_dir)

from computer_driver import ComputerDriver

def run_verify():
    print("\n--- DARKSKY SYSTEM INTEGRITY VERIFICATION ---")
    driver = ComputerDriver()
    
    # 1. Test RPA / Focus
    print("[1/2] Memeriksa Fokus Visual (RPA)...")
    try:
        focused = driver.ensure_focus()
        if focused:
            print("      ✅ OK: Driver berhasil menemukan dan memberikan fokus pada IDE.")
        else:
            print("      ⚠️ WARN: IDE tidak ditemukan, mencoba mode mandiri...")
    except Exception as e:
        print(f"      ❌ FAIL: Driver Error: {e}")

    # 2. Capture Screen
    print("[2/2] Mengambil Bukti Visual (Screenshot)...")
    try:
        filename = "verification_proof_current.png"
        driver.capture_screen(filename)
        # Ambil path absolut
        abs_path = os.path.abspath(filename)
        print(f"      ✅ OK: Screenshot disimpan di {abs_path}")
    except Exception as e:
        print(f"      ❌ FAIL: Gagal mengambil screenshot: {e}")

    print("\n--- ✅ VERIFIKASI SELESAI ---\n")

if __name__ == "__main__":
    run_verify()
