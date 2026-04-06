# Dokumentasi Agentic AI Full Stack Developer

## Pendahuluan

Dokumen ini menyediakan panduan komprehensif untuk instalasi, konfigurasi, dan penggunaan Agentic AI Full Stack Developer. Sistem ini dirancang sebagai meta-agent yang memungkinkan pengguna untuk mengotomatisasi pengembangan perangkat lunak secara end-to-end melalui perintah bahasa alami yang dikirimkan via Telegram. Agentic AI akan berinteraksi dengan Integrated Development Environment (IDE) berbasis AI yang terinstal di PC lokal, seperti Google Antigravity, Trae, atau Cursor, untuk membangun, menguji, dan mendeploy aplikasi web, serta melaporkan progres dan hasil akhir kembali kepada pengguna melalui Telegram.

## 1. Arsitektur Sistem

Sistem Agentic AI ini terdiri dari beberapa komponen kunci yang bekerja secara sinergis untuk mencapai otomatisasi pengembangan perangkat lunak. Tabel berikut merinci setiap komponen, teknologi yang digunakan, dan peran spesifiknya dalam arsitektur.

| Komponen | Teknologi Kunci | Peran |
| :--- | :--- | :--- |
| **Telegram Interface** | `python-telegram-bot` | Berfungsi sebagai antarmuka utama bagi pengguna untuk mengirimkan perintah dan menerima pembaruan status, notifikasi, serta hasil akhir proyek. |
| **Orchestrator (Inti AI)** | Python, LangChain/LangGraph, LLM (misalnya, Gemini, GPT-4) | Bertindak sebagai "otak" sistem, bertanggung jawab untuk mengelola alur kerja, memecah tugas pengembangan yang kompleks menjadi langkah-langkah yang lebih kecil dan terkelola, serta memantau eksekusi dan progres setiap langkah. |
| **Computer Use Driver** | Anthropic Computer Use API, PyAutoGUI, Selenium (opsional) | Memungkinkan AI untuk berinteraksi dengan antarmuka grafis (GUI) PC lokal. Ini mencakup simulasi input keyboard dan mouse, serta pengambilan screenshot untuk observasi visual. |
| **Vision-Language Model (VLM)** | Claude 3.5 Sonnet, GPT-4o, Gemini Vision | Menganalisis screenshot yang diambil oleh Computer Use Driver untuk memahami konteks visual di layar, seperti lokasi elemen UI (kotak chat, tombol, pesan error) dalam IDE AI, dan status progres pengembangan. |
| **Target IDE AI** | Google Antigravity, Trae, Cursor | Lingkungan pengembangan terintegrasi berbasis AI yang akan dioperasikan oleh meta-agent. IDE ini akan menerima prompt dari Orchestrator dan secara otonom menghasilkan, memodifikasi, dan menguji kode. |
| **Deployment Module** | GitHub API, Vercel CLI, GitPython | Mengelola proses kontrol versi (misalnya, membuat repositori, melakukan commit, push ke GitHub) dan deployment aplikasi ke platform hosting seperti Vercel. |

## 2. Alur Kerja (Workflow) Operasional

Alur kerja sistem ini dirancang untuk menangani permintaan pengembangan perangkat lunak dari awal hingga akhir, dengan intervensi manusia minimal. Berikut adalah langkah-langkah utama dalam alur kerja:

1.  **Penerimaan Permintaan**: Pengguna mengirimkan deskripsi proyek (misalnya, "Buat aplikasi booking bengkel mobil") melalui Telegram. Telegram Interface meneruskan permintaan ini ke Orchestrator.
2.  **Perencanaan Proyek**: Orchestrator menganalisis permintaan, membuat rencana pengembangan yang terperinci (misalnya, inisialisasi proyek, desain database, pengembangan frontend/backend, pengujian, deployment), dan memecahnya menjadi serangkaian tugas yang dapat dieksekusi.
3.  **Interaksi IDE AI (Loop Eksekusi)**:
    *   **Pembukaan IDE**: Orchestrator, melalui Computer Use Driver, membuka aplikasi IDE AI yang ditargetkan di PC lokal.
    *   **Input Prompt**: VLM digunakan untuk mengidentifikasi area input prompt atau chat di dalam IDE. Orchestrator kemudian mengetikkan instruksi atau prompt kode yang relevan ke IDE AI.
    *   **Eksekusi Kode oleh IDE AI**: IDE AI memproses prompt dan mulai menghasilkan atau memodifikasi kode.
    *   **Monitoring & Observasi**: Computer Use Driver secara berkala mengambil screenshot layar IDE. VLM menganalisis screenshot ini untuk memantau progres, mengidentifikasi pesan error, atau menunggu konfirmasi dari IDE AI.
    *   **Iterasi & Koreksi**: Berdasarkan observasi VLM, Orchestrator dapat memberikan prompt lanjutan, mengoreksi instruksi, atau meminta pengujian jika diperlukan. Proses ini berulang hingga tugas pengembangan selesai.
4.  **Pengujian Otomatis**: Setelah kode dihasilkan, Orchestrator dapat menginstruksikan Computer Use Driver untuk menjalankan perintah terminal di dalam IDE (misalnya, `npm test`, `pytest`) untuk melakukan pengujian unit atau integrasi. Hasil pengujian akan dianalisis oleh VLM.
5.  **Kontrol Versi & Deployment**: Setelah pengembangan dan pengujian berhasil, Deployment Module akan:
    *   Menginisialisasi repositori Git lokal (jika belum ada).
    *   Melakukan commit perubahan kode.
    *   Membuat repositori baru di GitHub (jika belum ada) dan melakukan push kode ke sana.
    *   Menggunakan Vercel CLI untuk mendeploy aplikasi ke Vercel.
6.  **Pelaporan Hasil**: Setelah deployment berhasil, Orchestrator mengirimkan notifikasi ke pengguna melalui Telegram, termasuk tautan ke repositori GitHub dan URL aplikasi yang telah di-deploy di Vercel.

## 3. Instalasi

Untuk menginstal dan menjalankan Agentic AI Full Stack Developer, ikuti langkah-langkah berikut:

### 3.1. Prasyarat Sistem

Pastikan sistem Anda memenuhi prasyarat berikut:

*   **Sistem Operasi**: Windows 10/11, macOS, atau distribusi Linux modern.
*   **Python**: Python 3.10 atau versi lebih baru terinstal. Anda dapat mengunduhnya dari [python.org](https://www.python.org/).
*   **Git**: Git terinstal. Unduh dari [git-scm.com](https://git-scm.com/downloads).
*   **IDE AI**: Salah satu IDE AI berikut terinstal dan dapat diakses dari sistem operasi Anda:
    *   [Google Antigravity](https://antigravity.google/)
    *   [Cursor](https://cursor.com/)
    *   [TRAE](https://www.trae.ai/)
*   **Vercel CLI**: Instal Vercel CLI secara global. Buka terminal dan jalankan:
    ```bash
    npm install -g vercel
    ```
    Pastikan Anda sudah login ke akun Vercel Anda melalui CLI dengan `vercel login`.
*   **Docker** (Opsional, Direkomendasikan): Untuk isolasi lingkungan, instal Docker Desktop dari [docker.com](https://www.docker.com/products/docker-desktop/).

### 3.2. Kloning Repositori

Kloning repositori proyek ini ke mesin lokal Anda:

```bash
git clone <URL_REPOSITORI_PROYEK>
cd agentic_ai_project
```

### 3.3. Instalasi Dependensi Python

Navigasi ke direktori proyek dan instal dependensi Python yang diperlukan:

```bash
pip install -r requirements.txt
```

Buat file `requirements.txt` dengan konten berikut di root proyek:

```
python-telegram-bot==20.x
python-dotenv
pyautogui
requests
```

### 3.4. Konfigurasi Environment Variables

Buat file `.env` di root direktori proyek dan isi dengan kunci API Anda:

```dotenv
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY" # Atau API Key untuk VLM/LLM lain
GITHUB_TOKEN="YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
VERCEL_TOKEN="YOUR_VERCEL_TOKEN"
TARGET_IDE="Antigravity" # Ganti dengan Cursor atau Trae jika menggunakan itu
IDE_PATH="" # Opsional: Path lengkap ke executable IDE jika tidak ditemukan otomatis
```

*   **Telegram Bot Token**: Dapatkan dari BotFather di Telegram.
*   **Anthropic API Key**: Dapatkan dari [Anthropic Console](https://console.anthropic.com/).
*   **GitHub Personal Access Token**: Buat di [GitHub Developer Settings](https://github.com/settings/tokens). Pastikan memiliki scope `repo`.
*   **Vercel Token**: Dapatkan dari [Vercel Dashboard](https://vercel.com/account/tokens).

## 4. Penggunaan

### 4.1. Menjalankan Bot

Setelah semua prasyarat terpenuhi dan konfigurasi selesai, jalankan bot dari terminal:

```bash
python main.py
```

Bot akan mulai berjalan dan mendengarkan pesan di Telegram.

### 4.2. Interaksi dengan Bot

Buka aplikasi Telegram Anda dan mulai chat dengan bot Anda. Anda dapat mengirimkan perintah seperti:

*   `/start`: Untuk memulai interaksi dan mendapatkan pesan sambutan.
*   `Buatkan web apps system booking bengkel mobil`: Berikan deskripsi proyek yang ingin Anda buat. Bot akan mulai memproses permintaan Anda, berinteraksi dengan IDE AI, dan memberikan update progres.

### 4.3. Pemantauan Progres

Bot akan mengirimkan update progres secara berkala di Telegram. Anda juga dapat memantau aktivitas di PC lokal Anda, di mana IDE AI akan beroperasi secara otomatis.

## 5. Pertimbangan Keamanan dan Privasi

*   **Eksekusi Lokal**: Sebagian besar operasi pengembangan dan interaksi dengan IDE AI terjadi secara lokal di PC pengguna, yang meminimalkan risiko kebocoran kode sumber ke pihak ketiga.
*   **Enkripsi Telegram**: Komunikasi antara pengguna dan bot Telegram dienkripsi secara end-to-end oleh Telegram.
*   **Isolasi Lingkungan**: Sangat disarankan untuk menjalankan komponen sistem dalam lingkungan terisolasi (misalnya, Virtual Machine atau kontainer Docker) untuk mencegah potensi konflik dependensi dan meningkatkan keamanan sistem host.
*   **Manajemen Kunci API**: Kunci API harus disimpan dengan aman (misalnya, menggunakan variabel lingkungan atau sistem manajemen rahasia) dan tidak boleh di-hardcode dalam kode sumber.

## Kesimpulan

Agentic AI Full Stack Developer menawarkan pendekatan revolusioner untuk pengembangan perangkat lunak dengan mengotomatisasi seluruh siklus hidup proyek. Dengan mengikuti panduan ini, Anda dapat menginstal dan mengkonfigurasi sistem untuk mulai membangun aplikasi dengan kekuatan AI.

## Referensi

[1] Google Antigravity. (n.d.). *Google Antigravity: The agentic development platform*. Retrieved from [https://antigravity.google/](https://antigravity.google/)
[2] Cursor. (n.d.). *Cursor: The AI-first Code Editor*. Retrieved from [https://cursor.com/](https://cursor.com/)
[3] TRAE. (n.d.). *TRAE - Collaborate with Intelligence*. Retrieved from [https://www.trae.ai/](https://www.trae.ai/)
[4] Anthropic. (n.d.). *Computer use tool - Claude API Docs*. Retrieved from [https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
[5] Medium. (2025, November 1). *Building Autonomous Multi-Agent Systems with Cursor 2.0*. Retrieved from [https://medium.com/@abhishek97.edu/building-autonomous-multi-agent-systems-with-cursor-2-0-from-manual-to-fully-automated-04397c1831af](https://medium.com/@abhishek97.edu/building-autonomous-multi-agent-systems-with-cursor-2-0-from-manual-to-fully-automated-04397c1831af)
[6] Digital Applied. (2025, October 15). *Anthropic Computer Use API: Desktop Automation Guide*. Retrieved from [https://www.digitalapplied.com/blog/anthropic-computer-use-api-guide](https://www.digitalapplied.com/blog/anthropic-computer-use-api-guide)
