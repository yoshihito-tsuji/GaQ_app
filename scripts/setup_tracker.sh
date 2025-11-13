#!/bin/bash
#
# ダウンロード追跡システム セットアップスクリプト
#
# 目的: launchdサービスを自動的にインストール・設定する
#
# 使用方法:
#   ./scripts/setup_tracker.sh
#

set -e

# 色設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo "ダウンロード追跡システム セットアップ"
echo "========================================${NC}"
echo ""

# 必要なディレクトリとファイルの存在確認
SCRIPT_DIR="/Users/yoshihitotsuji/Claude_Code/GaQ_app/scripts"
PLIST_SOURCE="${SCRIPT_DIR}/com.gaq.download-tracker.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.gaq.download-tracker.plist"
TRACK_SCRIPT="${SCRIPT_DIR}/track_downloads.sh"

if [ ! -f "${PLIST_SOURCE}" ]; then
    echo -e "${RED}✗ plistファイルが見つかりません: ${PLIST_SOURCE}${NC}"
    exit 1
fi

if [ ! -f "${TRACK_SCRIPT}" ]; then
    echo -e "${RED}✗ 追跡スクリプトが見つかりません: ${TRACK_SCRIPT}${NC}"
    exit 1
fi

# GitHub CLI の確認
echo -e "${BLUE}[1/5] 環境確認${NC}"
if ! command -v gh &> /dev/null; then
    echo -e "${RED}✗ GitHub CLI (gh) がインストールされていません${NC}"
    echo "  インストール方法: brew install gh"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI がインストールされています${NC}"

# GitHub 認証確認
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠ GitHub CLI が認証されていません${NC}"
    echo "  認証を開始しますか? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        gh auth login
    else
        echo -e "${RED}✗ GitHub認証が必要です${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ GitHub CLI が認証されています${NC}"
echo ""

# スクリプトに実行権限を付与
echo -e "${BLUE}[2/5] スクリプトの実行権限設定${NC}"
chmod +x "${TRACK_SCRIPT}"
echo -e "${GREEN}✓ 実行権限を設定しました${NC}"
echo ""

# LaunchAgents ディレクトリの作成
echo -e "${BLUE}[3/5] LaunchAgents ディレクトリの準備${NC}"
mkdir -p "$HOME/Library/LaunchAgents"
echo -e "${GREEN}✓ ディレクトリを確認しました${NC}"
echo ""

# 既存のサービスを停止
echo -e "${BLUE}[4/5] 既存サービスの確認${NC}"
if [ -f "${PLIST_DEST}" ]; then
    echo -e "${YELLOW}既存のサービスが見つかりました。停止します...${NC}"
    launchctl unload "${PLIST_DEST}" 2>/dev/null || true
    echo -e "${GREEN}✓ 既存サービスを停止しました${NC}"
fi
echo ""

# plist ファイルをコピー
echo -e "${BLUE}[5/5] サービスのインストール${NC}"
cp "${PLIST_SOURCE}" "${PLIST_DEST}"
echo -e "${GREEN}✓ plistファイルをコピーしました${NC}"

# サービスを読み込み
launchctl load "${PLIST_DEST}"
echo -e "${GREEN}✓ サービスを読み込みました${NC}"
echo ""

# テスト実行
echo -e "${BLUE}========================================"
echo "テスト実行"
echo "========================================${NC}"
echo ""
echo "スクリプトをテスト実行しますか? (y/n)"
read -r answer
if [ "$answer" = "y" ]; then
    echo ""
    "${TRACK_SCRIPT}"
    echo ""
fi

# 完了メッセージ
echo -e "${BLUE}========================================"
echo "セットアップ完了"
echo "========================================${NC}"
echo ""
echo -e "${GREEN}✅ ダウンロード追跡システムのセットアップが完了しました${NC}"
echo ""
echo "【設定内容】"
echo "  - 実行スケジュール: 毎日23:55"
echo "  - 対象リポジトリ: GaQ_app, Pop_app"
echo "  - ログファイル: /Users/yoshihitotsuji/Claude_Code/AccessLog/"
echo "  - サービス名: com.gaq.download-tracker"
echo ""
echo "【サービスの管理】"
echo "  確認: launchctl list | grep gaq"
echo "  手動実行: launchctl start com.gaq.download-tracker"
echo "  停止: launchctl stop com.gaq.download-tracker"
echo "  無効化: launchctl unload ~/Library/LaunchAgents/com.gaq.download-tracker.plist"
echo ""
echo "【ログの確認】"
echo "  実行ログ: cat /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker.log"
echo "  エラーログ: cat /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker_error.log"
echo "  ダウンロード数: cat /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv"
echo ""
echo "詳細は DOWNLOAD_TRACKER_SETUP.md をご覧ください"
echo ""
