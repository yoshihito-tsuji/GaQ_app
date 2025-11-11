#!/usr/bin/env python3
"""
Multi-Project GitHub Release Download Statistics Script

対象プロジェクト:
  - GaQ_app (Mac/Windows)
  - PoPuP (Windows)

使用方法:
  python3 check_download_stats.py [OPTIONS]

オプション:
  --csv              CSV形式で出力
  --json             JSON形式で出力
  --days N           直近N日間の平均を表示（デフォルト: 7）
  --project NAME     特定プロジェクトのみ表示 (gaq|popup)
  --help             ヘルプ表示

必要な環境変数:
  GITHUB_TOKEN       GitHub Personal Access Token (推奨)
                     ※未設定でも動作するがAPI制限あり
"""

import argparse
import csv
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# ============================================================================
# 設定
# ============================================================================

GITHUB_OWNER = "yoshihito-tsuji"

PROJECTS = {
    "gaq": "GaQ_app",
    "popup": "PoPuP"
}

RELEASES = {
    "gaq": "v1.1.1",
    "popup": ""  # 後で設定が必要
}

# カラーコード
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"

# ============================================================================
# GitHub API関数
# ============================================================================

def call_github_api(url: str) -> dict:
    """GitHub APIを呼び出す"""
    headers = {}

    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"error": "Not Found"}
        raise

def get_release_info(owner: str, repo: str, tag: str) -> dict:
    """リリース情報を取得"""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    return call_github_api(url)

# ============================================================================
# ユーティリティ関数
# ============================================================================

def calculate_days_since(published_at: str) -> int:
    """公開日からの経過日数を計算"""
    published = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    diff = now - published
    return diff.days

def determine_platform(asset_name: str) -> str:
    """アセット名からプラットフォームを判定"""
    name_lower = asset_name.lower()

    if '.dmg' in name_lower or 'mac' in name_lower:
        return "macOS"
    elif '.exe' in name_lower or '.zip' in name_lower or 'windows' in name_lower or 'portable' in name_lower:
        return "Windows"
    elif '.sha256' in name_lower:
        return "Hash"
    else:
        return "Unknown"

# ============================================================================
# 出力関数
# ============================================================================

def print_pretty_header(project_name: str):
    """プリティ出力のヘッダー"""
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}{'━' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}📦 {project_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'━' * 50}{Colors.RESET}")

def print_pretty_asset(asset_name: str, download_count: int, avg_per_day: str):
    """プリティ出力のアセット情報"""
    print(f"  {asset_name:<50}  {download_count:6} DL  ({avg_per_day}/日)")

def print_pretty_summary(total_downloads: int, days_since: int, days_filter: int):
    """プリティ出力の統計サマリー"""
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}📊 合計ダウンロード数: {total_downloads}{Colors.RESET}")

    if days_since > 0:
        total_avg = total_downloads / days_since
        print(f"{Colors.BOLD}📈 1日あたり平均: {total_avg:.2f}{Colors.RESET}")

    if days_since >= days_filter:
        recent_avg = int(total_downloads / days_since * days_filter)
        print(f"{Colors.BOLD}📅 直近{days_filter}日間推定: {recent_avg} DL{Colors.RESET}")

def print_pretty_footer():
    """プリティ出力のフッター"""
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}{'━' * 50}{Colors.RESET}")
    print()
    print(f"{Colors.GREEN}✅ 統計取得完了{Colors.RESET}")
    print()

    if not os.environ.get("GITHUB_TOKEN"):
        print(f"{Colors.YELLOW}💡 ヒント: GITHUB_TOKEN環境変数を設定するとAPI制限が緩和されます{Colors.RESET}")
        print()

# ============================================================================
# メイン処理
# ============================================================================

def process_project(
    project_key: str,
    project_name: str,
    release_tag: str,
    output_format: str,
    days_filter: int
) -> Tuple[List[dict], int, int]:
    """プロジェクトの統計を処理"""

    if not release_tag:
        if output_format == "pretty":
            print(f"{Colors.YELLOW}⚠️  {project_name}: リリースタグ未設定{Colors.RESET}")
        return [], 0, 0

    # リリース情報取得
    release_info = get_release_info(GITHUB_OWNER, project_name, release_tag)

    if "error" in release_info:
        if output_format == "pretty":
            print(f"{Colors.YELLOW}⚠️  リリース {release_tag} が見つかりません{Colors.RESET}")
        return [], 0, 0

    # プリティ出力のヘッダー
    if output_format == "pretty":
        print_pretty_header(project_name)

    # 公開日時取得
    published_at = release_info.get("published_at", "")
    days_since = calculate_days_since(published_at)

    if output_format == "pretty":
        print(f"{Colors.BOLD}リリース:{Colors.RESET} {release_tag}")
        print(f"{Colors.BOLD}公開日:{Colors.RESET} {published_at} ({days_since} 日前)")
        print()

    # アセット情報処理
    assets_data = []
    total_downloads = 0

    for asset in release_info.get("assets", []):
        asset_name = asset.get("name", "")
        download_count = asset.get("download_count", 0)

        # ソースコードは除外
        if "Source code" in asset_name:
            continue

        total_downloads += download_count

        # 1日あたりの平均
        if days_since > 0:
            avg_per_day = f"{download_count / days_since:.2f}"
        else:
            avg_per_day = "N/A"

        # プラットフォーム判定
        platform = determine_platform(asset_name)

        # データ保存
        asset_data = {
            "project": project_name,
            "platform": platform,
            "release": release_tag,
            "asset": asset_name,
            "downloads": download_count,
            "days_since": days_since,
            "avg_per_day": avg_per_day,
            "published_at": published_at
        }
        assets_data.append(asset_data)

        # プリティ出力
        if output_format == "pretty":
            print_pretty_asset(asset_name, download_count, avg_per_day)

    # 統計サマリー
    if output_format == "pretty":
        print_pretty_summary(total_downloads, days_since, days_filter)

    return assets_data, total_downloads, days_since

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Multi-Project GitHub Release Download Statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--csv", action="store_true", help="Output in CSV format")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--days", type=int, default=7, help="Show average for last N days (default: 7)")
    parser.add_argument("--project", choices=["gaq", "popup"], help="Show only specific project")

    args = parser.parse_args()

    # 出力形式決定
    if args.csv:
        output_format = "csv"
    elif args.json:
        output_format = "json"
    else:
        output_format = "pretty"

    # データ収集
    all_assets_data = []
    projects_data = []

    for project_key, project_name in PROJECTS.items():
        # フィルタ適用
        if args.project and args.project != project_key:
            continue

        release_tag = RELEASES[project_key]

        assets_data, total_downloads, days_since = process_project(
            project_key,
            project_name,
            release_tag,
            output_format,
            args.days
        )

        all_assets_data.extend(assets_data)

        if release_tag and assets_data:
            projects_data.append({
                "name": project_name,
                "release": release_tag,
                "total_downloads": total_downloads,
                "days_since_release": days_since,
                "published_at": assets_data[0]["published_at"] if assets_data else "",
                "assets": assets_data
            })

    # 出力
    if output_format == "csv":
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=["project", "platform", "release", "asset", "downloads", "days_since", "avg_per_day", "published_at"]
        )
        writer.writeheader()
        writer.writerows(all_assets_data)

    elif output_format == "json":
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "days_filter": args.days,
            "projects": projects_data
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))

    else:  # pretty
        print_pretty_footer()

if __name__ == "__main__":
    main()
