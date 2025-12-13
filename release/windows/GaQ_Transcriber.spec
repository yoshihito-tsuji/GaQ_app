# -*- mode: python ; coding: utf-8 -*-

"""
GaQ Offline Transcriber - Windows版 PyInstaller設定ファイル
v1.2.8 - pythonnet 3.x PYTHONNET_PYDLL問題修正
"""

import os
import sys
import struct
import platform
import importlib
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# ========================================
# アーキテクチャ検証（x64必須）
# ========================================
print("=" * 60)
print("INFO: Verifying Python architecture...")
pointer_size = struct.calcsize("P") * 8
machine = platform.machine()
print(f"INFO: Python pointer size: {pointer_size}bit")
print(f"INFO: Platform machine: {machine}")
print(f"INFO: Python executable: {sys.executable}")

if pointer_size != 64:
    print(f"FATAL: 64-bit Python required, but running {pointer_size}-bit")
    print("FATAL: Build cannot continue with 32-bit Python")
    sys.exit(1)

print("INFO: Architecture check passed (64-bit)")
print("=" * 60)

# ========================================
# 必須パッケージの検証（失敗時はビルド停止）
# ========================================
print("INFO: Verifying required packages...")

# webview パッケージの検証
try:
    webview = importlib.import_module('webview')
    webview_version = getattr(webview, '__version__', 'unknown')
    print(f"INFO: webview version: {webview_version}")
    print(f"INFO: webview location: {webview.__file__}")
except ImportError as e:
    print(f"FATAL: Failed to import webview: {e}")
    print("FATAL: Build cannot continue without webview package")
    sys.exit(1)

# webview/platforms の存在確認（検証のみ、収集はcollect_data_filesに任せる）
webview_package_dir = Path(webview.__file__).parent
webview_platforms_dir = webview_package_dir / 'platforms'
if not webview_platforms_dir.exists():
    print(f"FATAL: webview/platforms directory not found at {webview_platforms_dir}")
    sys.exit(1)
else:
    platforms_files = list(webview_platforms_dir.glob('*.py'))
    print(f"INFO: webview/platforms found with {len(platforms_files)} files")
    winforms_exists = 'winforms.py' in [f.name for f in platforms_files]
    if not winforms_exists:
        print("FATAL: winforms.py not found in webview/platforms")
        sys.exit(1)
    print("INFO: winforms.py verified")

# pythonnet パッケージの検証
try:
    pythonnet = importlib.import_module('pythonnet')
    pythonnet_dir = Path(pythonnet.__file__).parent
    print(f"INFO: pythonnet location: {pythonnet.__file__}")

    # Python.Runtime.dll の存在とアーキテクチャ確認
    runtime_dll = pythonnet_dir / 'runtime' / 'Python.Runtime.dll'
    if not runtime_dll.exists():
        # 別のパスを探す
        for dll_path in pythonnet_dir.rglob('Python.Runtime.dll'):
            runtime_dll = dll_path
            break

    if runtime_dll.exists():
        print(f"INFO: Python.Runtime.dll found at {runtime_dll}")
        print(f"INFO: Python.Runtime.dll size: {runtime_dll.stat().st_size} bytes")
    else:
        print("WARNING: Python.Runtime.dll not found in pythonnet package")
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
# データファイル収集（フックベースに一本化）
# ========================================
datas = [
    (str(src_dir / 'icon.png'), '.'),  # アイコンファイル
    (str(src_dir / 'static' / 'icon.png'), 'static'),  # 静的ファイル用アイコン
]

# faster_whisperのアセットファイルを収集
faster_whisper_datas = collect_data_files('faster_whisper', includes=['assets/*'])
datas += faster_whisper_datas
print(f"INFO: faster_whisper data files: {len(faster_whisper_datas)} items")

# webview のデータファイルを収集（PyInstallerフック経由）
# collect_data_files は .py ファイルを含むすべてのデータを収集する
webview_datas = collect_data_files('webview')
datas += webview_datas
print(f"INFO: webview data files: {len(webview_datas)} items")

# webview/platforms を明示的に追加（.pyファイルがcollect_data_filesで漏れる場合の保険）
# ディレクトリ全体を webview/platforms として追加
datas += [(str(webview_platforms_dir), 'webview/platforms')]
print(f"INFO: Explicitly added webview/platforms from {webview_platforms_dir}")

# pythonnet のデータファイルを収集
pythonnet_datas = collect_data_files('pythonnet')
datas += pythonnet_datas
print(f"INFO: pythonnet data files: {len(pythonnet_datas)} items")

# clr_loader のデータファイルを収集（.NET runtimeファイル含む）
clr_loader_datas = collect_data_files('clr_loader')
datas += clr_loader_datas
print(f"INFO: clr_loader data files: {len(clr_loader_datas)} items")

# ========================================
# バイナリファイル収集
# ========================================
binaries = []

# pythonnet の動的ライブラリを収集
pythonnet_libs = collect_dynamic_libs('pythonnet')
binaries += pythonnet_libs
print(f"INFO: pythonnet dynamic libs: {len(pythonnet_libs)} items")
for lib_src, lib_dst in pythonnet_libs:
    print(f"INFO:   - {lib_src} -> {lib_dst}")

# clr_loader の動的ライブラリを収集
clr_loader_libs = collect_dynamic_libs('clr_loader')
binaries += clr_loader_libs
print(f"INFO: clr_loader dynamic libs: {len(clr_loader_libs)} items")
for lib_src, lib_dst in clr_loader_libs:
    print(f"INFO:   - {lib_src} -> {lib_dst}")

# ========================================
# Python DLL を明示的に収集（pythonnet 3.x 用）
# ========================================
# pythonnet 3.x は PYTHONNET_PYDLL 環境変数で Python DLL のパスを必要とする
python_dll_name = f'python{sys.version_info.major}{sys.version_info.minor}.dll'
python_dll_path = Path(sys.prefix) / python_dll_name
if python_dll_path.exists():
    binaries.append((str(python_dll_path), '.'))
    print(f"INFO: Added Python DLL: {python_dll_path}")
else:
    # base_prefix を試す（venv の場合）
    python_dll_path = Path(sys.base_prefix) / python_dll_name
    if python_dll_path.exists():
        binaries.append((str(python_dll_path), '.'))
        print(f"INFO: Added Python DLL from base_prefix: {python_dll_path}")
    else:
        print(f"WARNING: Python DLL not found: {python_dll_name}")

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

# ========================================
# ランタイムフック（pythonnet PYTHONNET_PYDLL 設定用）
# ========================================
runtime_hooks_list = [
    str(Path('hooks') / 'hook-pythonnet-runtime.py'),
]
print(f"INFO: Runtime hooks: {runtime_hooks_list}")

a = Analysis(
    [str(src_dir / 'main_app.py')],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks_list,
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
