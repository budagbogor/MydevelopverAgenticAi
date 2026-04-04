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
echo [1/2] Memeriksa dependensi...
pip install -r requirements.txt --quiet

:: 3. Jalankan Dashboard GUI
echo [2/2] Memulai Dashboard Visual...
echo.
python main.py
echo.
echo [INFO] Bot telah berhenti.
pause
