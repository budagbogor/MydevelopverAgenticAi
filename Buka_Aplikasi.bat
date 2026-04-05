@echo off
title DarkSky Agentic AI Developer - Dashboard
setlocal enabledelayedexpansion

:: AGAR BISA DIJALANKAN SEBAGAI ADMINISTRATOR 
:: (Pindah ke folder lokasi script ini berada)
cd /d "%~dp0"

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

:: 2. Proteksi Lock File dengan Command CHOICE (Lebih Stabil)
if exist bot.lock (
    echo [!] ALERT: File bot.lock ditemukan. 
    echo Ini terjadi jika bot ditutup paksa atau crash sebelumnya.
    echo.
    echo [y] Hapus kunci sesi lama dan masuk sekarang.
    echo [n] Batalkan peluncuran.
    echo.
    choice /c yn /n /m "Pilihan Anda (y/n): "
    
    if errorlevel 2 (
        echo [INFO] Membatalkan peluncuran.
        pause
        exit /b
    )
    
    if errorlevel 1 (
        del /f /q bot.lock
        echo [OK] Kunci sesi dibersihkan.
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
