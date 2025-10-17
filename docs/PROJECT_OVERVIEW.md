# GaQ Offline Transcriber v1.1.0 - プロジェクト概要

## プロジェクトについて

**GaQ Offline Transcriber**は、オフライン動作するAI文字起こしアプリケーションです。

### 基本情報

- **バージョン**: v1.1.0
- **開発元**: 公立はこだて未来大学 辻研究室
- **Website**: https://tsuji-lab.net
- **文字起こしエンジン**: faster-whisper
- **対応プラットフォーム**: macOS、Windows

## 主要機能

### コア機能
- faster-whisper文字起こし（Medium/Large-v3対応）
- リアルタイムプログレスバー（SSE実装）
- 改行処理（句読点・80文字折り返し）
- 結果コピー・txt保存機能
- モデル管理機能

### UI/UX改善
- ウィンドウタイトル：「GaQ Offline Transcriber v1.1.0」
- 研究室表記：「公立はこだて未来大学：辻研究室（tsuji-lab.net）」
- プログレスバーのシャインエフェクト（4秒、明るさ50%）
- コピーメッセージ改善：「文字起こし結果をコピーしました。適切な位置にペーストしてください」

### ブラウザ起動
- Chrome推奨（アプリモード、独立プロファイル）
- フォールバック：デフォルトブラウザ

## 配布方針

### macOS版
- **採用**: 完全パッケージ版（build_standard）
  - Python 3.12.7環境同梱（約350MB）
  - ユーザーは追加ソフトウェアのインストール不要
  - ドラッグ&ドロップですぐに使用可能

- **不採用**: 軽量インストーラー版（launcher_final）
  - Python環境なし（188KB）
  - ユーザーがPython 3をインストール必要
  - 一般ユーザーには困難

### Windows版
- **ポータブルZIP版**: GaQ_Transcriber_Windows_v1.1.0_Portable.zip（138MB）
- **インストーラ版**: GaQ_Transcriber_Windows_v1.1.0_Setup.exe（95MB）

## オフライン動作について

- 初回起動時のみ音声認識モデル（約1.5GB～2.9GB）のダウンロードが必要
- モデルダウンロード後は完全にオフラインで動作
- 初回起動時はインターネット接続が必須

## システム要件

### macOS版
- macOS 10.15以降
- 推奨: 8GB RAM以上

### Windows版
- Windows 10/11
- 推奨: 8GB RAM以上
- CPU: faster-whisper実行時に高負荷

## ディレクトリ構成

```
GaQ_app_v1.1.0/
├── build_standard/              # macOS配布版（完全パッケージ）
│   └── GaQ Offline Transcriber.app (356MB)
│       └── Contents/
│           └── Resources/
│               ├── python/      # Python 3.12.7同梱
│               └── app/         # アプリケーション本体
│
├── launcher_final/              # 使用しない（軽量版）
│
├── release/
│   └── windows/                 # Windows版
│       ├── src/                 # ソースコード
│       ├── GaQ_Transcriber.spec # PyInstallerビルド設定
│       └── distribution/        # 配布用パッケージ
│
├── docs/                        # 📖 ドキュメント（このディレクトリ）
│   ├── PROJECT_OVERVIEW.md      # プロジェクト概要（このファイル）
│   ├── development/             # 開発記録
│   ├── releases/                # リリース履歴・レポート
│   ├── guides/                  # ガイド・手順書
│   └── troubleshooting/         # トラブルシューティング
│
└── README.md                    # プロジェクト基本情報
```

## ドキュメント構成

すべての開発記録、リリース情報、ガイド、トラブルシューティングは[docs/](.)ディレクトリに集約されています。

### [development/](development/)
- 日々の開発記録
- エラーログ
- 実装メモ

### [releases/](releases/)
- リリース作業報告
- バージョン履歴
- 修正レポート

### [guides/](guides/)
- ビルドガイド
- 配布手順
- 開発環境セットアップ

### [troubleshooting/](troubleshooting/)
- よくある問題と解決策
- エラー対策

## 技術スタック

### バックエンド
- FastAPI: Webアプリケーションフレームワーク
- Uvicorn: ASGIサーバー
- faster-whisper: 音声認識エンジン
- ctranslate2: faster-whisper依存ライブラリ

### フロントエンド
- HTML/CSS/JavaScript
- Server-Sent Events (SSE): リアルタイム進捗通信

### パッケージング
- PyInstaller: スタンドアロン実行ファイル作成
- Inno Setup (Windows): インストーラ作成
- hdiutil (macOS): DMGイメージ作成

## 開発ブランチ戦略

- **main**: 本番リリース版
- **dev**: 開発・検証・エラー対策ブランチ（このブランチ）

すべての開発作業はdevブランチで行い、安定後にmainブランチにマージします。

---

**最終更新**: 2025-10-09
**バージョン**: v1.1.0
**ステータス**: リリース済み
