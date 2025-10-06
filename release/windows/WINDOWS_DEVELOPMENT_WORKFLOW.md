# GaQ App v1.1.0 Windows版 - 開発作業手順書

## 1. プロジェクト概要

- **プロジェクト名**: GaQ App v1.1.0 Windows版
- **現在の状況**: 90%完成、微調整のみ必要
- **推定残作業時間**: 半日
- **コード品質**: 高品質、クロスプラットフォーム設計済み
- **主要技術**: FastAPI, pywebview, faster-whisper, PyInstaller

---

## 2. 環境セットアップ手順

### Python仮想環境の作成

```bash
# release/windowsディレクトリに移動
cd release/windows

# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
venv\Scripts\activate

# 依存パッケージのインストール
pip install --upgrade pip
pip install -r src/requirements.txt
```

### 必要な環境

- **Python**: 3.10以上推奨
- **OS**: Windows 10/11 (64bit)
- **メモリ**: 8GB以上推奨
- **ストレージ**: 空き容量5GB以上（Whisperモデル用）

---

## 3. 必須修正項目（優先度順）

### 修正1: アイコンファイルの作成

**ファイル**: `src/icon.ico`

**内容**:
- 既存の`src/static/icon.png`をICO形式に変換
- サイズ: 256x256, 128x128, 64x64, 32x32, 16x16 のマルチアイコン推奨

**推奨ツール**:
- オンライン: https://convertio.co/ja/png-ico/
- Python: pip install pillow して変換スクリプト実行

**変換スクリプト例**:

```python
# convert_icon.py
from PIL import Image

# PNGファイルを読み込み
img = Image.open('src/static/icon.png')

# ICO形式で保存（複数サイズ）
img.save('src/icon.ico', format='ICO', sizes=[
    (256, 256),
    (128, 128),
    (64, 64),
    (32, 32),
    (16, 16)
])

print("✅ icon.ico が作成されました")
```

**実行方法**:

```bash
# Pillowのインストール
pip install pillow

# スクリプトを実行
python convert_icon.py
```

---

### 修正2: requirements.txtの更新

**ファイル**: `src/requirements.txt`

**追加する行**:

```txt
# Windows用pywebviewバックエンド
pywebview[cef]>=4.0.0
```

**または** Windows 11以降の場合:

```txt
pywebview[edgehtml2]>=4.0.0
```

**推奨**: CEF（Chromium Embedded Framework）版が最も安定

**更新後のrequirements.txt全体**:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
faster-whisper>=1.0.0
aiofiles==23.2.1
pywebview[cef]>=4.0.0
requests>=2.25.0
```

---

### 修正3: .specファイルの修正

**ファイル**: `GaQ_Transcriber.spec`

**修正箇所**: line 72

```python
# 修正前
icon=str(src_dir / 'icon.png')

# 修正後
icon=str(src_dir / 'icon.ico')
```

**オプション: hiddenimportsの追加（pywebview関連）**

line 19-34のhiddenimportsセクションに以下を追加:

```python
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'faster_whisper',
    'ctranslate2',
    'av',
    'webview',  # 追加
    'webview.platforms.winforms',  # 追加
]
```

---

## 4. 動作テスト手順

### ステップ1: 開発モードでの動作確認

```bash
cd src
python main_app.py
```

**期待される動作**:
- ✅ ウィンドウが起動する
- ✅ 音声ファイルをドラッグ&ドロップできる
- ✅ 文字起こしが実行できる
- ✅ 結果がコピーできる
- ✅ 結果がダウンロードできる（txt形式）

### ステップ2: エラーログの確認

以下をチェック:
- ❌ コンソール出力にERRORがないか
- ✅ ファイル保存が正常に動作するか
- ✅ Whisperモデルのダウンロードが成功するか
- ✅ プログレスバーが正しく表示されるか

### ステップ3: テストファイルの準備

以下の音声ファイルでテスト:
- MP3ファイル（3-5分程度）
- M4Aファイル
- WAVファイル

---

## 5. PyInstallerビルド手順

### ステップ1: PyInstallerのインストール

```bash
pip install pyinstaller
```

### ステップ2: ビルド実行

```bash
# release/windowsディレクトリで実行
cd release/windows

# ビルド開始（5-10分かかります）
pyinstaller GaQ_Transcriber.spec
```

### ステップ3: ビルド結果の確認

```bash
# 実行ファイルの場所
dir dist\GaQ_Transcriber\GaQ_Transcriber.exe

# ファイルサイズ確認（目安: 500MB-1GB）
# 注意: Whisperモデルは含まれていません（初回実行時にダウンロード）
```

### ステップ4: 動作テスト

```bash
# dist/GaQ_Transcriberディレクトリに移動
cd dist\GaQ_Transcriber

# 実行
GaQ_Transcriber.exe
```

**期待される動作**:
- ✅ コンソールウィンドウが表示されない（`console=False`設定）
- ✅ アプリケーションウィンドウが起動
- ✅ アイコンが正しく表示される
- ✅ すべての機能が動作する

---

## 6. トラブルシューティング

### 問題1: pywebviewが起動しない

**エラーメッセージ**:
```
ImportError: No module named 'webview.platforms.winforms'
```

**原因**: Windows用バックエンドが不足

**解決策**:

```bash
pip install pythonnet  # または
pip install pywebview[cef]
```

---

### 問題2: アイコンが表示されない

**症状**: exeファイルのアイコンがデフォルトのまま

**原因**:
- .icoファイルが存在しない
- .specファイルのパスが間違っている

**解決策**:

```bash
# icon.icoファイルの存在を確認
ls src/icon.ico

# .specファイルのパスを確認
# line 72: icon=str(src_dir / 'icon.ico')
```

---

### 問題3: faster-whisperのモデルダウンロードエラー

**エラーメッセージ**:
```
HTTPError: 404 Client Error
```

**原因**: ネットワークまたはキャッシュの問題

**解決策**:

```bash
# キャッシュをクリア（Windows PowerShell）
Remove-Item -Recurse -Force $env:USERPROFILE\.cache\huggingface\hub

# キャッシュをクリア（Windows CMD）
rmdir /s /q %USERPROFILE%\.cache\huggingface\hub

# アプリを再起動してモデルを再ダウンロード
```

---

### 問題4: PyInstallerビルドエラー

**エラーメッセージ**:
```
ModuleNotFoundError: No module named 'xxx'
```

**原因**: hiddenimportsの不足

**解決策**:

1. .specファイルのhiddenimportsセクションに不足モジュールを追加
2. 再ビルド

```python
hiddenimports = [
    # 既存のインポート
    'uvicorn.logging',
    # ...
    # 追加
    'xxx',  # エラーで表示されたモジュール名
]
```

---

### 問題5: Windows Defenderに検疫される

**症状**: exeファイルが実行できない、削除される

**原因**: PyInstallerでビルドしたexeが誤検知される

**解決策**:

1. Windows Defender の除外設定に追加
2. ビルドオプションでコード署名を検討

```
設定 > 更新とセキュリティ > Windowsセキュリティ > ウイルスと脅威の防止
> 設定の管理 > 除外 > 除外の追加
```

---

## 7. 完成チェックリスト

### 修正フェーズ

- [ ] icon.icoファイルを作成
- [ ] requirements.txtを更新
- [ ] GaQ_Transcriber.specを修正
- [ ] 変更をGitコミット

```bash
git add .
git commit -m "fix: Windows版の必須修正を完了（icon.ico, requirements.txt, .spec）"
```

---

### テストフェーズ

- [ ] 開発モードで動作確認（`python main_app.py`）
- [ ] 音声ファイルアップロードのテスト（MP3, M4A, WAV）
- [ ] 文字起こし処理のテスト（Medium, Large-v3モデル）
- [ ] 結果コピー機能のテスト
- [ ] 結果ダウンロード機能のテスト（txt形式）
- [ ] エラーログの確認（コンソールにERRORがないか）
- [ ] モデル管理機能のテスト（削除、再ダウンロード）

---

### ビルドフェーズ

- [ ] PyInstallerでビルド実行（`pyinstaller GaQ_Transcriber.spec`）
- [ ] dist/GaQ_Transcriber.exeの動作確認
- [ ] アイコンが正しく表示されるか確認
- [ ] ファイルサイズの確認（目安: 500MB前後、モデル除く）
- [ ] 別のWindows PCでの動作確認（可能であれば）

---

### リリース準備

- [ ] README.mdの更新（Windows版の説明を追加）
- [ ] CHANGELOG.mdの作成
- [ ] 動作環境ドキュメントの作成
- [ ] GitHubリリースページの準備
- [ ] リリースノートの作成

---

## 8. 次回セッションでの作業開始方法

```bash
# 1. プロジェクトディレクトリに移動
cd C:\Users\tsuji\Claude_Code\GaQ_app

# 2. Cursorで開く（または任意のエディタ）
cursor .

# 3. このファイルを開く
# release/windows/WINDOWS_DEVELOPMENT_WORKFLOW.md

# 4. 仮想環境を有効化
cd release\windows
venv\Scripts\activate

# 5. 「修正1」から順番に作業開始
```

**推奨**: このファイルをブックマークして、いつでも参照できるようにする

---

## 9. 推定タイムライン

### 明日 Day 1（2-3時間）

1. **修正1-3の実装**（30分）
   - icon.ico作成
   - requirements.txt更新
   - .spec修正

2. **開発モードでの動作テスト**（1-2時間）
   - 初回Whisperモデルダウンロード（30分-1時間）
   - 機能テスト（30分）

3. **問題があれば修正**（30分）

---

### 明後日 Day 2（1-2時間）

1. **PyInstallerビルド**（30分）
   - ビルド実行
   - ビルド結果の確認

2. **ビルド版の動作確認**（30分）
   - exeファイル実行
   - 全機能テスト

3. **問題があれば修正**（30分）

---

### 3日目（1時間）

1. **最終確認**（30分）
   - すべてのチェックリスト項目を確認
   - ドキュメント確認

2. **ドキュメント更新**（15分）
   - README.md
   - CHANGELOG.md

3. **GitHubへプッシュ**（15分）
   - コミット
   - プッシュ
   - リリースページ作成

---

## 10. 重要な注意事項

### ⚠️ 初回Whisperモデルダウンロード

- 初回起動時にWhisperモデル（約1.5GB - 3GB）がダウンロードされます
- **インターネット接続が必要です**
- ダウンロード時間: 約10-30分（回線速度による）
- ダウンロード先: `%USERPROFILE%\.cache\huggingface\hub`

**ダウンロードサイズ**:
- Medium モデル: 約1.5GB
- Large-v3 モデル: 約2.9GB

---

### ⚠️ ビルドサイズ

- 完成したexeファイル（フォルダ一式）: 約500MB-1GB
- Whisperモデルは含まれません（初回実行時にダウンロード）
- 配布時: ZIPファイルで圧縮推奨

---

### ⚠️ Windows Defender

- PyInstallerでビルドしたexeは、初回実行時にWindows Defenderに検疫される可能性があります
- **除外設定が必要な場合があります**
- 配布時: ユーザーに除外設定の手順を案内

---

### ⚠️ メモリ使用量

- 文字起こし処理中: 約2-4GB
- Large-v3モデル使用時: 約4-6GB
- **8GB以上のメモリ推奨**

---

### ⚠️ GPU対応

- 現在の設定: CPU only（`device="cpu"`）
- GPU対応する場合: CUDA対応版のfaster-whisperが必要
- GPU版は別途設定が必要

---

## 11. 追加情報

### 参考リンク

- **faster-whisper**: https://github.com/SYSTRAN/faster-whisper
- **pywebview**: https://pywebview.flowrl.com/
- **PyInstaller**: https://pyinstaller.org/
- **FastAPI**: https://fastapi.tiangolo.com/

### コードレビューポイント

- ✅ pathlibを一貫して使用（クロスプラットフォーム対応）
- ✅ エラーハンドリングが充実
- ✅ ログ出力が詳細
- ✅ Windows対応コード（`multiprocessing.freeze_support()`）
- ✅ 日本語処理が適切（改行処理）

---

## 12. 最終確認項目

リリース前に以下を確認:

- [ ] Windows 10での動作確認
- [ ] Windows 11での動作確認
- [ ] 音声ファイル形式のテスト（MP3, M4A, WAV, FLAC, OGG, MP4）
- [ ] 長時間音声（30分以上）のテスト
- [ ] プログレスバーが正常に動作するか
- [ ] モデル削除・再ダウンロード機能
- [ ] オフライン動作確認（モデルダウンロード後）
- [ ] エラーメッセージが日本語で表示されるか
- [ ] ファイル保存先の確認
- [ ] アンインストール方法の確認

---

**最終更新**: 2025-10-03
**バージョン**: Windows v1.1.0
**ステータス**: 修正準備完了
