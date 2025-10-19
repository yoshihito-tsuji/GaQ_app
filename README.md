# GaQ Offline Transcriber

オフライン動作するAI文字起こしアプリケーション

## 基本情報

- **バージョン**:
  - Mac版: v1.1.1
  - Windows版: v1.1.0
- **開発元**: [公立はこだて未来大学 辻研究室](https://tsuji-lab.net)
- **対応プラットフォーム**: macOS、Windows
- **文字起こしエンジン**: faster-whisper

## ✅ **Mac版v1.1.1 完全復旧完了！（2025-10-18更新）**

### 🎉 解決済み - すべての機能が動作します

Mac版v1.1.1において、pywebview環境でのすべての課題が解決され、**実用可能な状態**になりました！

#### ✅ 動作確認済み機能

1. **✅ ファイル選択** - クリックでファイル選択ダイアログが正常に動作
2. **✅ ドラッグ&ドロップ** - ファイルをドラッグ&ドロップで選択可能（新機能！）
3. **✅ 文字起こし実行** - Medium、Large-v3モデルで正常動作
4. **✅ リアルタイム進捗表示** - プログレスバーが正しく更新
5. **✅ 結果のコピー** - クリップボードへのコピーが確実に動作
6. **✅ 結果の保存** - メタデータ（文字数・処理時間）付きで保存
7. **✅ モデル選択** - モデル変更時のファイル再アップロードが正常動作

### 🔧 2025-10-18の主要改善内容

#### 1. ドラッグ&ドロップ機能の実装

**解決方法**: `text/uri-list` データ型からファイルパスを直接取得

```javascript
uploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    var uriList = e.dataTransfer.getData('text/uri-list');
    if (uriList) {
        var filePath = decodeURIComponent(uriList.replace('file://', '').trim());
        uploadFileViaPywebview(filePath, fileName);
    }
});
```

**成果**:

- ファイルをドラッグ&ドロップで選択できる
- クリック選択との併用が可能
- ユーザビリティが大幅に向上

#### 2. Large-v3選択時のエラー解決

**問題**: モデル変更時に「ファイルが見つかりません」エラー

**解決方法**: ファイルパスを保持し、文字起こし前に常に再アップロード

```javascript
window.uploadedFilePath = filePath;
if (window.uploadedFilePath) {
    var reuploadResult = await window.pywebview.api.upload_audio_file(window.uploadedFilePath);
    await startTranscriptionWithFileId(reuploadResult.file_id, fileName, model);
}
```

**成果**: モデル変更時も正しくファイルが処理される

#### 3. クリップボードコピーの完全実装

**解決方法**: AppleScript + 一時ファイル方式

```python
# 一時ファイルに保存
with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp:
    tmp.write(text)

# AppleScriptで読み込んでクリップボードにセット
applescript = '''
set fileContents to read fileRef as «class utf8»
set the clipboard to fileContents
'''
```

**成果**: 長文でも確実にクリップボードにコピーできる

#### 4. 保存ファイルへのメタデータ追加

**実装内容**:

```text
（文字起こし結果テキスト）

---
文字数：994文字
処理時間：1分20秒
```

**成果**: 保存ファイルに自動的に統計情報が追記される

#### 5. モデルダウンロードの改善

**変更内容**:

- 確認ダイアログを廃止（自動ダウンロード）
- トースト通知で進捗表示
- ダウンロード完了後、自動的に文字起こし開始

**成果**: ユーザー操作が減り、スムーズな体験を提供

### 📊 動作確認済み環境

- **OS**: macOS 14.8 (arm64)
- **Python**: 3.12.3
- **pywebview**: 6.0
- **PyInstaller**: 6.16.0
- **モデル**: Medium, Large-v3

### 📝 使い方

1. **DMGをマウント**: `GaQ_Transcriber_v1.1.1_mac.dmg` をダブルクリック
2. **アプリをインストール**: `GaQ Offline Transcriber.app` を Applications フォルダにドラッグ
3. **アプリを起動**: Applications フォルダから起動
4. **ファイルを選択**: クリックまたはドラッグ&ドロップ
5. **文字起こし実行**: 「文字起こし開始」ボタンをクリック
6. **結果を利用**: コピーまたは保存

### 🔍 トラブルシューティング

ログの確認:

```bash
tail -f ~/.gaq/logs/app.log
```

詳細は [docs/development/HISTORY.md](docs/development/HISTORY.md) を参照してください。

---

## 過去の問題（解決済み）

### pywebview環境での動作不良（2025-10-17 → 2025-10-18で解決）

以下の問題はすべて解決済みです：

1. **Bridge APIの直接テスト**

   ```javascript
   // Console で実行
   window.pywebview.api.select_audio_file()
   ```

### 📄 関連ドキュメント

- **[docs/development/20251017_pywebview_improvements.md](docs/development/20251017_pywebview_improvements.md)** - 本日の修正作業詳細レポート
- **[docs/development/20251016_mac_launch_error.md](docs/development/20251016_mac_launch_error.md)** - 前回の起動エラー修正

---

## ✅ Mac版 v1.1.1 - 一部修正完了（2025-10-17更新）

### 修正完了した内容

- **問題**: HTMLテンプレートの波括弧衝突により`Internal Server Error`が発生
- **修正**: `string.Template`を使用した安全なテンプレート処理に変更
- **検証**: 起動・UI表示は正常動作確認済み

### ⚠️ 未解決の問題

- ファイル選択機能が動作しない（pywebview制約）
- モデル管理ボタンが反応しない（pywebview制約）

### 配布状況

- ⏳ **重大な動作不良のため、v1.1.1は配布保留中**
- ⏳ pywebview問題の解決後に配布予定

### 詳細レポート

修正内容とテスト結果の詳細は以下を参照してください：

- **[docs/development/20251017_mac_smoke_test.md](docs/development/20251017_mac_smoke_test.md)** - 初期修正・検証レポート
- **[docs/development/20251018_mac_multi_issue_fix.md](docs/development/20251018_mac_multi_issue_fix.md)** - pywebview問題修正作業レポート（未完了）

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
├── release/                     # 🤖 ビルド環境（Mac/Windows）
│   ├── mac/                     # Mac版ビルド環境
│   │   ├── src/                 # ⚠️ 要同期管理（手編集注意）
│   │   ├── build.sh             # ビルドスクリプト
│   │   └── GaQ_Transcriber.spec
│   ├── windows/                 # Windows版ビルド環境
│   │   ├── src/                 # ⚠️ 要同期管理（手編集注意）
│   │   ├── build.bat            # ビルドスクリプト
│   │   └── GaQ_Transcriber.spec
│   └── README.md                # ⚠️ 手編集禁止の注意事項
├── scripts/                     # ビルド＆同期スクリプト
│   └── check_sync.sh            # ソース同期確認スクリプト
├── docs/                        # 📖 すべてのドキュメント
│   ├── PROJECT_OVERVIEW.md      # プロジェクト詳細概要
│   ├── HISTORY.md               # 開発履歴
│   ├── development/             # 開発記録・エラーログ
│   ├── releases/                # リリース履歴・レポート
│   ├── guides/                  # ビルドガイド・手順書
│   └── troubleshooting/         # トラブルシューティング
├── build_standard/              # ⚠️ 旧バージョン（現在未使用）
├── launcher_final/              # ⚠️ 不採用版（現在未使用）
└── README.md                    # このファイル
```

⚠️ **重要な注意事項**:
- `release/mac/src/` と `release/windows/src/` は**必ず同期を取ること**
- 編集後は `./scripts/check_sync.sh` で差分確認が必須
- 詳細は [release/README.md](release/README.md) を参照

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

## トラブルシューティング

### 🚨 アプリが起動しない場合

#### 症状
- DMGからインストール後、アプリをダブルクリックしても起動しない
- アプリアイコンがDockに一瞬表示されてすぐ消える

#### 確認手順

**1. ログファイルを確認**

```bash
cat ~/.gaq/logs/app.log
```

ログに以下のようなエラーが表示されていないか確認：
- `ImportError: cannot import name 'XXX'` → モジュール欠損
- `Permission denied` → 実行権限の問題
- `Address already in use` → ポート競合（既に起動中の可能性）

**2. 既存インスタンスの確認**

別のGaQ Transcriber が既に起動している可能性があります：

```bash
# プロセス確認
ps aux | grep GaQ_Transcriber

# 既存プロセスを終了
pkill -f "GaQ_Transcriber"
```

**3. 再インストール**

1. アプリを完全にアンインストール
   ```bash
   rm -rf "/Applications/GaQ Offline Transcriber.app"
   ```

2. DMGを再マウントしてインストール

**4. ターミナルから直接起動（詳細ログ確認）**

```bash
"/Applications/GaQ Offline Transcriber.app/Contents/MacOS/GaQ_Transcriber"
```

エラーメッセージが表示される場合は、その内容を確認してください。

---

### 🖱️ 画面が動作しない場合（UI無反応）

#### 症状
- アプリは起動するが、ボタンをクリックしても反応しない
- ドラッグ&ドロップが動作しない
- すべてのUI要素が無反応

#### 原因
JavaScriptの初期化エラーの可能性があります。

#### 確認手順

**1. JavaScriptログの確認**

```bash
tail -50 ~/.gaq/logs/app.log | grep "\[JS\]"
```

**期待される正常なログ**:
```
[JS] ✅ Console hook installed
[JS] ✅ カスタムダイアログAPI登録完了
[JS] ✅ グローバルエラーハンドラー登録完了
[JS] ===== GaQ JavaScript starting =====
[JS] ✅ initializeApp() 完了
```

**JavaScriptログが全く表示されない場合** → JavaScript初期化失敗

**2. エラーログの確認**

```bash
tail -50 ~/.gaq/logs/app.log | grep -i error
```

以下のようなエラーが表示される場合：
- `SyntaxError` → JavaScriptコード構文エラー
- `ReferenceError: XXX is not defined` → 未定義の関数/変数参照
- `🚨 [Global Error]` → JavaScript実行時エラー

**3. Safari検証（開発者向け）**

アプリを一度起動して、生成されたHTMLをSafariで開いて検証：

```bash
# アプリを起動（すぐ終了してOK）
open "/Applications/GaQ Offline Transcriber.app"

# Safariで検証
open -a Safari /tmp/gaq_debug.html
```

Safari の開発メニュー → JavaScriptコンソール でエラーを確認。

**4. テストモードでの検証（開発者向け）**

極小テストページで JavaScript 実行を検証：

```bash
cd /path/to/GaQ_app/release/mac
export GAQ_TEST_MODE=1
export GAQ_WEBVIEW_DEBUG=1
bash test_javascript.sh
```

Alert が表示される → JavaScript は動作可能
Alert が表示されない → JavaScript 実行環境の問題

#### 対処方法

**一時的な回避策**:
1. アプリを完全終了
2. `~/.gaq/logs/app.log` を削除
3. アプリを再起動

**それでも解決しない場合**:
- 開発ログ `docs/development/` で類似問題を検索
- GitHubのIssueで報告（ログファイルを添付）

---

### 📝 その他の問題

#### モデルのダウンロードが進まない
- インターネット接続を確認
- `~/.cache/huggingface/` の容量を確認（Large-v3は約3GB必要）

#### 文字起こし結果が不正確
- より高精度なモデル（Large-v3）を選択
- 音声ファイルの品質を確認（ノイズが多いと精度低下）

#### クリップボードコピーができない
- macOS のセキュリティ設定を確認
- システム環境設定 → セキュリティとプライバシー → アクセシビリティ

---

## 開発者向けトラブルシューティング

### JavaScript実行エラーの診断フロー

詳細なガイドは以下を参照：

- [JavaScript診断の完全ガイド](docs/development/20251019_smoke_test_and_sync_check.md#緊急対応-javascript完全停止問題の調査)
- [過去の事例：2025-10-19 JavaScript完全停止](docs/HISTORY.md#2025-10-19-javascript完全停止問題の解決緊急対応)
- [問題分析レポート](codex_report_20251019.md)

#### クイック診断手順

##### 1. Safari JavaScriptコンソールでエラー行を特定

```bash
# アプリを起動して /tmp/gaq_debug.html を生成
open "/Applications/GaQ Offline Transcriber.app"

# Safariで開く
open -a Safari /tmp/gaq_debug.html
```

Safari の「開発」メニュー → 「JavaScriptコンソールを表示」でエラーを確認

##### 2. エラー行の該当コードを確認

```bash
# エラー行番号が1397の場合
sed -n '1390,1405p' /tmp/gaq_debug.html
```

##### 3. Pythonソースで該当箇所を検索

```bash
cd release/mac/src
# エラー行付近のJavaScriptコードで検索
grep -n "該当するコード断片" main.py
```

##### 4. 典型的な問題パターン

| エラー | 原因 | 解決方法 |
|--------|------|----------|
| `SyntaxError: Unexpected EOF` | JavaScript文字列内の実際の改行 | Python側で `\\n` にエスケープ |
| `ReferenceError: XXX is not defined` | 関数定義の順序問題 | グローバルスコープで定義 |
| `SyntaxError: Unexpected token` | クォート、括弧の不一致 | Pythonテンプレート内の構文チェック |

##### 5. Python文字列エスケープの注意点

Pythonのトリプルクォート(`"""..."""`)内でJavaScriptを書く場合：

```python
# ❌ 間違い - \n が実際の改行になる
alert('テキスト\n改行');

# ✅ 正しい - \\n でJavaScriptの \n になる
alert('テキスト\\n改行');
```

##### 6. テストモードでの検証

```bash
cd release/mac
export GAQ_TEST_MODE=1
export GAQ_WEBVIEW_DEBUG=1
bash test_javascript.sh
```

Alert が表示される → JavaScript実行環境は正常
Alert が表示されない → JavaScript構文エラーまたは実行環境の問題

---

## 連絡先

- **Website**: https://tsuji-lab.net
- **開発元**: 公立はこだて未来大学 辻研究室
- **問題報告**: GitHub Issues

---

**最終更新**: 2025-10-19
**バージョン**: Mac v1.1.1 / Windows v1.1.0
**ステータス**: リリース済み
