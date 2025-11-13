# GitHub Release ダウンロード数追跡 - セットアップガイド

## 概要

このシステムは、複数のGitHub Releaseのダウンロード数を定期的に取得し、CSV形式で記録します。

### 対象リポジトリ

- **yoshihito-tsuji/GaQ_app** (GaQ Transcriber)
- **yoshihito-tsuji/Pop_app** (PoPuP)

## ファイル構成

```
Claude_Code/
├── GaQ_app/
│   └── scripts/
│       ├── track_downloads.sh                    # ダウンロード数取得スクリプト
│       ├── com.gaq.download-tracker.plist        # launchd設定ファイル
│       └── DOWNLOAD_TRACKER_SETUP.md             # このファイル
└── AccessLog/
    ├── downloads_YYYY-MM-DD.csv                  # 日次ログ
    ├── downloads_all.csv                         # 累積ログ
    ├── tracker.log                               # 実行ログ
    └── tracker_error.log                         # エラーログ
```

## 必要な環境

- macOS
- GitHub CLI (`gh`) がインストールされ、認証済みであること
- GitHub リポジトリへのアクセス権限

## 手動実行

スクリプトを手動で実行する場合:

```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app
./scripts/track_downloads.sh
```

## 自動実行の設定（launchd - 推奨）

macOSでは`launchd`を使用した定期実行が推奨されます。

### 1. plistファイルのインストール

```bash
# plistファイルをLaunchAgentsディレクトリにコピー
cp /Users/yoshihitotsuji/Claude_Code/GaQ_app/scripts/com.gaq.download-tracker.plist \
   ~/Library/LaunchAgents/
```

### 2. launchdに登録

```bash
# サービスを読み込む
launchctl load ~/Library/LaunchAgents/com.gaq.download-tracker.plist
```

### 3. 動作確認

```bash
# サービスが登録されているか確認
launchctl list | grep gaq

# 手動でサービスを実行してテスト
launchctl start com.gaq.download-tracker

# ログを確認
cat /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker.log
```

### 4. サービスの管理

```bash
# サービスを停止
launchctl stop com.gaq.download-tracker

# サービスを無効化（登録解除）
launchctl unload ~/Library/LaunchAgents/com.gaq.download-tracker.plist

# サービスを再読み込み（設定変更後）
launchctl unload ~/Library/LaunchAgents/com.gaq.download-tracker.plist
launchctl load ~/Library/LaunchAgents/com.gaq.download-tracker.plist
```

## 自動実行の設定（cron - 代替方法）

cronを使用する場合は以下の手順で設定します。

### 1. crontabの編集

```bash
crontab -e
```

### 2. 以下の行を追加

```cron
# 毎日午前0時にダウンロード数を記録
0 0 * * * /bin/bash /Users/yoshihitotsuji/Claude_Code/GaQ_app/scripts/track_downloads.sh >> /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker.log 2>&1
```

### 3. 設定の確認

```bash
crontab -l
```

## 実行スケジュールのカスタマイズ

### launchdの場合

`com.gaq.download-tracker.plist` の `StartCalendarInterval` セクションを編集:

```xml
<!-- 例: 毎日午前9時に実行 -->
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>

<!-- 例: 1日に複数回実行（午前9時と午後9時） -->
<key>StartCalendarInterval</key>
<array>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <dict>
        <key>Hour</key>
        <integer>21</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</array>
```

### cronの場合

cronの書式: `分 時 日 月 曜日 コマンド`

```cron
# 毎日午前9時
0 9 * * * /bin/bash /path/to/track_downloads.sh

# 12時間ごと（午前0時と午後12時）
0 0,12 * * * /bin/bash /path/to/track_downloads.sh

# 毎週月曜日の午前0時
0 0 * * 1 /bin/bash /path/to/track_downloads.sh
```

## CSVファイルの形式

### downloads_YYYY-MM-DD.csv（日次ログ）

その日に記録されたデータのみが含まれます。

```csv
記録日時,リポジトリ,リリース名,タグ,アセット名,ダウンロード数
"2025-11-13 23:55:00","GaQ","GaQ Transcriber v1.1.1 (macOS)","v1.1.1-mac","GaQ_Transcriber_v1.1.1_mac.dmg",4
"2025-11-13 23:55:00","PoPuP","PoPuP v1.2.0","v1.2.0","PoPuP_Portable_v1.2.0.zip",37
```

### downloads_all.csv（累積ログ）

すべての記録が時系列で保存されます。

```csv
記録日時,リポジトリ,リリース名,タグ,アセット名,ダウンロード数
"2025-11-13 23:55:00","GaQ","GaQ Transcriber v1.1.1 (macOS)","v1.1.1-mac","GaQ_Transcriber_v1.1.1_mac.dmg",4
"2025-11-13 23:55:00","PoPuP","PoPuP v1.2.0","v1.2.0","PoPuP_Portable_v1.2.0.zip",37
"2025-11-14 23:55:00","GaQ","GaQ Transcriber v1.1.1 (macOS)","v1.1.1-mac","GaQ_Transcriber_v1.1.1_mac.dmg",6
"2025-11-14 23:55:00","PoPuP","PoPuP v1.2.0","v1.2.0","PoPuP_Portable_v1.2.0.zip",40
```

## データの分析方法

### Excelで開く

CSVファイルをExcelやGoogle Sheetsで開いて、グラフ化や集計ができます。

### コマンドラインで確認

```bash
# 最新の記録を表示
tail -n 10 /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv

# GaQの総ダウンロード数
grep "\"GaQ\"" /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv | \
  awk -F',' '{sum+=$6} END {print "GaQ Total:", sum}'

# PoPuPの総ダウンロード数
grep "\"PoPuP\"" /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv | \
  awk -F',' '{sum+=$6} END {print "PoPuP Total:", sum}'

# 特定のリリースのダウンロード数を集計
grep "v1.1.1-mac" /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv

# 全体の総ダウンロード数
awk -F',' 'NR>1 {sum+=$6} END {print "Overall Total:", sum}' \
    /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv
```

## トラブルシューティング

### GitHub CLI が認証されていない

```bash
gh auth login
```

### スクリプトが実行されない

1. スクリプトに実行権限があるか確認:
   ```bash
   chmod +x /Users/yoshihitotsuji/Claude_Code/GaQ_app/scripts/track_downloads.sh
   ```

2. ログファイルを確認:
   ```bash
   cat /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker_error.log
   ```

3. launchdサービスの状態を確認:
   ```bash
   launchctl list | grep gaq
   ```

### データが記録されない

1. 手動実行して動作確認:
   ```bash
   ./scripts/track_downloads.sh
   ```

2. GitHub APIの呼び出し制限を確認:
   ```bash
   gh api rate_limit
   ```

## セキュリティ上の注意

- このスクリプトは読み取り専用で、リポジトリに変更を加えません
- GitHub CLIの認証トークンは安全に保管されます
- ログファイルにはダウンロード数のみが記録され、個人情報は含まれません

## メンテナンス

### 古いログファイルの整理

```bash
# 30日以前の日次ログを削除
find /Users/yoshihitotsuji/Claude_Code/AccessLog -name "downloads_*.csv" -mtime +30 -delete
```

### 累積ログのバックアップ

```bash
# 定期的にバックアップを作成
cp /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv \
   /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all_backup_$(date +%Y%m%d).csv
```

## リポジトリの追加方法

追加のリポジトリを監視したい場合は、[track_downloads.sh](track_downloads.sh) の以下の部分を編集してください：

```bash
# 追跡対象のリポジトリ
REPO_NAMES=("yoshihito-tsuji/GaQ_app" "yoshihito-tsuji/Pop_app")
REPO_DISPLAY_NAMES=("GaQ" "PoPuP")
```

例：新しいリポジトリ `yoshihito-tsuji/NewApp` を追加する場合

```bash
REPO_NAMES=("yoshihito-tsuji/GaQ_app" "yoshihito-tsuji/Pop_app" "yoshihito-tsuji/NewApp")
REPO_DISPLAY_NAMES=("GaQ" "PoPuP" "NewApp")
```

## 更新履歴

- 2025-11-13: 初版作成
- 2025-11-13: 複数リポジトリ対応（GaQ_app, Pop_app）、実行時間を23:55に変更
