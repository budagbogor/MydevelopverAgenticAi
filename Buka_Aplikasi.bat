@echo off
title DarkSky Agentic AI Developer - Dashboard
echo.
echo  ======================================================
echo     DARKSKY AGENTIC AI DEVELOPER - GUI LAUNCHER
echo  ======================================================
echo.

:: 1. Cek apakah Python terinstal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Pastikan Python terinstal dan ada di PATH.
    pause
    exit /b
)

:: 2. Pastikan dependensi terupdate (Latar Belakang)
echo [1/3] Memeriksa dependensi...
pip install -r requirements.txt --quiet

:: 3. Proteksi Safe Start (Anti-Dual Session)
echo [2/3] Memeriksa sesi bot...
if exist bot.lock (
    echo.
    echo [WARNING] Bot sepertinya sudah berjalan di jendela lain!
    echo Harap tutup jendela bot yang lama terlebih dahulu.
    echo Jika Anda yakin tidak ada bot yang jalan, hapus file "bot.lock".
    echo.
    pause
    exit /b
)

:: 4. Jalankan Dashboard GUI
echo [3/3] Memulai Dashboard Visual...
echo.
python main.py
echo.
echo [INFO] Bot telah berhenti.
pause
