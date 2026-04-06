import asyncio
import os
import sys
from unittest.mock import MagicMock

# Tambahkan path aplikasi agar bisa import module
sys.path.append(os.getcwd())

from orchestrator import Orchestrator

async def run_mock_test():
    print("🚀 Memulai Uji Coba Swarm Otonom (Mock Telegram)...")
    
    # Setup environment
    os.environ["PROJECT_ROOT"] = r"I:\projectWebApps2026\test_autonomous_mission"
    if not os.path.exists(os.environ["PROJECT_ROOT"]):
        os.makedirs(os.environ["PROJECT_ROOT"])
    
    orchestrator = Orchestrator()
    
    # Mock Update Telegram
    update = MagicMock()
    async def mock_reply(text, **kwargs):
        print(f"TRG: {text}")
    
    async def mock_reply_photo(photo, caption=None, **kwargs):
        print(f"TRG [PHOTO]: {caption}")

    update.message.reply_text = mock_reply
    update.message.reply_photo = mock_reply_photo
    
    # Task Brief
    task = "Buat aplikasi To-Do List modern dengan React dan CSS Glassmorphism."
    
    try:
        await orchestrator.process_task(task, update)
        print("✅ Test Selesai Tanpa Crash.")
    except Exception as e:
        print(f"❌ Test Gagal dengan Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_mock_test())
