# GitHub Release ダウンロード数追跡システム（複数リポジトリ対応）

## 対象リポジトリ

- **GaQ_app** (GaQ Transcriber) - Windows/Mac版音声文字起こしアプリ
- **Pop_app** (PoPuP) - Windows版ポップアップアプリ

## クイックスタート

### 1. セットアップ（初回のみ）

```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app
./scripts/setup_tracker.sh
```

このスクリプトが自動的に以下を実行します:
- 環境チェック（GitHub CLI）
- 実行権限の設定
- launchdサービスのインストール
- テスト実行

### 2. 手動実行（任意）

```bash
./scripts/track_downloads.sh
```

### 3. ログの確認

```bash
# ダウンロード数の確認
cat /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv

# 実行ログの確認
cat /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker.log
```

## ファイル一覧

| ファイル | 説明 |
|---------|------|
| [track_downloads.sh](track_downloads.sh) | ダウンロード数取得スクリプト（メイン） |
| [setup_tracker.sh](setup_tracker.sh) | セットアップ用スクリプト |
| [com.gaq.download-tracker.plist](com.gaq.download-tracker.plist) | launchd設定ファイル |
| [DOWNLOAD_TRACKER_SETUP.md](DOWNLOAD_TRACKER_SETUP.md) | 詳細なセットアップガイド |

## 自動実行のスケジュール

デフォルトでは**毎日23:55**に自動実行されます。

変更方法は [DOWNLOAD_TRACKER_SETUP.md](DOWNLOAD_TRACKER_SETUP.md) を参照してください。

## 出力ファイル

すべてのファイルは `/Users/yoshihitotsuji/Claude_Code/AccessLog/` に保存されます。

| ファイル | 説明 |
|---------|------|
| `downloads_YYYY-MM-DD.csv` | 日次ログ（その日のデータのみ） |
| `downloads_all.csv` | 累積ログ（全データの履歴） |
| `tracker.log` | スクリプト実行ログ |
| `tracker_error.log` | エラーログ |

### CSV形式

```csv
記録日時,リポジトリ,リリース名,タグ,アセット名,ダウンロード数
"2025-11-13 23:55:00","GaQ","GaQ Transcriber v1.1.1 (macOS)","v1.1.1-mac","GaQ_Transcriber_v1.1.1_mac.dmg",4
"2025-11-13 23:55:00","PoPuP","PoPuP v1.2.0","v1.2.0","PoPuP_Portable_v1.2.0.zip",37
```

## サービスの管理

```bash
# サービスの状態確認
launchctl list | grep gaq

# 手動実行
launchctl start com.gaq.download-tracker

# サービス停止
launchctl stop com.gaq.download-tracker

# サービス無効化
launchctl unload ~/Library/LaunchAgents/com.gaq.download-tracker.plist

# サービス再有効化
launchctl load ~/Library/LaunchAgents/com.gaq.download-tracker.plist
```

## データの活用例

### Excelで開く

CSVファイルをExcelやGoogle Sheetsで開いて分析できます。

### コマンドラインで集計

```bash
# 最新10件の記録を表示
tail -n 10 /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv

# GaQの総ダウンロード数
grep "\"GaQ\"" /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv | \
  awk -F',' '{sum+=$6} END {print "GaQ Total:", sum}'

# PoPuPの総ダウンロード数
grep "\"PoPuP\"" /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv | \
  awk -F',' '{sum+=$6} END {print "PoPuP Total:", sum}'

# 全体の総ダウンロード数
awk -F',' 'NR>1 {sum+=$6} END {print "Overall Total:", sum}' \
  /Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv
```

### グラフ化

Pythonやスプレッドソフトを使用して、時系列グラフを作成できます。

```python
import pandas as pd
import matplotlib.pyplot as plt

# CSVを読み込み
df = pd.read_csv('/Users/yoshihitotsuji/Claude_Code/AccessLog/downloads_all.csv')

# 日付ごとにグループ化
df['記録日時'] = pd.to_datetime(df['記録日時'])
daily_downloads = df.groupby('記録日時')['ダウンロード数'].sum()

# グラフ化
daily_downloads.plot(kind='line', title='Daily Downloads')
plt.show()
```

## トラブルシューティング

### 問題: スクリプトが実行されない

```bash
# 実行権限を確認
ls -la ./scripts/track_downloads.sh

# 実行権限がない場合
chmod +x ./scripts/track_downloads.sh
```

### 問題: GitHub認証エラー

```bash
# 認証状態を確認
gh auth status

# 再認証
gh auth login
```

### 問題: データが記録されない

```bash
# エラーログを確認
cat /Users/yoshihitotsuji/Claude_Code/AccessLog/tracker_error.log

# 手動実行でテスト
./scripts/track_downloads.sh
```

### 問題: サービスが起動しない

```bash
# サービスの状態を確認
launchctl list | grep gaq

# plistファイルの構文チェック
plutil ~/Library/LaunchAgents/com.gaq.download-tracker.plist

# 再インストール
./scripts/setup_tracker.sh
```

## セキュリティとプライバシー

- このシステムは**読み取り専用**です
- GitHub Releaseの公開情報のみを取得します
- 個人を特定できる情報は記録されません
- ダウンロード数の集計データのみが保存されます

## 今後の拡張案

- [x] 複数リポジトリ対応（GaQ_app, Pop_app）
- [ ] 週次・月次レポートの自動生成
- [ ] Slack/メール通知機能
- [ ] Webダッシュボード
- [ ] グラフ自動生成
- [ ] 追加リポジトリの簡単な設定方法

## サポート

詳細なドキュメント: [DOWNLOAD_TRACKER_SETUP.md](DOWNLOAD_TRACKER_SETUP.md)

## ライセンス

MIT License

---

作成日: 2025-11-13
