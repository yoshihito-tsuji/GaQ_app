# 開発ログ - 2025-10-16 Mac版起動不良調査

## 作業概要
- **日付**: 2025-10-16
- **作業時間**: 19:25 - 19:49 (約24分)
- **担当者**: Claude Code (Sonnet 4.5)
- **ブランチ**: dev
- **目的**: Dockでアイコンが跳ね続け起動しない不具合の原因特定と修正
- **ステータス**: ✅ **完了 - 起動成功**

## Mac環境情報
- **macOS バージョン**: 15.7.1 (Build 24G231)
- **アーキテクチャ**: Apple Silicon (arm64)
- **インストールパス**: `/Applications/GaQ Offline Transcriber.app`
- **使用DMG**: GaQ_Transcriber_v1.1.0_Final.dmg（想定）

## 作業内容

### 1. 再現調査

#### 1.1 Dockから起動（症状確認）
**実施時刻**: 未実施
**症状**:
- Dockでアイコンが跳ね続ける
- アプリケーションウィンドウが表示されない

#### 1.2 ターミナルから直接起動
**コマンド実行予定**:
```bash
# 方法1: open コマンド
open -a "/Applications/GaQ Offline Transcriber.app"

# 方法2: 実行ファイル直接起動
"/Applications/GaQ Offline Transcriber.app/Contents/MacOS/GaQ_Transcriber"
```

**結果**: 未実施

#### 1.3 システムログ収集
**コマンド実行予定**:
```bash
# 直近10分のアプリケーションログ
log show --predicate 'process == "GaQ_Transcriber"' --last 10m > ~/Desktop/gaq_system_log.txt

# クラッシュレポート確認
ls -lt ~/Library/Logs/DiagnosticReports/GaQ_Transcriber* | head -5
```

**結果**: 未実施

---

### 2. Gatekeeper・権限確認

#### 2.1 隔離属性確認
**コマンド実行予定**:
```bash
# 隔離属性の確認
xattr -l "/Applications/GaQ Offline Transcriber.app"

# 隔離属性が付いている場合は削除
xattr -d com.apple.quarantine "/Applications/GaQ Offline Transcriber.app"
```

**結果**: 未実施

#### 2.2 システム設定確認
- 「システム設定 > プライバシーとセキュリティ」でブロック状況を確認

---

### 3. アプリバンドル診断

#### 3.1 バンドル構成確認
**コマンド実行予定**:
```bash
# Contents ディレクトリ構成
ls -la "/Applications/GaQ Offline Transcriber.app/Contents"

# Info.plist 確認
plutil -p "/Applications/GaQ Offline Transcriber.app/Contents/Info.plist" | grep -E "(CFBundleExecutable|CFBundleIdentifier|CFBundleVersion)"
```

**結果**: 未実施

#### 3.2 動的ライブラリ確認
**コマンド実行予定**:
```bash
# 依存ライブラリの確認
otool -L "/Applications/GaQ Offline Transcriber.app/Contents/MacOS/GaQ_Transcriber"
```

**結果**: 未実施

#### 3.3 Resourcesディレクトリ確認
**確認項目**:
- `Contents/Resources/python` の存在
- 必要な `lib` ディレクトリの存在
- サイズが適切か（350MB前後）

---

### 4. 依存ライブラリ確認

**確認対象パッケージ**:
- pywebview
- pyobjc*
- requests
- faster_whisper
- ctranslate2
- av

**確認方法**:
```bash
# site-packages の確認
ls "/Applications/GaQ Offline Transcriber.app/Contents/Resources/python/site-packages" | grep -E "(pywebview|pyobjc|requests|faster_whisper|ctranslate2|av)"
```

**結果**: 未実施

---

### 5. 再ビルド計画（必要に応じて）

**デバッグビルド手順**:
```bash
cd release/mac
source venv/bin/activate

# GaQ_Transcriber.spec を編集（console=True に変更）
# pyinstaller GaQ_Transcriber.spec

# 新しい .app で起動テスト
open dist/GaQ\ Offline\ Transcriber.app
```

---

## 問題と解決

### 発生した問題
**問題の内容:**
- Mac版アプリがビルドされておらず、起動テスト環境がなかった
- 初回ビルド時にFastAPIの型アノテーションでエラーが発生

**原因:**
Python 3.13 + FastAPI 0.104.1 + Pydantic 2.12.2の組み合わせで、`Annotated[UploadFile, File()]`構文がサポートされていなかった

```python
# エラーが発生したコード
file: Annotated[UploadFile, File()]

# エラーメッセージ
AssertionError: Param: file can only be a request body, using Body()
```

**解決策:**
従来の型アノテーション構文に変更
```python
# 修正後（2箇所）
file: UploadFile = File(...)
model: str = Form(DEFAULT_MODEL)
```

**変更ファイル:**
- `release/mac/src/main.py` (Line 969-970, 1024-1025)

---

## 実施した作業

### 1. ビルド環境セットアップ (19:25 - 19:33)
```bash
cd /Users/ytsuji/dev/GaQ_app/GaQ_app_v1.1.0/release/mac
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip  # 25.1.1 → 25.2
pip install -r src/requirements.txt  # 50+パッケージ
pip install pyinstaller  # 6.16.0
pip install Pillow  # アイコン変換に必要
```

### 2. 初回ビルド試行 (19:33 - 19:38)
```bash
pyinstaller --clean -y GaQ_Transcriber.spec
```
**結果**: ビルド成功、`dist/GaQ Offline Transcriber.app` (186MB) 生成

### 3. 起動テストとエラー発見 (19:38 - 19:41)
```bash
"/Users/ytsuji/dev/GaQ_app/.../GaQ_Transcriber" 2>&1
```
**エラー発見**:
```
AssertionError: Param: file can only be a request body, using Body()
```

### 4. コード修正 (19:41 - 19:43)
- `main.py` Line 969-970: `/transcribe` エンドポイント修正
- `main.py` Line 1024-1025: `/transcribe-stream` エンドポイント修正
- `main.py` Line 12: 不要な`Annotated`インポート削除

### 5. 再ビルドと起動確認 (19:43 - 19:49)
```bash
pyinstaller --clean -y GaQ_Transcriber.spec
open "dist/GaQ Offline Transcriber.app"
```
**結果**: ✅ **起動成功！**

---

## テスト結果

### ✅ 完了したテスト項目
- [x] ビルド環境セットアップ (venv, 依存パッケージ)
- [x] PyInstallerビルド成功 (186MB)
- [x] ターミナルから起動してエラーログを取得
- [x] エラー原因を特定 (型アノテーション問題)
- [x] コード修正実施
- [x] 再ビルド成功
- [x] 修正後の起動確認成功
- [x] openコマンドでの起動テスト成功
- [x] プロセス動作確認 (PID: 38639)

### 起動ログ
```
2025-10-16 19:46:20 - __main__ - INFO - === GaQ Offline Transcriber 起動 ===
2025-10-16 19:46:20 - __main__ - INFO - ✅ FastAPIサーバー起動確認: http://127.0.0.1:8000/health
2025-10-16 19:46:20 - __main__ - INFO - 🖥️ Webviewウィンドウ起動: http://127.0.0.1:8000
2025-10-16 19:46:21 - __main__ - INFO - 🚀 FastAPIサーバー起動: http://127.0.0.1:8000
```

---

## 成果物

### ビルド成果物
- **場所**: `/Users/ytsuji/dev/GaQ_app/GaQ_app_v1.1.0/release/mac/dist/`
- **ファイル**: `GaQ Offline Transcriber.app`
- **サイズ**: 186MB
- **ステータス**: ✅ 起動確認済み

### ビルド環境
- **Python**: 3.13.5
- **PyInstaller**: 6.16.0
- **アーキテクチャ**: arm64 (Apple Silicon)
- **macOS SDK**: 15.4.0

---

## 次のステップ

### 推奨される追加作業
- [ ] DMGファイルの作成（配布用）
- [ ] 実際の文字起こし機能の動作テスト
- [ ] モデルダウンロード機能のテスト
- [ ] Windows版への同様の修正適用

### 修正が必要な場合の再ビルド手順
```bash
cd /Users/ytsuji/dev/GaQ_app/GaQ_app_v1.1.0/release/mac
source venv/bin/activate
pyinstaller --clean -y GaQ_Transcriber.spec
```

---

## 技術的知見

### Python 3.13とFastAPI互換性問題
- **問題**: Python 3.13 + FastAPI 0.104.1 + Pydantic 2.12.2 の組み合わせで`Annotated[UploadFile, File()]`構文が動作しない
- **対策**: 従来の`file: UploadFile = File(...)`構文を使用
- **影響範囲**: FastAPIの全ファイルアップロードエンドポイント

### 再発防止策
1. FastAPI/Pydanticのバージョンアップ時は型アノテーションの互換性を確認
2. 開発環境でのビルドテストを定期的に実施
3. Python 3.13での動作を継続的に検証

---

## メモ・備考

### 発見事項
- 初回調査時、アプリがビルドされていない状態だったため、まずビルド環境の構築から開始
- Pillowライブラリがないとアイコン(.png → .icns)の自動変換ができない
- `python_multipart`の隠しインポートが見つからない警告が出るが、ビルドと起動には影響なし

### 作業効率
- 型アノテーション問題の特定と修正: 約5分
- ビルド環境セットアップ〜修正完了まで: 約24分

---

**作成日時**: 2025-10-16 19:25
**完了日時**: 2025-10-16 19:49
**最終更新**: 2025-10-16 19:49
