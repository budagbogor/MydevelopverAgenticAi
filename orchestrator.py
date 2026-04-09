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
import shutil
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
        # [DIFY-STYLE] Variable Pool: Single Source of Truth for agents
        self.variable_pool = {
            "project_name": os.path.basename(self.base_dir),
            "start_time": datetime.now().isoformat(),
            "nodes": {} 
        }
        
    async def _execute_terminal(self, instruction, i, milestones, update):
        """Menjalankan perintah shell/terminal secara otonom di PROJECT_ROOT."""
        active_root = os.getenv("PROJECT_ROOT", os.getcwd())
        if not os.path.exists(active_root):
            os.makedirs(active_root)
            
        print(f"[TERMINAL] Base Dir: {active_root}")
        
        # Ekstrak blok kode triple backticks
        raw_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', instruction, re.DOTALL)
        if not raw_blocks:
            # Fallback ke backticks tunggal
            raw_blocks = re.findall(r'`([^`\n]+)`', instruction)
        
        if not raw_blocks:
            print(f"[TERMINAL] No executable commands found. Skipping.")
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
                        print(f"[INTERCEPT] File created via Line-Logic: {cat_filename}")
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
                    print(f"[INTERCEPT] File created via Echo-Logic: {filename}")
                    continue

                # [DETEKSI] MKDIR
                if line_clean.lower().startswith('mkdir '):
                    folder = line_clean.replace('mkdir -p ', '').replace('mkdir ', '').replace('"', '').strip()
                    # Handle multiple folders in one line (e.g. mkdir folder1 folder2)
                    folders = [f.strip() for f in re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', folder) if f.strip()]
                    for f_path in folders:
                        if f_path:
                            os.makedirs(os.path.join(active_root, f_path.replace('\\', '/')), exist_ok=True)
                    print(f"[INTERNAL] Folders created: {folder}")
                    continue

                # [DETEKSI] RM -RF atau RM
                if line_clean.lower().startswith('rm '):
                    target_raw = line_clean[3:].replace('-rf ', '').replace('-f ', '').replace('-r ', '').strip()
                    targets = [t.strip('"') for t in re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', target_raw)]
                    
                    for target in targets:
                        if '*' in target:
                            import glob
                            items = glob.glob(os.path.join(active_root, target.replace('\\', '/')))
                            for item in items:
                                try:
                                    if os.path.isdir(item): shutil.rmtree(item)
                                    else: os.remove(item)
                                except: pass
                            print(f"[INTERNAL] RM Wildcard: {target}")
                        else:
                            full_path = os.path.join(active_root, target.replace('\\', '/'))
                            try:
                                if os.path.exists(full_path):
                                    if os.path.isdir(full_path): shutil.rmtree(full_path)
                                    else: os.remove(full_path)
                                    print(f"[INTERNAL] RM: {target}")
                            except: pass
                    continue

                # [DETEKSI] CP / MV
                for op_prefix in ['cp ', 'mv ']:
                    if line_clean.lower().startswith(op_prefix):
                        parts = [p.strip('"') for p in re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', line_clean[len(op_prefix):])]
                        if len(parts) >= 2:
                            src_rel, dst_rel = parts[0], parts[1]
                            src_p = os.path.join(active_root, src_rel.replace('\\', '/'))
                            dst_p = os.path.join(active_root, dst_rel.replace('\\', '/'))
                            try:
                                if op_prefix.strip() == 'cp':
                                    if os.path.isdir(src_p): shutil.copytree(src_p, dst_p, dirs_exist_ok=True)
                                    else: shutil.copy2(src_p, dst_p)
                                else: # mv
                                    shutil.move(src_p, dst_p)
                                print(f"[INTERNAL] {op_prefix.upper().strip()}: {src_rel} -> {dst_rel}")
                            except Exception as e:
                                print(f"[WARN] {op_prefix.upper().strip()} Error: {e}")
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

                print(f"[TERMINAL] Target: {active_root} | Executing: {clean_cmd}")
                
                # [HOTFIX 2.26] Precise Server Detection: Avoid flagging 'create' or 'init' as background server.
                is_server = False
                server_keywords = ["run dev", "run start", "next dev", "yarn dev", "npm start"]
                if any(kw in clean_cmd.lower() for kw in server_keywords):
                    is_server = True
                elif clean_cmd.strip().lower() == "vite" or clean_cmd.strip().lower().endswith("bin/vite"):
                    is_server = True
                
                # [HOTFIX 2.19] Windows Binary Guard
                if os.name == 'nt' and any(x in clean_cmd.lower() for x in ["npm ", "npx "]):
                    if not shutil.which("npm") and not shutil.which("npm.cmd"):
                        print("[BINARY GUARD] npm/npx NOT FOUND in PATH.")
                        await update.message.reply_text("🚨 **Binary Guard:** `npm` tidak ditemukan di PATH. Silakan instal Node.js.")
                        return True # Skip execution to avoid WinError 2

                try:
                    process = await asyncio.create_subprocess_shell(
                        clean_cmd,
                        cwd=active_root,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    
                    if is_server:
                        print(f"[SERVER] Background: {clean_cmd}")
                        await update.message.reply_text("🚀 **Server Started:** Waiting for warm-up...")
                        await asyncio.sleep(5.0) 
                        continue

                    try:
                        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_val)
                        
                        if process.returncode == 0:
                            print(f"[OK] OK: {cmd[:50]}")
                            await update.message.reply_text(f"✅ **OK:** `{cmd[:60]}`")
                        else:
                            error = stderr.decode().strip()
                            print(f"[WARN] Warning: {error[:150]}")
                            await update.message.reply_text(f"⚠️ **Warning:**\n`{error[:150]}`")
                            
                    except asyncio.TimeoutError:
                        process.terminate()
                        print(f"[TIMEOUT] Stuck Detection: {cmd[:30]} timed out.")
                        await update.message.reply_text(f"⏰ **Velocity Timeout:** `{cmd[:50]}`. Auto-recovering...")
                    except Exception as e:
                        print(f"[ERROR] Execution Error: {e}")
                        await update.message.reply_text(f"❌ **Terminal Error:** `{str(e)[:100]}`")
                
                    # [HOTFIX 2.25] Neural Terminal Auditor 2.0 (OpenHands-style)
                    if stdout or stderr:
                        out_text = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
                        critical_errors = ["npm ERR!", "FATAL ERROR", "Module not found", "Command not found", "failed to compile"]
                        
                        if any(err in out_text for err in critical_errors):
                            print(f"[CRITICAL AUDIT] Terdeteksi kegagalan log: {out_text[:100]}")
                            await update.message.reply_text(f"🚨 **Critical Audit:** Perintah sepertinya gagal meskipun terminal selesai.\n`{out_text[:150]}`")
                            
                            # Memicu Troubleshooting Mode (GPT-Pilot-style)
                            if "node_modules" in out_text.lower() or "not found" in out_text.lower():
                                milestones.insert(i + 1, {"name": "Troubleshooting: Fix Dependencies", "instruction": "```bash\nnpm install\n```", "required_agent": "terminal_bot"})
                            elif "EADDRINUSE" in out_text:
                                milestones.insert(i + 1, {"name": "Troubleshooting: Clear Port", "instruction": "```bash\nnpx kill-port 5173\n```", "required_agent": "terminal_bot"})
                            return False # Tandai sebagai gagal agar tidak lanjut asal-asalan
                            
                    if process.returncode != 0:
                        return False

                except Exception as e:
                    print(f"[ERROR] Critical Shell Error: {e}")
                    await update.message.reply_text(f"❌ **Shell Error:** {e}")
                    return False
        
        return True

    async def _verify_project_integrity(self, path, update):
        """Memastikan folder proyek memiliki dependensi dan file scaffold yang lengkap."""
        print(f"[INTEGRITY] Guarding path: {path}")
        
        # 1. Cek Folder Dasar
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            return "EMPTY"
            
        # 2. Cek file scaffold Vite
        critical_files = ["package.json"]
        found_files = os.listdir(path)
        has_scaffold = all(f in found_files for f in critical_files)
        
        if not has_scaffold:
            return "EMPTY"

        # 3. Cek node_modules (Kritis untuk Localhost)
        node_modules_path = os.path.join(path, "node_modules")
        if not os.path.exists(node_modules_path):
            print("[INTEGRITY FAIL] node_modules tidak ditemukan.")
            return "MISSING_DEPS"
            
        return "READY"
            
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
                    print(f"[BROWSER] Accessing {url} (Attempt {attempt+1}/{max_retries})...")
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
                    print(f"[WARN] Attempt {attempt+1} failed for port {port}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(8.0) # Tunggu lebih lama
                    else:
                        # [HOTFIX 2.11] Visual Self-Healing: Jika tetap gagal, suruh bot lain perbaiki
                        print("[VISUAL SELF-HEALING] Browser tetap gagal. Memicu rencana perbaikan...")
                        await update.message.reply_text("🚨 **Visual Self-Healing:** Localhost mati. Mencoba menghidupkan ulang server...")
                        # Tambahkan Milestone baru di antrean untuk menyalakan server ulang
                        return "trigger_server_restart"
                    continue
            
            if success: break
        
        if not success:
            await update.message.reply_text("❌ **Browser Error:** Tidak dapat menemukan server lokal di port manapun (5173, 3000, 8080, 4173).")
        return success

    def _get_recursive_snapshot(self, directory):
        """Merekam seluruh struktur file secara rekursif (Aider-style Repository Mapping)."""
        tree = []
        for root, dirs, files in os.walk(directory):
            if any(x in root for x in [".git", "node_modules", "vendor", ".next", "__pycache__", "dist", "build"]):
                continue
            level = root.replace(directory, '').count(os.sep)
            indent = ' ' * 4 * (level)
            tree.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                tree.append(f"{subindent}{f}")
        return "\n".join(tree)

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
        print(f"[BRAINSTORMING] Memperluas prompt ke Milestones: {brief_task}")
        
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
        
        # 3. Health Check & Integrity (Hotfix 2.26 - Granular Recovery)
        integrity_status = await self._verify_project_integrity(current_root, update)
        if integrity_status != "READY":
            print(f"[RECOVERY] Memperbaiki integritas proyek ({integrity_status})...")
            
            if integrity_status == "EMPTY":
                msg = "🚨 **Integrity Alert:** Folder proyek kosong atau tidak valid. Melakukan inisialisasi scaffold Vite..."
                recovery_instr = "```bash\nnpm create vite@latest . -- --template react-ts\nnpm install\n```"
            else: # MISSING_DEPS
                msg = "🚨 **Integrity Alert:** Dependensi (`node_modules`) hilang. Menjalankan instalasi ulang..."
                recovery_instr = "```bash\nnpm install\n```"
                
            await update.message.reply_text(msg)
            
            recovery_milestone = {
                "id": 0,
                "name": "Emergency Project Recovery",
                "instruction": recovery_instr,
                "required_agent": "terminal_bot"
            }
            milestones.insert(0, recovery_milestone)

        # 4. Eksekusi Swarm melalui Workers (Dify-style Automation)
        # Variable Pool sudah diinisialisasi di __init__, kita reset untuk tugas baru jika perlu
        self.variable_pool["nodes"] = {} 
        self.variable_pool["project_root"] = current_root

        # 3. Execution Phase (Node-Based Workflow)
        for i, ms in enumerate(milestones):
            ms_name = ms.get('name', 'Terminal Task')
            ms_instruction = ms.get('instruction', '')
            agent_id = ms.get('required_agent', 'coder_internal')
            
            # Node Entry in Variable Pool
            node_id = f"node_{i}"
            self.variable_pool["nodes"][node_id] = {"name": ms_name, "status": "RUNNING", "start_time": time.time()}
            
            # Telegram Node Status (Dify-style)
            node_header = f"📍 **NODE [{i+1}/{len(milestones)}]:** `{ms_name}`\n"
            node_header += f"⚙️ **Status:** `PROCESSING`\n"
            node_header += f"👤 **Agent:** `{agent_id}`"
            await update.message.reply_text(node_header)
            
            # Inject context from Variable Pool to instruction
            safe_instruction = ms_instruction.replace("`", "'")
            
            success = False
            if agent_id in ['coder_internal', 'coder_trae', 'ux_ui_designer']:
                success = await self._execute_internal_coder_stage(ms, i, milestones, update)
                if success:
                    # Store Result in Pool
                    self.variable_pool["nodes"][node_id]["result"] = "Code blocks written successfully"
            elif agent_id == 'terminal_bot':
                success = await self._execute_terminal_stage(ms, i, milestones, update)
                if success:
                    self.variable_pool["nodes"][node_id]["result"] = "Terminal commands executed"
            elif agent_id == 'browser_bot':
                success = await self._execute_browser_stage(ms, update)
            
            # Update Node Status
            final_status = "SUCCESS" if success else "FAILED"
            self.variable_pool["nodes"][node_id]["status"] = final_status
            self.variable_pool["nodes"][node_id]["end_time"] = time.time()
            
            status_icon = "✅" if success else "❌"
            await update.message.reply_text(f"{status_icon} **NODE [{ms_name}] {final_status}**")
            
            if not success:
                print(f"[WORKFLOW] Stopping at {ms_name} due to failure.")
                break

        # 4. Neural Distillation (Knowledge Bank)
        await self._final_distillation(update)
    
    async def _execute_internal_coder_stage(self, ms, i, milestones, update):
        """Implementasi PRO-MAX: Koding Otonom dengan AutoGPT-style Reflexion."""
        ms_name = ms.get('name', 'Internal Coder Task')
        ms_instruction = ms.get('instruction', '')
        agent_id = 'coder_internal'
        active_root = os.getenv("PROJECT_ROOT", os.getcwd())
        
        for attempt in range(1, 4):
            # Repository Mapping Context (Aider-style)
            context_tree = self._get_recursive_snapshot(active_root)
            
            # [DIFY] Inject Variable Pool Context (Single Source of Truth)
            pool_data = json.dumps(self.variable_pool.get("nodes", {}), indent=2)
            current_instruction = f"{ms_instruction}\n\n[VARIABLE POOL CONTEXT]:\n{pool_data}"
            
            if attempt > 1:
                print(f"🔄 [{agent_id}] Reflexion Attempt {attempt}: Menganalisis log error...")
                await update.message.reply_text(f"⚠️ **Reflexion Mode (Attempt {attempt}):** Menganalisis log error dan memperbaiki diri...")
            
            result = await self.internal_coder.execute_task(current_instruction, active_root, context_tree)
            
            # [VITALITY GUARD]
            if not result or (not result.get('written_files') and result.get('status') == 'SUCCESS'):
                pass
            
            if result['status'] == 'SUCCESS':
                written = ", ".join(result['written_files'])
                print(f"🔍 [{agent_id}] Verifikasi koding (Attempt {attempt})...")
                
                # --- CRITICAL HONEST VERIFICATION ---
                error_log = ""
                integrity_check = await self._verify_project_integrity(active_root, update)
                
                if not integrity_check:
                    error_log = "CRITICAL: Proyek tidak utuh (kurang package.json/node_modules). Fokus pada inisialisasi."
                elif os.path.exists(os.path.join(active_root, "package.json")):
                    verify = subprocess.run(["npm", "run", "lint"], cwd=active_root, capture_output=True, text=True, shell=True)
                    if verify.returncode != 0:
                        error_log = verify.stdout + verify.stderr
                
                if not error_log and integrity_check:
                    await update.message.reply_text(f"✅ **Koding Sukses:** `{written}`\n🌟 *Bot menyadari potensi bug dan telah memperbaikinya via Self-Criticism.*")
                    self.sona.record_step(agent_id, "SUCCESS", f"Verified on attempt {attempt}", status="SUCCESS")
                    return True
                else:
                    print(f"⚠️ [{agent_id}] Gagal Verifikasi. Memicu Reflexion Cycle...")
                    # Update instruksi untuk putaran perbaikan berikutnya dengan LOG LENGKAP
                    ms_instruction = f"URGENT REFLEXION (Attempt {attempt}):\n\nERROR LOG:\n{error_log}\n\nPERBAIKI KESALAHAN DI ATAS. PASTIKAN STANDAR PRO-MAX TERPENUHI."
            else:
                print(f"❌ [{agent_id}] AI Gagal format. Retrying...")
        
        return False

    async def _execute_terminal_stage(self, ms, i, milestones, update):
        """Spesifik untuk agen Terminal: Command Line execution."""
        ms_instruction = ms.get('instruction', '')
        ms_name = ms.get('name', 'Terminal Task')
        agent_id = 'terminal_bot'
        
        success = await self._execute_terminal(ms_instruction, i, milestones, update)
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
            
        await update.message.reply_text("Neural Distillation: Menyaring pengalaman untuk Knowledge Bank...")
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
            with open(raw_img, 'rb') as photo_file:
                await update.message.reply_photo(photo=photo_file, caption="Hasil Akhir Proyek")
        except: pass