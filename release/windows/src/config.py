"""
設定ファイル
"""

import os
import sys
from pathlib import Path

# OS判定
IS_WINDOWS = os.name == "nt"

# ベースディレクトリ
# PyInstallerでバンドルされた実行ファイルの場合、sys.frozenが設定される
if getattr(sys, 'frozen', False):
    # 実行ファイル（.exe）のディレクトリを起点とする
    BASE_DIR = Path(sys.executable).parent
else:
    # 開発環境（スクリプト実行時）は従来通り
    BASE_DIR = Path(__file__).parent.parent

# アップロードディレクトリ
# Windows: %LOCALAPPDATA%\GaQ\uploads（書き込み権限が保証される場所）
# macOS/Linux: ~/.gaq/uploads
if IS_WINDOWS:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        UPLOAD_DIR = Path(local_app_data) / "GaQ" / "uploads"
    else:
        # フォールバック: ユーザーホームディレクトリ
        UPLOAD_DIR = Path.home() / ".gaq" / "uploads"
else:
    UPLOAD_DIR = Path.home() / ".gaq" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 許可する音声ファイル形式
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".mp4"}

# アプリケーションバージョン
APP_VERSION = "1.2.7"

# faster-whisperモデル設定
AVAILABLE_MODELS = ["medium", "large-v3"]
DEFAULT_MODEL = "medium"

# サーバー設定
HOST = "127.0.0.1"
PORT = 8000
