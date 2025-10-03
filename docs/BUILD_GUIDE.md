# GaQ Offline Transcriber - ビルドガイド

## 📦 パッケージング手順

### 🍎 Mac版ビルド（Mac環境で実行）

#### 1. 事前準備
```bash
# プロジェクトディレクトリに移動
cd /Users/yoshihitotsuji/Claude_Code/GaQ_Transcriber_v1.1.0_Release/release/mac

# 仮想環境がない場合は作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r src/requirements.txt
pip install pyinstaller
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

#### 1. 事前準備
```powershell
# プロジェクトディレクトリに移動（Parallels共有フォルダ経由）
cd Z:\Users\yoshihitotsuji\Claude_Code\GaQ_Transcriber_v1.1.0_Release\release\windows

# または、ローカルにコピーした場合
cd C:\GaQ_Transcriber_v1.1.0_Release\release\windows

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
1. **Mac版**: `GaQ_Transcriber_v1.1.0_mac.dmg`
2. **Windows版**: `GaQ_Transcriber_v1.1.0_windows_x64.zip`
3. **ソースコード**: `GaQ_Transcriber_v1.1.0_source.zip`

---

## 🔗 参考リンク

- [PyInstaller公式ドキュメント](https://pyinstaller.org/)
- [pywebview公式ドキュメント](https://pywebview.flowrl.com/)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)

---

**最終更新**: 2025-10-02
**担当**: 公立はこだて未来大学 辻研究室
