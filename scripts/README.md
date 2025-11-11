# Scripts / スクリプト

このディレクトリには、プロジェクト管理用のユーティリティスクリプトが含まれています。

## 📊 check_download_stats.py

GitHub Releaseのダウンロード統計を取得するスクリプトです。

### 対象プロジェクト

- **GaQ_app** (Mac/Windows)
- **PoPuP** (Windows)

### 使用方法

#### 基本的な使用

```bash
# すべてのプロジェクトの統計を表示
python3 scripts/check_download_stats.py

# 特定のプロジェクトのみ表示
python3 scripts/check_download_stats.py --project gaq
python3 scripts/check_download_stats.py --project popup
```

#### 出力形式の選択

```bash
# CSV形式で出力
python3 scripts/check_download_stats.py --csv

# JSON形式で出力
python3 scripts/check_download_stats.py --json

# CSVファイルに保存
python3 scripts/check_download_stats.py --csv > stats.csv
```

#### オプション

- `--csv`: CSV形式で出力
- `--json`: JSON形式で出力
- `--days N`: 直近N日間の平均を表示（デフォルト: 7）
- `--project NAME`: 特定プロジェクトのみ表示 (`gaq` または `popup`)
- `--help`: ヘルプ表示

### 環境変数

#### GITHUB_TOKEN（推奨）

GitHub Personal Access Tokenを設定すると、API制限が緩和されます。

```bash
# トークンを設定
export GITHUB_TOKEN="your_github_token_here"

# 統計取得
python3 scripts/check_download_stats.py
```

**Personal Access Tokenの作成方法**:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" をクリック
3. Scopes: `public_repo` を選択
4. トークンをコピーして環境変数に設定

### 出力例

#### プリティ出力（デフォルト）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 GaQ_app
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
リリース: v1.1.1
公開日: 2025-11-11T03:26:06Z (0 日前)

  GaQ_Transcriber_v1.1.1_mac.dmg                           2 DL  (N/A/日)
  GaQ_Transcriber_v1.1.1_mac.dmg.sha256                    1 DL  (N/A/日)

📊 合計ダウンロード数: 3
```

#### CSV出力

```csv
project,platform,release,asset,downloads,days_since,avg_per_day,published_at
GaQ_app,macOS,v1.1.1,GaQ_Transcriber_v1.1.1_mac.dmg,2,0,N/A,2025-11-11T03:26:06Z
GaQ_app,macOS,v1.1.1,GaQ_Transcriber_v1.1.1_mac.dmg.sha256,1,0,N/A,2025-11-11T03:26:06Z
```

#### JSON出力

```json
{
  "generated_at": "2025-11-11T04:30:03Z",
  "days_filter": 7,
  "projects": [
    {
      "name": "GaQ_app",
      "release": "v1.1.1",
      "total_downloads": 3,
      "days_since_release": 0,
      "assets": [...]
    }
  ]
}
```

### プラットフォーム判定

スクリプトは、アセット名から自動的にプラットフォームを判定します：

- **macOS**: `.dmg`, `mac`, `Mac` を含むファイル
- **Windows**: `.exe`, `.zip`, `Windows`, `Portable` を含むファイル
- **Hash**: `.sha256` を含むファイル
- **Unknown**: 上記以外

---

## ⏰ daily_stats_collect.sh

ダウンロード統計を自動収集するラッパースクリプトです。毎日00:00に実行されることを想定しています。

### 機能

- ダウンロード統計をCSV形式で収集
- 日付別のファイルに保存 (`stats/downloads_YYYY-MM-DD.csv`)
- 実行ログを記録 (`logs/stats_collection.log`)

### 手動実行

```bash
./scripts/daily_stats_collect.sh
```

### 自動実行の設定

`setup_daily_stats.sh` スクリプトを使用して設定できます（後述）。

または、手動でcrontabに追加：

```bash
# crontabを開く
crontab -e

# 以下を追加（パスは実際の環境に合わせて変更）
0 0 * * * cd /Users/ytsuji/dev/GaQ_app && ./scripts/daily_stats_collect.sh >> /Users/ytsuji/dev/GaQ_app/logs/cron.log 2>&1
```

### 出力先

- **統計データ**: `stats/downloads_YYYY-MM-DD.csv`
- **実行ログ**: `logs/stats_collection.log`
- **cronログ**: `logs/cron.log`

---

## ⚙️ setup_daily_stats.sh

毎日00:00の自動統計収集を設定するセットアップスクリプトです。

### 使用方法

```bash
./scripts/setup_daily_stats.sh
```

### セットアップ内容

1. 必要なディレクトリを作成（`stats/`, `logs/`）
2. cron設定コマンドを表示
3. テスト実行を提供

### セットアップ手順

スクリプトを実行すると、以下の手順が案内されます：

1. スクリプトを実行
2. 表示されたcronコマンドをコピー
3. `crontab -e` で設定を追加
4. 保存して完了

### 環境変数の設定（推奨）

API制限を緩和するため、GITHUB_TOKENの設定を推奨します：

```bash
# ~/.zshrc または ~/.bash_profile に追加
export GITHUB_TOKEN="your_github_token_here"
```

---

## 🔧 check_sync.sh

Mac版とWindows版のソースコード同期状態を確認するスクリプトです。

### 使用方法

```bash
./scripts/check_sync.sh
```

詳細は [release/README.md](../release/README.md) を参照してください。

---

## 📝 新しいスクリプトの追加

新しいスクリプトを追加する際の規則：

1. **実行権限を付与**: `chmod +x scripts/your_script.sh`
2. **Shebang行を追加**: `#!/usr/bin/env bash` または `#!/usr/bin/env python3`
3. **このREADMEに使用方法を追記**
4. **コメントで目的と使用方法を明記**

---

**最終更新**: 2025-11-11
