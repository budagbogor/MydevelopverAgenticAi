import json
import os

class LightningMemory:
    def __init__(self, storage_path="lightning_memory.json"):
        self.storage_path = storage_path
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_memory(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.memory, f, indent=4)

    def save_experience(self, window_title, task, actions, success=True):
        """Menyimpan pengalaman sukses atau gagal untuk pembelajaran."""
        key = f"{window_title.lower()} | {task.lower()}"
        
        if key not in self.memory:
            self.memory[key] = {
                "window": window_title,
                "task": task,
                "successful_actions": [],
                "failed_actions": [],
                "count": 0
            }
        
        if success:
            # Gunakan set untuk menghindari duplikasi aksi yang sama
            current_actions = [json.dumps(a) for a in actions]
            for action in current_actions:
                if action not in self.memory[key]["successful_actions"]:
                    self.memory[key]["successful_actions"].append(action)
            self.memory[key]["count"] += 1
        else:
            current_actions = [json.dumps(a) for a in actions]
            for action in current_actions:
                if action not in self.memory[key]["failed_actions"]:
                    self.memory[key]["failed_actions"].append(action)

        self._save_memory()
        return key

    def get_relevant_memories(self, window_title, task):
        """Mendapatkan memori yang relevan berdasarkan konteks jendela dan tugas."""
        # Cari kemiripan sederhana
        relevant = []
        for key, data in self.memory.items():
            # Jika jendela mirip atau tugas mirip
            if window_title.lower() in key or task.lower() in key:
                if data["successful_actions"]:
                    relevant.append(data)
        
        return relevant[:3] # Batasi 3 memori teratas agar prompt tidak terlalu panjang

    def get_formatted_for_prompt(self, window_title, task):
        memories = self.get_relevant_memories(window_title, task)
        if not memories:
            return "Tidak ada riwayat pembelajaran sebelumnya."
        
        formatted = "--- RIWAYAT PEMBELAJARAN (LIGHTNING MEMORY) ---\n"
        for m in memories:
            formatted += f"Window: {m['window']}\n"
            # Format aksi dari JSON string kembali ke list
            actions = [json.loads(a) for a in m['successful_actions']]
            formatted += f"Aksi Sukses: {actions}\n"
        formatted += "----------------------------------------------"
        return formatted
