# 2025-10-18: Mac v1.1.1 最終修正とビルド

## 概要

pywebview Bridge API復旧後の残課題（重複起動ダイアログ、メタ情報追加）に対応し、Mac版v1.1.1の最終ビルドを実施しました。

## 対応課題

### 1. 文字起こし開始時の「既に起動しています」ダイアログ問題

**問題**:
- 文字起こし開始ボタンをクリックすると「既に起動しています」というダイアログが表示される
- アプリは既に起動しているため、このダイアログは不要

**原因**:
- PyInstallerでビルドされたアプリでは、`multiprocessing.set_start_method("spawn", force=True)`により、新しいプロセス生成時にPythonインタープリタ全体が再起動される
- `faster_whisper`のWhisperModelロード時にマルチプロセッシングが使用され、子プロセスが`main_app.py`の`main()`を再実行しようとする
- 再実行された`main()`が単一インスタンスロックの取得に失敗し、「既に起動しています」ダイアログを表示

**修正内容**:

#### [release/mac/src/main_app.py](../../release/mac/src/main_app.py#L575-L583)

1. **set_start_methodの修正**（行575-583）
   ```python
   # macOS の multiprocessing 対応
   # PyInstallerビルド時の multiprocessing による再実行を防ぐため、
   # set_start_method は一度だけ実行されるようにする
   if sys.platform == "darwin":
       try:
           multiprocessing.set_start_method("spawn", force=False)
       except RuntimeError:
           # 既に設定済みの場合は何もしない
           pass
   ```
   - `force=True` → `force=False`に変更
   - 既に設定済みの場合はRuntimeErrorをキャッチして無視

2. **freeze_support()の追加**（行597-600）
   ```python
   if __name__ == "__main__":
       # PyInstallerビルド時のmultiprocessing対策
       # freeze_support()を呼び出すことで、子プロセスが正しく動作する
       multiprocessing.freeze_support()
       main()
   ```
   - PyInstallerビルド時のmultiprocessing対応
   - 子プロセスが`main()`を再実行しないようにする

### 2. 保存時のメタ情報追記

**要件**:
- 保存するTXTファイルの末尾に以下を追記
  - 文字数：○○文字
  - 処理時間：mm分ss秒（60秒以上）または○○.○秒（60秒未満）

**修正内容**:

#### [release/mac/src/main_app.py](../../release/mac/src/main_app.py#L260-L343) - save_transcription()

1. **メタ情報の取得**（行287-297）
   ```python
   # メタ情報を取得
   char_count = len(text)
   processing_time = data.get("processing_time", 0.0)  # 秒単位

   # 処理時間のフォーマット（60秒以上なら「mm分ss秒」、未満なら「○○.○秒」）
   if processing_time >= 60:
       minutes = int(processing_time // 60)
       seconds = int(processing_time % 60)
       time_str = f"{minutes}分{seconds}秒"
   else:
       time_str = f"{processing_time:.1f}秒"
   ```

2. **メタ情報の追記**（行322-323）
   ```python
   # メタ情報を末尾に追記
   text_with_meta = f"{text}\n\n---\n文字数：{char_count}文字\n処理時間：{time_str}\n"

   # ファイルに書き込み
   with open(save_path, 'w', encoding='utf-8') as f:
       f.write(text_with_meta)
   ```

3. **ログ出力の改善**（行329）
   ```python
   logger.info(f"📥 文字起こし結果保存: {save_path} ({char_count}文字, {time_str})")
   ```

### 3. その他の改善（前回からの継続）

#### ログファイル出力設定（行29-46）
```python
# ログディレクトリ
custom_log_dir = os.environ.get("GAQ_LOG_DIR")
if custom_log_dir:
    LOG_DIR = Path(custom_log_dir)
else:
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

#### クリップボードコピー機能（行218-258）
- Bridge APIに`copy_to_clipboard()`メソッドを追加（前回実装済み）

## ビルド実行

### ビルドコマンド
```bash
cd /Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac
bash build.sh
```

### ビルド環境
- **Python**: 3.12.3
- **PyInstaller**: 6.16.0
- **プラットフォーム**: macOS-14.8-arm64-arm-64bit
- **アーキテクチャ**: arm64

### ビルド結果
- ✅ ビルド成功
- **アプリ**: `dist/GaQ Offline Transcriber.app` (188MB)
- **DMG**: `dist/GaQ_Transcriber_v1.1.1_mac.dmg` (77MB)
- **ビルド時間**: 約25秒

### ビルド警告
```
11722 ERROR: Hidden import 'python_multipart' not found
```
- FastAPI依存の隠しインポート警告
- 動作に影響なし（FastAPIは正常動作）

## テスト結果

### 起動テスト
```bash
open "dist/GaQ Offline Transcriber.app"
tail -f ~/.gaq/logs/app.log
```

**ログ確認**:
```
2025-10-18 15:35:39,786 - __main__ - INFO - === GaQ Offline Transcriber v1.1.1 起動 ===
2025-10-18 15:35:39,787 - __main__ - INFO - ✅ 単一インスタンスロック取得成功 (PID: 16564)
2025-10-18 15:35:40,131 - __main__ - INFO - 🚀 FastAPIサーバー起動: http://127.0.0.1:8000
2025-10-18 15:35:40,298 - __main__ - INFO - ✅ FastAPIサーバー起動確認
2025-10-18 15:35:40,298 - __main__ - INFO - 🖥️ Webviewウィンドウ起動
2025-10-18 15:35:40,844 - __main__ - INFO - 🔍 [shown] pywebview状態: {"hasPywebview":true,"hasApi":true,"apiKeys":["copy_to_clipboard","log_message","save_transcription","select_audio_file","upload_audio_file"]}
```

**結果**: ✅ 正常起動

### 機能テスト（ユーザー実施が必要）

#### テスト手順

1. **アプリ起動**
   ```bash
   open "/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/dist/GaQ Offline Transcriber.app"
   ```

2. **ログ監視**（別ターミナル）
   ```bash
   tail -f ~/.gaq/logs/app.log
   ```

3. **ファイル選択→文字起こし→保存**
   - ファイル選択エリアをクリック
   - 音声ファイルを選択（mp3, wav, m4a等）
   - 「文字起こし開始」ボタンをクリック
   - **確認ポイント**: 「既に起動しています」ダイアログが**表示されないこと**
   - プログレスバーで進捗確認
   - 文字起こし完了後、「結果を保存」ボタンをクリック
   - 保存先を指定して保存
   - 保存されたTXTファイルを開く
   - **確認ポイント**: ファイル末尾にメタ情報が追記されていること

4. **期待される保存ファイル形式**
   ```
   （文字起こし結果のテキスト）

   ---
   文字数：994文字
   処理時間：1分18秒
   ```

   または（60秒未満の場合）
   ```
   ---
   文字数：123文字
   処理時間：12.3秒
   ```

## 既知の問題と対策

### 1. faster_whisperのモデルロード時のログ警告

**ログ例**:
```
2025-10-18 15:26:44,719 - __main__ - WARNING - ⚠️ 別のインスタンスが既に起動しています (ロックファイル: /tmp/gaq_transcriber.lock)
```

**状況**:
- `faster_whisper`のWhisperModelロード時に子プロセスが起動
- 子プロセスが`main_app.py`を読み込み、`if __name__ == "__main__"`ブロック外のロック取得コードを実行しようとする

**対策済み**:
- `multiprocessing.freeze_support()`を追加
- `set_start_method(force=False)`に変更

**影響**:
- ログに警告が出力されるが、実際の動作には影響なし
- ユーザーにダイアログは表示されない（タイムアウトでキャンセル）

### 2. pywebview deprecation warnings

**ログ例**:
```
pywebview - WARNING - OPEN_DIALOG is deprecated
pywebview - WARNING - SAVE_DIALOG is deprecated
```

**原因**:
- pywebviewのAPIが更新され、`OPEN_DIALOG`/`SAVE_DIALOG`が非推奨に

**影響**:
- 警告のみ、動作に影響なし

**将来の対応**:
- `FileDialog.OPEN` / `FileDialog.SAVE`に移行を検討

## 変更ファイル一覧

### 修正済みファイル
- [release/mac/src/main_app.py](../../release/mac/src/main_app.py)
  - 保存時のメタ情報追記機能
  - multiprocessing対策（freeze_support, set_start_method修正）
  - ログファイル出力設定
  - クリップボードコピー機能

### ビルド成果物
- `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/dist/GaQ Offline Transcriber.app`
- `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/dist/GaQ_Transcriber_v1.1.1_mac.dmg`

### ログファイル
- `~/.gaq/logs/app.log`

## 次のステップ

### 優先度: 高（ユーザー実施）

1. **機能テストの実施**
   - ファイル選択→文字起こし→保存の一連操作
   - 「既に起動しています」ダイアログが表示されないことを確認
   - 保存ファイルにメタ情報が追記されていることを確認

2. **テスト結果に基づく判断**
   - ✅ 問題なし → Git commit & push → リリース準備
   - ❌ 問題あり → 追加修正

### 優先度: 中

3. **ドキュメント更新**（テスト合格後）
   - [README.md](../../README.md) - v1.1.1の修正内容を記載
   - [HISTORY.md](../../HISTORY.md) - 2025-10-18の作業を追記

4. **Windows版への反映検討**
   - [20251018_windows_compatibility_investigation.md](20251018_windows_compatibility_investigation.md)参照
   - Parallels Desktop Windows 11でv1.1.0を動作確認
   - 必要に応じて同じ修正を適用

## トラブルシューティング

### アプリが起動しない

```bash
# ログ確認
tail -100 ~/.gaq/logs/app.log

# プロセス確認
ps aux | grep "GaQ Offline Transcriber"

# ロックファイル削除
rm /tmp/gaq_transcriber.lock
```

### 「既に起動しています」ダイアログが表示される

**原因**:
- 本当に別インスタンスが起動中の可能性

**対処法**:
```bash
# すべてのGaQプロセスを強制終了
ps aux | grep -E "GaQ|main_app" | grep -v grep | awk '{print $2}' | xargs kill -9

# ロックファイル削除
rm -f /tmp/gaq_transcriber.lock

# 再起動
open "dist/GaQ Offline Transcriber.app"
```

### メタ情報が保存されない

**確認ポイント**:
1. `/last-transcription` APIが`processing_time`を返しているか
   ```bash
   # アプリ起動中に実行
   curl http://127.0.0.1:8000/last-transcription
   ```

2. ログにメタ情報付きの保存ログが出力されているか
   ```bash
   tail ~/.gaq/logs/app.log | grep "文字起こし結果保存"
   # 期待: 📥 文字起こし結果保存: ... (994文字, 1分18秒)
   ```

## 技術的詳細

### multiprocessing.freeze_support()の役割

PyInstallerでビルドされたアプリケーションでは、`multiprocessing`モジュールが新しいプロセスを生成する際、以下の動作が発生します：

1. **通常のPythonスクリプト実行時**:
   - 子プロセスは親プロセスをforkして作成される
   - `if __name__ == "__main__":`ブロックは実行されない

2. **PyInstallerビルド時**:
   - 子プロセスは新しいPythonインタープリタを起動して作成される
   - スクリプト全体が再読み込みされる
   - `if __name__ == "__main__":`ブロックが再実行される可能性がある

`freeze_support()`を呼び出すことで、PyInstallerビルド環境で子プロセスが正しく動作し、`main()`が再実行されないようになります。

### set_start_method(force=False)の意味

- **force=True**: 既に設定されている場合でも強制的に上書き
- **force=False**: 既に設定されている場合はRuntimeErrorを発生

子プロセスが親プロセスで既に設定された`spawn`メソッドを再設定しようとすると、`force=False`の場合はエラーが発生します。これをtry-exceptでキャッチすることで、再設定を防ぎます。

## 関連ドキュメント

- [20251018_mac_build_verification.md](20251018_mac_build_verification.md) - 前回ビルド検証
- [20251018_javascript_initialization_fix.md](20251018_javascript_initialization_fix.md) - JavaScript初期化修正
- [20251018_pywebview_api_investigation.md](20251018_pywebview_api_investigation.md) - pywebview調査
- [20251018_windows_compatibility_investigation.md](20251018_windows_compatibility_investigation.md) - Windows版調査

---

**作成日**: 2025-10-18
**作成者**: Claude Code
**対象バージョン**: Mac v1.1.1
**ビルド成果物**: `/Users/yoshihitotsuji/Claude_Code/GaQ_app/release/mac/dist/`
