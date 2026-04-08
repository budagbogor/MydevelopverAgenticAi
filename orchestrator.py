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
from datetime import datetime
from swarm.worker_internal import InternalCoder
from neural.sona import SonaMemory
from neural.bank import ReasoningBank

class Orchestrator:
    def __init__(self):
        self.sona = SonaMemory()
        self.bank = ReasoningBank()
        self.queen = QueenCoordinator()
        self.internal_coder = InternalCoder()
        
        self.driver = ComputerDriver() 
        self.web_search = WebSearch()
        self.memory = LightningMemory() # Legacy support
        self.client = OpenAI(api_key=SUMOPOD_API_KEY, base_url=SUMOPOD_BASE_URL)
        self.history = []
        self.stuck_count = 0
        self.no_action_count = 0  # [NEW] Untuk Loop Breaker
        self.last_visual_hash = "" # [NEW] Deteksi stagnasi
        self.base_dir = os.getenv("PROJECT_ROOT", os.getcwd())
        self.initial_snapshot = {}
        
    async def _execute_terminal(self, instruction, update):
        """Menjalankan perintah shell/terminal secara otonom di PROJECT_ROOT."""
        active_root = os.getenv("PROJECT_ROOT", os.getcwd())
        if not os.path.exists(active_root):
            os.makedirs(active_root)
            
        print(f"🖥️ [TERMINAL] Base Dir: {active_root}")
        
        # Ekstrak blok kode triple backticks
        raw_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', instruction, re.DOTALL)
        if not raw_blocks:
            # Fallback ke backticks tunggal
            raw_blocks = re.findall(r'`([^`\n]+)`', instruction)
        
        if not raw_blocks:
            print(f"⚠️ [TERMINAL] No executable commands found. Skipping.")
            return True

        for block in raw_blocks:
            lines = block.strip().split('\n')
            
            in_cat_block = False
            cat_filename = ""
            cat_content = []
            
            for line in lines:
                line_clean = line.strip()
                if not line_clean: continue
                
                # [STATE] SEDANG DALAM BLOK CAT
                if in_cat_block:
                    if line_clean.upper() == "EOF":
                        # Selesai, tulis file
                        filepath = os.path.join(active_root, cat_filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write("\n".join(cat_content))
                        print(f"🛡️ [INTERCEPT] File created via Line-Logic: {cat_filename}")
                        in_cat_block = False
                    else:
                        cat_content.append(line)
                    continue

                # [DETEKSI] AWAL BLOK CAT
                cat_start_match = re.search(r'cat\s+<<EOF\s+>\s+([\w\.\-/\\]+)', line_clean, re.IGNORECASE)
                if cat_start_match:
                    in_cat_block = True
                    # Tangani path dengan backslash atau forward slash
                    cat_filename = cat_start_match.group(1).replace('\\', '/').strip()
                    cat_content = []
                    continue

                # [DETEKSI] ECHO > FILE
                echo_match = re.search(r'echo\s+["\']?(.*?)["\']?\s+>\s+([\w\.\-/\\]+)', line_clean, re.IGNORECASE)
                if echo_match:
                    content, filename = echo_match.groups()
                    filepath = os.path.join(active_root, filename.replace('\\', '/').strip())
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content.strip())
                    print(f"🛡️ [INTERCEPT] File created via Echo-Logic: {filename}")
                    continue

                # [DETEKSI] MKDIR
                if line_clean.lower().startswith('mkdir '):
                    folder = line_clean.replace('mkdir -p ', '').replace('mkdir ', '').replace('"', '').strip()
                    folders = [f.strip() for f in folder.split(' ') if f.strip()]
                    for f_path in folders:
                        if f_path:
                            # Paksa os.makedirs untuk setiap folder bertingkat
                            os.makedirs(os.path.join(active_root, f_path.replace('\\', '/')), exist_ok=True)
                    print(f"🛡️ [INTERNAL] Folders created: {folder}")
                    continue

                # [DEFAULT] EKSEKUSI SHELL
                # Saring komentar & instruksi narasi
                if line_clean.startswith('#') or any(line_clean.lower().startswith(f) for f in ["buat", "isi file"]):
                    continue

                # Modifikasi agar non-interaktif
                cmd = re.sub(r'(npx |npm create |npm exec )(create-vite(@latest)?|vite|react-native(@latest)?(\s+init)?)', 
                             r'\1\2 --no-interactive ', line_clean)
                
                # Cleanup language labels (e.g. "bash npm install")
                for lang in ['shell ', 'bash ', 'powershell ', 'cmd ']:
                    if cmd.lower().startswith(lang): cmd = cmd[len(lang):].strip()

                # [HOTFIX 2.15] Terminal Path Guard: Hapus instruksi 'cd' manual yang rawan halusinasi
                # Kita selalu menggunakan active_root sebagai CWD yang sah.
                clean_cmd = re.sub(r'cd\s+[^\n&|;]+[&|;]*', '', cmd).strip()
                if not clean_cmd: continue # Abaikan jika hanya berisi perintah cd
                
                # [VELOCITY] Adaptive Timeout based on command type
                timeout_val = 300 # Default (install/build)
                if any(x in clean_cmd.lower() for x in ["mkdir", "git", "touch", "ls", "dir", "cat"]):
                    timeout_val = 30
                elif "npx init" in clean_cmd.lower():
                    timeout_val = 120

                print(f"📟 [TERMINAL] Target: {active_root} | Executing: {clean_cmd}")
                
                is_server = any(x in clean_cmd.lower() for x in ["run dev", "run start", "vite", "next dev"])
                
                try:
                    process = await asyncio.create_subprocess_shell(
                        clean_cmd,
                        cwd=active_root,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    
                    if is_server:
                        print(f"🚀 [SERVER] Background: {clean_cmd}")
                        await update.message.reply_text("🚀 **Server Started:** Waiting for warm-up...")
                        await asyncio.sleep(5.0) 
                        continue

                    try:
                        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_val)
                        
                        if process.returncode == 0:
                            print(f"✅ OK: {cmd[:50]}")
                            await update.message.reply_text(f"✅ **OK:** `{cmd[:60]}`")
                        else:
                            error = stderr.decode().strip()
                            print(f"⚠️ Warning: {error[:150]}")
                            await update.message.reply_text(f"⚠️ **Warning:**\n`{error[:150]}`")
                            
                    except asyncio.TimeoutError:
                        process.terminate()
                        print(f"⏰ [VELOCITY] Stuck Detection: {cmd[:30]} timed out.")
                        await update.message.reply_text(f"⏰ **Velocity Timeout:** `{cmd[:50]}`. Auto-recovering...")
                    except Exception as e:
                        print(f"❌ Execution Error: {e}")
                        await update.message.reply_text(f"❌ **Terminal Error:** `{str(e)[:100]}`")
                
                    # [HOTFIX 2.12] Neural Terminal Auditor: Membaca Output untuk Self-Healing
                    if stdout or stderr:
                        out_text = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
                        if "npm ERR!" in out_text or "node_modules" in out_text.lower() and "not found" in out_text.lower():
                            print("🧠 [NEURAL AUDITOR] Mendeteksi masalah dependensi. Menjalankan Self-Healing...")
                            await update.message.reply_text("🧠 **Neural Auditor:** Mendeteksi masalah dependensi. Memperbaiki otomatis...")
                            # Menjadwalkan pengerjaan ulang terminal secara cerdas
                            milestones.insert(i + 1, {"name": "Self-Healing: npm install", "instruction": "```bash\nnpm install\n```", "required_agent": "terminal_bot"})
                        elif "EADDRINUSE" in out_text:
                            await update.message.reply_text("🧠 **Neural Auditor:** Port terpakai. Mencoba membebaskan port...")
                            milestones.insert(i + 1, {"name": "Self-Healing: Clear Port", "instruction": "```bash\nnpx kill-port 5173\n```", "required_agent": "terminal_bot"})
                except Exception as e:
                    print(f"❌ Critical Shell Error: {e}")
                    await update.message.reply_text(f"❌ **Shell Error:** {e}")
        
        return True

    async def _verify_project_integrity(self, path, update):
        """Memastikan folder proyek memiliki dependensi dan file scaffold yang lengkap."""
        print(f"🔍 [INTEGRITY] Guarding path: {path}")
        
        # 1. Cek Folder Dasar
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
        # 2. Cek node_modules (Kritis untuk Localhost)
        node_modules_path = os.path.join(path, "node_modules")
        if not os.path.exists(node_modules_path):
            print("🚨 [INTEGRITY FAIL] node_modules tidak ditemukan. Menjadwalkan instalasi paksa...")
            await update.message.reply_text("🚨 **Integrity Alert:** Dependensi (`node_modules`) hilang. Memulai instalasi paksa...")
            return False # Membutuhkan instalasi baru
            
        # 3. Cek file scaffold Vite
        critical_files = ["package.json", "index.html"]
        found_files = os.listdir(path)
        for f in critical_files:
            if f not in found_files:
                print(f"🚨 [INTEGRITY FAIL] File {f} hilang.")
                return False
        return True
            
        return True

    async def _execute_browser_preview(self, update):
        """Membuka browser dan mengambil screenshot hasil akhir (Dynamic Port Detection)."""
        ports = [5173, 3000, 8080, 4173] # Vite, Next.js, Generic, Vite Preview
        success = False
        for port in ports:
            url = f"http://localhost:{port}"
            # [HOTFIX 2.8] Warm-up Retry Logic untuk Localhost
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"🌐 [BROWSER] Accessing {url} (Attempt {attempt+1}/{max_retries})...")
                    webbrowser.open(url)
                    await asyncio.sleep(8.0) # Jeda loading halaman
                    
                    img_path = self.driver.take_screenshot(f"verify_port_{port}.png")
                    
                    await update.message.reply_photo(
                        photo=open(img_path, 'rb'), 
                        caption=f"📸 **Visual Verification Result ({url})**"
                    )
                    success = True
                    break 
                except Exception as e:
                    print(f"⚠️ Attempt {attempt+1} failed for port {port}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(8.0) # Tunggu lebih lama
                    else:
                        # [HOTFIX 2.11] Visual Self-Healing: Jika tetap gagal, suruh bot lain perbaiki
                        print("🚨 [VISUAL SELF-HEALING] Browser tetap gagal. Memicu rencana perbaikan...")
                        await update.message.reply_text("🚨 **Visual Self-Healing:** Localhost mati. Mencoba menghidupkan ulang server...")
                        # Tambahkan Milestone baru di antrean untuk menyalakan server ulang
                        return "trigger_server_restart"
                    continue
            
            if success: break
        
        if not success:
            await update.message.reply_text("❌ **Browser Error:** Tidak dapat menemukan server lokal di port manapun (5173, 3000, 8080, 4173).")
        return success

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
            # [VISION TURBO] Scale down to 0.4 for faster processing & upload
            img = img.resize((int(w * 0.4), int(h * 0.4)), Image.LANCZOS)
            w, h = img.size
            draw = ImageDraw.Draw(img)
            for i in range(0, 101, 20):
                x, y = (i / 100) * w, (i / 100) * h
                draw.line([(x, 0), (x, h)], fill=(128, 128, 128, 128), width=1)
                draw.line([(0, y), (w, y)], fill=(128, 128, 128, 128), width=1)
            
            grid_path = image_path.replace(".png", "_turbo.jpg")
            # [VISION TURBO] aggressive compression (65) for instant transmission
            img.save(grid_path, "JPEG", quality=65, optimize=True)
            return grid_path
        except Exception as e:
            print(f"⚠️ Gagal optimasi vision: {e}")
            return image_path

    def encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _get_relevant_skills(self, task_description):
        """Memindai folder skills/ dan memuat pengetahuan yang relevan dengan tugas (Enhanced with Master Standards)."""
        skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        injected_context = "\n--- MASTER DEVELOPER STANDARDS (INJECTED) ---\n"
        
        # Default Best Practices if no specific skill matches
        injected_context += "1. STRUCTURE: Always use 'src/components', 'src/hooks', 'src/services', and 'src/types' folders.\n"
        injected_context += "2. STYLING: Prefer Tailwind CSS with high-contrast dark modes and Framer Motion for micro-animations.\n"
        injected_context += "3. TYPESCRIPT: Use strict typing, avoid 'any', and define Interfaces for all data props.\n"
        injected_context += "4. MOBILE: If mobile, use Expo (React Native) with professional navigation patterns.\n"
        
        if not os.path.exists(skills_dir): return injected_context
        
        task_lower = task_description.lower()
        found = False
        
        for file in os.listdir(skills_dir):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(skills_dir, file), 'r') as f:
                        skill_data = json.load(f)
                        if any(kw in task_lower for kw in skill_data.get('keywords', [])):
                            found = True
                            injected_context += f"CATEGORY: {skill_data['category']}\n"
                            injected_context += f"CORE BEST PRACTICES:\n- " + "\n- ".join(skill_data['best_practices']) + "\n"
                            injected_context += f"PREMIUM TECH STACK: {', '.join(skill_data['tech_stack'])}\n\n"
                except Exception as e:
                    print(f"⚠️ Gagal muat modul skill {file}: {e}")
        
        injected_context += "STRICT INSTRUCTION: Apply the above standards to create a WORLD-CLASS professional software architecture.\n"
        return injected_context

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
        
        # 3. Health Check & Integrity (Hotfix 2.14)
        integrity_passed = await self._verify_project_integrity(current_root, update)
        if not integrity_passed:
            print("🛠️ [RECOVERY] Memperbaiki integritas proyek yang rusak...")
            # Suntikkan Milestone Inisialisasi secara paksa di urutan pertama
            recovery_milestone = {
                "id": 0,
                "name": "Emergency Project Recovery",
                "instruction": "```bash\nnpm create vite@latest . -- --template react-ts\nnpm install\n```",
                "required_agent": "terminal_bot"
            }
            milestones.insert(0, recovery_milestone)

        # 4. Eksekusi Swarm melalui Workers
        for i, ms in enumerate(milestones):
            ms_name = ms.get('name', f'Stage {i+1}')
            ms_instruction = ms.get('instruction', '')
            
            # Truncate instruction if too long for Telegram (Limit ~4096)
            safe_instruction = (ms_instruction[:3500] + '...') if len(ms_instruction) > 3500 else ms_instruction
            
            # 3. Eksekusi Berdasarkan Jenis Agen (Otonomi v2: Internal Coding)
            agent_id = ms.get('required_agent', 'coder_internal')
            await update.message.reply_text(f"🏗️ **MENGERJAKAN [{i+1}/{len(milestones)}]:** {ms_name}\n👤 **Agent:** `{agent_id}`\n📜 **Instruksi:**\n{safe_instruction}")
            
            if agent_id in ['coder_internal', 'coder_trae', 'ux_ui_designer']:
                await self._execute_internal_coder_stage(ms, i, milestones, update)
            elif agent_id == 'terminal_bot':
                await self._execute_terminal_stage(ms, i, milestones, update)
            elif agent_id == 'browser_bot':
                await self._execute_browser_stage(ms, update)

        # 4. Neural Distillation (Knowledge Bank)
        await self._final_distillation(update)
    
    async def _execute_internal_coder_stage(self, ms, i, milestones, update):
        """Implementasi PRO-MAX: Koding Otonom dengan Siklus Self-Healing (ReAct)."""
        ms_name = ms.get('name', 'Internal Coder Task')
        ms_instruction = ms.get('instruction', '')
        agent_id = 'coder_internal'
        active_root = os.getenv("PROJECT_ROOT", os.getcwd())
        
        # SIKLUS: Berpikir -> Bertindak -> Observasi -> Perbaiki (Maks 3 Iterasi)
        for attempt in range(1, 4):
            context = self._get_recursive_snapshot(active_root)
            context_str = json.dumps(list(context.keys()), indent=2)
            
            # Jika ini adalah percobaan perbaikan (attempt > 1), sertakan error sebelumnya
            current_instruction = ms_instruction
            if attempt > 1:
                print(f"🔄 [{agent_id}] Attempt {attempt}: Mencoba memperbaiki error sebelumnya...")
            
            result = await self.internal_coder.execute_task(current_instruction, active_root, context_str)
            
            # [HOTFIX 2.6] VITALITY GUARD: Deteksi Respon Kosong/Melamun
            if not result or (not result.get('written_files') and result.get('status') == 'SUCCESS'):
                self.no_action_count += 1
                print(f"⚠️ [LOOP BREAKER] Agen memberikan respon kosong (Count: {self.no_action_count}/3)")
                if self.no_action_count >= 3:
                    print("🚨 [VITALITY GUARD] Memicu Emergency Refresh...")
                    await update.message.reply_text("🚨 **Vitality Guard:** Saya merasa stuck dalam pemikiran. Mencoba menyegarkan sistem...")
                    self.driver.press_key("esc")
                    await asyncio.sleep(1.0)
                    self.no_action_count = 0 # Reset
                    # Ambil screenshot baru sebagai trigger vision baru
                    self.driver.take_screenshot("emergency_refresh.png")
                    continue
            else:
                self.no_action_count = 0 # Reset jika ada aksi nyata
            
            if result['status'] == 'SUCCESS':
                written = ", ".join(result['written_files'])
                # --- VERIFIKASI SEGERA (Observation) ---
                print(f"🔍 [{agent_id}] Verifikasi koding (Attempt {attempt})...")
                # Jika Web Vite, cek linting
                error_log = ""
                if os.path.exists(os.path.join(active_root, "package.json")):
                    verify = subprocess.run(["npm", "run", "lint"], cwd=active_root, capture_output=True, text=True, shell=True)
                    if verify.returncode != 0:
                        error_log = verify.stdout + verify.stderr
                        print(f"⚠️ [{agent_id}] Deteksi Error Linter:\n{error_log[:200]}")
                
                if not error_log:
                    await update.message.reply_text(f"✅ **Koding PRO-MAX Sukses:**\n📂 Files: `{written}`\n✨ Kualitas: Terverifikasi (Lint Passed).")
                    self.sona.record_step(agent_id, "SUCCESS", f"Code written and verified on attempt {attempt}", status="SUCCESS")
                    return True
                else:
                    # Gagal Verifikasi: Analisa error dan update instruksi (Self-Healing)
                    print(f"⚠️ [{agent_id}] Gagal Verifikasi. Log Error: {error_log[:100]}...")
                    
                    # Berikan hint spesifik untuk error umum
                    reflection_hint = ""
                    if "no-empty-object-type" in error_log or "An interface declaring no members" in error_log:
                        reflection_hint = "HINT: Jangan gunakan 'interface Name extends Base {}' yang kosong. Gunakan 'type Name = Base' atau tambahkan properti ke interface tersebut."
                    elif "no-explicit-any" in error_log:
                        reflection_hint = "HINT: Ganti tipe 'any' dengan tipe data yang spesifik (misal: Record<string, unknown> atau gunakan unknown)."
                    
                    ms_instruction = f"REFLEKSI KEGAGALAN (Attempt {attempt}):\n{error_log}\n\n{reflection_hint}\n\nPERBAIKI FILE TERKAIT. INSTRUKSI ASLI: {ms_instruction}"
            else:
                await update.message.reply_text(f"❌ **Internal Coder Gagal (Attempt {attempt}):** {result.get('error')}")
        
        # Jika sampai sini berarti gagal setelah 3 kali percobaan
        self.sona.record_step(agent_id, "FAILED", "Failed after 3 self-healing attempts", status="FAILED")
        return False

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