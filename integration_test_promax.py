import asyncio
import os
import sys
import json
import shutil
from unittest.mock import AsyncMock, MagicMock

# Ensure project root is in path
PRJ_ROOT = r"i:\projectWebApps2026\DIRECTORY-PROJECT-FOLDER\DarkSkyProject"
sys.path.append(PRJ_ROOT)

from orchestrator import Orchestrator

async def run_integration_test():
    print("[INTEGRATION TEST] Memulai Pengujian Agentic PRO-MAX Upgrade...")
    
    # 1. SETUP LINGKUNGAN TEST
    test_dir = os.path.join(PRJ_ROOT, "TEST_INTEGRATION_PROMAX")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    os.environ["PROJECT_ROOT"] = test_dir
    
    # Init Orchestrator
    torch = Orchestrator()
    torch.base_dir = test_dir
    
    # Mock Telegram
    update = AsyncMock()
    update.message = AsyncMock()
    async def mock_reply(text, **kwargs):
        # Strip all non-ascii just in case
        safe_text = text.encode('ascii', 'ignore').decode()
        print(f"[TELEGRAM]: {safe_text[:150]}...")
        return AsyncMock()
    
    update.message.reply_text = mock_reply
    update.message.reply_photo = mock_reply
    
    # --- SKENARIO: FULL CYCLE + REFLEXION TRIGGER ---
    print("\n--- SKENARIO: FULL CYCLE + REFLEXION TRIGGER ---")
    
    # Simulasi prompt user
    task_brief = "Buat aplikasi React sederhana. Buat komponen src/App.tsx yang menggunakan variabel 'myUndefinedVar' agar terjadi error linting, lalu perbaiki sendiri."
    
    try:
        # Jalankan proses orkestrasi lengkap
        await torch.process_task(task_brief, update)
        
        print("\n[TEST LOGS] Memeriksa hasil akhir di Variable Pool...")
        # Gunakan ensure_ascii=True untuk print JSON aman
        print(json.dumps(torch.variable_pool, indent=2, ensure_ascii=True))
        
        # VERIFIKASI 1: Apakah Variable Pool mencatat node?
        if len(torch.variable_pool.get("nodes", {})) > 0:
            print("[VERIFIED] Variable Pool mencatat riwayat eksekusi Node.")
        else:
            print("[FAILED] Variable Pool kosong.")

        # VERIFIKASI 2: Apakah ada file yang tertulis?
        if os.path.exists(os.path.join(test_dir, "package.json")):
             print("[VERIFIED] Integritas Proyek Terjaga (package.json exists).")
        
    except Exception as e:
        print(f"[CRITICAL TEST FAIL] Terjadi error saat pengujian: {e}")
        import traceback
        traceback.print_exc()

    print("\n[INTEGRATION TEST DONE] Periksa log di atas untuk validasi perilaku bot.")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
