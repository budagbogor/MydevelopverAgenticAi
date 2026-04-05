@echo off
title DarkSky Agentic AI Developer - Telegram Bot Mode
setlocal enabledelayedexpansion

:: AGAR BISA DIJALANKAN SEBAGAI ADMINISTRATOR 
:: (Pindah ke folder lokasi script ini berada)
cd /d "%~dp0"

echo.
echo  ======================================================
echo     DARKSKY AGENTIC AI DEVELOPER - TELEGRAM BOT MODE
echo  ======================================================
echo.

:: 1. Cek apakah Python terinstal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Pastikan Python terinstal dan ada di PATH.
    pause
    exit /b
)

:: 2. Proteksi Lock File
if exist bot.lock (
    echo [!] ALERT: File bot.lock ditemukan. 
    echo Ini terjadi jika bot ditutup paksa atau crash sebelumnya.
    echo.
    echo Menghapus kunci sesi lama dan masuk sekarang...
    del /f /q bot.lock
    echo [OK] Kunci sesi dibersihkan.
)

:: 3. Pastikan dependensi terupdate (Latar Belakang)
echo [1/2] Memeriksa dependensi (PyYAML, dll)...
pip install -r requirements.txt --quiet

:: 4. Jalankan Bot Telegram Mode CLI
echo [2/2] Memulai Bot Telegram (Otonom)...
echo.
echo Tips: Kirim pesan lewat Telegram untuk memulai misi Swarm Intelligence!
echo.
python main.py --cli
echo.
echo [INFO] Bot telah berhenti.
pause
