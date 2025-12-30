# GaQ Offline Transcriber

オフラインで動作する faster-whisper ベースの文字起こしアプリです。macOS / Windows の両方で v1.2.10 を提供しており、初回のみモデルをダウンロードすれば以降は完全にオフラインで利用できます。

---

## 🚨 重要：AI担当者への最優先指示

**このREADME.mdを最初から最後まで必ず精読してください。**

あなたが新しくこのプロジェクトに参加する際、または作業を再開する際は、以下の手順を厳守してください：

### 📋 AI起動時の必須手順（5ステップ）

1. **README.md精読** → プロジェクト全体像を把握
2. **役割定義確認** → `@claude.md` または `@codex.md` を確認
3. **LOG確認** → `docs/development/` で最新の作業状況を確認
4. **HISTORY確認** → `docs/HISTORY.md` で重要な開発履歴を確認
5. **From/To形式で応答開始** → 必ず「From: [あなたの名前] / To: [受信者名]」形式で開始

### ⚠️ 禁止事項

- README.mdを読まずに作業を開始すること
- 三者協働ルールを無視して単独で判断すること
- From/To形式を使わずに応答すること
- ログや決定事項を記録せずに作業を進めること
- **日本語以外の言語（英語等）で応答・ドキュメント・コメントを記述すること**

**開発方法論の詳細**: [Dev-Rules](https://github.com/yoshihito-tsuji/Dev-Rules) を参照してください。

---

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
  - Windows v1.2.10（ブラウザアプリモード - pythonnet依存解消）
  - macOS v1.2.10（最新安定版）
- 詳しい配布状況と改善内容は `docs/handbook/release_status.md` を参照

## 使い方（Mac版）
1. GitHub Releases から `GaQ_Transcriber_v1.1.1_mac.dmg` をダウンロード
2. DMG をマウントし、`GaQ Offline Transcriber.app` を Applications にドラッグ
3. アプリを起動し、クリックまたはドラッグ&ドロップで音声ファイルを選択
4. モデル（Medium / Large-v3）を選び、「文字起こし開始」を押す
5. 進捗バーとログを確認しながら待機し、完了後にコピーまたは保存

## 使い方（Windows版ポータブル）
1. `GaQ_Transcriber_Windows_v1.1.1_Portable.zip` を取得し、任意のフォルダに展開
2. `GaQ_Transcriber.exe` を実行（初回のみモデル自動ダウンロード）
3. 音声ファイルを選択 → モデル選択 → 「文字起こし開始」
4. 完了後に結果をコピーするか、メタデータ付きで保存

## 主要な操作ポイント
- ファイルはダイアログ / ドラッグ&ドロップの両方に対応
- モデル変更時は自動的に再アップロードされるため、同一ファイルを繰り返し指定する必要はありません
- 保存時には文字数・処理時間が追記され、クリップボードコピーは AppleScript（macOS）と Windows API を使用

## トラブルシューティング
- ログ確認: `tail -f ~/.gaq/logs/app.log`（macOS）  
  Windows でも `~\\.gaq\\logs\\app.log` を参照可能
- 詳細な診断フローや JS / pywebview の調査手順は `docs/handbook/troubleshooting.md` を参照してください

## ドキュメント案内

### ユーザー向けドキュメント
- `docs/handbook/release_status.md` – 配布状況、ダウンロードリンク、変更点
- `docs/handbook/troubleshooting.md` – 詳細な診断手順・過去の事例
- `docs/PROJECT_OVERVIEW.md` – プロジェクト概要

### 開発者向けドキュメント
- `docs/HISTORY.md` – 開発履歴と重要な決定事項
- `docs/handbook/development_workflow.md` – リポジトリ運用ルール、チェックリスト、ビルド方法
- `docs/development/` – 日次開発ログ
- `docs/releases/` – リリースレポート
- `@claude.md` / `@codex.md` – AI担当者の役割定義

### 三者協働開発ルール
このプロジェクトは [Dev-Rules](https://github.com/yoshihito-tsuji/Dev-Rules) の三者協働開発方法論に基づいて開発されています。

- **Codex（設計担当）**: 要件分析、システム設計、技術選定
- **Claude Code（実装担当）**: コーディング、テスト、デバッグ
- **Yoshihitoさん（プロダクトオーナー）**: 最終意思決定、要件定義

詳細は [Dev-Rules README](https://github.com/yoshihito-tsuji/Dev-Rules/blob/main/README.md) を参照してください。

## 連絡先
- Website: https://tsuji-lab.net
- 問題報告: GitHub Issues（リンク先 Release ページ参照）
- 最終更新: 2025-12-30（macOS v1.2.10 / Windows v1.2.10）
