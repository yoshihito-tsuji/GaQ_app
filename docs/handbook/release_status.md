# Release Status & Distribution

GaQ Offline Transcriber は macOS / Windows の双方で v1.1.1 を提供中です。配布状況と直近の改善内容をここに集約し、README から参照可能な新しい情報ハブとしました。

## 現行バージョン

- **Mac**: v1.1.1（pywebview 課題をすべて解消、実運用可能）
- **Windows**: v1.1.1（クリップボード関連の API 定義を修正）
- **文字起こしエンジン**: faster-whisper（Medium / Large-v3）

## コード署名・公証の状況

### macOS

| 項目 | 状況 | 備考 |
| --- | --- | --- |
| Developer ID署名 | ✅ 対応済み | `./build.sh --sign` |
| Apple公証（Notarization） | ✅ 対応済み | `./build.sh --notarize` |
| Stapler埋め込み | ✅ 対応済み | 公証後自動実行 |
| DMG署名 | ✅ 対応済み | 署名モード時に自動 |

署名・公証済みのDMGは、Gatekeeperで保護されたMacでも警告なしにインストールできます。

### Windows

| 項目 | 状況 | 備考 |
| --- | --- | --- |
| MSIX化 | ⏳ 準備中 | SmartScreen回避のため |
| SignTool署名 | ⏳ 準備中 | EV証明書を検討中 |
| Microsoft Store | 📋 将来検討 | 任意 |

現在はPortable ZIP版を提供中。SmartScreen警告が表示される場合は「詳細情報」→「実行」で起動可能。

## 配布パッケージ

### macOS版

- GitHub Releases: [v1.1.1-mac](https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.1.1-mac)
- ダウンロード: [GaQ_Transcriber_v1.1.1_mac.dmg (77.5MB)](https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1-mac/GaQ_Transcriber_v1.1.1_mac.dmg)
- ハッシュ: [SHA256](https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1-mac/GaQ_Transcriber_v1.1.1_mac.dmg.sha256)
- 変更ハイライト: SSE ハートビート / アプリ終了高速化 / pywebview 完全対応 / モデル自動ダウンロード

### Windows版

- 搭載バージョン: v1.1.1 Portable ZIP（139MB）
  `C0A423E91310702AAAFCE6896F63C493A05249C20A01CEC39401AA6D796E48CB`
- 配布形式: ZIP 解凍 → `GaQ_Transcriber.exe` 実行（インストーラ版は署名準備中）
- 修正内容: クリップボードコピーでの Windows API 型定義を追加
- リリース配布: GitHub Releases への掲載準備中（暫定で手動共有）

### オフライン動作

- 初回のみ音声認識モデル（1.5GB〜2.9GB）をダウンロード
- モデル取得後は完全オフライン

## 動作環境

| 項目 | macOS | Windows |
| --- | --- | --- |
| 対応 OS | macOS 10.15+（確認済み: macOS 14.8 arm64） | Windows 10 / 11 |
| 推奨メモリ | 8GB 以上 | 8GB 以上 |
| バンドル環境 | Python 3.12 同梱 DMG | Portable ZIP（Python 同梱） |
| 主要依存 | pywebview 6.0 / PyInstaller 6.16.0 | 同等構成 |

## 2025-10-18 改善サマリ

| 改善項目 | 内容 | 効果 |
| --- | --- | --- |
| ドラッグ&ドロップ | `text/uri-list` から直接ファイルパスを取得 | クリック操作と併用可能になり UX 向上 |
| Large-v3 切替時の再アップロード | モデル変更前に常にファイルを再アップロード | モデル切替時の「ファイルが見つかりません」を排除 |
| クリップボードコピー | AppleScript + 一時ファイルで確実にコピー | 長文でも確実にコピー、検証ノイズを排除 |
| 保存ファイルのメタデータ | 文字数と処理時間を末尾に追記 | 共有用ログが自動で整備される |
| モデルダウンロード動線 | 自動ダウンロード + トースト通知 + 完了後自動開始 | ワークフローがワンクリック化 |

## 動作確認済み項目

1. ファイル選択ダイアログ
2. ドラッグ&ドロップ
3. Medium / Large-v3 モデルでの文字起こし
4. リアルタイム進捗表示
5. 結果のコピー（AppleScript）
6. 結果保存（メタデータ付き）
7. モデル選択（再アップロードを含む）

## 既知課題と履歴

- pywebview 環境の動作不良（2025-10-17 → 18 にて全項目解消）
- HTML テンプレートでの波括弧衝突 → `string.Template` へ移行
- Windows Installer（Setup.exe）は SmartScreen を回避するため MSIX 化＋署名を準備中
- 詳細な日次レポートは `docs/development/` と `docs/releases/` を参照

## 参考資料

- [docs/HISTORY.md](../HISTORY.md) – プロジェクト履歴
- [docs/releases/](../releases/) – リリースごとのレポート
- [docs/handbook/development_workflow.md](development_workflow.md) – 配布と同期手順
- [docs/handbook/troubleshooting.md](troubleshooting.md) – リリース後の安定性確保手順

**最終更新**: 2025-12-05（署名・公証フロー追加）
