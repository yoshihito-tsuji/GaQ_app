@echo off
REM GaQ Offline Transcriber - Windows build script
REM Requires: Python 3.12.x

echo === GaQ Offline Transcriber - Windows Build ===
echo.

REM 1. Check Python 3.12
echo 1. Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    echo Install Python 3.12.x: https://www.python.org/downloads/release/python-3127/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if "%PYTHON_MAJOR%.%PYTHON_MINOR%" neq "3.12" (
    echo [ERROR] Python 3.12 is required. Detected: %PYTHON_VERSION%
    exit /b 1
)
echo [OK] Python %PYTHON_VERSION%
echo.

REM 2. Ensure venv
echo 2. Ensuring virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [OK] venv ready
echo.

REM 3. Install dependencies
echo 3. Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r src\requirements.txt >nul 2>&1
pip install pyinstaller >nul 2>&1
echo [OK] Dependencies installed
echo.

REM 4. PyInstaller build (artifacts folder)
set DIST_PATH=artifacts\dist
set BUILD_PATH=artifacts\build
if not exist artifacts mkdir artifacts

for /f "tokens=*" %%i in ('pyinstaller --version') do set PYINSTALLER_VERSION=%%i
echo PyInstaller: %PYINSTALLER_VERSION%
echo 4. Building with PyInstaller...

pyinstaller --clean -y --distpath %DIST_PATH% --workpath %BUILD_PATH% GaQ_Transcriber.spec

if %errorlevel% equ 0 (
    echo.
    echo [OK] Build finished.
    echo Output:
    echo   %DIST_PATH%\GaQ_Transcriber\GaQ_Transcriber.exe
    dir %DIST_PATH%\GaQ_Transcriber\GaQ_Transcriber.exe 2>nul
) else (
    echo [ERROR] Build failed.
    exit /b 1
)

echo.
echo === Build complete ===
