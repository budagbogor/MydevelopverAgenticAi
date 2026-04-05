import pyautogui
import time
from computer_driver import ComputerDriver

driver = ComputerDriver()

def calibrate():
    print("🎯 MEMULAI KALIBRASI TOMBOL SUBMIT")
    print("Target: Menemukan koordinat akurat tombol 'Send' (Panah Hijau) Trae.")
    
    if driver.ensure_focus():
        width, height = pyautogui.size()
        
        # Titik A: Estimasi 1 (Paling mungkin)
        # Grid X=97, Y=93
        x1 = int(0.97 * width)
        y1 = int(0.93 * height)
        
        print(f"\n📍 MEMERIKSA TITIK A (X={x1}, Y={y1})")
        pyautogui.moveTo(x1, y1, duration=1.5)
        print(">>> Apakah kursor sekarang berada di atas PANAH HIJAU? (Tunggu 3 detik)")
        time.sleep(3)
        
        # Titik B: Estimasi 2 (Sedikit lebih ke kiri)
        # Grid X=94, Y=93
        x2 = int(0.94 * width)
        y2 = int(0.93 * height)
        
        print(f"\n📍 MEMERIKSA TITIK B (X={x2}, Y={y2})")
        pyautogui.moveTo(x2, y2, duration=1.5)
        print(">>> Atau apakah ini lebih tepat di atas PANAH HIJAU? (Tunggu 3 detik)")
        time.sleep(3)

        print("\n✅ SELESAI.")
        print("Lapor ke saya: Manakah yang lebih tepat? Titik A, Titik B, atau sebutkan arah melesetnya!")
    else:
        print("❌ Gagal menemukan jendela Trae.")

if __name__ == "__main__":
    calibrate()
