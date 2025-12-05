# GaQ Offline Transcriber - ビルドガイド

## ⚠️ 重要: Python バージョン要件

**このプロジェクトは Python 3.12.x でのビルドが必須です。**

- **必須バージョン**: Python 3.12.7 以降の 3.12.x
- **非推奨**: Python 3.13.x（FastAPI/Pydantic互換性問題のため）
- **理由**: Python 3.13では型アノテーション互換性の問題が発生します

### Python 3.12のインストール

#### macOS
```bash
# Homebrewでインストール
brew install python@3.12

# インストール確認
/opt/homebrew/bin/python3.12 --version
```

#### Windows
Python 3.12.x を以下からダウンロードしてインストール:
- https://www.python.org/downloads/release/python-3127/

---

## 🔐 コード署名・公証（macOS）

### 前提条件

1. **Apple Developer Program**に登録（年間$99）
2. **Developer ID Application証明書**をKeychainにインストール
3. **App固有パスワード**を作成（公証用）

### 証明書の準備

```bash
# 利用可能な証明書を確認
security find-identity -v -p codesigning

# 出力例:
# 1) XXXXX "Developer ID Application: Your Name (TEAM_ID)"
```

### 公証用認証情報の保存（推奨）

Keychainに認証情報を保存することで、毎回パスワードを入力する必要がなくなります：

```bash
xcrun notarytool store-credentials "notarytool" \
  --apple-id "your@email.com" \
  --team-id "YOUR_TEAM_ID" \
  --password "app-specific-password"
```

### ビルドオプション

```bash
cd release/mac

# 通常ビルド（署名なし、開発用）
./build.sh

# 署名付きビルド（Developer ID署名）
./build.sh --sign

# 署名＋公証（本番リリース用）
./build.sh --notarize

# DMGをスキップ（.appのみ生成）
./build.sh --sign --skip-dmg
```

### 環境変数による設定

```bash
# 証明書を明示的に指定する場合
export DEVELOPER_ID="Developer ID Application: Your Name (TEAM_ID)"

# 環境変数で公証認証情報を設定する場合（Keychain推奨）
export APPLE_ID="your@email.com"
export APPLE_PASSWORD="app-specific-password"
export TEAM_ID="YOUR_TEAM_ID"
```

### 署名・公証の検証

```bash
# 署名の検証
codesign --verify --deep --strict --verbose=2 "dist/GaQ Offline Transcriber.app"

# 公証チケットの確認
xcrun stapler validate "dist/GaQ Offline Transcriber.app"

# Gatekeeperでの検証
spctl --assess --verbose=4 --type execute "dist/GaQ Offline Transcriber.app"
```

---

## 📦 パッケージング手順

### 🍎 Mac版ビルド（Mac環境で実行）

#### 推奨: ビルドスクリプトを使用

```bash
# プロジェクトディレクトリに移動
cd release/mac

# ビルドスクリプトを実行（自動的にPython 3.12を使用）
./build.sh
```

ビルドスクリプトは以下を自動的に実行します：
- Python 3.12のバージョン確認
- 仮想環境の作成（必要に応じて）
- 依存パッケージのインストール
- PyInstallerでのビルド

#### 手動ビルド

```bash
# プロジェクトディレクトリに移動
cd release/mac

# Python 3.12で仮想環境を作成
/opt/homebrew/bin/python3.12 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# Pythonバージョン確認（3.12.xであることを確認）
python --version

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r src/requirements.txt
pip install pyinstaller
pip install Pillow
```

#### 2. ビルド実行
```bash
# PyInstallerでビルド
pyinstaller GaQ_Transcriber.spec

# ビルド成功後、以下のファイルが生成されます
# dist/GaQ Offline Transcriber.app
```

#### 3. 動作確認
```bash
# アプリを起動
open "dist/GaQ Offline Transcriber.app"

# または、ターミナルから直接実行
./dist/GaQ\ Offline\ Transcriber.app/Contents/MacOS/GaQ_Transcriber
```

#### 4. 配布準備
```bash
# .appファイルをDMGイメージにパッケージング（オプション）
hdiutil create -volname "GaQ Offline Transcriber" \
  -srcfolder "dist/GaQ Offline Transcriber.app" \
  -ov -format UDZO \
  GaQ_Transcriber_v1.1.0_mac.dmg
```

---

### 🪟 Windows版ビルド（Windows環境で実行）

#### 推奨: ビルドスクリプトを使用

```powershell
# プロジェクトディレクトリに移動
cd release\windows

# ビルドスクリプトを実行（自動的にPython 3.12を使用）
.\build.bat
```

ビルドスクリプトは以下を自動的に実行します：
- Python 3.12のバージョン確認
- 仮想環境の作成（必要に応じて）
- 依存パッケージのインストール
- PyInstallerでのビルド

#### 手動ビルド

```powershell
# プロジェクトディレクトリに移動
cd release\windows

# Pythonバージョン確認（3.12.xであることを確認）
python --version

# 3.12.x でない場合は、Python 3.12をインストール後、フルパスを指定
# C:\Python312\python.exe -m venv venv

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
venv\Scripts\activate

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r src\requirements.txt
pip install pyinstaller
```

#### 2. ビルド実行
```powershell
# PyInstallerでビルド
pyinstaller GaQ_Transcriber.spec

# ビルド成功後、以下のフォルダが生成されます
# dist\GaQ_Transcriber\
```

#### 3. 動作確認
```powershell
# 実行ファイルを起動
.\dist\GaQ_Transcriber\GaQ_Transcriber.exe
```

#### 4. 配布準備
```powershell
# distフォルダをZIPに圧縮（PowerShell）
Compress-Archive -Path .\dist\GaQ_Transcriber `
  -DestinationPath GaQ_Transcriber_v1.1.0_windows_x64.zip

# または、7-Zipを使用
7z a -tzip GaQ_Transcriber_v1.1.0_windows_x64.zip .\dist\GaQ_Transcriber\
```

---

## 🔧 トラブルシューティング

### Mac版

#### エラー: `ModuleNotFoundError: No module named 'xxx'`
```bash
# 隠しインポートに追加
# GaQ_Transcriber.spec の hiddenimports リストに追加
hiddenimports = [
    'uvicorn.logging',
    # ... 既存のインポート
    'xxx',  # 不足しているモジュールを追加
]
```

#### エラー: `.app` が起動しない
```bash
# ターミナルから起動してログを確認
./dist/GaQ\ Offline\ Transcriber.app/Contents/MacOS/GaQ_Transcriber

# または、consoleモードでビルド
# GaQ_Transcriber.spec の console=False を True に変更
```

#### アイコンが表示されない
```bash
# icon.pngをico形式に変換（オプション）
# macOSは.pngでも動作しますが、.icnsが推奨
# https://iconverticons.com/online/ で変換
```

### Windows版

#### エラー: `ModuleNotFoundError: No module named 'xxx'`
```powershell
# Mac版と同様に hiddenimports に追加
```

#### エラー: `Failed to execute script`
```powershell
# consoleモードでビルドしてエラー詳細を確認
# GaQ_Transcriber.spec の console=False を True に変更
```

#### Windows Defenderが実行をブロック
```powershell
# 開発者署名を追加（オプション）
# または、ユーザーに「詳細情報」→「実行」を指示

# ビルド後、VirusTotalでスキャンして安全性を確認
# https://www.virustotal.com/
```

---

## 📊 ビルドサイズ最適化

### サイズ削減オプション

#### 1. UPX圧縮（Mac/Windows共通）
```bash
# UPXをインストール
# Mac
brew install upx

# Windows
# https://upx.github.io/ からダウンロード

# .specファイルでupx=Trueを設定（デフォルトで有効）
```

#### 2. 不要なファイルを除外
```python
# GaQ_Transcriber.spec に追加
excludes = [
    'tkinter',      # Tkinterは使用しない
    'matplotlib',   # matplotlibは使用しない
    'IPython',      # IPythonは使用しない
]
```

#### 3. ワンファイルビルド（オプション）
```python
# GaQ_Transcriber.spec を修正
# exe = EXE(...) の中に以下を追加
onefile=True,  # 単一実行ファイルにまとめる
```

注意: ワンファイルビルドは起動が遅くなる可能性があります。

---

## ✅ ビルド後のチェックリスト

### Mac版
- [ ] .appファイルが生成されている
- [ ] アイコンが表示される
- [ ] ダブルクリックで起動する
- [ ] FastAPIサーバーが起動する
- [ ] Webviewウィンドウが表示される
- [ ] 文字起こし機能が動作する
- [ ] モデル管理機能が動作する

### Windows版
- [ ] .exeファイルが生成されている
- [ ] アイコンが表示される
- [ ] ダブルクリックで起動する
- [ ] FastAPIサーバーが起動する
- [ ] Webviewウィンドウが表示される
- [ ] 文字起こし機能が動作する
- [ ] モデル管理機能が動作する

---

## 📝 リリースノート作成

### バージョン表記
- **メジャーバージョン**: 大きな機能追加や破壊的変更
- **マイナーバージョン**: 新機能追加
- **パッチバージョン**: バグ修正

例: v1.1.0 = メジャー.マイナー.パッチ

### リリース成果物

1. **Mac版**: `GaQ_Transcriber_v1.1.1_mac.dmg`（署名・公証済み推奨）
2. **Windows版**: `GaQ_Transcriber_Windows_v1.1.1_Portable.zip`
3. **ソースコード**: `GaQ_Transcriber_v1.1.1_source.zip`

---

## 🔗 参考リンク

- [PyInstaller公式ドキュメント](https://pyinstaller.org/)
- [pywebview公式ドキュメント](https://pywebview.flowrl.com/)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [Apple Developer - Notarizing](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Microsoft Docs - MSIX](https://docs.microsoft.com/ja-jp/windows/msix/)

---

**最終更新**: 2025-12-05
**担当**: 公立はこだて未来大学 辻研究室
