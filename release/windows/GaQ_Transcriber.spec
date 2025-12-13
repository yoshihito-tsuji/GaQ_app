# -*- mode: python ; coding: utf-8 -*-

"""
GaQ Offline Transcriber - Windows版 PyInstaller設定ファイル

方針:
- EdgeChromium(WebView2) を第一候補とする
- それでも失敗した場合に winforms/pythonnet フォールバックを許容し、起動を優先
- EdgeChromium依存のpywin32、フォールバック用pythonnetのDLLを明示収集
"""

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# ソースコードディレクトリ
src_dir = Path('src')

# 追加データファイル（アイコン、静的ファイルなど）
datas = [
    (str(src_dir / 'icon.png'), '.'),  # アイコンファイル
    (str(src_dir / 'static' / 'icon.png'), 'static'),  # 静的ファイル用アイコン
]

# faster_whisperのアセットファイルを収集
faster_whisper_datas = collect_data_files('faster_whisper', includes=['assets/*'])
datas += faster_whisper_datas

# 追加バイナリ（DLL）: EdgeChromium用pywin32を明示収集（pythonnetは同梱しない）
binaries = []
for mod in ("pythoncom", "pywintypes"):
    try:
        binaries.extend(collect_dynamic_libs(mod))
    except Exception as e:
        print(f"Warning: {mod} DLL収集エラー: {e}")

# 追加の隠しインポート（必要に応じて追加）
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'faster_whisper',
    'ctranslate2',
    'av',
    # pywebview (EdgeChromiumのみを使用。winforms/pythonnetは除外)
    'webview',
    'webview.platforms',
    'webview.platforms.edgechromium',
    # pywin32 依存
    'pythoncom',
    'pywintypes',
    'win32api',
    'win32com',
    'win32com.client',
]

block_cipher = None

# winforms / pythonnet へのフォールバックを禁止
excludes = [
    'pythonnet',
    'clr',
    'clr_loader',
    'webview.platforms.winforms',
    'webview.platforms.winforms_app',
]

a = Analysis(
    [str(src_dir / 'main_app.py')],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(src_dir / 'runtime_hook_pywebview.py')],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GaQ_Transcriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,  # コンソールウィンドウを表示しない
    disable_windowed_traceback=False,
    target_arch='x64',  # Windows x64アーキテクチャ
    codesign_identity=None,
    entitlements_file=None,
    icon=str(src_dir / 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GaQ_Transcriber',
)
