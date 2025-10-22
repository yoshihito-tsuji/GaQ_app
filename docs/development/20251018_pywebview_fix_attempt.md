# Mac版 v1.1.1 - pywebview制約対応の実装試行

**日付**: 2025-10-18
**担当**: Claude Code
**ステータス**: ⚠️ 実装完了・動作未確認（問題未解決）

---

## 📋 作業概要

前回のテストで発見されたpywebview環境特有の制約に対して、Python Bridge APIを使った修正を実装しました。しかし、実機テストで問題が解決しないことが確認されました。

---

## ❌ 未解決の問題

### 1. ファイル選択が動作しない
- **現象**: ファイル選択エリアをクリックしてもダイアログが表示されない
- **原因**: pywebviewでは `<input type="file">` の `.click()` メソッドが制限されている

### 2. モデル管理ボタンが反応しない
- **現象**: 「モデル管理」ボタンをクリックしてもモーダルが開かない
- **原因**: イベント伝播の制約、または `addEventListener` の動作制限

### 3. ドラッグ&ドロップが動作しない
- **現象**: ファイルをドラッグ&ドロップしても反応しない
- **原因**: `DataTransfer` オブジェクトへのアクセスが制限されている

---

## 🔧 実装した修正内容

### 1. Python Bridge API の拡張

#### `main_app.py` - Bridge クラスに2つのメソッド追加

**`select_audio_file()` メソッド** ([main_app.py:239-297](../../release/mac/src/main_app.py#L239-L297))
```python
def select_audio_file(self):
    """音声ファイル選択ダイアログを表示（pywebview用）"""
    try:
        file_types = (
            'Audio Files (*.mp3;*.wav;*.m4a;*.flac;*.ogg;*.aac;*.wma)',
            'Video Files (*.mp4;*.mov;*.avi;*.mkv;*.wmv;*.flv)',
            'All Files (*.*)'
        )

        file_path = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=file_types
        )

        if not file_path:
            logger.info("📂 ファイル選択: キャンセル")
            return {"success": False, "path": None, "name": None, "cancelled": True}

        # タプルの場合は最初の要素を取得
        if isinstance(file_path, tuple):
            file_path = file_path[0] if file_path else None

        file_name = os.path.basename(file_path)
        logger.info(f"📂 ファイル選択: {file_name} ({file_path})")

        return {"success": True, "path": file_path, "name": file_name}

    except Exception as e:
        logger.error(f"❌ ファイル選択エラー: {e}", exc_info=True)
        return {"success": False, "path": None, "name": None, "error": str(e)}
```

**`upload_audio_file(file_path)` メソッド** ([main_app.py:299-363](../../release/mac/src/main_app.py#L299-L363))
```python
def upload_audio_file(self, file_path):
    """選択された音声ファイルをFastAPIサーバーにアップロード（pywebview用）"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"❌ ファイルが見つかりません: {file_path}")
            return {"success": False, "file_id": None, "message": "ファイルが見つかりません"}

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        logger.info(f"📤 アップロード開始: {file_name} ({file_size} bytes)")

        # FastAPIの /upload エンドポイントにPOST
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            response = requests.post(
                "http://127.0.0.1:8000/upload",
                files=files,
                timeout=30
            )

        if response.status_code == 200:
            data = response.json()
            file_id = data.get('file_id')
            logger.info(f"✅ アップロード成功: {file_name} (file_id: {file_id})")
            return {"success": True, "file_id": file_id, "message": "アップロード成功"}
        else:
            logger.error(f"❌ アップロード失敗: HTTP {response.status_code}")
            return {"success": False, "file_id": None, "message": f"アップロード失敗: HTTP {response.status_code}"}

    except Exception as e:
        logger.error(f"❌ アップロードエラー: {e}", exc_info=True)
        return {"success": False, "file_id": None, "message": f"エラー: {str(e)}"}
```

### 2. JavaScript側の修正

#### ファイル選択エリアのクリックイベント修正 ([main.py:541-577](../../release/mac/src/main.py#L541-L577))

```javascript
// クリックでファイル選択（pywebview/Safari対応）
uploadArea.addEventListener('click', async function(e) {
    console.log('uploadArea clicked');

    // pywebview環境を検出してBridge APIを使用
    if (window.pywebview && window.pywebview.api && window.pywebview.api.select_audio_file) {
        console.log('🔧 pywebview環境を検出 - Bridge APIを使用');
        e.preventDefault();
        e.stopPropagation();

        try {
            console.log('📂 ファイル選択ダイアログを表示中...');
            var result = await window.pywebview.api.select_audio_file();
            console.log('✅ ファイル選択結果:', result);

            if (result.success && result.path) {
                console.log('📤 ファイルをアップロード中:', result.name);
                await uploadFileViaPywebview(result.path, result.name);
            } else if (!result.cancelled) {
                showToast('✗ ファイル選択に失敗しました');
                console.error('❌ ファイル選択失敗:', result);
            } else {
                console.log('ℹ️ ファイル選択がキャンセルされました');
            }
        } catch (error) {
            console.error('❌ ファイル選択エラー:', error);
            showToast('✗ ファイル選択に失敗しました');
        }
    } else {
        // 通常のブラウザ環境 - 標準のfile inputを使用
        console.log('🌐 ブラウザ環境 - 標準file inputを使用');
        e.preventDefault();
        e.stopPropagation();
        console.log('fileInput.click() executing');
        fileInput.click();
    }
});
```

#### アップロード関数の追加 ([main.py:640-669](../../release/mac/src/main.py#L640-L669))

```javascript
// pywebview経由でファイルをアップロード
async function uploadFileViaPywebview(filePath, fileName) {
    console.log('📤 uploadFileViaPywebview() 開始:', fileName);

    try {
        // Bridge APIを使ってファイルをアップロード
        var uploadResult = await window.pywebview.api.upload_audio_file(filePath);
        console.log('✅ アップロード結果:', uploadResult);

        if (uploadResult.success && uploadResult.file_id) {
            console.log('✅ ファイルアップロード成功 - file_id:', uploadResult.file_id);

            // UIを更新
            fileName.textContent = '✅ ' + fileName;
            transcribeBtn.disabled = false;
            resultDiv.style.display = 'none';

            // selectedFileIDを保存（文字起こし時に使用）
            window.uploadedFileId = uploadResult.file_id;
            window.uploadedFileName = fileName;

            showToast('✓ ファイルを選択しました: ' + fileName);
        } else {
            console.error('❌ アップロード失敗:', uploadResult.message);
            showToast('✗ ' + uploadResult.message);
        }
    } catch (error) {
        console.error('❌ アップロードエラー:', error);
        showToast('✗ アップロードに失敗しました');
    }
}
```

#### 文字起こし実行の修正 ([main.py:672-708](../../release/mac/src/main.py#L672-L708))

```javascript
// 文字起こし実行（SSEでリアルタイム進捗表示）
transcribeBtn.addEventListener('click', function() {
    // pywebview環境とブラウザ環境の両方に対応
    if (!selectedFile && !window.uploadedFileId) {
        alert('ファイルを選択してください');
        return;
    }

    var model = modelSelect.value;

    // モデル存在確認
    fetch('/check-model/' + model)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (!data.exists) {
                var message = 'モデル「' + model + '」をダウンロードします（約' + data.size_gb + 'GB、数分かかります）。\\n続行しますか？';

                if (confirm(message)) {
                    // pywebview環境の場合はfile_idを使用、ブラウザ環境はFileオブジェクト
                    if (window.uploadedFileId) {
                        startTranscriptionWithFileId(window.uploadedFileId, window.uploadedFileName, model);
                    } else {
                        startTranscription(selectedFile, model);
                    }
                }
            } else {
                // pywebview環境の場合はfile_idを使用、ブラウザ環境はFileオブジェクト
                if (window.uploadedFileId) {
                    startTranscriptionWithFileId(window.uploadedFileId, window.uploadedFileName, model);
                } else {
                    startTranscription(selectedFile, model);
                }
            }
        })
        .catch(function(error) {
            console.error('エラー:', error);
            alert('モデルチェックに失敗しました');
        });
```

#### file_id対応の文字起こし関数追加 ([main.py:804-894](../../release/mac/src/main.py#L804-L894))

```javascript
// file_idを使って文字起こしを実行（pywebview環境用）
function startTranscriptionWithFileId(fileId, fileName, model) {
    console.log('文字起こし開始（file_id使用）:', fileId, fileName, 'モデル:', model);

    transcribeBtn.disabled = true;
    progress.style.display = 'block';
    resultDiv.style.display = 'none';

    // プログレスバーをリセット
    var progressBarFill = document.getElementById('progressBarFill');
    var progressStatus = document.getElementById('progressStatus');
    progressBarFill.style.width = '0%';
    progressBarFill.textContent = '0%';
    progressStatus.textContent = '準備中...';

    // file_idとmodelをクエリパラメータで送信
    var url = '/transcribe-stream-by-id?file_id=' + encodeURIComponent(fileId) + '&model=' + encodeURIComponent(model);

    fetch(url, { method: 'GET' })
    .then(function(response) {
        // SSE ストリーム処理（既存のstartTranscription関数と同じ）
        // ...
    })
    .catch(function(error) {
        alert('エラー: ' + error.message);
        progress.style.display = 'none';
        transcribeBtn.disabled = false;
    });
}
```

### 3. FastAPI バックエンドの拡張

#### `/transcribe-stream-by-id` エンドポイント追加 ([main.py:1365-1483](../../release/mac/src/main.py#L1365-L1483))

```python
@app.get("/transcribe-stream-by-id")
async def transcribe_stream_by_id(
    background_tasks: BackgroundTasks,
    file_id: str,
    model: str = DEFAULT_MODEL,
):
    """
    アップロード済みファイルをfile_idで文字起こし（pywebview環境用）

    Args:
        file_id: アップロード済みファイルのID
        model: 使用するモデル（medium, large-v3）

    Returns:
        Server-Sent Eventsストリーム
    """

    async def event_stream():
        temp_file = None
        try:
            # file_idからファイルパスを検索
            logger.info(f"file_idから文字起こし開始: {file_id}, model: {model}")

            # UPLOAD_DIR内のファイルを検索
            matching_files = list(UPLOAD_DIR.glob(f"{file_id}*"))

            if not matching_files:
                yield f"data: {json.dumps({'error': f'ファイルが見つかりません: {file_id}'})}\n\n"
                return

            temp_file = matching_files[0]
            logger.info(f"ファイル検出: {temp_file}")

            # 既存のtranscribe-streamと同じ処理
            # （モデルチェック、文字起こし実行、進捗送信）
            # ...

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 4. モデル管理ボタンの修正 ([main.py:1005-1039](../../release/mac/src/main.py#L1005-L1039))

```javascript
// モーダルを開く関数（グローバルに定義）
window.openModelModal = function() {
    console.log('📂 openModelModal() が呼ばれました');
    console.log('modelModal.style.display before:', modelModal.style.display);
    loadModels();
    modelModal.style.display = 'block';
    console.log('modelModal.style.display after:', modelModal.style.display);
};

// モデル管理ボタンのイベント（複数の方法で設定）
if (modelManageBtn) {
    // 方法1: addEventListener（通常のブラウザ環境）
    modelManageBtn.addEventListener('click', function(e) {
        console.log('🔧 モデル管理ボタンがクリックされました（addEventListener）');
        e.preventDefault();
        e.stopPropagation();
        window.openModelModal();
    }, true); // キャプチャフェーズで実行

    // 方法2: onclick属性（pywebview環境での確実性向上）
    modelManageBtn.onclick = function(e) {
        console.log('🔧 モデル管理ボタンがクリックされました（onclick）');
        e.preventDefault();
        e.stopPropagation();
        window.openModelModal();
        return false;
    };

    console.log('✅ モデル管理ボタンのイベントリスナー設定完了');
}
```

---

## 📦 ビルド結果

```bash
✓ ビルドが成功しました！

成果物:
  dist/GaQ Offline Transcriber.app
  188M	dist/GaQ Offline Transcriber.app

✓ DMGパッケージを作成しました！
  dist/GaQ_Transcriber_v1.1.1_mac.dmg
  78M   dist/GaQ_Transcriber_v1.1.1_mac.dmg
```

---

## ⚠️ 実機テスト結果

ユーザーからの報告：**引き続き、同様の問題が発生しています**

1. ファイル選択機能が動作しない
2. モデル管理ボタンが反応しない
3. ドラッグ&ドロップが動作しない

---

## 🔍 考察・原因分析

### 可能性1: Bridge APIの初期化タイミング

- `window.pywebview.api` が利用可能になるタイミングが遅い
- JavaScriptの実行タイミングとBridge登録のタイミングが合っていない

### 可能性2: イベント伝播の根本的な制約

- pywebviewのWebKit実装に起因する制約
- `addEventListener` と `onclick` の両方が効かない可能性

### 可能性3: デバッグ情報の不足

- JavaScriptコンソールログがPythonログに出力されていない
- 実際にどこで失敗しているか特定できていない

---

## 📋 次回作業の優先順位

### 最優先：デバッグ環境の整備

1. **JavaScriptコンソールログの取得**
   - pywebviewでJavaScriptコンソールをPythonログに出力
   - `window.pywebview.api` の存在確認ログ
   - すべてのイベントリスナー登録の成否確認

2. **最小限のテストケース作成**
   - 単純なボタン1つでBridge API呼び出しをテスト
   - ファイル選択以外の機能（例: alert表示）でBridge動作確認

3. **段階的な動作確認**
   - ブラウザ環境（http://127.0.0.1:8000）での動作確認
   - pywebview環境との動作比較

### 中優先：代替アプローチの検討

1. **UI要素の直接配置**
   - JavaScript経由ではなく、Python側でネイティブUIボタンを配置
   - pywebviewのAPI経由で直接操作

2. **別のUIフレームワークの検討**
   - Electron、Tauri、Flaskなどの代替案
   - pywebviewの制約を回避できる方法

3. **ポーリング方式**
   - 定期的にPython側の状態を確認
   - ファイル選択状態をpollingで検出

---

## 📝 関連ドキュメント

- **[~/Desktop/pywebview_fix_instructions.md](~/Desktop/pywebview_fix_instructions.md)** - 詳細な修正指示書
- **[docs/development/20251017_mac_smoke_test.md](20251017_mac_smoke_test.md)** - 初期テスト結果
- **[docs/development/20251018_mac_multi_issue_fix.md](20251018_mac_multi_issue_fix.md)** - マルチ問題修正作業

---

## 🎯 まとめ

- ✅ Bridge API、JavaScript修正、FastAPIエンドポイント追加を実装完了
- ✅ ビルド成功（188MB app、78MB DMG）
- ❌ 実機テストで問題未解決
- 🔜 次回は徹底的なデバッグ環境整備が必須

**結論**: pywebviewの制約は予想以上に深刻。根本的な解決には、デバッグ情報の強化と代替アプローチの検討が必要。
