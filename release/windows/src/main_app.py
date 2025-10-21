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

# ログディレクトリ
custom_log_dir = os.environ.get("GAQ_LOG_DIR")
if custom_log_dir:
    LOG_DIR = Path(custom_log_dir)
else:
    LOG_DIR = Path.home() / ".gaq" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

# ログ設定（ファイルとコンソールの両方に出力）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPIサーバープロセスのグローバル参照（終了時に使用）
server_process = None


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
        display alert "お知らせ" message "GaQ Offline Transcriber は既に起動しています。\\n\\n既存のウィンドウを確認してください。" as informational buttons {"OK"} default button "OK"
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
    FastAPIサーバーを起動（別プロセスで実行）

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

    def copy_to_clipboard(self, text: str):
        """
        文字列をクリップボードにコピー

        Args:
            text: コピーする文字列

        Returns:
            dict: {"success": bool, "message": str}
        """
        logger.info(f"🔔 [Bridge] copy_to_clipboard() が呼び出されました - text length: {len(text) if text else 0}")
        try:
            if not text:
                logger.warning("⚠️ コピーするテキストが空です")
                return {
                    "success": False,
                    "message": "コピーするテキストが空です"
                }

            # 方法: 一時ファイル経由でAppleScriptを使ってクリップボードにコピー
            # 長いテキストをコマンドライン引数で渡すと制限を超えるため、
            # 一時ファイルに書き込んでから、AppleScriptでファイルを読み込む

            import tempfile
            import os

            # 一時ファイルを作成してテキストを書き込み
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as tmp:
                tmp.write(text)
                tmp_path = tmp.name

            logger.info(f"📝 一時ファイル作成: {tmp_path} ({len(text)}文字)")

            try:
                # AppleScriptでファイルを読み込んでクリップボードにセット
                applescript = f'''
                set theFile to POSIX file "{tmp_path}"
                set fileRef to open for access theFile
                set fileContents to read fileRef as «class utf8»
                close access fileRef
                set the clipboard to fileContents
                '''

                logger.info(f"🍎 AppleScriptでクリップボードにセット中...")

                result = subprocess.run(
                    ['osascript', '-e', applescript],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode != 0:
                    logger.error(f"❌ AppleScript失敗: {result.stderr}")
                    return {
                        "success": False,
                        "message": f"クリップボードへのコピーに失敗しました: {result.stderr}"
                    }

                logger.info(f"✅ AppleScriptでクリップボードにコピーしました ({len(text)}文字)")

                return {
                    "success": True,
                    "message": "クリップボードにコピーしました"
                }

            finally:
                # 一時ファイルを削除
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    logger.debug(f"🗑️ 一時ファイル削除: {tmp_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ クリップボードコピーエラー: {e}", exc_info=True)
            return {
                "success": False,
                "message": "クリップボードへのコピーに失敗しました"
            }
        except Exception as e:
            logger.error(f"❌ クリップボードコピーエラー: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"クリップボードへのコピーに失敗しました: {str(e)}"
            }

    def save_transcription(self):
        """
        文字起こし結果をファイルに保存（メタ情報付き）

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

            # メタ情報を取得
            char_count = len(text)
            processing_time = data.get("processing_time", 0.0)  # 秒単位
            model_name = data.get("model", "")  # モデル名

            # モデル名の表示形式を整形
            if model_name == "medium":
                model_display = "Medium"
            elif model_name == "large-v3":
                model_display = "Large-v3"
            else:
                model_display = model_name or "不明"

            # 処理時間のフォーマット（60秒以上なら「mm分ss秒」、未満なら「○○.○秒」）
            if processing_time >= 60:
                minutes = int(processing_time // 60)
                seconds = int(processing_time % 60)
                time_str = f"{minutes}分{seconds}秒"
            else:
                time_str = f"{processing_time:.1f}秒"

            timestamp_str = data.get("timestamp") or datetime.now().isoformat()
            try:
                timestamp_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                timestamp_dt = datetime.now()

            # ファイル保存ダイアログを表示
            file_types = ('Text Files (*.txt)', )
            save_path = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=f'文字起こし結果_{timestamp_dt.strftime("%Y%m%d_%H%M%S")}.txt',
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

            # メタ情報を末尾に追記
            text_with_meta = f"{text}\n\n---\n文字数：{char_count}文字\n処理時間：{time_str}\n音声認識モデル：{model_display}\n"

            # ファイルに書き込み
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text_with_meta)

            logger.info(f"📥 文字起こし結果保存: {save_path} ({char_count}文字, {time_str})")

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
        logger.info("🔔 [Bridge] select_audio_file() が呼び出されました")
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
        logger.info(f"🔔 [Bridge] upload_audio_file() が呼び出されました - file_path: {file_path}")
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
    # テストモード確認（環境変数 GAQ_TEST_MODE=1 で /test ページを開く）
    test_mode = os.environ.get("GAQ_TEST_MODE", "0") == "1"
    if test_mode:
        url = f"http://{host}:{port}/test"
        logger.info("🧪 [TEST MODE] テストページを起動します: /test")
    else:
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
        title=f"GaQ Offline Transcriber v{APP_VERSION}",
        url=url,
        width=800,
        height=900,
        resizable=True,
        frameless=False,  # タイトルバーを表示
        easy_drag=True,  # ドラッグ可能
        js_api=bridge,  # JSブリッジを登録
    )

    def log_pywebview_state(event_name: str):
        """
        window.pywebview / window.pywebview.api の存在をログに出力する
        """
        try:
            result = window.evaluate_js(
                """
                (function() {
                    var hasPywebview = typeof window.pywebview !== 'undefined';
                    var hasApi = hasPywebview && !!window.pywebview.api;
                    var apiKeys = hasApi ? Object.keys(window.pywebview.api) : [];
                    return JSON.stringify({
                        hasPywebview: hasPywebview,
                        hasApi: hasApi,
                        apiKeys: apiKeys
                    });
                })();
                """
            )
            if isinstance(result, str):
                logger.info(f"🔍 [{event_name}] pywebview状態: {result}")
            else:
                logger.info(f"🔍 [{event_name}] pywebview状態(raw): {result}")
        except Exception as exc:
            logger.error(f"❌ [{event_name}] pywebview確認エラー: {exc}", exc_info=True)

    window.events.loaded += lambda: log_pywebview_state("loaded")
    window.events.shown += lambda: log_pywebview_state("shown")

    # ★コンソールフックは main.py の <script> タグ内に直接埋め込み済み
    # （以前は window.events.loaded で注入していたが、タイミングが遅すぎたため変更）
    # def setup_console_hook():
    #     """
    #     コンソールログをPython側にブリッジするJSコードを注入
    #     """
    #     ...
    # window.events.loaded += setup_console_hook

    # ドラッグ&ドロップイベントハンドラーの登録
    def setup_drag_drop_handler():
        """
        pywebview DOM APIを使ってドラッグ&ドロップイベントを登録
        """
        try:
            from webview.dom import DOMEventHandler

            def on_drop(e):
                """
                ドロップイベントハンドラー
                pywebviewFullPathを取得してJavaScriptに通知
                """
                try:
                    logger.info("📥 [DragDrop] ドロップイベント発生")
                    files = e.get('dataTransfer', {}).get('files', [])

                    if not files:
                        logger.warning("⚠️ [DragDrop] ドロップされたファイルがありません")
                        return

                    # 最初のファイルのパスを取得
                    first_file = files[0]
                    file_path = first_file.get('pywebviewFullPath')
                    file_name = first_file.get('name', 'unknown')

                    logger.info(f"📂 [DragDrop] ファイルドロップ: {file_name} ({file_path})")

                    if not file_path:
                        logger.error("❌ [DragDrop] pywebviewFullPathが取得できませんでした")
                        return

                    # JavaScriptにファイルパスを通知
                    # window.__droppedFilePathにセットして、JavaScriptイベントを発火
                    js_code = f'''
                    (function() {{
                        window.__droppedFilePath = {json.dumps(file_path)};
                        window.__droppedFileName = {json.dumps(file_name)};
                        var event = new CustomEvent('pywebviewFileDrop', {{
                            detail: {{
                                path: {json.dumps(file_path)},
                                name: {json.dumps(file_name)}
                            }}
                        }});
                        window.dispatchEvent(event);
                        console.log('🎯 [DragDrop] pywebviewFileDrop イベント発火:', {json.dumps(file_name)});
                    }})();
                    '''
                    window.evaluate_js(js_code)
                    logger.info(f"✅ [DragDrop] JavaScript通知完了: {file_name}")

                except Exception as ex:
                    logger.error(f"❌ [DragDrop] ドロップ処理エラー: {ex}", exc_info=True)

            # dragoverイベントのハンドラー（dropを許可するために必須）
            def on_dragover(e):
                """
                dragoverイベントでprevent_defaultしないとdropイベントが発火しない
                """
                # ログは大量になるので出力しない
                pass

            # イベントをバインドする DOM 要素を取得
            try:
                upload_area = window.dom.get_element('#uploadArea')
                logger.info("✅ [DragDrop] uploadArea要素の取得に成功")
            except Exception as lookup_error:
                upload_area = None
                logger.error(f"❌ [DragDrop] uploadArea取得エラー: {lookup_error}", exc_info=True)

            if upload_area is None:
                logger.error("❌ [DragDrop] uploadArea要素を取得できなかったため、ドラッグ&ドロップを無効化します")
                return

            # dragoverとdropイベントにハンドラーを登録
            # dragoverでpreventDefaultしないとdropイベントが発火しない
            upload_area.events.dragover += DOMEventHandler(on_dragover, prevent_default=True, stop_propagation=False)
            upload_area.events.drop += DOMEventHandler(on_drop, prevent_default=True, stop_propagation=True)

            logger.info("✅ [DragDrop] ドロップイベントハンドラー登録完了（dragover + drop）")

        except Exception as e:
            logger.error(f"❌ [DragDrop] ハンドラー登録エラー: {e}", exc_info=True)

    # loadedイベント後にドラッグ&ドロップハンドラーを設定
    window.events.loaded += setup_drag_drop_handler

    # ★第2段階: FastAPIプロセス終了処理
    def shutdown_server():
        """
        FastAPIサーバープロセスを終了する

        - 最大5秒待機して正常終了を試みる
        - タイムアウト時は強制終了（terminate → kill）
        - 最大合計8秒で必ず終了
        """
        global server_process

        if server_process is None:
            logger.info("🔹 [Shutdown] サーバープロセスは未起動または既に終了済み")
            return

        try:
            logger.info("🛑 [Shutdown] FastAPIサーバープロセスの終了を開始...")
            start_time = time.time()

            # プロセスが生きているかチェック
            if not server_process.is_alive():
                logger.info("✅ [Shutdown] サーバープロセスは既に終了済み")
                return

            # 正常終了を試みる（5秒待機）
            logger.info("⏳ [Shutdown] プロセスの正常終了を待機中（最大5秒）...")
            server_process.join(timeout=5)

            # タイムアウト後も生きている場合は強制終了（terminate）
            if server_process.is_alive():
                elapsed = time.time() - start_time
                logger.warning(f"⚠️  [Shutdown] {elapsed:.1f}秒経過してもプロセスが終了しないため、terminate()を実行")
                server_process.terminate()
                server_process.join(timeout=2)  # terminate後2秒待機

                # terminate()でも終了しない場合はkill()を使用
                if server_process.is_alive():
                    logger.warning(f"⚠️  [Shutdown] terminate()でも終了しないため、kill()を実行")
                    server_process.kill()
                    server_process.join(timeout=1)  # kill後1秒待機

                    if server_process.is_alive():
                        logger.error("❌ [Shutdown] kill()後もプロセスが残存しています")
                    else:
                        total_time = time.time() - start_time
                        logger.info(f"✅ [Shutdown] プロセスをkill()で強制終了しました（合計{total_time:.1f}秒）")
                else:
                    total_time = time.time() - start_time
                    logger.info(f"✅ [Shutdown] プロセスをterminate()で終了しました（合計{total_time:.1f}秒）")
            else:
                elapsed = time.time() - start_time
                logger.info(f"✅ [Shutdown] プロセスが正常終了しました（{elapsed:.1f}秒）")

        except Exception as e:
            logger.error(f"❌ [Shutdown] プロセス終了処理でエラーが発生: {e}", exc_info=True)

    # ★第1段階: 終了確認ダイアログの実装
    def on_closing():
        """
        ウィンドウ終了時の確認ダイアログ
        アプリの雰囲気に合わせたAppleScriptダイアログ

        Returns:
            bool: True=終了を許可, False=終了をキャンセル
        """
        try:
            logger.info("🚪 [Closing] ウィンドウ終了要求を検知")

            # AppleScriptダイアログ（アイコンを "note" にして柔らかい印象に）
            script = '''
            display dialog "処理中のタスクがある場合は中断されます。

アプリケーションを終了してもよろしいですか？" ¬
                with title "GaQ Offline Transcriber - 終了確認" ¬
                buttons {"キャンセル", "終了"} ¬
                default button "終了" ¬
                cancel button "キャンセル" ¬
                with icon note
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ [Closing] ユーザーが終了を承認")
                # ★第2段階: FastAPIサーバープロセスを終了
                shutdown_server()
                return True
            else:
                logger.info("❌ [Closing] ユーザーが終了をキャンセル")
                return False

        except Exception as e:
            logger.error(f"❌ [Closing] 終了確認ダイアログエラー: {e}", exc_info=True)
            # エラー時は終了をキャンセル（安全側に倒す）
            return False

    window.events.closing += on_closing

    # Webviewを起動（メインスレッド）
    webview_debug = os.environ.get("GAQ_WEBVIEW_DEBUG", "0") == "1"
    private_mode_env = os.environ.get("GAQ_WEBVIEW_PRIVATE")
    if private_mode_env is None:
        webview_private_mode = False
    else:
        webview_private_mode = private_mode_env.lower() not in {"0", "false", "no"}
    webview.start(debug=webview_debug, private_mode=webview_private_mode)


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
    # PyInstallerビルド時の multiprocessing による再実行を防ぐため、
    # set_start_method は一度だけ実行されるようにする
    if sys.platform == "darwin":
        try:
            multiprocessing.set_start_method("spawn", force=False)
        except RuntimeError:
            # 既に設定済みの場合は何もしない
            pass

    # ★第2段階: FastAPIサーバーを別プロセスで起動（Thread→Process化）
    global server_process
    server_process = multiprocessing.Process(
        target=run_fastapi_server, args=("127.0.0.1", 8000), daemon=True
    )
    server_process.start()
    logger.info(f"🚀 [Main] FastAPIサーバープロセスを起動 (PID: {server_process.pid})")

    # Webviewウィンドウを作成（メインスレッド）
    create_webview_window("127.0.0.1", 8000)

    logger.info(f"=== GaQ Offline Transcriber {APP_VERSION} 終了 ===")


if __name__ == "__main__":
    # PyInstallerビルド時のmultiprocessing対策
    # freeze_support()を呼び出すことで、子プロセスが正しく動作する
    multiprocessing.freeze_support()
    main()
