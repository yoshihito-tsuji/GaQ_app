"""
設定ファイル
"""

from pathlib import Path

# ベースディレクトリ
BASE_DIR = Path(__file__).parent.parent

# アップロードディレクトリ
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 許可する音声ファイル形式
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".mp4"}

# faster-whisperモデル設定
AVAILABLE_MODELS = ["medium", "large-v3"]
DEFAULT_MODEL = "medium"

# サーバー設定
HOST = "127.0.0.1"
PORT = 8000
