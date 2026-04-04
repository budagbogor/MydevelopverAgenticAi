@echo off
title DarkSky Agentic AI Developer
echo.
echo  ======================================================
echo     DARKSKY AGENTIC AI DEVELOPER - TELEGRAM BOT
echo  ======================================================
echo.

:: Cek apakah Python terinstal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Pastikan Python terinstal dan ada di PATH.
    pause
    exit /b
)

:: Pastikan dependensi terupdate
echo [1/2] Memeriksa dependensi...
pip install -r requirements.txt --quiet

:: Jalankan main.py dengan mode CLI (Langsung Aktif)
echo [2/2] Memulai Bot dalam mode CLI...
echo.
echo [SAFE START] Membersihkan sesi bot lama...
if exist bot.lock del /f /q bot.lock
python main.py --cli
echo.
echo [INFO] Bot telah berhenti.
pause