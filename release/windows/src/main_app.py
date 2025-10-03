"""
GaQ Offline Transcriber - ネイティブアプリ版メインエントリーポイント
pywebview + FastAPI によるオフライン文字起こしアプリ
"""

import logging
import multiprocessing
import os
import sys
import threading
import time
from pathlib import Path

import requests
import uvicorn
import webview

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def is_server_ready(host: str = "127.0.0.1", port: int = 8000, timeout: int = 30) -> bool:
    """
    FastAPIサーバーが起動しているか確認

    Args:
        host: ホスト名
        port: ポート番号
        timeout: タイムアウト時間（秒）

    Returns:
        サーバーが起動していればTrue
    """
    url = f"http://{host}:{port}/health"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                logger.info(f"✅ FastAPIサーバー起動確認: {url}")
                return True
        except requests.exceptions.RequestException:
            # サーバーがまだ起動していない
            time.sleep(0.5)

    logger.error(f"❌ FastAPIサーバー起動タイムアウト: {url}")
    return False


def run_fastapi_server(host: str = "127.0.0.1", port: int = 8000):
    """
    FastAPIサーバーを起動（別スレッドで実行）

    Args:
        host: ホスト名
        port: ポート番号
    """
    try:
        # main.pyをインポート（FastAPIアプリケーション）
        from main import app

        logger.info(f"🚀 FastAPIサーバー起動: http://{host}:{port}")

        # uvicornでサーバーを起動（リロードなし）
        uvicorn.run(app, host=host, port=port, log_level="warning")

    except Exception as e:
        logger.error(f"❌ FastAPIサーバー起動エラー: {e}", exc_info=True)
        sys.exit(1)


def create_webview_window(host: str = "127.0.0.1", port: int = 8000):
    """
    pywebviewウィンドウを作成

    Args:
        host: ホスト名
        port: ポート番号
    """
    url = f"http://{host}:{port}"

    # サーバー起動を待機
    if not is_server_ready(host, port):
        logger.error("FastAPIサーバーが起動しませんでした")
        sys.exit(1)

    # アイコンファイルのパス（存在すれば設定）
    icon_path = Path(__file__).parent / "icon.png"
    icon = str(icon_path) if icon_path.exists() else None

    # Webviewウィンドウを作成
    logger.info(f"🖥️ Webviewウィンドウ起動: {url}")
    window = webview.create_window(
        title="GaQ Offline Transcriber",
        url=url,
        width=800,
        height=900,
        resizable=True,
        frameless=False,  # タイトルバーを表示
        easy_drag=True,  # ドラッグ可能
    )

    # Webviewを起動（メインスレッド）
    webview.start(debug=False)


def main():
    """
    アプリケーションのメインエントリーポイント
    """
    logger.info("=== GaQ Offline Transcriber 起動 ===")

    # Windows の multiprocessing 対応
    if sys.platform == "win32":
        multiprocessing.freeze_support()

    # FastAPIサーバーを別スレッドで起動
    server_thread = threading.Thread(
        target=run_fastapi_server, args=("127.0.0.1", 8000), daemon=True
    )
    server_thread.start()

    # Webviewウィンドウを作成（メインスレッド）
    create_webview_window("127.0.0.1", 8000)

    logger.info("=== GaQ Offline Transcriber 終了 ===")


if __name__ == "__main__":
    main()
