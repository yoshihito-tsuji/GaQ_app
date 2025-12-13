# -*- mode: python ; coding: utf-8 -*-

"""
GaQ Offline Transcriber - Windows版 PyInstaller設定ファイル
v1.2.6 - CI堅牢化（importlib経由でwebview検証、失敗時はビルド停止）
"""

import os
import sys
import importlib
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# ========================================
# 必須パッケージの検証（失敗時はビルド停止）
# ========================================
print("=" * 60)
print("INFO: Verifying required packages...")

# webview パッケージの検証
try:
    webview = importlib.import_module('webview')
    # webviewはバージョン属性がない場合がある
    webview_version = getattr(webview, '__version__', 'unknown')
    print(f"INFO: webview version: {webview_version}")
    print(f"INFO: webview location: {webview.__file__}")
except ImportError as e:
    print(f"FATAL: Failed to import webview: {e}")
    print("FATAL: Build cannot continue without webview package")
    sys.exit(1)

# webview/platforms の存在確認
webview_package_dir = Path(webview.__file__).parent
webview_platforms_dir = webview_package_dir / 'platforms'
if not webview_platforms_dir.exists():
    print(f"FATAL: webview/platforms directory not found at {webview_platforms_dir}")
    sys.exit(1)
else:
    platforms_files = list(webview_platforms_dir.glob('*.py'))
    print(f"INFO: webview/platforms found with {len(platforms_files)} files")
    if 'winforms.py' not in [f.name for f in platforms_files]:
        print("WARNING: winforms.py not found in webview/platforms")

# pythonnet パッケージの検証
try:
    pythonnet = importlib.import_module('pythonnet')
    print(f"INFO: pythonnet location: {pythonnet.__file__}")
except ImportError as e:
    print(f"FATAL: Failed to import pythonnet: {e}")
    sys.exit(1)

# clr_loader パッケージの検証
try:
    clr_loader = importlib.import_module('clr_loader')
    clr_loader_version = getattr(clr_loader, '__version__', 'unknown')
    print(f"INFO: clr_loader version: {clr_loader_version}")
except ImportError as e:
    print(f"FATAL: Failed to import clr_loader: {e}")
    sys.exit(1)

print("INFO: All required packages verified successfully")
print("=" * 60)

# ========================================
# ソースコードディレクトリ
# ========================================
src_dir = Path('src')

# ========================================
# データファイル収集
# ========================================
datas = [
    (str(src_dir / 'icon.png'), '.'),  # アイコンファイル
    (str(src_dir / 'static' / 'icon.png'), 'static'),  # 静的ファイル用アイコン
]

# faster_whisperのアセットファイルを収集
faster_whisper_datas = collect_data_files('faster_whisper', includes=['assets/*'])
datas += faster_whisper_datas

# webview のデータファイルを収集（PyInstallerフック経由）
datas += collect_data_files('webview')

# webview/platforms を明示的に収集（collect_data_filesでは.pyが収集されない場合がある）
# 上記で検証済みのパスを使用
datas += [(str(webview_platforms_dir), 'webview/platforms')]
print(f"INFO: Added webview/platforms from {webview_platforms_dir}")

# pythonnet のデータファイルを収集
datas += collect_data_files('pythonnet')

# ========================================
# バイナリファイル収集
# ========================================
binaries = []
binaries += collect_dynamic_libs('pythonnet')

# ========================================
# 隠しインポート
# ========================================
hiddenimports = [
    # uvicorn
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
    # faster_whisper
    'faster_whisper',
    'ctranslate2',
    'av',
    # pywebview winforms backend (Windows WebView2) - winforms固定
    'webview',
    'webview.platforms',
    'webview.platforms.winforms',  # 必須: Windows WebView2バックエンド
    'webview.platforms.edgechromium',
    # pythonnet 関連
    'clr',
    'clr_loader',
    'pythonnet',
    # .NET Forms 関連（pythonnet経由で使用）
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
print(f"INFO: Total hiddenimports: {len(hiddenimports)}")

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
    excludes=[
        'cefpython3',  # 旧CEFバックエンド（不要・競合回避）
    ],
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
