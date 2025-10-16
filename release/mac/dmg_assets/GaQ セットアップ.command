#!/bin/bash
#
# GaQ Offline Transcriber v1.1.1 - 自動セットアップスクリプト
# このスクリプトはアプリケーションのインストールとセキュリティ設定を自動化します
#

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GaQ Offline Transcriber v1.1.1${NC}"
echo -e "${BLUE}  自動セットアップ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# アプリケーション名
APP_NAME="GaQ Offline Transcriber.app"

# DMGマウントポイント（このスクリプトがDMG内にあると仮定）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DMG_APP="$SCRIPT_DIR/$APP_NAME"

# インストール先
INSTALL_DIR="/Applications"
INSTALLED_APP="$INSTALL_DIR/$APP_NAME"

echo -e "${YELLOW}ステップ 1/3: アプリケーションを確認しています...${NC}"
if [ ! -d "$DMG_APP" ]; then
    echo -e "${RED}エラー: $APP_NAME が見つかりません${NC}"
    echo "DMGを開いて、このスクリプトが正しい場所から実行されているか確認してください。"
    exit 1
fi
echo -e "${GREEN}✓ アプリケーションを確認しました${NC}"
echo ""

echo -e "${YELLOW}ステップ 2/3: アプリケーションをインストールしています...${NC}"
echo "インストール先: $INSTALL_DIR"

# 既存のアプリがあれば削除
if [ -d "$INSTALLED_APP" ]; then
    echo -e "${YELLOW}既存のバージョンを削除しています...${NC}"
    rm -rf "$INSTALLED_APP"
fi

# アプリケーションをコピー
cp -R "$DMG_APP" "$INSTALL_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ アプリケーションをインストールしました${NC}"
else
    echo -e "${RED}エラー: アプリケーションのインストールに失敗しました${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}ステップ 3/3: セキュリティ設定を解除しています...${NC}"
echo "macOSのGatekeeperセキュリティ属性を削除します..."

# Quarantine属性を削除（管理者権限が必要）
sudo xattr -dr com.apple.quarantine "$INSTALLED_APP"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ セキュリティ設定を解除しました${NC}"
else
    echo -e "${RED}警告: セキュリティ設定の解除に失敗しました${NC}"
    echo "手動で実行してください:"
    echo "  xattr -dr com.apple.quarantine \"$INSTALLED_APP\""
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  セットアップが完了しました！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}次の手順:${NC}"
echo "1. 「アプリケーション」フォルダを開く"
echo "2. 「GaQ Offline Transcriber」をダブルクリックして起動"
echo ""
echo -e "${YELLOW}初回起動時の注意:${NC}"
echo "• 音声認識モデル（約1.5～2.9GB）を自動ダウンロードします"
echo "• ダウンロード後は完全オフラインで動作します"
echo ""
echo -e "${BLUE}お問い合わせ:${NC}"
echo "https://tsuji-lab.net"
echo ""

# アプリケーションフォルダを開く
echo -e "${YELLOW}アプリケーションフォルダを開いています...${NC}"
open "$INSTALL_DIR"

echo ""
echo -e "${GREEN}Press any key to close this window...${NC}"
read -n 1 -s
