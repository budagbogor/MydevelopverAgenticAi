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
        print(f"[CODER] Thinking with PRO-MAX Brain...")
        standards = self._load_standards()
        standards_str = json.dumps(standards, indent=2)
        
        prompt = f"""
        Anda adalah Master Developer Autonomous dengan standar "PRO-MAX" yang terinspirasi oleh AutoGPT, open-hands, dan aider. 
        Tugas Anda adalah berpikir secara mendalam dan menulis kode berkualitas tinggi.

        STRUKTUR PEMIKIRAN (Wajib):
        1. THOUGHT: Rincian rencana Anda untuk menyelesaikan tugas ini.
        2. CRITICISM: Kritik terhadap rencana Anda sendiri (apa yang bisa salah? apa asumsi yang berisiko?).
        3. CODE: Implementasi kode dalam format Fiber-Optic.

        STANDAR KUALITAS PRO-MAX:
        {standards_str}

        DATA KONTEKS PROYEK (Repository Map):
        {context}

        INSTRUKSI TUGAS:
        "{instruction}"

        FORMAT OUTPUT (Fiber-Optic):
        Setiap blok kode HARUS diawali dengan baris "FILE: path/to/file.tsx".
        """

        try:
            # Gunakan model yang paling cerdas untuk koding
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a critical autonomous software engineer. Focus on Self-Criticism (AutoGPT style) to avoid hallucinations."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            raw_content = response.choices[0].message.content
            written_files = []
            
            # [HOTFIX 2.30] AutoGPT Extraction: Log Thought & Criticism
            thought = re.search(r'THOUGHT:\s*(.*?)\s*(?:CRITICISM:|FILE:)', raw_content, re.DOTALL | re.IGNORECASE)
            criticism = re.search(r'CRITICISM:\s*(.*?)\s*(?:FILE:|```)', raw_content, re.DOTALL | re.IGNORECASE)
            
            if thought: print(f"[THOUGHT] {thought.group(1).strip()[:200]}...")
            if criticism: print(f"[CRITICISM] {criticism.group(1).strip()[:200]}...")

            # [HOTFIX 2.22] Fiber-Optic 2.0: Ekstraksi Fleksibel Multi-Pattern
            file_blocks = []
            
            # Pattern 1: Standar FILE: path
            p1 = re.findall(r'FILE:\s*([^\s\n]+)[\s\n]*```[a-z]*\n(.*?)\n```', raw_content, re.DOTALL | re.IGNORECASE)
            for path, content in p1:
                file_blocks.append((path.strip(), content))
            
            # Pattern 2: Fallback ke Inline Path (Baris pertama blok kode)
            if not file_blocks:
                blocks = re.findall(r'```[a-z]*\n(.*?)\n```', raw_content, re.DOTALL)
                for block_content in blocks:
                    first_line = block_content.split('\n')[0].strip()
                    # Deteksi komentar // path atau # path atau /* path
                    path_match = re.search(r'^(?://|#|/\*|--)\s*([\w\.\-/]+)', first_line)
                    if path_match:
                        path_relative = path_match.group(1).strip()
                        actual_content = "\n".join(block_content.split("\n")[1:])
                        file_blocks.append((path_relative, actual_content))
            
            # Pattern 3: Fallback ke JSON mode
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
                print(f"DEBUG: AI Response did not contain extractable files. Body: {raw_content[:200]}...")
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
                "summary": f"Otonomi Sukses: Menulis {len(written_files)} file melalui jalur Fiber-Optic 2.0."
            }

        except Exception as e:
            # [HOTFIX 2.22] Detailed Error Feedback
            print(f"⚠️ [{self.agent_id}] Extraction Failed: {e}")
            return {"status": "FAILED", "error": f"Format Respon AI Tidak Dikenal: {str(e)}"}

        except Exception as e:
            print(f"❌ [{self.agent_id}] Error: {e}")
            return {"status": "FAILED", "error": str(e)}
