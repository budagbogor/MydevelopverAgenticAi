import pyautogui
import time
import os
import subprocess
import pygetwindow as gw
import uiautomation as auto
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
        print(f"[DRIVER] Inisialisasi (DPI Scale: {self.dpi_scale})")
    def close_ide(self):
        """Mematikan proses IDE secara paksa untuk restart bersih."""
        try:
            import subprocess
            exe_name = os.path.basename(IDE_PATH)
            print(f"[STOP] Mematikan {TARGET_IDE} ({exe_name})...")
            # Gunakan taskkill dengan /F (force) dan /T (tree) untuk mematikan semua sub-proses
            subprocess.run(["taskkill", "/F", "/T", "/IM", exe_name], capture_output=True)
            time.sleep(2.0) # Tunggu cleanup
            # Pastikan bot.lock dibersihkan jika bot berjalan di dalam IDE
            if os.path.exists("bot.lock"): os.remove("bot.lock")
            return True
        except Exception as e:
            print(f"[WARN] Gagal mematikan IDE: {e}")
            return False

    def close_all_tabs(self):
        """Menutup semua tab editor di Trae/VSCode menggunakan hotkey Ctrl+K W."""
        print("[CLEAN] Membersihkan tab editor (Clean Slate)...")
        self.ensure_focus() # Pastikan terfokus sebelum menekan hotkey
        pyautogui.hotkey('ctrl', 'k')
        time.sleep(0.2)
        pyautogui.press('w')
        time.sleep(1.0)

    def ensure_focus(self, target_name=None, force_restart=False):
        """
        Memastikan jendela aplikasi aktif secara dinamis menggunakan UI Automation.
        """
        target = target_name if target_name else TARGET_IDE
        print(f"[EYES] Mencoba fokus ke: {target}")
        
        try:
            # 1. Cari jendela menggunakan uiautomation (lebih tangguh)
            root = auto.GetRootControl()
            # Fuzzy search melalui semua top-level windows
            target_win = None
            for win in root.GetChildren():
                if target.lower() in win.Name.lower():
                    target_win = win
                    break
            
            if target_win and not force_restart:
                print(f"[EYES] Menemukan jendela via UIA: {target_win.Name}")
                # Gunakan GetWindowVisualState() sesuai spek uiautomation
                try:
                    if target_win.GetWindowVisualState() == auto.WindowVisualState.Minimized:
                        target_win.SetWindowVisualState(auto.WindowVisualState.Normal)
                except:
                    pass
                
                target_win.SetActive()
                target_win.SetFocus()
                time.sleep(1.0)
                return True
            
            # 2. Fallback: Jika uiautomation gagal, coba jalankan IDE
            if target == TARGET_IDE:
                print(f"[EYES] IDE belum terbuka, menjalankan: {IDE_PATH}...")
                subprocess.Popen(f'"{IDE_PATH}" "{os.getenv("PROJECT_ROOT", os.getcwd())}"', shell=True)
                # Tunggu jendela muncul (maks 20 detik)
                for _ in range(20):
                    time.sleep(1)
                    for win in root.GetChildren():
                        if target.lower() in win.Name.lower():
                            win.SetActive()
                            return True
            
            return False
        except Exception as e:
            print(f"[EYES] Gagal fokus ke {target}: {e}")
            return False

    def capture_screen(self, filename="current_state.png"):
        """Mengambil screenshot layar untuk verifikasi visual (Reflect)."""
        os.makedirs(self.screenshot_dir, exist_ok=True)
        path = os.path.join(self.screenshot_dir, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return path

    def take_screenshot(self, filename="current_state.png"):
        """Alias untuk capture_screen agar kompatibel dengan browser bot."""
        return self.capture_screen(filename)

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
                
                print(f"[CLICK] at ({int(target_x)}, {int(target_y)})")
                pyautogui.moveTo(target_x, target_y, duration=0.3)
                pyautogui.click()
                
            elif action_type == "TYPE":
                if not params or len(params) < 1: return
                # Klik area input terlebih dahulu untuk memastikan kursor aktif
                print(f"[TYPE] Typing Verbatim: {params[0][:30]}...")
                # Jeda 2 detik (Warm-up) agar Windows/Trae benar-benar siap menerima karakter pertama
                time.sleep(2.0)
                pyautogui.write(str(params[0]), interval=0.05)
                
                # --- AUTO-SUBMIT (Insurance) ---
                time.sleep(1.0)
                pyautogui.press('enter')
                print("[OK] Submit Sent")
                
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
            print(f"[ERROR] Driver Error: {e}")

    def type_in_trae(self, instruction):
        """Metode khusus untuk berinteraksi dengan Trae AI Builder via Ctrl+U."""
        print(f"[VISUAL] Mengirim instruksi ke Trae Builder: {instruction[:50]}...")
        if self.ensure_focus():
            # 1. Buka AI Builder (Ctrl+U sesuai permintaan user)
            pyautogui.hotkey('ctrl', 'u')
            time.sleep(2.0) # Tunggu panel muncul
            
            # 2. Ketik instruksi
            pyautogui.write(instruction, interval=0.01)
            time.sleep(0.5)
            
            # 3. Kirim (Enter)
            pyautogui.press('enter')
            print("[VISUAL] Instruksi terkirim ke Trae.")
            return True
        return False

    def open_in_trae(self, file_path):
        """Membuka file tertentu di Trae agar pengguna bisa melihat hasilnya di layar."""
        print(f"[VISUAL] Membuka file di Trae: {file_path}")
        if self.ensure_focus():
            # Gunakan Ctrl+P (Quick Open)
            pyautogui.hotkey('ctrl', 'p')
            time.sleep(0.5)
            # Ketik nama file
            pyautogui.write(os.path.basename(file_path), interval=0.01)
            time.sleep(0.5)
            pyautogui.press('enter')
            return True
        return False