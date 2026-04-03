@echo off
echo 🌌 DarkSky Desktop Builder - Powered by PyInstaller
echo ===================================================
echo.
echo [1/3] Menyiapkan dependensi...
pip install flet pyinstaller winshell pypiwin32 > nul

echo [2/3] Memulai proses pemaketan (packaging)...
echo Ini mungkin memakan waktu beberapa menit. Silakan tunggu.
pyinstaller --noconfirm --onedir --windowed ^
    --add-data ".env;." ^
    --add-data "lightning_memory.json;." ^
    --hidden-import "flet" ^
    --name "DarkSkyAgent" ^
    "main.py"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [3/3] SELESAI!
    echo Aplikasi Anda ada di folder: dist\DarkSkyAgent\DarkSkyAgent.exe
    echo Jangan lupa sertakan file .env dan data memori di folder yang sama.
) else (
    echo.
    echo ❌ Gagal melakukan build. Periksa pesan kesalahan di atas.
)
pause
