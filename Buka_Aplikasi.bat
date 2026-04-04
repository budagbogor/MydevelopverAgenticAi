echo.
echo [SAFE START] Membersihkan SEMUA sesi bot lama (Hard Reset)...
taskkill /F /IM python.exe /T >nul 2>&1
if exist bot.lock del /f /q bot.lock
python main.py
echo.
pause
