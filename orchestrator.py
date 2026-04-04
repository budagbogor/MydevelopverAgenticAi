import asyncio
import base64
import json
import os
import hashlib
import time
import re
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from computer_driver import ComputerDriver
from search_tool import WebSearch
from lightning_memory import LightningMemory
from config import SUMOPOD_API_KEY, SUMOPOD_BASE_URL, DEFAULT_MODEL, TARGET_IDE, PROJECT_ROOT

class Orchestrator:
    def __init__(self):
        self.driver = ComputerDriver()
        self.web_search = WebSearch()
        self.memory = LightningMemory() # LIGHTNING MEMORY INTEGRATION
        self.client = OpenAI(api_key=SUMOPOD_API_KEY, base_url=SUMOPOD_BASE_URL)
        self.history = []
        self.master_plan = []
        self.last_screenshot_hash = ""
        self.stuck_count = 0
        self.last_search_results = ""
        self.searched_queries = set()
        self.search_count = 0

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
        2. "instruction": Instruksi SANGAT DETAIL untuk diketikkan ke dalam AI Builder/Prompt (misal: "Ketik di Builder: 'Create a responsive Hero section with Tailwind CSS, a catchy headline, and a dark theme in Hero.tsx'"). JANGAN hanya memberikan nama file.
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
        # --- BRAINSTORMING / MILESTONE GENERATOR ---
        await update.message.reply_text("🧠 **Brainstorming:** Sedang menyusun strategi pembangunan bertahap...")
        plan_data = await self.enhance_prompt(task_brief)
        
        summary = plan_data.get('master_plan_summary', '')
        milestones = plan_data.get('milestones', [])
        
        # Ringkasan strategi besar
        await update.message.reply_text(f"📝 **STRATEGI BESAR:**\n{summary}\n\n🏃 **Target:** {len(milestones)} Milestones.")

        # Snapshot Rekursif Awal
        self.initial_snapshot = self._get_recursive_snapshot(PROJECT_ROOT)
        self.history = []
        self.stuck_count = 0
        self.last_screenshot_hash = "" # Tambahkan tracking hash
        self.searched_queries = set()
        self.search_count = 0
        max_search_limit = 5
        
        # LOOP MILESTONES (INCREMENTAL EXECUTION)
        for i, ms in enumerate(milestones):
            ms_name = ms.get('name', f'Stage {i+1}')
            ms_instruction = ms.get('instruction', '')
            is_ui = ms.get('is_ui_stage', False)
            
            await update.message.reply_text(f"🏗️ **MENGERJAKAN [{i+1}/{len(milestones)}]:** {ms_name}\n\n📜 **Instruksi:**\n{ms_instruction}")
            
            # --- MIN-Autonomous Loop per Milestone ---
            max_steps = 15 # Fokus pendek per milestone
            for step in range(max_steps):
                if not self.driver.ensure_focus(): pass
                
                await asyncio.sleep(0.1)
                raw_img = self.driver.take_screenshot()
                
                # --- VISUAL STUCK DETECTION ---
                current_hash = self.get_image_hash(raw_img)
                if current_hash == self.last_screenshot_hash:
                    self.stuck_count += 1
                else:
                    self.stuck_count = 0
                self.last_screenshot_hash = current_hash
                
                if self.stuck_count >= 5:
                    print(f"⚠️ VISUAL STUCK DETECTED di Milestone '{ms_name}'! Mencoba memulihkan fokus...")
                    self.driver.ensure_focus(force_restart=False)
                    self.driver.execute_action("HOTKEY", ["esc"])
                    self.driver.execute_action("CLICK", [50, 50]) # Klik tengah untuk aktivasi
                    self.stuck_count = 0
                    await update.message.reply_text(f"⚠️ **Visual Stuck:** Bot mendeteksi layar tidak berubah. Mencoba kalibrasi fokus...")
                
                grid_img = self.draw_grid(raw_img)
                base64_img = self.encode_image(grid_img)
                active_win = self.driver.get_active_window()
                
                # Context Milestone
                learning_context = self.memory.get_formatted_for_prompt(active_win, ms_instruction)
                
                prompt = f"""
                CURRENT MILESTONE: {ms_name}
                OBJECTIVE: {ms_instruction}
                Progress: Step {step + 1}/{max_steps} in this stage.
                Active Window: "{active_win}"
                
                {learning_context}

                INSTRUCTION:
                - Your OBJECTIVE is: {ms_instruction}
                - YOU MUST FOLLOW THIS OBJECTIVE VERBATIM. If the objective says "Ketik di Builder: '...'", you MUST type exactly that text.
                - NEVER say "SELESAI" if Trae has not finished generating code.
                - VERIFY PHYSICAL CHANGE: You MUST see new files or code in the editor before finishing.
                - If stuck, click the input box and re-type.
                - Balas dengan status "SELESAI" hanya jika pekerjaan sudah benar-benar terwujud di kode.
                """

                try:
                    response = self.client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a professional software developer operator. Return ONLY valid JSON."},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                            ]}
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    res = json.loads(response.choices[0].message.content.strip())
                    actions = res.get('actions', [])
                    status = res.get('status', 'PROSES')

                    # LOG NOTIFICATION (Visuals only for UI Stage)
                    if is_ui and step % 3 == 0:
                        await update.message.reply_photo(photo=open(grid_img, 'rb'), caption=f"📸 **Progress UI: {ms_name}**")

                    if status == "SELESAI":
                        # --- STRICT PHYSICAL VALIDATION (Recursive) ---
                        current_snapshot = self._get_recursive_snapshot(PROJECT_ROOT)
                        # Cari perbedaan (file baru atau file berubah waktu modifikasinya)
                        new_files = [f for f in current_snapshot if f not in self.initial_snapshot]
                        changed_files = [f for f, t in current_snapshot.items() if f in self.initial_snapshot and t > self.initial_snapshot[f]]
                        
                        # Filter out logs, lock files, and hidden OS files
                        real_changes = [f for f in (new_files + changed_files) if not any(x in f for x in ['.log', 'bot.lock', '.DS_Store', 'node_modules', '.next'])]
                        
                        if not real_changes:
                            print(f"⚠️ REJECTED: Bot mencoba SELESAI Milestone '{ms_name}' tanpa hasil fisik nyata.")
                            # Suntikkan peringatan ke prompt berikutnya
                            status = "PROSES"
                            ms_instruction += "\n\nCRITICAL WARNING: Verifikasi gagal. Saya tidak menemukan perubahan file apapun. Anda HARUS mengetikkan instruksi ke Trae Builder (Ctrl+Enter) dan menunggu hingga kode muncul sebelum menyatakan SELESAI."
                        else:
                            await update.message.reply_text(f"✅ **Milestone Berhasil:** {ms_name}\n📂 Perubahan terdeteksi pada {len(real_changes)} file.")
                            # Update snapshot untuk milestone berikutnya
                            self.initial_snapshot = current_snapshot
                            break # Lanjut ke Milestone berikutnya

                    # Execute Actions (WITH FULL DISCLOSURE)
                    for action in actions:
                        a_type = action.get('type')
                        a_params = action.get('params', [])
                        
                        if a_type == "SEARCH":
                            if self.search_count < max_search_limit:
                                query = a_params[0].strip() if a_params else ""
                                self.last_search_results = self.web_search.get_formatted_string(query)
                                self.search_count += 1
                            continue

                        # Telegram Mirroring
                        if a_type == "TYPE":
                            await update.message.reply_text(f"⌨️ **Bot Mengetik:** `{a_params[0]}`")
                        elif a_type == "CLICK":
                            await update.message.reply_text(f"🖱️ **Bot Klik di:** `{a_params}`")
                        elif a_type == "HOTKEY":
                            await update.message.reply_text(f"🎹 **Bot Hotkey:** `{a_params}`")

                        # Console Logging
                        print(f"🤖 Agent Action: {a_type}({a_params})")
                        self.driver.execute_action(a_type, a_params)
                        
                        # --- AUTO-SUBMIT HOTKEY (Trae Builder) ---
                        if a_type == "TYPE":
                            await asyncio.sleep(0.5)
                            self.driver.execute_action("HOTKEY", ["ctrl", "enter"])
                            print("⌨️ Auto-Submit: Ctrl+Enter sent.")
                        
                        await asyncio.sleep(0.8) # Beri jeda lebih lama untuk verifikasi

                        # Kirim Screenshot Bukti jika aksi penting
                        if a_type in ["TYPE", "CLICK", "ENTER", "HOTKEY"]:
                             post_img = self.driver.take_screenshot()
                             post_grid = self.draw_grid(post_img)
                             await update.message.reply_photo(photo=open(post_grid, 'rb'), caption=f"📸 **Hasil Aksi: {a_type}**")

                except Exception as e:
                    print(f"⚠️ Error dalam Milestone loop: {e}")
                    await asyncio.sleep(1)

        await update.message.reply_text("✨ **MISI SELESAI:** Seluruh Milestone telah dikerjakan.")
        # Kirim layar terakhir jika stage terakhir adalah UI
        if milestones and milestones[-1].get('is_ui_stage'):
             try:
                 raw_img = self.driver.take_screenshot()
                 await update.message.reply_photo(photo=open(raw_img, 'rb'), caption="🖼️ **Hasil Akhir Proyek**")
             except: pass