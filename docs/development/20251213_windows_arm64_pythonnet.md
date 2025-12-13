# 開発ログ - 2025-12-13 (pythonnet/ARM64対応)

**From**: Claude Code（実装エンジニア）
**To**: Codex（アーキテクト）
**CC**: Yoshihitoさん（プロジェクトオーナー）

---

## 報告概要

Windows ARM64環境でのpywebview起動問題を調査・修正中。v1.2.3のビルドを複数回実施。

## 問題の経緯

### 発生した問題

ARM64環境（Parallels on Apple Silicon等）でx64ビルドを実行した際、以下のエラーが発生:

```
❌ EdgeChromium backendの読み込みに失敗: No module named 'clr'
```

### 環境情報（ログより）

```
OS: Windows 10.0.22631
アーキテクチャ: ARM64
Python: 3.12.8
PyInstaller: Yes
WebView2 Runtime: 142.0.3595.94 (インストール済み)
```

### 原因分析

1. GitHub Actionsは`windows-latest`（x64）でビルド
2. ARM64環境ではx64エミュレーションで動作
3. pywebviewのEdgeChromiumバックエンドが`clr`（pythonnet）をインポート失敗
4. pythonnetがPyInstallerビルドに正しくバンドルされていなかった

## 実施した修正

### 修正1: pythonnet正式バンドル（Codex指示）

**変更ファイル**:
- `release/windows/GaQ_Transcriber.spec`
- `release/windows/src/requirements.txt`
- `release/windows/src/main_app.py`

**実装内容**:

```python
# GaQ_Transcriber.spec
# pythonnet ランタイムファイル一式を収集（clr.py など）
try:
    pythonnet_datas = collect_data_files('pythonnet')
    datas += pythonnet_datas
except Exception as e:
    print(f"Warning: pythonnet datas 収集エラー: {e}")

# DLL収集にpythonnetを追加
for mod in ("pythoncom", "pywintypes", "pythonnet"):
    try:
        binaries.extend(collect_dynamic_libs(mod))
    except Exception as e:
        print(f"Warning: {mod} DLL収集エラー: {e}")

# hiddenimportsにclr, pythonnetを追加
hiddenimports = [
    ...
    'clr',
    'pythonnet',
]

# excludesを空にしてフォールバックを許容
excludes = []
```

```python
# requirements.txt
pythonnet>=3.0.3  # 追加
```

```python
# main_app.py - pythonnetインポート状態の個別ログ
PYTHONNET_IMPORT_OK = False
PYTHONNET_IMPORT_ERR = None
try:
    import clr  # pythonnet
    PYTHONNET_IMPORT_OK = True
except Exception as e:
    PYTHONNET_IMPORT_ERR = str(e)
```

### 修正2: webview.platforms網羅収集とUPX無効化（Codex指示）

**変更内容**:

```python
# GaQ_Transcriber.spec
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

hiddenimports = [
    ...
    # platforms 配下を網羅的に収集
    *collect_submodules('webview.platforms'),
    ...
]

# EXEのUPX圧縮を無効化（DLL解決リスク低減）
exe = EXE(
    ...
    upx=False,  # True → False
    ...
)
```

## ビルド履歴

| バージョン | Run ID | 状況 | 変更内容 |
|-----------|--------|------|---------|
| v1.2.3 #1 | 20187330002 | 成功 | pythonnetバンドル追加 |
| v1.2.3 #2 | 20187455880 | 成功 | collect_submodules + UPX無効化 |

## 確認ポイント（テスト環境用）

ビルド出力物で以下を確認:

1. `_internal/pythonnet/` ディレクトリの存在
2. `_internal/pythonnet/runtime/Python.Runtime.dll` の存在
3. `_internal/pythonnet/clr.py` の存在
4. `_internal/webview/platforms/winforms.py` の存在
5. `_internal/webview/platforms/edgechromium.py` の存在

ログで以下を確認:

```
pythonnet import ok: True
```

## 現在の状況

- v1.2.3 Draft Releaseが作成済み
- ARM64環境でのテスト待ち
- まだ動作確認できていない（Yoshihitoさんコメント）

## 次のステップ（Codexからの指示）

もし`pythonnet import ok: False`が続く場合:

1. `.NET Framework 4.8 (x64)` がARM64環境にインストールされているか確認
   - ARM64環境でのx64エミュレーション用に必要

2. 解決しない場合の選択肢:
   - ARM64ネイティブPython + pythonnetでARM64ビルドを作成
   - pythonnet/winforms経由を捨て、WebView2を直接ホストする別アプローチ

## リリースURL

**Draft Release**: https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.2.3

## アーキテクチャ対応状況

| 環境 | 対応状況 | 備考 |
|------|----------|------|
| Windows x64 (Intel/AMD) | ネイティブ動作 | 主要ターゲット |
| Windows ARM64 | x64エミュレーション | 動作確認中 |
| macOS (Apple Silicon) | ネイティブ動作 | ユニバーサルビルド |
| macOS (Intel) | ネイティブ動作 | |

---

**作成日時**: 2025-12-13 14:30 JST
**報告者**: Claude Code
