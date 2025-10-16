# -*- mode: python ; coding: utf-8 -*-

"""
GaQ Offline Transcriber - Mac版 PyInstaller設定ファイル
"""

import os
import sys
from pathlib import Path

# ソースコードディレクトリ
src_dir = Path('src')

# pywebviewパッケージのパスを取得
try:
    import webview
    webview_path = Path(webview.__file__).parent
    webview_js = webview_path / 'js'
except ImportError:
    webview_js = None

# faster-whisperパッケージのパスを取得
try:
    import faster_whisper
    faster_whisper_path = Path(faster_whisper.__file__).parent
    faster_whisper_assets = faster_whisper_path / 'assets'
except ImportError:
    faster_whisper_assets = None

# 追加データファイル（アイコン、静的ファイルなど）
datas = [
    (str(src_dir / 'icon.png'), '.'),  # アイコンファイル
    (str(src_dir / 'static' / 'icon.png'), 'static'),  # 静的ファイル用アイコン
]

# pywebviewのJSディレクトリを追加（必須）
if webview_js and webview_js.exists():
    datas.append((str(webview_js), 'webview/js'))

# faster-whisperのassetsフォルダを追加（ONNXモデルファイル含む）
# VAD（音声検出）に必須のsilero_encoder/decoder_v5.onnxファイルを含む
if faster_whisper_assets and faster_whisper_assets.exists():
    datas.append((str(faster_whisper_assets), 'faster_whisper/assets'))

# 追加の隠しインポート（完全な依存関係リスト）
hiddenimports = [
    # uvicorn関連（FastAPIサーバー実行に必須）
    'uvicorn',
    'uvicorn.server',
    'uvicorn.main',
    'uvicorn.config',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan.off',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.uvloop',

    # FastAPI関連
    'fastapi',
    'fastapi.staticfiles',
    'fastapi.responses',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.applications',
    'fastapi.routing',
    'fastapi.params',

    # Starlette関連（FastAPIのベース）
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.responses',
    'starlette.middleware',
    'starlette.middleware.cors',
    'starlette.staticfiles',

    # Pydantic関連（FastAPIのデータバリデーション）
    'pydantic',
    'pydantic.v1',
    'pydantic_core',

    # multipart/formdata処理
    'multipart',
    'python_multipart',

    # 非同期I/O
    'asyncio',
    'concurrent.futures',

    # faster-whisper関連
    'faster_whisper',
    'faster_whisper.transcribe',
    'faster_whisper.audio',
    'faster_whisper.vad',
    'faster_whisper.feature_extractor',
    'faster_whisper.tokenizer',

    # CTranslate2（faster-whisperのバックエンド）
    'ctranslate2',
    'ctranslate2._ext',

    # PyAV（音声処理）
    'av',
    'av.audio',
    'av.codec',
    'av.container',
    'av.format',
    'av.stream',

    # pywebview関連
    'webview',
    'webview.platforms',
    'webview.platforms.cocoa',

    # HTTP関連
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',

    # その他必須モジュール
    'multiprocessing',
    'threading',
    'pathlib',
    'json',
    'logging',
    'uuid',
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
    console=False,  # コンソールウィンドウを表示しない
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(src_dir / 'icon.png'),
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

app = BUNDLE(
    coll,
    name='GaQ Offline Transcriber.app',
    icon=str(src_dir / 'icon.png'),
    bundle_identifier='jp.ac.fun.tsuji.gaq',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.1.1',
        'CFBundleVersion': '1.1.1',
    },
)
