@echo off
echo Building Pacman Remastered executable...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

echo.
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Building executable...
pyinstaller pacman_remastered.spec

echo.
if exist dist\PacmanRemastered.exe (
    echo Build successful! Executable is in: dist\PacmanRemastered.exe
) else (
    echo Build failed! Check the output above for errors.
)

pause


