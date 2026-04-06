import pyautogui
import time
import os
from dotenv import load_dotenv

# Muat variabel DPI_SCALE
load_dotenv()

print("="*50)
print("🚀 ALAT KALIBRASI DPI OTOMATIS")
print("="*50)

width, height = pyautogui.size()
print(f"📊 Resolusi Fisik: {width} x {height}")

def test_scale(scale_value):
    print(f"\n🧪 MENGETES DPI_SCALE: {scale_value}")
    print("Mouse akan bergerak ke Pojok Kanan Bawah (95%, 95%)...")
    
    target_x = ((95 / 100) * width) / scale_value
    target_y = ((95 / 100) * height) / scale_value
    
    pyautogui.moveTo(target_x, target_y, duration=1.5)
    time.sleep(1)
    # Kembali ke tengah
    pyautogui.moveTo(width/2, height/2, duration=0.5)

print("\nSilakan perhatikan kursor mouse Anda.")
test_scale(1.0)
test_scale(1.25)
test_scale(1.5)

print("\n" + "="*50)
print("HASIL TES:")
print("1. Jika mendarat tepat saat mengetes 1.0 -> Gunakan DPI_SCALE=1.0")
print("2. Jika mendarat tepat saat mengetes 1.25 -> Gunakan DPI_SCALE=1.25")
print("3. Jika mendarat tepat saat mengetes 1.5 -> Gunakan DPI_SCALE=1.5")
print("="*50)
print("\nManakah yang paling akurat mendarat di pojok kanan bawah?")
