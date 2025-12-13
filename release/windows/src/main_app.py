"""
GaQ Offline Transcriber - ネイティブアプリ版メインエントリーポイント
pywebview + FastAPI によるオフライン文字起こしアプリ
"""

import atexit
import faulthandler
import json
import logging
import multiprocessing
import os
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import requests
import uvicorn

# ===== pywebviewバックエンド設定 =====
# EdgeChromium（WebView2）を第一候補にする
os.environ.setdefault("PYWEBVIEW_GUI", "edgechromium")
import webview

# EdgeChromiumのインポート可否を事前に確認してログを出す
EDGECHROMIUM_IMPORT_OK = False
EDGECHROMIUM_IMPORT_ERR = None
try:
    import webview.platforms.edgechromium  # noqa: F401
    EDGECHROMIUM_IMPORT_OK = True
except Exception as e:
    EDGECHROMIUM_IMPORT_ERR = str(e)
    # フォールバックはさせず、後でユーザーに案内して終了する

from config import APP_VERSION, LOG_DIR as CONFIG_LOG_DIR, UPLOAD_DIR

# OS判定
IS_WINDOWS = os.name == "nt"

# ===== フェイルファスト: クラッシュログ有効化 =====
# ハードクラッシュ時にスタックトレースをファイルに出力
_CRASH_LOG_DIR = Path.home() / ".gaq" / "logs"
_CRASH_LOG_DIR.mkdir(parents=True, exist_ok=True)
_CRASH_LOG_FILE = _CRASH_LOG_DIR / "crash.log"
try:
    _crash_log_handle = open(_CRASH_LOG_FILE, "a", encoding="utf-8")
    faulthandler.enable(file=_crash_log_handle, all_threads=True)
except Exception:
    # ファイル出力失敗時はstderrにフォールバック
    faulthandler.enable()

# OS別のファイルロックモジュールをインポート
if IS_WINDOWS:
    import msvcrt
else:
    import fcntl

# ロックファイルのパス（OS別）
if IS_WINDOWS:
    LOCK_FILE = Path(os.environ.get("TEMP", Path.home())) / "gaq_transcriber.lock"
else:
    LOCK_FILE = "/tmp/gaq_transcriber.lock"

lock_file_handle = None

# ログディレクトリ（config.pyから取得、環境変数で上書き可能）
custom_log_dir = os.environ.get("GAQ_LOG_DIR")
if custom_log_dir:
    LOG_DIR = Path(custom_log_dir)
else:
    LOG_DIR = CONFIG_LOG_DIR  # config.pyで定義されたディレクトリを使用
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

        if IS_WINDOWS:
            # Windows: msvcrtを使用した排他ロック
            try:
                msvcrt.locking(lock_file_handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                # ロック失敗 = 既に別のインスタンスが起動中
                logger.warning(f"⚠️ 別のインスタンスが既に起動しています (ロックファイル: {LOCK_FILE})")
                if lock_file_handle:
                    lock_file_handle.close()
                    lock_file_handle = None
                return False
        else:
            # macOS/Linux: fcntlを使用した排他ロック
            fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        # ロック成功時、PIDを記録（seek(0) → truncate()でゴミを残さない）
        lock_file_handle.seek(0)
        lock_file_handle.truncate()
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
            if IS_WINDOWS:
                # Windows: msvcrtでロック解除
                msvcrt.locking(lock_file_handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                # macOS/Linux: fcntlでロック解除
                fcntl.flock(lock_file_handle.fileno(), fcntl.LOCK_UN)

            lock_file_handle.close()
            logger.info("🔓 単一インスタンスロック解放")
        except Exception as e:
            logger.error(f"ロック解放エラー: {e}")
        finally:
            lock_file_handle = None


def show_already_running_dialog():
    """
    既に起動中である旨をユーザーに通知（OS別）
    """
    try:
        if IS_WINDOWS:
            # Windows: ctypesでMessageBoxを表示
            import ctypes
            MB_OK = 0x0
            MB_ICONINFORMATION = 0x40
            ctypes.windll.user32.MessageBoxW(
                0,
                "GaQ Offline Transcriber は既に起動しています。\n\n既存のウィンドウを確認してください。",
                "お知らせ",
                MB_OK | MB_ICONINFORMATION
            )
        else:
            # macOS: osascriptでダイアログ表示
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
        文字列をクリップボードにコピー（OS別）

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

            if IS_WINDOWS:
                # Windows用に改行コードを整形（LF → CRLF）
                text_windows = text.replace("\r\n", "\n").replace("\n", "\r\n")

                # Windows: win32clipboardを使用
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(text_windows, win32clipboard.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                    logger.info(f"✅ Windowsクリップボードにコピーしました ({len(text)}文字)")
                    return {
                        "success": True,
                        "message": "クリップボードにコピーしました"
                    }
                except ImportError:
                    # win32clipboardが利用できない場合はctypesで代替（安全な実装）
                    logger.warning("⚠️ win32clipboard not available, using ctypes fallback")
                    import ctypes

                    # 定数定義
                    GMEM_MOVEABLE = 0x0002
                    GMEM_ZEROINIT = 0x0040
                    CF_UNICODETEXT = 13

                    # Windows API の型定義
                    kernel32 = ctypes.windll.kernel32
                    user32 = ctypes.windll.user32

                    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
                    kernel32.GlobalAlloc.restype = ctypes.c_void_p

                    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
                    kernel32.GlobalLock.restype = ctypes.c_void_p

                    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
                    kernel32.GlobalUnlock.restype = ctypes.c_bool

                    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
                    kernel32.GlobalFree.restype = ctypes.c_void_p

                    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
                    user32.OpenClipboard.restype = ctypes.c_bool

                    user32.EmptyClipboard.argtypes = []
                    user32.EmptyClipboard.restype = ctypes.c_bool

                    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
                    user32.SetClipboardData.restype = ctypes.c_void_p

                    user32.CloseClipboard.argtypes = []
                    user32.CloseClipboard.restype = ctypes.c_bool

                    handle = None
                    try:
                        # Unicode文字列バッファを作成（null終端を含む）
                        buffer = ctypes.create_unicode_buffer(text_windows + "\0")
                        size = ctypes.sizeof(buffer)

                        # グローバルメモリを割り当て
                        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, size)
                        if not handle:
                            logger.error("GlobalAlloc failed")
                            return {
                                "success": False,
                                "message": "クリップボードへのコピーに失敗しました（メモリ割り当てエラー）"
                            }

                        # メモリをロックしてデータをコピー
                        locked = kernel32.GlobalLock(handle)
                        if not locked:
                            kernel32.GlobalFree(handle)
                            logger.error("GlobalLock failed")
                            return {
                                "success": False,
                                "message": "クリップボードへのコピーに失敗しました（メモリロックエラー）"
                            }

                        ctypes.memmove(locked, ctypes.addressof(buffer), size)
                        kernel32.GlobalUnlock(handle)

                        # クリップボードを開いてデータをセット
                        if not user32.OpenClipboard(0):
                            kernel32.GlobalFree(handle)
                            logger.error("OpenClipboard failed")
                            return {
                                "success": False,
                                "message": "クリップボードへのコピーに失敗しました（クリップボードオープンエラー）"
                            }

                        user32.EmptyClipboard()

                        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
                            user32.CloseClipboard()
                            kernel32.GlobalFree(handle)
                            logger.error("SetClipboardData failed")
                            return {
                                "success": False,
                                "message": "クリップボードへのコピーに失敗しました（データセットエラー）"
                            }

                        user32.CloseClipboard()

                        # 成功時はhandleの所有権がクリップボードに移るため、GlobalFreeは不要
                        logger.info(f"✅ Windowsクリップボードにコピーしました (ctypesフォールバック) ({len(text)}文字)")
                        return {
                            "success": True,
                            "message": "クリップボードにコピーしました"
                        }

                    except Exception as e:
                        # エラー時はメモリを解放
                        if handle:
                            try:
                                kernel32.GlobalFree(handle)
                            except:
                                pass
                        try:
                            user32.CloseClipboard()
                        except:
                            pass
                        logger.exception(f"ctypesクリップボードコピーエラー: {e}")
                        return {
                            "success": False,
                            "message": f"クリップボードへのコピーに失敗しました: {str(e)}"
                        }
            else:
                # macOS: 一時ファイル経由でAppleScriptを使用
                import tempfile

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
                        logger.error(f"AppleScript失敗: {result.stderr}")
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
            logger.error(f"クリップボードコピーエラー: {e}", exc_info=True)
            return {
                "success": False,
                "message": "クリップボードへのコピーに失敗しました"
            }
        except Exception as e:
            logger.error(f"クリップボードコピーエラー: {e}", exc_info=True)
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

            # ファイル保存ダイアログを表示（pywebview 6.1+対応）
            file_types = ('Text Files (*.txt)', )

            # pywebview 6.1以降ではFileDialog Enumを使用、それ以前はSAVE_DIALOGを使用
            try:
                # pywebview 6.1+
                from webview import FileDialog
                dialog_type = FileDialog.SAVE
            except ImportError:
                # pywebview < 6.1 (後方互換)
                dialog_type = webview.SAVE_DIALOG

            save_path = webview.windows[0].create_file_dialog(
                dialog_type,
                save_filename=f'文字起こし結果_{timestamp_dt.strftime("%Y%m%d_%H%M%S")}.txt',
                file_types=file_types
            )

            # create_file_dialogの戻り値がタプル/リストの場合は先頭要素を採用
            if isinstance(save_path, (tuple, list)):
                save_path = save_path[0] if save_path else None

            # Pathインスタンスの場合はstr()へ変換
            if save_path and hasattr(save_path, '__fspath__'):
                save_path = str(save_path)

            # ユーザーがキャンセルした場合、または空文字/Noneの場合
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
    logger.info(f"🛰️ PYWEBVIEW_GUI={os.environ.get('PYWEBVIEW_GUI')} / EdgeChromium import ok: {EDGECHROMIUM_IMPORT_OK}")
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
        ウィンドウ終了時の確認ダイアログ（OS別）

        Returns:
            bool: True=終了を許可, False=終了をキャンセル
        """
        try:
            logger.info("🚪 [Closing] ウィンドウ終了要求を検知")

            if IS_WINDOWS:
                # Windows: ctypesでMessageBoxを表示
                import ctypes
                MB_YESNO = 0x4
                MB_ICONQUESTION = 0x20
                MB_DEFBUTTON2 = 0x100
                IDYES = 6

                result = ctypes.windll.user32.MessageBoxW(
                    0,
                    "処理中のタスクがある場合は中断されます。\n\nアプリケーションを終了してもよろしいですか？",
                    "GaQ Offline Transcriber - 終了確認",
                    MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2
                )

                if result == IDYES:
                    logger.info("✅ [Closing] ユーザーが終了を承認")
                    # ★第2段階: FastAPIサーバープロセスを終了
                    shutdown_server()
                    return True
                else:
                    logger.info("❌ [Closing] ユーザーが終了をキャンセル")
                    return False
            else:
                # macOS: AppleScriptダイアログ（アイコンを "note" にして柔らかい印象に）
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
    webview.start(debug=webview_debug, private_mode=webview_private_mode, gui="edgechromium")


def log_system_info():
    """
    起動時のシステム情報をログに出力（診断用）
    """
    try:
        import ctypes

        logger.info("=== システム情報 ===")
        logger.info(f"  OS: {platform.system()} {platform.release()} ({platform.version()})")
        logger.info(f"  アーキテクチャ: {platform.machine()}")
        logger.info(f"  Python: {platform.python_version()}")
        logger.info(f"  実行パス: {sys.executable}")
        logger.info(f"  作業ディレクトリ: {os.getcwd()}")
        logger.info(f"  PyInstaller: {'Yes' if getattr(sys, 'frozen', False) else 'No'}")

        # メモリ情報（Windows）
        if IS_WINDOWS:
            try:
                kernel32 = ctypes.windll.kernel32

                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                mem_status = MEMORYSTATUSEX()
                mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))

                total_gb = mem_status.ullTotalPhys / (1024**3)
                avail_gb = mem_status.ullAvailPhys / (1024**3)
                logger.info(f"  メモリ: {avail_gb:.1f}GB 空き / {total_gb:.1f}GB 合計")

                if avail_gb < 4.0:
                    logger.warning(f"  ⚠️ 利用可能メモリが少ない状態です（Large-v3モデルには8GB以上推奨）")
            except Exception as mem_err:
                logger.debug(f"  メモリ情報取得失敗: {mem_err}")

        # ログディレクトリ情報
        logger.info(f"  ログディレクトリ: {LOG_DIR}")
        logger.info(f"  クラッシュログ: {_CRASH_LOG_FILE}")
        logger.info("===================")

        # CPU命令セットのチェック（AVX/AVX2）
        check_cpu_features()

    except Exception as e:
        logger.warning(f"システム情報取得エラー: {e}")


def check_runtime_dependencies():
    """
    VC++ Runtime / UCRT / OpenSSL などの依存DLLを確認

    不足している場合は警告をログに出力し、インストール案内を表示
    """
    if not IS_WINDOWS:
        return True  # Windows以外はチェック不要

    import ctypes

    required_dlls = [
        ('vcruntime140.dll', 'Visual C++ Runtime', 'https://aka.ms/vs/17/release/vc_redist.x64.exe'),
        ('msvcp140.dll', 'Visual C++ Runtime', 'https://aka.ms/vs/17/release/vc_redist.x64.exe'),
        ('ucrtbase.dll', 'Universal C Runtime', None),  # Windowsに標準搭載
    ]

    missing_dlls = []
    logger.info("=== DLL依存チェック ===")

    for dll_name, description, download_url in required_dlls:
        try:
            ctypes.WinDLL(dll_name)
            logger.info(f"  ✅ {dll_name}")
        except OSError:
            logger.warning(f"  ❌ {dll_name} が見つかりません ({description})")
            if download_url:
                missing_dlls.append((dll_name, description, download_url))

    logger.info("=======================")

    if missing_dlls:
        logger.error("⚠️ 必要なランタイムが不足しています:")
        for dll_name, description, download_url in missing_dlls:
            logger.error(f"  - {description}: {download_url}")

        # ユーザーにダイアログで通知
        try:
            import ctypes
            MB_OK = 0x0
            MB_ICONERROR = 0x10
            message = (
                "必要なランタイムが見つかりません。\n\n"
                "Visual C++ 再頒布可能パッケージをインストールしてください:\n"
                "https://aka.ms/vs/17/release/vc_redist.x64.exe\n\n"
                "インストール後、アプリを再起動してください。"
            )
            ctypes.windll.user32.MessageBoxW(0, message, "GaQ - ランタイムエラー", MB_OK | MB_ICONERROR)
        except Exception:
            pass

        return False

    return True


def check_webview2_runtime():
    """
    WebView2ランタイムの存在を確認

    WebView2が見つからない場合は自動インストーラへの誘導を表示

    Returns:
        bool: WebView2が利用可能な場合True
    """
    if not IS_WINDOWS:
        return True

    import ctypes
    import winreg

    WEBVIEW2_DOWNLOAD_URL = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"

    logger.info("=== WebView2ランタイムチェック ===")

    # レジストリでWebView2の存在を確認
    webview2_keys = [
        # Per-machine installation
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
        # Per-user installation
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
    ]

    webview2_found = False
    webview2_version = None

    for hkey, key_path in webview2_keys:
        try:
            with winreg.OpenKey(hkey, key_path) as key:
                version, _ = winreg.QueryValueEx(key, "pv")
                if version and version != "0.0.0.0":
                    webview2_found = True
                    webview2_version = version
                    break
        except (FileNotFoundError, OSError):
            continue

    if webview2_found:
        logger.info(f"  ✅ WebView2 Runtime: {webview2_version}")
        logger.info("=================================")
        return True
    else:
        logger.warning("  ❌ WebView2 Runtimeが見つかりません")
        logger.warning(f"     ダウンロード: {WEBVIEW2_DOWNLOAD_URL}")
        logger.info("=================================")

        # ユーザーにダイアログで通知
        try:
            MB_YESNO = 0x4
            MB_ICONWARNING = 0x30
            IDYES = 6

            message = (
                "WebView2ランタイムが見つかりません。\n\n"
                "このアプリを実行するにはWebView2が必要です。\n"
                "今すぐダウンロードページを開きますか？\n\n"
                "(Windows 10/11には通常プリインストールされています)"
            )

            result = ctypes.windll.user32.MessageBoxW(
                0, message, "GaQ - WebView2が必要です",
                MB_YESNO | MB_ICONWARNING
            )

            if result == IDYES:
                # ブラウザでダウンロードページを開く
                import webbrowser
                webbrowser.open(WEBVIEW2_DOWNLOAD_URL)
                logger.info("WebView2ダウンロードページを開きました")

        except Exception as e:
            logger.error(f"WebView2ダイアログエラー: {e}")

        return False


def get_gpu_disable_flag():
    """
    GPU無効化フラグを環境変数またはコマンドライン引数から取得

    Returns:
        bool: GPU無効化する場合True
    """
    # 環境変数チェック
    if os.environ.get("GAQ_DISABLE_GPU", "0") == "1":
        return True

    # コマンドライン引数チェック
    if "--disable-gpu" in sys.argv:
        return True

    return False


def check_cpu_features():
    """
    CPU命令セット（AVX/AVX2/FMA）の対応状況を確認

    ctranslate2/faster-whisperはAVX2を使用する可能性があるため、
    非対応CPUでは起動時に警告を表示
    """
    if not IS_WINDOWS:
        return  # Windows以外は簡易チェック不可

    try:
        import ctypes
        import struct

        # CPUIDを使用してAVX/AVX2をチェック
        # 簡易実装: レジストリまたはWMIで確認

        # 方法1: PowerShellでCPU情報を取得
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Caption"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
        )

        if result.returncode == 0:
            cpu_name = result.stdout.strip()
            logger.info(f"  CPU: {cpu_name}")

        # 方法2: ctranslate2のCPU情報をログ（利用可能な場合）
        try:
            import ctranslate2
            if hasattr(ctranslate2, 'get_supported_compute_types'):
                compute_types = ctranslate2.get_supported_compute_types("cpu")
                logger.info(f"  ctranslate2対応compute_types: {compute_types}")

                # int8が使えない場合は警告
                if "int8" not in compute_types:
                    logger.warning("  ⚠️ int8 compute typeが利用できません。パフォーマンスが低下する可能性があります。")
        except ImportError:
            pass  # ctranslate2が読み込めない場合はスキップ
        except Exception as ct_err:
            logger.debug(f"  ctranslate2チェックエラー: {ct_err}")

        # 古いCPU（AVX非対応）の警告
        # Intel Core2/初代Core i、AMD Phenom II以前はAVX非対応
        old_cpu_patterns = [
            "Core2", "Core(TM)2", "Pentium", "Celeron",
            "Phenom", "Athlon", "Sempron", "Turion"
        ]
        if result.returncode == 0:
            cpu_lower = cpu_name.lower()
            for pattern in old_cpu_patterns:
                if pattern.lower() in cpu_lower:
                    logger.warning(f"  ⚠️ 古いCPU({pattern})が検出されました。")
                    logger.warning("     AVX/AVX2命令に対応していない場合、文字起こし処理が失敗する可能性があります。")
                    break

    except subprocess.TimeoutExpired:
        logger.debug("  CPU情報取得タイムアウト")
    except Exception as e:
        logger.debug(f"  CPU機能チェックエラー: {e}")


def main():
    """
    アプリケーションのメインエントリーポイント
    """
    logger.info(f"=== GaQ Offline Transcriber {APP_VERSION} 起動 ===")
    logger.info(f"🛰️ PYWEBVIEW_GUI={os.environ.get('PYWEBVIEW_GUI')} / EdgeChromium import ok: {EDGECHROMIUM_IMPORT_OK}")
    if not EDGECHROMIUM_IMPORT_OK:
        logger.error(f"❌ EdgeChromium backendの読み込みに失敗: {EDGECHROMIUM_IMPORT_ERR}")
        if IS_WINDOWS:
            try:
                import ctypes
                MB_OK = 0x0
                MB_ICONERROR = 0x10
                message = (
                    "EdgeChromiumバックエンドの読み込みに失敗しました。\n"
                    "WebView2ランタイムが正しくインストールされているか、\n"
                    "配布物が破損していないかを確認してください。\n\n"
                    "再インストール後も解決しない場合は、ログを添えてご連絡ください。"
                )
                ctypes.windll.user32.MessageBoxW(0, message, "GaQ - WebView起動エラー", MB_OK | MB_ICONERROR)
            except Exception:
                pass
        sys.exit(1)

    # システム情報をログ出力（診断用）
    log_system_info()

    # DLL依存チェック（Windows）
    if IS_WINDOWS:
        if not check_runtime_dependencies():
            logger.error("=== 必要なランタイムが不足しているため終了します ===")
            sys.exit(1)

        # WebView2ランタイムチェック（Windows）
        # EdgeChromiumバックエンドはWebView2が必須のため、未インストール時は終了
        if not check_webview2_runtime():
            logger.error("=== WebView2が見つからないため終了します ===")
            sys.exit(1)

    # GPU無効化フラグを確認
    if get_gpu_disable_flag():
        logger.info("🔧 GPU無効化モードが有効です")
        os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = "--disable-gpu"

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
