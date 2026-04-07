import asyncio
import pyautogui
import time
import os
import pyperclip
import uiautomation as auto
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
        
        # --- NEW: PANGGIL TRAE BUILDER DENGAN HOTKEY (Shortcut-First) ---
        print(f"🔍 [{self.agent_id}] Focusing Trae Builder with robust shortcuts...")
        
        # 1. Recursive Focus Strategy (Mencoba 3x untuk memastikan jendela aktif)
        focus_success = False
        for i in range(3):
            if self.driver.ensure_focus():
                focus_success = True
                break
            await asyncio.sleep(1.0)
            
        # 2. Bersihkan overlay dengan Escape
        pyautogui.press('esc')
        await asyncio.sleep(0.5)
        
        # 3. Panggil/Fokus Builder Panel (Ctrl+I)
        print(f"⌨️ [{self.agent_id}] Panggil Builder via Ctrl+I...")
        pyautogui.hotkey('ctrl', 'i')
        # Tunggu lebih lama agar panel benar-benar ter-render (2.5s)
        await asyncio.sleep(2.5)
        
        # --- NEW: VERIFIKASI ELEMAN "BUILDER" (The Absolute Focus) ---
        print(f"🔍 [{self.agent_id}] Memverifikasi keberadaan kotak input AI Builder...")
        
        # Cari jendela Trae untuk mendapatkan PID
        root = auto.GetRootControl()
        trae_win = None
        for win in root.GetChildren():
            if 'trae' in win.Name.lower():
                trae_win = win
                break
        
        builder_input = None
        if trae_win:
            # [NEW] Ambil ProcessId dari jendela utama Trae untuk filter elemen
            trae_pid = trae_win.ProcessId
            
            # Cari input builder
            builder_input = self._find_builder_input(trae_win, trae_pid)
        
        # Jika tidak ketemu via search, coba ambil yang sedang fokus (sangat akurat setelah Ctrl+I)
        if not builder_input:
            focused = auto.GetFocusedControl()
            # Cek apakah elemen yang fokus ada di dalam jendela Trae secara aman
            is_trae_element = False
            try:
                curr = focused
                for _ in range(5): # Telusuri ke atas maksimal 5 level
                    if not curr: break
                    name = getattr(curr, 'Name', '').lower()
                    type_name = getattr(curr, 'ControlTypeName', '')
                    if 'trae' in name or type_name == 'WindowControl':
                        is_trae_element = True
                        break
                    curr = curr.GetParentControl()
            except: pass

            if focused and (getattr(focused, 'ControlTypeName', '') in ['EditControl', 'DocumentControl'] or is_trae_element):
                print(f"✅ [{self.agent_id}] Menemukan input melalui FocusedControl: {getattr(focused, 'Name', 'Unknown')}")
                builder_input = focused
                # Pastikan jendela Utama di Maximized untuk konsistensi koordinat fallback nantinya
                try:
                    win = builder_input.GetTopLevelWindow()
                    if win.GetWindowVisualState() != auto.WindowVisualState.Maximized:
                        win.SetWindowVisualState(auto.WindowVisualState.Maximized)
                except: pass

        if builder_input:
            print(f"✅ [{self.agent_id}] Elemen Builder ditemukan! Fokuskan...")
            builder_input.SetFocus()
            builder_input.Click()
            await asyncio.sleep(0.5)
            
            # Bersihkan teks lama secara aman
            builder_input.SendKeys('{Ctrl}a{Backspace}', waitTime=0.5)
        else:
            print(f"⚠️ [{self.agent_id}] Warning: Elemen tidak terdeteksi via UI Tree, beralih ke Fallback Click.")
            # Fallback Click (Posisi input Builder)
            width, height = pyautogui.size()
            target_x = int(0.85 * width)
            target_y = int(0.88 * height) 
            pyautogui.click(target_x, target_y)
            await asyncio.sleep(0.5)
        
        # C. Brute-Force Clear existing text (Select All + Backspace)
        # Dilakukan 2x untuk memastikan jika ada dialog 'Accept' atau 'Reject' yang tersisa
        for _ in range(2):
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            await asyncio.sleep(0.5)
        
        # --- NEW: VERIFIKASI INPUT SEBELUM SUBMIT ---
        if builder_input:
            try:
                # Gunakan UIA SendKeys yang lebih andal daripada pyautogui paste
                builder_input.SendKeys(str(instruction), waitTime=1.0)
                print(f"✅ [{self.agent_id}] Instruksi disuntikkan via UIA.")
            except:
                print(f"📋 [{self.agent_id}] UIA injection gagal, fallback ke Clipboard Paste...")
                pyperclip.copy(str(instruction))
                pyautogui.hotkey('ctrl', 'v')
        else:
            # Fallback total jika elemen fisik tidak ada
            pyperclip.copy(str(instruction))
            pyautogui.hotkey('ctrl', 'v')
        
        await asyncio.sleep(1.5)
        
        # --- NEW: BUKTI VISUAL (Reflect) ---
        print(f"📸 [{self.agent_id}] Mengambil bukti input...")
        self.driver.take_screenshot(f"proof_of_input_{ms_name}.png")
        
        # 4. Submit (Mekanisme Brute-Force)
        print("🚀 Submitting mission...")
        width, height = pyautogui.size()
        # Method 1: Hotkey
        for key in ["ctrl", "enter"]: pyautogui.keyDown(key)
        time.sleep(0.2)
        for key in ["enter", "ctrl"]: pyautogui.keyUp(key)
        await asyncio.sleep(1.0)
        
        # Method 2: Klik tombol Submit (Ikon Panah)
        submit_x = int(0.8990 * width)
        submit_y = int(0.7852 * height)
        pyautogui.click(submit_x, submit_y)
        await asyncio.sleep(0.5)
        
        # Method 3: Standard Enter (3x)
        for _ in range(3):
            pyautogui.press('enter')
            time.sleep(0.2)
        
        # 5. Catat ke SONA
        self.sona.record_step(
            agent_id=self.agent_id,
            action=f"Typed and Submitted to Trae Builder",
            observation="Task submitted. Awaiting monitoring feedback.",
            thought=f"Executing {ms_name} with instruction: {instruction}"
        )
        
        return {"status": "SUCCESS", "milestone": ms_name}

    def _find_builder_input(self, trae_win, trae_pid=None):
        """
        Mencari elemen input AI Builder secara rekursif di dalam jendela Trae.
        """
        try:
            # Pastikan jendela aktif
            trae_win.SetActive()
            
            def find_recursive(el, depth=0):
                if depth > 10: return None
                
                children = el.GetChildren()
                # Prioritas 1: Langsung cari EditControl/DocumentControl
                for child in children:
                    type_name = child.ControlTypeName
                    name = child.Name.lower()
                    
                    if type_name in ['EditControl', 'DocumentControl']:
                        # AI Builder biasanya tidak punya nama tetap, tapi seringkali mengandung kata kunci
                        if any(p in name for p in ['builder', 'ai', 'chat', 'input', 'ask', 'interactive', 'prompt']):
                            return child
                        # Fallback: Ambil EditControl pertama yang ditemui jika kedalaman cukup
                        if depth >= 2:
                            return child
                            
                # Prioritas 2: Telusuri lebih dalam
                for child in children:
                    res = find_recursive(child, depth + 1)
                    if res: return res
                return None
            
            result = find_recursive(trae_win)
            if not result:
                # Last resort: Ambil elemen yang sedang fokus saat ini jika milik proses Trae
                focused = auto.GetFocusedControl()
                if focused:
                    try:
                        # Gunakan ProcessId daripada GetTopLevelWindow() yang rapuh
                        if trae_pid and focused.ProcessId == trae_pid:
                            return focused
                        # Jika trae_pid tidak ada, minimal cek tipenya
                        if focused.ControlTypeName in ['EditControl', 'DocumentControl']:
                            return focused
                    except:
                        pass
                    
            return result
        except Exception as e:
            print(f"❌ [EYES] Error saat mencari elemen: {e}")
            return None

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
