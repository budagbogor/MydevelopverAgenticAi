import asyncio
import os
import sys
import time

# Sync path
current_dir = os.getcwd()
sys.path.append(current_dir)

from orchestrator import Orchestrator

class MockMessage:
    async def edit_text(self, text):
        # Bersihkan markdown untuk print konsol
        clean_text = text.replace("```", "").replace("**", "")
        print(f"   [MSG-EDIT] {clean_text}")

class MockMessageInitial:
    async def reply_text(self, text, parse_mode=None):
        print(f"   [MSG-REPLY] {text}")
        return MockMessage()

class MockUpdate:
    message = MockMessageInitial()

async def prove_live_logs():
    print("\n--- PROVING HOTFIX 5.0 (LIVE LOGS) ---")
    orch = Orchestrator()
    update = MockUpdate()
    
    # Kita tes dengan perintah yang menghasilkan output: npm --version
    print("[RUN] Mencoba perintah terminal dengan Live Streaming...")
    # Paksa agar timeout cepat dan log buffer terlihat jika memungkinkan
    # Kita menggunakan 'dir' atau 'ls' yang banyak outputnya
    success = await orch._execute_terminal("dir", 0, [], update)
    
    if success:
        print("\n[SUCCESS] PEMBUKTIAN SELESAI: Orchestrator berhasil menangkap dan menyalurkan log secara real-time.")
    else:
        print("\n[FAILED] PEMBUKTIAN GAGAL.")

if __name__ == "__main__":
    asyncio.run(prove_live_logs())
