import base64
import os
import json
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv

# Load config
load_dotenv()
SUMOPOD_API_KEY = os.getenv("SUMOPOD_API_KEY")
SUMOPOD_BASE_URL = os.getenv("SUMOPOD_BASE_URL", "https://ai.sumopod.com/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")

client = OpenAI(api_key=SUMOPOD_API_KEY, base_url=SUMOPOD_BASE_URL)

def test_vision():
    print(f"🔍 Mencoba Vision Test ke: {SUMOPOD_BASE_URL}")
    print(f"🤖 Model: {DEFAULT_MODEL}")
    
    # Ambil screenshot dummy atau jika ada file lama
    test_img_path = "test_vision.jpg"
    
    try:
        # Buat gambar dummy 400x400 RGB
        img = Image.new('RGB', (400, 400), color = (73, 109, 137))
        img.save(test_img_path, "JPEG", quality=50)
        
        with open(test_img_path, "rb") as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')
            
        print("📤 Mengirim gambar ke API...")
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Apa isi gambar ini? Jawab singkat saja."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }
            ],
            max_tokens=50
        )
        
        print("✅ BERHASIL!")
        print(f"💬 Respon AI: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ GAGAL: {str(e)}")
        if hasattr(e, 'response'):
            print(f"📋 Detail Error: {e.response.text}")
        return False

if __name__ == "__main__":
    test_vision()
