import pyautogui
import time
import os
from dotenv import load_dotenv

# Muat variabel DPI_SCALE
load_dotenv()
DPI_SCALE = float(os.getenv("DPI_SCALE", "1.0"))

print("="*50)
print("🚀 DEBUG: ALAT CEK KOORDINAT & DPI")
print("="*50)

width, height = pyautogui.size()
print(f"📊 Resolusi Terdeteksi Sistem: {width} x {height}")
print(f"⚙️ DPI Scale yang Digunakan: {DPI_SCALE}")

# Kalkulasi Target (Sama dengan logika bot)
def move_to_grid(x_p, y_p):
    target_x = ((x_p / 100) * width) / DPI_SCALE
    target_y = ((y_p / 100) * height) / DPI_SCALE
    print(f"🤖 Moving to Grid [{x_p}%, {y_p}%] -> Pixel ({int(target_x)}, {int(target_y)})")
    pyautogui.moveTo(target_x, target_y, duration=1.0)
    time.sleep(1)

print("\n⚠️ PERHATIAN: Mouse akan bergerak sendiri ke 4 pojok layar Anda.")
print("Jika kursor tidak mendarat di pojok yang benar, berarti DPI_SCALE salah.\n")
time.sleep(3)

# Tes 4 Pojok
move_to_grid(5, 5)     # Pojok Kiri Atas
move_to_grid(95, 5)    # Pojok Kanan Atas
move_to_grid(95, 95)   # Pojok Kanan Bawah
move_to_grid(5, 95)    # Pojok Kiri Bawah
move_to_grid(50, 50)   # Tengah Layar

print("\n✅ Tes Selesai.")
print("Jika kursor tadi mendarat mendarat di pojok-pojok layar dengan benar maka DPI_SCALE sudah OK.")
print("Jika kursor mendarat jauh dari pojok, silakan beritahu saya.")
