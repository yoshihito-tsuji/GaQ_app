# -*- mode: python ; coding: utf-8 -*-

"""
GaQ Offline Transcriber - Windows版 PyInstaller設定ファイル
"""

import os
from pathlib import Path

# ソースコードディレクトリ
src_dir = Path('src')

# 追加データファイル（アイコン、静的ファイルなど）
datas = [
    (str(src_dir / 'icon.png'), '.'),  # アイコンファイル
    (str(src_dir / 'static' / 'icon.png'), 'static'),  # 静的ファイル用アイコン
]

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
]

block_cipher = None

a = Analysis(
    [str(src_dir / 'main_app.py')],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
