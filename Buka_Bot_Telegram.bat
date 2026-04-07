@echo off
title DarkSky Agentic AI Developer - Telegram Bot Mode
setlocal enabledelayedexpansion

:: AGAR BISA DIJALANKAN SEBAGAI ADMINISTRATOR 
:: (Pindah ke folder lokasi script ini berada)
cd /d "%~dp0"

echo.

:: 0. Force Cleanup All Possible Python Bot Instances
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*main.py --cli*' } | Stop-Process -Force"
timeout /t 2 /nobreak >nul

if exist bot.lock del /f /q bot.lock >nul 2>&1

:: 1. Cek apakah Python terinstal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Pastikan Python terinstal dan ada di PATH.
    pause
    exit /b
)

:: 2. Proteksi & Pembersihan Instansi Lama (Conflict Protection)
if exist bot.lock (
    echo [!] ALERT: File bot.lock ditemukan. 
    echo Mencoba membersihkan instansi bot yang masih menggantung...
    
    :: Gunakan PowerShell untuk mencari dan mematikan proses python yang menjalankan main.py
    powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*main.py --cli*' } | Stop-Process -Force"
    
    del /f /q bot.lock >nul 2>&1
    echo [OK] Instansi lama dibersihkan.
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
