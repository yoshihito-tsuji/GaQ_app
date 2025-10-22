#!/bin/bash
# JavaScript実行テスト用スクリプト
# 極小テストページ /test で pywebview の JavaScript 実行を検証

set -e

echo "=== GaQ JavaScript 実行テスト ==="
echo ""
echo "このスクリプトは以下をテストします："
echo "1. /test エンドポイントで極小HTMLを配信"
echo "2. pywebview で JavaScript が実行されるか確認"
echo "3. デバッグモードでWebKit Inspector を有効化"
echo ""

# 既存のアプリを終了
echo "既存のアプリケーションを終了中..."
pkill -f "GaQ_Transcriber" || true
pkill -f "GaQ Offline Transcriber" || true
sleep 2

# ログファイルをクリア
LOG_FILE="$HOME/.gaq/logs/app.log"
if [ -f "$LOG_FILE" ]; then
    echo "ログファイルをクリア: $LOG_FILE"
    > "$LOG_FILE"
fi

# 環境変数設定
export GAQ_TEST_MODE=1          # /test ページを開く
export GAQ_WEBVIEW_DEBUG=1      # WebKit Inspector 有効化

echo ""
echo "環境変数:"
echo "  GAQ_TEST_MODE=1 (テストページモード)"
echo "  GAQ_WEBVIEW_DEBUG=1 (デバッグモード)"
echo ""

# アプリを起動
APP_PATH="dist/GaQ Offline Transcriber.app/Contents/MacOS/GaQ_Transcriber"

if [ ! -f "$APP_PATH" ]; then
    echo "❌ エラー: アプリが見つかりません: $APP_PATH"
    echo "先にビルドしてください: bash build.sh"
    exit 1
fi

echo "アプリを起動します..."
echo "ウィンドウが表示されたら、以下を確認してください："
echo ""
echo "【確認事項】"
echo "1. Alertダイアログ「🎉 Alert works!」が表示される"
echo "2. ページに「✅ JavaScript executed successfully!」と表示される"
echo "3. ログファイルに [TEST] pywebview API is available! が記録される"
echo ""
echo "【WebKit Inspector の使い方（macOS）】"
echo "1. Safari → 開発 → localhost を選択"
echo "2. JavaScript コンソールでエラーを確認"
echo ""

# アプリを起動（バックグラウンド）
"$APP_PATH" &
APP_PID=$!

echo "アプリ起動: PID=$APP_PID"
echo ""
echo "ログを監視中（Ctrl+C で終了）..."
echo "---"

# ログをtail
sleep 3
tail -f "$LOG_FILE" | grep --line-buffered -E "TEST|JavaScript|error|Error|alert"
