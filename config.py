import os
from dotenv import load_dotenv

# Muat variabel dari .env
load_dotenv()

# Identifikasi API & Model
SUMOPOD_API_KEY = os.getenv("SUMOPOD_API_KEY")
SUMOPOD_BASE_URL = os.getenv("SUMOPOD_BASE_URL", "https://ai.sumopod.com/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini/gemini-2.5-flash")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Keamanan Whitelist
raw_whitelist = os.getenv("ALLOWED_TELEGRAM_USER_IDS", "")
ALLOWED_TELEGRAM_WHITELIST = [u.strip() for u in raw_whitelist.split(",") if u.strip()]

# Konfigurasi IDE
TARGET_IDE = os.getenv("TARGET_IDE", "Trae")
IDE_PATH = os.getenv("IDE_PATH", r"C:\Users\DarkSky\AppData\Local\Programs\Trae\Trae.exe")

# Lokasi folder proyek
PROJECT_ROOT = os.getenv("PROJECT_ROOT", os.getcwd())

# Token Deployment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")

SCREENSHOT_DIR = "screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def save_config(updates: dict):
    """Memperbarui variabel di file .env secara permanen dari dictionary."""
    try:
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        new_lines = []
        processed_keys = set()
        
        # Update key yang sudah ada
        for line in lines:
            stripped = line.strip()
            if "=" in stripped and not stripped.startswith("#"):
                key = stripped.split("=")[0]
                if key in updates:
                    new_lines.append(f"{key}={updates[key]}\n")
                    processed_keys.add(key)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Tambahkan key baru jika ada
        for key, value in updates.items():
            if key not in processed_keys:
                new_lines.append(f"{key}={value}\n")
                
        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        load_dotenv(override=True) # Muat ulang variabel lingkungan
        return True
    except Exception as e:
        print(f"Error save_config: {e}")
        return False