@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    call SETUP_SERVER.bat
)

echo Rebuilding YouCubeServer.exe...
".venv\Scripts\python.exe" -m pip install --upgrade pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist YouCubeServer.spec del /q YouCubeServer.spec

".venv\Scripts\python.exe" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name YouCubeServer ^
  YouCubeServerGUI.py

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

copy /y "dist\YouCubeServer.exe" "YouCubeServer.exe" >nul

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist YouCubeServer.spec del /q YouCubeServer.spec

echo.
echo YouCubeServer.exe rebuilt successfully.
echo You can now launch the backend without a command window.
pause
