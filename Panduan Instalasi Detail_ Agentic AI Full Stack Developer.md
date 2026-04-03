# Panduan Instalasi Detail: Agentic AI Full Stack Developer

Panduan ini dirancang untuk membantu Anda mengonfigurasi setiap komponen sistem secara mendalam, mulai dari pembuatan akun hingga pengaturan lingkungan di PC lokal Anda. Tujuan utama dari dokumen ini adalah untuk memastikan Anda dapat menginstal, mengonfigurasi, dan menjalankan Agentic AI Full Stack Developer dengan sukses, memungkinkan otomatisasi pengembangan perangkat lunak melalui perintah Telegram.

---

## Bagian 1: Persiapan Akun dan Kunci API

Sistem Agentic AI ini memerlukan akses ke beberapa layanan eksternal untuk berfungsi dengan baik. Ikuti langkah-langkah di bawah ini untuk mendapatkan dan mengamankan kredensial (kunci API) yang diperlukan dari setiap layanan.

### 1.1. Telegram Bot (Antarmuka Pengguna)
Telegram Bot akan berfungsi sebagai titik interaksi utama antara Anda dan Agentic AI. Anda akan mengirimkan perintah pengembangan melalui bot ini dan menerima pembaruan status serta hasil proyek.

1.  **Buka Telegram**: Luncurkan aplikasi Telegram di perangkat Anda (desktop atau seluler).
2.  **Cari BotFather**: Di kolom pencarian Telegram, ketik `@BotFather` dan pilih bot resmi BotFather.
3.  **Mulai Percakapan**: Kirim perintah `/start` ke BotFather jika Anda belum pernah berinteraksi dengannya.
4.  **Buat Bot Baru**: Kirim perintah `/newbot`.
5.  **Pilih Nama Bot**: BotFather akan meminta Anda untuk memilih nama untuk bot Anda (misalnya, `AgenticDevAssistant`). Nama ini adalah nama tampilan bot.
6.  **Pilih Username Bot**: Selanjutnya, BotFather akan meminta Anda untuk memilih *username* untuk bot Anda (misalnya, `AgenticDevAssistantBot`). *Username* harus diakhiri dengan `bot` (case-insensitive) dan harus unik.
7.  **Dapatkan API Token**: Setelah berhasil membuat bot, BotFather akan memberikan pesan konfirmasi yang berisi **HTTP API Token**. Token ini adalah string alfanumerik yang sangat penting (contoh: `1234567890:ABCDEF1234567890abcdef1234567890`). **Simpan token ini dengan aman** karena akan digunakan sebagai nilai untuk variabel lingkungan `TELEGRAM_BOT_TOKEN`.
8.  **Mulai Bot Anda**: Cari bot yang baru Anda buat di Telegram (gunakan *username* yang Anda pilih) dan kirim perintah `/start` kepadanya. Ini akan menginisialisasi bot dan memungkinkan bot Anda untuk menerima pesan dari Anda.

### 1.2. Anthropic API (Otak Vision & Computer Use)
Anthropic API akan digunakan untuk model Vision-Language (VLM) yang memungkinkan Agentic AI "melihat" dan memahami antarmuka IDE AI Anda, serta Large Language Model (LLM) untuk perencanaan dan eksekusi tugas yang kompleks.

1.  **Daftar/Login ke Anthropic Console**: Kunjungi [Anthropic Console](https://console.anthropic.com/) dan daftar untuk akun baru atau masuk jika Anda sudah memilikinya.
2.  **Verifikasi Akun dan Saldo**: Pastikan akun Anda telah diverifikasi dan Anda memiliki saldo kredit yang cukup untuk menggunakan model Anthropic, khususnya **Claude 3.5 Sonnet** atau model lain yang mendukung *Computer Use* atau *Vision capabilities*. Anda mungkin perlu menambahkan metode pembayaran.
3.  **Buat Kunci API**: Navigasi ke bagian **API Keys** di dashboard Anthropic Console Anda.
4.  Klik tombol **"Create a Key"** atau serupa. Berikan nama deskriptif untuk kunci Anda (misalnya, `AgenticAIDevKey`).
5.  **Simpan Kunci API**: Salin kunci API yang dihasilkan. **Simpan kunci ini dengan sangat aman** karena ini adalah kredensial sensitif. Ini akan digunakan sebagai nilai untuk variabel lingkungan `ANTHROPIC_API_KEY`.

### 1.3. GitHub (Kontrol Versi & Repositori)
GitHub akan digunakan untuk mengelola kode sumber proyek yang dihasilkan oleh Agentic AI, termasuk pembuatan repositori baru, *commit*, dan *push* kode.

1.  **Login ke GitHub**: Buka [github.com](https://github.com/) dan masuk ke akun GitHub Anda.
2.  **Akses Pengaturan Pengembang**: Klik gambar profil Anda di sudut kanan atas, lalu pilih **"Settings"**.
3.  Di sidebar kiri, gulir ke bawah dan klik **"Developer settings"**.
4.  Di sidebar kiri berikutnya, pilih **"Personal access tokens"**, lalu klik **"Tokens (classic)"**.
5.  **Buat Token Baru**: Klik tombol **"Generate new token (classic)"**.
6.  **Konfigurasi Token**: Berikan nama yang mudah diingat untuk token Anda (misalnya, `AgenticDevPAT`).
7.  **Pilih Scope**: Centang kotak untuk scope berikut. Ini memberikan izin yang diperlukan agar Agentic AI dapat berinteraksi dengan repositori Anda:
    *   `repo`: Memberikan kontrol penuh atas repositori pribadi.
    *   `workflow`: Memungkinkan pembaruan alur kerja GitHub Actions (jika di masa depan Anda ingin mengotomatisasi CI/CD).
8.  **Generate Token**: Gulir ke bawah dan klik tombol **"Generate token"**.
9.  **Simpan Token**: GitHub akan menampilkan token yang dihasilkan. **Salin token ini segera** karena Anda tidak akan dapat melihatnya lagi setelah meninggalkan halaman ini. Simpan sebagai `GITHUB_TOKEN`.

### 1.4. Vercel (Deployment Otomatis)
Vercel akan digunakan untuk mendeploy aplikasi web yang dihasilkan oleh Agentic AI ke lingkungan produksi secara otomatis.

1.  **Login ke Vercel**: Kunjungi [vercel.com](https://vercel.com/) dan masuk ke akun Vercel Anda.
2.  **Akses Pengaturan Akun**: Klik gambar profil Anda di sudut kanan atas, lalu pilih **"Settings"**.
3.  Di sidebar kiri, pilih **"Tokens"**.
4.  **Buat Token Baru**: Klik tombol **"Create"**.
5.  **Konfigurasi Token**: Berikan nama yang deskriptif (misalnya, `AgenticDevVercelToken`).
6.  **Pilih Scope**: Pastikan scope diatur ke **"Full Access"** untuk memungkinkan deployment penuh.
7.  **Simpan Token**: Salin token yang dihasilkan. **Simpan token ini dengan aman** karena ini akan digunakan sebagai nilai untuk variabel lingkungan `VERCEL_TOKEN`.

---

## Bagian 2: Instalasi Perangkat Lunak dan Lingkungan Python di PC Lokal

Bagian ini memandu Anda melalui instalasi perangkat lunak dasar yang diperlukan dan penyiapan lingkungan pengembangan Python untuk proyek Agentic AI.

### 2.1. Instalasi Python dan Git

1.  **Python (Versi 3.10 atau Lebih Baru)**:
    *   Kunjungi situs web resmi Python: [python.org](https://www.python.org/downloads/).
    *   Unduh *installer* yang sesuai dengan sistem operasi Anda (Windows, macOS, Linux).
    *   **Untuk Windows**: Saat menjalankan *installer*, **SANGAT PENTING** untuk mencentang opsi **"Add Python to PATH"** di awal proses instalasi. Ini akan memastikan Python dapat diakses dari Command Prompt atau PowerShell.
    *   Ikuti langkah-langkah instalasi lainnya dengan pengaturan default.
    *   Verifikasi instalasi dengan membuka terminal/Command Prompt dan menjalankan:
        ```bash
        python --version
        pip --version
        ```
        Anda seharusnya melihat versi Python dan pip yang terinstal.

2.  **Git (Sistem Kontrol Versi)**:
    *   Kunjungi situs web resmi Git: [git-scm.com/downloads](https://git-scm.com/downloads).
    *   Unduh *installer* yang sesuai dengan sistem operasi Anda.
    *   Jalankan *installer* dan ikuti langkah-langkahnya. Pengaturan default umumnya sudah cukup untuk sebagian besar pengguna.
    *   Verifikasi instalasi dengan membuka terminal/Command Prompt dan menjalankan:
        ```bash
        git --version
        ```
        Anda seharusnya melihat versi Git yang terinstal.

### 2.2. Instalasi Vercel CLI

Vercel Command Line Interface (CLI) diperlukan untuk mendeploy proyek ke Vercel dari terminal Anda.

1.  **Instal Node.js**: Vercel CLI memerlukan Node.js. Jika Anda belum menginstalnya, unduh dari [nodejs.org](https://nodejs.org/en/download/). Ikuti instruksi instalasi default.
2.  **Instal Vercel CLI Global**: Buka terminal (Command Prompt/PowerShell di Windows, Terminal di macOS/Linux) dan jalankan perintah berikut untuk menginstal Vercel CLI secara global:
    ```bash
    npm install -g vercel
    ```
3.  **Login ke Vercel CLI**: Setelah instalasi selesai, Anda perlu mengautentikasi Vercel CLI dengan akun Vercel Anda. Jalankan perintah:
    ```bash
    vercel login
    ```
    Perintah ini akan membuka browser Anda dan meminta Anda untuk login ke akun Vercel Anda. Setelah berhasil login, terminal akan mengonfirmasi bahwa Anda telah masuk.

### 2.3. Persiapan Lingkungan Proyek Python

Langkah ini melibatkan kloning repositori proyek Agentic AI dan menyiapkan lingkungan Python yang terisolasi untuk dependensinya.

1.  **Kloning Repositori Proyek**: Buka terminal dan navigasikan ke direktori tempat Anda ingin menyimpan proyek (misalnya, `C:\Users\YourUser\Documents\Projects`). Kemudian, kloning repositori Agentic AI:
    ```bash
    git clone <URL_REPOSITORI_PROYEK_ANDA>
    cd agentic_ai_project
    ```
    *(Catatan: URL repositori proyek akan diberikan setelah kode inti selesai dan di-push ke GitHub.)*

2.  **Buat Virtual Environment**: Sangat disarankan untuk menggunakan *virtual environment* untuk mengelola dependensi Python proyek ini. Ini mencegah konflik dengan paket Python global lainnya.
    ```bash
    python -m venv venv
    ```
    Perintah ini akan membuat folder `venv` di dalam direktori proyek Anda yang berisi instalasi Python terisolasi.

3.  **Aktifkan Virtual Environment**:
    *   **Windows (Command Prompt)**:
        ```bash
        .\venv\Scripts\activate
        ```
    *   **Windows (PowerShell)**:
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **macOS/Linux (Bash/Zsh)**:
        ```bash
        source venv/bin/activate
        ```
    Setelah diaktifkan, Anda akan melihat `(venv)` di awal prompt terminal Anda, menunjukkan bahwa Anda berada di dalam *virtual environment*.

4.  **Buat `requirements.txt`**: Di root direktori proyek (`agentic_ai_project`), buat file baru bernama `requirements.txt` dan isi dengan konten berikut:
    ```
    python-telegram-bot==20.x
    python-dotenv
    pyautogui
    requests
    Pillow
    ```

5.  **Instal Dependensi Python**: Dengan *virtual environment* aktif, instal semua dependensi yang tercantum dalam `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    Ini akan menginstal semua pustaka Python yang diperlukan untuk menjalankan Agentic AI.

---

## Bagian 3: Konfigurasi IDE AI (Google Antigravity / Trae / Cursor) untuk Otomatisasi

Agentic AI akan berinteraksi langsung dengan IDE AI pilihan Anda. Bagian ini menjelaskan cara menginstal IDE dan menyiapkan sistem operasi Anda untuk memungkinkan otomatisasi GUI yang mulus.

### 3.1. Instalasi IDE AI Pilihan Anda

Pilih salah satu IDE AI berikut dan instal di PC lokal Anda:

*   **Google Antigravity**: Kunjungi [antigravity.google](https://antigravity.google/) dan ikuti instruksi instalasi untuk sistem operasi Anda. Antigravity dirancang sebagai platform pengembangan berbasis agen, menjadikannya pilihan yang sangat cocok.
*   **Cursor**: Kunjungi [cursor.com](https://cursor.com/) dan unduh *installer* yang sesuai. Cursor adalah IDE yang berfokus pada AI dengan fitur-fitur seperti *code generation*, *chat*, dan *debugging* yang didukung AI.
*   **TRAE**: Kunjungi [trae.ai](https://www.trae.ai/) dan unduh *installer* yang tersedia. TRAE diposisikan sebagai "10x AI Engineer" yang dapat membangun solusi perangkat lunak secara independen.

Pastikan IDE yang Anda pilih terinstal dengan benar dan dapat diluncurkan dari menu Start (Windows) atau Applications (macOS/Linux).

### 3.2. Pengaturan Aksesibilitas Sistem Operasi (PENTING)

Modul `ComputerDriver` dalam Agentic AI menggunakan pustaka `pyautogui` untuk mensimulasikan input keyboard dan mouse, serta mengambil *screenshot*. Untuk melakukan ini, `pyautogui` memerlukan izin aksesibilitas khusus dari sistem operasi Anda. Tanpa izin ini, Agentic AI tidak akan dapat berinteraksi dengan GUI IDE Anda.

*   **Untuk Pengguna Windows**:
    *   Pastikan Anda menjalankan terminal (Command Prompt atau PowerShell) sebagai **Administrator** saat meluncurkan `main.py` bot. Klik kanan pada ikon terminal dan pilih "Run as administrator".
    *   Dalam beberapa kasus, Anda mungkin perlu memastikan bahwa aplikasi Python atau terminal Anda memiliki izin untuk mengontrol input. Ini biasanya diatur secara otomatis saat menjalankan sebagai administrator, tetapi jika Anda mengalami masalah, periksa pengaturan keamanan Windows Anda terkait "Control access to your screen" atau "Allow apps to control your device".

*   **Untuk Pengguna macOS**:
    *   Buka **System Settings** (atau System Preferences di versi macOS yang lebih lama).
    *   Navigasi ke **Privacy & Security** > **Accessibility**.
    *   Di panel kanan, Anda akan melihat daftar aplikasi yang meminta kontrol komputer Anda. Anda perlu menambahkan aplikasi terminal yang Anda gunakan (misalnya, Terminal, iTerm2) dan juga aplikasi IDE AI Anda (misalnya, Google Antigravity, Cursor, TRAE) ke daftar ini.
    *   Klik ikon `+` dan navigasikan ke `/Applications/` untuk menambahkan IDE Anda, dan `/System/Applications/Utilities/` untuk Terminal (atau lokasi iTerm2 jika Anda menggunakannya).
    *   Pastikan kotak centang di samping setiap aplikasi yang relevan diaktifkan.

*   **Untuk Pengguna Linux**:
    *   Pengaturan aksesibilitas di Linux bervariasi tergantung pada distribusi dan lingkungan desktop (GNOME, KDE, XFCE, dll.). Umumnya, `pyautogui` bekerja dengan baik di Linux jika `python-xlib` terinstal dan X server berjalan. Anda mungkin perlu menginstal paket tambahan seperti `scrot` atau `gnome-screenshot` untuk fungsi *screenshot*.
    *   Instal dependensi yang diperlukan:
        ```bash
        sudo apt-get install scrot # Untuk Debian/Ubuntu
        sudo yum install scrot # Untuk Fedora/CentOS
        pip install python-xlib
        ```
    *   Jika Anda mengalami masalah, cari dokumentasi spesifik untuk distribusi Linux dan lingkungan desktop Anda mengenai izin aksesibilitas untuk aplikasi yang mengontrol input.

---

## Bagian 4: Menjalankan dan Menguji Sistem

Setelah semua persiapan selesai, Anda siap untuk menjalankan Agentic AI dan mengujinya.

### 4.1. Konfigurasi File `.env`

Di root direktori proyek Anda (`agentic_ai_project`), buat file baru bernama `.env` (pastikan ada titik di depannya) dan masukkan semua kunci API yang telah Anda kumpulkan di Bagian 1. Ganti placeholder dengan nilai aktual Anda.

```dotenv
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
GITHUB_TOKEN="YOUR_GITHUB_PERSONAL_ACCESS_TOKEN_HERE"
VERCEL_TOKEN="YOUR_VERCEL_TOKEN_HERE"

# Pilih IDE AI yang Anda gunakan: Antigravity, Trae, atau Cursor
TARGET_IDE="Antigravity"

# Opsional: Path lengkap ke executable IDE jika sistem tidak dapat menemukannya secara otomatis
# Contoh untuk Windows: IDE_PATH="C:\Program Files\Google Antigravity\antigravity.exe"
# Contoh untuk macOS: IDE_PATH="/Applications/Cursor.app"
IDE_PATH=""
```

### 4.2. Menjalankan Bot

Pastikan *virtual environment* Anda aktif (lihat Bagian 2.3) dan Anda berada di root direktori proyek (`agentic_ai_project`) di terminal. Kemudian, jalankan perintah berikut:

```bash
python main.py
```

Anda akan melihat pesan di terminal yang menunjukkan bahwa bot telah dimulai. Bot sekarang akan mendengarkan perintah dari Telegram.

### 4.3. Interaksi Awal dengan Bot

1.  Buka aplikasi Telegram Anda dan mulai chat dengan bot yang telah Anda buat.
2.  Kirim perintah `/start`. Bot akan merespons dengan pesan sambutan.
3.  Kirimkan deskripsi proyek yang ingin Anda buat, misalnya:
    `Buatkan web apps system booking bengkel mobil`
    Bot akan mengonfirmasi penerimaan permintaan dan mulai memprosesnya. Anda akan melihat log aktivitas di terminal Anda dan bot akan mengirimkan pembaruan progres melalui Telegram.

### 4.4. Pemantauan Progres dan Troubleshooting

*   **Pemantauan Visual**: Perhatikan layar PC Anda. Anda akan melihat Agentic AI secara otomatis membuka IDE AI, mengetikkan perintah, dan berinteraksi dengan antarmuka. Ini adalah indikasi bahwa `ComputerDriver` berfungsi.
*   **Log Terminal**: Pantau output di terminal tempat Anda menjalankan `main.py`. Ini akan memberikan informasi tentang langkah-langkah yang sedang diambil oleh Orchestrator.
*   **Pembaruan Telegram**: Bot akan mengirimkan pesan ke Telegram Anda mengenai status proyek, seperti "Langkah 1: Merencanakan arsitektur proyek..." dan hasil akhir deployment.

#### Troubleshooting Umum:

*   **Mouse/Keyboard Tidak Bergerak**: Jika Agentic AI tidak dapat menggerakkan mouse atau mengetik, kemungkinan besar ini adalah masalah izin aksesibilitas. Pastikan Anda telah mengikuti langkah-langkah di Bagian 3.2 dengan benar untuk sistem operasi Anda. Di Windows, coba jalankan terminal sebagai Administrator. Di macOS, pastikan aplikasi terminal dan IDE Anda terdaftar di pengaturan Aksesibilitas.
*   **IDE Tidak Terbuka**: Pastikan nama IDE yang Anda masukkan di `TARGET_IDE` dalam file `.env` sesuai persis dengan nama aplikasi yang terdaftar di sistem operasi Anda. Jika masih bermasalah, coba tentukan `IDE_PATH` secara eksplisit ke lokasi executable IDE Anda.
*   **Error API (Anthropic, GitHub, Vercel)**: Periksa kembali semua kunci API di file `.env` Anda. Pastikan tidak ada kesalahan ketik, token belum kedaluwarsa, dan akun Anda memiliki izin serta saldo yang cukup (terutama untuk Anthropic).
*   **Bot Tidak Merespons di Telegram**: Pastikan `TELEGRAM_BOT_TOKEN` sudah benar dan bot Anda sedang berjalan di terminal. Periksa juga koneksi internet Anda.
*   **`pyautogui.FAILSAFE` Terpicu**: `pyautogui` memiliki fitur keamanan di mana jika Anda menggerakkan mouse ke salah satu sudut layar (biasanya pojok kiri atas) terlalu cepat, program akan berhenti. Ini dirancang untuk memberi Anda kontrol kembali jika otomatisasi berjalan di luar kendali. Jika ini terjadi, cukup jalankan ulang bot.

---

## Kesimpulan

Dengan mengikuti panduan instalasi detail ini, Anda seharusnya sekarang memiliki Agentic AI Full Stack Developer yang berfungsi penuh di PC lokal Anda. Sistem ini membuka potensi besar untuk otomatisasi pengembangan perangkat lunak, memungkinkan Anda untuk fokus pada ide-ide besar sementara AI menangani detail implementasi. Jangan ragu untuk bereksperimen dengan berbagai deskripsi proyek dan mengamati bagaimana Agentic AI mewujudkannya.

## Referensi

[1] Google Antigravity. (n.d.). *Google Antigravity: The agentic development platform*. Retrieved from [https://antigravity.google/](https://antigravity.google/)
[2] Cursor. (n.d.). *Cursor: The AI-first Code Editor*. Retrieved from [https://cursor.com/](https://cursor.com/)
[3] TRAE. (n.d.). *TRAE - Collaborate with Intelligence*. Retrieved from [https://www.trae.ai/](https://www.trae.ai/)
[4] Anthropic. (n.d.). *Computer use tool - Claude API Docs*. Retrieved from [https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
[5] Medium. (2025, November 1). *Building Autonomous Multi-Agent Systems with Cursor 2.0*. Retrieved from [https://medium.com/@abhishek97.edu/building-autonomous-multi-agent-systems-with-cursor-2-0-from-manual-to-fully-automated-04397c1831af](https://medium.com/@abhishek97.edu/building-autonomous-multi-agent-systems-with-cursor-2-0-from-manual-to-fully-automated-04397c1831af)
[6] Digital Applied. (2025, October 15). *Anthropic Computer Use API: Desktop Automation Guide*. Retrieved from [https://www.digitalapplied.com/blog/anthropic-computer-use-api-guide](https://www.digitalapplied.com/blog/anthropic-computer-use-api-guide)
[7] Python Software Foundation. (n.d.). *Python Downloads*. Retrieved from [https://www.python.org/downloads/](https://www.python.org/downloads/)
[8] Git. (n.d.). *Downloads*. Retrieved from [https://git-scm.com/downloads](https://git-scm.com/downloads)
[9] Node.js. (n.d.). *Download Node.js*. Retrieved from [https://nodejs.org/en/download/](https://nodejs.org/en/download/)
[10] Vercel. (n.d.). *Vercel CLI*. Retrieved from [https://vercel.com/docs/cli](https://vercel.com/docs/cli)
