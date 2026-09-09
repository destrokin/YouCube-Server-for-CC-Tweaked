@echo off
cd /d "%~dp0"

if exist "YouCubeServer.exe" (
    start "" "YouCubeServer.exe"
    exit /b 0
)

if not exist ".venv\Scripts\python.exe" (
    echo YouCube has not been set up yet.
    echo Running setup first...
    call SETUP_SERVER.bat
)

if exist "YouCubeServer.exe" (
    start "" "YouCubeServer.exe"
    exit /b 0
)

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Setup did not create the Python environment.
    pause
    exit /b 1
)

echo.
echo YouCubeServer.exe is not available.
echo Starting the Python GUI fallback.
echo.
".venv\Scripts\python.exe" "YouCubeServerGUI.py"
