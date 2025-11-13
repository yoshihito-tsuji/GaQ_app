#!/bin/bash
#
# GitHub Release ダウンロード数追跡スクリプト（複数リポジトリ対応）
#
# 目的: 複数のGitHub Releaseの各アセットのダウンロード数を取得し、
#       CSV形式で記録する
#
# 使用方法:
#   ./scripts/track_downloads.sh
#
# 対象リポジトリ:
#   - yoshihito-tsuji/GaQ_app (GaQ Transcriber)
#   - yoshihito-tsuji/Pop_app (PoPuP)
#
# 出力先:
#   /Users/yoshihitotsuji/Claude_Code/AccessLog/
#
# CSV形式:
#   日付,リポジトリ,リリース名,タグ,アセット名,ダウンロード数
#

set -e

# 色設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 出力先ディレクトリ
OUTPUT_DIR="/Users/yoshihitotsuji/Claude_Code/AccessLog"
CURRENT_DATE=$(date "+%Y-%m-%d")
CURRENT_DATETIME=$(date "+%Y-%m-%d %H:%M:%S")

# 日次ログファイル (日付ごと)
DAILY_LOG="${OUTPUT_DIR}/downloads_${CURRENT_DATE}.csv"

# 累積ログファイル (すべての記録)
CUMULATIVE_LOG="${OUTPUT_DIR}/downloads_all.csv"

# 追跡対象のリポジトリ
REPO_NAMES=("yoshihito-tsuji/GaQ_app" "yoshihito-tsuji/Pop_app")
REPO_DISPLAY_NAMES=("GaQ" "PoPuP")

# ディレクトリ作成
mkdir -p "${OUTPUT_DIR}"

echo -e "${BLUE}========================================"
echo "GitHub Release ダウンロード数追跡"
echo "========================================${NC}"
echo ""
echo "実行日時: ${CURRENT_DATETIME}"
echo "出力先: ${OUTPUT_DIR}"
echo ""

# GitHub CLI が利用可能かチェック
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠ GitHub CLI (gh) がインストールされていません${NC}"
    echo "インストール方法: brew install gh"
    exit 1
fi

# GitHub認証チェック
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠ GitHub CLI が認証されていません${NC}"
    echo "認証方法: gh auth login"
    exit 1
fi

# CSVヘッダー (ファイルが存在しない場合のみ)
if [ ! -f "${DAILY_LOG}" ]; then
    echo "記録日時,リポジトリ,リリース名,タグ,アセット名,ダウンロード数" > "${DAILY_LOG}"
fi

if [ ! -f "${CUMULATIVE_LOG}" ]; then
    echo "記録日時,リポジトリ,リリース名,タグ,アセット名,ダウンロード数" > "${CUMULATIVE_LOG}"
fi

# GitHub Release 情報を取得
echo -e "${BLUE}ダウンロード数を取得中...${NC}"
echo ""

# 合計ダウンロード数を計算
total_downloads=0
total_release_count=0

# 各リポジトリを処理
for idx in "${!REPO_NAMES[@]}"; do
    repo="${REPO_NAMES[$idx]}"
    repo_display_name="${REPO_DISPLAY_NAMES[$idx]}"

    echo -e "${BLUE}--- ${repo_display_name} (${repo}) ---${NC}"

    # リリース数をカウント
    release_count=$(gh api "repos/${repo}/releases" --jq 'length' 2>/dev/null || echo "0")

    if [ "$release_count" = "0" ]; then
        echo -e "${YELLOW}  リリースが見つかりませんでした${NC}"
        echo ""
        continue
    fi

    total_release_count=$((total_release_count + release_count))

    # 各リリースを処理
    for i in $(seq 0 $((release_count - 1))); do
        # リリース情報を取得
        release_name=$(gh api "repos/${repo}/releases" --jq ".[$i].name")
        tag=$(gh api "repos/${repo}/releases" --jq ".[$i].tag_name")
        assets_count=$(gh api "repos/${repo}/releases" --jq ".[$i].assets | length")

        # アセットが存在しない場合はスキップ
        if [ "$assets_count" = "0" ]; then
            continue
        fi

        # 各アセットを処理
        for j in $(seq 0 $((assets_count - 1))); do
            asset_name=$(gh api "repos/${repo}/releases" --jq ".[$i].assets[$j].name")
            download_count=$(gh api "repos/${repo}/releases" --jq ".[$i].assets[$j].download_count")

            # クォートを削除
            release_name=$(echo "$release_name" | tr -d '"')
            tag=$(echo "$tag" | tr -d '"')
            asset_name=$(echo "$asset_name" | tr -d '"')
            download_count=$(echo "$download_count" | tr -d '"')

            # CSVに記録（カンマを含む場合はクォートで囲む）
            echo "\"${CURRENT_DATETIME}\",\"${repo_display_name}\",\"${release_name}\",\"${tag}\",\"${asset_name}\",${download_count}" >> "${DAILY_LOG}"
            echo "\"${CURRENT_DATETIME}\",\"${repo_display_name}\",\"${release_name}\",\"${tag}\",\"${asset_name}\",${download_count}" >> "${CUMULATIVE_LOG}"

            # 合計ダウンロード数を計算
            total_downloads=$((total_downloads + download_count))

            # 結果表示
            echo -e "  ${GREEN}✓${NC} ${release_name} (${tag})"
            echo "    └─ ${asset_name}: ${download_count} DL"
        done
    done

    echo ""
done

echo -e "${BLUE}========================================"
echo "集計結果"
echo "========================================${NC}"
echo -e "対象リポジトリ: ${#REPO_NAMES[@]} 個"
echo -e "総リリース数: ${total_release_count}"
echo -e "総ダウンロード数: ${GREEN}${total_downloads}${NC}"
echo ""
echo -e "${GREEN}✅ ログファイルに記録しました${NC}"
echo "  - 日次ログ: ${DAILY_LOG}"
echo "  - 累積ログ: ${CUMULATIVE_LOG}"
echo ""
