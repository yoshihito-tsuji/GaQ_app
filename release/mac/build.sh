#!/bin/bash
#
# GaQ Offline Transcriber - Mac版ビルドスクリプト
# Python 3.12系を使用してビルドを実行します
#
# 署名・公証オプション:
#   --sign        : Developer IDで署名を実行
#   --notarize    : Apple公証を実行（--signを含む）
#   --skip-dmg    : DMG作成をスキップ
#
# 環境変数:
#   DEVELOPER_ID  : Developer ID証明書名（例: "Developer ID Application: Your Name (TEAM_ID)"）
#   APPLE_ID      : Apple ID（公証用）
#   APPLE_PASSWORD: App固有パスワード（公証用、Keychainプロファイル "notarytool" 推奨）
#   TEAM_ID       : Apple Developer Team ID（公証用）
#

set -e  # エラー時に停止

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# コマンドライン引数の解析
DO_SIGN=false
DO_NOTARIZE=false
SKIP_DMG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --sign)
            DO_SIGN=true
            shift
            ;;
        --notarize)
            DO_SIGN=true
            DO_NOTARIZE=true
            shift
            ;;
        --skip-dmg)
            SKIP_DMG=true
            shift
            ;;
        *)
            echo -e "${RED}不明なオプション: $1${NC}"
            echo "使用方法: ./build.sh [--sign] [--notarize] [--skip-dmg]"
            exit 1
            ;;
    esac
done

echo "=== GaQ Offline Transcriber - Mac版ビルド ==="
echo ""
if [ "$DO_SIGN" = true ]; then
    echo -e "${BLUE}署名モード: 有効${NC}"
fi
if [ "$DO_NOTARIZE" = true ]; then
    echo -e "${BLUE}公証モード: 有効${NC}"
fi
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

# ========================================
# 署名処理
# ========================================
if [ "$DO_SIGN" = true ]; then
    echo -e "${YELLOW}5. アプリケーションに署名しています...${NC}"

    # Developer ID証明書の確認
    if [ -z "$DEVELOPER_ID" ]; then
        # 利用可能な証明書を検索
        AVAILABLE_CERT=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | sed 's/.*"\(.*\)"/\1/')
        if [ -z "$AVAILABLE_CERT" ]; then
            echo -e "${RED}エラー: Developer ID Application証明書が見つかりません${NC}"
            echo "DEVELOPER_ID環境変数を設定するか、Keychainに証明書をインストールしてください"
            echo ""
            echo "利用可能な証明書:"
            security find-identity -v -p codesigning
            exit 1
        fi
        DEVELOPER_ID="$AVAILABLE_CERT"
        echo "使用する証明書: $DEVELOPER_ID"
    fi

    APP_PATH="dist/GaQ Offline Transcriber.app"

    # 署名前にQuarantine属性を削除
    xattr -cr "$APP_PATH" 2>/dev/null || true

    # deep署名（すべてのバンドル内コンポーネントに署名）
    echo "署名を実行中..."
    codesign --deep --force --options runtime \
        --sign "$DEVELOPER_ID" \
        --timestamp \
        "$APP_PATH"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 署名が完了しました${NC}"

        # 署名の検証
        echo "署名を検証中..."
        codesign --verify --deep --strict --verbose=2 "$APP_PATH"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 署名の検証に成功しました${NC}"
        else
            echo -e "${YELLOW}警告: 署名の検証でエラーが発生しました${NC}"
        fi
    else
        echo -e "${RED}エラー: 署名に失敗しました${NC}"
        exit 1
    fi
    echo ""
else
    echo "5. 署名をスキップ（--signオプションで有効化）"
    echo ""
fi

# ========================================
# 公証処理
# ========================================
if [ "$DO_NOTARIZE" = true ]; then
    echo -e "${YELLOW}6. Apple公証を申請しています...${NC}"

    APP_PATH="dist/GaQ Offline Transcriber.app"
    ZIP_PATH="dist/GaQ_Offline_Transcriber_for_notarization.zip"

    # Team IDの確認
    if [ -z "$TEAM_ID" ]; then
        # 証明書からTeam IDを抽出
        TEAM_ID=$(echo "$DEVELOPER_ID" | grep -oE '\([A-Z0-9]+\)$' | tr -d '()')
        if [ -z "$TEAM_ID" ]; then
            echo -e "${RED}エラー: TEAM_ID環境変数を設定してください${NC}"
            exit 1
        fi
        echo "Team ID: $TEAM_ID"
    fi

    # 公証用ZIPを作成
    echo "公証用ZIPを作成中..."
    rm -f "$ZIP_PATH"
    ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"

    # notarytool用のKeychain認証情報を確認
    # 推奨: xcrun notarytool store-credentials "notarytool" で事前に保存
    if xcrun notarytool history --keychain-profile "notarytool" > /dev/null 2>&1; then
        echo "Keychainプロファイル 'notarytool' を使用します"

        # 公証申請
        echo "公証を申請中（数分かかる場合があります）..."
        xcrun notarytool submit "$ZIP_PATH" \
            --keychain-profile "notarytool" \
            --wait

        NOTARIZE_RESULT=$?
    else
        # 環境変数から認証情報を取得
        if [ -z "$APPLE_ID" ] || [ -z "$APPLE_PASSWORD" ]; then
            echo -e "${RED}エラー: 公証には認証情報が必要です${NC}"
            echo ""
            echo "方法1: Keychainプロファイルを作成（推奨）"
            echo "  xcrun notarytool store-credentials \"notarytool\" \\"
            echo "    --apple-id \"your@email.com\" \\"
            echo "    --team-id \"$TEAM_ID\" \\"
            echo "    --password \"app-specific-password\""
            echo ""
            echo "方法2: 環境変数を設定"
            echo "  export APPLE_ID=\"your@email.com\""
            echo "  export APPLE_PASSWORD=\"app-specific-password\""
            echo "  export TEAM_ID=\"$TEAM_ID\""
            exit 1
        fi

        # 公証申請
        echo "公証を申請中（数分かかる場合があります）..."
        xcrun notarytool submit "$ZIP_PATH" \
            --apple-id "$APPLE_ID" \
            --password "$APPLE_PASSWORD" \
            --team-id "$TEAM_ID" \
            --wait

        NOTARIZE_RESULT=$?
    fi

    if [ $NOTARIZE_RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ 公証が完了しました${NC}"

        # Stapler: 公証チケットをアプリに埋め込み
        echo "公証チケットを埋め込み中..."
        xcrun stapler staple "$APP_PATH"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 公証チケットの埋め込みが完了しました${NC}"
        else
            echo -e "${YELLOW}警告: 公証チケットの埋め込みに失敗しました${NC}"
        fi

        # 公証用ZIPを削除
        rm -f "$ZIP_PATH"
    else
        echo -e "${RED}エラー: 公証に失敗しました${NC}"
        echo "詳細ログを確認してください:"
        echo "  xcrun notarytool log <submission-id> --keychain-profile notarytool"
        exit 1
    fi
    echo ""
else
    if [ "$DO_SIGN" = true ]; then
        echo "6. 公証をスキップ（--notarizeオプションで有効化）"
    fi
    echo ""
fi

# ========================================
# DMG作成
# ========================================
if [ "$SKIP_DMG" = true ]; then
    echo -e "${YELLOW}DMG作成をスキップ（--skip-dmgオプション）${NC}"
    echo ""
    echo "=== すべて完了 ==="
    exit 0
fi

echo -e "${YELLOW}7. DMGパッケージを作成しています...${NC}"

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
    echo "インストールガイドをコピーしています..."

    # 署名・公証済みの場合はxattr削除不要版のインストール方法を使用
    if [ "$DO_NOTARIZE" = true ]; then
        # 署名・公証済み版用のインストール方法（シンプル）
        cat > "$DMG_TEMP_DIR/インストール方法.txt" << 'EOF'
GaQ Offline Transcriber v1.1.1 - インストール方法
============================================

【インストール手順】

1. この画面で「GaQ Offline Transcriber」アイコンを
   「Applications」フォルダにドラッグ＆ドロップしてください。

2. アプリケーションフォルダから
   「GaQ Offline Transcriber」をダブルクリックして起動します。

【初回起動時の注意】

・音声認識モデル（約1.5～2.9GB）を自動ダウンロードします。
・ダウンロード後は完全オフラインで動作します。

【お問い合わせ】

公立はこだて未来大学 辻研究室
https://tsuji-lab.net
EOF
        echo -e "${GREEN}✓ 署名・公証済み版のインストール方法を使用${NC}"
    else
        # 開発版（未署名）用のインストール方法
        cp "$DMG_ASSETS_DIR/インストール方法.txt" "$DMG_TEMP_DIR/"
        cp "$DMG_ASSETS_DIR/GaQ セットアップ.command" "$DMG_TEMP_DIR/"
        chmod +x "$DMG_TEMP_DIR/GaQ セットアップ.command"
        echo -e "${YELLOW}開発版: セットアップスクリプト（xattr削除）を含む${NC}"
    fi
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

    # DMGへの署名（署名モードの場合）
    if [ "$DO_SIGN" = true ]; then
        echo ""
        echo "DMGに署名しています..."
        codesign --force --sign "$DEVELOPER_ID" --timestamp "dist/$DMG_NAME"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ DMGへの署名が完了しました${NC}"
        else
            echo -e "${YELLOW}警告: DMGへの署名に失敗しました${NC}"
        fi
    fi

    echo ""
    echo "成果物:"
    echo "  dist/$DMG_NAME"
    ls -lh "dist/$DMG_NAME" 2>/dev/null || echo "  (サイズ情報の取得に失敗)"

    # DMGサイズを表示
    DMG_SIZE=$(du -h "dist/$DMG_NAME" | awk '{print $1}')
    echo "  DMGサイズ: $DMG_SIZE"

    # SHA256ハッシュを生成
    echo ""
    echo "SHA256ハッシュを生成しています..."
    shasum -a 256 "dist/$DMG_NAME" > "dist/${DMG_NAME}.sha256"
    echo -e "${GREEN}✓ ハッシュファイル: dist/${DMG_NAME}.sha256${NC}"
    cat "dist/${DMG_NAME}.sha256"
else
    echo -e "${YELLOW}警告: DMGの作成に失敗しました${NC}"
    echo "手動でDMGを作成してください"
fi

# 一時ディレクトリを削除
rm -rf "$DMG_TEMP_DIR"

echo ""
echo "=== すべて完了 ==="

# 署名・公証のサマリを表示
if [ "$DO_SIGN" = true ] || [ "$DO_NOTARIZE" = true ]; then
    echo ""
    echo "=========================================="
    echo "署名・公証サマリ"
    echo "=========================================="
    if [ "$DO_SIGN" = true ]; then
        echo -e "${GREEN}✓ アプリ署名: 完了${NC}"
        echo "  証明書: $DEVELOPER_ID"
    fi
    if [ "$DO_NOTARIZE" = true ]; then
        echo -e "${GREEN}✓ Apple公証: 完了${NC}"
        echo -e "${GREEN}✓ Stapler: 完了${NC}"
    fi
    if [ "$DO_SIGN" = true ]; then
        echo -e "${GREEN}✓ DMG署名: 完了${NC}"
    fi
    echo ""
    echo "このDMGはGatekeeperで保護されたMacで"
    echo "警告なしにインストールできます。"
fi
