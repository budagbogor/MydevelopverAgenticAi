import pyautogui
import time
import os
import re
import subprocess
import pygetwindow as gw
from config import IDE_PATH, TARGET_IDE

class ComputerDriver:
    def __init__(self):
        pyautogui.FAILSAFE = False 
        self.screenshot_dir = "screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        
        self._project_root = os.getenv("PROJECT_ROOT", os.getcwd())
        
        # --- CALIBRATION: DPI SCALE ---
        # Jika layar 4K dengan scaling 150%, set DPI_SCALE=1.5 di .env
        self.dpi_scale = float(os.getenv("DPI_SCALE", "1.0"))
        print(f"⚙️ Driver diinisialisasi (DPI Scale: {self.dpi_scale})")
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
        # Muat ulang project root dari environment agar selalu up-to-date
        self._project_root = os.getenv("PROJECT_ROOT", os.getcwd())
        
        try:
            if force_restart and target == TARGET_IDE:
                self.close_ide()

            # 1. Cari jendela yang mirip dengan target
            all_windows = gw.getAllWindows()
            target_windows = [w for w in all_windows if target.lower() in w.title.lower()]
            
            # --- SYNC VALIDATION (PROYEK BENAR?) ---
            project_base = os.path.basename(self._project_root)
            if target_windows and target == TARGET_IDE and not force_restart:
                win = target_windows[0]
                # Jika nama proyek tidak ada di judul, tunggu dulu — Trae butuh waktu untuk memuat folder
                if project_base.lower() not in win.title.lower():
                    print(f"⏳ Judul Trae ('{win.title}') belum menunjukkan '{project_base}'. Menunggu 10 detik...")
                    time.sleep(10)
                    # Cek ulang setelah menunggu
                    all_windows = gw.getAllWindows()
                    target_windows = [w for w in all_windows if target.lower() in w.title.lower()]
                    if target_windows:
                        win = target_windows[0]
                        if project_base.lower() not in win.title.lower():
                            # Masih salah setelah menunggu - tapi JANGAN restart jika memang folder baru kosong
                            print(f"⚠️ Judul masih '{win.title}'. Menerima kondisi ini (folder kosong baru).")
            
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
                print(f"🚀 Menjalankan {target} pada folder: {self._project_root}...")
                # Gunakan format string tunggal dengan tanda kutip untuk shell=True di Windows
                cmd = f'"{IDE_PATH}" "{self._project_root}"'
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
        """Eksekusi fisik dengan perlindungan zona bahaya dan Super-Focus."""
        try:
            # --- MANDATORY FOCUS RE-CHECK ---
            # Pastikan aplikasi target benar-benar di depan sebelum aksi sensitif
            if action_type in ["CLICK", "TYPE", "HOTKEY"]:
                self.ensure_focus()
                
            if action_type == "CLICK":
                if not params or len(params) < 2: return
                width, height = pyautogui.size()
                x_p = self.clean_coord(params[0])
                y_p = self.clean_coord(params[1])
                
                # Proteksi pojok kanan atas (Tombol Close)
                if x_p > 95 and y_p < 5: return
                
                target_x = (x_p / 100) * width
                target_y = (y_p / 100) * height
                
                print(f"🤖 CLICK at ({int(target_x)}, {int(target_y)})")
                pyautogui.moveTo(target_x, target_y, duration=0.3)
                pyautogui.click()
                
            elif action_type == "TYPE":
                if not params or len(params) < 1: return
                # Klik area input terlebih dahulu untuk memastikan kursor aktif
                print(f"⌨️ Typing Verbatim: {params[0][:30]}...")
                # Jeda 2 detik (Warm-up) agar Windows/Trae benar-benar siap menerima karakter pertama
                time.sleep(2.0)
                pyautogui.write(str(params[0]), interval=0.05)
                
                # --- AUTO-SUBMIT (Double Insurance) ---
                time.sleep(1.0)
                # 1. Hotkey Submit
                for key in ["ctrl", "enter"]: pyautogui.keyDown(key)
                time.sleep(0.1)
                for key in ["enter", "ctrl"]: pyautogui.keyUp(key)
                
                # 2. Click Submit (Presisi: GridX=89.90, GridY=85.00 - Sedikit lebih rendah dari input)
                time.sleep(1.0)
                width, height = pyautogui.size()
                target_x = (89.90 / 100) * width
                target_y = (85.00 / 100) * height # Menurunkan bidikan agar mengenai tombol kikir
                pyautogui.moveTo(target_x, target_y, duration=0.2)
                pyautogui.click()
                
                # 3. Triple-Enter Brute Force (Jaminan 100% Terkirim)
                time.sleep(0.5)
                for _ in range(3): pyautogui.press('enter')
                print("✅ Submit Sent (Hotkey + Offset-Click + Triple-Enter)")
                
            elif action_type == "HOTKEY":
                if not params: return
                # Eksekusi hotkey dengan jeda manual agar lebih andal
                for key in params:
                    pyautogui.keyDown(key)
                time.sleep(0.1)
                for key in reversed(params):
                    pyautogui.keyUp(key)
                
            elif action_type == "ENTER":
                pyautogui.press('enter')
                
            elif action_type == "WAIT":
                duration = self.clean_coord(params[0]) if params else 2
                time.sleep(duration)
                
        except Exception as e:
            print(f"❌ Driver Error: {e}")