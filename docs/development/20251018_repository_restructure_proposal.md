# リポジトリ構成改善提案

**作成日**: 2025-10-18
**作成者**: Claude Code
**ステータス**: 提案（レビュー待ち）

---

## 📋 現状の問題点

### 1. **コードの重複と不整合リスク**

現在、主要なPythonファイルが複数のディレクトリに重複して存在しています：

```
./build_standard/main.py              (1247行)
./release/mac/src/main.py             (1958行) ← 最新版（pywebview対応済み）
./release/windows/src/main.py         (1525行)
./launcher_final/.../main.py          (古い版)

./build_standard/transcribe.py
./release/mac/src/transcribe.py       ← 各々が異なる内容
./release/windows/src/transcribe.py
./launcher_final/.../transcribe.py
```

**リスク**:
- ✗ 片方だけ修正して他方が取り残される（今回のpywebview問題がこれに該当）
- ✗ どのファイルが「正」なのか不明確
- ✗ 行数が大幅に異なる（main.py: 1247行 vs 1958行）
- ✗ diff確認が手作業で、同期漏れが発生しやすい

### 2. **ディレクトリの役割が不明確**

| ディレクトリ | 現状の役割（推測） | 問題点 |
|---|---|---|
| `build_standard/` | macOS完全パッケージ版？ | 古いコード（pywebview対応なし） |
| `release/mac/` | Mac版実際のビルド元 | ✅ 最新だが、独立して編集されている |
| `release/windows/` | Windows版ビルド元 | ✅ 独立して編集されている |
| `launcher_final/` | 軽量インストーラー版 | ❌ 不採用だが残存している |

**問題**:
- README.mdでは「`build_standard/` = macOS配布版」と記載されているが、実際は`release/mac/`が使われている
- 「手編集すべきソース」と「自動生成物」の区別がない

### 3. **開発プロセスの文書化不足**

現在のREADMEには以下が欠けています：

- ✗ 「どのディレクトリを編集すべきか」の明示
- ✗ 「複数環境向けに機能追加する際の手順」
- ✗ 「ビルド成果物の生成方法」（手動コピー？スクリプト？）
- ✗ 「コード同期の確認方法」

---

## 🎯 改善提案

### 提案1: 単一ソースの原則（Single Source of Truth）

#### 理想的な構成

```
GaQ_app_v1.1.0/
├── src/                          # 📝 唯一の編集対象（共通ソース）
│   ├── main.py                   # FastAPI + pywebview統合
│   ├── main_app.py               # アプリケーションエントリーポイント
│   ├── transcribe.py             # 文字起こし処理
│   ├── config.py                 # 設定
│   ├── templates/                # HTMLテンプレート（Jinja2）
│   │   └── index.html.j2
│   └── static/                   # 静的ファイル
│       ├── css/
│       └── js/
├── build/                        # 🤖 自動生成ディレクトリ（編集禁止）
│   ├── mac/                      # Mac版ビルド成果物
│   │   ├── src/ -> ../../src/   # シンボリックリンクまたはコピー
│   │   ├── GaQ_Transcriber.spec
│   │   └── dist/
│   └── windows/                  # Windows版ビルド成果物
│       ├── src/ -> ../../src/
│       ├── GaQ_Transcriber.spec
│       └── dist/
├── scripts/                      # ビルドスクリプト
│   ├── build_mac.sh
│   ├── build_windows.bat
│   └── sync_check.sh             # ソース同期確認スクリプト
├── docs/
└── README.md
```

#### 暫定的な構成（既存を活かす）

```
GaQ_app_v1.1.0/
├── src/                          # 📝 新規作成：唯一の編集対象
│   ├── common/                   # プラットフォーム共通コード
│   │   ├── transcribe.py
│   │   └── config.py
│   ├── platforms/                # プラットフォーム固有コード
│   │   ├── mac/
│   │   │   ├── main_app.py      # macOS固有処理
│   │   │   └── bridge.py        # pywebview Bridge
│   │   └── windows/
│   │       └── main_app.py      # Windows固有処理
│   └── templates/
│       └── index.html.j2
├── release/                      # 🤖 自動生成（手編集禁止）
│   ├── README.md                 # ⚠️ このディレクトリは自動生成です
│   ├── mac/
│   │   ├── src/ ← scripts/sync_sources.shで生成
│   │   └── build.sh
│   └── windows/
│       ├── src/ ← scripts/sync_sources.batで生成
│       └── build.bat
├── scripts/
│   ├── sync_sources.sh           # src/ → release/*/src/ にコピー
│   ├── check_sync.sh             # 差分チェック
│   └── build_all.sh              # 全プラットフォームビルド
├── build_standard/               # 🗑️ 削除予定（deprecated）
├── launcher_final/               # 🗑️ 削除予定（不採用版）
└── README.md
```

---

## 📝 README.md 改善案

### 追加すべきセクション

#### 1. 開発方針・品質基準

```markdown
## 🛡️ 開発方針・品質基準

### コード管理の原則

1. **単一ソースの原則（Single Source of Truth）**
   - 編集対象は `src/` ディレクトリのみ
   - `release/mac/src/`, `release/windows/src/` は自動生成ファイル（手編集禁止）
   - 修正は必ず `src/` で行い、スクリプトで全環境に反映

2. **複数環境への機能追加手順**
   ```bash
   # 1. src/ で編集
   vim src/common/transcribe.py

   # 2. 全環境にソースを同期
   ./scripts/sync_sources.sh

   # 3. 差分がないことを確認
   ./scripts/check_sync.sh

   # 4. 各環境でビルド＆テスト
   cd release/mac && ./build.sh
   cd release/windows && ./build.bat
   ```

3. **進捗機能など主要処理の編集ルール**
   - プログレスバー、文字起こしエンジン、UI/UXなど主要機能は全環境で完全同期必須
   - 編集後は必ず `./scripts/check_sync.sh` で差分チェック
   - プラットフォーム固有の処理は `src/platforms/{mac,windows}/` に分離

### 禁止事項

- ❌ `release/mac/src/main.py` を直接編集
- ❌ `release/windows/src/main.py` を直接編集
- ❌ 片方の環境だけ修正して他方を忘れる
- ❌ HTML/JSの巨大な生文字列を直接main.pyに埋め込む

### 推奨事項

- ✅ `src/` で編集 → `scripts/sync_sources.sh` で同期
- ✅ HTMLテンプレートはJinja2化して `src/templates/` に配置
- ✅ プラットフォーム差分は設定ファイル（`config.py`）で吸収
- ✅ コミット前に `check_sync.sh` で差分確認
```

#### 2. 承認フロー

```markdown
## ✅ 承認フロー

### 開発作業の手順

#### 1. 作業開始時
- [ ] 過去の開発ログ確認（`docs/HISTORY.md`, `docs/development/`）
- [ ] 今日の作業ログを作成（`docs/development/YYYYMMDD_*.md`）
- [ ] 現在のソース同期状態を確認（`./scripts/check_sync.sh`）

#### 2. 開発中
- [ ] `src/` で編集
- [ ] プラットフォーム固有処理は `src/platforms/` に分離
- [ ] エラー発生時はエラーログ作成（`docs/development/errors/ERROR_*.md`）

#### 3. 編集完了時
- [ ] `./scripts/sync_sources.sh` でソース同期
- [ ] `./scripts/check_sync.sh` で差分なしを確認
- [ ] 各環境でビルド＆テスト
- [ ] 開発ログに結果を記録

#### 4. コミット前
- [ ] 開発ログが完成している
- [ ] エラーログが適切に記録されている
- [ ] `docs/HISTORY.md` に重要な変更を追記
- [ ] **ソース同期が完了している（check_sync.sh で確認済み）**

### コードレビュー基準

- ✅ すべてのプラットフォームでビルド成功
- ✅ 主要機能（ファイル選択、文字起こし、保存、コピー）が動作
- ✅ ソース同期が確認されている
- ✅ 開発ログが完備されている
```

#### 3. ディレクトリ構成の明確化

```markdown
## 📁 ディレクトリ構成

```
GaQ_app_v1.1.0/
├── src/                          # 📝 編集対象：共通ソース
│   ├── common/                   # プラットフォーム共通コード
│   ├── platforms/                # プラットフォーム固有コード
│   └── templates/                # HTMLテンプレート
├── release/                      # 🤖 自動生成（手編集禁止）
│   ├── mac/                      # Mac版ビルド環境
│   └── windows/                  # Windows版ビルド環境
├── scripts/                      # ビルド＆同期スクリプト
│   ├── sync_sources.sh           # ソース同期
│   ├── check_sync.sh             # 差分チェック
│   └── build_all.sh              # 全環境ビルド
├── docs/                         # ドキュメント
└── README.md
```

### 重要なルール

⚠️ **`release/mac/src/` と `release/windows/src/` は自動生成ファイルです**

- これらのファイルは `scripts/sync_sources.sh` で `src/` からコピーされます
- 直接編集しても、次回の同期時に上書きされます
- 編集は必ず `src/` で行ってください
```

---

## 🔧 実装計画

### フェーズ1: 暫定対応（即座に実施可能）

#### 1.1. ドキュメント整備
- [ ] README.mdに「開発方針・品質基準」セクションを追加
- [ ] `release/README.md` を作成し、「手編集禁止」を明記
- [ ] 既存の開発ログテンプレートに「ソース同期確認」チェック項目を追加

#### 1.2. スクリプト作成
- [ ] `scripts/check_sync.sh` - 主要ファイルのdiff確認スクリプト
- [ ] CI用チェックリスト作成（`docs/development/CI_CHECKLIST.md`）

### フェーズ2: 段階的移行（中期）

#### 2.1. `src/` ディレクトリ作成
- [ ] `src/common/` に共通コードを集約
- [ ] `src/platforms/{mac,windows}/` に固有コードを分離
- [ ] HTMLテンプレートをJinja2化（`src/templates/`）

#### 2.2. 自動同期スクリプト作成
- [ ] `scripts/sync_sources.sh` - `src/` → `release/*/src/` にコピー
- [ ] `scripts/build_all.sh` - 全環境の自動ビルド

#### 2.3. ビルドプロセスの自動化
- [ ] `release/mac/build.sh` を修正（sync → build → test）
- [ ] `release/windows/build.bat` を修正

### フェーズ3: 完全移行（長期）

#### 3.1. 不要ディレクトリの削除
- [ ] `build_standard/` を削除（または `deprecated/` に移動）
- [ ] `launcher_final/` を削除（または `deprecated/` に移動）

#### 3.2. CI/CD導入
- [ ] GitHub Actions設定（`.github/workflows/`）
- [ ] 自動diff チェック
- [ ] 自動ビルドテスト（Mac/Windows）

---

## 📊 優先順位

| 項目 | 優先度 | 実施時期 | 理由 |
|---|---|---|---|
| README.md改善 | 🔴 最高 | 即座 | 再発防止のため |
| `check_sync.sh` 作成 | 🔴 最高 | 即座 | 現状の問題検出 |
| `release/README.md` 作成 | 🔴 最高 | 即座 | 誤編集防止 |
| CI チェックリスト作成 | 🟡 高 | 1週間以内 | 品質保証 |
| `src/` ディレクトリ作成 | 🟡 高 | 2週間以内 | 根本解決 |
| 自動同期スクリプト | 🟡 高 | 2週間以内 | 作業効率化 |
| HTMLテンプレート化 | 🟢 中 | 1ヶ月以内 | 保守性向上 |
| CI/CD導入 | 🟢 中 | 2ヶ月以内 | 完全自動化 |
| 不要ディレクトリ削除 | 🔵 低 | 3ヶ月以内 | クリーンアップ |

---

## 🎯 次のアクション

1. **このドキュメントのレビュー**
   - 提案内容の確認
   - 優先順位の調整
   - 実施計画の合意

2. **即座に実施（合意後）**
   - README.md改善
   - `scripts/check_sync.sh` 作成
   - `release/README.md` 作成

3. **段階的実施**
   - フェーズ1から順次実施
   - 各フェーズ完了後にレビュー

---

## 📚 参考資料

- [docs/HISTORY.md](../HISTORY.md) - 過去の問題発生履歴
- [docs/development/20251009_docs_restructure.md](20251009_docs_restructure.md) - ドキュメント構造改善
- [今回のpywebview問題](20251018_final_completion_report.md) - コード不整合の実例

---

**レビュー待ち** - このドキュメントの内容について、ご意見・修正案をお聞かせください。
