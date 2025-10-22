# GaQ Offline Transcriber 開発履歴

## 2025-10-18: Mac版v1.1.1 pywebview環境の完全復旧

### 概要

Mac版v1.1.1において、pywebview環境での入力系・コピー・保存機能が完全に動作するようになりました。前回のセッションで残っていた課題をすべて解決し、実用可能な状態になりました。

### 解決した主要課題

#### 1. ドラッグ&ドロップ機能の実装

**問題**:
- pywebview環境では `e.dataTransfer.files` からFileオブジェクトが取得できない
- Python側のDOM APIハンドラーがイベントをキャッチできない
- JavaScript側で `preventDefault()` を呼ぶとPython側にイベントが伝播しない

**試行錯誤**:
- 試行1: Python側のDOM dropハンドラーのみ実装 → Python側のログが出ない
- 試行2: dragoverハンドラー追加（prevent_default=True） → 変化なし
- 試行3: JavaScript側のpreventDefault()を条件分岐 → 依然として動作せず
- **最終解決**: `text/uri-list` データ型からファイルパスを直接取得

**実装方法**:
```javascript
// #uploadArea に直接 dragover/drop ハンドラをバインド
uploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('dragover');

    if (window.pywebview && window.pywebview.api) {
        // text/uri-list からファイルパスを取得
        var uriList = e.dataTransfer.getData('text/uri-list');
        if (uriList) {
            var filePath = decodeURIComponent(uriList.replace('file://', '').trim());
            var fileName = filePath.split('/').pop();
            uploadFileViaPywebview(filePath, fileName);
        }
    } else {
        // ブラウザ環境では従来通り
        var files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }
});
```

**成果**:
- ✅ ドラッグ&ドロップでファイルが正しく選択できる
- ✅ `text/uri-list` から絶対パスを取得
- ✅ クリック選択との併用が可能

#### 2. Large-v3選択時の「ファイルが見つかりません」エラー解決

**問題**:
- モデルをLarge-v3に変更して文字起こし実行すると「ファイルが見つかりません」エラー
- クリック選択とドラッグ&ドロップで異なるアップロード処理が原因
- `window.uploadedFileId` の管理が不適切

**解決策**:
```javascript
// クリック／ドラッグ共通で window.uploadedFilePath を保持
window.uploadedFilePath = filePath;
window.uploadedFileName = fileName;

// 文字起こし前に常に再アップロード
if (window.uploadedFilePath) {
    var reuploadResult = await window.pywebview.api.upload_audio_file(window.uploadedFilePath);
    if (reuploadResult.success && reuploadResult.file_id) {
        await startTranscriptionWithFileId(reuploadResult.file_id, window.uploadedFileName, model);
    }
}
```

**成果**:
- ✅ モデル変更時も正しくファイルが再アップロードされる
- ✅ Large-v3での文字起こしが正常に動作
- ✅ ファイルIDの管理が一元化

#### 3. クリップボードコピー機能の完全実装

**問題**:
- `subprocess` + `pbcopy` では0バイトしかコピーされない
- AppleScriptで直接文字列を渡すとコマンドライン長制限でクラッシュ
- UTF-8エンコーディングの検証エラー

**最終解決策**:
```python
def copy_to_clipboard(self, text: str):
    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    try:
        # AppleScriptでファイルを読み込んでクリップボードにセット
        applescript = f'''
        set theFile to POSIX file "{tmp_path}"
        set fileRef to open for access theFile
        set fileContents to read fileRef as «class utf8»
        close access fileRef
        set the clipboard to fileContents
        '''

        subprocess.run(['osascript', '-e', applescript],
                      capture_output=True, text=True, check=True, timeout=5)

        # 検証（エンコーディングエラーを許容）
        verify_process = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_bytes, stderr_bytes = verify_process.communicate()

        try:
            clipboard_text = stdout_bytes.decode('utf-8')
        except UnicodeDecodeError:
            clipboard_text = stdout_bytes.decode('utf-8', errors='replace')

        return {"success": True, "message": "クリップボードにコピーしました"}

    finally:
        os.unlink(tmp_path)
```

**成果**:
- ✅ 長文でもクリップボードに正しくコピーできる
- ✅ AppleScriptで確実にUTF-8として処理
- ✅ PyInstaller環境でも安定動作

#### 4. 保存機能のメタデータ追加

**実装**:
```python
def save_transcription(self):
    # /last-transcription から結果を取得
    response = requests.get("http://127.0.0.1:8000/last-transcription", timeout=5)
    data = response.json()
    text = data.get("text", "")

    # メタデータを計算
    char_count = len(text)
    processing_time = data.get("processing_time", 0.0)

    if processing_time >= 60:
        minutes = int(processing_time // 60)
        seconds = int(processing_time % 60)
        time_str = f"{minutes}分{seconds}秒"
    else:
        time_str = f"{processing_time:.1f}秒"

    # メタデータを追記
    text_with_meta = f"{text}\n\n---\n文字数：{char_count}文字\n処理時間：{time_str}\n"

    # ファイルに保存
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(text_with_meta)
```

**成果**:
- ✅ 保存ファイルに文字数と処理時間を自動追記
- ✅ 処理時間は60秒以上で「分秒」表記に自動変換
- ✅ ファイル名は `transcription_YYYYMMDD_HHMMSS.txt` 形式

#### 5. モデルダウンロード時の挙動改善

**変更内容**:
```javascript
// 未ダウンロードモデルは確認ダイアログを使わず通知のみで処理継続
if (!data.exists) {
    showToast('モデル「' + model + '」をダウンロードします（約' + data.size_gb + 'GB）', 4000);
    showToast('しばらくお待ちください...', 3000);
    showToast('ダウンロード後、自動的に文字起こしを開始します', 4000);

    if (window.uploadedFilePath) {
        var reuploadResult = await window.pywebview.api.upload_audio_file(window.uploadedFilePath);
        await startTranscriptionWithFileId(reuploadResult.file_id, window.uploadedFileName, model);
    }
}
```

**成果**:
- ✅ 確認ダイアログを廃止（自動的にダウンロード開始）
- ✅ トースト通知で進捗を表示
- ✅ ダウンロード完了後、自動的に文字起こし開始

#### 6. UI/UXの微修正

**AppleScriptダイアログの統一**:
```applescript
# 重複起動時
display dialog "GaQ Offline Transcriber は既に起動しています。" buttons {"OK"} default button "OK" with title "お知らせ"

# インストール完了時
display dialog "インストールが完了しました。\\nアプリケーションフォルダから起動してください。" buttons {"OK"} default button "OK" with title "お知らせ"
```

**ログ出力の強化**:
- ドラッグ&ドロップ処理: `📥 [DragDrop]` プレフィックス
- アップロード成功: `✅ アップロード成功: ファイル名 (file_id: xxx)`
- モデルダウンロード: `📦 [ModelDownload]` プレフィックス

**成果**:
- ✅ ダイアログのタイトルが統一され、ユーザー体験が向上
- ✅ ログの可読性が向上し、デバッグが容易に

### ビルド・動作確認

**ビルド環境**:
- Python: 3.12.3
- PyInstaller: 6.16.0
- pywebview: 6.0
- macOS: 14.8 (arm64)

**ビルドコマンド**:
```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac
bash build.sh
```

**成果物**:
- アプリ: `dist/GaQ Offline Transcriber.app` (188MB)
- DMG: `dist/GaQ_Transcriber_v1.1.1_mac.dmg` (77MB)

**動作確認項目**:
- ✅ クリック選択でファイルを選択できる
- ✅ ドラッグ&ドロップでファイルを選択できる
- ✅ 文字起こしが正常に実行できる（Medium, Large-v3）
- ✅ プログレスバーがリアルタイムで更新される
- ✅ 結果をクリップボードにコピーできる
- ✅ 結果をファイルに保存できる（メタデータ付き）
- ✅ モデル選択を変更できる
- ✅ 複数ファイルを連続処理できる

### 残存課題（今後の検討事項）

#### 1. 強制終了の再発

**状況**: 文字起こし完了後、アプリを終了すると強制終了する場合がある

**原因仮説**:
- FastAPIサーバーの停止処理が不完全
- multiprocessingプロセスの終了待ちがタイムアウト
- pywebviewウィンドウのクローズ処理とサーバー停止の競合

**対処方針**: 今後の検討事項として保留（機能には影響なし）

#### 2. Windows版への展開

**状況**: Mac版v1.1.1の実装をWindows版にも反映する必要がある

**作業項目**:
- Windows版でのドラッグ&ドロップ実装
- Windows版でのクリップボードコピー実装（pyperclip等）
- Windows版でのファイル保存ダイアログ調整
- PyInstallerビルドスクリプトの整備

**優先度**: 中（Mac版が安定してから着手）

### 技術的知見

#### pywebview環境でのファイルドロップ

- **DOM API（window.dom.document.events.drop）は動作しない**: JavaScript側のイベントリスナーとの競合が原因
- **text/uri-list データ型が有効**: `e.dataTransfer.getData('text/uri-list')` でファイルパスを取得可能
- **file:// プレフィックスの除去が必要**: `decodeURIComponent()` と `replace('file://', '')` で処理

#### PyInstaller環境でのクリップボード操作

- **pbcopy は信頼性が低い**: subprocessで呼び出しても0バイトになる場合がある
- **AppleScript + 一時ファイルが確実**: ファイル経由でクリップボードにセットすると確実
- **UTF-8エンコーディング指定が必須**: `«class utf8»` を指定しないと文字化けする

#### FastAPI + pywebviewの統合

- **ファイルIDの管理が重要**: モデル変更時は常に再アップロードが必要
- **window.uploadedFilePath で統一**: クリックとドロップで共通の変数を使用
- **Bridge APIの活用**: pywebview.api経由で確実にPython側の関数を呼び出す

### 開発時間

- **作業時間**: 約6時間
- **主要タスク**:
  - ドラッグ&ドロップ実装: 3時間（試行錯誤含む）
  - クリップボードコピー実装: 1.5時間
  - Large-v3エラー修正: 0.5時間
  - UI/UX改善: 0.5時間
  - ビルド・動作確認: 0.5時間

### まとめ

Mac版v1.1.1は、pywebview環境での入力系・コピー・保存機能がすべて動作するようになり、**実用可能な状態**になりました。ドラッグ&ドロップ機能の実装により、ユーザビリティが大幅に向上しました。

今後は、Windows版への展開と、強制終了問題の解決を検討していきます。

---

## 2025-10-16: Mac版起動エラー修正とPython 3.12固定ビルド対応

### 概要

Mac版v1.1.1の起動エラーを修正し、Python 3.12固定ビルドに対応しました。

### 主要な変更点

#### 1. build.shのPython検出ロジック修正

**問題**: Homebrewのpython3.12パスがハードコードされており、システムPythonを検出できない

**修正**:
```bash
# 修正前
PYTHON_CMD="/opt/homebrew/bin/python3.12"

# 修正後
PYTHON_CMD=$(which python3.12 2>/dev/null || echo "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12")
```

**成果**:
- ✅ システムPython 3.12を優先的に検出
- ✅ Homebrewパスにフォールバックしない
- ✅ ビルド環境の移植性が向上

#### 2. バージョン表示機能の追加

**実装**:
```python
# main_app.pyに追加
APP_VERSION = "1.1.1"
logger.info(f"=== GaQ Offline Transcriber v{APP_VERSION} 起動 ===")
```

**成果**:
- ✅ ログでバージョンが確認できる
- ✅ 起動・終了時に明確なマーカーが出力される

#### 3. DMG再ビルド検証

**検証項目**:
- ✅ ビルドが成功する
- ✅ DMGが正しく作成される
- ✅ アプリが起動する
- ✅ バージョン表示が正しい

### 残存課題

#### Mac版v1.1.1の重大な問題

**起動エラー**:
```
AttributeError: module 'pywebview.window' has no attribute 'Window'
```

**原因**: pywebview 5.3とpywebview 6.0のAPI変更

**対応**: README.mdに警告を追加

```markdown
> ⚠️ **Mac版v1.1.1には起動エラーがあります**
> 現在、Mac版v1.1.1は起動時にエラーが発生します。修正版をお待ちください。
> Windows版v1.1.0は正常に動作します。
```

---

## これ以前の履歴

詳細は各バージョンのリリースノートを参照してください。

- **v1.1.0**: Windows版初回リリース
- **v1.0.x**: Mac版初期開発
