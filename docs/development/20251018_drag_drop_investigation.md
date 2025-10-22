# 2025-10-18: ドラッグ&ドロップ機能 調査・実装レポート

## 概要

Mac版v1.1.1のpywebview環境でドラッグ&ドロップによるファイル受け付けを実装しました。これまではクリック選択のみでしたが、ユーザビリティ向上のためドラッグ&ドロップにも対応しました。

## 背景

### 以前の実装（v1.1.1 修正前）

- **JavaScript側**: `e.dataTransfer.files` からファイルを取得できないため、pywebview環境ではドロップを拒否
- **ユーザー体験**: ドラッグ&ドロップ時に「⚠️ ドラッグ&ドロップは未対応です。クリックしてファイルを選択してください」のトースト表示
- **理由**: pywebviewのセキュリティ制約により、ブラウザのFileオブジェクトが利用不可

### 課題

1. ユーザーはドラッグ&ドロップに慣れているため、クリック選択のみでは不便
2. pywebview 6.0の機能を活用できていない
3. Mac版とWindows版（将来）で操作方法が統一できる

## 技術調査

### pywebview 6.0の機能確認

**ドキュメント**: https://pywebview.flowrl.com/6.0/guide/dom.html

pywebview 6.0（Cocoa backend）では、**DOM API**を使ってブラウザイベントをPython側で直接ハンドリングできることが判明：

```python
from webview.dom import DOMEventHandler

def on_drop(e):
    files = e.get('dataTransfer', {}).get('files', [])
    file_path = files[0].get('pywebviewFullPath')  # フルパスが取得可能
    # ...

window.dom.document.events.drop += DOMEventHandler(on_drop, prevent_default=True)
```

**重要な発見**:
- `pywebviewFullPath` プロパティでファイルの絶対パスが取得できる
- `prevent_default=True` でデフォルト動作をブロック
- Python側で処理後、JavaScriptにカスタムイベントで通知できる

## 実装設計

### アーキテクチャ

```
[ユーザー操作: ファイルドロップ]
        ↓
[Browser: drop event]
        ↓
[Python: window.dom.document.events.drop]
  - ファイルパスを pywebviewFullPath から取得
  - カスタムイベント pywebviewFileDrop を発火
        ↓
[JavaScript: window.addEventListener('pywebviewFileDrop')]
  - event.detail.path でファイルパスを受け取る
  - uploadFileViaPywebview() を呼び出す
        ↓
[既存のアップロードフロー]
  - Bridge API: upload_audio_file()
  - FastAPI: /upload-audio
  - 文字起こし可能状態へ
```

### 実装ファイル

#### 1. release/mac/src/main_app.py

**追加内容**: Python側のDOM dropハンドラー（行630-694）

```python
def setup_drag_drop_handler():
    """
    pywebview DOM APIを使ってドラッグ&ドロップを処理する。
    ブラウザのdropイベントを直接Pythonで受け取り、ファイルパスを取得する。
    """
    from webview.dom import DOMEventHandler

    def on_drop(e):
        """
        ドロップイベントのハンドラー。
        e.dataTransfer.files から pywebviewFullPath でファイルパスを取得できる。
        """
        logger.info("📥 [DragDrop] ドロップイベント発生")

        # dataTransfer.filesからファイル情報を取得
        files = e.get('dataTransfer', {}).get('files', [])

        if not files:
            logger.warning("⚠️ [DragDrop] ファイルが見つかりません")
            return

        first_file = files[0]
        file_path = first_file.get('pywebviewFullPath')  # 絶対パス
        file_name = first_file.get('name', 'unknown')

        logger.info(f"📂 [DragDrop] ファイルドロップ: {file_name} ({file_path})")

        if not file_path:
            logger.error("❌ [DragDrop] pywebviewFullPathが取得できませんでした")
            return

        # JavaScriptにカスタムイベントを発火してファイル情報を渡す
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
            console.log('📥 pywebviewFileDropイベントを発火しました:', {json.dumps(file_name)});
        }})();
        '''
        window.evaluate_js(js_code)
        logger.info(f"✅ [DragDrop] JavaScriptにイベント発火: {file_name}")

    # DOM dropイベントにハンドラーを登録
    # prevent_default=True でブラウザのデフォルト動作（ファイルを開く）を防ぐ
    window.dom.document.events.drop += DOMEventHandler(
        on_drop,
        prevent_default=True,
        stop_propagation=True
    )
    logger.info("✅ [DragDrop] DOM dropハンドラーを登録しました")

# pywebview起動後にドラッグ&ドロップハンドラーをセットアップ
window.events.loaded += setup_drag_drop_handler
```

**ポイント**:
- `window.events.loaded` イベントで初期化（DOM読み込み後に実行）
- `prevent_default=True` でブラウザのデフォルト動作をブロック
- `window.evaluate_js()` でJavaScriptにカスタムイベントを発火
- JSON.dumps() でエスケープ処理を安全に実行

#### 2. release/mac/src/main.py

**修正内容1**: dropイベントハンドラーの変更（行685-708）

**修正前**:
```javascript
if (window.pywebview && window.pywebview.api) {
    // pywebview環境ではドロップ非対応のため案内
    showToast('⚠️ ドラッグ&ドロップは未対応です。クリックしてファイルを選択してください', 4000);
    console.warn('⚠️ pywebview環境ではドラッグ&ドロップは非対応です');
    return;
}
```

**修正後**:
```javascript
if (window.pywebview && window.pywebview.api) {
    // pywebview環境ではPython側のDOM dropハンドラーに任せる
    // （pywebviewFileDropカスタムイベントで受け取る）
    console.log('🎯 pywebview環境: Python側でドロップ処理中...');
    return;
}
```

**修正内容2**: pywebviewFileDropカスタムイベントリスナーの追加（行721-740）

```javascript
// pywebview環境でのドラッグ&ドロップ処理
// Python側のDOM dropハンドラーから発火されるカスタムイベントを受け取る
console.log('📝 pywebviewFileDrop カスタムイベントリスナー登録中...');
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
console.log('✅ pywebviewFileDrop カスタムイベントリスナー登録完了');
```

**ポイント**:
- `e.detail.path` と `e.detail.name` でファイル情報を取得
- 既存の `uploadFileViaPywebview()` 関数を再利用（行746-775）
- エラーハンドリングとログ出力を充実

## ビルド結果

### ビルド環境

```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac
bash build.sh
```

- **Python**: 3.12.3
- **PyInstaller**: 6.16.0
- **pywebview**: 6.0
- **プラットフォーム**: macOS-14.8-arm64-arm-64bit

### ビルド成果物

- **アプリ**: `dist/GaQ Offline Transcriber.app` (188MB)
- **DMG**: `dist/GaQ_Transcriber_v1.1.1_mac.dmg` (77MB)
- **ビルド時間**: 約24秒

### ビルド警告

```
12291 ERROR: Hidden import 'python_multipart' not found
```

- FastAPI依存パッケージの警告（動作には影響なし）

## テスト手順

### 1. DMGマウントとアプリ起動

```bash
# DMGマウント
hdiutil attach "/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/dist/GaQ_Transcriber_v1.1.1_mac.dmg"

# アプリ起動
open "/Volumes/GaQ Offline Transcriber v1.1.1/GaQ Offline Transcriber.app"

# ログ監視（別ターミナル）
tail -f ~/.gaq/logs/app.log
```

### 2. ドラッグ&ドロップテスト

**操作手順**:
1. GaQ Offline Transcriber アプリを起動
2. Finderから音声ファイル（mp3, wav, m4a等）を選択
3. アプリのファイル選択エリアにドラッグ&ドロップ
4. ログで以下を確認:
   ```
   📥 [DragDrop] ドロップイベント発生
   📂 [DragDrop] ファイルドロップ: test.m4a (/Users/.../test.m4a)
   ✅ [DragDrop] JavaScriptにイベント発火: test.m4a
   📥 pywebviewFileDrop イベント受信: {path: "/Users/.../test.m4a", name: "test.m4a"}
   📂 ドロップされたファイル: test.m4a (...)
   🔔 [Bridge] upload_audio_file() が呼び出されました
   ✅ アップロード成功: test.m4a
   ```

5. UIで以下を確認:
   - ファイル名が表示される: `✅ test.m4a`
   - 「文字起こし開始」ボタンが有効化
   - トースト通知: `✓ ファイルを選択しました: test.m4a`

6. 文字起こし実行:
   - 「文字起こし開始」ボタンをクリック
   - プログレスバーが表示される
   - 結果が表示される

7. コピー・保存機能:
   - 「結果をコピー」ボタンでクリップボードにコピー
   - 「結果を保存」ボタンでtxtファイルに保存（メタデータ付き）

### 期待される動作

| 操作 | 期待される結果 |
|------|---------------|
| ファイルをドロップ | ✅ ファイル名が表示され、文字起こしボタンが有効化 |
| ドロップログ | ✅ `📥 [DragDrop]` ログが出力される |
| JavaScript連携 | ✅ `pywebviewFileDrop` イベントが発火 |
| アップロード | ✅ `upload_audio_file()` が呼び出される |
| トースト通知 | ✅ `✓ ファイルを選択しました` が表示 |
| クリック選択 | ✅ 従来通り動作（併用可能） |

## 動作確認（ユーザー実施が必要）

### チェックリスト

- [ ] **ドラッグ&ドロップ**: ファイル選択エリアに音声ファイルをドロップしてファイル名が表示される
- [ ] **ドロップログ確認**: `~/.gaq/logs/app.log` で `📥 [DragDrop]` ログが出力される
- [ ] **文字起こし実行**: ドロップしたファイルで文字起こしが正常に実行できる
- [ ] **プログレスバー**: リアルタイムで進捗が表示される
- [ ] **結果表示**: 文字起こし結果が正しく表示される
- [ ] **コピー機能**: 「結果をコピー」ボタンでクリップボードにコピーできる
- [ ] **保存機能**: 「結果を保存」ボタンでtxtファイルに保存できる（メタデータ付き）
- [ ] **クリック選択**: 従来のクリック選択も引き続き動作する
- [ ] **複数ファイルドロップ**: 最初のファイルのみ処理される（複数ドロップ時の挙動確認）

### 実際のテストファイル例

```
/Users/yoshihitotsuji/Desktop/Audio_test.m4a
/Users/yoshihitotsuji/Desktop/test.mp3
/Users/yoshihitotsuji/Desktop/sample.wav
```

## トラブルシューティング

### ドラッグ&ドロップが反応しない

**確認事項**:
1. pywebview 6.0がインストールされているか確認
   ```bash
   pip show pywebview
   ```
   Version: 6.0 以上

2. ログで `✅ [DragDrop] DOM dropハンドラーを登録しました` が出力されているか確認
   ```bash
   grep "DragDrop" ~/.gaq/logs/app.log
   ```

3. ブラウザ環境（開発時）では従来通り `e.dataTransfer.files` で動作する

### ファイルパスが取得できない

**ログ出力例**:
```
❌ [DragDrop] pywebviewFullPathが取得できませんでした
```

**対処**:
- pywebviewのバージョンを確認（6.0以上が必要）
- macOS Cocoa backendが使用されているか確認
- ファイルシステムのアクセス権限を確認

### アップロードに失敗する

**ログ出力例**:
```
❌ アップロードエラー: ...
```

**対処**:
- ファイルパスが正しいか確認（シンボリックリンクやネットワークドライブではない）
- ファイルサイズが大きすぎないか確認（FastAPI upload_max_size: 100MB）
- ファイル形式が音声/動画形式か確認（mp3, wav, m4a, mp4等）

## 技術的な制約と注意点

### pywebview環境の制約

1. **ファイル取得方法の違い**:
   - ブラウザ環境: `e.dataTransfer.files` → Fileオブジェクト
   - pywebview環境: `e.dataTransfer.files[0].pywebviewFullPath` → 絶対パス文字列

2. **セキュリティ制約**:
   - pywebviewはFileオブジェクトを提供しない（セキュリティ上の理由）
   - ファイルパス文字列のみ取得可能
   - Python側で実際のファイル読み込みが必要

3. **イベントハンドリング**:
   - DOM APIは `window.events.loaded` 後に利用可能
   - `prevent_default=True` でブラウザのデフォルト動作をブロック
   - カスタムイベントでJavaScriptに通知

### ブラウザ環境との互換性

**ブラウザ環境** (開発時):
- `e.dataTransfer.files` から直接Fileオブジェクトを取得
- `handleFile(files[0])` で処理
- FormDataでアップロード

**pywebview環境** (本番):
- Python側でDOM dropイベントをキャッチ
- `pywebviewFullPath` でファイルパスを取得
- Bridge API `upload_audio_file()` でアップロード

## まとめ

### 実装完了項目

- ✅ pywebview 6.0 DOM API調査
- ✅ Python側DOM dropハンドラー実装（main_app.py）
- ✅ JavaScript側カスタムイベントリスナー実装（main.py）
- ✅ 既存のアップロードフロー統合
- ✅ PyInstallerビルド成功
- ✅ DMGパッケージ作成
- ✅ 本ドキュメント作成

### 保留中（ユーザー実施が必要）

- ⏳ 実機でのドラッグ&ドロップテスト
- ⏳ 文字起こし・コピー・保存の動作確認
- ⏳ ログ出力の確認

### 今後の拡張可能性

1. **複数ファイル対応**:
   - 現在は最初のファイルのみ処理
   - `files` 配列をループして複数ファイルを処理可能

2. **ファイル形式チェック**:
   - Python側で拡張子チェック
   - 音声/動画ファイル以外を早期に拒否

3. **ドラッグビジュアルフィードバック**:
   - `dragenter`, `dragleave` イベントも同様に実装
   - UIのハイライト表示を強化

4. **Windows版への反映**:
   - 同じ実装をWindows版にも適用
   - pywebview 6.0のWindows backend（Edge/Chromium）で動作確認

## 関連ドキュメント

- [20251018_mac_build_verification.md](20251018_mac_build_verification.md) - Mac v1.1.1 ビルド検証
- [20251018_javascript_initialization_fix.md](20251018_javascript_initialization_fix.md) - JavaScript初期化修正
- [20251018_pywebview_api_investigation.md](20251018_pywebview_api_investigation.md) - pywebview API調査
- [pywebview 6.0 DOM API Documentation](https://pywebview.flowrl.com/6.0/guide/dom.html)

---

**作成日**: 2025-10-18
**作成者**: Claude Code
**対象バージョン**: Mac v1.1.1
**実装状況**: 実装完了（ユーザーテスト待ち）
