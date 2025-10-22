# Development - 開発記録

このディレクトリには日々の開発記録、エラーログ、実装メモを保管します。

## ディレクトリ構成

```
development/
├── README.md                    # このファイル
├── DAILY_LOG_TEMPLATE.md        # 日次開発ログのテンプレート
├── ERROR_LOG_TEMPLATE.md        # エラーログのテンプレート
├── YYYYMMDD_*.md               # 日次開発ログ（例: 20251009_ui_improvement.md）
└── errors/                      # エラー関連ドキュメント
    └── ERROR_*.md              # 個別エラーログ
```

## ファイル命名規則

### 日次開発ログ
- フォーマット: `YYYYMMDD_brief_description.md`
- 例: `20251009_progress_bar_fix.md`
- 例: `20251010_model_cache_improvement.md`

### エラーログ
- フォーマット: `errors/ERROR_brief_description.md`
- 例: `errors/ERROR_winerror_1314.md`
- 例: `errors/ERROR_model_download_failed.md`

## テンプレート使用方法

### 新規開発ログを作成する場合

```bash
# テンプレートをコピー
cp docs/development/DAILY_LOG_TEMPLATE.md docs/development/$(date +%Y%m%d)_description.md

# エディタで編集
code docs/development/$(date +%Y%m%d)_description.md
```

### エラーログを作成する場合

```bash
# errorsディレクトリを作成（初回のみ）
mkdir -p docs/development/errors

# テンプレートをコピー
cp docs/development/ERROR_LOG_TEMPLATE.md docs/development/errors/ERROR_description.md

# エディタで編集
code docs/development/errors/ERROR_description.md
```

## 記録する内容

### 必ず記録すべきこと
- ✅ 実装した機能の詳細
- ✅ 発生したエラーと解決方法
- ✅ 変更したファイルとその理由
- ✅ テスト結果
- ✅ 次にやるべきこと

### 記録推奨
- 🔍 調査したこと（コードリーディング、ライブラリ調査など）
- 💡 学んだこと、気づいたこと
- ⚠️ 注意が必要な箇所
- 🚧 未解決の課題

## 開発ワークフロー

1. **作業開始時**: 日次ログを作成し、作業内容を記録
2. **エラー発生時**: エラーログを作成し、調査・解決過程を記録
3. **作業終了時**: 日次ログに結果とテスト内容を追記
4. **重要な変更**: コミット前にログを確認・更新

## 既存の開発記録

現在のプロジェクトの開発履歴は以下を参照：
- [../HISTORY.md](../HISTORY.md) - プロジェクト全体の履歴
- [../releases/](../releases/) - リリース関連の記録

---

**最終更新**: 2025-10-09
