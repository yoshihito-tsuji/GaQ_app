#!/bin/bash
#
# GaQ Offline Transcriber - Mac版ビルドスクリプト
# Python 3.12系を使用してビルドを実行します
#

set -e  # エラー時に停止

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== GaQ Offline Transcriber - Mac版ビルド ==="
echo ""

# Python 3.12の確認
echo "1. Pythonバージョン確認..."
# システムにインストールされているpython3.12を使用
PYTHON_CMD=$(which python3.12 2>/dev/null || echo "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12")

if [ ! -f "$PYTHON_CMD" ]; then
    echo -e "${RED}エラー: Python 3.12が見つかりません${NC}"
    echo ""
    echo "以下のコマンドでインストールしてください:"
    echo "  brew install python@3.12"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d. -f1,2)

if [ "$PYTHON_MAJOR_MINOR" != "3.12" ]; then
    echo -e "${RED}エラー: Python 3.12が必要ですが、$PYTHON_VERSION が見つかりました${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION を使用します${NC}"
echo ""

# 仮想環境の確認と作成
echo "2. 仮想環境の確認..."
if [ ! -d "venv" ]; then
    echo "仮想環境を作成中..."
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ 仮想環境を作成しました${NC}"
else
    echo -e "${GREEN}✓ 既存の仮想環境を使用します${NC}"
fi
echo ""

# 仮想環境をアクティベート
source venv/bin/activate

# 仮想環境のPythonバージョン確認
VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
VENV_PYTHON_MAJOR_MINOR=$(echo $VENV_PYTHON_VERSION | cut -d. -f1,2)

if [ "$VENV_PYTHON_MAJOR_MINOR" != "3.12" ]; then
    echo -e "${YELLOW}警告: 仮想環境のPythonバージョンが異なります (${VENV_PYTHON_VERSION})${NC}"
    echo "仮想環境を再作成します..."
    deactivate 2>/dev/null || true
    rm -rf venv
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✓ 仮想環境を再作成しました${NC}"
fi
echo ""

# 依存パッケージのインストール
echo "3. 依存パッケージのインストール..."
pip install --upgrade pip > /dev/null
pip install -r src/requirements.txt > /dev/null
pip install pyinstaller > /dev/null
pip install Pillow > /dev/null
echo -e "${GREEN}✓ 依存パッケージをインストールしました${NC}"
echo ""

# PyInstallerバージョン確認
PYINSTALLER_VERSION=$(pyinstaller --version)
echo "PyInstaller: $PYINSTALLER_VERSION"
echo ""

# ビルド実行
echo "4. PyInstallerでビルド実行..."
pyinstaller --clean -y GaQ_Transcriber.spec

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ ビルドが成功しました！${NC}"
    echo ""
    echo "成果物:"
    echo "  dist/GaQ Offline Transcriber.app"
    ls -lh "dist/GaQ Offline Transcriber.app" 2>/dev/null || echo "  (サイズ情報の取得に失敗)"
    du -sh "dist/GaQ Offline Transcriber.app" 2>/dev/null || true
else
    echo -e "${RED}エラー: ビルドに失敗しました${NC}"
    exit 1
fi

echo ""
echo "=== ビルド完了 ==="
echo ""

# DMG作成
echo -e "${YELLOW}5. DMGパッケージを作成しています...${NC}"

APP_NAME="GaQ Offline Transcriber"
DMG_NAME="GaQ_Transcriber_v1.1.1_mac.dmg"
DMG_TEMP_DIR="dmg_temp"
DMG_ASSETS_DIR="dmg_assets"

# 一時ディレクトリを作成
rm -rf "$DMG_TEMP_DIR"
mkdir -p "$DMG_TEMP_DIR"

# アプリをコピー
echo "アプリをコピーしています..."
cp -R "dist/$APP_NAME.app" "$DMG_TEMP_DIR/"

# DMG用ファイルをコピー
if [ -d "$DMG_ASSETS_DIR" ]; then
    echo "インストールガイドとセットアップスクリプトをコピーしています..."
    cp "$DMG_ASSETS_DIR/インストール方法.txt" "$DMG_TEMP_DIR/"
    cp "$DMG_ASSETS_DIR/GaQ セットアップ.command" "$DMG_TEMP_DIR/"
    chmod +x "$DMG_TEMP_DIR/GaQ セットアップ.command"
fi

# Applications フォルダへのシンボリックリンクを作成
echo "Applicationsフォルダへのリンクを作成しています..."
ln -s /Applications "$DMG_TEMP_DIR/Applications"

# 既存のDMGを削除
if [ -f "dist/$DMG_NAME" ]; then
    rm "dist/$DMG_NAME"
fi

# DMGを作成
echo "DMGを作成しています..."
hdiutil create \
    -volname "$APP_NAME v1.1.1" \
    -srcfolder "$DMG_TEMP_DIR" \
    -ov \
    -format UDZO \
    "dist/$DMG_NAME"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ DMGパッケージを作成しました！${NC}"
    echo ""
    echo "成果物:"
    echo "  dist/$DMG_NAME"
    ls -lh "dist/$DMG_NAME" 2>/dev/null || echo "  (サイズ情報の取得に失敗)"

    # DMGサイズを表示
    DMG_SIZE=$(du -h "dist/$DMG_NAME" | awk '{print $1}')
    echo "  DMGサイズ: $DMG_SIZE"
else
    echo -e "${YELLOW}警告: DMGの作成に失敗しました${NC}"
    echo "手動でDMGを作成してください"
fi

# 一時ディレクトリを削除
rm -rf "$DMG_TEMP_DIR"

echo ""
echo "=== すべて完了 ==="
