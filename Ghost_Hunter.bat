@echo off
title 👻 GHOST HUNTER - DarkSky Agent Recovery
cd /d "%~dp0"

echo.
echo ===================================================
echo   DARK SKY GHOST HUNTER - Nuclear Cleanup Mode
echo ===================================================
echo [!] Melakukan pembersihan total instansi yang menggantung...
echo.

:: 1. Matikan semua Python (Bot utama)
echo [1/4] Mematikan semua Proses Python...
taskkill /F /IM python.exe /T >nul 2>&1

:: 2. Matikan Node dan NPM (Instalasi yang macet)
echo [2/4] Mematikan semua Proses Node & NPM...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM npm.exe /T >nul 2>&1

:: 3. Matikan Trae (IDE yang mungkin lag)
echo [3/4] Mematikan Trae IDE...
taskkill /F /IM Trae.exe /T >nul 2>&1

:: 4. Bersihkan Lock File & Temporary
echo [4/4] Membersihkan residu sistem...
if exist bot.lock del /f /q bot.lock >nul 2>&1
if exist .env.tmp del /f /q .env.tmp >nul 2>&1

echo.
echo ===================================================
echo   ✅ PEMBERSIHAN SELESAI!
echo   Sekarang Anda bisa menjalankan 'Buka_Bot_Telegram.bat'
echo ===================================================
echo.
pause
