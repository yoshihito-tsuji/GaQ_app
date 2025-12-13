# -*- mode: python ; coding: utf-8 -*-

"""
GaQ Offline Transcriber - Windows版 PyInstaller設定ファイル

依存DLL:
- VC++ Runtime (vcruntime140.dll, vcruntime140_1.dll, msvcp140.dll)
- UCRT (ucrtbase.dll)
- OpenSSL (libcrypto-*.dll, libssl-*.dll)
- FFmpeg関連 (PyAVがバンドル)

これらはPyInstallerが自動収集するが、確実にバンドルされるよう
binaries設定で明示的に指定することも可能。
"""

import os
import sys
import glob
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# ソースコードディレクトリ
src_dir = Path('src')

# ===== 追加バイナリ（DLL）の収集 =====
binaries = []

# VC++ Runtime / UCRT / OpenSSL DLLの明示的収集
# これらはPyInstallerが通常自動収集するが、念のため手動でも確認
def find_system_dlls():
    """システムDLLを検索してバンドルリストに追加"""
    dll_patterns = [
        # VC++ Runtime
        'vcruntime140.dll',
        'vcruntime140_1.dll',
        'msvcp140.dll',
        'msvcp140_1.dll',
        # UCRT
        'ucrtbase.dll',
        # OpenSSL (Pythonディストリビューションに含まれる)
        'libcrypto-*.dll',
        'libssl-*.dll',
    ]

    search_paths = [
        Path(sys.base_prefix) / 'DLLs',
        Path(sys.base_prefix),
        Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'System32',
    ]

    found_dlls = []
    for pattern in dll_patterns:
        for search_path in search_paths:
            if search_path.exists():
                matches = list(search_path.glob(pattern))
                for match in matches:
                    if match.is_file():
                        found_dlls.append((str(match), '.'))
                        break  # 最初に見つかったものを使用

    return found_dlls

# システムDLLを収集（PyInstallerの自動収集を補完）
try:
    system_dlls = find_system_dlls()
    binaries.extend(system_dlls)
except Exception as e:
    print(f"Warning: システムDLL収集エラー: {e}")

# ctranslate2のDLLを明示的に収集
try:
    ct2_libs = collect_dynamic_libs('ctranslate2')
    binaries.extend(ct2_libs)
except Exception as e:
    print(f"Warning: ctranslate2 DLL収集エラー: {e}")

# PyAV (av) のDLLを明示的に収集
try:
    av_libs = collect_dynamic_libs('av')
    binaries.extend(av_libs)
except Exception as e:
    print(f"Warning: av DLL収集エラー: {e}")

# ===== データファイルの収集 =====
# 追加データファイル（アイコン、静的ファイルなど）
datas = [
    (str(src_dir / 'icon.png'), '.'),  # アイコンファイル
    (str(src_dir / 'static' / 'icon.png'), 'static'),  # 静的ファイル用アイコン
]

# faster_whisperのアセットファイルを収集
faster_whisper_datas = collect_data_files('faster_whisper', includes=['assets/*'])
datas += faster_whisper_datas

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
    # pywebview (EdgeChromium backend for Windows)
    'webview',
    'webview.platforms',
    'webview.platforms.edgechromium',
    'bottle',
    'proxy_tools',
]

block_cipher = None

a = Analysis(
    [str(src_dir / 'main_app.py')],
    pathex=[],
    binaries=binaries,  # 明示的に収集したDLLを含める
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
