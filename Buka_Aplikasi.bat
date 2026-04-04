echo.
echo [SAFE START] Memeriksa sesi bot...
if exist bot.lock (
    echo.
    echo [WARNING] Bot sepertinya sudah berjalan di jendela lain!
    echo Harap tutup jendela bot yang lama terlebih dahulu.
    echo.
    pause
    exit
)
python main.py
echo.
pause
