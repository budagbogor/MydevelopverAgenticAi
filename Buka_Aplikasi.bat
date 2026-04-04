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

:: 2. Proteksi Lock File yang Lebih Ramah (Ghost Lock Handler)
if exist bot.lock (
    echo [!] ALERT: File bot.lock ditemukan. 
    echo Ini terjadi jika bot ditutup paksa atau crash sebelumnya.
    echo.
    set /p choice="Hapus kunci sesi lama dan masuk sekarang? (y/n): "
    if /i "%choice%"=="y" (
        del /f /q bot.lock
        echo [OK] Kunci sesi dibersihkan.
    ) else (
        echo [INFO] Membatalkan peluncuran.
        pause
        exit /b
    )
)

:: 3. Pastikan dependensi terupdate (Latar Belakang)
echo [1/2] Memeriksa dependensi...
pip install -r requirements.txt --quiet

:: 4. Jalankan Dashboard GUI
echo [2/2] Memulai Dashboard Visual...
echo.
python main.py
echo.
echo [INFO] Bot telah berhenti.
pause
