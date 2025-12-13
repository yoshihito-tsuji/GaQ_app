# -*- mode: python ; coding: utf-8 -*-

"""
GaQ Offline Transcriber - Windows版 PyInstaller設定ファイル
v1.2.3 - webview/platforms/winforms.py 収集対応
"""

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

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

# webview のデータファイルを収集
datas += collect_data_files('webview')

# webview/platforms を明示的に収集（collect_data_filesでは.pyが収集されない場合がある）
# 絶対パスで明示的に指定
webview_platforms_src = r'C:\Users\tsuji\Claude_Code\GaQ_app\release\windows\venv\Lib\site-packages\webview\platforms'
if os.path.exists(webview_platforms_src):
    datas += [(webview_platforms_src, 'webview/platforms')]
    print(f"INFO: Added webview/platforms from {webview_platforms_src}")

# pythonnet のデータファイルを収集
datas += collect_data_files('pythonnet')

# バイナリファイル
binaries = []

# pythonnet のバイナリを収集
binaries += collect_dynamic_libs('pythonnet')

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
    # pywebview winforms backend (Windows WebView2)
    'webview',
    'webview.platforms',
    'webview.platforms.winforms',
    'webview.platforms.edgechromium',
    # pythonnet 関連
    'clr',
    'clr_loader',
    'pythonnet',
    # .NET Forms 関連
    'System',
    'System.Windows',
    'System.Windows.Forms',
    'System.Drawing',
    # その他
    'bottle',
    'proxy_tools',
]

# webview のサブモジュールを全て収集
hiddenimports += collect_submodules('webview')

block_cipher = None

a = Analysis(
    [str(src_dir / 'main_app.py')],
    pathex=[],
    binaries=binaries,
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
