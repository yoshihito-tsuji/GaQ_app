# GaQ Offline Transcriber v1.1.1

音声・動画ファイルを高精度にテキスト化するオフライン文字起こしアプリです。

## 📦 リリース情報

- **バージョン**: v1.1.1
- **リリース日**: 2025-11-11
- **対応プラットフォーム**: macOS 10.15 (Catalina) 以降

## ✨ 主な機能

### 高精度な文字起こし
- Whisper AIモデルによる高精度な音声認識
- 日本語・英語など多言語対応
- オフライン動作（インターネット接続不要）

### 使いやすいインターフェース
- ドラッグ&ドロップでのファイル選択
- リアルタイム進捗表示
- 完了時の通知機能

### 便利な出力機能
- クリップボードへのコピー機能
- メタデータ付きテキストファイル保存
- タイムスタンプ付き出力

## 📥 ダウンロード

### macOS版
- **DMGファイル**: [GaQ_Transcriber_v1.1.1_mac.dmg](https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1-mac/GaQ_Transcriber_v1.1.1_mac.dmg) (77.5MB)
- **SHA256ハッシュ**: [GaQ_Transcriber_v1.1.1_mac.dmg.sha256](https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1-mac/GaQ_Transcriber_v1.1.1_mac.dmg.sha256)

## 💻 動作環境

### macOS版
- **OS**: macOS 10.15 (Catalina) 以降
- **メモリ**: 8GB RAM以上推奨
- **ストレージ**: 約200MB（アプリ本体 + モデルファイル）
- **ネットワーク**: 初回起動時のみ（モデルダウンロード用）

## 🚀 インストール方法

1. **DMGファイルをダウンロード**
   - 上記リンクから `GaQ_Transcriber_v1.1.1_mac.dmg` をダウンロード

2. **DMGをマウント**
   - ダウンロードしたDMGファイルをダブルクリック

3. **アプリをインストール**
   - "GaQ Offline Transcriber.app" を Applications フォルダにドラッグ&ドロップ

4. **アプリを起動**
   - Applications フォルダから "GaQ Offline Transcriber" を起動
   - 初回起動時は右クリック → "開く" を選択（Gatekeeperの警告を回避）

## 🔒 セキュリティ

ダウンロードしたファイルの整合性を確認できます：

```bash
# ファイルをダウンロード後、ターミナルで実行
shasum -a 256 GaQ_Transcriber_v1.1.1_mac.dmg

# SHA256ハッシュファイルと比較
curl -L https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1-mac/GaQ_Transcriber_v1.1.1_mac.dmg.sha256
```

## 📝 v1.1.1の変更内容

### Mac版
- ✅ Python 3.12.3環境で動作確認済み
- ✅ すべての主要機能が正常動作
- ✅ ドラッグ&ドロップでのファイル選択対応
- ✅ リアルタイム進捗表示
- ✅ クリップボードコピー機能
- ✅ メタデータ付きファイル保存
- ✅ 安定性の向上

## 🛠️ 技術仕様

- **Python**: 3.12.3
- **Whisper**: OpenAI Whisper (faster-whisper)
- **UI**: pywebview + FastAPI
- **パッケージング**: PyInstaller

## 🐛 既知の問題

現在、重大な既知の問題はありません。

問題が発生した場合は、[Issues](https://github.com/yoshihito-tsuji/GaQ_app/issues) でご報告ください。

## 📚 ドキュメント

- [README.md](https://github.com/yoshihito-tsuji/GaQ_app/blob/main/README.md) - プロジェクト概要
- [docs/HISTORY.md](https://github.com/yoshihito-tsuji/GaQ_app/blob/main/docs/HISTORY.md) - 開発履歴

## 👥 開発元

**公立はこだて未来大学 辻研究室**

## 📊 フィードバック

アプリの改善にご協力ください：

- バグ報告: [GitHub Issues](https://github.com/yoshihito-tsuji/GaQ_app/issues)
- 機能要望: [GitHub Issues](https://github.com/yoshihito-tsuji/GaQ_app/issues)
- その他: 辻研究室までお問い合わせください

---

**ライセンス**: [LICENSE](https://github.com/yoshihito-tsuji/GaQ_app/blob/main/LICENSE)
