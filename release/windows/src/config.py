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


def get_app_data_dir() -> Path:
    """
    アプリケーションデータディレクトリを取得

    Windows: %LOCALAPPDATA%\GaQ
    macOS/Linux: ~/.gaq

    OneDriveリダイレクトの影響を受けないパスを使用

    Returns:
        Path: アプリケーションデータディレクトリ
    """
    if IS_WINDOWS:
        # LOCALAPPDATA を優先（OneDriveリダイレクトの影響を受けない）
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            app_dir = Path(local_app_data) / "GaQ"
        else:
            # フォールバック: ユーザープロファイル配下
            app_dir = Path.home() / "AppData" / "Local" / "GaQ"
    else:
        # macOS/Linux: ~/.gaq
        app_dir = Path.home() / ".gaq"

    return app_dir


def verify_write_permission(directory: Path) -> bool:
    """
    ディレクトリへの書き込み権限を確認

    Args:
        directory: 確認するディレクトリ

    Returns:
        bool: 書き込み可能な場合True
    """
    try:
        # ディレクトリが存在しない場合は作成を試みる
        directory.mkdir(parents=True, exist_ok=True)

        # テストファイルを書き込んで削除
        test_file = directory / ".write_test"
        test_file.write_text("test", encoding="utf-8")
        test_file.unlink()
        return True
    except (OSError, IOError, PermissionError):
        return False


def get_upload_dir() -> Path:
    """
    アップロードディレクトリを取得（書き込み権限を確認）

    優先順位:
    1. EXE隣接ディレクトリ
    2. LOCALAPPDATA配下
    3. TEMP配下（最終フォールバック）

    Returns:
        Path: アップロードディレクトリ
    """
    # 優先: EXE隣接ディレクトリ
    primary_dir = BASE_DIR / "uploads"
    if verify_write_permission(primary_dir):
        return primary_dir

    # フォールバック1: LOCALAPPDATA配下
    app_data_dir = get_app_data_dir() / "uploads"
    if verify_write_permission(app_data_dir):
        return app_data_dir

    # フォールバック2: TEMP配下
    if IS_WINDOWS:
        temp_dir = Path(os.environ.get("TEMP", os.environ.get("TMP", "C:\\Temp"))) / "GaQ" / "uploads"
    else:
        temp_dir = Path("/tmp") / "gaq" / "uploads"

    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


# アップロードディレクトリ（書き込み権限を確認してフォールバック）
UPLOAD_DIR = get_upload_dir()

# ログディレクトリ
LOG_DIR = get_app_data_dir() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# モデルキャッシュディレクトリ（HuggingFace標準パスを使用、環境変数で上書き可能）
def get_model_cache_dir() -> Path:
    """
    モデルキャッシュディレクトリを取得

    環境変数 HF_HOME または HF_HUB_CACHE が設定されている場合はそれを使用
    """
    # 環境変数チェック
    hf_cache = os.environ.get("HF_HUB_CACHE") or os.environ.get("HF_HOME")
    if hf_cache:
        return Path(hf_cache)

    # デフォルト: ~/.cache/huggingface/hub
    return Path.home() / ".cache" / "huggingface" / "hub"


MODEL_CACHE_DIR = get_model_cache_dir()

# 許可する音声ファイル形式
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".mp4"}

# アプリケーションバージョン
APP_VERSION = "1.2.3"

# faster-whisperモデル設定
AVAILABLE_MODELS = ["medium", "large-v3"]
DEFAULT_MODEL = "medium"

# サーバー設定
HOST = "127.0.0.1"
PORT = 8000
