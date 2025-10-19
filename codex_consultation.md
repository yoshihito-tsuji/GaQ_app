# Codex相談: pywebview + FastAPI アプリケーションでJavaScriptが実行されない問題

## 問題の概要

GaQ Offline Transcriber（pywebview + FastAPI構成のmacOSアプリケーション）において、2025-10-19の15:30ビルド以降、**JavaScriptが全く実行されない**という深刻な問題が発生しています。

## 症状

1. **JavaScript実行の完全な停止**
   - `alert()` やデバッグメッセージが一切表示されない
   - JavaScriptのコンソールログが全く記録されない
   - UI要素（ボタン、ドラッグ&ドロップなど）が全て無反応

2. **Python側は正常**
   - FastAPIサーバーは正常に起動（`http://127.0.0.1:8000`）
   - `GET /` エンドポイントは呼ばれている
   - HTMLテンプレートは正常に生成されている（62,813 bytes）
   - Python側のドラッグ&ドロップハンドラーは動作している

3. **ログからの観察**
   - 15:21のセッション: 完全に動作（大量のJavaScriptログあり）
   - 15:31以降のセッション: JavaScriptログが一切ない
   - 15:56のデバッグセッション:
     ```
     🌐 [DEBUG] GET / エンドポイントが呼ばれました
     🌐 [DEBUG] Template定義完了 - APP_VERSION: 1.1.1
     🌐 [DEBUG] Template.substitute完了 - HTML長: 62813 bytes
     🌐 [DEBUG] <script>タグの数: 3
     ```
   - しかし、JavaScriptのデバッグメッセージ（画面上の赤いdiv）は表示されない

## 15:30ビルドで実施した変更

カスタム確認ダイアログの実装：

1. **HTML構造の追加** (line 1557-1566):
   ```html
   <div id="confirmDialog">
       <div class="confirm-content">
           <div class="confirm-header">お知らせ</div>
           <div class="confirm-body" id="confirmMessage"></div>
           <div class="confirm-footer">
               <button class="confirm-btn confirm-btn-cancel" onclick="closeConfirmDialog(false)">キャンセル</button>
               <button class="confirm-btn confirm-btn-ok" onclick="closeConfirmDialog(true)">OK</button>
           </div>
       </div>
   </div>
   ```

2. **2つ目の`<script>`タグの追加** (line 1568-1585):
   ```javascript
   <script>
       // カスタム確認ダイアログ - グローバルに公開
       var confirmCallback = null;

       window.showConfirmDialog = function(message, callback) {
           document.getElementById('confirmMessage').textContent = message;
           document.getElementById('confirmDialog').style.display = 'block';
           confirmCallback = callback;
       };

       window.closeConfirmDialog = function(result) {
           document.getElementById('confirmDialog').style.display = 'none';
           if (confirmCallback) {
               confirmCallback(result);
               confirmCallback = null;
           }
       };
   </script>
   ```

3. **CSSスタイルの追加** (line 452-513):
   モーダルダイアログのスタイル定義

## HTML生成方法の特徴

`main.py` では、Pythonの `string.Template` を使用してHTML全体を生成しています：

```python
@app.get("/", response_class=HTMLResponse)
async def root():
    """ルートエンドポイント（簡易UIを返す）"""
    logger.info("🌐 [DEBUG] GET / エンドポイントが呼ばれました")
    html_template = Template("""
<!DOCTYPE html>
<html lang="ja">
<head>
    ...
</head>
<body>
    ...
    <script>
        // メインスクリプト（約1000行）
    </script>

    <!-- カスタム確認ダイアログ -->
    <div id="confirmDialog">...</div>

    <script>
        // カスタムダイアログ用スクリプト
    </script>
</body>
</html>
    """)
    logger.info(f"🌐 [DEBUG] Template定義完了 - APP_VERSION: {APP_VERSION}")
    html_content = html_template.substitute(version=APP_VERSION)
    logger.info(f"🌐 [DEBUG] Template.substitute完了 - HTML長: {len(html_content)} bytes")
    logger.info(f"🌐 [DEBUG] <script>タグの数: {html_content.count('<script>')}")
    return HTMLResponse(content=html_content)
```

## 過去の類似問題

2025-10-18にも同様の「JavaScript初期化失敗」問題が発生し、その時の原因は：
- HTML構造の問題（生HTMLの構成エラー）
- スコープ問題

今回はそれと同じパターンの可能性があります。

## 検証済みの事項

1. ✅ `string.Template` で `$version` は正しく置換されている
2. ✅ HTMLテンプレートの構文エラーはない（Pythonのパースは成功）
3. ✅ JavaScript内に `${...}` やバッククォートは使用していない
4. ✅ FastAPIサーバーとpywebviewの通信は確立している
5. ✅ `/health` エンドポイントは応答している
6. ❌ JavaScript内のデバッグコード（alert, console.log, DOM操作）が一切実行されない

## 質問

1. **HTML構造の問題**:
   - Pythonの三重引用符 `"""..."""` 内に複数の `<script>` タグを配置する方法に問題はありますか？
   - `string.Template` の使用が、HTML内のJavaScriptコードに影響を与える可能性はありますか？

2. **pywebviewの制約**:
   - pywebviewのWebKitエンジンが、特定のHTML構造を拒否する可能性はありますか？
   - 2つ目の`<script>`タグの追加が問題を引き起こした可能性はありますか？

3. **デバッグ方法**:
   - pywebview環境でJavaScriptのエラーログを取得する方法はありますか？
   - HTMLが正しくレンダリングされているかを確認する方法はありますか？

4. **推奨される修正方針**:
   - HTML生成方法を変更すべきでしょうか？（f-string, Jinja2など）
   - `<script>`タグの配置場所を変更すべきでしょうか？
   - Pythonの三重引用符内でのHTMLエスケープが必要でしょうか？

## 期待される解決策

- JavaScriptが正常に実行される
- 2つの`<script>`タグが両方とも動作する
- カスタムダイアログ機能が使用できる

## 関連ファイル

- `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/src/main.py` (line 62-1602)
- `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/src/main_app.py` (pywebview Bridge API)

## 環境

- macOS 14.5
- Python 3.12.12
- pywebview (WebKit backend)
- FastAPI
- PyInstaller 6.16.0

---

**緊急度**: 高（アプリケーション全機能が使用不可）
