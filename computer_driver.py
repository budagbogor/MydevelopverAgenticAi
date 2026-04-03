import pyautogui
import time
import os
import re
import subprocess
import pygetwindow as gw
from config import IDE_PATH, TARGET_IDE, PROJECT_ROOT

class ComputerDriver:
    def __init__(self):
        pyautogui.FAILSAFE = False 
        self.screenshot_dir = "screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    def close_ide(self):
        """Mematikan proses IDE secara paksa untuk restart bersih."""
        try:
            import subprocess
            print(f"🛑 Mematikan {TARGET_IDE}...")
            subprocess.run(["taskkill", "/F", "/IM", os.path.basename(IDE_PATH)], capture_output=True)
            time.sleep(1.0)
            return True
        except Exception as e:
            print(f"⚠️ Gagal mematikan IDE: {e}")
            return False

    def get_active_window(self):
        """Mendapatkan judul jendela yang sedang aktif."""
        try:
            win = gw.getActiveWindow()
            return win.title if win else "Desktop/Unknown"
        except:
            return "Unknown"

    def ensure_focus(self, target_name=None, force_restart=False):
        """Memastikan jendela aplikasi aktif secara dinamis."""
        target = target_name if target_name else TARGET_IDE
        try:
            if force_restart and target == TARGET_IDE:
                self.close_ide()

            # 1. Cari jendela yang mirip dengan target
            all_windows = gw.getAllWindows()
            target_windows = [w for w in all_windows if target.lower() in w.title.lower()]
            
            if target_windows:
                win = target_windows[0]
                try:
                    if win.isMinimized: win.restore()
                    win.activate()
                    time.sleep(1.0)
                    return True
                except: pass
            
            # 2. Jika ini IDE dan belum terbuka, coba jalankan
            if target == TARGET_IDE and os.path.exists(IDE_PATH):
                print(f"🚀 Menjalankan {target}...")
                subprocess.Popen([IDE_PATH, PROJECT_ROOT], shell=True)
                for _ in range(15):
                    time.sleep(1)
                    if [w for w in gw.getAllWindows() if target.lower() in w.title.lower()]:
                        return True
            
            # 3. Jika aplikasi umum (misal terminal/browser), biarkan AI yang menanganinya via TYPE 'win' + nama aplikasi
            return False
                
        except Exception as e:
            print(f"⚠️ Fokus Gagal untuk {target}: {e}")
        return False

    def take_screenshot(self):
        # Ambil screenshot layar penuh untuk analisis Vision
        path = os.path.join(self.screenshot_dir, "current_state.png")
        pyautogui.screenshot(path)
        return path

    def clean_coord(self, val):
        """Membersihkan kotoran teks dari koordinat (X:32 -> 32.0)."""
        try:
            # Mengambil hanya angka dan titik desimal
            clean_val = re.sub(r'[^0-9.]', '', str(val))
            return float(clean_val)
        except:
            return 0.0

    def execute_action(self, action_type, params):
        """Eksekusi fisik dengan perlindungan zona bahaya."""
        try:
            if action_type == "CLICK":
                if not params or len(params) < 2: return
                width, height = pyautogui.size()
                x_p = self.clean_coord(params[0])
                y_p = self.clean_coord(params[1])
                
                # Proteksi pojok kanan atas (Tombol Close/System Windows) 
                # Jika di atas 95% lebar dan di bawah 5% tinggi
                if x_p > 95 and y_p < 5:
                    print("🛡️ Proteksi: Membatalkan klik pada area sistem CLOSE.")
                    return
                
                target_x = (x_p / 100) * width
                target_y = (y_p / 100) * height
                
                pyautogui.moveTo(target_x, target_y, duration=0.3)
                pyautogui.click()
                
            elif action_type == "TYPE":
                if not params or len(params) < 1: return
                pyautogui.write(str(params[0]), interval=0.01)
                
            elif action_type == "HOTKEY":
                if not params: return
                pyautogui.hotkey(*params)
                
            elif action_type == "ENTER":
                pyautogui.press('enter')
                
            elif action_type == "WAIT":
                duration = self.clean_coord(params[0]) if params else 2
                time.sleep(duration)
                
        except Exception as e:
            print(f"❌ Driver Error: {e}")