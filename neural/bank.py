import json
import os
import yaml
from openai import OpenAI
from config import SUMOPOD_API_KEY, SUMOPOD_BASE_URL, DEFAULT_MODEL

class ReasoningBank:
    """
    ReasoningBank (Distilled Knowledge)
    Ref: RuFlo v3 Philosophy
    Turns long trajectories into compact, reusable Knowledge Items (KIs).
    """
    def __init__(self, storage_path="neural/knowledge_bank.json"):
        self.storage_path = storage_path
        self.bank = self._load_bank()
        self.client = OpenAI(api_key=SUMOPOD_API_KEY, base_url=SUMOPOD_BASE_URL)

    def _load_bank(self):
        default_structure = {"patterns": [], "resolved_errors": [], "best_practices": []}
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except: pass
        return default_structure

    def _save_bank(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.bank, f, indent=4)

    async def distill_trajectory(self, trajectory_json):
        """
        Uses an LLM to extract the 'essence' of a trajectory.
        What worked? What failed? What's the lesson?
        """
        prompt = f"""
        Tugas Anda sebagai Chief Neural Architect.
        Analisis riwayat tindakan (trajectory) agen berikut dan ekstrak "Knowledge Item" (KI).
        
        TRAJECTORY:
        {json.dumps(trajectory_json, indent=2)}
        
        EKSTRAK (Wajib JSON):
        - "title": Judul singkat untuk pengetahuan ini.
        - "category": 'pattern', 'error_resolution', atau 'best_practice'.
        - "summary": Deskripsi singkat (1 kalimat).
        - "distillation": Pelajaran mendalam (langkah konkrit untuk masa depan).
        - "keywords": 3-5 kata kunci.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You convert raw AI execution logs into high-level strategic knowledge. Ensure output is a SINGLE JSON OBJECT."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            print(f"DEBUG: RAW KI CONTENT: {raw_content[:200]}")
            ki = json.loads(raw_content)
            
            # Jika LLM mengembalikan list, ambil elemen pertama
            if isinstance(ki, list) and len(ki) > 0:
                ki = ki[0]
            
            if not isinstance(ki, dict):
                raise ValueError("KI is not a dictionary")

            # Save to bank (Gunakan .get untuk antisipasi key hilang)
            category = ki.get('category', 'best_practice')
            if category == 'pattern': self.bank['patterns'].append(ki)
            elif category == 'error_resolution': self.bank['resolved_errors'].append(ki)
            else: self.bank.setdefault('best_practices', []).append(ki)
            
            self._save_bank()
            return ki
        except Exception as e:
            print(f"⚠️ Gagal melakukan distilasi: {e}")
            return None

    def get_relevant_knowledge(self, task_description):
        """
        Mencari pengetahuan relevan di bank berdasarkan kata kunci.
        """
        relevant = []
        task_lower = task_description.lower()
        
        for cat in self.bank:
            for item in self.bank[cat]:
                if any(kw in task_lower for kw in item.get('keywords', [])):
                    relevant.append(item)
                    
        return relevant[:5]
