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
            exe_name = os.path.basename(IDE_PATH)
            print(f"🛑 Mematikan {TARGET_IDE} ({exe_name})...")
            # Gunakan taskkill dengan /F (force) dan /T (tree) untuk mematikan semua sub-proses
            subprocess.run(["taskkill", "/F", "/T", "/IM", exe_name], capture_output=True)
            time.sleep(2.0) # Tunggu cleanup
            # Pastikan bot.lock dibersihkan jika bot berjalan di dalam IDE
            if os.path.exists("bot.lock"): os.remove("bot.lock")
            return True
        except Exception as e:
            print(f"⚠️ Gagal mematikan IDE: {e}")
            return False

    def close_all_tabs(self):
        """Menutup semua tab editor di Trae/VSCode menggunakan hotkey Ctrl+K W."""
        print("🧼 Membersihkan tab editor (Clean Slate)...")
        self.ensure_focus() # Pastikan terfokus sebelum menekan hotkey
        pyautogui.hotkey('ctrl', 'k')
        time.sleep(0.2)
        pyautogui.press('w')
        time.sleep(1.0)

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
            
            # --- SYNC VALIDATION (PROYEK BENAR?) ---
            project_base = os.path.basename(PROJECT_ROOT)
            if target_windows and target == TARGET_IDE:
                win = target_windows[0]
                # Jika nama proyek tidak ada di judul jendela, paksa restart
                if project_base.lower() not in win.title.lower():
                    print(f"🔄 Judul Jendela Salah ('{win.title}'). Meminta restart untuk folder '{project_base}'...")
                    force_restart = True
            
            if target_windows and not force_restart:
                win = target_windows[0]
                try:
                    if win.isMinimized: win.restore()
                    win.activate()
                    time.sleep(1.0)
                    return True
                except: pass
            
            # 2. Jika IDE belum terbuka atau butuh restart
            if target == TARGET_IDE and (not target_windows or force_restart):
                if force_restart: self.close_ide()
                print(f"🚀 Menjalankan {target} pada folder: {PROJECT_ROOT}...")
                # Gunakan format string tunggal dengan tanda kutip untuk shell=True di Windows
                cmd = f'"{IDE_PATH}" "{PROJECT_ROOT}"'
                subprocess.Popen(cmd, shell=True)
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