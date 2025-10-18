# Codex作業プロンプト: Mac版ドラッグ&ドロップ機能の実装

## 作業概要

Mac版GaQ Offline Transcriber v1.1.1において、pywebview環境でのドラッグ&ドロップ機能が動作していません。Python側のDOM dropハンドラーが全く呼ばれず、ファイルのドロップが受け付けられない状態です。

## 現在の症状

### 実際の動作

1. ユーザーが音声ファイルをアプリのファイル選択エリアにドラッグ&ドロップ
2. JavaScript側で `🎯 pywebview環境: Python側でドロップ処理中...` のログが出力
3. **Python側のログが一切出ない**（`📥 [DragDrop] ドロップイベント発生` が出ない）
4. 処理が停止し、ファイルが選択されない

### 期待される動作

1. ユーザーが音声ファイルをドラッグ&ドロップ
2. JavaScript側: `🎯 pywebview環境: Python側でドロップ処理中...`
3. **Python側: `📥 [DragDrop] ドロップイベント発生`**（← これが出ない）
4. Python側: `📂 [DragDrop] ファイルドロップ: test.m4a (/Users/.../test.m4a)`
5. Python側: `✅ [DragDrop] JavaScript通知完了: test.m4a`
6. JavaScript側: `📥 pywebviewFileDrop イベント受信`
7. ファイルアップロード処理が開始される

### 実際のログ出力

```
2025-10-18 16:42:11,802 - __main__ - INFO - ✅ [DragDrop] ドロップイベントハンドラー登録完了（dragover + drop）
...（起動処理）...
2025-10-18 16:42:58,989 - __main__ - INFO - [JS] 🎯 pywebview環境: Python側でドロップ処理中...
```

**重要**: Python側の `📥 [DragDrop] ドロップイベント発生` が全く出ていない

## 技術的背景

### 環境情報

- **OS**: macOS 14.8 (arm64)
- **Python**: 3.12.3
- **pywebview**: 6.0
- **PyInstaller**: 6.16.0
- **Backend**: Cocoa (macOS native)
- **アプリ**: PyInstallerでビルドされたスタンドアロンアプリ

### アーキテクチャ設計

```
[ユーザー操作: ファイルドロップ]
        ↓
[Browser DOM: drop event]
        ↓
    ┌───────────────────────────────────┐
    │ JavaScript層                       │
    │ - uploadArea.addEventListener()   │
    │ - pywebview環境チェック            │
    │ - preventDefaultsを呼ばない（重要）│
    └───────────────────────────────────┘
        ↓（イベント伝播）
    ┌───────────────────────────────────┐
    │ Python DOM API層                   │
    │ - window.dom.document.events.drop │
    │ - DOMEventHandler(on_drop)        │
    │ - prevent_default=True            │
    └───────────────────────────────────┘
        ↓
    ┌───────────────────────────────────┐
    │ Python処理                         │
    │ - pywebviewFullPathを取得          │
    │ - CustomEvent発火                 │
    └───────────────────────────────────┘
        ↓
    ┌───────────────────────────────────┐
    │ JavaScript層                       │
    │ - pywebviewFileDropイベント受信    │
    │ - uploadFileViaPywebview()        │
    └───────────────────────────────────┘
```

### 実装ファイル

#### 1. release/mac/src/main_app.py（Python側）

**ハンドラー登録部分**（行631-701）:

```python
def setup_drag_drop_handler():
    """
    pywebview DOM APIを使ってドラッグ&ドロップイベントを登録
    """
    try:
        from webview.dom import DOMEventHandler

        def on_drop(e):
            """
            ドロップイベントハンドラー
            pywebviewFullPathを取得してJavaScriptに通知
            """
            try:
                logger.info("📥 [DragDrop] ドロップイベント発生")  # ← このログが出ない
                files = e.get('dataTransfer', {}).get('files', [])

                if not files:
                    logger.warning("⚠️ [DragDrop] ドロップされたファイルがありません")
                    return

                # 最初のファイルのパスを取得
                first_file = files[0]
                file_path = first_file.get('pywebviewFullPath')
                file_name = first_file.get('name', 'unknown')

                logger.info(f"📂 [DragDrop] ファイルドロップ: {file_name} ({file_path})")

                if not file_path:
                    logger.error("❌ [DragDrop] pywebviewFullPathが取得できませんでした")
                    return

                # JavaScriptにファイルパスを通知
                js_code = f'''
                (function() {{
                    window.__droppedFilePath = {json.dumps(file_path)};
                    window.__droppedFileName = {json.dumps(file_name)};
                    var event = new CustomEvent('pywebviewFileDrop', {{
                        detail: {{
                            path: {json.dumps(file_path)},
                            name: {json.dumps(file_name)}
                        }}
                    }});
                    window.dispatchEvent(event);
                    console.log('🎯 [DragDrop] pywebviewFileDrop イベント発火:', {json.dumps(file_name)});
                }})();
                '''
                window.evaluate_js(js_code)
                logger.info(f"✅ [DragDrop] JavaScript通知完了: {file_name}")

            except Exception as ex:
                logger.error(f"❌ [DragDrop] ドロップ処理エラー: {ex}", exc_info=True)

        # dragoverイベントのハンドラー（dropを許可するために必須）
        def on_dragover(e):
            """
            dragoverイベントでprevent_defaultしないとdropイベントが発火しない
            """
            # ログは大量になるので出力しない
            pass

        # dragoverとdropイベントにハンドラーを登録
        # dragoverでpreventDefaultしないとdropイベントが発火しない
        window.dom.document.events.dragover += DOMEventHandler(on_dragover, prevent_default=True, stop_propagation=False)
        window.dom.document.events.drop += DOMEventHandler(on_drop, prevent_default=True, stop_propagation=True)

        logger.info("✅ [DragDrop] ドロップイベントハンドラー登録完了（dragover + drop）")

    except Exception as e:
        logger.error(f"❌ [DragDrop] ハンドラー登録エラー: {e}", exc_info=True)

# loadedイベント後にドラッグ&ドロップハンドラーを設定
window.events.loaded += setup_drag_drop_handler
```

**起動ログ確認**:
```
2025-10-18 16:42:11,802 - __main__ - INFO - ✅ [DragDrop] ドロップイベントハンドラー登録完了（dragover + drop）
```
→ ハンドラー登録自体は成功している

#### 2. release/mac/src/main.py（JavaScript側）

**dragoverイベント**（行674-681）:

```javascript
// ドラッグオーバー時の処理
uploadArea.addEventListener('dragover', function(e) {
    // pywebview環境ではPython側のDOM dragoverハンドラーに任せる
    if (!(window.pywebview && window.pywebview.api)) {
        // ブラウザ環境のみpreventDefaultsを呼ぶ
        preventDefaults(e);
    }
    uploadArea.classList.add('dragover');
});
```

**dropイベント**（行689-711）:

```javascript
uploadArea.addEventListener('drop', function(e) {
    // pywebview環境かチェック
    if (window.pywebview && window.pywebview.api) {
        // pywebview環境ではPython側のDOM dropハンドラーに完全に任せる
        // preventDefaults()を呼ばずに即座にreturn
        // （Python側でpreventDefault=Trueが設定されている）
        console.log('🎯 pywebview環境: Python側でドロップ処理中...');
        uploadArea.classList.remove('dragover');
        return;  // ← preventDefaults()を呼ばずにreturn
    }

    // ブラウザ環境では従来通りpreventDefaultsを呼ぶ
    preventDefaults(e);
    uploadArea.classList.remove('dragover');

    // ブラウザ環境では従来通りファイル処理
    var files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    } else {
        showToast('✗ ファイルが選択されていません', 3000);
    }
});
```

**pywebviewFileDropカスタムイベントリスナー**（行724-740）:

```javascript
window.addEventListener('pywebviewFileDrop', function(e) {
    console.log('📥 pywebviewFileDrop イベント受信:', e.detail);
    var filePath = e.detail.path;
    var fileName = e.detail.name;

    if (!filePath) {
        console.error('❌ ファイルパスが取得できませんでした');
        showToast('✗ ファイルパスが取得できませんでした', 3000);
        return;
    }

    console.log('📂 ドロップされたファイル:', fileName, '(' + filePath + ')');

    // pywebview経由でファイルをアップロード
    uploadFileViaPywebview(filePath, fileName);
});
```

## これまでの試行錯誤

### 試行1: 初期実装

**内容**: Python側のDOM dropハンドラーのみ実装
**結果**: ❌ Python側のログが出ない
**原因仮説**: dragoverでpreventDefault()していないためdropが発火しない

### 試行2: dragoverハンドラー追加

**内容**: Python側にdragoverハンドラーを追加（prevent_default=True）
**結果**: ❌ 変化なし。Python側のログが出ない
**原因仮説**: JavaScript側のpreventDefault()がPython側をブロックしている

### 試行3: JavaScript側のpreventDefault()を削除

**内容**:
- dragoverイベント: pywebview環境ではpreventDefault()を呼ばない
- dropイベント: pywebview環境ではpreventDefault()を呼ばない

**結果**: ❌ 依然としてPython側のログが出ない（現在の状態）

**ログ**:
```
2025-10-18 16:42:58,989 - __main__ - INFO - [JS] 🎯 pywebview環境: Python側でドロップ処理中...
```
→ JavaScript側は動作しているが、Python側が全く反応しない

## 問題の核心

### 仮説1: イベントリスナーの優先順位

JavaScript側の `uploadArea.addEventListener('drop', ...)` が、Python側の `window.dom.document.events.drop` よりも先に実行され、イベント伝播をブロックしている可能性。

**検証方法**:
- JavaScript側のdropイベントリスナーを完全に削除
- または、uploadArea要素ではなくdocument全体でリスナーを登録

### 仮説2: pywebview DOM APIの制約

pywebview 6.0のDOM APIが、特定の要素（`#uploadArea`）に対するイベントを正しくキャプチャできない可能性。

**検証方法**:
- `window.dom.document.events.drop` ではなく、特定要素のイベントを登録する方法を調査
- pywebview 6.0のドキュメントやサンプルコードを確認

### 仮説3: イベントバブリングの問題

`uploadArea` 要素でイベントがキャプチャされ、documentレベルまで伝播していない可能性。

**検証方法**:
- JavaScript側で `e.stopPropagation()` を呼んでいないか確認（現在は呼んでいない）
- イベントキャプチャフェーズで処理する

### 仮説4: pywebviewのバグまたは未実装機能

pywebview 6.0のCocoa backendで、DOM dropイベントが正しく動作しない可能性。

**検証方法**:
- pywebview GitHubのissuesを確認
- 簡単なテストケースを作成して検証
- 別のイベント（click等）で動作確認

## Codexへの作業依頼

### 目的

Mac版GaQ Offline Transcriber v1.1.1において、pywebview環境でドラッグ&ドロップ機能を動作させる。

### 作業内容

1. **原因特定**:
   - なぜPython側のDOM dropハンドラー（`on_drop`関数）が呼ばれないのかを特定する
   - pywebview 6.0のDOM API仕様を確認
   - イベント伝播の問題を調査

2. **解決策の実装**:
   - 以下のいずれかのアプローチで実装
     - **アプローチA**: JavaScript側のdropイベントリスナーを削除し、Python側のみで処理
     - **アプローチB**: pywebview DOM APIの使い方を修正（要素レベルでのイベント登録など）
     - **アプローチC**: 代替手段（drag & drop以外のファイル受け渡し方法）を検討
     - **アプローチD**: pywebviewのバグ回避策を実装

3. **動作確認**:
   - ビルド後、実際にファイルをドラッグ&ドロップして動作確認
   - 以下のログが出ることを確認:
     ```
     📥 [DragDrop] ドロップイベント発生
     📂 [DragDrop] ファイルドロップ: test.m4a (/Users/.../test.m4a)
     ✅ [DragDrop] JavaScript通知完了: test.m4a
     ```

4. **ドキュメント更新**:
   - 実装方法と原因を `docs/development/20251018_drag_drop_investigation.md` に記録
   - トラブルシューティング情報を追加

### 制約条件

- **既存機能を壊さない**: クリックによるファイル選択は引き続き動作すること
- **ブラウザ環境との互換性**: 開発時（ブラウザで直接開く）でも動作すること
- **Mac版のみ対応**: Windows版は将来対応（現時点では考慮不要）
- **PyInstallerビルド**: スタンドアロンアプリとして動作すること

### 参考情報

#### pywebview 6.0 DOM API ドキュメント

- URL: https://pywebview.flowrl.com/6.0/guide/dom.html
- 重要セクション:
  - DOM Events
  - Event Handlers
  - File Drop Support

#### 関連ファイル

- **Python側**: `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/src/main_app.py`（行631-701）
- **JavaScript側**: `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/src/main.py`（行674-681, 689-711, 724-740）
- **ビルドスクリプト**: `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/build.sh`

#### テスト手順

```bash
# ビルド
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac
bash build.sh

# アプリ起動
open "dist/GaQ Offline Transcriber.app"

# ログ監視
tail -f ~/.gaq/logs/app.log

# ドラッグ&ドロップテスト
# 1. Finderから音声ファイル（mp3, m4a, wav）を選択
# 2. アプリのファイル選択エリアにドロップ
# 3. ログで以下を確認:
#    - 📥 [DragDrop] ドロップイベント発生
#    - 📂 [DragDrop] ファイルドロップ: xxx.m4a
#    - ✅ [DragDrop] JavaScript通知完了
```

### デバッグヒント

#### 1. Python側のログを追加

`on_drop` 関数の先頭に以下を追加して、関数が呼ばれているか確認:

```python
def on_drop(e):
    logger.info("🔥 [DEBUG] on_drop関数が呼ばれました！")  # 最優先ログ
    logger.info(f"🔥 [DEBUG] イベントオブジェクト: {type(e)}")
    logger.info(f"🔥 [DEBUG] イベント内容: {e}")
    # ...既存コード...
```

#### 2. dragoverのログを追加

`on_dragover` 関数でもログを出力:

```python
def on_dragover(e):
    logger.info("🔥 [DEBUG] on_dragover関数が呼ばれました！")
```

#### 3. JavaScript側のイベントリスナーを削除

一時的に `uploadArea.addEventListener('drop', ...)` をコメントアウトして、Python側のみで処理できるか確認:

```javascript
// uploadArea.addEventListener('drop', function(e) { ... });  // コメントアウト
```

#### 4. document全体でリスナー登録

uploadArea要素ではなく、document全体でPython側のハンドラーを登録:

```python
# window.dom.document.events.drop の代わりに
# window.dom.body.events.drop または
# window.dom.getElementById('uploadArea').events.drop を試す
```

#### 5. pywebview DOM APIの動作確認

簡単なclickイベントで動作確認:

```python
def on_click(e):
    logger.info("✅ [DEBUG] クリックイベントが動作しています！")

window.dom.document.events.click += DOMEventHandler(on_click)
```

### 成功基準

以下のすべてが満たされること:

1. ✅ ファイルをドラッグ&ドロップすると、Python側のログ `📥 [DragDrop] ドロップイベント発生` が出力される
2. ✅ ファイルパスが正しく取得され、`📂 [DragDrop] ファイルドロップ: xxx.m4a (/path/to/file)` が出力される
3. ✅ JavaScriptにCustomEventが発火され、`📥 pywebviewFileDrop イベント受信` が出力される
4. ✅ ファイルがアップロードされ、文字起こし可能状態になる
5. ✅ クリックによるファイル選択も引き続き動作する
6. ✅ ブラウザ環境（開発時）でも正常に動作する

### 失敗パターンと対処

#### パターン1: Python側のログが全く出ない（現在の状態）

**対処**: JavaScript側のイベントリスナーを削除、またはイベント伝播を許可

#### パターン2: `on_drop`が呼ばれるが、`files`が空

**対処**: イベントオブジェクトの構造を確認、`pywebviewFullPath` の取得方法を修正

#### パターン3: ファイルパスは取得できるが、CustomEventが発火しない

**対処**: `window.evaluate_js()` のタイミングやスコープを確認

#### パターン4: pywebview DOM APIが動作しない

**対処**: 代替手段として、JavaScript側で `window.pywebview.api.custom_method()` を呼び出してファイルパスを渡す方法を検討

### 代替案（DOM APIが動作しない場合）

もしpywebview DOM APIでのdropイベントハンドリングが不可能な場合、以下の代替手段を検討:

#### 代替案A: データURLでファイルを送信

```javascript
uploadArea.addEventListener('drop', function(e) {
    if (window.pywebview && window.pywebview.api) {
        preventDefaults(e);
        var files = e.dataTransfer.files;
        if (files.length > 0) {
            var reader = new FileReader();
            reader.onload = function(event) {
                var base64Data = event.target.result;
                window.pywebview.api.upload_file_from_dataurl(base64Data, files[0].name);
            };
            reader.readAsDataURL(files[0]);
        }
    }
});
```

**欠点**: 大きなファイルでメモリ消費が増加

#### 代替案B: ドラッグ&ドロップを諦める

ドラッグ&ドロップは非対応とし、クリック選択のみにする（元の仕様）。

---

## まとめ

**現在の問題**: Python側のDOM dropハンドラーが全く呼ばれない

**目標**: ドラッグ&ドロップでファイルを受け付け、文字起こし可能にする

**Codexへの依頼**: 原因特定と解決策の実装、動作確認

よろしくお願いします！
