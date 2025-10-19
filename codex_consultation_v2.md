# Codex緊急相談: pywebview + FastAPI でJavaScriptが完全に実行されない

## 🚨 緊急度: CRITICAL

GaQ Offline Transcriber（pywebview + FastAPI + macOS）において、2025-10-19 15:30以降、**JavaScriptが完全に実行されない**状態が継続しています。複数の修正を試みましたが、依然として解決していません。

---

## 現在の状況

### ✅ 動作している部分
1. FastAPIサーバーは正常起動（`http://127.0.0.1:8000`）
2. `GET /` エンドポイントは正常に呼ばれている
3. HTMLテンプレートは正常に生成されている（64,455 bytes）
4. HTML構造に構文エラーはない（検証済み）
5. Python側のBridge APIは動作（ドラッグ&ドロップハンドラー登録成功）

### ❌ 動作していない部分
1. **JavaScript が一切実行されない**
   - `console.log()` が全く記録されない
   - デバッグ用の `alert()` も表示されない
   - DOMへのデバッグdiv追加も実行されない
   - グローバルエラーハンドラーも動作しない（エラーログなし）
2. すべてのUI機能が無反応（ボタン、ドラッグ&ドロップなど）

---

## タイムライン

### 15:21 - 最後に動作していたセッション
- すべて正常動作
- ログに大量のJavaScriptメッセージ（`[JS]` プレフィックス）
- ドラッグ&ドロップ、文字起こし、すべて機能

### 15:30 - 問題発生（カスタムダイアログ実装）
- 2つ目の`<script>`タグを追加
- 以降、JavaScriptが完全停止

### 15:42-15:55 - 修正試行1
- `showConfirmDialog()` を `window.*` に明示バインド
- 効果なし

### 16:06 - 修正試行2（最新）
- 2つ目の`<script>`タグを削除
- カスタムダイアログ関数をメインスクリプト内の`initializeApp()`定義前に移動
- `deleteModel()` に未定義ガードを追加
- グローバルエラーハンドラー追加
- **依然として効果なし**

---

## 検証済み事項

### HTML生成
```
🌐 [DEBUG] GET / エンドポイントが呼ばれました
🌐 [DEBUG] Template定義完了 - APP_VERSION: 1.1.1
🌐 [DEBUG] Template.substitute完了 - HTML長: 64455 bytes
🌐 [DEBUG] <script>タグの数: 2
🌐 [DEBUG] HTMLを保存しました: /tmp/gaq_debug.html
```

### HTML構造（/tmp/gaq_debug.html）
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>GaQ Offline Transcriber</title>
    <style>...</style>
</head>
<body>
    ...
    <script>
        // デバッグコード（即時実行関数）
        (function() {
            var debugDiv = document.createElement('div');
            debugDiv.id = 'debug-info';
            debugDiv.style.cssText = 'position:fixed;top:0;left:0;background:red;color:white;padding:10px;z-index:99999;';
            debugDiv.textContent = 'DEBUG: JavaScript LOADED! Build: 1.1.1 at ' + new Date().toISOString();
            document.addEventListener('DOMContentLoaded', function() {
                document.body.appendChild(debugDiv);
            });
        })();

        // コンソールフック
        (function() {
            console.log = function() { ... };
            console.error = function() { ... };
            console.log('✅ Console hook installed');
        })();

        // カスタムダイアログAPI
        var confirmCallback = null;
        window.showConfirmDialog = function(message, callback) { ... };
        window.closeConfirmDialog = function(result) { ... };
        console.log('✅ カスタムダイアログAPI登録完了');

        // グローバルエラーハンドラー
        window.addEventListener('error', function(event) {
            console.error('🚨 [Global Error]', event);
        });
        window.addEventListener('unhandledrejection', function(event) {
            console.error('🚨 [Unhandled Rejection]', event);
        });
        console.log('✅ グローバルエラーハンドラー登録完了');

        // initializeApp() 定義とその他1000行以上のコード
        ...
    </script>
</body>
</html>
```

### Python側の確認
```python
# main.py (line 62-1589)
@app.get("/", response_class=HTMLResponse)
async def root():
    logger.info("🌐 [DEBUG] GET / エンドポイントが呼ばれました")
    html_template = Template("""...""")
    html_content = html_template.substitute(version=APP_VERSION)

    # デバッグ用保存
    with open("/tmp/gaq_debug.html", 'w', encoding='utf-8') as f:
        f.write(html_content)

    return HTMLResponse(content=html_content)
```

### ブラウザでの検証
`/tmp/gaq_debug.html` をSafariで開いた場合の動作は**未確認**です（pywebview環境でのみ発生する問題の可能性）。

---

## 最も奇妙な点

1. **HTMLは正しく配信されている**（ログ証拠あり）
2. **構文エラーはない**（Pythonで生成成功、HTMLバリデーション通過）
3. **グローバルエラーハンドラーすら動作しない**（= スクリプトタグ自体が評価されていない？）
4. **Python側のpywebview初期化は成功**（`[DragDrop] JavaScript通知完了`ログあり）

---

## pywebview特有の問題の可能性

### main_app.py の構造
```python
# main_app.py
import webview

class Bridge:
    def log_message(self, level, message):
        logger.info(f"[JS] {message}")

    def select_audio_file(self):
        result = window.create_file_dialog(webview.OPEN_DIALOG, ...)
        return result

    # ...その他のメソッド

def start_app():
    # FastAPIサーバーをバックグラウンドで起動
    uvicorn_thread = threading.Thread(target=run_fastapi, daemon=True)
    uvicorn_thread.start()

    # pywebviewウィンドウ作成
    window = webview.create_window(
        'GaQ Offline Transcriber',
        'http://127.0.0.1:8000',
        js_api=Bridge()
    )

    # ドラッグ&ドロップハンドラー登録（Python側）
    window.events.shown += lambda: register_drag_handler(window)

    webview.start()
```

### 動作していた15:21セッションとの唯一の違い
- **HTML構造が変更された**（2つ目の`<script>`タグ追加 → 削除）
- それ以外の環境は完全に同一

---

## 質問

### 1. pywebview/WebKitの制約
- pywebviewのWebKitエンジンは、特定のHTML構造やJavaScriptパターンを拒否しますか？
- `string.Template` で生成したHTMLに、pywebviewが解釈できない要素がある可能性は？
- pywebviewは、特定のサイズ（64KB）を超えるHTMLやJavaScriptをブロックしますか？

### 2. JavaScript実行の前提条件
- pywebviewで**JavaScriptが全く実行されない**状況は、何が原因で起こりますか？
  - CSP（Content Security Policy）の問題？
  - MIMEタイプの問題？
  - Encoding の問題？
  - HTML構造の問題？

### 3. デバッグ方法
- pywebview環境で、**WebKitのコンソール出力を取得する方法**はありますか？
- `webview.create_window(debug=True)` のようなオプションは有効ですか？
- macOSのWebKit Inspectorをpywebviewアプリに接続する方法はありますか？

### 4. HTMLResponse の問題可能性
- FastAPIの `HTMLResponse` は正しく使えていますか？
- `Content-Type` ヘッダーを明示的に設定する必要がありますか？
  ```python
  return HTMLResponse(
      content=html_content,
      media_type="text/html; charset=utf-8"
  )
  ```

### 5. 同じHTMLがブラウザでは動作するか？
`/tmp/gaq_debug.html` をブラウザで開いた際に：
- JavaScriptは実行されますか？
- 赤いデバッグメッセージは表示されますか？
- コンソールにエラーは出ますか？

**この検証を推奨します。もしブラウザで動作すれば、pywebview固有の問題であることが確定します。**

---

## 試すべき次の手段

### オプションA: HTML生成方法の完全変更
```python
# f-string または Jinja2 に変更
from jinja2 import Template

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r") as f:
        template = Template(f.read())
    html_content = template.render(version=APP_VERSION)
    return HTMLResponse(content=html_content)
```

### オプションB: 極小HTMLでの検証
```python
@app.get("/test", response_class=HTMLResponse)
async def test():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body>
        <h1>Test</h1>
        <script>
            alert('JavaScript works!');
            console.log('Console works!');
        </script>
    </body>
    </html>
    """)
```

この `/test` エンドポイントで `window = webview.create_window('Test', 'http://127.0.0.1:8000/test')` を試す。

### オプションC: pywebview debugモードの有効化
```python
webview.start(debug=True)  # WebKit Inspector有効化
```

### オプションD: 別のバックエンドで検証
```python
# Gtk/Qt バックエンドで試す（macOSでは難しいが）
webview.start(gui='qt')
```

---

## 環境詳細

- **OS**: macOS 14.5 (Sonoma)
- **Python**: 3.12.12
- **pywebview**: `webview.__version__` 要確認（おそらく4.x）
- **FastAPI**: 最新
- **PyInstaller**: 6.16.0
- **WebKitバックエンド**: macOS標準（Cocoa）

---

## 添付ファイル

1. **/tmp/gaq_debug.html** - 実際に生成されたHTML（64,455 bytes）
2. **~/.gaq/logs/app.log** - 最新100行
3. **release/mac/src/main.py** (line 62-1602) - HTML生成コード
4. **release/mac/src/main_app.py** - pywebview初期化コード

---

## 期待される解決策

1. JavaScriptが実行される
2. `console.log()` がPythonログに転送される
3. 全UI機能が復旧する

---

## 重要な補足

**15:21のセッションでは完全に動作していた**という事実が、最も重要な手がかりです。環境やライブラリは全く同じで、**HTMLの構造のみが変更された**ことで問題が発生しています。

おそらく以下のいずれかです：
1. pywebviewが特定のHTML構造をブロックしている
2. 生成されたHTMLに、人間には見えない制御文字やエンコーディング問題がある
3. FastAPIのレスポンス生成プロセスに問題がある
4. pywebviewのキャッシュ問題（可能性は低い - 複数回インストールしても同じ）

緊急のご支援をお願いいたします。
