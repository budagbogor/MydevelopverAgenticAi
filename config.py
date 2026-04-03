import os
from dotenv import load_dotenv

load_dotenv()

SUMOPOD_API_KEY = os.getenv("SUMOPOD_API_KEY")
SUMOPOD_BASE_URL = os.getenv("SUMOPOD_BASE_URL", "https://ai.sumopod.com/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini/gemini-2.5-flash")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Keamanan Whitelist dengan proteksi spasi (strip)
raw_whitelist = os.getenv("ALLOWED_TELEGRAM_USER_IDS", "")
ALLOWED_TELEGRAM_WHITELIST = [u.strip() for u in raw_whitelist.split(",") if u.strip()]

TARGET_IDE = os.getenv("TARGET_IDE", "Trae")
IDE_PATH = os.getenv("IDE_PATH", r"C:\Users\DarkSky\AppData\Local\Programs\Trae\Trae.exe")

# Lokasi folder proyek resmi untuk agen
PROJECT_ROOT = os.getenv("PROJECT_ROOT", os.getcwd())

# Token Deployment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")

SCREENSHOT_DIR = "screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def update_env_project_root(new_path):
    """Memperbarui variabel PROJECT_ROOT di file .env secara permanen."""
    global PROJECT_ROOT
    try:
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        found = False
        new_lines = []
        for line in lines:
            if line.startswith("PROJECT_ROOT="):
                new_lines.append(f"PROJECT_ROOT={new_path}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"PROJECT_ROOT={new_path}\n")
            
        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        PROJECT_ROOT = new_path
        return True
    except Exception as e:
        print(f"Error update_env_project_root: {e}")
        return False