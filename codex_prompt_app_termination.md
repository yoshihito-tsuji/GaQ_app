# Codex相談: アプリ終了時のフリーズ問題について

## 問題の概要

GaQ Offline Transcriber（Mac版 v1.1.1）において、**モデルダウンロード中にアプリを終了しようとすると、フリーズしたような状態になり、終了に非常に時間がかかる**という問題が発生しています。

## 発生状況

### タイムライン（ログから）

```
13:02:46 - ユーザーがLarge-v3モデルを選択
13:02:52 - モデルダウンロード開始（約2.9GB）
13:02:52 - 文字起こしプロセス開始
13:02:53 - Hugging Face Hubからモデルダウンロード開始
13:02:57 - ★ユーザーがアプリ終了を試みる（ログに「終了」と記録）
13:03:33 - モデルロード完了（40.4秒かかった）
13:05:48 - 文字起こし完了（135.9秒）
13:05:48 - ★ようやくアプリ終了（終了操作から約3分後）
```

### 問題点

1. **ユーザーが終了操作をしても、すぐには終了しない**
2. **進行中のモデルダウンロードと文字起こしが完了するまで待たされる**
3. **フリーズしたように見え、ユーザー体験が非常に悪い**
4. **約3分間、アプリが反応しない状態が続く**

## 技術的背景

### アーキテクチャ

- **pywebview**: GUIウィンドウを提供
- **FastAPI**: バックエンドサーバー（localhost:8000）
- **faster-whisper**: 文字起こしエンジン（CPU/GPUで動作）
- **マルチプロセス**: FastAPIサーバーは別プロセスで起動

### 現在の終了処理

```python
# main_app.py の終了処理
def create_webview_window(host: str, port: int):
    # ... ウィンドウ作成 ...

    webview.start()  # ★ここでブロッキング（ウィンドウが閉じられるまで待機）

    logger.info(f"=== GaQ Offline Transcriber {APP_VERSION} 終了 ===")
```

**問題**: `webview.start()`はブロッキング関数で、ウィンドウが閉じられるまで戻らない。しかし、進行中の処理（モデルDL、文字起こし）が完了するまでウィンドウが閉じられない可能性がある。

### 文字起こしプロセス

```python
# main.py の文字起こしエンドポイント
@app.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    # バックグラウンドタスクとして実行
    background_tasks.add_task(
        transcription_service.transcribe,
        file_path,
        model=request.model,
        # ...
    )
```

**問題**: `background_tasks`は非同期だが、FastAPIサーバープロセスが生きている限り実行され続ける。

## 質問

### 1. 即座に終了させる方法

**ユーザーが終了操作をした際に、進行中の処理をキャンセルして即座に終了する方法はありますか？**

考えられるアプローチ：
- ウィンドウの`closing`イベントをフック
- 進行中のタスクをキャンセル
- FastAPIサーバーを強制終了
- pywebviewウィンドウを閉じる

### 2. ユーザーへのフィードバック

**終了処理中であることをユーザーに伝える方法はありますか？**

考えられるアプローチ：
- 終了確認ダイアログを表示（「処理中ですが終了しますか？」）
- 終了中のプログレス表示
- 強制終了オプションの提供

### 3. グレースフルシャットダウン

**可能であれば、進行中の処理を完了させてから終了する場合、どのように実装すべきですか？**

考えられるアプローチ：
- 進行中のタスクを追跡
- タスク完了後に終了
- タイムアウト設定（例: 5秒待って、それでも完了しなければ強制終了）

### 4. pywebview特有の問題

**pywebviewを使用している場合、`webview.start()`のブロッキング動作を回避する方法はありますか？**

考えられるアプローチ：
- `window.events.closing`イベントの活用
- 別スレッドでの処理
- シグナルハンドラーの実装

## 期待する動作

### 理想的な動作

1. **ユーザーが終了ボタンをクリック**
2. **確認ダイアログ表示**: 「処理中ですが終了しますか？」
3. **ユーザーがOKをクリック**
4. **即座に終了処理開始**:
   - 進行中のタスクをキャンセル
   - FastAPIサーバーを停止
   - pywebviewウィンドウを閉じる
5. **1-2秒以内にアプリが完全に終了**

### 妥協案

- タイムアウト機能: 終了操作から5秒以内に終了できない場合は強制終了
- プログレス表示: 「終了処理中...」と表示して、ユーザーに待たせていることを明示

## コード構造

### 関連ファイル

1. **main_app.py**: pywebviewウィンドウの管理、アプリのメインエントリーポイント
2. **main.py**: FastAPIサーバー、文字起こしエンドポイント
3. **transcribe.py**: 文字起こしサービス（faster-whisperを使用）

### 現在のプロセス構成

```
main_app.py (メインプロセス)
  ├── FastAPIサーバー (別プロセス: multiprocessing.Process)
  │   └── transcription_service (faster-whisper)
  │       └── モデルダウンロード (Hugging Face Hub)
  └── pywebview ウィンドウ (メインスレッド)
```

## 制約条件

- **macOS環境**: pywebview 6.0、Python 3.12
- **マルチプロセス**: FastAPIサーバーは別プロセスで起動
- **長時間処理**: モデルダウンロードは数十秒〜数分かかる
- **ユーザー体験**: 終了操作は即座に反映されるべき

## 参考情報

- pywebview documentation: https://pywebview.flowrl.com/
- FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Python multiprocessing: https://docs.python.org/3/library/multiprocessing.html

---

**どのようなアプローチが最適でしょうか？コード例や実装のヒントをいただけると助かります。**
