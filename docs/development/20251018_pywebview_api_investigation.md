# 2025-10-18: pywebview API注入問題の調査レポート

**日付**: 2025-10-18
**担当**: Claude Code
**ステータス**: 🚨 重大な問題未解決 - Codexへエスカレーション

---

## 📋 問題概要

Mac版v1.1.1において、pywebview環境でのJavaScript初期化とBridge API注入が完全に失敗しています。

### 主要な症状

1. **ファイル選択エリアをクリックしてもダイアログが表示されない**
2. **モデル管理ボタンが反応しない**
3. **ドラッグ&ドロップが機能しない**
4. **JavaScriptのログがPython側に一切届いていない**

---

## 🔍 実施した調査内容

### 1. ログ出力の確認

**起動時のログ**:
```
2025-10-18 14:01:02,700 - __main__ - INFO - === GaQ Offline Transcriber v1.1.1 起動 ===
2025-10-18 14:01:02,700 - __main__ - INFO - ✅ 単一インスタンスロック取得成功 (PID: 5039)
2025-10-18 14:01:03,596 - __main__ - INFO - 🚀 FastAPIサーバー起動: http://127.0.0.1:8000
2025-10-18 14:01:03,718 - __main__ - INFO - ✅ FastAPIサーバー起動確認: http://127.0.0.1:8000/health
2025-10-18 14:01:03,719 - __main__ - INFO - 🖥️ Webviewウィンドウ起動: http://127.0.0.1:8000
```

**ファイル選択エリアをクリックした後**:
- **ログに変化なし**
- `[JS]` プレフィックス付きログが一切出力されない
- `🔔 [Bridge] select_audio_file() が呼び出されました` も出力されない

**結論**: JavaScriptは実行されているが、`window.pywebview.api`が利用できないため、ログがPythonに転送されていない。

---

### 2. Safari Web Inspectorでの確認

**結果**:
- Safari → 開発メニューに **GaQ Offline Transcriber** が表示されない
- pywebviewウィンドウがSafariのリモートデバッグ対象として認識されていない

**考えられる原因**:
- pywebviewのWebKit実装が、Safariのリモートデバッグを許可していない
- `debug=False`でwebview.start()しているため、デバッグが無効化されている可能性

---

## 🔧 実施した修正内容

### 修正1: `safeInitialize()`のフラグ制御改善

**ファイル**: [release/mac/src/main.py:1228-1244](../../release/mac/src/main.py#L1228-L1244)

```javascript
function safeInitialize(source) {
    if (appInitialized) return;

    triggerInitializeApp(source);

    // ★initializeApp()の成功を確認してからフラグを立てる
    if (window.__appInitialized) {
        appInitialized = true;
        console.log('✅ safeInitialize() 完了');
    } else {
        console.error('❌ initializeApp() 失敗 - 再試行可能');
    }
}
```

**効果**: 初期化失敗時の再試行が可能になった（理論上）

---

### 修正2: タイムアウトを1秒に短縮

**ファイル**: [release/mac/src/main.py:1259-1277](../../release/mac/src/main.py#L1259-L1277)

**変更前**: 2秒/5秒
**変更後**: 1秒/3秒

---

### 修正3: コンソールフックを`<script>`タグ内に直接埋め込み

**ファイル**: [release/mac/src/main.py:491-538](../../release/mac/src/main.py#L491-L538)

**変更前**: `main_app.py`の`window.events.loaded`でフックを注入
**変更後**: `<script>`タグの**最初**にフックコードを直接埋め込み

```javascript
<script>
    // ★コンソールフックを最優先で設定
    (function() {
        console.log = function() {
            var message = /* ... */;
            originalLog.apply(console, arguments);

            if (window.pywebview && window.pywebview.api && window.pywebview.api.log_message) {
                window.pywebview.api.log_message('info', message);
            }
        };
        // ...
    })();
</script>
```

**期待した効果**: すべてのJavaScriptログがPythonに転送される
**実際の結果**: ログが一切転送されていない → `window.pywebview.api`が利用不可

---

### 修正4: Bridgeメソッドにログ追加

**ファイル**: [release/mac/src/main_app.py](../../release/mac/src/main_app.py)

```python
def select_audio_file(self):
    logger.info("🔔 [Bridge] select_audio_file() が呼び出されました")
    # ...

def upload_audio_file(self, file_path):
    logger.info(f"🔔 [Bridge] upload_audio_file() が呼び出されました - file_path: {file_path}")
    # ...
```

**結果**: これらのログが一切出力されていない → Bridgeメソッドが呼ばれていない

---

### 修正5: JavaScript側でpywebviewの詳細情報をログ出力

**ファイル**: [release/mac/src/main.py:540-546](../../release/mac/src/main.py#L540-L546)

```javascript
console.log('===== GaQ JavaScript starting =====');
console.log('document.readyState:', document.readyState);
console.log('window.pywebview exists:', !!window.pywebview);
console.log('window.pywebview:', window.pywebview);
console.log('window.pywebview.api:', window.pywebview ? window.pywebview.api : 'N/A');
console.log('window.pywebview.api.select_audio_file:', window.pywebview && window.pywebview.api ? window.pywebview.api.select_audio_file : 'N/A');
```

**結果**: これらのログもPythonログに出力されていない

---

### 修正6: ログファイル出力の設定

**ファイル**: [release/mac/src/main_app.py:29-43](../../release/mac/src/main_app.py#L29-L43)

```python
# ログディレクトリ
LOG_DIR = Path.home() / ".gaq" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

# ログ設定（ファイルとコンソールの両方に出力）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

**結果**: `~/.gaq/logs/app.log`に正常にログが出力されるようになった

---

## 🚨 根本的な問題

### 問題の核心: `window.pywebview.api`が利用不可

**証拠**:
1. JavaScriptログが一切Pythonログに転送されていない
2. Bridgeメソッド（`select_audio_file`等）が一切呼ばれていない
3. コンソールフック内の以下の条件が常に`false`：
   ```javascript
   if (window.pywebview && window.pywebview.api && window.pywebview.api.log_message) {
       // ここが実行されていない
   }
   ```

**考えられる原因**:

#### 仮説1: Bridge APIの注入タイミング問題
- `webview.create_window(..., js_api=bridge)`でBridgeを登録しているが、注入が遅れている
- `<script>`タグが実行される時点では、まだ`window.pywebview.api`が利用できない
- `pywebviewready`イベントが発火していない可能性

#### 仮説2: pywebviewのバージョン/実装問題
- pywebviewのWebKit実装に制約がある
- macOS環境特有の問題
- Bridge APIの注入メカニズム自体が機能していない

#### 仮説3: セキュリティ制約
- macOSのセキュリティ設定がJavaScript-Python間の通信をブロック
- Content Security Policy (CSP) の制約
- WebKitのサンドボックス制約

---

## 🔬 未実施の調査項目

### 1. Safari Web Inspectorでのデバッグ

**問題**: Safari → 開発メニューに「GaQ Offline Transcriber」が表示されない

**対策案**:
- `webview.start(debug=True)`に変更して再起動
- pywebviewのドキュメントでリモートデバッグの有効化方法を確認

### 2. `window.pywebview`の直接確認

**現状**: コンソールフックが機能していないため、`window.pywebview`の存在を確認できていない

**対策案**:
- `alert()`や`document.title`を使ってデバッグ情報を表示
- HTMLに直接デバッグ情報を書き出す

```javascript
// 例
document.body.innerHTML += '<div style="position:fixed;top:0;left:0;background:red;color:white;z-index:9999;">' +
    'pywebview: ' + (!!window.pywebview) + '<br>' +
    'api: ' + (window.pywebview ? !!window.pywebview.api : 'N/A') +
    '</div>';
```

### 3. pywebviewreadyイベントの発火確認

**現状**: `pywebviewready`イベントリスナーは登録しているが、発火しているか不明

**対策案**:
- `alert()`を使って発火を確認
- HTMLへのデバッグ情報書き込み

---

## 📊 現在のファイル状態

### 変更されたファイル

1. **release/mac/src/main.py**
   - コンソールフックを`<script>`内に埋め込み
   - `safeInitialize()`のフラグ制御改善
   - タイムアウト短縮（1秒/3秒）
   - pywebview詳細情報のログ追加

2. **release/mac/src/main_app.py**
   - Bridgeメソッドにログ追加
   - ログファイル出力設定追加

### git status

```
modified:   release/mac/src/main.py
modified:   release/mac/src/main_app.py
```

---

## 🎯 Codexへの依頼事項

### 最優先: `window.pywebview.api`が利用できない原因の特定

以下のいずれかの方法で原因を特定してください：

#### 方法1: alertを使ったデバッグ

`main.py`の`<script>`タグに以下を追加：

```javascript
alert('pywebview: ' + (!!window.pywebview) + '\n' +
      'api: ' + (window.pywebview ? !!window.pywebview.api : 'N/A'));
```

#### 方法2: HTMLへのデバッグ情報書き込み

```javascript
setTimeout(function() {
    var debugDiv = document.createElement('div');
    debugDiv.style.cssText = 'position:fixed;top:0;left:0;background:red;color:white;padding:10px;z-index:9999;';
    debugDiv.innerHTML =
        'pywebview exists: ' + (!!window.pywebview) + '<br>' +
        'pywebview.api exists: ' + (window.pywebview ? !!window.pywebview.api : 'N/A') + '<br>' +
        '__appInitialized: ' + window.__appInitialized;
    document.body.appendChild(debugDiv);
}, 2000);
```

#### 方法3: pywebviewのデバッグモード有効化

`main_app.py`の`webview.start()`を以下に変更：

```python
webview.start(debug=True)
```

これにより、Safari Web Inspectorでデバッグ可能になる可能性があります。

---

### 第2優先: Bridge API注入の確認

**現状の実装** ([main_app.py:425-434](../../release/mac/src/main_app.py#L425-L434)):

```python
window = webview.create_window(
    title=f"GaQ Offline Transcriber {APP_VERSION}",
    url=url,
    width=800,
    height=900,
    resizable=True,
    frameless=False,
    easy_drag=True,
    js_api=bridge,  # ←Bridgeを登録
)
```

**確認項目**:
- `js_api=bridge`が正しく機能しているか
- `pywebviewready`イベントが発火するか
- Bridge APIの注入タイミング

**対策案**:
- `window.events.loaded`ハンドラ内で`window.pywebview.api`の存在を確認
- `window.evaluate_js()`で直接`window.pywebview`を確認

```python
def check_pywebview_api():
    try:
        result = window.evaluate_js('JSON.stringify({pywebview: !!window.pywebview, api: !!(window.pywebview && window.pywebview.api)})')
        logger.info(f"🔍 pywebview状態: {result}")
    except Exception as e:
        logger.error(f"❌ pywebview確認エラー: {e}")

window.events.loaded += check_pywebview_api
```

---

### 第3優先: 代替デバッグ方法の検討

Safari Web Inspectorが使えない場合の代替案：

#### 案1: ログを画面に表示

```javascript
function debugLog(msg) {
    var debugDiv = document.getElementById('debug-log');
    if (!debugDiv) {
        debugDiv = document.createElement('div');
        debugDiv.id = 'debug-log';
        debugDiv.style.cssText = 'position:fixed;bottom:0;left:0;width:100%;background:black;color:lime;font-size:10px;padding:5px;max-height:200px;overflow-y:auto;z-index:9999;';
        document.body.appendChild(debugDiv);
    }
    debugDiv.innerHTML += msg + '<br>';
}

// 使用例
debugLog('JavaScript started');
debugLog('pywebview: ' + (!!window.pywebview));
```

#### 案2: FastAPI経由でログ送信

```javascript
fetch('/log', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: 'pywebview exists: ' + (!!window.pywebview),
        timestamp: new Date().toISOString()
    })
});
```

FastAPI側に`/log`エンドポイントを追加：

```python
@app.post("/log")
async def client_log(data: dict):
    logger.info(f"📱 [CLIENT] {data.get('message')}")
    return {"success": True}
```

---

## 📝 次回作業の推奨手順

1. **`webview.start(debug=True)`に変更**
2. **alertまたはHTMLデバッグ情報でpywebviewの状態確認**
3. **`window.events.loaded`ハンドラで`window.pywebview.api`を確認**
4. **FastAPI経由のログエンドポイント追加**
5. **原因特定後、適切な修正を実施**

---

## 🔗 関連ファイル

- [release/mac/src/main.py](../../release/mac/src/main.py)
- [release/mac/src/main_app.py](../../release/mac/src/main_app.py)
- [docs/development/20251018_javascript_initialization_fix.md](20251018_javascript_initialization_fix.md)

---

## 📋 まとめ

### 完了した修正
- ✅ `safeInitialize()`のフラグ制御改善
- ✅ タイムアウト短縮（1秒/3秒）
- ✅ コンソールフックを`<script>`内に埋め込み
- ✅ Bridgeメソッドにログ追加
- ✅ JavaScript側でpywebview詳細情報のログ追加
- ✅ ログファイル出力設定追加

### 未解決の問題
- ❌ `window.pywebview.api`が利用できない
- ❌ JavaScriptログがPythonに転送されない
- ❌ Bridgeメソッドが呼ばれない
- ❌ Safari Web Inspectorでデバッグできない

### 次のアクション
- 🔜 `window.pywebview`の存在確認（alert/HTMLデバッグ）
- 🔜 `webview.start(debug=True)`でデバッグモード有効化
- 🔜 Bridge API注入の確認
- 🔜 代替デバッグ方法の実装

---

**結論**: JavaScript初期化ロジックは大幅に改善されたが、**pywebview Bridge APIの注入自体が失敗している**可能性が高い。根本原因の特定には、`window.pywebview`の直接確認が必須。
