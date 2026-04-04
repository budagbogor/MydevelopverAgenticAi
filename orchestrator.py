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
        2. "instruction": Instruksi sangat detail untuk agen coding (path file, logic, dsb).
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
        
        # Tunjukkan Ringkasan Rencana
        await update.message.reply_text(f"📝 **STRATEGI BESAR:**\n{summary}\n\n🏃 **Target:** {len(milestones)} Milestones.")

        # Ambil daftar file awal untuk validasi
        self.initial_files = set(os.listdir(PROJECT_ROOT))
        self.history = []
        self.stuck_count = 0
        self.searched_queries = set()
        self.search_count = 0
        max_search_limit = 5
        
        # LOOP MILESTONES (INCREMENTAL EXECUTION)
        for i, ms in enumerate(milestones):
            ms_name = ms.get('name', f'Stage {i+1}')
            ms_instruction = ms.get('instruction', '')
            is_ui = ms.get('is_ui_stage', False)
            
            await update.message.reply_text(f"🏗️ **MENGERJAKAN [{i+1}/{len(milestones)}]:** {ms_name}")
            
            # --- MIN-Autonomous Loop per Milestone ---
            max_steps = 15 # Fokus pendek per milestone
            for step in range(max_steps):
                if not self.driver.ensure_focus(): pass
                
                await asyncio.sleep(0.1)
                raw_img = self.driver.take_screenshot()
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
                - Jika ini tahap UI (is_ui_stage=True), pastikan tampilan terlihat di layar.
                - Jika sudah selesai dengan milestone ini, balas dengan status "SELESAI".
                - Jangan SELESAI jika belum membuat file/perubahan nyata.
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
                        # Validasi sederhana
                        current_files = set(os.listdir(PROJECT_ROOT))
                        if current_files - self.initial_files or step > 3:
                            await update.message.reply_text(f"✅ **Milestone Berhasil:** {ms_name}")
                            break # Lanjut ke Milestone berikutnya
                        else:
                            # Paksa lanjut jika belum ada bukti kerja
                            status = "PROSES"

                    # Execute Actions
                    for action in actions:
                        a_type = action.get('type')
                        a_params = action.get('params', [])
                        
                        if a_type == "SEARCH":
                            if self.search_count < max_search_limit:
                                query = a_params[0].strip() if a_params else ""
                                self.last_search_results = self.web_search.get_formatted_string(query)
                                self.search_count += 1
                            continue

                        self.driver.execute_action(a_type, a_params)
                        await asyncio.sleep(0.1)

                except Exception as e:
                    print(f"⚠️ Error dalam Milestone loop: {e}")
                    await asyncio.sleep(1)

        await update.message.reply_text("✨ **MISI SELESAI:** Seluruh Milestone telah dikerjakan.")
        # Kirim layar terakhir jika stage terakhir adalah UI
        if milestones and milestones[-1].get('is_ui_stage'):
             raw_img = self.driver.take_screenshot()
             await update.message.reply_photo(photo=open(raw_img, 'rb'), caption="🖼️ **Hasil Akhir Proyek**")

        # Ambil daftar file awal untuk validasi
        self.initial_files = set(os.listdir(PROJECT_ROOT))

        self.history = []
        self.stuck_count = 0
        self.master_plan = ""
        self.last_screenshot_hash = ""
        self.last_search_results = ""
        self.searched_queries = set()
        self.search_count = 0
        max_search_limit = 5

        max_steps = 40
        last_image_path = None
        
        try:
            for step in range(max_steps):
                if not self.driver.ensure_focus():
                    print(f"⚠️ Peringatan: Jendela aplikasi target belum aktif.")
                
                await asyncio.sleep(0.1) # --- FAST REACTION ---
                raw_img = self.driver.take_screenshot()
                current_hash = self.get_image_hash(raw_img)
                is_stuck = current_hash == self.last_screenshot_hash
                self.last_screenshot_hash = current_hash
                
                if is_stuck: self.stuck_count += 1
                else: self.stuck_count = 0

                grid_img = self.draw_grid(raw_img)
                last_image_path = grid_img
                base64_img = self.encode_image(grid_img)
                active_win = self.driver.get_active_window()
                learning_context = self.memory.get_formatted_for_prompt(active_win, task_description)

                prompt = f"""
                GOAL: {task_description}
                Step: {step + 1}/{max_steps}
                Status: {"STUCK" if is_stuck else "OK"}
                Active Window: "{active_win}"
                Project: {PROJECT_ROOT}
                
                {learning_context}

                MASTER_PLAN: {self.master_plan if self.master_plan else "Inisialisasi."}
                SEARCH_RESULTS: {self.last_search_results if self.last_search_results else "N/A"}

                INSTRUCTION:
                - OBSERVASI TERMINAL: JANGAN mengetik "y" atau karakter konfirmasi kecuali Anda melihat JELAS ada pertanyaan "(y/n)" atau "?" di layar.
                - SEBELUM MENGETIK: Jika ingin mengetik perintah, CLICK area terminal terlebih dahulu.
                - Autonomous Decision: Answer IDE checklists/questions with default stacks (Next.js/Tailwind).
                - Use HOTKEYS when possible.
                - STATUS SELESAI: Gunakan status "SELESAI" HANYA jika Anda yakin semua instruksi telah dijalankan.
                - ATURAN STOP TEGAS: Dilarang SELESAI jika Anda belum membuat file baru. Langkah pertama wajib berupa inisialisasi (misal: buat README.md atau project_structure.txt).
                - Jika layar hanya menampilkan desktop pengerjaan Anda dianggap MASIH PROSES. Anda HARUS mengklik {TARGET_IDE} atau Terminal.

                RESPOND WITH VALID JSON:
                {{
                    "status": "PROSES/SELESAI",
                    "critique": "Analisis.",
                    "new_master_plan": "Update.",
                    "actions": [
                        {{ "type": "CLICK", "params": [x, y] }},
                        {{ "type": "HOTKEY", "params": ["ctrl", "s"] }},
                        {{ "type": "TYPE", "params": ["text"] }},
                        {{ "type": "WAIT", "params": [0.1] }}
                    ]
                }}
                """

                try:
                    response = self.client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a Universal Software Operator. Return ONLY valid JSON."},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                            ]}
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    raw_content = response.choices[0].message.content.strip()
                    
                    try:
                        res = json.loads(raw_content)
                    except:
                        cleaned = re.search(r'(\{.*\})', raw_content, re.DOTALL)
                        if cleaned: res = json.loads(cleaned.group(1))
                        else: raise ValueError("JSON Error")

                    if res.get('new_master_plan'):
                        self.master_plan = res['new_master_plan']

                    actions = res.get('actions', [])
                    if res.get('status') == "SELESAI":
                        # --- PHYSICAL FILE VALIDATION ---
                        current_files = set(os.listdir(PROJECT_ROOT))
                        new_files = current_files - self.initial_files
                        
                        # Filter out common junk/logs if any
                        real_changes = [f for f in new_files if not f.endswith('.log') and f != 'bot.lock']
                        
                        if step < 3 or not real_changes:
                            print(f"⚠️ Menolak status SELESAI prematur (Langkah {step + 1}). Tidak ada file baru terdeteksi.")
                            self.master_plan = f"Pekerjaan belum selesai. Saya tidak melihat adanya file baru di {PROJECT_ROOT}. Anda WAJIB memulai dengan membuat README.md atau inisialisasi proyek melalui terminal. JANGAN SELESAI jika folder masih kosong!"
                            await update.message.reply_text("⚠️ **Bot Berusaha Selesai Terlalu Cepat:** Memaksa lanjut ke fase inisialisasi...")
                        else:
                            await update.message.reply_text("✨ **Tugas Selesai.**")
                            break

                    for action in actions:
                        a_type = action.get('type')
                        a_params = action.get('params', [])

                        if a_type == "SEARCH":
                            if self.search_count < max_search_limit:
                                query = a_params[0].strip() if a_params else ""
                                await update.message.reply_text(f"🔍 **Riset:** {query}")
                                self.last_search_results = self.web_search.get_formatted_string(query)
                                self.search_count += 1
                            break 

                        if is_stuck and self.stuck_count >= 2:
                            recovery_action = ["HOTKEY", ["ctrl", "enter"]] if "trae" in active_win.lower() else ["HOTKEY", ["esc"]]
                            self.driver.execute_action(recovery_action[0], recovery_action[1])
                            await update.message.reply_text(f"⚡ **Recovery:** Stuck.")
                            await asyncio.sleep(0.2)
                            self.stuck_count = 0
                            break

                        if a_type:
                            self.driver.execute_action(a_type, a_params)
                            # --- ULTRA FAST COMMANDS ---
                    
                    await asyncio.sleep(0.1)

                except Exception as e:
                    await update.message.reply_text(f"❌ Gangguan: {str(e)}")
                    break

        except Exception as outer_e:
            await update.message.reply_text(f"❌ Fatal: {str(outer_e)}")
        
        finally:
            if last_image_path and os.path.exists(last_image_path):
                try:
                    with open(last_image_path, 'rb') as photo:
                        await update.message.reply_photo(photo=photo, caption="🖼️ **Layar Terakhir**")
                except: pass