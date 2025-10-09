# GaQ Offline Transcriber - Documentation

このディレクトリには、GaQ Offline Transcriberプロジェクトのすべてのドキュメントが格納されています。

## 📖 ドキュメント構成

### 概要ドキュメント
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - プロジェクトの詳細概要、技術スタック、配布方針
- **[HISTORY.md](HISTORY.md)** - プロジェクト全体の開発履歴と変更履歴

### ディレクトリ

#### [development/](development/)
日々の開発記録、エラーログ、実装メモ

- **[README.md](development/README.md)** - 開発記録の書き方、テンプレート使用方法
- **[DAILY_LOG_TEMPLATE.md](development/DAILY_LOG_TEMPLATE.md)** - 日次開発ログのテンプレート
- **[ERROR_LOG_TEMPLATE.md](development/ERROR_LOG_TEMPLATE.md)** - エラーログのテンプレート
- `YYYYMMDD_*.md` - 日次開発ログ（例: 20251009_ui_improvement.md）
- `errors/ERROR_*.md` - 個別エラーログ

#### [releases/](releases/)
リリース履歴、作業報告、修正レポート

- **[COMPLETION_REPORT.md](releases/COMPLETION_REPORT.md)** - v1.1.0リリース作業完了報告
- **[PROGRESS_BAR_FIX_REPORT.md](releases/PROGRESS_BAR_FIX_REPORT.md)** - プログレスバー修正レポート

#### [guides/](guides/)
ビルド手順、配布手順、環境セットアップガイド

- **[BUILD_GUIDE.md](guides/BUILD_GUIDE.md)** - macOS/Windowsのビルド手順、トラブルシューティング

#### [troubleshooting/](troubleshooting/)
よくある問題と解決策、エラー対策

## 🔍 ドキュメントの探し方

### プロジェクトについて知りたい
→ [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### 開発の経緯を知りたい
→ [HISTORY.md](HISTORY.md)

### ビルド方法を知りたい
→ [guides/BUILD_GUIDE.md](guides/BUILD_GUIDE.md)

### 特定の問題を解決したい
→ [troubleshooting/](troubleshooting/)

### 日々の開発記録を見たい
→ [development/](development/)

### リリース情報を見たい
→ [releases/](releases/)

## ✍️ ドキュメントの書き方

### 新規開発ログを作成
```bash
cp docs/development/DAILY_LOG_TEMPLATE.md docs/development/$(date +%Y%m%d)_description.md
```

### エラーログを作成
```bash
mkdir -p docs/development/errors
cp docs/development/ERROR_LOG_TEMPLATE.md docs/development/errors/ERROR_description.md
```

## 📋 記録する内容

### 必ず記録すべきこと
- ✅ 実装した機能の詳細
- ✅ 発生したエラーと解決方法
- ✅ 変更したファイルとその理由
- ✅ テスト結果
- ✅ 次にやるべきこと

### 記録推奨
- 🔍 調査したこと
- 💡 学んだこと、気づいたこと
- ⚠️ 注意が必要な箇所
- 🚧 未解決の課題

## 🚀 開発ワークフロー

1. **作業開始時**: 日次ログを作成
2. **エラー発生時**: エラーログを作成
3. **作業終了時**: 結果とテストを記録
4. **重要な変更**: コミット前にログを確認・更新

---

**最終更新**: 2025-10-09
**ブランチ**: dev
