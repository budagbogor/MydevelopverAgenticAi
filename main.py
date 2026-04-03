import flet as ft
from gui_app import main_launcher
import logging

def main():
    # Setup logging awal agar bisa ditangkap oleh GUI
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    print("🌌 Starting DarkSky Desktop Engine...")
    ft.app(target=main_launcher)

if __name__ == '__main__':
    main()