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
        print(f"👑 [QUEEN] Decomposing mission: {user_task}")
        
        # Cari pengetahuan relevan dari bank
        relevant_knowledge = self.bank.get_relevant_knowledge(user_task)
        knowledge_context = json.dumps(relevant_knowledge, indent=2) if relevant_knowledge else "None"

        prompt = f"""
        Tugas Anda sebagai Swarm Queen (Project Manager).
        Pecah instruksi pengguna berikut menjadi Milestones teknis yang sangat spesifik.
        Gunakan pengetahuan strategis berikut jika relevan:
        {knowledge_context}

        INSTRUKSI PENGGUNA: "{user_task}"
        
        WAJIB: Setiap Masterplan HARUS mencakup tahapan berikut (dalam urutan logis):
        1. "terminal_bot": Inisialisasi Proyek (Berikan perintah `git init && npm install` atau `npx create-vite` dalam blok kode triple backticks).
        2. "coder_trae": Implementasi Kode (Penjelasan naratif untuk asisten Trae).
        3. "terminal_bot": Quality Check & Build (Gunakan `npm run build` dalam blok kode).
        4. "terminal_bot": Start Dev Server (Gunakan `npm run dev` dalam blok kode).
        5. "browser_bot": Visual Verification (Screenshot).
        6. "terminal_bot": Final Push (Gunakan perintah `git add . && git commit` dalam blok kode).

        PENTING: Jika "required_agent" adalah "terminal_bot", properti "instruction" di bawah ini HANYA boleh berisi blok kode triple backticks dengan perintah shell (Contoh: ```bash npm install ```). DILARANG KERAS menambahkan narasi atau penjelasan manusia di luar blok kode tersebut dalam field "instruction".

        FORMAT KELUARAN (Wajib JSON):
        {{
            "strategy": "Penjelasan singkat strategi harian/misi.",
            "milestones": [
                {{
                    "id": 1,
                    "name": "Nama Milestone",
                    "instruction": "Hanya blok kode untuk terminal_bot, atau penjelasan detail untuk coder_trae.",
                    "required_agent": "terminal_bot" | "coder_trae" | "browser_bot",
                    "is_critical": true
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gemini/gemini-2.5-pro", # Use high reasoning model
                messages=[
                    {"role": "system", "content": "You are the Queen Coordinator. Break down complex missions into precise milestones."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Queen failed to decompose: {e}")
            return {"strategy": "Linear fallback", "milestones": [{"id": 1, "name": "Main Execution", "instruction": user_task, "required_agent": "coder_trae"}]}

    async def orchestrate(self, user_task, update_callback=None):
        """
        Main loop for orchestration.
        """
        plan = await self.decompose_task(user_task)
        self.sona.start_trajectory(user_task)
        
        if update_callback:
            await update_callback(f"👑 **Queen Strategy:**\n{plan['strategy']}\n\n🏃 **Target:** {len(plan['milestones'])} Milestones.")

        final_results = []
        for ms in plan['milestones']:
            if update_callback:
                await update_callback(f"🏗️ **MENGERJAKAN Milestone {ms['id']}:** {ms['name']}")
            
            # 1. Pilih Worker (untuk saat ini kita hanya punya Trae Worker)
            # Logika seleksi agen bisa lebih kompleks di masa depan
            agent_id = ms.get('required_agent', 'coder_trae')
            
            # 2. Eksekusi melalui worker (akan diimplementasikan di worker_trae.py)
            # Placeholder for worker execution
            print(f"🚀 Delegating '{ms['name']}' to {agent_id}...")
            
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
