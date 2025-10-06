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
    icon_path = Path(__file__).parent / "icon.ico"
    icon = str(icon_path) if icon_path.exists() else None

    # Webviewウィンドウを作成
    logger.info(f"🖥️ Webviewウィンドウ起動: {url}")

    # pywebviewのバージョンによってはiconパラメータが使えないため、
    # まずウィンドウを作成してから、後でアイコンを設定する
    window = webview.create_window(
        title="GaQ Offline Transcriber v1.1.0",
        url=url,
        width=800,
        height=900,
        resizable=True,
        frameless=False,  # タイトルバーを表示
        easy_drag=True,  # ドラッグ可能
        js_api=Api(),  # JavaScript APIを公開
    )

    # Webviewを起動（メインスレッド）
    # 本番ビルド: デバッグモードを無効化（開発者ツールを非表示）
    webview.start(debug=False)


class Api:
    """pywebview JavaScript API"""

    def save_file(self, content, default_filename):
        """
        ファイル保存ダイアログを表示してファイルを保存

        Args:
            content: 保存する内容
            default_filename: デフォルトのファイル名

        Returns:
            dict: {'success': bool, 'path': str or None, 'message': str}
        """
        try:
            # ファイル保存ダイアログを表示
            file_path = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_filename,
                file_types=("Text Files (*.txt)",),
            )

            if file_path:
                # ファイルパスがタプルで返される場合があるので、最初の要素を取得
                if isinstance(file_path, tuple):
                    file_path = file_path[0]

                # ファイルに書き込み
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                logger.info(f"✅ ファイルを保存しました: {file_path}")
                return {
                    "success": True,
                    "path": str(file_path),
                    "message": "ファイルを保存しました",
                }
            else:
                logger.info("ℹ️ ファイル保存がキャンセルされました")
                return {
                    "success": False,
                    "path": None,
                    "message": "キャンセルされました",
                }

        except Exception as e:
            logger.error(f"❌ ファイル保存エラー: {e}")
            return {
                "success": False,
                "path": None,
                "message": f"保存エラー: {str(e)}",
            }


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
