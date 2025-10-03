#!/bin/bash
#
# GaQ Offline Transcriber - セットアップスクリプト
# Python環境構築と依存関係インストール
#

set -e

RESOURCES_DIR="$1"
APP_DIR="$2"
LOG_FILE="$APP_DIR/install.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error_exit() {
    log "ERROR: $1"
    exit 1
}

log "=== GaQ Offline Transcriber セットアップ開始 ==="

# Python 3確認
log "Python環境を確認中..."
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3がインストールされていません。\nHomebrewでインストールしてください:\nbrew install python@3.11"
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
log "Python バージョン: $PYTHON_VERSION"

# 仮想環境作成
log "Python仮想環境を作成中..."
python3 -m venv "$APP_DIR/venv" || error_exit "仮想環境の作成に失敗しました"

# 仮想環境をアクティベート
source "$APP_DIR/venv/bin/activate" || error_exit "仮想環境のアクティベーションに失敗しました"

# pip更新
log "pipを更新中..."
pip install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1 || log "WARNING: pip更新に失敗しましたが続行します"

# 依存関係インストール
log "依存パッケージをインストール中（数分かかります）..."
pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    faster-whisper>=1.0.0 \
    aiofiles==23.2.1 \
    requests>=2.25.0 >> "$LOG_FILE" 2>&1 || error_exit "依存パッケージのインストールに失敗しました"

log "依存パッケージのインストール完了"

# アプリファイルをコピー
log "アプリケーションファイルをコピー中..."
mkdir -p "$APP_DIR/app"
cp -r "$RESOURCES_DIR/app_files/"* "$APP_DIR/app/" || error_exit "アプリファイルのコピーに失敗しました"

# 起動スクリプト作成
log "起動スクリプトを作成中..."
cat > "$APP_DIR/run_gaq.sh" << 'EOF'
#!/bin/bash
# GaQ Offline Transcriber 起動スクリプト

APP_DIR="$HOME/.gaq"
cd "$APP_DIR/app"

# 仮想環境をアクティベート
source "$APP_DIR/venv/bin/activate"

# ポート使用確認
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "ポート8000は既に使用されています。ブラウザでhttp://127.0.0.1:8000を開いてください。"
    # キオスクモードでChromeを起動（UI完全非表示）
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
        --app=http://127.0.0.1:8000 \
        --kiosk \
        --disable-infobars \
        --disable-session-crashed-bubble \
        --disable-restore-session-state \
        --no-first-run \
        --no-default-browser-check \
        > /dev/null 2>&1 &
    exit 0
fi

# FastAPIサーバー起動
echo "GaQ Offline Transcriber を起動中..."
python3 main.py &
SERVER_PID=$!

# サーバー起動待機
sleep 3

# キオスクモードでChromeを起動（UI完全非表示）
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --app=http://127.0.0.1:8000 \
    --kiosk \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-restore-session-state \
    --no-first-run \
    --no-default-browser-check \
    > /dev/null 2>&1 &

echo "GaQ Offline Transcriber が起動しました"
echo "終了するには Ctrl+C を押してください"

# サーバーを待機
wait $SERVER_PID
EOF

chmod +x "$APP_DIR/run_gaq.sh"

log "=== セットアップ完了 ==="
exit 0
