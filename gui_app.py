import flet as ft
import os
import threading
import logging
import time
import sys
from config import (
    TELEGRAM_BOT_TOKEN, SUMOPOD_API_KEY, SUMOPOD_BASE_URL, 
    DEFAULT_MODEL, TARGET_IDE, IDE_PATH, PROJECT_ROOT,
    GITHUB_TOKEN, VERCEL_TOKEN, ALLOWED_TELEGRAM_USER_IDS,
    save_config
)
from utils import set_autostart, is_autostart_enabled
from telegram_bot import TelegramBot

# Konfigurasi Tema yang Lebih Aman untuk Versi Flet Anda
DARK_BG = "black"
DARK_NAV = "#111827"
ACCENT_BLUE = ft.Colors.BLUE
ACCENT_PURPLE = ft.Colors.PURPLE
TEXT_PRIMARY = ft.Colors.WHITE
TEXT_SECONDARY = ft.Colors.GREY_400

class LogHandler(logging.Handler):
    def __init__(self, log_view, page):
        super().__init__()
        self.log_view = log_view
        self.page = page

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_view.controls.append(ft.Text(msg, color=TEXT_PRIMARY, size=12))
            self.page.update()
        except:
            # Sesi GUI hancur atau ditutup, abaikan update log visual
            pass

class DarkSkyApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DarkSky Agentic AI"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = DARK_BG
        self.page.padding = 0
        self.page.window_width = 1100
        self.page.window_height = 750
        self.page.update()
        
        self.bot_thread = None
        self.is_running = False
        
        # Form UI Refs
        self.token_input = ft.TextField(label="Telegram Bot Token", value=TELEGRAM_BOT_TOKEN or "", password=True, can_reveal_password=True, expand=True)
        self.user_id_input = ft.TextField(label="Allowed User ID", value=str(ALLOWED_TELEGRAM_USER_IDS or ""), expand=True)
        self.api_key_input = ft.TextField(label="Sumopod API Key", value=SUMOPOD_API_KEY or "", password=True, can_reveal_password=True, expand=True)
        self.base_url_input = ft.TextField(label="Base URL", value=SUMOPOD_BASE_URL or "", expand=True)
        self.model_input = ft.TextField(label="Model AI", value=DEFAULT_MODEL or "", expand=True)
        self.ide_input = ft.TextField(label="Target IDE", value=TARGET_IDE or "", expand=True)
        self.root_path_input = ft.TextField(label="Project Root Path", value=PROJECT_ROOT or "", expand=True)
        self.github_token_input = ft.TextField(label="GitHub Token", value=GITHUB_TOKEN or "", password=True, can_reveal_password=True, expand=True)
        self.vercel_token_input = ft.TextField(label="Vercel Token", value=VERCEL_TOKEN or "", password=True, can_reveal_password=True, expand=True)
        self.autostart_switch = ft.Switch(label="Start on Windows Boot", value=is_autostart_enabled(), active_color=ACCENT_BLUE)
        
        print("🔧 Initializing DarkSkyApp UI...")
        try:
            self.setup_ui()
            self.setup_logging()
            self.page.update()
            print("✅ UI Setup Complete.")
        except Exception as e:
            print(f"❌ Error during UI Setup: {e}")

    def setup_logging(self):
        handler = LogHandler(self.log_view, self.page)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    def setup_ui(self):
        # Sidebar
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            bgcolor=DARK_NAV,
            destinations=[
                ft.NavigationRailDestination(icon="dashboard", label="Dashboard"),
                ft.NavigationRailDestination(icon="settings", label="Settings"),
                ft.NavigationRailDestination(icon="help_outline", label="Docs"),
            ],
            on_change=self.on_nav_change,
        )

        self.dashboard_view = self.create_dashboard_view()
        self.settings_view = self.create_settings_view()
        self.docs_view = self.create_docs_view()

        # LAYOUT BERSIH: Tanpa penumpukan container yang berlebihan
        self.page.add(
            ft.Row([
                ft.Container(content=self.rail, bgcolor=DARK_NAV, width=110),
                ft.Container(content=self.dashboard_view, expand=True, bgcolor="black", padding=20)
            ], expand=True, spacing=0)
        )
        self.page.update()

    def on_nav_change(self, e):
        idx = e.control.selected_index
        views = [self.dashboard_view, self.settings_view, self.docs_view]
        self.content.content = views[idx]
        self.page.update()

    def create_dashboard_view(self):
        self.status_icon = ft.Icon("circle", color="red", size=14)
        self.status_text = ft.Text("OFFLINE", color=TEXT_SECONDARY, weight=ft.FontWeight.BOLD)
        self.log_view = ft.ListView(expand=True, spacing=5, auto_scroll=True)
        self.start_btn = ft.ElevatedButton(
            "ACTIVATE BOT", 
            icon="power_settings_new", 
            bgcolor="blue", 
            color="white",
            on_click=self.toggle_bot,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )

        return ft.Column([
            self.start_btn, # TOMBOL SEKARANG DI PALING ATAS
            ft.Text("DarkSky | Agent Dashboard", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Row([self.status_icon, self.status_text], spacing=8),
            ft.Container(
                content=self.log_view,
                expand=True,
                bgcolor="black",
                padding=10,
            )
        ], expand=True)

    def create_settings_view(self):
        return ft.Column([
            ft.Text("Configuration Hub", size=28, weight=ft.FontWeight.BOLD, color=ACCENT_PURPLE),
            ft.Text("Manage your tokens and system preferences", color=TEXT_SECONDARY),
            ft.Divider(height=30, color=ft.Colors.WHITE12),
            ft.Row([self.token_input, self.user_id_input]),
            ft.Row([self.api_key_input, self.base_url_input]),
            ft.Row([self.model_input, self.ide_input]),
            self.root_path_input,
            ft.Row([self.github_token_input, self.vercel_token_input]),
            ft.Divider(height=30, color=ft.Colors.WHITE12),
            ft.Row([
                self.autostart_switch,
                ft.ElevatedButton("SAVE CHANGES", icon="save", bgcolor=ACCENT_PURPLE, color=ft.Colors.WHITE, on_click=self.handle_save)
            ])
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def create_docs_view(self):
        return ft.Column([
            ft.Text("Documentation & Guides", size=28, weight=ft.FontWeight.BOLD, color=ACCENT_BLUE),
            ft.Divider(height=20, color=ft.Colors.WHITE12),
            ft.Markdown(
                """
### 🔧 Prasyarat Sistem
Aplikasi ini membutuhkan beberapa software terinstal agar fitur otonom berjalan lancar:
1. **Trae IDE**: Editor utama yang dikendalikan bot.
2. **Git**: Diperlukan untuk push kode ke GitHub.
3. **Vercel CLI**: Diperlukan untuk deployment otomatis.
4. **Chrome/Edge**: Untuk riset web otomatis.

### 🔑 Cara Mengisi Konfigurasi
* **Telegram Token**: Dapatkan dari BotFather.
* **Allowed User ID**: ID Telegram Anda (gunakan bot `@userinfobot` untuk cek).
* **API Key**: Gunakan kunci API dari penyedia LLM Anda (OpenAI/Sumopod/Gemini).
* **GitHub Token**: TOKEN PAT (Personal Access Token) dengan hak akses repo.
* **Vercel Token**: Didapatkan dari Dashboard Vercel > Settings > Tokens.
                """,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def handle_save(self, e):
        updates = {
            "TELEGRAM_BOT_TOKEN": self.token_input.value,
            "ALLOWED_TELEGRAM_USER_IDS": self.user_id_input.value,
            "SUMOPOD_API_KEY": self.api_key_input.value,
            "SUMOPOD_BASE_URL": self.base_url_input.value,
            "DEFAULT_MODEL": self.model_input.value,
            "TARGET_IDE": self.ide_input.value,
            "PROJECT_ROOT": self.root_path_input.value,
            "GITHUB_TOKEN": self.github_token_input.value,
            "VERCEL_TOKEN": self.vercel_token_input.value,
        }
        
        success = save_config(updates)
        success_auto, msg_auto = set_autostart(self.autostart_switch.value)
        
        if success:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Settings Saved! {msg_auto}"), bgcolor=ACCENT_BLUE)
            self.page.snack_bar.open = True
            logging.info("💾 Konfigurasi diperbarui oleh pengguna.")
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Failed to save settings."), bgcolor=ft.Colors.RED_ACCENT)
            self.page.snack_bar.open = True
        self.page.update()

    def toggle_bot(self, e):
        if not self.is_running:
            self.start_bot()
        else:
            logging.warning("⚠️ Untuk menghentikan bot, tutup aplikasi atau matikan proses manual.")

    def start_bot(self):
        if not TELEGRAM_BOT_TOKEN:
            logging.error("❌ Token Telegram kosong. Harap isi di menu Settings.")
            return

        self.is_running = True
        self.status_icon.color = ft.Colors.GREEN_400
        self.status_text.value = "ONLINE"
        self.status_text.color = ft.Colors.GREEN_400
        self.start_btn.text = "BOT IS ACTIVE"
        self.start_btn.disabled = True
        self.page.update()

        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()

    def run_bot(self):
        try:
            bot = TelegramBot(TELEGRAM_BOT_TOKEN)
            bot.run()
        except Exception as ex:
            logging.error(f"🚨 Bot Fatal Error: {str(ex)}")
            self.status_icon.color = ft.Colors.RED_ACCENT
            self.status_text.value = "CRASHED"
            self.status_text.color = ft.Colors.RED_ACCENT
            self.start_btn.disabled = False
            self.start_btn.text = "RESTART BOT"
            self.is_running = False
            self.page.update()

def main_launcher(page: ft.Page):
    DarkSkyApp(page)

if __name__ == "__main__":
    ft.app(target=main_launcher)
