import json
import yaml
import os
import asyncio
from openai import OpenAI
from config import SUMOPOD_API_KEY, SUMOPOD_BASE_URL, DEFAULT_MODEL
from neural.sona import SonaMemory
from neural.bank import ReasoningBank

class QueenCoordinator:
    """
    Queen Coordinator (The Swarm Brain)
    Ref: RuFlo v3 Philosophy
    Decomposes tasks, delegates to workers, and gathers consensus.
    """
    def __init__(self, specs_path="agents/specs.yaml"):
        self.specs = self._load_specs(specs_path)
        self.sona = SonaMemory()
        self.bank = ReasoningBank()
        self.client = OpenAI(api_key=SUMOPOD_API_KEY, base_url=SUMOPOD_BASE_URL)
        self.workers = {} # Will hold references to worker specialized classes

    def _load_specs(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)['agents']
        return []

    async def decompose_task(self, user_task):
        """
        Pecah tugas menjadi Milestone strategis (Design -> Implement -> Test).
        """
        print(f"[QUEEN] Decomposing mission: {user_task}")
        
        # Cari pengetahuan relevan dari bank dengan Reranking (Dify-style)
        relevant_knowledge = await self.bank.get_relevant_knowledge(user_task)
        knowledge_context = json.dumps(relevant_knowledge, indent=2) if relevant_knowledge else "None"

        prompt = f"""
        Tugas Anda sebagai Swarm Queen (Project Manager).
        Pecah instruksi pengguna berikut menjadi Milestones teknis yang sangat spesifik.
        Gunakan pengetahuan strategis berikut jika relevan:
        {knowledge_context}

        INSTRUKSI PENGGUNA: "{user_task}"
        
        WAJIB: Setiap Masterplan HARUS mencakup tahapan berikut (dalam urutan logis):
        1. "terminal_bot": Inisialisasi Proyek (Web: Vite; Mobile: `npx react-native@latest init` atau `flutter create .`).
        2. "terminal_bot": Clean Slate (Hapus file default: `rm -rf src/*` di Web atau bersihkan boilerplate di Mobile).
        3. "devops_quality": Arsitektur Folder (PRO-MAX Standard: `src/components`, `src/hooks`, `src/services`, `src/types`, `src/theme`).
        4. "ux_ui_designer": Design System (Gunakan Standar PREMIUM: Material 3, Tamagui, atau shadcn/ui).
        5. "coder_internal": Implementasi Kode Utama (Gunakan Standar PRO-MAX dari neural knowledge).
        6. "terminal_bot": Quality Check & Build.
        7. "terminal_bot": Start Server / Emulator.
        8. "browser_bot" atau "vision_bot": Visual Verification.

        PENTING: Jika "required_agent" adalah "terminal_bot", properti "instruction" di bawah ini HANYA boleh berisi blok kode triple backticks dengan perintah shell. DILARANG KERAS menambahkan narasi atau penjelasan manusia di luar blok kode tersebut dalam field "instruction".

        FORMAT KELUARAN (Wajib JSON):
        {{
            "strategy": "Penjelasan singkat strategi harian/misi.",
            "milestones": [
                {{
                    "id": 1,
                    "name": "Nama Milestone",
                    "instruction": "Pastikan setiap Milestone memiliki daftar instruksi yang JELAS untuk agen koding (internal_coder) atau agen terminal (terminal_bot). ATURAN KRITIS WINDOWS: 1. DILARANG menggunakan terminal_bot untuk menulis konten file (seperti echo > atau cat <<EOF). Setiap pembuatan atau modifikasi konten file WAJIB dilakukan oleh internal_coder. 2. terminal_bot hanya digunakan untuk: npm install, npx init, git, dan manajemen proses. 3. Hapus semua file boilerplate (Clean Slate) sebelum mulai koding profesional.",
                    "required_agent": "terminal_bot" | "coder_internal" | "browser_bot",
                    "is_critical": true
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL, # Use stable model from config
                messages=[
                    {"role": "system", "content": "You are the Queen Coordinator. Break down complex missions into precise milestones."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[WARN] Queen failed to decompose: {e}")
            # [HOTFIX 2.10] Rich Fallback: Pastikan instalasi & server selalu ada
            return {
                "strategy": "Recovery fallback (Complete Cycle)", 
                "milestones": [
                    {
                        "id": 1, 
                        "name": "Project Initialization", 
                        "instruction": "```bash\nnpm create vite@latest . -- --template react-ts\nnpm install\n```", 
                        "required_agent": "terminal_bot"
                    },
                    {
                        "id": 2, 
                        "name": "Main Execution", 
                        "instruction": user_task, 
                        "required_agent": "coder_internal"
                    },
                    {
                        "id": 3, 
                        "name": "Launch Server", 
                        "instruction": "```bash\nnpm run dev\n```", 
                        "required_agent": "terminal_bot"
                    },
                    {
                        "id": 4, 
                        "name": "Visual Check", 
                        "instruction": "Buka localhost:5173", 
                        "required_agent": "browser_bot"
                    }
                ]
            }

    async def orchestrate(self, user_task, update_callback=None):
        """
        Main loop for orchestration.
        """
        plan = await self.decompose_task(user_task)
        self.sona.start_trajectory(user_task)
        
        if update_callback:
            await update_callback(f"[STRATEGY] Queen Strategy:\n{plan['strategy']}\n\n[TARGET] Target: {len(plan['milestones'])} Milestones.")

        final_results = []
        for ms in plan['milestones']:
            if update_callback:
                await update_callback(f"[STEP] MENGERJAKAN Milestone {ms['id']}: {ms['name']}")
            
            # 1. Pilih Worker (untuk saat ini kita hanya punya Trae Worker)
            # Logika seleksi agen bisa lebih kompleks di masa depan
            agent_id = ms.get('required_agent', 'coder_internal')
            
            # 2. Eksekusi melalui worker (akan diimplementasikan di worker_trae.py)
            # Placeholder for worker execution
            print(f"[QUEEN] Delegating '{ms['name']}' to {agent_id}...")
            
            # --- Simulasi Step untuk SONA ---
            self.sona.record_step(
                agent_id=agent_id,
                action=f"Execute Milestone: {ms['name']}",
                observation="Awaiting implementation of WorkerTrae",
                thought=ms['instruction']
            )
            
            final_results.append(ms)

        self.sona.end_trajectory("SUCCESS", "Plan executed (Simulated)")
        return final_results
