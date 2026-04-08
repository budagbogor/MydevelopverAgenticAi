import os
import json
import re
from openai import OpenAI
from config import SUMOPOD_API_KEY, SUMOPOD_BASE_URL, DEFAULT_MODEL

class InternalCoder:
    """
    Internal Coder Worker (Headless Autonomous Developer) - PRO-MAX Upgrade
    Menulis kode langsung ke disk menggunakan API LLM dan Standar PRO-MAX.
    """
    def __init__(self, agent_id="coder_internal"):
        self.agent_id = agent_id
        self.client = OpenAI(api_key=SUMOPOD_API_KEY, base_url=SUMOPOD_BASE_URL)
        self.standards_path = "neural/patterns/pro_max_standards.json"

    def _load_standards(self):
        """Memuat standar koding PRO-MAX dari pengetahuan bot."""
        if os.path.exists(self.standards_path):
            with open(self.standards_path, 'r') as f:
                return json.load(f)
        return {}

    async def execute_task(self, instruction, active_root, context="No context"):
        """
        Menerima instruksi koding, menghasilkan file, dan menyimpannya secara absolut.
        """
        print(f"🧠 [{self.agent_id}] Thinking with PRO-MAX Brain...")
        standards = self._load_standards()
        standards_str = json.dumps(standards, indent=2)
        
        prompt = f"""
        Anda adalah Master Developer Autonomous dengan standar "PRO-MAX" yang terinspirasi oleh open-devin dan gpt-engineer. 
        Tugas Anda adalah menulis kode lengkap untuk file-file yang diperlukan berdasarkan instruksi di bawah ini.
        
        STANDAR KUALITAS PRO-MAX:
        {standards_str}

        DATA KONTEKS PROYEK (Struktur File Saat Ini):
        {context}

        INSTRUKSI TUGAS:
        "{instruction}"

        ATURAN PENULISAN:
        1. Gunakan TypeScript (React/Vite).
        2. Terapkan desain premium (Glassmorphism, Bento Grid, Lucide Icons, Framer Motion).
        3. Tulis kode yang SIAP PRODUKSI, modular, dan bersih.
        4. Berikan output dalam format JSON yang berisi daftar file yang akan dibuat/diperbarui.

        FORMAT OUTPUT (Wajib JSON):
        {{
            "files": [
                {{
                    "path": "src/components/MyComponent.tsx",
                    "content": "// Kode lengkap di sini...",
                    "explanation": "Penjelasan singkat perubahan."
                }}
            ]
        }}
        """

        try:
            # Gunakan model yang paling cerdas untuk koding
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional developer. Provide your response as a series of code blocks. Each block MUST be preceded by a line with the file path, like this: \n\nFILE: src/App.tsx\n```tsx\n// code\n```"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            raw_content = response.choices[0].message.content
            written_files = []
            
            # [HOTFIX 2.17] Fiber-Optic Extraction: Ekstrak file dan konten menggunakan Regex
            # Pola: Mencari "FILE: path" diikuti oleh blok markdown
            file_blocks = re.findall(r'FILE:\s*([^\s\n]+)[\s\n]*```[a-z]*\n(.*?)\n```', raw_content, re.DOTALL)
            
            # Jika Regex gagal, coba fallback ke JSON mode yang sudah disanitasi
            if not file_blocks:
                try:
                    clean_content = re.sub(r'^```json\s*', '', raw_content.strip())
                    clean_content = re.sub(r'\s*```$', '', clean_content)
                    data = json.loads(clean_content)
                    for f in data.get('files', []):
                        file_blocks.append((f['path'], f['content']))
                except:
                    pass

            if not file_blocks:
                raise ValueError("Gagal mengekstrak blok kode valid dari respon AI.")

            for path_relative, content in file_blocks:
                path_absolute = os.path.join(active_root, path_relative)
                
                # Pastikan direktori ada
                dir_name = os.path.dirname(path_absolute)
                if dir_name and not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)
                
                with open(path_absolute, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                written_files.append(path_relative)
                print(f"✅ [{self.agent_id}] Extracted & Written: {path_absolute}")

            return {
                "status": "SUCCESS",
                "written_files": written_files,
                "summary": f"Otonomi Sukses: Menulis {len(written_files)} file melalui jalur Fiber-Optic."
            }

        except Exception as e:
            # [HOTFIX 2.17] Silent Fail: Jangan membanjiri log internal dengan detail teknis JSON
            print(f"⚠️ [{self.agent_id}] Silent Retry Triggered: {e}")
            return {"status": "FAILED", "error": "AI Response Format Invalid. Retrying silently..."}

            return {
                "status": "SUCCESS",
                "written_files": written_files,
                "summary": f"Berhasil menulis {len(written_files)} file secara otonom."
            }

        except Exception as e:
            print(f"❌ [{self.agent_id}] Error: {e}")
            return {"status": "FAILED", "error": str(e)}
