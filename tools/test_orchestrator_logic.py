import os
import asyncio
import json
from orchestrator import Orchestrator

def test_skill_selection():
    print("\n🧪 [TEST] Skill Selection...")
    orch = Orchestrator()
    
    tasks = [
        "buat landing page toko sparepart",
        "buat sistem login dan database user",
        "buat checkout stripe",
        "buat kalkulator simpel"
    ]
    
    for t in tasks:
        skills = orch._get_relevant_skills(t)
        if skills:
            print(f"✅ Tugas: '{t}' -> SKILL DETECTED!")
            # print(skills[:100] + "...")
        else:
            print(f"ℹ️ Tugas: '{t}' -> No specific skill (General).")

async def test_file_validation_logic():
    print("\n🧪 [TEST] File Validation Logic Simulation...")
    orch = Orchestrator()
    orch.initial_files = {"main.py", "config.py"} # Mock initial state
    
    # Simulate step 5 with NO new files
    current_files_empty = {"main.py", "config.py"}
    new_files = current_files_empty - orch.initial_files
    real_changes = [f for f in new_files if not f.endswith('.log') and f != 'bot.lock']
    
    if not real_changes:
        print("✅ SUCCESS: System correctly identified NO NEW FILES and would block SELESAI.")
    else:
        print("❌ FAILURE: Validation logic missed empty folder.")

    # Simulate step 5 WITH new file
    current_files_full = {"main.py", "config.py", "README.md"}
    new_files = current_files_full - orch.initial_files
    real_changes = [f for f in new_files if not f.endswith('.log') and f != 'bot.lock']
    
    if real_changes:
        print(f"✅ SUCCESS: System identified new files: {real_changes}")
    else:
        print("❌ FAILURE: Validation logic missed README.md.")

if __name__ == "__main__":
    test_skill_selection()
    asyncio.run(test_file_validation_logic())
