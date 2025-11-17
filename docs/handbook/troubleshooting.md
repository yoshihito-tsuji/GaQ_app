# Troubleshooting & Diagnostics

運用時および開発時の詳細なトラブルシューティング手順をまとめました。README ではコマンド提示のみとし、実際の作業はこのファイルを参照してください。

## クイック確認
- アプリ動作中のログ追跡: `tail -f ~/.gaq/logs/app.log`
- JavaScript ログ確認: macOS では `CMD+Option+I` で Web Inspector、または Safari で `/tmp/gaq_debug.html` を開く
- コマンド失敗時は `docs/development/` にエラーログを作成

## JavaScript / pywebview 調査フロー
1. アプリを起動し、ログに `[JS]` が流れているか確認  
   表示例:
   ```
   [JS] ✅ Console hook installed
   [JS] ✅ initializeApp() 完了
   ```
   → ログが何も出ない場合は JavaScript 初期化エラー
2. Safari 開発者ツールで `/tmp/gaq_debug.html` を開き、コンソールエラーと行番号を確認
3. エラー行を `sed -n '1390,1405p' /tmp/gaq_debug.html` などで抽出し、`release/*/src/main.py` と突き合わせ
4. 典型的な原因
   - `\n` のエスケープ漏れ → `\\n` に置換
   - 閉じ括弧 / クォート齟齬
   - `ReferenceError`（関数定義順序）
5. テストモードでの再現:  
   ```bash
   cd release/mac
   export GAQ_TEST_MODE=1
   export GAQ_WEBVIEW_DEBUG=1
   bash test_javascript.sh
   ```
   Alert が出れば JavaScript 環境は正常。出ない場合は構文エラーや pywebview 設定を疑う。

## クリップボード関連
- 2025-10-21 以前は `pbpaste` による検証処理が誤検知を起こしていた（`WARNING - ⚠️ クリップボード内容が一致しません`）
- AppleScript + 一時ファイル方式へ移行済みで、コピー自体は成功している
- 手動検証が必要な場合: `pbpaste | wc -m` / `pbpaste | head -c 100`

## モデルダウンロード
- ダウンロードが止まる → ネットワークと `~/.cache/huggingface/` の空き容量（Large-v3 約 3GB）を確認
- 2025-10-18 以降は自動ダウンロード + トースト通知に統一

## 文字起こし品質
- 精度が低い場合は Large-v3 を選択
- 音声ソースのノイズや音量を確認し、必要なら外部ツールで前処理

## 既知の再発防止ポイント
- 2025-10-03: `progress_callback` 未設定でプログレスバーが進まない → コールバックは必ず渡す
- 2025-10-17〜18: pywebview 差分で Mac/Windows どちらかが破綻 → 共通コードの片側のみ修正は禁止
- 詳細調査ログ: `docs/releases/PROGRESS_BAR_FIX_REPORT.md`, `docs/development/20251018_final_completion_report.md`

## 追加の診断手順
### Safari 検証
```bash
open "/Applications/GaQ Offline Transcriber.app"
open -a Safari /tmp/gaq_debug.html
```

### ログ検索
```bash
tail -50 ~/.gaq/logs/app.log | grep -i error
```
- `SyntaxError` → JavaScript 構文エラー
- `ReferenceError` → 未定義
- `🚨 [Global Error]` → 実行時エラー（優先調査）

### エラー再現テンプレ
```bash
cp docs/development/ERROR_LOG_TEMPLATE.md docs/development/errors/ERROR_issue.md
```
- 発生条件 / 期待結果 / 実際の結果 / ログ抜粋 / 再発防止策を記入

## フィードバック経路
- ユーザー報告: GitHub Issues または 研究室窓口（README 参照）
- 内部共有: `docs/development/` ログ、`docs/team_ops/` で連絡体制を更新

---

このファイルに追記する際は「詳細手順・調査ログ・ケーススタディ」を積極的に集約し、README 側はリンクのみを残す方針で運用します。
