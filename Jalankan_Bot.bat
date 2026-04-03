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

:: Jalankan main.py
echo [2/2] Memulai Bot...
echo.
python main.py
echo.
echo [INFO] Bot telah berhenti.
pause