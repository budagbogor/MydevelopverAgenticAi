import asyncio
import base64
import json
import os
import hashlib
import time
import re
import pyautogui
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from computer_driver import ComputerDriver
from search_tool import WebSearch
from lightning_memory import LightningMemory
from swarm.queen import QueenCoordinator
from swarm.worker_trae import TraeWorker
from neural.sona import SonaMemory
from neural.bank import ReasoningBank

class Orchestrator:
    def __init__(self):
        self.sona = SonaMemory()
        self.bank = ReasoningBank()
        self.queen = QueenCoordinator()
        self.trae_worker = TraeWorker(self.sona)
        
        self.driver = ComputerDriver() # Legacy for fallback
        self.web_search = WebSearch()
        self.memory = LightningMemory() # Legacy support
        self.client = OpenAI(api_key=SUMOPOD_API_KEY, base_url=SUMOPOD_BASE_URL)
        self.history = []
        self.stuck_count = 0

    def _get_recursive_snapshot(self, directory):
        """Merekam seluruh struktur file secara rekursif untuk deteksi perubahan yang akurat."""
        snapshot = {}
        for root, dirs, files in os.walk(directory):
            # Abaikan folder sampah untuk performa
            if any(x in root for x in [".git", "node_modules", "vendor", ".next", "__pycache__"]):
                continue
            for name in files:
                filepath = os.path.join(root, name)
                try:
                    stats = os.stat(filepath)
                    snapshot[filepath] = stats.st_mtime
                except:
                    pass
        return snapshot

    def get_image_hash(self, image_path):
        try:
            img = Image.open(image_path).convert('L').resize((64, 64), Image.NEAREST)
            return hashlib.md5(img.tobytes()).hexdigest()
        except:
            return ""

    def draw_grid(self, image_path):
        try:
            img = Image.open(image_path).convert('RGB')
            w, h = img.size
            # --- HIGH FIDELITY (0.6 Scale) ---
            img = img.resize((int(w * 0.6), int(h * 0.6)), Image.LANCZOS)
            w, h = img.size
            draw = ImageDraw.Draw(img)
            for i in range(0, 101, 20):
                x, y = (i / 100) * w, (i / 100) * h
                draw.line([(x, 0), (x, h)], fill=(128, 128, 128, 128), width=1)
                draw.line([(0, y), (w, y)], fill=(128, 128, 128, 128), width=1)
            grid_path = image_path.replace(".png", "_optimized.jpg")
            img.save(grid_path, "JPEG", quality=80, optimize=True)
            return grid_path
        except Exception as e:
            print(f"⚠️ Gagal optimasi vision: {e}")
            return image_path

    def encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _get_relevant_skills(self, task_description):
        """Memindai folder skills/ dan memuat pengetahuan yang relevan dengan tugas."""
        skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        if not os.path.exists(skills_dir): return ""
        
        injected_context = "\n--- UNIVERSAL SKILLS LIBRARY (INJECTED) ---\n"
        task_lower = task_description.lower()
        found = False
        
        for file in os.listdir(skills_dir):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(skills_dir, file), 'r') as f:
                        skill_data = json.load(f)
                        # Pindai kecocokan keyword
                        if any(kw in task_lower for kw in skill_data.get('keywords', [])):
                            found = True
                            injected_context += f"CATEGORY: {skill_data['category']}\n"
                            injected_context += f"CORE BEST PRACTICES:\n- " + "\n- ".join(skill_data['best_practices']) + "\n"
                            injected_context += f"PREMIUM TECH STACK: {', '.join(skill_data['tech_stack'])}\n\n"
                except Exception as e:
                    print(f"⚠️ Gagal muat modul skill {file}: {e}")
        
        if found:
            injected_context += "INSTRUCTION: Terapkan standar di atas dalam blueprint pembangunan software ini agar hasilnya LUAR BIASA.\n"
            return injected_context
        return ""

    async def enhance_prompt(self, brief_task):
        """Mengubah input singkat menjadi daftar Milestone teknis yang terstruktur (JSON)."""
        print(f"🧠 [BRAINSTORMING] Memperluas prompt ke Milestones: {brief_task}")
        
        relevant_skills = self._get_relevant_skills(brief_task)
        
        enhancer_prompt = f"""
        Tugas Anda adalah sebagai Lead Software Architect.
        Ubah instruksi singkat pengguna berikut menjadi Rencana Pembangunan bertahap (Milestones).
        
        {relevant_skills}

        INSTRUKSI PENGGUNA: "{brief_task}"
        
        Pecah menjadi 3-5 Milestone teknis. Setiap Milestone HARUS mencakup:
        1. "name": Judul singkat tahap.
        2. "instruction": Instruksi JELAS (Maks 250 karakter) untuk diketikkan ke dalam AI Builder/Prompt (misal: "Create a modern Hero section with Hero.tsx, dark theme, and shadcn buttons"). JANGAN berikan instruksi yang terlalu panjang/bertele-tele karena akan membingungkan pelaksana.
        3. "is_ui_stage": Boolean (True jika ini adalah tahap pembuatan Halaman Produk/UI visual).

        FORMAT KELUARAN WAJIB JSON:
        {{
            "master_plan_summary": "Ringkasan strategi besar.",
            "milestones": [
                {{ "name": "Inisialisasi", "instruction": "...", "is_ui_stage": false }},
                {{ "name": "Frontend UI", "instruction": "...", "is_ui_stage": true }}
            ]
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a Software Architect. Break down missions into professional technical JSON milestones."},
                    {"role": "user", "content": enhancer_prompt}
                ],
                response_format={"type": "json_object"}
            )
            res_data = json.loads(response.choices[0].message.content.strip())
            print(f"✅ [BRAINSTORMING DONE] {len(res_data.get('milestones', []))} Milestones diciptakan.")
            return res_data
        except Exception as e:
            print(f"⚠️ Gagal brainstorming milestone: {e}")
            return {
                "master_plan_summary": brief_task,
                "milestones": [{"name": "Eksekusi Utama", "instruction": brief_task, "is_ui_stage": True}]
            }

    async def process_task(self, task_brief, update):
        """
        Orkestrasi Tugas Menggunakan Swarm Intelligence (RuFlo Style).
        """
        await update.message.reply_text("👑 **Swarm Queen:** Sedang melakukan dekomposisi misi strategis...")
        
        # 1. Dekomposisi tingkat tinggi oleh Queen
        plan = await self.queen.decompose_task(task_brief)
        summary = plan.get('strategy', '')
        milestones = plan.get('milestones', [])
        
        await update.message.reply_text(f"📝 **STRATEGI BESAR:**\n{summary}\n\n🏃 **Target:** {len(milestones)} Milestones.")
        
        # 2. Inisiasi Track Memory (SONA)
        self.sona.start_trajectory(task_brief)
        self.initial_snapshot = self._get_recursive_snapshot(PROJECT_ROOT)
        
        # 3. Eksekusi Swarm melalui Workers
        for i, ms in enumerate(milestones):
            ms_name = ms.get('name', f'Stage {i+1}')
            ms_instruction = ms.get('instruction', '')
            agent_id = ms.get('required_agent', 'coder_trae')
            
            await update.message.reply_text(f"🏗️ **MENGERJAKAN [{i+1}/{len(milestones)}]:** {ms_name}\n👤 **Agent:** `{agent_id}`\n📜 **Instruksi:**\n{ms_instruction}")
            
            # Eksekusi Milestones (Trae Worker khusus GUI)
            if agent_id == 'coder_trae':
                result = await self.trae_worker.execute_milestone(ms)
                await update.message.reply_text(f"⌨️ **Bot Mengetik:** `{ms_instruction[:80]}...`")
                
                # FASE 2: MONITORING LOOP (Tunggu file berubah)
                max_wait = 60
                code_found = False
                for wait_step in range(max_wait):
                    await asyncio.sleep(2.0)
                    current_snapshot = self._get_recursive_snapshot(PROJECT_ROOT)
                    real_changes = [f for f in current_snapshot if (f not in self.initial_snapshot or current_snapshot[f] > self.initial_snapshot[f]) and any(ext in f for ext in ['.tsx', '.ts', '.js', '.css', '.html'])]
                    
                    if real_changes:
                        code_found = True
                        await update.message.reply_text(f"✅ **Milestone Sukses:** {ms_name}\n📂 File kode terdeteksi.")
                        self.initial_snapshot = current_snapshot
                        self.sona.record_step(agent_id, "SUCCESS", f"Changes detected: {real_changes}")
                        break
                    
                    if wait_step % 5 == 0:
                        print(f"⏳ Monitoring changes for {ms_name}...")

                if not code_found:
                    await update.message.reply_text(f"⚠️ **Timeout:** {ms_name}. Melanjutkan...")
                    self.sona.record_step(agent_id, "TIMEOUT", "No code detected within timeframe.")

        # 4. Neural Distillation (Knowledge Bank)
        path = self.sona.end_trajectory("SUCCESS", "Project completed.")
        with open(path, 'r') as f:
            trajectory_data = json.load(f)
            
        await update.message.reply_text("🧠 **Neural Distillation:** Menyaring pengalaman untuk Knowledge Bank...")
        ki = await self.bank.distill_trajectory(trajectory_data)
        if ki:
            await update.message.reply_text(f"💡 **Pengetahuan Baru Disimpan:**\n*{ki['title']}*\nCategory: {ki['category']}")

        await update.message.reply_text("✨ **MISI SELESAI:** Seluruh Milestone dan Distilasi telah selesai.")
        # Kirim layar terakhir jika stage terakhir adalah UI
        if milestones and milestones[-1].get('is_ui_stage'):
             try:
                 raw_img = self.driver.take_screenshot()
                 await update.message.reply_photo(photo=open(raw_img, 'rb'), caption="🖼️ **Hasil Akhir Proyek**")
             except: pass