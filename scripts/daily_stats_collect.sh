#!/usr/bin/env bash

# ============================================================================
# Daily Download Statistics Collection Script
# ============================================================================
#
# このスクリプトは、毎日00:00に自動実行されることを想定しています。
#
# 機能:
#   - ダウンロード統計をCSV形式で収集
#   - 日付別のファイルに保存
#   - ログファイルに実行結果を記録
#
# 設定方法:
#   crontabに以下を追加:
#   0 0 * * * cd /Users/ytsuji/dev/GaQ_app && ./scripts/daily_stats_collect.sh >> /Users/ytsuji/dev/GaQ_app/logs/cron.log 2>&1
#
# ============================================================================

set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 出力ディレクトリ
STATS_DIR="$PROJECT_ROOT/stats"
LOGS_DIR="$PROJECT_ROOT/logs"

# ディレクトリが存在しない場合は作成
mkdir -p "$STATS_DIR"
mkdir -p "$LOGS_DIR"

# 日付
TODAY=$(date +"%Y-%m-%d")
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# ログファイル
LOG_FILE="$LOGS_DIR/stats_collection.log"

# ============================================================================
# ログ関数
# ============================================================================

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# ============================================================================
# メイン処理
# ============================================================================

log "=========================================="
log "ダウンロード統計収集開始"
log "=========================================="

# CSV出力ファイル
CSV_FILE="$STATS_DIR/downloads_${TODAY}.csv"

log "出力先: $CSV_FILE"

# Python3の存在確認
if ! command -v python3 &> /dev/null; then
    log "エラー: python3が見つかりません"
    exit 1
fi

# スクリプト実行
cd "$PROJECT_ROOT"

if python3 scripts/check_download_stats.py --csv > "$CSV_FILE" 2>&1; then
    LINES=$(wc -l < "$CSV_FILE" | tr -d ' ')
    log "成功: $LINES 行のデータを収集しました"

    # 合計ダウンロード数を計算（ヘッダー行を除く）
    if [ "$LINES" -gt 1 ]; then
        TOTAL=$(awk -F',' 'NR>1 {sum+=$5} END {print sum}' "$CSV_FILE")
        log "合計ダウンロード数: $TOTAL"
    fi
else
    log "エラー: スクリプト実行に失敗しました"
    exit 1
fi

log "=========================================="
log "ダウンロード統計収集完了"
log "=========================================="
log ""

exit 0
