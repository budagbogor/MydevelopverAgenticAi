import os
import asyncio
import sys
import time
from telegram import BotCommand
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from config import TELEGRAM_BOT_TOKEN, ALLOWED_TELEGRAM_WHITELIST, PROJECT_ROOT, GITHUB_TOKEN, VERCEL_TOKEN, save_config
from orchestrator import Orchestrator
from deployment import DeploymentManager
from search_tool import WebSearch

class TelegramBot:
    def __init__(self, token=None):
        self.lock_file = "bot.lock"
        self.is_processing = False # ANTI-CONCURRENCY LOCK
        if os.path.exists(self.lock_file):
            print("\n⚠️ PERINGATAN: Bot sudah berjalan di jendela lain!")
            print("Harap tutup bot lama sebelum membuka yang baru.")
            sys.exit(1)
        
        with open(self.lock_file, "w") as f:
            f.write(str(os.getpid()))

        self.orchestrator = Orchestrator()
        self.web_search = WebSearch()
        bot_token = token if token else TELEGRAM_BOT_TOKEN
        self.app = Application.builder().token(bot_token).build()
        
        # Handlers
        self.app.add_handler(CommandHandler('start', self.handle_start))
        self.app.add_handler(CommandHandler('help', self.handle_help))
        self.app.add_handler(MessageHandler(filters.Regex(r'^/cmd\s'), self.handle_terminal_command))
        self.app.add_handler(CommandHandler('new_project', self.handle_new_project))
        self.app.add_handler(CommandHandler('deploy_github', self.handle_deploy_github))
        self.app.add_handler(CommandHandler('search', self.handle_search_manual))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def is_allowed(self, user_id):
        is_ok = str(user_id) in ALLOWED_TELEGRAM_WHITELIST
        if not is_ok:
            print(f"🚫 Akses Ditolak untuk User ID: {user_id}")
        return is_ok

    async def handle_start(self, update, context):
        """Menampilkan panduan awal dan mendaftarkan menu perintah."""
        commands = [
            BotCommand("start", "Mulai dan lihat panduan"),
            BotCommand("help", "Bantuan perintah lengkap"),
            BotCommand("new_project", "Buat folder proyek baru"),
            BotCommand("search", "Cari info di web (manual)"),
            BotCommand("deploy_github", "Push kode ke GitHub"),
            BotCommand("cmd", "Jalankan perintah terminal")
        ]
        await context.bot.set_my_commands(commands)
        
        welcome_msg = (
            "🌌 **Halo! Saya DarkSky Agent.**\n\n"
            "Saya adalah asisten pengembang otonom Anda. Anda bisa langsung "
            "mengirimkan instruksi pembuatan software atau menggunakan menu "
            "perintah di pojok kiri bawah.\n\n"
            "Ketik /help untuk detail penggunaan."
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def handle_help(self, update, context):
        """Menampilkan panduan perintah lengkap."""
        help_msg = (
            "📖 **Panduan Perintah DarkSky:**\n\n"
            "🚀 **Tugas Otonom:** Kirim teks biasa (contoh: 'buatkan landing page')\n"
            "📁 **/new_project [Nama]**: Membuat folder & pindah fokus kerja\n"
            "💻 **/cmd [perintah]**: Menjalankan CLI (contoh: `/cmd dir`)\n"
            "🔍 **/search [query]**: Riset manual ke internet\n"
            "📦 **/deploy_github**: Mengunggah progress ke Repo Anda\n\n"
            "⚡ *Tips:* Gunakan Dashboard Desktop untuk memantau log secara visual!"
        )
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def handle_terminal_command(self, update, context):
        user_id = update.effective_user.id
        if not self.is_allowed(user_id):
            return await update.message.reply_text(f"🚫 Akses ditolak (ID Anda: {user_id})")
        
        cmd = update.message.text.split('/cmd ', 1)[1]
        await update.message.reply_text(f"💻 **Terminal:** `{cmd}`", parse_mode='Markdown')
        
        try:
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=PROJECT_ROOT
            )
            stdout, stderr = await process.communicate()
            res = (stdout + stderr).decode().strip()
            if not res: res = "Command executed (no output)."
            await update.message.reply_text(f"```\n{res[:4000]}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ **Error Terminal:**\n{str(e)}")

    async def handle_new_project(self, update, context):
        user_id = update.effective_user.id
        if not self.is_allowed(user_id): return await update.message.reply_text(f"🚫 Akses ditolak (ID Anda: {user_id})")
        if not context.args: return await update.message.reply_text("💡 Gunakan: /new_project Nama")

        project_name = context.args[0]
        from config import BASE_DIR
        new_path = os.path.join(BASE_DIR, project_name)
        try:
            is_new = not os.path.exists(new_path)
            if is_new: os.makedirs(new_path)
            
            if save_config({"PROJECT_ROOT": new_path}):
                msg = f"✅ Proyek diperbarui ke: {new_path}\n"
                msg += "🚀 **Mereset IDE dan Membuka Folder Baru...**" if is_new else "🔄 **Melanjutkan proyek yang sudah ada...**"
                await update.message.reply_text(msg)
                
                # Paksa tutup dan buka kembali IDE dengan path baru
                self.orchestrator.driver.ensure_focus(force_restart=True)
                # Bersihkan tab lama (Clean Slate) hanya jika proyek benar-benar baru
                if is_new: self.orchestrator.driver.close_all_tabs()
                # Tunggu sebentar agar IDE benar-benar terbuka sebelum menerima tugas baru
                await asyncio.sleep(5)
            else:
                await update.message.reply_text("❌ Gagal update .env")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def handle_deploy_github(self, update, context):
        user_id = update.effective_user.id
        if not self.is_allowed(user_id): return await update.message.reply_text(f"🚫 Akses ditolak (ID Anda: {user_id})")
        if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
            return await update.message.reply_text("❌ GITHUB_TOKEN belum diatur.")

        deployer = DeploymentManager(GITHUB_TOKEN, VERCEL_TOKEN)
        await update.message.reply_text(f"🚀 Memulai Deployment GitHub...")
        try:
            repo_url = deployer.create_github_repo(os.path.basename(PROJECT_ROOT))
            deployer.push_to_github(repo_url, PROJECT_ROOT)
            await update.message.reply_text(f"✅ Sukses! Repo: {repo_url}")
        except Exception as e:
            await update.message.reply_text(f"❌ Gagal: {e}")

    async def handle_search_manual(self, update, context):
        user_id = update.effective_user.id
        if not self.is_allowed(user_id): return await update.message.reply_text(f"🚫 Akses ditolak (ID Anda: {user_id})")
        if not context.args: return await update.message.reply_text("💡 Gunakan: /search Query")

        query = " ".join(context.args)
        await update.message.reply_text(f"🔍 Mencari: {query}...")
        try:
            results = self.web_search.get_formatted_string(query)
            await update.message.reply_text(f"✅ **Hasil:**\n\n{results[:4000]}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def handle_message(self, update, context):
        user_id = update.effective_user.id
        if not self.is_allowed(user_id): return
        
        if self.is_processing:
            return await update.message.reply_text("⏳ **Bot Sedang Sibuk:** Harap tunggu hingga tugas sebelumnya selesai atau ketik /stop.")

        text = update.message.text
        # --- AUTO-PROJECT DETECTION ---
        if text.lower().startswith("buat web aplikasi") or text.lower().startswith("buatkan web aplikasi"):
            potential_name = text.split("aplikasi ", 1)[-1].split("\n")[0].strip()
            folder_name = "".join([c if c.isalnum() else "-" for c in potential_name[:30]]).lower().strip("-")
            
            current_project = os.path.basename(PROJECT_ROOT)
            if folder_name and folder_name != current_project:
                await update.message.reply_text(f"🎨 **Intent Proyek Baru Terdeteksi:** {folder_name}")
                context.args = [folder_name]
                await self.handle_new_project(update, context)

        self.is_processing = True
        try:
            await self.orchestrator.process_task(text, update)
        finally:
            self.is_processing = False

    def run(self):
        print("🤖 DarkSky Bot is starting...")
        retry_delay = 5  # Detik awal untuk retry
        
        while True:
            try:
                print(f"📡 Mencoba menghubungkan ke Telegram (Delay: {retry_delay}s jika gagal)...")
                self.app.run_polling(drop_pending_updates=True, close_loop=False) # close_loop=False agar thread tidak mati
                # Jika keluar secara normal, hentikan loop
                break 
            except Exception as e:
                error_msg = str(e).lower()
                print(f"⚠️ [CONNECTION ERROR] Gagal menyambung: {e}")
                
                # Jika error karena token salah, jangan retry terus menerus
                if "unauthorized" in error_msg:
                    print("❌ Error: Token Telegram tidak valid. Menghentikan bot.")
                    break
                
                # Berikan jeda sebelum mencoba lagi
                time.sleep(retry_delay)
                # Exponential backoff (maksimal 60 detik)
                retry_delay = min(retry_delay * 2, 60)
                print(f"🔄 Mencoba menyambung kembali dalam {retry_delay} detik...")
                continue
            finally:
                # Membersihkan file kunci saat bot benar-benar berhenti
                if hasattr(self, 'lock_file') and os.path.exists(self.lock_file):
                    try:
                        os.remove(self.lock_file)
                    except:
                        pass