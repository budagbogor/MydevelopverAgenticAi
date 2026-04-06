import pyautogui
import time

print("🛰️ MEMULAI PENCARI SASARAN OTOMATIS")
print("Tugas Anda: Dalam 5 detik, tempelkan kursor mouse Anda tepat di atas IKON PANAH HIJAU di Trae.")
print("Diamkan di sana sampai muncul pengumuman!")
print("-" * 40)

for i in range(5, 0, -1):
    print(f"⌛ Menghitung mundur: {i}...")
    time.sleep(1)

# Ambil koordinat saat ini
x, y = pyautogui.position()
width, height = pyautogui.size()

# Hitung koordinat relatif (untuk disimpan dalam bot)
grid_x = (x / width) * 100
grid_y = (y / height) * 100

print("-" * 40)
print(f"🚀 SASARAN DITEMUKAN!")
print(f"Koordinat Pixel: X={x}, Y={y}")
print(f"Koordinat Grid:  GridX={grid_x:.2f}, GridY={grid_y:.2f}")
print("-" * 40)
print("\nSalin (Copy) hasil di atas dan kirimkan ke saya!")
