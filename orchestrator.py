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
            img = Image.open(image_path)
            
            # --- TOKEN SAVER OPTIMIZED for Trae ---
            w, h = img.size
            img = img.resize((int(w * 0.8), int(h * 0.8)), Image.LANCZOS)
            w, h = img.size

            draw = ImageDraw.Draw(img)
            for i in range(0, 101, 10):
                x, y = (i / 100) * w, (i / 100) * h
                draw.line([(x, 0), (x, h)], fill=(128, 128, 128), width=1)
                draw.line([(0, y), (w, y)], fill=(128, 128, 128), width=1)
                draw.text((x + 2, 2), str(i), fill=(200, 200, 200))
                draw.text((2, y + 2), str(i), fill=(200, 200, 200))
            
            grid_path = image_path.replace(".png", "_optimized.png")
            img.save(grid_path, optimize=True, quality=80)
            return grid_path
        except Exception as e:
            print(f"⚠️ Gagal optimasi vision: {e}")
            return image_path

    def encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

    async def process_task(self, task_description, update):
        print(f"\n[🚀 MASTER PLAN ACTIVE] START: {task_description}")
        await update.message.reply_text(f"🏘️ **Senior Architect Engine Start**\nTarget: {task_description}")

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
                
                await asyncio.sleep(0.3) 
                raw_img = self.driver.take_screenshot()
                current_hash = self.get_image_hash(raw_img)
                is_stuck = current_hash == self.last_screenshot_hash
                self.last_screenshot_hash = current_hash
                
                if is_stuck: self.stuck_count += 1
                else: self.stuck_count = 0

                grid_img = self.draw_grid(raw_img)
                last_image_path = grid_img
                base64_img = self.encode_image(grid_img)

                # --- OBSERVASI: Cek jendela aktif ---
                active_win = self.driver.get_active_window()
                
                # --- LIGHTNING MEMORY RETRIEVAL ---
                learning_context = self.memory.get_formatted_for_prompt(active_win, task_description)

                prompt = f"""
                GOAL: {task_description}
                Step: {step + 1}/{max_steps}
                Status: {"STUCK" if is_stuck else "OK"}
                Active Window: "{active_win}"
                Project: {PROJECT_ROOT}
                
                {learning_context}

                MASTER_PLAN SAAT INI:
                {self.master_plan if self.master_plan else "Belum dibuat."}

                SEARCH_RESULTS (Riset Software/UI):
                {self.last_search_results if self.last_search_results else "Data riset kosong."}

                INSTRUKSI OPERATOR:
                - Jika Anda tidak tahu cara menggunakan software "{active_win}", lakukan SEARCH tutorial/shortcut keyboard-nya.
                - OBSERVASI: Pastikan layar memvalidasi langkah sebelumnya.
                - ANTI-HALUSINASI: Jangan menebak lokasi tombol. Gunakan HOTKEY jika tersedia.

                RESPON JSON (Wajib satu baris):
                {{
                    "status": "PROSES/SELESAI",
                    "critique": "Analisis satu baris tanpa Enter.",
                    "new_master_plan": "Update ringkas satu baris.",
                    "actions": [
                        {{ "type": "SEARCH/CLICK/TYPE/HOTKEY/ENTER/WAIT", "params": ["nilai"] }}
                    ]
                }}

                PENTING: JANGAN gunakan Enter/Newline di dalam JSON. Satu baris saja per field.

                TIPS KHUSUS TRAE IDE (SUPER FAST MODE):
                - TOMBOL 'KEEP' (Wajib): Jika tombol 'Keep' (hijau) muncul, SEGERA tekan HOTKEY ['ctrl', 'enter'].
                - NOTIFIKASI 'DELETE FILES': Jika melihat teks "Delete X files", cari tombol berwarna MERAH (Run/Confirm) di baris yang sama dan segera CLICK. 
                - NOTIFIKASI 'REVIEW FILES': Jika melihat banner "X files need review", segera CLICK ikon CHECK/KEEP.
                - Jika status STUCK terdeteksi saat tombol konfirmasi terlihat, langsung lakukan CLICK pada area tombol tersebut.
                """

                try:
                    sys_msg = """Anda adalah Universal Software Operator & Expert Learner kelas dunia. 
                    Anda memiliki LIGHTNING MEMORY yang menyimpan pengalaman masa lalu. Gunakan data tersebut untuk menghindari kesalahan yang sama."""

                    response = self.client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=[
                            {"role": "system", "content": sys_msg},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
                            ]}
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=3000
                    )
                    
                    raw_content = response.choices[0].message.content.strip()
                    print(f"--- [Step {step+1}] ARCHITECT RESPONSE ---")
                    
                    # --- SANITIZATION ---
                    cleaned_content = re.search(r'(\{.*\})', raw_content.replace('\n', ' '), re.DOTALL)
                    res = json.loads(cleaned_content.group(1)) if cleaned_content else {"status": "STUCK", "actions": []}
                    
                    if res.get('new_master_plan'):
                        self.master_plan = res['new_master_plan']

                    actions = res.get('actions', [])
                    current_status = res.get('status', 'PROSES')
                    
                    if current_status == "SELESAI":
                        await update.message.reply_text("✨ **Tugas Selesai dengan Kualitas Premium.**")
                        break

                    for action in actions:
                        a_type = action.get('type')
                        a_params = action.get('params', [])

                        if a_type == "SEARCH":
                            if self.search_count >= max_search_limit: continue
                            query = a_params[0].strip() if a_params else ""
                            await update.message.reply_text(f"🔍 **Riset Web Architect ({self.search_count+1}):** _{query}_", parse_mode='Markdown')
                            self.last_search_results = self.web_search.get_formatted_string(query)
                            self.search_count += 1
                            break 

                        if is_stuck and self.stuck_count >= 2:
                            print("🚨 Stuck terdeteksi, mencoba pemulihan cerdas...")
                            recovery_action = ["HOTKEY", ["ctrl", "enter"]] if "trae" in active_win.lower() else ["HOTKEY", ["esc"]]
                            self.driver.execute_action(recovery_action[0], recovery_action[1])
                            
                            # --- LIGHTNING LEARN REPORTING ---
                            # Simpan pengalaman sukses jika revovery berhasil (dianggap berhasil jika loop lanjut)
                            self.memory.save_experience(active_win, task_description, [action])
                            await update.message.reply_text(f"⚡ **LIGHTNING LEARN:** Memperoleh pengalaman baru menangani hambatan di jendela `{active_win}`. Strategi ini telah disimpan ke memori permanen.")
                            
                            await asyncio.sleep(0.5)
                            self.stuck_count = 0
                            break

                        if a_type:
                            print(f"🎬 Eksekusi Operator: {a_type} {a_params}")
                            self.driver.execute_action(a_type, a_params)
                            await asyncio.sleep(0.2)

                    await asyncio.sleep(0.2)

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    await update.message.reply_text(f"❌ Gangguan Loop: {str(e)}")
                    break

        except Exception as outer_e:
            import traceback
            traceback.print_exc()
            await update.message.reply_text(f"❌ Gangguan Fatal Operator: {str(outer_e)}")
        
        finally:
            if last_image_path and os.path.exists(last_image_path):
                try:
                    with open(last_image_path, 'rb') as photo:
                        await update.message.reply_photo(photo=photo, caption="🖼️ **Kondisi Layar Terakhir**")
                except Exception as img_err:
                    print(f"⚠️ Gagal mengirim screenshot terakhir: {img_err}")