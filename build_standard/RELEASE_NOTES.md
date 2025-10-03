# GaQ Offline Transcriber v1.1.0 - リリースノート

## 📦 配布パッケージ

**ファイル名**: `GaQ_Transcriber_v1.1.0.dmg`
**サイズ**: 178MB
**場所**: `/Users/yoshihitotsuji/Claude_Code/GaQ_Transcriber_v1.1.0_Release/build_standard/`

---

## ✨ 主な特徴

### 完全自己完結型アプリケーション
- ✅ **外部Python依存を完全排除**: Python Standalone Buildsを使用
- ✅ **どのMac環境でも動作**: `/Library/Frameworks/Python.framework`への依存なし
- ✅ **オフライン動作**: インターネット接続不要（初回AIモデルダウンロード除く）

### 技術仕様
- **Python**: 3.12.7 (Python Standalone Builds)
- **faster-whisper**: 1.0.3 (OpenAI Whisper実装)
- **FastAPI**: 0.104.1
- **uvicorn**: 0.24.0
- **アーキテクチャ**: ARM64最適化（Apple Silicon）

---

## 📊 パッケージ構成

### .appバンドル構造
```
GaQ Offline Transcriber.app (362MB)
├── Contents/
│   ├── MacOS/
│   │   └── GaQ_Transcriber (起動スクリプト)
│   ├── Resources/
│   │   ├── python/ (53MB)
│   │   │   ├── bin/python3
│   │   │   └── lib/libpython3.12.dylib
│   │   ├── venv/ (304MB)
│   │   │   ├── bin/
│   │   │   ├── lib/
│   │   │   └── (fastapi, uvicorn, faster-whisper等)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── transcribe.py
│   │   │   └── templates/
│   │   ├── static/
│   │   │   └── icon.png
│   │   └── icon.icns
│   └── Info.plist
```

### DMG内容
```
GaQ Transcriber v1.1.0.dmg (178MB圧縮)
├── GaQ Offline Transcriber.app
├── Applications (→ /Applications シンボリックリンク)
└── インストール方法.txt
```

---

## 🔧 依存関係の検証結果

### Python実行ファイル
```bash
$ otool -L venv/bin/python3
venv/bin/python3:
    /System/Library/Frameworks/CoreFoundation.framework/...
    @executable_path/../lib/libpython3.12.dylib  ← 相対パス!
    /usr/lib/libSystem.B.dylib
```

✅ `/Library/Frameworks/`への依存なし
✅ システムライブラリのみ使用
✅ 相対パスで自己完結

---

## 🚀 動作確認済み

### 起動テスト
- ✅ Python 3.12.7 正常ロード
- ✅ FastAPIサーバー起動成功
- ✅ ヘルスチェック成功 (http://127.0.0.1:8000/health)
- ✅ Chrome --appモード起動成功
- ✅ UIが正常に表示

### ログ抜粋
```
[2025-10-02 15:50:23] GaQ Offline Transcriber 起動
[2025-10-02 15:50:23] アーキテクチャ: arm64
[2025-10-02 15:50:23] Python: .../venv/bin/python3
[2025-10-02 15:50:23] Pythonバージョン: Python 3.12.7
[2025-10-02 15:50:28] ✅ サーバー起動成功
[2025-10-02 15:50:28] Chrome --appモードでブラウザを起動
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     127.0.0.1:62823 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:62824 - "GET / HTTP/1.1" 200 OK
```

---

## 📝 インストール手順

1. DMGファイルをダブルクリックしてマウント
2. `GaQ Offline Transcriber.app`を`Applications`フォルダにドラッグ&ドロップ
3. Applicationsフォルダから起動
4. 初回セキュリティ警告が出た場合:
   - 「システム設定」→「プライバシーとセキュリティ」
   - 「このまま開く」をクリック

---

## 🎯 解決した技術課題

### 1. Python依存問題
**問題**: 標準venvは`/Library/Frameworks/Python.framework/`にシンボリックリンク
**解決**: Python Standalone Buildsで完全自己完結化

### 2. 空白を含むパス問題
**問題**: "GaQ Offline Transcriber.app"の空白でシェルスクリプトがエラー
**解決**: すべてのパス変数を引用符で囲む

### 3. ensurepip問題
**問題**: Python Standalone Buildsで`ensurepip`が失敗
**解決**: `--without-pip`で作成後、手動でpipインストール

### 4. libpython参照問題
**問題**: `dyld: Library not loaded: libpython3.12.dylib`
**解決**: `venv/lib/`にシンボリックリンク作成

---

## 🔍 システム要件

- **OS**: macOS 11.0 (Big Sur) 以降
- **CPU**: Apple Silicon (M1/M2/M3) または Intel Mac
- **RAM**: 4GB以上推奨
- **ストレージ**: 約2GB（アプリ362MB + AIモデル1.4GB）

---

## 📧 開発・サポート

**開発**: 公立はこだて未来大学 辻研究室 (tsuji-lab.net)
**ログファイル**: `~/Library/Logs/GaQ_Transcriber.log`
**モデル保存先**: `~/.cache/huggingface/hub/`

---

## ⚙️ 次回配布時の注意点

### DMG再作成手順
```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_Transcriber_v1.1.0_Release/build_standard
rm -rf dmg_contents
mkdir dmg_contents
cp -R "GaQ Offline Transcriber.app" dmg_contents/
ln -s /Applications dmg_contents/Applications
cp インストール方法.txt dmg_contents/
hdiutil create -volname "GaQ Transcriber v1.1.0" -srcfolder dmg_contents -ov -format UDZO GaQ_Transcriber_v1.1.0.dmg
```

### 署名とNotarization（オプション）
本リリースでは未実施。Apple Developer IDで署名する場合:
```bash
codesign --deep --force --sign "Developer ID Application: ..." "GaQ Offline Transcriber.app"
xcrun notarytool submit GaQ_Transcriber_v1.1.0.dmg --keychain-profile "..."
```

---

**リリース日**: 2025年10月2日
**バージョン**: 1.1.0
**ビルド**: Python Standalone Builds版
