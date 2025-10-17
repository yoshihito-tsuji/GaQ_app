# GaQ Offline Transcriber

オフライン動作するAI文字起こしアプリケーション

## 基本情報

- **バージョン**:
  - Mac版: v1.1.1
  - Windows版: v1.1.0
- **開発元**: [公立はこだて未来大学 辻研究室](https://tsuji-lab.net)
- **対応プラットフォーム**: macOS、Windows
- **文字起こしエンジン**: faster-whisper

## ⚠️ 緊急対応課題（Mac版 v1.1.1）

- 最新ビルド `GaQ_Transcriber_v1.1.1_mac.dmg` でアプリを起動すると、ウィンドウ上に `Internal Server Error` が表示され操作できない問題が発生中です。
- 原因調査と修正対応は **翌営業日以降に着手予定**。進行状況は `docs/development/` 配下の最新ログを参照してください。
- ユーザーへの配布・更新案内は、不具合の切り分けが完了するまで一時停止してください。

## 主要機能

- faster-whisper文字起こし（Medium/Large-v3対応）
- リアルタイムプログレスバー
- 改行処理（句読点・80文字折り返し）
- 結果コピー・txt保存機能
- モデル管理機能

## 動作環境

### macOS版
- macOS 10.15以降
- 推奨: 8GB RAM以上
- Python 3.12.7同梱（追加インストール不要）

### Windows版
- Windows 10/11
- 推奨: 8GB RAM以上

## オフライン動作について

- **初回起動時のみ**音声認識モデル（約1.5GB～2.9GB）のダウンロードが必要
- モデルダウンロード後は完全にオフラインで動作

## 配布パッケージ

### macOS版
- **完全パッケージ版**: `GaQ_Transcriber_v1.1.1_mac.dmg` (約187MB)
  - Python 3.12.12環境同梱
  - ドラッグ&ドロップですぐに使用可能
  - v1.1.1: 起動不具合修正 + Python 3.12固定ビルド

### Windows版
- **ポータブルZIP版**: `GaQ_Transcriber_Windows_v1.1.0_Portable.zip` (138MB)
- **インストーラ版**: `GaQ_Transcriber_Windows_v1.1.0_Setup.exe` (95MB)

## ディレクトリ構成

```
GaQ_app_v1.1.0/
├── build_standard/              # macOS配布版（完全パッケージ）
├── release/windows/             # Windows版
├── docs/                        # 📖 すべてのドキュメント
│   ├── PROJECT_OVERVIEW.md      # プロジェクト詳細概要
│   ├── HISTORY.md               # 開発履歴
│   ├── development/             # 開発記録・エラーログ
│   ├── releases/                # リリース履歴・レポート
│   ├── guides/                  # ビルドガイド・手順書
│   └── troubleshooting/         # トラブルシューティング
└── README.md                    # このファイル
```

## 📖 ドキュメント

**すべての開発記録、リリース情報、ガイド、トラブルシューティングは[docs/](docs/)ディレクトリにあります。**

### 主要ドキュメント

- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** - プロジェクトの詳細概要
- **[docs/HISTORY.md](docs/HISTORY.md)** - 開発履歴・変更履歴
- **[docs/guides/BUILD_GUIDE.md](docs/guides/BUILD_GUIDE.md)** - ビルド手順
- **[docs/releases/](docs/releases/)** - リリース作業報告
- **[docs/development/](docs/development/)** - 日々の開発記録

## 開発ブランチ

- **main**: 本番リリース版
- **dev**: 開発・検証・エラー対策ブランチ

---

## 🚀 開発者向け：開発ワークフロー

**⚠️ 開発作業を開始する前に必ずこのセクションを確認してください**

### 1. 作業開始時

#### 必須：過去の記録を確認
```bash
# プロジェクト概要と開発履歴を確認
cat docs/PROJECT_OVERVIEW.md
cat docs/HISTORY.md

# 最近の開発ログを確認
ls -lt docs/development/*.md | head -5
```

#### 必須：新規開発ログを作成
```bash
# テンプレートをコピーして今日の作業ログを作成
cp docs/development/DAILY_LOG_TEMPLATE.md docs/development/$(date +%Y%m%d)_brief_description.md

# エディタで開いて作業内容を記録
code docs/development/$(date +%Y%m%d)_brief_description.md
```

### 2. 開発中

#### エラー発生時：エラーログを作成
```bash
# errorsディレクトリを作成（初回のみ）
mkdir -p docs/development/errors

# エラーログを作成
cp docs/development/ERROR_LOG_TEMPLATE.md docs/development/errors/ERROR_brief_description.md

# エラー内容、原因、解決策を記録
code docs/development/errors/ERROR_brief_description.md
```

#### 記録すべき内容
- ✅ 実装した機能の詳細
- ✅ 変更したファイルとその理由
- ✅ 発生したエラーと解決方法
- ✅ テスト結果
- ✅ 次にやるべきこと

### 3. 作業終了時

#### 必須：開発ログを更新
```bash
# 今日の作業ログに結果とテスト内容を追記
code docs/development/$(date +%Y%m%d)_*.md
```

#### コミット前の確認
- [ ] 開発ログが完成している
- [ ] エラーログが適切に記録されている
- [ ] docs/HISTORY.mdに重要な変更を追記（必要に応じて）

### 4. ファイル命名規則

- **日次ログ**: `YYYYMMDD_brief_description.md`
  - 例: `20251009_progress_bar_fix.md`
- **エラーログ**: `errors/ERROR_brief_description.md`
  - 例: `errors/ERROR_model_download_failed.md`

### 📚 詳細な開発記録ガイド

開発記録の詳しい書き方は以下を参照：
- **[docs/development/README.md](docs/development/README.md)** - 開発記録の書き方、テンプレート使用方法

---

## ビルド方法

詳細は[docs/guides/BUILD_GUIDE.md](docs/guides/BUILD_GUIDE.md)を参照してください。

### macOS版（簡易版）
```bash
cd release/mac
source venv/bin/activate
pyinstaller GaQ_Transcriber.spec
```

### Windows版（簡易版）
```powershell
cd release\windows
venv\Scripts\activate
pyinstaller GaQ_Transcriber.spec
```

## トラブルシューティング

問題が発生した場合は、以下のドキュメントを参照してください：

- [docs/troubleshooting/](docs/troubleshooting/)
- [docs/guides/BUILD_GUIDE.md](docs/guides/BUILD_GUIDE.md) - トラブルシューティングセクション

## ライセンス

このプロジェクトは公立はこだて未来大学 辻研究室によって開発されています。

## 連絡先

- **Website**: https://tsuji-lab.net
- **開発元**: 公立はこだて未来大学 辻研究室

---

**最終更新**: 2025-10-16
**バージョン**: Mac v1.1.1 / Windows v1.1.0
**ステータス**: リリース済み
