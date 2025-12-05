# Development Workflow & Repository Rules

開発関連のルール・チェックリスト・ワークフローを README から分離し、ここに集約しました。ClaudeCode が後続作業を行う際の参照先として利用してください。

## リポジトリ構成（運用中のガイドライン）

```text
GaQ_app/
├── release/               # Mac / Windows ビルドソース（同一内容を維持）
│   ├── mac/
│   └── windows/
├── scripts/               # 同期・ビルド補助スクリプト
├── docs/                  # ドキュメント一式
└── README.md              # 利用者向け概要
```

### 重要な注意事項

- `release/mac/src/` と `release/windows/src/` は必ず同期させる（Single Source of Truth）
- 差分確認は `./scripts/check_sync.sh` をコミット前後に実行
- `build_standard/` と `launcher_final/` は旧構成のため編集禁止
- 会話（AI 間含む）は日本語で記録

## 編集ルールと推奨手順

1. 共通コード（`transcribe.py`, `config.py` など）は Mac/Windows 両方を同時に更新
2. プラットフォーム固有コードでも共通部分は整合性を確認
3. HTML/JS の巨大文字列を Python に直接埋め込むのは避け、テンプレート化を検討
4. 編集後は両環境でビルドし、主要フロー（ファイル選択・文字起こし・保存・コピー）を確認

### 進捗機能の扱い

- プログレスバーとモデル管理の処理は全環境で完全同期が必須
- `progress_callback` や SSE の扱いは差分が混入しやすいため、修正点をログに残す

## チェックリスト

### 作業開始

- 過去ログを確認（`docs/HISTORY.md`, `docs/development/`）
- 当日の開発ログを `docs/development/YYYYMMDD_*.md` として作成
- `./scripts/check_sync.sh` で同期基準を確認

### 作業中

- 共通コードは両ビルド環境で編集
- エラーが起きたら `docs/development/errors/ERROR_*.md` へ記録
- 大きな変更は途中でもコミットしておく

### 作業完了

- `./scripts/check_sync.sh` で差分ゼロを確認
- `cd release/mac && ./build.sh`
- `cd release/windows && ./build.bat`
- 主要機能のテスト結果を開発ログに追記

### コミット前

- 開発ログとエラーログを更新
- 重要変更は `docs/HISTORY.md` に追記（必要時）
- 同期チェックとビルド確認済みであることを明記

### コードレビュー時の基準

- すべてのプラットフォームでビルド成功
- 主要機能が正常動作
- `./scripts/check_sync.sh` 実行済み
- ログ・エラーログがそろっている

## Git 運用とビルド

- `gacp "message"`: 変更を追加 → コミット → push（ビルドなしの保存用 workflow）
- 手動ビルド: `release/mac` / `release/windows` ディレクトリでローカルビルド
- **GitHub Actions**: v* タグで自動ビルド・リリース（導入済み）

## GitHub Actions 自動ビルド

### ワークフロー概要

`.github/workflows/build-release.yml` でmacOS/Windowsの自動ビルドとGitHub Release作成を行います。

### トリガー

| トリガー | 動作 |
| --- | --- |
| タグプッシュ（`v*`） | 自動ビルド → Draft Release作成 |
| 手動実行（workflow_dispatch） | バージョン指定でビルド |

### 実行方法

#### 方法1: タグプッシュ（推奨）

```bash
# バージョンタグを作成してプッシュ
git tag v1.2.0
git push origin v1.2.0
```

#### 方法2: 手動実行

1. GitHub → Actions → "Build and Release" を選択
2. "Run workflow" をクリック
3. バージョン番号を入力（例: `1.2.0`）
4. 必要に応じて "Skip macOS notarization" をチェック
5. "Run workflow" で実行

### ビルド成果物

| プラットフォーム | 成果物 | 備考 |
| --- | --- | --- |
| macOS | `GaQ_Transcriber_v{version}_mac.dmg` | 署名・公証済み |
| macOS | `*.dmg.sha256` | SHA256ハッシュ |
| Windows | `GaQ_Transcriber_Windows_v{version}_Portable.zip` | 未署名 |
| Windows | `*.zip.sha256` | SHA256ハッシュ |

### 必要なSecrets

GitHubリポジトリの Settings → Secrets and variables → Actions で設定:

| Secret名 | 説明 | 取得方法 |
| --- | --- | --- |
| `APPLE_DEVELOPER_ID_CERT_BASE64` | Developer ID証明書（.p12をbase64化） | 下記参照 |
| `APPLE_DEVELOPER_ID_CERT_PASSWORD` | 証明書のパスフレーズ | 証明書エクスポート時に設定 |
| `APPLE_ID` | Apple ID（メールアドレス） | Apple Developer登録時のメール |
| `APPLE_TEAM_ID` | Apple Developer Team ID | Developer Portalで確認 |
| `APPLE_APP_SPECIFIC_PASSWORD` | App固有パスワード | appleid.apple.comで生成 |

### 証明書のbase64エンコード方法

```bash
# Keychainから証明書をエクスポート（.p12形式）
# Keychain Access → 証明書を右クリック → 書き出す

# base64エンコード
base64 -i DeveloperID.p12 | pbcopy

# クリップボードの内容をGitHub Secretsに貼り付け
```

### App固有パスワードの生成

1. [appleid.apple.com](https://appleid.apple.com) にサインイン
2. セキュリティ → App固有パスワード → パスワードを生成
3. 生成されたパスワードを `APPLE_APP_SPECIFIC_PASSWORD` に設定

### ワークフロー実行後

1. Actions タブでビルド状況を確認
2. 成功後、Releases タブに Draft リリースが作成される
3. リリースノートを確認・編集
4. "Publish release" で公開

### ショートカット例

```bash
gacp() {
  local msg="${1:-update}"
  git add -A
  git commit -m "$msg" || true
  git push
}
```

## 作業ログの付け方

```bash
cp docs/development/DAILY_LOG_TEMPLATE.md docs/development/$(date +%Y%m%d)_task_name.md
cp docs/development/ERROR_LOG_TEMPLATE.md docs/development/errors/ERROR_description.md
```

- 必ず「実装内容 / 発生した問題 / 対応状況 / テスト結果 / 次のアクション」を記録
- 重大な重大差分は `docs/HISTORY.md` にも要約を追記

## 再発防止の知見

- 2025-10-03 のプログレスバー進行不具合: `progress_callback` 渡し忘れ → 共通コードの変更は必ず両環境で動作確認
- 2025-10-17〜18 の pywebview 不具合: Mac のみ修正した結果、差分が拡大 → 片側だけの修正禁止
- 詳細レポート: `docs/releases/PROGRESS_BAR_FIX_REPORT.md`, `docs/development/20251018_final_completion_report.md`

## 将来の課題・改善

- Windows: MSIX 化 + コード署名の導入で SmartScreen を回避（検討中）
- リポジトリ再構成: `src/` を Single Source とし、自動同期スクリプトで `release/*/src/` を生成（提案: `docs/development/20251018_repository_restructure_proposal.md`）

---

このファイルを更新する際は、README に載せるべき最小限の情報（用途・操作・導線）から外れる内容を優先的にこちらへ移してください。
