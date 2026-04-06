import asyncio
import base64
import json
import os
import hashlib
import time
import re
import pyautogui
from openai import OpenAI
import subprocess
import webbrowser
from PIL import Image, ImageDraw, ImageFont
from computer_driver import ComputerDriver
from search_tool import WebSearch
from lightning_memory import LightningMemory
from config import SUMOPOD_API_KEY, SUMOPOD_BASE_URL, DEFAULT_MODEL
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
        
    async def _execute_terminal(self, instruction, update):
        """Menjalankan perintah shell/terminal secara otonom di PROJECT_ROOT."""
        active_root = os.getenv("PROJECT_ROOT", os.getcwd())
        if not os.path.exists(active_root):
            os.makedirs(active_root)
            
        print(f"🖥️ [TERMINAL] Base Dir: {active_root}")
        
        # Ekstrak dari blok kode triple backticks (prioritas utama) - Lebih fleksibel terhadap spasi/newline
        commands = re.findall(r'```(?:bash|sh|cmd|powershell)?\s*(.*?)\s*```', instruction, re.DOTALL)
        
        # Jika tidak ada blok kode, coba cari baris tunggal (backticks tunggal)
        if not commands:
            commands = re.findall(r'`([^`\n]+)`', instruction)
            
        print(f"DEBUG: Found commands: {commands}")
        
        # [NEW] Pre-processing: Bersihkan perintah dari Queen agar selalu non-interaktif
        processed_commands = []
        for cmd_block in commands:
            # Ganti npm create vite atau variasi lainnya dengan npx create-vite@latest ./ --no-interactive
            # Regex ini menangkap create-vite([@latest]?) [nama_folder] dan menggantinya
            cmd_block = re.sub(r'(npx |npm create |npm exec )(create-vite(@latest)?|vite)(?:\s+)?(\S+)?', 
                               r'\1create-vite@latest ./ --no-interactive ', cmd_block)
            
            # Pastikan flag --template ada jika belum ada
            if "create-vite" in cmd_block and "--template" not in cmd_block:
                cmd_block += " --template react-ts"
                
            processed_commands.append(cmd_block)
        
        commands = processed_commands

        # Jika masih tidak ada, coba cari perintah berbasis kata kunci (Penyelamat jika Queen lalai)
        if not commands:
            lines = instruction.split('\n')
            tech_keywords = ["npm ", "npx ", "git ", "mkdir ", "touch ", "cd "]
            potential_cmds = [line.strip() for line in lines if any(line.strip().lower().startswith(kw) for kw in tech_keywords)]
            if potential_cmds:
                print(f"🪄 [TERMINAL] Magic Extraction: Ditemukan {len(potential_cmds)} perintah tanpa backticks.")
                commands = ["\n".join(potential_cmds)]

        # Jika TETAP tidak ada, JANGAN jalankan instruksi narasi (hindari error 'Buat proyek...')
        if not commands:
            print(f"⚠️ [TERMINAL] No executable commands found in instruction. Skipping narrative text.")
            await update.message.reply_text("⚠️ **Terminal Warning:** Instruksi ini berupa narasi dan tidak mengandung blok kode perintah. Melewati...")
            return False

        print(f"DEBUG: Executing commands: {commands}")
        for cmd_block in commands:
            # INTEGRITY FIX: Gabungkan perintah berantai jika mengandung inisialisasi
            # Hal ini penting agar 'cd project && npm install' berjalan dalam satu sub-proses shell.
            if "&&" in cmd_block:
                individual_cmds = [cmd_block.strip()]
            else:
                individual_cmds = [l.strip() for l in cmd_block.split('\n') if l.strip()]

            for cmd in individual_cmds:
                # Filter narasi
                forbidden_starts = ["buat", "jalankan", "hentikan", "create", "stop", "masuk ke"]
                if not cmd or cmd.startswith('#') or any(cmd.lower().startswith(f) for f in forbidden_starts if " " in cmd): 
                    continue
                
                # Fix: Jika "npm create vite ... [nama]", ganti nama folder jadi "./" agar init di folder saat ini
                if "create-vite" in cmd or "create vite" in cmd:
                    # 1. Pastikan npx -y dan --no-interactive digunakan agar tidak ada prompt apapun
                    if "npx " in cmd and "-y" not in cmd:
                        cmd = cmd.replace("npx ", "npx -y ")
                    elif "npm create" in cmd:
                         cmd = cmd.replace("npm create", "npx -y create")
                    
                    if "--no-interactive" not in cmd:
                        cmd = cmd.replace("create-vite ", "create-vite@latest ./ --no-interactive ")
                        cmd = cmd.replace("create vite ", "create-vite@latest ./ --no-interactive ")
                    
                    # 2. Bersihkan nama proyek dari argumen: ganti nama folder yang diberikan dengan './'
                    # Contoh: npx create-vite my-app -> npx create-vite ./
                    cmd = re.sub(r'(create-vite@latest\s+)(\S+)', r'\1./', cmd)
                    
                    # 3. Clean-up chained 'cd' commands: Jika ada '&& cd [nama_proyek]', buang bagian cd-nya
                    # Karena kita sudah memaksa instalasi di './'
                    cmd = re.sub(r'&&\s*cd\s+\S+\s*&&', '&&', cmd)
                    cmd = re.sub(r'&&\s*cd\s+\S+\s*$', '', cmd)

                    # 4. Pastikan ada flag --template
                    if "--template" not in cmd:
                        cmd += " --template react"
                    print(f"🔧 [HARDENED V2] Project Init command: {cmd}")
                
                # Skip "cd" individual jika dia berdiri sendiri (tidak dalam rantai &&)
                if cmd.strip().startswith("cd ") and "&&" not in cmd:
                    print(f"⏭️ Skipping standalone cd: {cmd}")
                    continue

                await update.message.reply_text(f"📟 **Executing:** `{cmd[:120]}`")
                try:
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        cwd=active_root,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    # TIMEOUT 120 detik! Jika npm menggantung, kita lanjut
                    try:
                        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300) # Tingkatkan ke 300s untuk npm install
                        
                        # Settling Delay: Jika ini perintah init proyek, tunggu agar file stabil di disk
                        if any(x in cmd for x in ["create-", "npx ", "init"]):
                            print("⏳ Settling Delay: Menunggu file sistem (5s)...")
                            await asyncio.sleep(5)
                            
                            # Jalankan git init jika folder belum merupakan repository git
                            if not os.path.exists(os.path.join(self.base_dir, ".git")):
                                print("📂 [GIT] Initializing new repository...")
                                os.system(f'cd /d "{self.base_dir}" && git init')
                            
                        if process.returncode == 0:
                            output = stdout.decode().strip()
                            if output:
                                print(f"✅ Output: {output[:200]}...")
                                await update.message.reply_text(f"✅ **OK:** `{cmd[:60]}`")
                        else:
                            error = stderr.decode().strip()
                            print(f"⚠️ Terminal Error: {error[:200]}")
                            await update.message.reply_text(f"⚠️ **Warning:**\n`{error[:200]}`")
                            
                    except asyncio.TimeoutError:
                        process.kill()
                        await update.message.reply_text(f"⏰ **Timeout:** `{cmd}` terlalu lama (>300s). Melanjutkan...")
                        
                except Exception as e:
                    print(f"❌ Subprocess Execution Error: {e}")
                    await update.message.reply_text(f"❌ **Terminal Error:** `{str(e)}`")
        
        # [NEW] [EYES] Verifikasi Integritas Proyek (Mencegah folder kosong)
        if any("create-vite" in cb or "init" in cb for cb in commands):
            if not self._verify_project_integrity(active_root):
                await update.message.reply_text("⛔ **Integrity Error:** Project init gagal (folder kosong). Membatalkan sisa misi.")
                return False
        
        return True

    def _verify_project_integrity(self, path):
        """Memastikan folder proyek berisi file scaffold Vite yang valid."""
        critical_files = ["package.json", "index.html"]
        found_files = os.listdir(path)
        print(f"🔍 [INTEGRITY] Checking {path}... Found: {found_files}")
        
        for f in critical_files:
            if f not in found_files:
                return False
        
        # Cek apakah package.json berisi scripts dev (bukan file kosong)
        try:
            with open(os.path.join(path, "package.json"), "r") as f:
                data = json.load(f)
                if "scripts" not in data or "dev" not in data["scripts"]:
                    return False
        except:
            return False
            
        return True

    async def _execute_browser_preview(self, update):
        """Membuka browser dan mengambil screenshot hasil akhir."""
        url = "http://localhost:3000" # Default untuk Next.js/Vite
        await update.message.reply_text(f"🌐 **Opening Browser:** {url}")
        
        try:
            webbrowser.open(url)
            await asyncio.sleep(5.0) # Tunggu loading
            
            # Ambil screenshot
            img_path = self.driver.take_screenshot()
            await update.message.reply_photo(photo=open(img_path, 'rb'), caption="📸 **Visual Verification Result**")
            return True
        except Exception as e:
            await update.message.reply_text(f"⚠️ Gagal membuka browser: {e}")
            return False

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
        # Muat ulang project root dari environment
        current_root = os.getenv("PROJECT_ROOT", os.getcwd())
        self.initial_snapshot = self._get_recursive_snapshot(current_root)
        
        # 3. Eksekusi Swarm melalui Workers
        for i, ms in enumerate(milestones):
            ms_name = ms.get('name', f'Stage {i+1}')
            ms_instruction = ms.get('instruction', '')
            agent_id = ms.get('required_agent', 'coder_trae')
            
            await update.message.reply_text(f"🏗️ **MENGERJAKAN [{i+1}/{len(milestones)}]:** {ms_name}\n👤 **Agent:** `{agent_id}`\n📜 **Instruksi:**\n{ms_instruction}")
            
            # Dispatch ke metode eksekusi agen yang sesuai
            if agent_id == 'coder_trae':
                await self._execute_coder_trae_stage(ms, i, milestones, update)
            elif agent_id == 'terminal_bot':
                await self._execute_terminal_stage(ms, i, milestones, update)
            elif agent_id == 'browser_bot':
                await self._execute_browser_stage(ms, update)

        # 4. Neural Distillation (Knowledge Bank)
        await self._final_distillation(update)
    
    async def _execute_coder_trae_stage(self, ms, i, milestones, update):
        """Spesifik untuk agen Coder Trae: GUI Interaction + Monitoring."""
        ms_name = ms.get('name', 'Coder Task')
        ms_instruction = ms.get('instruction', '')
        agent_id = 'coder_trae'
        
        # 1. Reflect Pre-state
        self.driver.capture_screen("reflect_before.png")
        
        # 2. Eksekusi Milestones (Typing)
        await self.trae_worker.execute_milestone(ms)
        await update.message.reply_text(f"⌨️ **Bot Mengetik:** `{ms_instruction[:80]}...`")
        
        # 3. Reflect Post-state & Monitoring
        await asyncio.sleep(2.0)
        self.driver.capture_screen("reflect_after.png")
        print(f"📸 [REFLECT] Snapshot diambil untuk milestone: {ms_name}")

        # Monitoring Loop untuk deteksi file baru/berubah
        max_wait = 60
        code_found = False
        for wait_step in range(max_wait):
            await asyncio.sleep(2.0)
            active_root = os.getenv("PROJECT_ROOT", os.getcwd())
            current_snapshot = self._get_recursive_snapshot(active_root)
            real_changes = [f for f in current_snapshot if (f not in self.initial_snapshot or current_snapshot[f] > self.initial_snapshot[f]) and any(ext in f for ext in ['.tsx', '.ts', '.js', '.css', '.html', '.json'])]
            
            if real_changes:
                code_found = True
                await update.message.reply_text(f"✅ **Milestone Sukses:** {ms_name}\n📂 File kode terdeteksi.")
                self.initial_snapshot = current_snapshot
                self.sona.record_step(agent_id, "SUCCESS", f"Changes detected: {real_changes}", status="SUCCESS")
                break
            
            if wait_step % 10 == 0:
                print(f"⏳ Monitoring changes for {ms_name}...")

        if not code_found:
            await update.message.reply_text(f"⚠️ **Timeout:** {ms_name}. Melanjutkan...")
            self.sona.record_step(agent_id, "TIMEOUT", "No code detected within timeframe.", status="TIMEOUT")

    async def _execute_terminal_stage(self, ms, i, milestones, update):
        """Spesifik untuk agen Terminal: Command Line execution."""
        ms_instruction = ms.get('instruction', '')
        ms_name = ms.get('name', 'Terminal Task')
        agent_id = 'terminal_bot'
        
        success = await self._execute_terminal(ms_instruction, update)
        if not success:
            # Fallback jika Queen gagal memberikan perintah (misal: untuk project init)
            if i == 0 or any(x in ms_name.lower() for x in ["inisialisasi", "init"]):
                project_root = os.getenv("PROJECT_ROOT", os.getcwd())
                auto_cmd = f"npx -y create-vite@latest ./ --template react-ts --no-interactive && npm install"
                await update.message.reply_text(f"🪄 **Auto-Init Fallback:**\n`{auto_cmd}`")
                
                try:
                    process = await asyncio.create_subprocess_shell(
                        auto_cmd, cwd=project_root,
                        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    await process.communicate()
                    if process.returncode == 0:
                        await update.message.reply_text(f"✅ **Auto-Init Berhasil!**")
                        self.sona.record_step(agent_id, "SUCCESS", f"Auto-init: {auto_cmd}", status="SUCCESS")
                        return
                except: pass
            
            await update.message.reply_text("⚠️ **Terminal Skip:** Melanjutkan ke tahap berikutnya...")
            self.sona.record_step(agent_id, "SKIPPED", "No valid commands.", status="SKIPPED")
        else:
            self.sona.record_step(agent_id, "SUCCESS", "Terminal commands executed.", status="SUCCESS")

    async def _execute_browser_stage(self, ms, update):
        """Spesifik untuk agen Browser Bot: Visual Preview."""
        success = await self._execute_browser_preview(update)
        if not success:
            self.sona.record_step("browser_bot", "WARNING", "Browser preview failed.", status="FAILED")
        else:
            self.sona.record_step("browser_bot", "SUCCESS", "Browser preview captured.", status="SUCCESS")

    async def _final_distillation(self, update):
        """Neural Distillation (Knowledge Bank) + Milestone Final Report."""
        # Tentukan status akhir
        verdict = "SUCCESS" if all(step.get('status') == "SUCCESS" for step in self.sona.current_trajectory) else "FAILED"
        path = self.sona.end_trajectory(verdict, "Project sequence completed.")
        
        with open(path, 'r') as f:
            trajectory_data = json.load(f)
            
        await update.message.reply_text("🧠 **Neural Distillation:** Menyaring pengalaman untuk Knowledge Bank...")
        knowledge_list = await self.bank.distill_trajectory(trajectory_data)
        
        # Handle string or list output (Safety)
        if isinstance(knowledge_list, str):
            try:
                knowledge_list = json.loads(knowledge_list)
            except:
                knowledge_list = [{"title": "New Knowledge", "category": "general"}]

        if knowledge_list:
            if isinstance(knowledge_list, dict): knowledge_list = [knowledge_list]
            for ki in knowledge_list:
                if not isinstance(ki, dict): continue
                title = ki.get('title', 'Untitled Knowledge')
                await update.message.reply_text(f"💡 **Pengetahuan Baru:**\n*{title}*")

        await update.message.reply_text("✨ **MISI SELESAI:** Seluruh Tahapan dan Distilasi Selesai.")
        # Ambil screenshot hasil akhir satu kali
        try:
            raw_img = self.driver.take_screenshot("final_result.png")
            await update.message.reply_photo(photo=open(raw_img, 'rb'), caption="🖼️ **Hasil Akhir Proyek**")
        except: pass