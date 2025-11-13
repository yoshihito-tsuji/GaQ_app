# ダウンロード数追跡システム - 実装完了サマリー

## 実装日

2025-11-13

## システム概要

GaQ_app と Pop_app の GitHub Release ダウンロード数を統合的に追跡し、CSV形式で記録するシステムを構築しました。

## 主な機能

### 1. 複数リポジトリ対応
- **GaQ_app** (GaQ Transcriber) - Windows/Mac版音声文字起こしアプリ
- **Pop_app** (PoPuP) - Windows版ポップアップアプリ

### 2. 自動実行スケジュール
- **実行時間**: 毎日23:55
- **実行方式**: macOS launchd（cronの推奨代替）

### 3. データ保存
- **保存先**: `/Users/yoshihitotsuji/Claude_Code/AccessLog/`
- **形式**: CSV
- **ファイル種別**:
  - 日次ログ: `downloads_YYYY-MM-DD.csv`
  - 累積ログ: `downloads_all.csv`

## 現在のダウンロード統計

初回実行時（2025-11-13）のデータ:

| リポジトリ | リリース数 | 総ダウンロード数 |
|-----------|----------|----------------|
| GaQ | 3 | 4 |
| PoPuP | 3 | 40 |
| **合計** | **6** | **44** |

### 詳細内訳

#### GaQ_app
- Mac版 v1.1.1: 4 DL
- Windows版 v1.1.1: 0 DL

#### Pop_app
- PoPuP v1.2.0: 37 DL
- PoPuP v1.1.0: 2 DL
- PoPuP v1.0.0: 1 DL

## ファイル構成

```
Claude_Code/
├── GaQ_app/
│   └── scripts/
│       ├── track_downloads.sh              # メインスクリプト
│       ├── setup_tracker.sh                # セットアップスクリプト
│       ├── com.gaq.download-tracker.plist  # launchd設定
│       ├── README_DOWNLOADS.md             # クイックガイド
│       ├── DOWNLOAD_TRACKER_SETUP.md       # 詳細マニュアル
│       └── SUMMARY.md                      # このファイル
└── AccessLog/
    ├── downloads_2025-11-13.csv            # 日次ログ
    ├── downloads_all.csv                   # 累積ログ
    ├── tracker.log                         # 実行ログ（自動実行時）
    └── tracker_error.log                   # エラーログ（自動実行時）
```

## CSV形式

```csv
記録日時,リポジトリ,リリース名,タグ,アセット名,ダウンロード数
"2025-11-13 10:15:53","GaQ","GaQ Transcriber v1.1.1 (macOS)","v1.1.1-mac","GaQ_Transcriber_v1.1.1_mac.dmg",4
"2025-11-13 10:15:53","PoPuP","PoPuP v1.2.0","v1.2.0","PoPuP_Portable_v1.2.0.zip",37
```

## セットアップ手順

### クイックセットアップ（推奨）

```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app
./scripts/setup_tracker.sh
```

このコマンドで以下が自動実行されます：
1. 環境チェック（GitHub CLI）
2. 実行権限の設定
3. launchdサービスのインストール
4. テスト実行

### 手動実行

```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app
./scripts/track_downloads.sh
```

## データの確認方法

### ターミナルで確認

```bash
# 最新データの確認
tail -n 10 /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv

# GaQの総ダウンロード数
grep "\"GaQ\"" /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv | \
  awk -F',' '{sum+=$6} END {print "GaQ Total:", sum}'

# PoPuPの総ダウンロード数
grep "\"PoPuP\"" /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv | \
  awk -F',' '{sum+=$6} END {print "PoPuP Total:", sum}'
```

### Excel/Google Sheetsで確認

```bash
open /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv
```

## サービス管理

### 状態確認
```bash
launchctl list | grep gaq
```

### 手動実行
```bash
launchctl start com.gaq.download-tracker
```

### サービス停止
```bash
launchctl stop com.gaq.download-tracker
```

### サービス無効化
```bash
launchctl unload ~/Library/LaunchAgents/com.gaq.download-tracker.plist
```

### サービス再有効化
```bash
launchctl load ~/Library/LaunchAgents/com.gaq.download-tracker.plist
```

## 技術仕様

### 使用技術
- **言語**: Bash
- **API**: GitHub REST API (via GitHub CLI)
- **スケジューラ**: macOS launchd
- **データ形式**: CSV

### 依存関係
- GitHub CLI (`gh`)
- GitHub認証済みアカウント
- macOS（launchd使用のため）

### セキュリティ
- 読み取り専用アクセス
- 公開情報のみを取得
- 個人情報は記録しない

## 拡張性

### 新しいリポジトリの追加

[track_downloads.sh](track_downloads.sh) の以下の部分を編集：

```bash
# 追跡対象のリポジトリ
REPO_NAMES=("yoshihito-tsuji/GaQ_app" "yoshihito-tsuji/Pop_app")
REPO_DISPLAY_NAMES=("GaQ" "PoPuP")
```

例：`NewApp` を追加する場合

```bash
REPO_NAMES=("yoshihito-tsuji/GaQ_app" "yoshihito-tsuji/Pop_app" "yoshihito-tsuji/NewApp")
REPO_DISPLAY_NAMES=("GaQ" "PoPuP" "NewApp")
```

### 実行スケジュールの変更

[com.gaq.download-tracker.plist](com.gaq.download-tracker.plist) を編集：

```xml
<!-- 例: 毎日午前9時に変更 -->
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

変更後は再読み込みが必要：
```bash
launchctl unload ~/Library/LaunchAgents/com.gaq.download-tracker.plist
launchctl load ~/Library/LaunchAgents/com.gaq.download-tracker.plist
```

## 今後の改善案

- [x] 複数リポジトリ対応
- [ ] 週次・月次レポート自動生成
- [ ] グラフの自動生成（PNG/SVG）
- [ ] Slack/メール通知
- [ ] Webダッシュボード
- [ ] データベース連携
- [ ] リアルタイムモニタリング

## トラブルシューティング

### スクリプトが実行されない

```bash
# 実行権限を確認
ls -la ./scripts/track_downloads.sh

# 実行権限を付与
chmod +x ./scripts/track_downloads.sh
```

### GitHub認証エラー

```bash
# 認証状態を確認
gh auth status

# 再認証
gh auth login
```

### データが記録されない

```bash
# エラーログを確認
cat /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker_error.log

# 手動実行でテスト
./scripts/track_downloads.sh
```

## ドキュメント

- [README_DOWNLOADS.md](README_DOWNLOADS.md) - クイックスタートガイド
- [DOWNLOAD_TRACKER_SETUP.md](DOWNLOAD_TRACKER_SETUP.md) - 詳細セットアップガイド
- [SUMMARY.md](SUMMARY.md) - このファイル

## ライセンス

MIT License

## 作成者

Claude Code (with Anthropic's Claude)

---

**最終更新**: 2025-11-13

## アーカイブ情報

### 非推奨スクリプトのアーカイブ

統合システムの構築により、以下のスクリプトがアーカイブされました：

#### アーカイブされたファイル
- **Pop_app/scripts/check_download_stats.py** → `archive_data/deprecated_scripts/check_download_stats_old.py`

#### アーカイブ場所
```
/Users/yoshihitotsuji/Claude_Code/archive_data/deprecated_scripts/
├── README.md                        # アーカイブ情報
└── check_download_stats_old.py      # 旧Pop_appスクリプト
```

#### アーカイブ理由
複数リポジトリ対応の統合システムにより、個別プロジェクト用のスクリプトは不要になりました。

詳細は [archive_data/deprecated_scripts/README.md](/Users/yoshihitotsuji/Claude_Code/archive_data/deprecated_scripts/README.md) を参照してください。

---

**アーカイブ日**: 2025-11-13
