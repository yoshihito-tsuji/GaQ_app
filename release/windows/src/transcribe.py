"""
文字起こし処理モジュール
faster-whisperを使用した音声認識
"""

import hashlib
import json
import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Optional

# ===== Windows対応: シンボリックリンク無効化 =====
# 配布版で管理者権限を要求しないための設定
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
# ================================================

# ===== ffmpeg/PyAV設定 =====
# PyInstallerバンドル時、PyAVのffmpegを優先使用
def setup_ffmpeg_path():
    """
    PyAVにバンドルされたffmpegを優先使用するようPATHを設定

    PyInstallerでパッケージ化された場合、sys._MEIPASSにffmpegが含まれる
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでパッケージ化されている場合
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            meipass_path = Path(meipass)
            # ffmpegバイナリがある可能性のあるパス
            ffmpeg_paths = [
                meipass_path,
                meipass_path / "av",
                meipass_path / "ffmpeg",
            ]
            for ffmpeg_path in ffmpeg_paths:
                if ffmpeg_path.exists():
                    # PATHの先頭に追加（優先使用）
                    current_path = os.environ.get("PATH", "")
                    if str(ffmpeg_path) not in current_path:
                        os.environ["PATH"] = str(ffmpeg_path) + os.pathsep + current_path

setup_ffmpeg_path()
# ============================

from faster_whisper import WhisperModel
from huggingface_hub import snapshot_download

logger = logging.getLogger(__name__)

# モデルの期待されるファイル（破損検知用）
MODEL_REQUIRED_FILES = {
    "medium": ["model.bin", "config.json", "vocabulary.json", "tokenizer.json"],
    "large-v3": ["model.bin", "config.json", "vocabulary.json", "tokenizer.json"],
}


def check_model_exists(model_name: str) -> dict:
    """
    モデルがダウンロード済みか確認

    Args:
        model_name: モデル名（medium, large-v3など）

    Returns:
        dict: {
            'exists': bool,      # モデルが存在するか
            'size_gb': float,    # サイズ（GB単位）
            'path': str          # モデルパス（存在する場合のみ）
        }
    """
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_dir = cache_dir / f"models--Systran--faster-whisper-{model_name}"

    exists = model_dir.exists()
    size_gb = 0

    if exists:
        # ディレクトリサイズを計算
        total_size = sum(f.stat().st_size for f in model_dir.rglob("*") if f.is_file())
        size_gb = total_size / (1024**3)  # GB単位
    else:
        # 推定サイズ（未ダウンロード時）
        size_estimates = {
            "tiny": 0.075,
            "base": 0.14,
            "small": 0.46,
            "medium": 1.5,
            "large-v2": 2.9,
            "large-v3": 2.9,
        }
        size_gb = size_estimates.get(model_name, 1.5)

    return {
        "exists": exists,
        "size_gb": round(size_gb, 2),
        "path": str(model_dir) if exists else None,
    }


def verify_model_integrity(model_name: str) -> dict:
    """
    モデルの整合性を検証

    必須ファイルの存在確認と、config.jsonの読み取りテストを行う

    Args:
        model_name: モデル名（medium, large-v3など）

    Returns:
        dict: {
            'valid': bool,           # モデルが有効か
            'missing_files': list,   # 不足しているファイル
            'corrupted_files': list, # 破損しているファイル
            'model_path': str        # モデルパス
        }
    """
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_dir = cache_dir / f"models--Systran--faster-whisper-{model_name}"

    result = {
        "valid": False,
        "missing_files": [],
        "corrupted_files": [],
        "model_path": None,
    }

    if not model_dir.exists():
        logger.warning(f"モデルディレクトリが存在しません: {model_dir}")
        return result

    # snapshotsディレクトリ内の最新のスナップショットを探す
    snapshots_dir = model_dir / "snapshots"
    if not snapshots_dir.exists():
        logger.warning(f"snapshotsディレクトリが存在しません: {snapshots_dir}")
        return result

    # 最新のスナップショットディレクトリを取得
    snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
    if not snapshot_dirs:
        logger.warning("スナップショットが見つかりません")
        return result

    # 最も新しいディレクトリを使用
    latest_snapshot = max(snapshot_dirs, key=lambda d: d.stat().st_mtime)
    result["model_path"] = str(latest_snapshot)

    # 必須ファイルの確認
    required_files = MODEL_REQUIRED_FILES.get(model_name, ["model.bin", "config.json"])

    for file_name in required_files:
        file_path = latest_snapshot / file_name
        if not file_path.exists():
            result["missing_files"].append(file_name)
            logger.warning(f"必須ファイルが不足: {file_name}")
        else:
            # ファイルサイズが0の場合は破損とみなす
            if file_path.stat().st_size == 0:
                result["corrupted_files"].append(file_name)
                logger.warning(f"ファイルが破損（サイズ0）: {file_name}")

    # config.jsonの読み取りテスト
    config_path = latest_snapshot / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.debug(f"config.json読み取り成功: {config.get('model_type', 'unknown')}")
        except (json.JSONDecodeError, IOError) as e:
            result["corrupted_files"].append("config.json")
            logger.warning(f"config.jsonが破損: {e}")

    # 検証結果
    result["valid"] = len(result["missing_files"]) == 0 and len(result["corrupted_files"]) == 0

    if result["valid"]:
        logger.info(f"✅ モデル整合性チェック成功: {model_name}")
    else:
        logger.warning(f"⚠️ モデル整合性チェック失敗: {model_name}")
        logger.warning(f"   不足: {result['missing_files']}, 破損: {result['corrupted_files']}")

    return result


def repair_corrupted_model(model_name: str) -> bool:
    """
    破損したモデルを修復（削除して再ダウンロード可能にする）

    Args:
        model_name: モデル名

    Returns:
        bool: 修復準備が完了した場合True
    """
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_dir = cache_dir / f"models--Systran--faster-whisper-{model_name}"

    if not model_dir.exists():
        return True  # 既に存在しないなら修復不要

    try:
        logger.info(f"🔧 破損モデルを削除中: {model_name}")
        shutil.rmtree(model_dir)
        logger.info(f"✅ 破損モデル削除完了: {model_name}")
        return True
    except Exception as e:
        logger.error(f"❌ 破損モデル削除失敗: {e}")
        return False


def delete_model(model_name: str) -> dict:
    """
    モデルを削除

    Args:
        model_name: モデル名（medium, large-v3など）

    Returns:
        dict: {'success': bool, 'message': str}
    """
    if model_name == "medium":
        return {"success": False, "message": "デフォルトモデルは削除できません"}

    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_dir = cache_dir / f"models--Systran--faster-whisper-{model_name}"

    if not model_dir.exists():
        return {"success": False, "message": "モデルが見つかりません"}

    try:
        shutil.rmtree(model_dir)
        # 表示名を整形（large-v3 → Large-v3）
        display_name = "Large-v3" if model_name.lower() == "large-v3" else model_name
        logger.info(f"✅ モデル削除完了: {model_name}")
        return {"success": True, "message": f"{display_name}モデルを削除しました"}
    except Exception as e:
        logger.error(f"❌ モデル削除失敗: {model_name} - {str(e)}")
        return {"success": False, "message": f"削除失敗: {str(e)}"}


def format_text_with_linebreaks(text: str) -> str:
    """
    テキストに適切な改行を追加

    句点（。）や感嘆符・疑問符の後に改行を入れる

    Args:
        text: 元のテキスト

    Returns:
        改行を含むテキスト
    """
    # 句点・感嘆符・疑問符の後に改行を追加
    # ただし、引用符内や数字の後は除外
    text = re.sub(r"([。！？])(?=[^」』）\)])", r"\1\n", text)

    # 連続する改行を1つにまとめる
    text = re.sub(r"\n+", "\n", text)

    # 先頭と末尾の空白・改行を削除
    return text.strip()


class TranscriptionService:
    """文字起こしサービス"""

    def __init__(self):
        self.model = None
        self.current_model_name = None

    def load_model(self, model_name: str = "medium") -> None:
        """
        モデルをロード（必要に応じてダウンロード）

        Args:
            model_name: モデル名（medium, large-v3）
        """
        if self.current_model_name == model_name and self.model is not None:
            logger.info(f"モデル '{model_name}' は既にロード済み")
            return

        # モデル存在チェック
        model_info = check_model_exists(model_name)

        if not model_info["exists"]:
            logger.info(
                f"⬇️ モデル '{model_name}' をダウンロード中（約{model_info['size_gb']}GB、初回のみ）"
            )
        else:
            # 既存モデルの整合性チェック
            logger.info(f"🔍 モデル '{model_name}' の整合性を確認中...")
            integrity = verify_model_integrity(model_name)

            if not integrity["valid"]:
                logger.warning(f"⚠️ モデル '{model_name}' が破損しています。再ダウンロードを試みます...")
                if repair_corrupted_model(model_name):
                    logger.info(f"🔄 モデル '{model_name}' を再ダウンロードします")
                else:
                    logger.error(f"❌ モデル '{model_name}' の修復に失敗しました")
                    raise RuntimeError(
                        f"モデル '{model_name}' が破損しており、自動修復に失敗しました。\n"
                        f"手動でキャッシュを削除してください: {model_info['path']}"
                    )

        logger.info(f"モデル '{model_name}' をロード中...")
        logger.info(f"  compute_type: int8 (CPU最適化)")
        logger.info(f"  device: cpu")
        start_time = time.time()

        try:
            # faster-whisperが自動でダウンロード
            logger.info("  WhisperModel初期化開始...")
            self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
            logger.info("  WhisperModel初期化完了")

            self.current_model_name = model_name
            elapsed = time.time() - start_time

            logger.info(f"✅ モデルロード完了: {model_name} ({elapsed:.1f}秒)")

        except PermissionError as e:
            error_str = str(e)
            logger.error(f"❌ 権限エラー: {error_str}")

            # WinError 1314対策: シンボリックリンクエラーの場合
            if "1314" in error_str or "symlink" in error_str.lower():
                logger.warning("⚠️ WinError 1314を検出: キャッシュクリーンアップを試行")

                # 部分的なダウンロードファイルを削除
                cache_path = Path.home() / ".cache" / "huggingface" / "hub"
                if cache_path.exists():
                    for tmp_file in cache_path.glob("**/*.tmp"):
                        try:
                            tmp_file.unlink()
                            logger.info(f"削除: {tmp_file}")
                        except Exception:
                            pass
                    for lock_file in cache_path.glob("**/*.lock"):
                        try:
                            lock_file.unlink()
                            logger.info(f"削除: {lock_file}")
                        except Exception:
                            pass

                # 再試行1: 通常の方法でもう一度試す
                logger.info("🔄 モデルダウンロードを再試行（1回目）...")
                try:
                    self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
                    self.current_model_name = model_name
                    elapsed = time.time() - start_time
                    logger.info(f"✅ モデルロード完了（再試行成功）: {model_name} ({elapsed:.1f}秒)")
                    return  # 成功したら処理を抜ける
                except PermissionError:
                    # 再試行1でも失敗した場合、fallbackに進む
                    logger.warning("⚠️ 再試行1でも失敗: symlinkを使わないダウンロードに切り替え")

                    # 再試行2: snapshot_downloadでsymlinkを完全に無効化してダウンロード
                    try:
                        cache_dir = Path.home() / ".cache" / "huggingface"
                        # symlink/hardlinkを使わない専用ディレクトリ
                        fallback_dir = cache_dir / "no_symlink_models" / f"faster-whisper-{model_name}"

                        logger.info(f"🔄 Fallback: symlink無効モードでダウンロード開始...")
                        logger.info(f"   キャッシュディレクトリ: {cache_dir}")
                        logger.info(f"   実体ファイル展開先: {fallback_dir}")

                        # 中途半端なダウンロードが残っている場合に備えて削除
                        if fallback_dir.exists():
                            logger.info(f"   既存のfallbackディレクトリを削除: {fallback_dir}")
                            shutil.rmtree(fallback_dir)

                        # ディレクトリ作成
                        fallback_dir.mkdir(parents=True, exist_ok=True)
                        logger.info(f"   fallbackディレクトリを作成: {fallback_dir}")

                        # snapshot_downloadでモデルをダウンロード（symlink/hardlink完全無効）
                        logger.info(f"   モデルダウンロード中（symlink/hardlink無効、実体ファイルコピー）...")
                        model_path = snapshot_download(
                            repo_id=f"Systran/faster-whisper-{model_name}",
                            cache_dir=str(cache_dir),
                            local_dir=str(fallback_dir),  # 明示的にlocal_dirを指定
                            local_dir_use_symlinks=False,  # symlink/hardlink完全無効
                            resume_download=True,
                        )

                        logger.info(f"   ✅ ダウンロード完了: {model_path}")
                        logger.info(f"   実体ファイルが展開されました: {fallback_dir}")
                        logger.info(f"🔄 Fallbackでダウンロード完了、モデルをロード中...")

                        # fallback_dirからモデルをロード
                        self.model = WhisperModel(
                            str(fallback_dir),
                            device="cpu",
                            compute_type="int8"
                        )
                        self.current_model_name = model_name
                        elapsed = time.time() - start_time
                        logger.info(f"✅ モデルロード完了（Fallback成功、symlink無効モード）: {model_name} ({elapsed:.1f}秒)")
                        return  # 成功したら処理を抜ける

                    except Exception as fallback_error:
                        logger.error(f"❌ Fallbackでも失敗: {fallback_error}")
                        error_msg = (
                            "モデルのダウンロードに失敗しました（WinError 1314）。\n\n"
                            "symlink/hardlinkを使わない実体ファイルコピーでも失敗しました。\n"
                            "以下を確認してください:\n"
                            "1. インターネット接続\n"
                            "2. ディスク容量（約3GB必要）\n"
                            "3. セキュリティソフトの設定\n"
                            "4. ディスクの書き込み権限\n\n"
                            f"キャッシュフォルダ: {cache_dir}\n"
                            f"Fallback展開先: {fallback_dir}\n\n"
                            f"エラー詳細: {fallback_error}"
                        )
                        raise PermissionError(error_msg) from fallback_error
            else:
                error_msg = (
                    "モデルのダウンロードに失敗しました。\n\n"
                    "以下を確認してください:\n"
                    "1. インターネット接続\n"
                    "2. ディスク容量（約3GB必要）\n"
                    "3. セキュリティソフトの設定\n\n"
                    f"キャッシュフォルダ: {Path.home() / '.cache' / 'huggingface'}"
                )
                raise PermissionError(error_msg) from e

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ モデルロードエラー ({elapsed:.1f}秒経過): {e}", exc_info=True)

            # エラー種別の詳細診断
            error_str = str(e).lower()
            if "memory" in error_str or "メモリ" in error_str:
                logger.error("  → メモリ不足の可能性があります。他のアプリを終了してください。")
            elif "illegal instruction" in error_str or "sigill" in error_str:
                logger.error("  → CPU命令未対応の可能性があります（AVX/AVX2が必要）。")
            elif "ssl" in error_str or "certificate" in error_str:
                logger.error("  → SSL/証明書エラーの可能性があります。プロキシ設定を確認してください。")
            elif "timeout" in error_str or "connection" in error_str:
                logger.error("  → ネットワークエラーの可能性があります。インターネット接続を確認してください。")
            elif "disk" in error_str or "space" in error_str or "容量" in error_str:
                logger.error("  → ディスク容量不足の可能性があります（約3GB必要）。")

            raise

    def transcribe(
        self,
        audio_path: Path,
        model_name: str = "medium",
        language: str = "ja",
        progress_callback=None,
    ) -> dict[str, Any]:
        """
        音声ファイルを文字起こし

        Args:
            audio_path: 音声ファイルパス
            model_name: 使用するモデル
            language: 言語コード
            progress_callback: 進捗コールバック関数（0.0～1.0の進捗を受け取る）

        Returns:
            文字起こし結果
        """
        try:
            # モデルをロード
            self.load_model(model_name)

            logger.info(f"文字起こし開始: {audio_path.name}")
            start_time = time.time()

            # 文字起こし実行
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )

            # 音声の総時間を取得
            total_duration = info.duration if hasattr(info, "duration") else None

            # セグメントをテキストに変換
            text_segments = []
            segment_list = []

            for segment in segments:
                text = segment.text.strip()
                text_segments.append(text)
                segment_list.append({"start": segment.start, "end": segment.end, "text": text})

                # 進捗を通知（セグメント終了時間 / 総時間）
                if progress_callback and total_duration and total_duration > 0:
                    progress = min(
                        segment.end / total_duration, 0.95
                    )  # 最大95%まで（最後は処理完了で100%）
                    progress_callback(progress)

            # テキストを結合
            result_text = "".join(text_segments)

            logger.info(f"改行処理前: {len(result_text)}文字")
            logger.info(f"改行処理前の最初の100文字: {result_text[:100]}")

            # 改行処理を適用
            # 1. 句点（。）の後に改行を追加
            result_text = re.sub(r"。(?=[^」』）\)\n])", "。\n", result_text)

            # 2. 疑問符・感嘆符の後にも改行
            result_text = re.sub(r"([！？])(?=[^」』）\)\n])", r"\1\n", result_text)

            # 3. 改行数をカウント
            linebreak_count = result_text.count("\n")

            # 4. 句点が少ない場合（10個未満）は追加の改行処理
            if linebreak_count < 10:
                logger.info(f"句点が少ない（{linebreak_count}個）ため、追加の改行処理を実行")

                # 「って」「だって」「から」「けど」「よ」「ね」「わ」の後に改行
                result_text = re.sub(
                    r"(って|だって|から|けど|けども|もん|もんね)(?=[^」』）\)\n])",
                    r"\1\n",
                    result_text,
                )

                # 読点（、）の後でも改行（ただし、短い区切りは避ける）
                # 読点の後が20文字以上続いている場合のみ改行
                result_text = re.sub(r"、([^、\n]{20,})", r"、\n\1", result_text)

            # 5. 連続する改行を1つにまとめる
            result_text = re.sub(r"\n+", "\n", result_text)

            # 6. 先頭と末尾の空白・改行を削除
            result_text = result_text.strip()

            logger.info(f"改行処理後: {len(result_text)}文字")
            logger.info(f"改行数: {result_text.count(chr(10))}")
            logger.info(f"改行処理後の最初の200文字: {result_text[:200]}")

            elapsed = time.time() - start_time

            logger.info(f"✅ 文字起こし完了: {len(result_text)}文字 ({elapsed:.1f}秒)")

            return {
                "success": True,
                "text": result_text,
                "segments": segment_list,
                "duration": elapsed,
                "language": info.language,
                "char_count": len(result_text),
                "segment_count": len(segment_list),
            }

        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"❌ 文字起こしエラー: {e}", exc_info=True)

            # 音声フォーマット関連のエラー診断
            user_message = str(e)
            if "codec" in error_str or "decoder" in error_str:
                logger.error("  → 音声コーデックエラー: サポートされていない形式の可能性があります。")
                user_message = "音声形式がサポートされていません。MP3, WAV, M4A, FLAC, OGG形式をお試しください。"
            elif "sample" in error_str and ("rate" in error_str or "format" in error_str):
                logger.error("  → サンプリングレート/フォーマットエラー: 特殊な音声フォーマットの可能性があります。")
                user_message = "音声フォーマットが特殊です。標準的なMP3/WAVファイルに変換してお試しください。"
            elif "channel" in error_str:
                logger.error("  → チャンネルエラー: マルチチャンネル音声の可能性があります。")
                user_message = "マルチチャンネル音声は対応していません。ステレオまたはモノラルに変換してください。"
            elif "ffmpeg" in error_str or "avcodec" in error_str or "av" in error_str:
                logger.error("  → FFmpeg/PyAVエラー: 音声デコードに失敗しました。")
                user_message = "音声ファイルの読み込みに失敗しました。ファイルが破損していないか確認してください。"
            elif "memory" in error_str:
                logger.error("  → メモリエラー: 大きなファイルの処理でメモリ不足の可能性があります。")
                user_message = "メモリ不足です。他のアプリを終了するか、より小さいファイルをお試しください。"

            return {"success": False, "error": user_message}


# グローバルインスタンス（シングルトン）
transcription_service = TranscriptionService()
