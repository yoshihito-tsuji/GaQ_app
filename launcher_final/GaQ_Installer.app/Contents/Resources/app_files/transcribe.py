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
    文字起こし結果に適切な改行を追加

    - 句読点（。！？）の後に改行
    - 80文字程度で自然に折り返し
    - 連続する改行は2つまでに制限

    Args:
        text: 改行なしの文字起こし結果

    Returns:
        改行を追加した読みやすいテキスト
    """
    # 句読点で分割（句読点も保持）
    sentences = re.split(r'([。！？])', text)

    # 分割した文と句読点を再結合
    merged_sentences = []
    for i in range(0, len(sentences)-1, 2):
        if i+1 < len(sentences):
            merged_sentences.append(sentences[i] + sentences[i+1])

    # 最後の要素が句読点なしの場合
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        merged_sentences.append(sentences[-1])

    # 80文字程度で折り返し
    formatted_lines = []
    current_line = ""
    max_length = 80

    for sentence in merged_sentences:
        if len(current_line) + len(sentence) > max_length and current_line:
            formatted_lines.append(current_line.strip())
            current_line = sentence
        else:
            current_line += sentence

    if current_line:
        formatted_lines.append(current_line.strip())

    # 結合して返す
    result = '\n'.join(formatted_lines)

    # 連続する改行を2つまでに制限
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


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

                # 進捗を通知（10%から85%の範囲で）
                if progress_callback and total_duration and total_duration > 0:
                    progress = 0.10 + (segment.end / total_duration) * 0.75  # 10%〜85%
                    progress_callback(min(progress, 0.85))  # 最大85%まで

            # テキストを結合
            result_text = "".join(text_segments)

            # 改行処理（進捗90%）
            if progress_callback:
                progress_callback(0.90)

            logger.info(f"改行処理前: {len(result_text)}文字")
            logger.info(f"改行処理前の最初の100文字: {result_text[:100]}")

            # 句点の数をカウント
            period_count = result_text.count("。")
            logger.info(f"句点の数: {period_count}")

            # 改行処理（format_text_with_linebreaks関数を使用）
            result_text = format_text_with_linebreaks(result_text)

            # 句点が極端に少ない場合の追加処理
            if period_count < 3 and len(result_text) > 300:
                logger.info(f"句点が少ない（{period_count}個）長文のため、追加の改行処理を実行")
                # 既に80文字で折り返し済みだが、句点がない場合は更に細かく分割
                lines = []
                for i in range(0, len(result_text), 60):
                    lines.append(result_text[i : i + 60])
                result_text = "\n".join(lines)

            logger.info(f"改行処理後: {len(result_text)}文字")
            logger.info(f"改行数: {result_text.count(chr(10))}")
            logger.info(f"改行処理後の最初の200文字: {result_text[:200]}")

            # 完了（進捗95%）
            if progress_callback:
                progress_callback(0.95)

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
            logger.error(f"❌ 文字起こしエラー: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


# グローバルインスタンス（シングルトン）
transcription_service = TranscriptionService()
