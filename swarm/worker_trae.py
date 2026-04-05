import asyncio
import pyautogui
import time
import os
from computer_driver import ComputerDriver
from neural.sona import SonaMemory

class TraeWorker:
    """
    WorkerTrae (Specialist in Trae IDE GUI Interaction)
    Ref: RuFlo v3 Philosophy
    Handles concrete GUI tasks delegated by the Queen.
    """
    def __init__(self, sona_instance: SonaMemory):
        self.driver = ComputerDriver()
        self.sona = sona_instance
        self.agent_id = "coder_trae"

    async def execute_milestone(self, milestone_data):
        """
        Melaksanakan instruksi pengetikan dan penyerahan tugas ke Trae.
        """
        instruction = milestone_data.get('instruction', '')
        ms_name = milestone_data.get('name', 'Undefined Stage')
        
        print(f"🛠️ [{self.agent_id}] Executing: {ms_name}")
        
        # 1. Pastikan Trae terfokus
        self.driver.ensure_focus()
        await asyncio.sleep(1.0)
        
        # --- NEW: PANGGIL TRAE BUILDER DENGAN HOTKEY ---
        print(f"🔍 [{self.agent_id}] Focusing Trae Builder (Ctrl+I)...")
        pyautogui.hotkey('ctrl', 'i')
        await asyncio.sleep(1.5) # Tunggu panel muncul
        
        # 3. Ketik instruksi
        print(f"⌨️ Typing instruction: {instruction[:50]}...")
        pyautogui.write(str(instruction), interval=0.05) 
        await asyncio.sleep(1.5)
        
        # 4. Submit (Ctrl+Enter + Klik Fisik)
        for key in ["ctrl", "enter"]: pyautogui.keyDown(key)
        time.sleep(0.1)
        for key in ["enter", "ctrl"]: pyautogui.keyUp(key)
        await asyncio.sleep(0.5)
        
        submit_x = int(0.8990 * width)
        submit_y = int(0.7852 * height)
        pyautogui.click(submit_x, submit_y)
        
        # 5. Catat ke SONA
        self.sona.record_step(
            agent_id=self.agent_id,
            action=f"Typed and Submitted to Trae Builder",
            observation="Task submitted. Awaiting monitoring feedback.",
            thought=f"Executing {ms_name} with instruction: {instruction}"
        )
        
        return {"status": "SUCCESS", "milestone": ms_name}

    async def wait_for_completion(self, initial_snapshot, check_callback, timeout=120):
        """
        Memantau perubahan file melalui snapshot untuk mendeteksi penyelesaian tugas.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            await asyncio.sleep(2.0)
            if check_callback(): # Memanggil fungsi pengecekan file dari orchestrator
                print(f"✅ [{self.agent_id}] Task completed based on file changes.")
                return True
        print(f"⚠️ [{self.agent_id}] Monitoring timeout reached.")
        return False
