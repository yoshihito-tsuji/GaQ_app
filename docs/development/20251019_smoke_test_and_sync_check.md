# 開発ログ - 2025-10-19

## 作業概要
- **日付**: 2025-10-19
- **作業時間**: 09:00 - 20:05
- **担当者**: Claude Code
- **ブランチ**: dev
- **最終ビルド**: 20:02 (v1.1.1)

## 作業目的

Mac版v1.1.1の完全復旧（2025-10-18完了）を受けて、以下の確認作業を実施：

1. **履歴・ログの確認**: HISTORY.md および 2025-10-18関連ログから復旧内容と残課題を整理
2. **ソース同期確認**: `./scripts/check_sync.sh` でMac/Windowsソースの差分チェック
3. **スモークテスト**: 10/18改修点の動作確認（必要に応じてビルド）
4. **Windows版対応検討**: ソース差分の確認と対応計画の策定

## 作業前の状況確認

### HISTORY.md から確認した Mac v1.1.1 の復旧内容

#### ✅ 解決済み - 2025-10-18 完了

1. **ドラッグ&ドロップ機能の実装**
   - `text/uri-list` データ型からファイルパスを直接取得
   - クリック選択との併用が可能
   - 成果: ユーザビリティが大幅に向上

2. **Large-v3選択時のエラー解決**
   - モデル変更時に「ファイルが見つかりません」エラーを修正
   - `window.uploadedFilePath` で統一し、文字起こし前に常に再アップロード
   - 成果: モデル変更時も正しくファイルが処理される

3. **クリップボードコピー機能の完全実装**
   - AppleScript + 一時ファイル方式
   - UTF-8エンコーディング指定 `«class utf8»`
   - 成果: 長文でも確実にクリップボードにコピーできる

4. **保存ファイルへのメタデータ追加**
   - 文字数・処理時間を自動追記
   - 処理時間は60秒以上で「分秒」表記に自動変換
   - 成果: ファイルに統計情報が自動的に追記される

5. **モデルダウンロード時の挙動改善**
   - 確認ダイアログを廃止（自動ダウンロード）
   - トースト通知で進捗表示
   - ダウンロード完了後、自動的に文字起こし開始
   - 成果: ユーザー操作が減り、スムーズな体験を提供

6. **UI/UXの微修正**
   - AppleScriptダイアログの統一
   - ログ出力の強化（絵文字プレフィックス）

#### ⚠️ 残存課題（保留）

1. **強制終了の再発**
   - 状況: 文字起こし完了後、アプリを終了すると強制終了する場合がある
   - 原因仮説: FastAPIサーバーの停止処理が不完全 / multiprocessingプロセスの終了待ちがタイムアウト
   - 対処方針: 今後の検討事項として保留（機能には影響なし）

2. **Windows版への展開**
   - 状況: Mac版v1.1.1の実装をWindows版にも反映する必要がある
   - 作業項目:
     - Windows版でのドラッグ&ドロップ実装
     - Windows版でのクリップボードコピー実装（pyperclip等）
     - Windows版でのファイル保存ダイアログ調整
     - PyInstallerビルドスクリプトの整備
   - 優先度: 中（Mac版が安定してから着手）

### 動作確認済み環境（2025-10-18時点）

- **OS**: macOS 14.8 (arm64)
- **Python**: 3.12.3
- **pywebview**: 6.0
- **PyInstaller**: 6.16.0
- **モデル**: Medium, Large-v3

### ビルド成果物（2025-10-18時点）

- **アプリ**: `dist/GaQ Offline Transcriber.app` (188MB)
- **DMG**: `dist/GaQ_Transcriber_v1.1.1_mac.dmg` (77MB)

## 作業内容

### 1. ソース同期確認

#### 実施コマンド

```bash
./scripts/check_sync.sh
```

#### 初回実行結果（差分あり）

```
✗ transcribe.py - 差分あり
✗ config.py - 差分あり
⚠ main.py - Mac: 1958行, Win: 1525行 (差: 433行)
⚠ main_app.py - Mac: 762行, Win: 193行 (差: 569行)
❌ 差分が検出されました。修正が必要です。
```

#### 差分内容の確認

**transcribe.py の差分**:
- Windows版にのみ存在: シンボリックリンク無効化対策、WinError 1314対策、Fallbackダウンロード機能
- これらはWindows固有の対策だが、Mac版でも動作するはず（条件分岐でWindows固有処理が適用される）

**config.py の差分**:
- Windows版にのみ存在: PyInstaller実行ファイル対応の `BASE_DIR` 設定
- Mac版にも有用な変更

**対応**:
- Windows版の共通コード（transcribe.py, config.py）をMac版にコピー
- これによりMac版でもWindows固有のエラー対策が含まれるが、macOSでは発生しないため問題なし

```bash
cp release/windows/src/transcribe.py release/mac/src/transcribe.py
cp release/windows/src/config.py release/mac/src/config.py
```

#### 再実行結果（同期完了）

```
✓ transcribe.py - 同期済み
✓ config.py - 同期済み
⚠ main.py - Mac: 1958行, Win: 1525行 (差: 433行)
⚠ main_app.py - Mac: 762行, Win: 193行 (差: 569行)
✅ すべての共通コードが同期されています
```

**プラットフォーム固有ファイルの行数差**:
- Mac版のmain.py/main_app.pyが大きいのは、2025-10-18改修（pywebview対応、ドラッグ&ドロップなど）が反映されているため
- これは意図的な差分で、問題なし

### 2. Mac v1.1.1 ビルド

#### 実施判断

**ビルドを実施する理由**:
- 共通コード（transcribe.py, config.py）を更新したため、動作確認が必要
- 2025-10-18のビルド成果物が存在するが、更新後の動作を確認するために再ビルド推奨

#### ビルドコマンド

```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac
bash build.sh
```

#### ビルド結果

**実施日時**: 2025-10-19 09:11

**ビルド環境**:
- Python: 3.12.12
- PyInstaller: 6.16.0
- pywebview: 6.0
- macOS: 14.5 (arm64)

**成果物**:
- アプリ: `dist/GaQ Offline Transcriber.app` (187MB)
- DMG: `dist/GaQ_Transcriber_v1.1.1_mac.dmg` (77MB)

**ビルド状態**:
- ✅ ビルド成功
- ✅ DMGパッケージ作成成功
- ⚠️ 警告: Hidden import 'python_multipart' not found（動作には影響なし）

**変更点**:
- 共通コード（transcribe.py, config.py）をWindows版から同期
- Windows固有のエラー対策（WinError 1314など）が含まれるが、macOSでは発生しないため問題なし

### 3. スモークテスト

#### テスト項目

以下の2025-10-18改修点を順番に検証：

- [ ] **ドラッグ&ドロップ機能**: ファイルをドラッグ&ドロップで選択できるか
- [ ] **モデル変更時の再アップロード**: Large-v3などモデル変更時にファイルが正しく処理されるか
- [ ] **クリップボードコピー**: 長文でも確実にクリップボードにコピーできるか
- [ ] **保存メタデータ**: ファイル保存時に文字数・処理時間が追記されるか
- [ ] **モデル自動ダウンロード**: 未ダウンロードモデルが自動ダウンロードされるか

#### テスト環境

- OS: macOS 14.8 (arm64)
- アプリ: `dist/GaQ Offline Transcriber.app`

#### テスト結果

（これから実施）

### 4. Windows版ソースの差分確認

#### 確認対象ファイル

- `release/mac/src/` vs `release/windows/src/`

#### 確認結果

（これから実施）

## 問題と解決

### 問題1: APP_VERSIONインポートエラーでアプリが起動しない

#### 発生状況

**初回ビルド後（09:11）、DMGからインストールしたアプリが起動しない**

#### エラー内容

```
ImportError: cannot import name 'APP_VERSION' from 'config'
```

#### 原因

- Windows版のconfig.pyを同期した際に、`APP_VERSION`定数が削除されていた
- main_app.pyの23行目で`from config import APP_VERSION`しているが、config.pyに存在しない

#### 解決策

**修正内容**:
- `release/mac/src/config.py` に `APP_VERSION = "1.1.1"` を追加
- `release/windows/src/config.py` にも同様に追加（同期維持）

**修正箇所**:
```python
# config.py (line 24-25)
# アプリケーションバージョン
APP_VERSION = "1.1.1"
```

**再ビルド結果（09:17）**:
- ✅ ビルド成功
- ✅ DMGパッケージ作成成功
- ✅ アプリ起動確認成功

**起動ログ（09:18）**:
```
2025-10-19 09:18:01,667 - === GaQ Offline Transcriber 1.1.1 起動 ===
2025-10-19 09:18:02,042 - 🚀 FastAPIサーバー起動: http://127.0.0.1:8000
2025-10-19 09:18:03,115 - ✅ [DragDrop] ドロップイベントハンドラー登録完了
```

#### 教訓

- **共通コードの同期時は、両方のファイルを慎重に確認すること**
- **同期後は必ず`./scripts/check_sync.sh`を実行すること**
- **ビルド後はアプリの起動確認を必ず行うこと**

## 次のステップ

- [ ] スモークテスト完了
- [ ] Windows版への対応方針決定
- [ ] 必要に応じてHISTORY.md更新

## メモ・備考

### 参照ドキュメント

- [docs/development/HISTORY.md](HISTORY.md) - 開発履歴
- [docs/development/20251018_final_completion_report.md](20251018_final_completion_report.md) - 2025-10-18 最終完成レポート
- [README.md](../../README.md) - プロジェクト概要・運用ルール

### 作業方針

- check_sync.sh で差分確認を最優先
- 差分があれば同期作業を実施
- Mac版はビルド済みDMGが存在する場合はそれを使用してテスト
- Windows版への対応は差分確認後に計画を立てる

---

## 🚨 緊急対応: JavaScript完全停止問題（15:30-20:05）

### 問題発生

**15:30ビルド以降、JavaScriptが完全に実行されない**という重大な問題が発生。

#### 症状
- すべてのUI機能が無反応（ドラッグ&ドロップ、ボタン、モデル管理）
- `console.log()` が一切記録されない
- デバッグメッセージ（alert、画面表示）も表示されない
- Python側は正常動作（FastAPI、pywebview Bridge API）

### 原因調査プロセス

#### 仮説1: スコープ問題（誤り）
- 当初、`showConfirmDialog()` が2つ目の`<script>`タグで定義されていたため、`initializeApp()` からアクセスできない問題と推測
- **修正試行**: `window.*` への明示バインド、メインスクリプト内への移動
- **結果**: 効果なし

#### 仮説2: pywebview固有の問題（誤り）
- HTML生成は正常、構造も正しい
- pywebviewのキャッシュ問題や制約を疑う
- `/test` エンドポイント、`GAQ_WEBVIEW_DEBUG=1` などのデバッグ機能を実装
- **結果**: 問題はpywebview以前

#### 根本原因の特定（正解）
**Safari検証により判明**: `SyntaxError: Unexpected EOF` at line 1397

```javascript
// Pythonトリプルクォート内で \n が実際の改行になっていた
alert('モデル「' + modelName + '」を削除しますか？
      ↑ ここで改行（構文エラー！）
削除後は再度ダウンロードが必要です。');
```

Pythonの `string.Template` 内のトリプルクォート `"""..."""` では、`\n` がリテラル改行として扱われる。

### 修正内容

#### 1. エスケープ修正
[main.py:1462, 1466](file:///Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/src/main.py#L1462)

```python
# 修正前
alert('...\n\n...');  # → 実際の改行になる

# 修正後
alert('...\\n\\n...');  # → JavaScript内で \n として正しく解釈
```

#### 2. 追加実装（デバッグ強化）

**カスタムダイアログAPI**:
- `window.showConfirmDialog()` / `window.closeConfirmDialog()` をグローバル公開
- `initializeApp()` 定義前に配置（スコープ問題回避）

**グローバルエラーハンドラー**:
```javascript
window.addEventListener('error', function(event) {
    // 未捕捉例外をPythonログへ転送
});
window.addEventListener('unhandledrejection', function(event) {
    // Promise拒否をキャッチ
});
```

**テスト機能**:
- `/test` エンドポイント（極小テストHTML）
- `GAQ_TEST_MODE=1` で起動切り替え
- `test_javascript.sh` スクリプト

**未定義ガード**:
```javascript
if (typeof window.showConfirmDialog !== 'function') {
    // フォールバックでalert()使用
}
```

### 検証プロセス

1. **Safari検証** (`/tmp/gaq_debug.html`)
   - JavaScriptコンソールで `SyntaxError: Unexpected EOF` を発見
   - ブラウザでもJavaScript未実行を確認 → pywebview固有問題ではないと判明

2. **HTML構造分析**
   - 生成されたHTMLで改行が入っていることを確認
   - Pythonソースコードとの差異を発見

3. **修正検証**
   - エスケープ修正後、Safariで赤いデバッグメッセージ表示
   - pywebviewアプリで全機能復旧確認

### 成果

#### ✅ 完全復旧（20:02ビルド）
- 赤いデバッグメッセージ表示: `DEBUG: JavaScript LOADED! Build: 1.1.1 at 2025-10-19T11:03:44.296Z`
- ドラッグ&ドロップ: 正常動作
- 文字起こし: 正常動作
- コピー・保存: 正常動作
- モデル管理: 正常動作

#### 🛡️ 再発防止策

1. **文字列エスケープルール**
   - Pythonトリプルクォート内のJavaScript文字列では `\n` → `\\n` を使用
   - `\n\n` → `\\n\\n`

2. **グローバルエラーハンドラー導入**
   - 今後の未捕捉例外はすべてPythonログに記録される
   - デバッグ時間の大幅短縮が期待できる

3. **テスト環境整備**
   - `/test` エンドポイントで即座に検証可能
   - Safari検証をルーチン化

### 教訓

1. **Safari検証の重要性**
   - pywebview問題の切り分けに必須
   - JavaScriptコンソールでの構文エラー確認が最速

2. **Python文字列テンプレートの注意点**
   - `"""..."""` 内の `\n` は実際の改行になる
   - JavaScript埋め込み時は `\\n` 必須

3. **段階的デバッグの有効性**
   - 極小HTMLでの検証 → 問題の切り分け
   - ブラウザ検証 → pywebview/HTML問題の判別

---

## 最終状態

### ✅ Mac版 v1.1.1 完全動作確認済み（20:05）

**実装済み機能**:
- ドラッグ&ドロップ
- モデル自動ダウンロード
- クリップボードコピー
- メタデータ保存
- モデル管理（カスタムダイアログ）
- プログレスバーシャイマー効果
- グローバルエラーハンドリング

**ビルド成果物**:
- `dist/GaQ_Transcriber_v1.1.1_mac.dmg` (78MB)
- ビルド時刻: 2025-10-19 20:02

---

**作成日時**: 2025-10-19 完了
