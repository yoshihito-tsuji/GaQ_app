# Codex報告: JavaScript完全停止問題の解決（2025-10-19）

## 📋 概要

GaQ Offline Transcriber（pywebview + FastAPI）において、2025-10-19にJavaScriptが完全に実行されない重大な問題が発生しましたが、根本原因を特定し解決しました。

---

## 🚨 問題の詳細

### 発生状況
- **発生日時**: 2025-10-19 15:30（カスタムダイアログ実装後）
- **影響範囲**: すべてのUI機能（ドラッグ&ドロップ、ボタン、モデル管理）
- **継続時間**: 約5時間（15:30-20:05）

### 症状
1. JavaScriptが一切実行されない
2. `console.log()` がPythonログに記録されない
3. デバッグメッセージ（alert、DOM操作）も動作しない
4. **Python側は正常動作**（FastAPI、pywebview Bridge API）

### 最も困難だった点
- HTMLは正しく生成されている（64KB、構造も正常）
- Python側のpywebviewも正常動作
- ログにエラーメッセージが一切ない
- グローバルエラーハンドラーすら発火しない

---

## 🔍 根本原因

### Safari検証により判明
```
SyntaxError: Unexpected EOF
  at gaq_debug.html:1397
```

### 問題コード
```python
# main.py (Pythonトリプルクォート内)
html_template = Template("""
    <script>
        alert('モデル削除しますか？\n\n再ダウンロード必要です。');
    </script>
""")
```

### 何が起きたか
Pythonのトリプルクォート `"""..."""` 内では、`\n` が**リテラル改行**として扱われる。

生成されたHTML:
```javascript
alert('モデル削除しますか？
                      ↑ ここで実際に改行（構文エラー！）
再ダウンロード必要です。');
```

JavaScriptでは、**シングルクォート文字列内での改行は構文エラー**になる。

---

## ✅ 解決方法

### 修正
```python
# 修正前
alert('...\n\n...');  # → 実際の改行になる

# 修正後
alert('...\\n\\n...');  # → JavaScript内で \n として正しく解釈
```

### 実装箇所
- [release/mac/src/main.py:1462](file:///Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/src/main.py#L1462)
- [release/mac/src/main.py:1466](file:///Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/src/main.py#L1466)

---

## 🛡️ 追加実装（再発防止）

### 1. グローバルエラーハンドラー
```javascript
window.addEventListener('error', function(event) {
    var errorMsg = '🚨 [Global Error] ' + event.message +
                   ' at ' + event.filename + ':' + event.lineno;
    console.error(errorMsg);
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.log_message('error', errorMsg);
    }
});

window.addEventListener('unhandledrejection', function(event) {
    var errorMsg = '🚨 [Unhandled Promise Rejection] ' + event.reason;
    console.error(errorMsg);
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.log_message('error', errorMsg);
    }
});
```

**効果**: 今後はすべてのJavaScriptエラーがPythonログに記録される。

### 2. テスト環境整備
- `/test` エンドポイント（極小テストHTML）を追加
- `GAQ_TEST_MODE=1` でテストページ起動
- `GAQ_WEBVIEW_DEBUG=1` でWebKit Inspector有効化
- `test_javascript.sh` スクリプトで簡単にテスト実行

### 3. 未定義ガード
```javascript
function deleteModel(modelName) {
    if (typeof window.showConfirmDialog !== 'function') {
        console.error('❌ showConfirmDialog is not defined');
        alert('...');  // フォールバック
        return;
    }
    // 通常処理
}
```

---

## 📊 検証プロセス（重要な教訓）

### ステップ1: pywebview固有問題の疑い（誤り）
- 仮説: pywebviewのWebKit制約やキャッシュ問題
- 試行: デバッグモード、テストページ作成
- 結果: 効果なし

### ステップ2: スコープ問題の疑い（誤り）
- 仮説: カスタムダイアログ関数が別`<script>`タグで定義されている
- 試行: `window.*` への明示バインド、メインスクリプトへの統合
- 結果: 効果なし

### ステップ3: Safari検証（正解への道）
**ユーザー様の提案により実施**

```bash
open -a Safari /tmp/gaq_debug.html
```

1. Safari開発メニュー → JavaScriptコンソール
2. `SyntaxError: Unexpected EOF` at line 1397 を発見
3. 該当行を確認 → 文字列内改行を発見
4. Pythonソースコードとの比較 → `\n` エスケープ不足を特定

**所要時間**: Safari検証により10分で根本原因を特定（それまでの試行錯誤は約4時間）

---

## 🎓 教訓

### 1. Safari検証の重要性
- pywebview問題の切り分けに**必須**
- JavaScriptコンソールでの構文エラー確認が**最速**
- 今後はトラブル発生時に**最初に実行すべき手順**

### 2. Python文字列テンプレートの注意点
```python
# ❌ 誤り
"""
<script>
    alert('Line1\nLine2');  # 実際の改行になる
</script>
"""

# ✅ 正しい
"""
<script>
    alert('Line1\\nLine2');  # \n として解釈される
</script>
"""
```

### 3. デバッグ機能の重要性
- グローバルエラーハンドラーがあれば、最初から構文エラーを検出できた
- 極小テストページで問題を切り分けられる

### 4. 段階的デバッグ
1. ブラウザ（Safari）で動作確認 → pywebview/HTML問題を切り分け
2. 極小HTML（/test）で検証 → メインアプリ特有の問題を切り分け
3. エラーログ確認 → 具体的なエラー箇所を特定

---

## 📈 成果

### ✅ 完全復旧（20:02ビルド）
- すべてのUI機能が正常動作
- ユーザー確認済み

### 🚀 機能強化
1. グローバルエラーハンドラー導入
2. テスト環境整備（/test、環境変数、スクリプト）
3. 未定義ガード実装
4. カスタムダイアログAPI（「お知らせ」ヘッダー）

### 📝 ドキュメント整備
- 開発ログに詳細な調査過程を記録
- トラブルシューティングガイドをREADMEに追加予定
- 再発防止策の明文化

---

## 🔧 今後の推奨事項

### 開発フロー改善
1. **JavaScript変更時は必ずSafari検証**
   ```bash
   # ビルド後
   open -a Safari /tmp/gaq_debug.html
   # JavaScriptコンソールでエラー確認
   ```

2. **文字列エスケープルールの徹底**
   - Pythonトリプルクォート内のJavaScript: `\n` → `\\n`
   - レビュー時のチェックポイントに追加

3. **テスト環境の活用**
   ```bash
   # JavaScript実行テスト
   cd release/mac
   bash test_javascript.sh
   ```

### コード品質向上
1. HTMLテンプレート生成の見直し検討
   - `string.Template` → Jinja2移行を検討
   - JavaScript部分を外部ファイル化

2. CI/CDでの自動検証
   - ビルド後に自動でSafari検証
   - JavaScript構文チェックツール導入

---

## 📎 関連ファイル

- **修正ファイル**: `release/mac/src/main.py`
- **開発ログ**: `docs/development/20251019_smoke_test_and_sync_check.md`
- **テストスクリプト**: `release/mac/test_javascript.sh`
- **相談ドキュメント**: `codex_consultation_v2.md`

---

## 🙏 謝辞

ユーザー様による**Safari検証の提案**が問題解決の決定打となりました。pywebview環境でのデバッグは困難ですが、ブラウザ検証という基本的かつ強力な手法により、迅速に根本原因を特定できました。

---

**報告日**: 2025-10-19
**解決時刻**: 20:05
**最終ビルド**: GaQ_Transcriber_v1.1.1_mac.dmg (78MB)
