#!/usr/bin/env bash

# ============================================================================
# Daily Statistics Collection Setup Script
# ============================================================================
#
# このスクリプトは、毎日00:00に自動実行されるcron jobを設定します。
#
# 使用方法:
#   ./scripts/setup_daily_stats.sh
#
# ============================================================================

set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ""
echo "=========================================="
echo "ダウンロード統計の自動収集設定"
echo "=========================================="
echo ""

# 必要なディレクトリを作成
mkdir -p "$PROJECT_ROOT/stats"
mkdir -p "$PROJECT_ROOT/logs"

echo "✅ 出力ディレクトリを作成しました:"
echo "   - $PROJECT_ROOT/stats (統計データ)"
echo "   - $PROJECT_ROOT/logs (実行ログ)"
echo ""

# cron設定の表示
CRON_COMMAND="0 0 * * * cd $PROJECT_ROOT && ./scripts/daily_stats_collect.sh >> $PROJECT_ROOT/logs/cron.log 2>&1"

echo "=========================================="
echo "cron設定"
echo "=========================================="
echo ""
echo "以下のコマンドをcrontabに追加してください:"
echo ""
echo "$CRON_COMMAND"
echo ""
echo "設定手順:"
echo ""
echo "1. crontabを開く:"
echo "   crontab -e"
echo ""
echo "2. 上記のコマンドを追加して保存"
echo ""
echo "3. 設定を確認:"
echo "   crontab -l"
echo ""

# テスト実行
echo "=========================================="
echo "テスト実行"
echo "=========================================="
echo ""
echo "スクリプトをテスト実行しますか? [y/N]"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "テスト実行中..."
    echo ""

    if "$PROJECT_ROOT/scripts/daily_stats_collect.sh"; then
        echo ""
        echo "✅ テスト実行成功!"
        echo ""
        echo "生成されたファイル:"
        ls -lh "$PROJECT_ROOT/stats/"
        echo ""
        echo "ログファイル:"
        tail -n 20 "$PROJECT_ROOT/logs/stats_collection.log"
    else
        echo ""
        echo "❌ テスト実行に失敗しました"
        exit 1
    fi
else
    echo ""
    echo "テスト実行をスキップしました"
fi

echo ""
echo "=========================================="
echo "セットアップ完了"
echo "=========================================="
echo ""
echo "📝 メモ:"
echo "  - 毎日00:00に自動実行されます"
echo "  - 統計データは stats/ に保存されます"
echo "  - 実行ログは logs/ に保存されます"
echo "  - GITHUB_TOKEN環境変数を設定することを推奨します"
echo ""
echo "環境変数の設定方法:"
echo "  ~/.zshrc または ~/.bash_profile に以下を追加:"
echo "  export GITHUB_TOKEN=\"your_github_token_here\""
echo ""

exit 0
