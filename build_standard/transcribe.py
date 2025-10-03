"""
文字起こし処理モジュール
faster-whisperを使用した音声認識
"""

import logging
import re
import shutil
import time
from pathlib import Path
from typing import Any, Optional

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


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
        logger.info(f"✅ モデル削除完了: {model_name}")
        return {"success": True, "message": f"モデル {model_name} を削除しました"}
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
        モデルをロード（初回は自動ダウンロード）

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

        logger.info(f"モデル '{model_name}' をロード中...")
        start_time = time.time()

        # faster-whisperが自動でダウンロード
        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")

        self.current_model_name = model_name
        elapsed = time.time() - start_time

        logger.info(f"✅ モデルロード完了: {model_name} ({elapsed:.1f}秒)")

    def transcribe(
        self,
        audio_path: Path,
        model_name: str = "medium",
        language: str = "ja",
    ) -> dict[str, Any]:
        """
        音声ファイルを文字起こし

        Args:
            audio_path: 音声ファイルのパス
            model_name: 使用するモデル名（medium, large-v3）
            language: 言語コード（ja, en）

        Returns:
            dict: {
                'text': str,          # 文字起こしテキスト
                'segments': list,     # セグメント情報
                'duration': float,    # 処理時間
                'language': str       # 検出言語
            }
        """
        # モデルロード
        self.load_model(model_name)

        logger.info(f"文字起こし開始: {audio_path.name}")
        start_time = time.time()

        # 文字起こし実行
        segments, info = self.model.transcribe(
            str(audio_path), language=language, beam_size=5, vad_filter=True
        )

        # セグメントをリストに変換
        segment_list = []
        full_text = ""

        for segment in segments:
            segment_data = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
            }
            segment_list.append(segment_data)
            full_text += segment.text

        # 改行処理
        logger.info(f"改行処理前: {len(full_text)}文字")
        logger.info(f"改行処理前の最初の100文字: {full_text[:100]}")

        # 句点の数をカウント
        period_count = full_text.count("。")
        logger.info(f"句点の数: {period_count}")

        # 改行処理
        formatted_text = format_text_with_linebreaks(full_text)

        # 句点が少ない場合は追加の改行処理
        if period_count < 3:
            logger.info(f"句点が少ない（{period_count}個）ため、追加の改行処理を実行")
            # 50文字ごとに改行を追加
            lines = []
            for i in range(0, len(formatted_text), 50):
                lines.append(formatted_text[i : i + 50])
            formatted_text = "\n".join(lines)

        logger.info(f"改行処理後: {len(formatted_text)}文字")
        logger.info(f"改行数: {formatted_text.count(chr(10))}")
        logger.info(f"改行処理後の最初の200文字: {formatted_text[:200]}")

        duration = time.time() - start_time

        logger.info(f"✅ 文字起こし完了: {len(formatted_text)}文字 ({duration:.1f}秒)")

        return {
            "text": formatted_text,
            "segments": segment_list,
            "duration": duration,
            "language": info.language,
        }


# グローバルインスタンス
transcription_service = TranscriptionService()
