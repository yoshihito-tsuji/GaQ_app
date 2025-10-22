# GaQ Offline Transcriber v1.1.1 リリースノート

**リリース日**: 2025-10-21
**バージョン**: 1.1.1
**プラットフォーム**: macOS (Intel & Apple Silicon)

---

## 📋 概要

v1.1.1では、SSE（Server-Sent Events）の改善とログ管理の最適化を実施しました。フェーズ1として4つの高優先度改善を実装し、パフォーマンスと保守性を向上させました。

---

## ✨ 新機能・改善

### 1. ハートビート間隔の設定化

**環境変数による柔軟な設定**

- 環境変数 `GAQ_SSE_HEARTBEAT_INTERVAL` でSSEハートビート間隔を調整可能
- デフォルト: 10秒（既存動作と同じ）
- 用途: ネットワーク環境に応じた最適化

**使用例**:
```bash
# 5秒間隔に設定
export GAQ_SSE_HEARTBEAT_INTERVAL=5
open "/Applications/GaQ Offline Transcriber.app"
```

**メリット**:
- ネットワーク環境に応じた柔軟な調整
- 既存動作への影響なし

---

### 2. ログレベル制御

**環境変数によるログ出力制御**

- 環境変数 `GAQ_LOG_LEVEL` でログレベルを制御可能
- デフォルト: `INFO`（ハートビートログは非表示でノイズ削減）
- デバッグ時: `DEBUG`（ハートビートログを含む詳細ログを出力）

**使用例**:
```bash
# デバッグモードで起動
export GAQ_LOG_LEVEL=DEBUG
open "/Applications/GaQ Offline Transcriber.app"
```

**メリット**:
- 本番環境: ログノイズ削減（ハートビートログが出ない）
- デバッグ時: 詳細ログで問題追跡が容易

---

### 3. 非ポーリング化の簡素化

**CPU使用量の最適化**

- 0.1秒ポーリング → `asyncio.timeout()` による非ポーリング方式に変更
- `heartbeat_counter` と `MAX_WAIT_WITHOUT_HEARTBEAT` を削除
- コードの明確化と保守性向上

**メリット**:
- CPU使用量削減: 0.1秒×100回 → ハートビート間隔（10秒）で1回
- コード簡潔化: 不要な変数を削除
- 意図明確化: タイムアウト = ハートビート送信

---

### 4. SSE切断検知とログ整備

**クライアント切断時の適切な処理**

- `asyncio.CancelledError` による切断検知を実装
- 切断時に「🔌 クライアント切断検知」をログ出力
- Futureのキャンセル処理を追加

**メリット**:
- トラブルシュート容易化: 切断原因が明確
- リソースの適切な解放
- エラーハンドリング強化

---

## 🐛 バグ修正

### クリップボードコピー検証処理のノイズ除去

**問題**:
- pbpaste検証処理が誤検知により警告を出力
- 実際にはクリップボードコピーは正常動作

**修正内容**:
- pbpaste検証処理を完全削除
- AppleScriptの`set the clipboard to`のみを使用

**影響**:
- ログノイズ削減
- コードの簡潔化

---

## 📊 テスト結果

### 自動テスト

| テスト項目 | 結果 |
|-----------|------|
| ハートビート間隔の設定化 | ✅ PASS |
| ログレベル制御 | ✅ PASS |
| 非ポーリング化の簡素化 | ✅ PASS |
| SSE切断検知とログ整備 | ✅ PASS |

**総合判定**: ✅ **ALL PASS**

### 手動テスト（2025-10-21実施）

- ✅ ハートビート間隔（5秒設定）: 正確に5秒間隔で送信されることを確認
- ✅ ログレベル制御: INFOではハートビートログが出ず、DEBUGでは出ることを確認
- ✅ SSE切断検知: 切断時に「🔌 クライアント切断検知」ログが出ることを確認

詳細: [テスト結果ドキュメント](development/20251021_phase1_test_results.md)

---

## 📦 インストール

### macOS

1. **DMGファイルをダウンロード**:
   - `GaQ_Transcriber_v1.1.1_mac.dmg` (77MB)

2. **インストール**:
   - DMGファイルをダブルクリック
   - アプリを`Applications`フォルダにドラッグ&ドロップ

3. **初回起動**:
   - Applicationsフォルダから「GaQ Offline Transcriber」を右クリック → 「開く」

---

## 🔧 環境変数設定（オプション）

### ターミナルから起動する場合

```bash
# ログレベルをDEBUGに設定
export GAQ_LOG_LEVEL=DEBUG

# ハートビート間隔を5秒に設定
export GAQ_SSE_HEARTBEAT_INTERVAL=5

# アプリを起動
open "/Applications/GaQ Offline Transcriber.app"
```

### 通常起動の場合

環境変数を設定せずにアプリを起動すると、デフォルト設定が適用されます：
- ログレベル: `INFO`
- ハートビート間隔: `10秒`

---

## 📝 変更内容の詳細

### 変更ファイル

- `release/mac/src/main.py`: 2321行（+14行）
- `release/mac/src/main_app.py`: 848行（-35行）

### ソースコード同期

- ✅ Mac版とWindows版が完全同期（`check_sync.sh` で確認）

---

## 🎯 今後の予定

### フェーズ2（中優先度）

1. **進捗通知の双方向化**: サーバー→クライアントの進捗通知の改善
2. **エラーハンドリング強化**: より詳細なエラー情報とリカバリ処理

### フェーズ3（低優先度）

1. **リトライ機能**: 一時的なネットワークエラーのリトライ
2. **タイムアウト設定**: 長時間処理のタイムアウト設定

---

## 🔗 関連ドキュメント

- [フェーズ1実装詳細](development/20251021_phase1_implementation.md)
- [テスト結果](development/20251021_phase1_test_results.md)
- [開発履歴](HISTORY.md)
- [Codex相談結果分析](development/20251021_codex_response_analysis.md)

---

## ⚠️ 既知の問題

特になし

---

## 📞 サポート

問題が発生した場合は、以下のログファイルを確認してください：
- macOS: `~/.gaq/logs/app.log`

デバッグモードでの起動:
```bash
export GAQ_LOG_LEVEL=DEBUG
open "/Applications/GaQ Offline Transcriber.app"
```

---

**開発**: Claude Code + Codex（技術コンサルティング）
**リリース日**: 2025-10-21
**ライセンス**: [プロジェクトライセンスに準拠]
