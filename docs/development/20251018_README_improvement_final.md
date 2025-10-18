# README.md 改善案（最終版）

**作成日**: 2025-10-18
**目的**: 再発防止のための開発方針・品質基準・承認フローの明文化
**バージョン**: 最終版（レビュー反映済み）

---

## 挿入位置

この内容を `README.md` の L253（ディレクトリ構成の直後）に挿入してください。

---

## 🛡️ 開発方針・品質基準

### コード管理の原則

#### 1. 単一ソースの原則（Single Source of Truth）

**現状の暫定ルール**:
- `release/mac/src/` と `release/windows/src/` は本来は自動生成されるべきファイル
- 現在は手動で編集されているが、**必ず両方を同期させること**
- 編集後は `./scripts/check_sync.sh` で差分がないことを確認

**将来の理想形**:
- 編集対象は `src/` ディレクトリのみ
- `release/*/src/` は `scripts/sync_sources.sh` で自動生成
- 詳細は [docs/development/20251018_repository_restructure_proposal.md](docs/development/20251018_repository_restructure_proposal.md) を参照

#### 2. 複数環境への機能追加手順（現在）

**共通コード（transcribe.py, config.py）を編集する場合**:

```bash
# 1. Mac版を編集
vim release/mac/src/transcribe.py

# 2. Windows版も同じ内容に編集
vim release/windows/src/transcribe.py

# 3. 差分がないことを確認
./scripts/check_sync.sh

# 4. 各環境でビルド＆テスト
cd release/mac && ./build.sh
cd release/windows && ./build.bat
```

**プラットフォーム固有コード（main.py, main_app.py）を編集する場合**:
- Mac版とWindows版で行数が異なるのは正常（pywebview対応などの差異）
- ただし、共通部分（FastAPI ルーティング、文字起こし処理など）は同期すること
- 大きな機能追加時は両方を確認し、整合性を保つこと

#### 3. 進捗機能など主要処理の編集ルール

**以下の機能は全環境で完全同期が必須**:
- プログレスバー（`progress_callback`）
- 文字起こしエンジン（`transcribe.py`）
- モデル管理機能
- UI/UX（ファイル選択、ドラッグ&ドロップ）

**編集後の確認事項**:
- [ ] `./scripts/check_sync.sh` で差分チェック
- [ ] Mac版でビルド＆テスト
- [ ] Windows版でビルド＆テスト
- [ ] すべての主要機能が動作することを確認

#### 4. 禁止事項

- ❌ **片方の環境だけ修正して他方を忘れる**
  - 特に `transcribe.py`, `config.py` は完全に共通なので両方を同期すること
- ❌ **ソース同期確認なしでコミット**
  - コミット前に必ず `./scripts/check_sync.sh` を実行
- ❌ **HTML/JSの巨大な生文字列を直接main.pyに埋め込む**
  - 将来的にはテンプレート化（Jinja2）を検討
- ❌ **`build_standard/` または `launcher_final/` を編集**
  - これらは古いバージョンで、現在は使用されていません

#### 5. 推奨事項

- ✅ 共通コードは両環境を同時に編集
- ✅ 編集後は `./scripts/check_sync.sh` で確認
- ✅ プラットフォーム差分は最小限に抑える
- ✅ コミット前に両環境でビルド＆テスト
- ✅ 開発ログに同期確認の記録を残す

---

## ✅ 開発承認フロー

### 作業開始時のチェックリスト

- [ ] 過去の開発ログ確認（`docs/HISTORY.md`, `docs/development/`）
- [ ] 今日の作業ログを作成（`docs/development/YYYYMMDD_*.md`）
- [ ] **`./scripts/check_sync.sh` でソース同期状態を確認**

### 開発中のチェックリスト

- [ ] 共通コードは `release/mac/src/` と `release/windows/src/` の両方を編集
- [ ] プラットフォーム固有コードでも共通部分は同期
- [ ] エラー発生時はエラーログ作成（`docs/development/errors/ERROR_*.md`）
- [ ] 大きな変更の場合は段階的にコミット

### 編集完了時のチェックリスト

- [ ] **`./scripts/check_sync.sh` で差分なしを確認**
- [ ] Mac版でビルド成功を確認（`cd release/mac && ./build.sh`）
- [ ] Windows版でビルド成功を確認（`cd release/windows && ./build.bat`）
- [ ] 主要機能のテスト（ファイル選択、文字起こし、保存、コピー）
- [ ] 開発ログに結果を記録

### コミット前のチェックリスト

- [ ] 開発ログが完成している
- [ ] エラーログが適切に記録されている（エラー発生時）
- [ ] docs/HISTORY.md に重要な変更を追記（必要に応じて）
- [ ] **`./scripts/check_sync.sh` でソース同期を確認済み**
- [ ] すべてのプラットフォームでビルドが成功している
- [ ] すべてのプラットフォームで主要機能が正常に動作している

### コードレビュー基準

- ✅ すべてのプラットフォームでビルド成功
- ✅ 主要機能（ファイル選択、文字起こし、保存、コピー）が動作
- ✅ **`./scripts/check_sync.sh` でソース同期を確認済み**
- ✅ 開発ログが完備されている
- ✅ エラーログが適切に記録されている（エラー発生時）

---

## 🚨 再発防止のための重要な注意事項

### 過去に発生した問題

#### 問題1: プログレスバー進行問題（2025-10-03）
- **原因**: `transcribe()` メソッドに `progress_callback` が渡されていなかった
- **教訓**: 主要機能の修正は全環境で同期が必須
- **詳細**: [docs/releases/PROGRESS_BAR_FIX_REPORT.md](docs/releases/PROGRESS_BAR_FIX_REPORT.md)

#### 問題2: pywebview環境の動作不良（2025-10-17〜10-18）
- **原因**: Mac版のみpywebview対応を実装し、Windows版に反映されていなかった
- **教訓**: 片方だけ修正すると他方が取り残される
- **詳細**: [docs/development/20251018_final_completion_report.md](docs/development/20251018_final_completion_report.md)

### これらの問題を防ぐために

1. **`./scripts/check_sync.sh` を必ず実行**
   - コミット前に必ず実行
   - 差分が検出されたら必ず解消

2. **両環境で動作確認**
   - Mac版でビルド＆テスト
   - Windows版でビルド＆テスト（可能な場合）

3. **開発ログに同期確認を記録**
   - 「check_sync.sh 実行済み、差分なし」と明記

4. **将来的な改善計画**
   - `src/` ディレクトリに共通ソースを集約
   - 自動同期スクリプト（`scripts/sync_sources.sh`）の導入
   - CI/CD導入（自動ビルド＆テスト）

---

## 📚 関連ドキュメント

- **[release/README.md](release/README.md)** - releaseディレクトリの手編集禁止の注意事項
- **[docs/development/20251018_repository_restructure_proposal.md](docs/development/20251018_repository_restructure_proposal.md)** - リポジトリ構成改善提案
- **[scripts/check_sync.sh](scripts/check_sync.sh)** - ソース同期確認スクリプト

---
