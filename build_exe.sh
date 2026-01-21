#!/bin/bash

echo "Building Pacman Remastered executable..."
echo ""

# Check if PyInstaller is installed
if ! python -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    python -m pip install pyinstaller
fi

echo ""
echo "Cleaning previous build..."
rm -rf build dist __pycache__

echo ""
echo "Building executable..."
pyinstaller pacman_remastered.spec

echo ""
if [ -f "dist/PacmanRemastered" ] || [ -f "dist/PacmanRemastered.exe" ]; then
    echo "Build successful! Executable is in: dist/"
    ls -lh dist/
else
    echo "Build failed! Check the output above for errors."
    exit 1
fi


