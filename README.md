# GaQ Offline Transcriber

オフラインで動作する faster-whisper ベースの文字起こしアプリです。macOS / Windows の両方で v1.1.1 を提供しており、初回のみモデルをダウンロードすれば以降は完全にオフラインで利用できます。

## プライバシーポリシー

**本アプリは、利用者の情報保護を最優先に設計されています。**

### 外部通信について

- **AIモデルの初回ダウンロード時のみ**、外部サーバー（Hugging Face）と通信します
- モデルダウンロード完了後は、**完全にオフラインで動作**します
- 音声データ、文字起こし結果、設定情報は**一切外部に送信されません**

### 開発者としての対応

開発者が制御可能な範囲において、以下の設計方針を採用しています：

- テレメトリ（利用統計）の収集なし
- エラーレポートの自動送信なし
- 外部CDN/ライブラリの使用なし（全てローカル埋め込み）
- サーバー通信は`127.0.0.1`（ローカル）のみ

> **注**: WebViewエンジン（macOS: WebKit、Windows: CEF）はOS/ブラウザレベルで独自の通信を行う可能性がありますが、これはアプリケーションレベルでは制御できない一般的なWebViewアプリ共通の挙動です。

## 概要
- **開発元**: [公立はこだて未来大学 辻研究室](https://tsuji-lab.net)
- **対応プラットフォーム**: macOS 10.15 以降、Windows 10/11
- **最新リリース**:
  - [macOS v1.1.1](https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.1.1-mac)（pywebview 完全対応）
  - [Windows v1.2.10](https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.2.10)（ブラウザアプリモード採用、安定動作）
- 詳しい配布状況と改善内容は `docs/handbook/release_status.md` を参照

### Windows版 v1.2.10 の変更点

**v1.2.9 以前をお使いの方は、v1.2.10 への更新を推奨します。**

- デフォルトで Edge/Chrome アプリモード（`--app`）を使用
- pythonnet/WinForms 依存を解消し、GitHub配布版の起動問題を根本解決
- 従来のネイティブウィンドウ（pywebview）は廃止（環境変数で選択可能だが非推奨）

## 使い方（Mac版）
1. GitHub Releases から `GaQ_Transcriber_v1.1.1_mac.dmg` をダウンロード
2. DMG をマウントし、`GaQ Offline Transcriber.app` を Applications にドラッグ
3. アプリを起動し、クリックまたはドラッグ&ドロップで音声ファイルを選択
4. モデル（Medium / Large-v3）を選び、「文字起こし開始」を押す
5. 進捗バーとログを確認しながら待機し、完了後にコピーまたは保存

## 使い方（Windows版ポータブル）
1. `GaQ_Transcriber_Windows_v1.2.10_Portable.zip` を取得し、任意のフォルダに展開
2. `GaQ_Transcriber.exe` を実行（Edge/Chrome アプリモードで起動）
3. 初回のみモデル自動ダウンロード
4. 音声ファイルを選択 → モデル選択 → 「文字起こし開始」
5. 完了後に結果をコピーするか、メタデータ付きで保存

## 主要な操作ポイント
- ファイルはダイアログ / ドラッグ&ドロップの両方に対応
- モデル変更時は自動的に再アップロードされるため、同一ファイルを繰り返し指定する必要はありません
- 保存時には文字数・処理時間が追記され、クリップボードコピーは AppleScript（macOS）と Windows API を使用

## トラブルシューティング
- ログ確認: `tail -f ~/.gaq/logs/app.log`（macOS）  
  Windows でも `~\\.gaq\\logs\\app.log` を参照可能
- 詳細な診断フローや JS / pywebview の調査手順は `docs/handbook/troubleshooting.md` を参照してください

## ドキュメント案内
- `docs/handbook/release_status.md` – 配布状況、ダウンロードリンク、変更点
- `docs/handbook/development_workflow.md` – リポジトリ運用ルール、チェックリスト、ビルド方法
- `docs/handbook/troubleshooting.md` – 詳細な診断手順・過去の事例
- `docs/PROJECT_OVERVIEW.md` / `docs/HISTORY.md` – プロジェクト概要と履歴
- `docs/development/` / `docs/releases/` – 日次ログとリリースレポート

## 連絡先
- Website: https://tsuji-lab.net
- 問題報告: GitHub Issues（リンク先 Release ページ参照）
- 最終更新: 2025-12-13（macOS v1.1.1 / Windows v1.2.10）
