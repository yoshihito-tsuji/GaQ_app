@echo off
REM GaQ Offline Transcriber - Windows版ビルドスクリプト
REM Python 3.12系を使用してビルドを実行します

echo === GaQ Offline Transcriber - Windows版ビルド ===
echo.

REM Python 3.12の確認
echo 1. Pythonバージョン確認...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Pythonが見つかりません
    echo Python 3.12.x をインストールしてください:
    echo   https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if "%PYTHON_MAJOR%.%PYTHON_MINOR%" neq "3.12" (
    echo [エラー] Python 3.12が必要ですが、Python %PYTHON_VERSION% が見つかりました
    echo.
    echo Python 3.12.x をインストールしてください:
    echo   https://www.python.org/downloads/release/python-3127/
    exit /b 1
)

echo [OK] Python %PYTHON_VERSION% を使用します
echo.

REM 仮想環境の確認と作成
echo 2. 仮想環境の確認...
if not exist venv (
    echo 仮想環境を作成中...
    python -m venv venv
    echo [OK] 仮想環境を作成しました
) else (
    echo [OK] 既存の仮想環境を使用します
)
echo.

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM 依存パッケージのインストール
echo 3. 依存パッケージのインストール...
python -m pip install --upgrade pip >nul 2>&1
pip install -r src\requirements.txt >nul 2>&1
pip install pyinstaller >nul 2>&1
echo [OK] 依存パッケージをインストールしました
echo.

REM PyInstallerバージョン確認
for /f "tokens=*" %%i in ('pyinstaller --version') do set PYINSTALLER_VERSION=%%i
echo PyInstaller: %PYINSTALLER_VERSION%
echo.

REM ビルド実行
echo 4. PyInstallerでビルド実行...
pyinstaller --clean -y GaQ_Transcriber.spec

if %errorlevel% equ 0 (
    echo.
    echo [OK] ビルドが成功しました！
    echo.
    echo 成果物:
    echo   dist\GaQ_Transcriber\GaQ_Transcriber.exe
    dir dist\GaQ_Transcriber\GaQ_Transcriber.exe 2>nul
) else (
    echo [エラー] ビルドに失敗しました
    exit /b 1
)

echo.
echo === ビルド完了 ===
