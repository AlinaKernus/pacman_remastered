"""
Runtime hook for PyInstaller to fix paths in exe
This runs before main.py, so we can set up paths correctly
"""
import sys
import os

# PyInstaller creates a temp folder and stores path in _MEIPASS
if getattr(sys, 'frozen', False):
    # Running in a bundle (exe)
    # sys._MEIPASS is the temporary folder where PyInstaller extracts files
    BASE_DIR = sys._MEIPASS
    # Change working directory to BASE_DIR so relative paths work
    os.chdir(BASE_DIR)
else:
    # Running in normal Python environment
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set BASE_DIR as environment variable so all modules can use it
os.environ['GAME_BASE_DIR'] = BASE_DIR

# Also add pac-man-1 to path if it exists
PACMAN1_DIR = os.path.join(BASE_DIR, 'pac-man-1')
if os.path.exists(PACMAN1_DIR):
    sys.path.insert(0, PACMAN1_DIR)
    # Also change to pac-man-1 directory for relative paths in GameScene
    # This will be restored by singleplayer.py code

