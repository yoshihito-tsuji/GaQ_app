#!/usr/bin/env bash

# ============================================================================
# Multi-Project GitHub Release Download Statistics Script
# ============================================================================
#
# 対象プロジェクト:
#   - GaQ_app (Mac/Windows)
#   - PoPuP (Windows)
#
# 使用方法:
#   ./check_download_stats.sh [OPTIONS]
#
# オプション:
#   --csv              CSV形式で出力
#   --json             JSON形式で出力
#   --days N           直近N日間の平均を表示（デフォルト: 7）
#   --project NAME     特定プロジェクトのみ表示 (gaq|popup)
#   --help             ヘルプ表示
#
# 必要な環境変数:
#   GITHUB_TOKEN       GitHub Personal Access Token (推奨)
#                      ※未設定でも動作するがAPI制限あり
#
# ============================================================================

set -e

# ============================================================================
# Bash バージョンチェック
# ============================================================================

if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "⚠️  このスクリプトはBash 4.0以降が必要です"
    echo ""
    echo "macOSの場合、Homebrewでインストール:"
    echo "  brew install bash"
    echo ""
    echo "または、以下のコマンドで最新のbashを使用:"
    echo "  /opt/homebrew/bin/bash $0 $@"
    echo ""
    exit 1
fi

# ============================================================================
# 設定
# ============================================================================

# GitHubユーザー名/組織名
GITHUB_OWNER="yoshihito-tsuji"

# プロジェクト設定
declare -A PROJECTS=(
    ["gaq-mac"]="GaQ_app"
    ["gaq-win"]="GaQ_app"
    ["popup"]="PoPuP"
)

# リリース設定（プロジェクトごと）
declare -A RELEASES=(
    ["gaq-mac"]="v1.1.1-mac"
    ["gaq-win"]=""  # Windows版リリース後に設定
    ["popup"]=""  # 後で設定が必要
)

# カラー設定
COLOR_RESET="\033[0m"
COLOR_BOLD="\033[1m"
COLOR_GREEN="\033[32m"
COLOR_BLUE="\033[34m"
COLOR_YELLOW="\033[33m"
COLOR_CYAN="\033[36m"

# ============================================================================
# オプション解析
# ============================================================================

OUTPUT_FORMAT="pretty"
DAYS=7
FILTER_PROJECT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --csv)
            OUTPUT_FORMAT="csv"
            shift
            ;;
        --json)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --days)
            DAYS="$2"
            shift 2
            ;;
        --project)
            FILTER_PROJECT="$2"
            shift 2
            ;;
        --help)
            cat << EOF
Usage: $0 [OPTIONS]

Options:
  --csv              Output in CSV format
  --json             Output in JSON format
  --days N           Show average for last N days (default: 7)
  --project NAME     Show only specific project (gaq|popup)
  --help             Show this help message

Environment Variables:
  GITHUB_TOKEN       GitHub Personal Access Token (recommended)

Examples:
  $0                         # Show all projects
  $0 --project gaq           # Show only GaQ_app
  $0 --csv                   # CSV output
  $0 --days 30               # 30-day average

EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ============================================================================
# 関数定義
# ============================================================================

# GitHub API呼び出し
call_github_api() {
    local url="$1"
    local auth_header=""

    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        auth_header="-H \"Authorization: token $GITHUB_TOKEN\""
    fi

    eval curl -s $auth_header "$url"
}

# リリース情報取得
get_release_info() {
    local owner="$1"
    local repo="$2"
    local tag="$3"

    call_github_api "https://api.github.com/repos/$owner/$repo/releases/tags/$tag"
}

# 経過日数計算
calculate_days_since() {
    local published_at="$1"

    # macOS互換の日付計算
    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        local published_timestamp=$(date -d "$published_at" "+%s" 2>/dev/null || echo "0")
    else
        # BSD date (macOS)
        local published_timestamp=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$published_at" "+%s" 2>/dev/null || echo "0")
    fi

    local current_timestamp=$(date "+%s")
    local diff_seconds=$((current_timestamp - published_timestamp))
    local days=$((diff_seconds / 86400))
    echo "$days"
}

# ============================================================================
# メイン処理
# ============================================================================

# 出力バッファ
declare -a CSV_LINES=()
declare -a JSON_OBJECTS=()

# CSVヘッダー
if [[ "$OUTPUT_FORMAT" == "csv" ]]; then
    CSV_LINES+=("Project,Platform,Release,Asset,Downloads,Days Since Release,Avg per Day,Published At")
fi

# JSONヘッダー
if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    JSON_OBJECTS+=("{")
    JSON_OBJECTS+=("  \"generated_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",")
    JSON_OBJECTS+=("  \"days_filter\": $DAYS,")
    JSON_OBJECTS+=("  \"projects\": [")
fi

# プロジェクトごとに処理
FIRST_PROJECT=true
for project_key in "${!PROJECTS[@]}"; do
    project_name="${PROJECTS[$project_key]}"
    release_tag="${RELEASES[$project_key]}"

    # フィルタ適用
    if [[ -n "$FILTER_PROJECT" && "$project_key" != "$FILTER_PROJECT" ]]; then
        continue
    fi

    # リリースタグが未設定の場合はスキップ
    if [[ -z "$release_tag" ]]; then
        if [[ "$OUTPUT_FORMAT" == "pretty" ]]; then
            echo -e "${COLOR_YELLOW}⚠️  $project_name: リリースタグ未設定${COLOR_RESET}"
        fi
        continue
    fi

    # プリティ出力のヘッダー
    if [[ "$OUTPUT_FORMAT" == "pretty" ]]; then
        echo ""
        echo -e "${COLOR_BOLD}${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLOR_RESET}"
        echo -e "${COLOR_BOLD}${COLOR_CYAN}📦 $project_name${COLOR_RESET}"
        echo -e "${COLOR_BOLD}${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLOR_RESET}"
    fi

    # JSON: プロジェクト開始
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        if [[ "$FIRST_PROJECT" == false ]]; then
            JSON_OBJECTS+=("    },")
        fi
        JSON_OBJECTS+=("    {")
        JSON_OBJECTS+=("      \"name\": \"$project_name\",")
        JSON_OBJECTS+=("      \"release\": \"$release_tag\",")
        JSON_OBJECTS+=("      \"assets\": [")
        FIRST_PROJECT=false
    fi

    # リリース情報取得
    release_info=$(get_release_info "$GITHUB_OWNER" "$project_name" "$release_tag")

    # エラーチェック
    if echo "$release_info" | grep -q "Not Found"; then
        if [[ "$OUTPUT_FORMAT" == "pretty" ]]; then
            echo -e "${COLOR_YELLOW}⚠️  リリース $release_tag が見つかりません${COLOR_RESET}"
        fi
        continue
    fi

    # 公開日時取得
    published_at=$(echo "$release_info" | grep '"published_at"' | head -1 | sed 's/.*: "\(.*\)".*/\1/')
    days_since=$(calculate_days_since "$published_at")

    if [[ "$OUTPUT_FORMAT" == "pretty" ]]; then
        echo -e "${COLOR_BOLD}リリース:${COLOR_RESET} $release_tag"
        echo -e "${COLOR_BOLD}公開日:${COLOR_RESET} $published_at ($days_since 日前)"
        echo ""
    fi

    # アセット情報解析
    assets=$(echo "$release_info" | grep -A 3 '"name":' | grep -E '("name":|"download_count":)' | paste -d " " - -)

    total_downloads=0
    asset_count=0
    FIRST_ASSET=true

    while IFS= read -r line; do
        if [[ -z "$line" ]]; then
            continue
        fi

        asset_name=$(echo "$line" | sed 's/.*"name": "\([^"]*\)".*/\1/')
        download_count=$(echo "$line" | sed 's/.*"download_count": \([0-9]*\).*/\1/')

        if [[ -n "$asset_name" && "$asset_name" != "Source code"* ]]; then
            total_downloads=$((total_downloads + download_count))
            asset_count=$((asset_count + 1))

            # 1日あたりの平均
            if [[ $days_since -gt 0 ]]; then
                avg_per_day=$(echo "scale=2; $download_count / $days_since" | bc)
            else
                avg_per_day="N/A"
            fi

            # プラットフォーム判定
            platform="Unknown"
            if [[ "$asset_name" == *".dmg"* || "$asset_name" == *"mac"* || "$asset_name" == *"Mac"* ]]; then
                platform="macOS"
            elif [[ "$asset_name" == *".exe"* || "$asset_name" == *".zip"* || "$asset_name" == *"Windows"* || "$asset_name" == *"Portable"* ]]; then
                platform="Windows"
            elif [[ "$asset_name" == *".sha256"* ]]; then
                platform="Hash"
            fi

            # 出力
            case "$OUTPUT_FORMAT" in
                pretty)
                    printf "  %-50s  %6s DL  (%s/日)\n" "$asset_name" "$download_count" "$avg_per_day"
                    ;;
                csv)
                    CSV_LINES+=("$project_name,$platform,$release_tag,$asset_name,$download_count,$days_since,$avg_per_day,$published_at")
                    ;;
                json)
                    if [[ "$FIRST_ASSET" == false ]]; then
                        JSON_OBJECTS+=("        },")
                    fi
                    JSON_OBJECTS+=("        {")
                    JSON_OBJECTS+=("          \"name\": \"$asset_name\",")
                    JSON_OBJECTS+=("          \"platform\": \"$platform\",")
                    JSON_OBJECTS+=("          \"downloads\": $download_count,")
                    JSON_OBJECTS+=("          \"avg_per_day\": \"$avg_per_day\"")
                    FIRST_ASSET=false
                    ;;
            esac
        fi
    done <<< "$assets"

    # JSON: アセット終了
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        if [[ "$FIRST_ASSET" == false ]]; then
            JSON_OBJECTS+=("        }")
        fi
        JSON_OBJECTS+=("      ],")
    fi

    # 合計表示
    if [[ "$OUTPUT_FORMAT" == "pretty" ]]; then
        echo ""
        echo -e "${COLOR_BOLD}${COLOR_GREEN}📊 合計ダウンロード数: $total_downloads${COLOR_RESET}"

        if [[ $days_since -gt 0 ]]; then
            total_avg=$(echo "scale=2; $total_downloads / $days_since" | bc)
            echo -e "${COLOR_BOLD}📈 1日あたり平均: $total_avg${COLOR_RESET}"
        fi

        # 直近N日間の推定
        if [[ $days_since -ge $DAYS ]]; then
            recent_avg=$(echo "scale=0; $total_downloads / $days_since * $DAYS" | bc)
            echo -e "${COLOR_BOLD}📅 直近${DAYS}日間推定: $recent_avg DL${COLOR_RESET}"
        fi
    fi

    # JSON: プロジェクト情報追加
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        JSON_OBJECTS+=("      \"total_downloads\": $total_downloads,")
        JSON_OBJECTS+=("      \"days_since_release\": $days_since,")
        JSON_OBJECTS+=("      \"published_at\": \"$published_at\"")
    fi
done

# ============================================================================
# 出力
# ============================================================================

case "$OUTPUT_FORMAT" in
    csv)
        for line in "${CSV_LINES[@]}"; do
            echo "$line"
        done
        ;;
    json)
        JSON_OBJECTS+=("    }")
        JSON_OBJECTS+=("  ]")
        JSON_OBJECTS+=("}")
        for line in "${JSON_OBJECTS[@]}"; do
            echo "$line"
        done
        ;;
    pretty)
        echo ""
        echo -e "${COLOR_BOLD}${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLOR_RESET}"
        echo ""
        ;;
esac

# ============================================================================
# 完了
# ============================================================================

if [[ "$OUTPUT_FORMAT" == "pretty" ]]; then
    echo -e "${COLOR_GREEN}✅ 統計取得完了${COLOR_RESET}"
    echo ""

    if [[ -z "${GITHUB_TOKEN:-}" ]]; then
        echo -e "${COLOR_YELLOW}💡 ヒント: GITHUB_TOKEN環境変数を設定するとAPI制限が緩和されます${COLOR_RESET}"
        echo ""
    fi
fi
