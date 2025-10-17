# 2025-10-17: pywebview環境の改善実装

## 概要

pywebview環境におけるファイルアップロード、JavaScript初期化、コンソールログ、ドラッグ&ドロップの改善を実施。

**重要**: JavaScript初期化を `initializeApp()` 関数に移動した際、`copyResult()` 関数もグローバルスコープに公開する必要があることが判明し、修正を実施。

## 実装内容

### 1. `/upload` エンドポイントの実装

**ファイル**: [release/mac/src/main.py](../../release/mac/src/main.py#L1140)

**概要**:
- UploadFile を受け取り、UPLOAD_DIR に保存
- file_id と original_name を JSON で返却
- エラー時は適切な HTTP ステータスコード (400/500) を返却

**実装詳細**:
```python
@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """
    音声ファイルをアップロードしてfile_idを返す（pywebview環境用）
    """
    try:
        # ファイル拡張子チェック
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"対応していないファイル形式です: {file_ext}")

        # 一時ファイルとして保存
        file_id = str(uuid.uuid4())
        temp_file = UPLOAD_DIR / f"{file_id}{file_ext}"

        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)

        return JSONResponse(content={
            "file_id": file_id,
            "original_name": file.filename
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ アップロードエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
```

**対応する Bridge メソッド**: [main_app.py](../../release/mac/src/main_app.py#L299) の `upload_audio_file()`

### 2. JavaScript初期化タイミングの調整

**ファイル**: [release/mac/src/main.py](../../release/mac/src/main.py#L490-L1169)

**概要**:
- pywebview環境では `pywebviewready` イベントを待って初期化
- ブラウザ環境では `DOMContentLoaded` で初期化（フォールバック）
- window.pywebview.api の利用可能性を保証

**実装詳細**:
```javascript
function initializeApp() {
    console.log('🚀 initializeApp() 開始');
    console.log('pywebview API available:', !!window.pywebview);

    // DOM要素の取得とイベントリスナーの設定
    // ...
}

// pywebview環境では 'pywebviewready' イベントで初期化
document.addEventListener('pywebviewready', function() {
    console.log('📢 pywebviewready イベント検出');
    initializeApp();
});

// DOMContentLoaded（ブラウザ環境のフォールバック）
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📢 DOMContentLoaded イベント検出（ブラウザ環境）');
        if (!window.pywebview) {
            initializeApp();
        }
    });
} else {
    // すでにDOMが読み込まれている場合
    if (!window.pywebview) {
        initializeApp();
    } else {
        console.log('⏳ pywebviewready を待機中...');
    }
}
```

### 3. コンソールログのブリッジ実装

**ファイル**:
- [release/mac/src/main_app.py:174](../../release/mac/src/main_app.py#L174) - Bridge.log_message()
- [release/mac/src/main_app.py:431](../../release/mac/src/main_app.py#L431) - setup_console_hook()

**概要**:
- Bridge クラスに `log_message(level, message)` メソッドを追加
- Python 側で logger に書き出し
- window.evaluate_js で console.log/error/warn をフック
- JavaScript のログを Python 側に転送

**実装詳細**:

#### Bridge.log_message()
```python
def log_message(self, level: str, message: str):
    """JavaScriptからのログメッセージをPython側に転送"""
    try:
        level = level.lower()
        if level == "info":
            logger.info(f"[JS] {message}")
        elif level == "warning":
            logger.warning(f"[JS] {message}")
        elif level == "error":
            logger.error(f"[JS] {message}")
        elif level == "debug":
            logger.debug(f"[JS] {message}")
        else:
            logger.info(f"[JS] {message}")
        return {"success": True}
    except Exception as e:
        logger.error(f"❌ log_message エラー: {e}", exc_info=True)
        return {"success": False}
```

#### コンソールフック
```python
def setup_console_hook():
    """コンソールログをPython側にブリッジするJSコードを注入"""
    hook_script = """
    (function() {
        var originalLog = console.log;
        var originalError = console.error;
        var originalWarn = console.warn;

        console.log = function() {
            var message = Array.prototype.slice.call(arguments).map(function(arg) {
                return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
            }).join(' ');
            originalLog.apply(console, arguments);
            if (window.pywebview && window.pywebview.api && window.pywebview.api.log_message) {
                window.pywebview.api.log_message('info', message);
            }
        };
        // console.error, console.warn も同様にフック
    })();
    """
    window.evaluate_js(hook_script)
```

### 4. `copyResult()` 関数のグローバル公開 (追加修正)

**ファイル**: [release/mac/src/main.py:919](../../release/mac/src/main.py#L919)

**概要**:
- JavaScript初期化を `initializeApp()` 関数に移動した際、`copyResult()` 関数もローカルスコープに入ってしまった
- HTML の `onclick="copyResult()"` からアクセスできず、`ReferenceError: copyResult is not defined` が発生
- `window.copyResult` としてグローバルスコープに公開することで修正

**修正前の問題**:
```javascript
function initializeApp() {
    // ...
    function copyResult() {  // ローカルスコープ
        navigator.clipboard.writeText(resultText.value).then(...)
    }
}
// HTML: <button onclick="copyResult()"> ← ReferenceError!
```

**修正後**:
```javascript
function initializeApp() {
    // ...
    // copyResult関数をグローバルスコープに公開（onclick属性から呼び出せるようにする）
    window.copyResult = function() {
        var resultTextElement = document.getElementById('resultText');
        if (!resultTextElement) {
            console.error('resultText要素が見つかりません');
            return;
        }
        var text = resultTextElement.textContent;
        navigator.clipboard.writeText(text).then(...)
    };
}
```

**改善点**:
- 要素取得を安全に: `document.getElementById('resultText')` でエラーハンドリング
- `textContent` を使用: `div` 要素なので `value` ではなく `textContent` が正しい

### 5. ドラッグ&ドロップ対応方針

**ファイル**: [release/mac/src/main.py:605](../../release/mac/src/main.py#L605)

**仕様**:
- pywebview環境では `e.dataTransfer.files` からファイルパスを取得できない
- **pywebview環境**: ドロップ時にトースト通知で「クリックして選択してください」と案内
- **ブラウザ環境**: 従来通りドラッグ&ドロップ可能

**実装詳細**:
```javascript
// 【仕様】pywebview環境では e.dataTransfer.files からファイルパスを取得できないため、
// ドラッグ&ドロップは非対応とし、クリック選択を案内する方針とする。
// ブラウザ環境では従来通りドロップ可能。
uploadArea.addEventListener('drop', function(e) {
    preventDefaults(e);
    uploadArea.classList.remove('dragover');

    // pywebview環境かチェック
    if (window.pywebview && window.pywebview.api) {
        // pywebview環境ではドロップ非対応のため案内
        showToast('⚠️ ドラッグ&ドロップは未対応です。クリックしてファイルを選択してください', 4000);
        console.warn('⚠️ pywebview環境ではドラッグ&ドロップは非対応です');
        return;
    }

    // ブラウザ環境では従来通りファイル処理
    var files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    } else {
        showToast('✗ ファイルが選択されていません', 3000);
    }
});
```

## テスト手順

### 1. `/upload` エンドポイントの動作確認

#### テストケース 1: 正常系（音声ファイル）
```bash
# 音声ファイルをアップロード
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@test_audio.mp3"

# 期待する結果: HTTP 200
# {"file_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "original_name": "test_audio.mp3"}
```

#### テストケース 2: エラー系（非対応ファイル）
```bash
# テキストファイルをアップロード
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@test.txt"

# 期待する結果: HTTP 400
# {"detail": "対応していないファイル形式です: .txt"}
```

#### テストケース 3: pywebview環境での統合テスト
1. アプリを起動
2. ファイル選択エリアをクリック
3. ファイル選択ダイアログから音声ファイルを選択
4. Python側のログで以下を確認:
   ```
   📂 ファイル選択: test_audio.mp3 (/path/to/test_audio.mp3)
   📤 アップロード開始: test_audio.mp3 (12345 bytes)
   ファイル保存完了: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.mp3 (12345 bytes)
   ✅ アップロード成功: test_audio.mp3 (file_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
   ```

### 2. JavaScript初期化タイミングの確認

#### pywebview環境
1. アプリを起動
2. Python側のログで以下のシーケンスを確認:
   ```
   [JS] 📢 pywebviewready イベント検出
   [JS] 🚀 initializeApp() 開始
   [JS] pywebview API available: true
   [JS] ✅ initializeApp() 完了 - すべてのイベントリスナー設定完了
   ```

#### ブラウザ環境（開発モード）
1. http://127.0.0.1:8000 にアクセス
2. ブラウザのコンソールで以下を確認:
   ```
   📢 DOMContentLoaded イベント検出（ブラウザ環境）
   🚀 initializeApp() 開始
   pywebview API available: false
   ✅ initializeApp() 完了 - すべてのイベントリスナー設定完了
   ```

### 3. コンソールログブリッジの確認

#### テストケース: JSログがPython側に転送されること
1. アプリを起動
2. ファイル選択やボタンクリックなど、任意の操作を実行
3. Python側のログで `[JS]` プレフィックス付きのログが出力されることを確認:
   ```
   INFO - [JS] GaQ JavaScript starting...
   INFO - [JS] ✅ Console hook installed - JS logs will be forwarded to Python
   INFO - [JS] 📢 pywebviewready イベント検出
   INFO - [JS] 🚀 initializeApp() 開始
   INFO - [JS] pywebview API available: true
   ```

### 4. `/transcribe-stream-by-id` エンドポイントの動作確認

#### テストケース: file_idを使った文字起こし
1. アプリを起動
2. ファイルを選択（file_idが発行される）
3. 「文字起こし開始」ボタンをクリック
4. 以下を確認:
   - プログレスバーがリアルタイムで更新される
   - 文字起こし結果が表示される
   - Python側のログで以下を確認:
     ```
     file_idから文字起こし開始: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, model: medium
     ファイル検出: /path/to/uploads/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.mp3
     ```

### 5. ドラッグ&ドロップの動作確認

#### pywebview環境
1. アプリを起動
2. 音声ファイルをドラッグ&ドロップ
3. トースト通知で「⚠️ ドラッグ&ドロップは未対応です。クリックしてファイルを選択してください」が表示されることを確認
4. Python側のログで以下を確認:
   ```
   WARNING - [JS] ⚠️ pywebview環境ではドラッグ&ドロップは非対応です
   ```

#### ブラウザ環境
1. http://127.0.0.1:8000 にアクセス
2. 音声ファイルをドラッグ&ドロップ
3. ファイルが選択され、「✅ [ファイル名]」が表示されることを確認

## チェックリスト

- [ ] `/upload` エンドポイントが HTTP 200 を返すこと（正常系）
- [ ] `/upload` エンドポイントが HTTP 400 を返すこと（エラー系：非対応ファイル）
- [ ] pywebview環境で `pywebviewready` イベントが発火し、initializeApp() が実行されること
- [ ] window.pywebview.api が利用可能になっていること（pywebview環境）
- [ ] JSのログが Python 側に `[JS]` プレフィックス付きで出力されること
- [ ] `/transcribe-stream-by-id` が成功すること（file_idを使った文字起こし）
- [ ] pywebview環境でドラッグ&ドロップ時にトースト通知が表示されること
- [ ] ブラウザ環境でドラッグ&ドロップが正常に動作すること
- [x] `copyResult()` 関数がグローバルスコープから呼び出せること
- [x] ブラウザ環境で `typeof copyResult` が `"function"` を返すこと
- [x] コピーボタンクリック時に `ReferenceError` が発生しないこと

## 関連ファイル

- [release/mac/src/main.py](../../release/mac/src/main.py)
- [release/mac/src/main_app.py](../../release/mac/src/main_app.py)

## 参考資料

- [pywebview API Events](https://pywebview.flowrl.com/guide/api.html#events)
- [pywebview JavaScript API](https://pywebview.flowrl.com/guide/api.html#javascript-api)
