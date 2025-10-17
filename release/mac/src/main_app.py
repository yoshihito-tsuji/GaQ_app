"""
GaQ Offline Transcriber - ネイティブアプリ版メインエントリーポイント
pywebview + FastAPI によるオフライン文字起こしアプリ
"""

import atexit
import fcntl
import json
import logging
import multiprocessing
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import requests
import uvicorn
import webview

from config import APP_VERSION

# ロックファイルのパス
LOCK_FILE = "/tmp/gaq_transcriber.lock"
lock_file_handle = None

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def acquire_single_instance_lock():
    """
    単一インスタンス保証: 排他ロックを取得

    Returns:
        bool: ロック取得に成功したらTrue、失敗したらFalse
    """
    global lock_file_handle

    try:
        # ロックファイルを開く（存在しなければ作成）
        lock_file_handle = open(LOCK_FILE, 'w')

        # 非ブロッキングで排他ロックを試みる
        fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        # ロック成功時、PIDを記録
        lock_file_handle.write(str(os.getpid()))
        lock_file_handle.flush()

        logger.info(f"✅ 単一インスタンスロック取得成功 (PID: {os.getpid()})")

        # プロセス終了時にロックを解放
        atexit.register(release_single_instance_lock)

        return True

    except IOError:
        # ロック失敗 = 既に別のインスタンスが起動中
        logger.warning(f"⚠️ 別のインスタンスが既に起動しています (ロックファイル: {LOCK_FILE})")

        if lock_file_handle:
            lock_file_handle.close()
            lock_file_handle = None

        return False


def release_single_instance_lock():
    """
    単一インスタンスロックを解放
    """
    global lock_file_handle

    if lock_file_handle:
        try:
            fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_UN)
            lock_file_handle.close()
            logger.info("🔓 単一インスタンスロック解放")
        except Exception as e:
            logger.error(f"ロック解放エラー: {e}")
        finally:
            lock_file_handle = None


def show_already_running_dialog():
    """
    既に起動中である旨をユーザーに通知（macOS用）
    """
    try:
        # osascriptでダイアログ表示
        script = '''
        display dialog "GaQ Offline Transcriber は既に起動しています。\\n\\n既存のウィンドウを確認してください。" ¬
            with title "GaQ Offline Transcriber" ¬
            buttons {"OK"} ¬
            default button "OK" ¬
            with icon caution
        '''
        subprocess.run(['osascript', '-e', script], check=False, timeout=5)
    except Exception as e:
        logger.error(f"ダイアログ表示エラー: {e}")


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

    except OSError as e:
        if e.errno == 48:  # Address already in use
            logger.error(f"❌ ポート {port} は既に使用されています (Errno 48)")
            logger.error("   別のGaQインスタンスまたは他のアプリケーションがポートを使用中です")
        else:
            logger.error(f"❌ FastAPIサーバー起動エラー (OSError): {e}", exc_info=True)
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ FastAPIサーバー起動エラー: {e}", exc_info=True)
        sys.exit(1)


class Bridge:
    """
    JavaScript <-> Python ブリッジ
    pywebview の js_api として使用
    """

    def log_message(self, level: str, message: str):
        """
        JavaScriptからのログメッセージをPython側に転送

        Args:
            level: ログレベル (info, warning, error, debug)
            message: ログメッセージ

        Returns:
            dict: {"success": bool}
        """
        try:
            level = level.lower()
            if level == "info":
                logger.info(f"[JS] {message}")
            elif level == "warning":
                logger.warning(f"[JS] {message}")
            elif level == "error":
                logger.error(f"[JS] {message}")
            elif level == "debug":
                logger.debug(f"[JS] {message}")
            else:
                logger.info(f"[JS] {message}")

            return {"success": True}

        except Exception as e:
            logger.error(f"❌ log_message エラー: {e}", exc_info=True)
            return {"success": False}

    def save_transcription(self):
        """
        文字起こし結果をファイルに保存

        Returns:
            dict: {"success": bool, "message": str, "path": str|null}
        """
        try:
            # FastAPI の /last-transcription から結果を取得
            response = requests.get("http://127.0.0.1:8000/last-transcription", timeout=5)

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": "文字起こし結果の取得に失敗しました",
                    "path": None
                }

            data = response.json()
            text = data.get("text", "")

            if not text:
                return {
                    "success": False,
                    "message": "保存する文字起こし結果がありません",
                    "path": None
                }

            # ファイル保存ダイアログを表示
            file_types = ('Text Files (*.txt)', )
            save_path = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=f'transcription_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                file_types=file_types
            )

            # ユーザーがキャンセルした場合
            if not save_path:
                return {
                    "success": False,
                    "message": "キャンセルされました",
                    "path": None,
                    "cancelled": True
                }

            # ファイルに書き込み
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

            logger.info(f"📥 文字起こし結果保存: {save_path} ({len(text)}文字)")

            return {
                "success": True,
                "message": f"保存しました: {Path(save_path).name}",
                "path": save_path
            }

        except Exception as e:
            logger.error(f"❌ 保存エラー: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"保存に失敗しました: {str(e)}",
                "path": None
            }

    def select_audio_file(self):
        """
        音声ファイル選択ダイアログを表示（pywebview用）

        Returns:
            dict: {"success": bool, "path": str|None, "name": str|None, "cancelled": bool|None}
        """
        try:
            # ファイル選択ダイアログを表示
            file_types = (
                'Audio Files (*.mp3;*.wav;*.m4a;*.flac;*.ogg;*.aac;*.wma)',
                'Video Files (*.mp4;*.mov;*.avi;*.mkv;*.wmv;*.flv)',
                'All Files (*.*)'
            )

            file_path = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=file_types
            )

            logger.debug(f"create_file_dialog returned: {file_path} (type: {type(file_path)})")

            # ユーザーがキャンセルした場合
            if not file_path:
                logger.info("📂 ファイル選択: キャンセル")
                return {
                    "success": False,
                    "path": None,
                    "name": None,
                    "cancelled": True
                }

            # file_pathがシーケンスの場合は最初の要素を取得（pywebviewはリストを返すことがある）
            if isinstance(file_path, (tuple, list)):
                file_path = file_path[0] if file_path else None

            if file_path:
                file_path = os.fspath(file_path)

            if not file_path:
                return {
                    "success": False,
                    "path": None,
                    "name": None,
                    "cancelled": True
                }

            file_name = os.path.basename(file_path)
            logger.info(f"📂 ファイル選択: {file_name} ({file_path})")

            return {
                "success": True,
                "path": file_path,
                "name": file_name
            }

        except Exception as e:
            logger.error(f"❌ ファイル選択エラー: {e}", exc_info=True)
            return {
                "success": False,
                "path": None,
                "name": None,
                "error": str(e)
            }

    def upload_audio_file(self, file_path):
        """
        選択された音声ファイルをFastAPIサーバーにアップロード（pywebview用）

        Args:
            file_path: アップロードするファイルのパス

        Returns:
            dict: {"success": bool, "file_id": str|None, "message": str}
        """
        try:
            # ファイルの存在確認
            if not os.path.exists(file_path):
                logger.error(f"❌ ファイルが見つかりません: {file_path}")
                return {
                    "success": False,
                    "file_id": None,
                    "message": "ファイルが見つかりません"
                }

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            logger.info(f"📤 アップロード開始: {file_name} ({file_size} bytes)")

            # FastAPIの /upload エンドポイントにPOST
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                response = requests.post(
                    "http://127.0.0.1:8000/upload",
                    files=files,
                    timeout=30
                )

            # レスポンスを確認
            if response.status_code == 200:
                data = response.json()
                file_id = data.get('file_id')
                logger.info(f"✅ アップロード成功: {file_name} (file_id: {file_id})")
                return {
                    "success": True,
                    "file_id": file_id,
                    "message": "アップロード成功"
                }
            else:
                logger.error(f"❌ アップロード失敗: HTTP {response.status_code}")
                return {
                    "success": False,
                    "file_id": None,
                    "message": f"アップロード失敗: HTTP {response.status_code}"
                }

        except requests.exceptions.Timeout:
            logger.error(f"❌ アップロードタイムアウト: {file_path}")
            return {
                "success": False,
                "file_id": None,
                "message": "アップロードがタイムアウトしました"
            }
        except Exception as e:
            logger.error(f"❌ アップロードエラー: {e}", exc_info=True)
            return {
                "success": False,
                "file_id": None,
                "message": f"エラー: {str(e)}"
            }


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

    # JSブリッジを作成
    bridge = Bridge()

    # Webviewウィンドウを作成
    logger.info(f"🖥️ Webviewウィンドウ起動: {url}")
    window = webview.create_window(
        title=f"GaQ Offline Transcriber {APP_VERSION}",
        url=url,
        width=800,
        height=900,
        resizable=True,
        frameless=False,  # タイトルバーを表示
        easy_drag=True,  # ドラッグ可能
        js_api=bridge,  # JSブリッジを登録
    )

    def setup_console_hook():
        """
        コンソールログをPython側にブリッジするJSコードを注入
        """
        try:
            # console.log/error/warn をフックしてPython側に転送
            hook_script = """
            (function() {
                // オリジナルのconsoleメソッドを保存
                var originalLog = console.log;
                var originalError = console.error;
                var originalWarn = console.warn;

                // console.log をフック
                console.log = function() {
                    var message = Array.prototype.slice.call(arguments).map(function(arg) {
                        return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
                    }).join(' ');

                    originalLog.apply(console, arguments);

                    if (window.pywebview && window.pywebview.api && window.pywebview.api.log_message) {
                        window.pywebview.api.log_message('info', message);
                    }
                };

                // console.error をフック
                console.error = function() {
                    var message = Array.prototype.slice.call(arguments).map(function(arg) {
                        return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
                    }).join(' ');

                    originalError.apply(console, arguments);

                    if (window.pywebview && window.pywebview.api && window.pywebview.api.log_message) {
                        window.pywebview.api.log_message('error', message);
                    }
                };

                // console.warn をフック
                console.warn = function() {
                    var message = Array.prototype.slice.call(arguments).map(function(arg) {
                        return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
                    }).join(' ');

                    originalWarn.apply(console, arguments);

                    if (window.pywebview && window.pywebview.api && window.pywebview.api.log_message) {
                        window.pywebview.api.log_message('warning', message);
                    }
                };

                console.log('✅ Console hook installed - JS logs will be forwarded to Python');
            })();
            """
            window.evaluate_js(hook_script)
            logger.info("✅ コンソールログフック設定完了")
        except Exception as e:
            logger.error(f"❌ コンソールログフック設定エラー: {e}", exc_info=True)

    # Webview起動後にコンソールフックを設定
    window.events.loaded += setup_console_hook

    # Webviewを起動（メインスレッド）
    webview.start(debug=False)


def main():
    """
    アプリケーションのメインエントリーポイント
    """
    logger.info(f"=== GaQ Offline Transcriber {APP_VERSION} 起動 ===")

    # 単一インスタンスチェック
    if not acquire_single_instance_lock():
        # 既に起動中の場合
        show_already_running_dialog()
        logger.warning("=== 既存インスタンスが起動中のため終了します ===")
        sys.exit(0)

    # macOS の multiprocessing 対応
    if sys.platform == "darwin":
        multiprocessing.set_start_method("spawn", force=True)

    # FastAPIサーバーを別スレッドで起動
    server_thread = threading.Thread(
        target=run_fastapi_server, args=("127.0.0.1", 8000), daemon=True
    )
    server_thread.start()

    # Webviewウィンドウを作成（メインスレッド）
    create_webview_window("127.0.0.1", 8000)

    logger.info(f"=== GaQ Offline Transcriber {APP_VERSION} 終了 ===")


if __name__ == "__main__":
    main()
