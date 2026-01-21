"""
Helper module for getting correct paths in both development and exe environments
"""
import sys
import os

def get_base_dir():
    """Get the base directory of the game, works in both dev and exe"""
    if getattr(sys, 'frozen', False):
        # Running in a bundle (exe)
        return sys._MEIPASS
    else:
        # Running in normal Python environment
        # Go up from src/utils to project root
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_resource_path(relative_path):
    """Get absolute path to resource, works in both dev and exe"""
    base_dir = get_base_dir()
    return os.path.join(base_dir, relative_path)


