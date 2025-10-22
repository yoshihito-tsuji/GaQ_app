#!/bin/bash
#
# ソースファイル同期確認スクリプト
#
# 目的: release/mac/src/ と release/windows/src/ の主要ファイルが
#       同期されているかをチェックし、差分があれば警告する
#
# 使用方法:
#   ./scripts/check_sync.sh
#
# 終了コード:
#   0: すべて同期済み
#   1: 差分あり（要対応）
#

set -e

# 色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# チェック対象ファイル（共通コード）
COMMON_FILES=(
    "transcribe.py"
    "config.py"
)

# プラットフォーム固有ファイル（行数のみチェック）
PLATFORM_SPECIFIC_FILES=(
    "main.py"
    "main_app.py"
)

echo "========================================"
echo "ソースファイル同期確認"
echo "========================================"
echo ""

# ディレクトリ存在確認
if [ ! -d "release/mac/src" ]; then
    echo -e "${RED}✗ release/mac/src/ が見つかりません${NC}"
    exit 1
fi

if [ ! -d "release/windows/src" ]; then
    echo -e "${RED}✗ release/windows/src/ が見つかりません${NC}"
    exit 1
fi

# 共通ファイルの差分チェック
echo "【共通コードの同期確認】"
echo ""

has_diff=0

for file in "${COMMON_FILES[@]}"; do
    mac_file="release/mac/src/$file"
    win_file="release/windows/src/$file"

    if [ ! -f "$mac_file" ]; then
        echo -e "${YELLOW}⚠ Mac版に $file が見つかりません${NC}"
        has_diff=1
        continue
    fi

    if [ ! -f "$win_file" ]; then
        echo -e "${YELLOW}⚠ Windows版に $file が見つかりません${NC}"
        has_diff=1
        continue
    fi

    # 差分チェック
    if diff -q "$mac_file" "$win_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $file - 同期済み${NC}"
    else
        echo -e "${RED}✗ $file - 差分あり${NC}"
        echo "  詳細を確認: diff release/mac/src/$file release/windows/src/$file"
        has_diff=1
    fi
done

echo ""
echo "【プラットフォーム固有ファイルの確認】"
echo ""

for file in "${PLATFORM_SPECIFIC_FILES[@]}"; do
    mac_file="release/mac/src/$file"
    win_file="release/windows/src/$file"

    if [ ! -f "$mac_file" ]; then
        echo -e "${YELLOW}⚠ Mac版に $file が見つかりません${NC}"
        continue
    fi

    if [ ! -f "$win_file" ]; then
        echo -e "${YELLOW}⚠ Windows版に $file が見つかりません${NC}"
        continue
    fi

    mac_lines=$(wc -l < "$mac_file" | tr -d ' ')
    win_lines=$(wc -l < "$win_file" | tr -d ' ')

    diff_lines=$((mac_lines - win_lines))
    if [ $diff_lines -lt 0 ]; then
        diff_lines=$((-diff_lines))
    fi

    # 行数差が50行以内なら正常とみなす
    if [ $diff_lines -le 50 ]; then
        echo -e "${GREEN}✓ $file - Mac: ${mac_lines}行, Win: ${win_lines}行 (差: ${diff_lines}行)${NC}"
    else
        echo -e "${YELLOW}⚠ $file - Mac: ${mac_lines}行, Win: ${win_lines}行 (差: ${diff_lines}行)${NC}"
        echo "  → 行数差が大きいです。意図的な変更か確認してください。"
    fi
done

echo ""
echo "========================================"

if [ $has_diff -eq 0 ]; then
    echo -e "${GREEN}✅ すべての共通コードが同期されています${NC}"
    exit 0
else
    echo -e "${RED}❌ 差分が検出されました。修正が必要です。${NC}"
    echo ""
    echo "【推奨される対応】"
    echo "1. どちらが最新版か確認（git log で最終更新日時を比較）"
    echo "2. 最新版の内容を反映（cp コマンドまたは手動マージ）"
    echo "3. 再度このスクリプトを実行して確認"
    echo ""
    echo "【将来的な対応】"
    echo "- src/ ディレクトリに共通ソースを集約"
    echo "- scripts/sync_sources.sh で自動同期"
    exit 1
fi
