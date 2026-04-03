import os
import sys

# Windows specific imports
try:
    import winreg
    import winshell
except ImportError:
    winreg = None
    winshell = None

def set_autostart(enabled=True):
    """Mengaktifkan atau menonaktifkan fitur start otomatis di Windows."""
    if sys.platform != "win32" or winreg is None:
        return False, "Fitur ini hanya didukung di Windows."

    app_name = "DarkSkyAgent"
    # Menentukan path exe (jika sudah di-build) atau script python
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        app_path = f'"{sys.executable}" "{os.path.abspath("main.py")}"'

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            status = "Auto-start diaktifkan."
        else:
            try:
                winreg.DeleteValue(key, app_name)
                status = "Auto-start dinonaktifkan."
            except FileNotFoundError:
                status = "Auto-start sudah nonaktif."
        winreg.CloseKey(key)
        return True, status
    except Exception as e:
        return False, f"Gagal mengubah registri: {str(e)}"

def is_autostart_enabled():
    """Mengecek apakah auto-start sedang aktif di registri."""
    if sys.platform != "win32" or winreg is None:
        return False
    
    app_name = "DarkSkyAgent"
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, app_name)
        winreg.CloseKey(key)
        return True
    except:
        return False
