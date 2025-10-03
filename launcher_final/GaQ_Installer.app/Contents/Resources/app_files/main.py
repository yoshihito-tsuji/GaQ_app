"""
FastAPI メインアプリケーション
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import uvicorn
from config import ALLOWED_EXTENSIONS, AVAILABLE_MODELS, DEFAULT_MODEL, HOST, PORT, UPLOAD_DIR
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from transcribe import transcription_service

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション
app = FastAPI(
    title="GaQ Transcription API", description="音声文字起こしAPI (faster-whisper)", version="2.0.0"
)

# CORS設定（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルの配信
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# グローバル変数：最後の文字起こし結果を保存
last_transcription = {"text": "", "processing_time": 0, "timestamp": None}


def cleanup_file(file_path: Path):
    """アップロードファイルを削除"""
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"一時ファイル削除: {file_path.name}")
    except Exception as e:
        logger.error(f"ファイル削除エラー: {e}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """ルートエンドポイント（簡易UIを返す）"""
    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GaQ Offline Transcriber - オフラインAI文字おこし</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🦜</text></svg>">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(to bottom right, #ffffff 0%, #f5faf3 30%, #e8f5e0 70%, #d4ecc8 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 8px 32px rgba(90, 146, 69, 0.15);
            }
            h1 {
                color: #5a9245;
                margin-bottom: 10px;
                font-size: 32px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .logo-icon {
                width: 48px;
                height: 48px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 3px dashed #7ab55c;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                margin-bottom: 20px;
            }
            .upload-area:hover {
                background: #f5faf3;
                border-color: #5a9245;
            }
            .upload-area.dragover {
                background: #f5faf3;
                border-color: #5a9245;
            }
            input[type="file"] { display: none; }
            .file-name {
                margin-top: 15px;
                color: #5a9245;
                font-weight: bold;
            }
            select {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                margin-bottom: 20px;
                cursor: pointer;
            }
            /* モデル選択ドロップダウン（モデル管理ボタンの隣） */
            #modelSelect {
                flex: 1;
                min-width: 0;
                height: 36px;
                box-sizing: border-box;
                padding: 8px 12px;
                font-size: 14px;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                background-color: white;
                cursor: pointer;
                transition: border-color 0.3s;
                margin-bottom: 0;
            }
            #modelSelect:focus {
                outline: none;
                border-color: #7ab55c;
            }
            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #7ab55c 0%, #5a9245 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(90, 146, 69, 0.25);
                background: linear-gradient(135deg, #8bc46d 0%, #6aa356 100%);
            }
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .credit {
                text-align: center;
                font-size: 14px;
                color: #666;
                margin-top: 8px;
            }
            .progress {
                margin-top: 20px;
                padding: 15px;
                background: #f5faf3;
                border-radius: 8px;
                border: 1px solid #e8f5e0;
                text-align: center;
                display: none;
            }
            .progress-bar-container {
                width: 100%;
                height: 30px;
                background-color: #e5e7eb;
                border-radius: 15px;
                overflow: hidden;
                margin: 15px 0;
            }
            .progress-bar-fill {
                height: 100%;
                width: 0%;
                background: linear-gradient(135deg, #7ab55c 0%, #5a9245 100%);
                transition: width 0.3s ease;
                border-radius: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
                position: relative;
                overflow: hidden;
            }
            .progress-bar-fill::after {
                content: "";
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg,
                    rgba(255, 255, 255, 0) 0%,
                    rgba(255, 255, 255, 0.5) 50%,
                    rgba(255, 255, 255, 0) 100%
                );
                animation: shine 4s ease-in-out infinite;
            }
            @keyframes shine {
                0% {
                    left: -100%;
                }
                50% {
                    left: 100%;
                }
                100% {
                    left: 100%;
                }
            }
            .progress-status {
                margin-top: 10px;
                color: #5a9245;
                font-weight: bold;
                white-space: pre-line;
                line-height: 1.6;
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: #f5faf3;
                border-radius: 8px;
                border: 1px solid #e8f5e0;
                display: none;
            }
            .result-text {
                white-space: pre-wrap;
                line-height: 1.8;
                color: #333;
            }
            .stats {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 2px solid #ddd;
                color: #666;
                font-size: 14px;
            }
            .copy-btn {
                margin-top: 15px;
                background: #7ab55c;
            }
            .copy-btn:hover {
                background: #6aa356;
            }
            .save-btn {
                width: 100%;
                padding: 12px;
                background: #7ab55c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 15px;
                transition: background 0.3s;
            }
            .save-btn:hover {
                background: #5a9245;
            }
            .save-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            /* モデル管理ボタン（モデル選択の横） */
            .model-manage-btn-inline {
                background: rgba(255, 255, 255, 0.95);
                color: #7ab55c;
                border: 2px solid #7ab55c;
                padding: 8px 12px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 600;
                transition: all 0.3s;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                white-space: nowrap;
                flex-shrink: 0;
                max-width: 150px;
                min-width: 120px;
                height: 36px;
                box-sizing: border-box;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .model-manage-btn-inline:hover {
                background: #7ab55c;
                color: white;
                box-shadow: 0 4px 12px rgba(122, 181, 92, 0.3);
            }
            /* モーダル */
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
            }
            .modal-content {
                background-color: white;
                margin: 10% auto;
                padding: 0;
                border-radius: 12px;
                width: 80%;
                max-width: 600px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }
            .modal-header {
                padding: 20px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-header h2 {
                margin: 0;
                color: #7ab55c;
                flex: 1;
            }
            .modal-close {
                background: none;
                border: none;
                font-size: 28px;
                cursor: pointer;
                color: #999;
                padding: 0;
                margin-left: auto;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-close:hover {
                color: #333;
            }
            .modal-body {
                padding: 20px;
            }
            /* モデルリスト */
            .model-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            .model-info {
                flex: 1;
                margin-right: 15px;
            }
            .model-name {
                font-weight: bold;
                font-size: 16px;
                color: #333;
            }
            .model-details {
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }
            .model-status {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
            .model-status.downloaded {
                background: #e8f5e9;
                color: #2e7d32;
            }
            .model-status.not-downloaded {
                background: #fff3e0;
                color: #e65100;
            }
            .delete-btn {
                background: #f44336 !important;
                color: white !important;
                border: none !important;
                padding: 6px 12px !important;
                border-radius: 6px !important;
                cursor: pointer !important;
                font-size: 12px !important;
                white-space: nowrap !important;
                min-width: 70px !important;
                max-width: 100px !important;
            }
            .delete-btn:hover {
                background: #d32f2f !important;
            }
            .delete-btn:disabled {
                background: #ccc !important;
                cursor: not-allowed !important;
                font-size: 11px !important;
                padding: 6px 10px !important;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>
                <img src="/static/icon.png" alt="GaQ Logo" class="logo-icon">
                GaQ Offline Transcriber
            </h1>
            <p class="subtitle">オフラインAI文字おこしアプリケーション</p>

            <div class="upload-area" id="uploadArea">
                <p>📁 音声ファイルをドラッグ&ドロップ<br>または<br>クリックして選択</p>
                <div class="file-name" id="fileName"></div>
            </div>

            <input type="file" id="fileInput" accept="audio/*,video/*">

            <div style="display: flex; align-items: stretch; gap: 10px; margin-bottom: 20px;">
                <select id="modelSelect">
                    <option value="medium">標準精度（Medium）- バランス重視【推奨設定】</option>
                    <option value="large-v3">高精度（Large-v3）- 精度最優先（PC高負荷・句読点なし）</option>
                </select>
                <button id="modelManageBtn" class="model-manage-btn-inline" type="button">
                    ⚙️ モデル管理
                </button>
            </div>

            <button id="transcribeBtn" disabled>文字起こし開始</button>

            <p class="credit">公立はこだて未来大学：辻研究室（tsuji-lab.net）</p>

            <div class="progress" id="progress">
                <p>🔄 処理中...</p>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" id="progressBarFill">0%</div>
                </div>
                <p class="progress-status" id="progressStatus">準備中...</p>
            </div>

            <div class="result" id="result">
                <h3>📝 文字起こし結果</h3>
                <div class="result-text" id="resultText"></div>
                <div class="stats" id="stats"></div>
                <button class="copy-btn" onclick="copyResult()">📋 コピー</button>
                <button class="save-btn" id="saveBtn" style="display: none;">💾 結果を保存（txt形式）</button>
            </div>
        </div>

        <!-- モデル管理モーダル -->
        <div id="modelModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>モデル管理</h2>
                    <button class="modal-close" id="modalClose">&times;</button>
                </div>
                <div class="modal-body" id="modelList">
                    <!-- JavaScriptで動的に生成 -->
                </div>
            </div>
        </div>

        <script>
            console.log('GaQ JavaScript starting...');

            var uploadArea = document.getElementById('uploadArea');
            var fileInput = document.getElementById('fileInput');
            var fileName = document.getElementById('fileName');
            var transcribeBtn = document.getElementById('transcribeBtn');
            var progress = document.getElementById('progress');
            var resultDiv = document.getElementById('result');
            var resultText = document.getElementById('resultText');
            var stats = document.getElementById('stats');
            var modelSelect = document.getElementById('modelSelect');
            var saveBtn = document.getElementById('saveBtn');
            var modelManageBtn = document.getElementById('modelManageBtn');
            var modelModal = document.getElementById('modelModal');
            var modalClose = document.getElementById('modalClose');
            var modelList = document.getElementById('modelList');

            // 要素の存在確認（デバッグ用）
            console.log('uploadArea:', uploadArea);
            console.log('fileInput:', fileInput);
            console.log('transcribeBtn:', transcribeBtn);

            if (!uploadArea || !fileInput || !transcribeBtn) {
                console.error('Required elements not found!');
                alert('エラー: ページの読み込みに失敗しました。ページを再読み込みしてください。');
            }

            var selectedFile = null;

            // デフォルト動作を完全に防止する関数
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            // ページ全体でドラッグ&ドロップのデフォルト動作を防止（Safari対応）
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function(eventName) {
                document.body.addEventListener(eventName, preventDefaults, false);
            });

            // クリックでファイル選択（Safari対応：イベント伝播を防止）
            uploadArea.addEventListener('click', function(e) {
                console.log('uploadArea clicked');
                e.preventDefault();
                e.stopPropagation();
                console.log('fileInput.click() executing');
                fileInput.click();
            });

            // ドラッグ進入時の処理
            uploadArea.addEventListener('dragenter', function(e) {
                preventDefaults(e);
                uploadArea.classList.add('dragover');
            });

            // ドラッグオーバー時の処理
            uploadArea.addEventListener('dragover', function(e) {
                preventDefaults(e);
                uploadArea.classList.add('dragover');
            });

            // ドラッグ退出時の処理
            uploadArea.addEventListener('dragleave', function(e) {
                preventDefaults(e);
                uploadArea.classList.remove('dragover');
            });

            // ドロップ時の処理
            uploadArea.addEventListener('drop', function(e) {
                preventDefaults(e);
                uploadArea.classList.remove('dragover');
                var files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFile(files[0]);
                }
            });

            // ファイル選択時の処理
            fileInput.addEventListener('change', function(e) {
                console.log('fileInput change event fired', e.target.files);
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });

            // ファイル処理関数
            function handleFile(file) {
                console.log('handleFile executing:', file.name, file.type);

                // 音声/動画ファイルかチェック
                var validTypes = ['audio/', 'video/'];
                var isValid = validTypes.some(function(type) {
                    return file.type.indexOf(type) === 0;
                });

                if (!isValid && file.type !== '') {
                    console.warn('Invalid file type:', file.type);
                    alert('音声ファイルまたは動画ファイルを選択してください');
                    return;
                }

                selectedFile = file;
                fileName.textContent = '✅ ' + file.name;
                transcribeBtn.disabled = false;
                resultDiv.style.display = 'none';

                console.log('File selected successfully:', file.name);
            }

            // 文字起こし実行（SSEでリアルタイム進捗表示）
            transcribeBtn.addEventListener('click', function() {
                if (!selectedFile) {
                    alert('ファイルを選択してください');
                    return;
                }

                var model = modelSelect.value;

                // モデル存在確認
                fetch('/check-model/' + model)
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (!data.exists) {
                            var message = 'モデル「' + model + '」をダウンロードします（約' + data.size_gb + 'GB、数分かかります）。\\n続行しますか？';

                            if (confirm(message)) {
                                startTranscription(selectedFile, model);
                            }
                        } else {
                            startTranscription(selectedFile, model);
                        }
                    })
                    .catch(function(error) {
                        console.error('エラー:', error);
                        alert('モデルチェックに失敗しました');
                    });
            });

            // 文字起こし実行関数
            function startTranscription(file, model) {
                console.log('文字起こし開始:', file.name, 'モデル:', model);

                transcribeBtn.disabled = true;
                progress.style.display = 'block';
                resultDiv.style.display = 'none';

                // プログレスバーをリセット
                var progressBarFill = document.getElementById('progressBarFill');
                var progressStatus = document.getElementById('progressStatus');
                progressBarFill.style.width = '0%';
                progressBarFill.textContent = '0%';
                progressStatus.textContent = '準備中...';

                var formData = new FormData();
                formData.append('file', file);
                formData.append('model', model);

                fetch('/transcribe-stream', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    var reader = response.body.getReader();
                    var decoder = new TextDecoder();
                    var buffer = '';

                    function processStream() {
                        return reader.read().then(function(result) {
                            if (result.done) {
                                return;
                            }

                            // 受信したデータをデコード
                            buffer += decoder.decode(result.value, { stream: true });

                            // 改行で分割してイベントを処理
                            var lines = buffer.split("\\n");
                            buffer = lines.pop(); // 最後の不完全な行は保持

                            for (var i = 0; i < lines.length; i++) {
                                var line = lines[i];
                                if (line.indexOf('data: ') === 0) {
                                    var dataStr = line.slice(6);
                                    if (dataStr.trim()) {
                                        var data = JSON.parse(dataStr);

                                        if (data.error) {
                                            alert('エラー: ' + data.error);
                                            progress.style.display = 'none';
                                            transcribeBtn.disabled = false;
                                            return;
                                        }

                                        if (data.progress !== undefined) {
                                            // プログレスバー更新
                                            progressBarFill.style.width = data.progress + '%';
                                            progressBarFill.textContent = data.progress + '%';

                                            if (data.status) {
                                                progressStatus.textContent = data.status;
                                            }
                                        }

                                        if (data.result && data.result.success) {
                                            // 完了時の処理
                                            resultText.textContent = data.result.text;
                                            stats.innerHTML =
                                                '<strong>文字数:</strong> ' + data.result.char_count.toLocaleString() + '文字 | ' +
                                                '<strong>処理時間:</strong> ' + data.result.duration.toFixed(1) + '秒 | ' +
                                                '<strong>セグメント:</strong> ' + data.result.segment_count;
                                            resultDiv.style.display = 'block';
                                            saveBtn.style.display = 'block';
                                            progress.style.display = 'none';
                                            transcribeBtn.disabled = false;
                                        }
                                    }
                                }
                            }

                            return processStream();
                        });
                    }

                    return processStream();
                })
                .catch(function(error) {
                    alert('エラー: ' + error.message);
                    progress.style.display = 'none';
                    transcribeBtn.disabled = false;
                });
            }

            function copyResult() {
                navigator.clipboard.writeText(resultText.textContent);
                alert('文字起こし結果をコピーしました。\n適切な位置にペーストしてください');
            }

            // 保存ボタンのイベントリスナー
            saveBtn.addEventListener('click', function() {
                saveBtn.disabled = true;
                saveBtn.textContent = '保存中...';

                fetch('/save-transcription', {
                    method: 'POST'
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('保存に失敗しました');
                    }
                    return response.blob();
                })
                .then(function(blob) {
                    // ダウンロード
                    var url = window.URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url;

                    // ファイル名生成（タイムスタンプ付き）
                    var now = new Date();
                    var timestamp = now.getFullYear() +
                                   ('0' + (now.getMonth() + 1)).slice(-2) +
                                   ('0' + now.getDate()).slice(-2) + '_' +
                                   ('0' + now.getHours()).slice(-2) +
                                   ('0' + now.getMinutes()).slice(-2) +
                                   ('0' + now.getSeconds()).slice(-2);
                    a.download = 'transcription_' + timestamp + '.txt';

                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);

                    saveBtn.disabled = false;
                    saveBtn.textContent = '💾 結果を保存（txt形式）';
                })
                .catch(function(error) {
                    console.error('保存エラー:', error);
                    alert('保存に失敗しました');
                    saveBtn.disabled = false;
                    saveBtn.textContent = '💾 結果を保存（txt形式）';
                });
            });

            // モデル選択変更時のイベントハンドラ
            modelSelect.addEventListener('change', function() {
                console.log('Model select changed!');
                var selectedModel = modelSelect.value;
                console.log('Selected model:', selectedModel);
                checkModelStatus(selectedModel);
            });

            // モデル状態チェック関数
            function checkModelStatus(modelName) {
                console.log('Checking model status:', modelName);
                fetch('/check-model/' + modelName)
                    .then(function(response) {
                        console.log('Response received:', response);
                        return response.json();
                    })
                    .then(function(data) {
                        console.log('Model data:', data);
                        if (!data.exists) {
                            // モデルが未ダウンロード
                            console.log('Model NOT exists - showing dialog');
                            var message = 'モデル「' + modelName + '」は未ダウンロードです。\\n' +
                                         'サイズ: 約' + data.size_gb + 'GB\\n\\n' +
                                         '初回使用時に自動でダウンロードされます（数分かかります）。\\n' +
                                         '続行しますか？';

                            if (!confirm(message)) {
                                // キャンセルされた場合、mediumに戻す
                                modelSelect.value = 'medium';
                            }
                        } else {
                            console.log('Model exists - no dialog shown');
                        }
                    })
                    .catch(function(error) {
                        console.error('モデルチェックエラー:', error);
                    });
            }

            console.log('All event listeners registered successfully');

            // モデル管理ボタンのイベント
            console.log('modelManageBtn:', modelManageBtn);
            console.log('modelModal:', modelModal);

            if (modelManageBtn) {
                modelManageBtn.addEventListener('click', function(e) {
                    console.log('🔧 モデル管理ボタンがクリックされました！');
                    e.preventDefault();
                    console.log('About to call openModelModal()');
                    console.log('typeof openModelModal:', typeof openModelModal);
                    openModelModal();
                });
                console.log('✅ モデル管理ボタンのイベントリスナー設定完了');
            } else {
                console.error('❌ modelManageBtn が見つかりません！');
            }

            // モーダルを開く
            function openModelModal() {
                console.log('📂 openModelModal() が呼ばれました');
                console.log('modelModal.style.display before:', modelModal.style.display);
                loadModels();
                modelModal.style.display = 'block';
                console.log('modelModal.style.display after:', modelModal.style.display);
            }

            // モーダルを閉じる
            modalClose.addEventListener('click', function() {
                modelModal.style.display = 'none';
            });

            // モーダル外をクリックで閉じる
            window.addEventListener('click', function(e) {
                if (e.target === modelModal) {
                    modelModal.style.display = 'none';
                }
            });

            // モデル一覧を読み込む
            function loadModels() {
                fetch('/models')
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        displayModels(data.models);
                    })
                    .catch(function(error) {
                        console.error('モデル一覧取得エラー:', error);
                        modelList.innerHTML = '<p>エラーが発生しました</p>';
                    });
            }

            // モデル一覧を表示
            function displayModels(models) {
                var html = '';

                models.forEach(function(model) {
                    var statusClass = model.info.exists ? 'downloaded' : 'not-downloaded';
                    var statusText = model.info.exists ? 'ダウンロード済み' : '未ダウンロード';

                    html += '<div class="model-item">';
                    html += '  <div class="model-info">';
                    html += '    <div class="model-name">' + model.display_name + '</div>';
                    html += '    <div class="model-details">';
                    html += '      サイズ: 約' + model.size_gb + 'GB';
                    html += '      <span class="model-status ' + statusClass + '">' + statusText + '</span>';
                    html += '    </div>';
                    html += '  </div>';

                    if (model.deletable && model.info.exists) {
                        html += '  <button class="delete-btn" data-model-name="' + model.name + '">🗑️ 削除</button>';
                    } else if (!model.deletable) {
                        html += '  <button class="delete-btn" disabled>削除不可</button>';
                    } else {
                        html += '  <div style="width: 80px;"></div>';  // スペース確保
                    }

                    html += '</div>';
                });

                modelList.innerHTML = html;

                // 削除ボタンにイベントリスナーを追加
                var deleteButtons = modelList.querySelectorAll('.delete-btn[data-model-name]');
                deleteButtons.forEach(function(button) {
                    button.addEventListener('click', function() {
                        deleteModel(this.getAttribute('data-model-name'));
                    });
                });
            }

            // モデルを削除
            function deleteModel(modelName) {
                if (!confirm('モデル「' + modelName + '」を削除しますか？\\n\\n削除後は再度ダウンロードが必要です。')) {
                    return;
                }

                fetch('/models/' + modelName, {
                    method: 'DELETE'
                })
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        alert(data.message);
                        loadModels();  // 一覧を再読み込み
                    } else {
                        alert('エラー: ' + data.message);
                    }
                })
                .catch(function(error) {
                    console.error('削除エラー:', error);
                    alert('削除に失敗しました');
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "service": "GaQ Transcription API"}


@app.get("/models")
async def get_models():
    """
    利用可能なモデル一覧（詳細情報付き）

    Returns:
        モデル情報のリスト（ダウンロード状況、サイズなど）
    """
    from transcribe import check_model_exists

    models = [
        {
            "name": "medium",
            "display_name": "標準精度（Medium）",
            "size_gb": 1.5,
            "deletable": False,  # デフォルトモデルは削除不可
            "info": check_model_exists("medium"),
        },
        {
            "name": "large-v3",
            "display_name": "高精度（Large-v3）",
            "size_gb": 2.9,
            "deletable": True,
            "info": check_model_exists("large-v3"),
        },
    ]

    return {"models": models, "default": DEFAULT_MODEL}


@app.get("/check-model/{model_name}")
async def check_model(model_name: str):
    """
    モデルの存在確認

    Args:
        model_name: モデル名（medium, large-v3など）

    Returns:
        モデルの存在状況とサイズ情報
    """
    from transcribe import check_model_exists

    result = check_model_exists(model_name)
    return JSONResponse(content=result)


@app.post("/transcribe")
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    model: Annotated[str, Form()] = DEFAULT_MODEL,
):
    """
    音声ファイルを文字起こし

    Args:
        file: 音声ファイル
        model: 使用するモデル（medium, large-v3）

    Returns:
        文字起こし結果
    """
    try:
        # ファイル拡張子チェック
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, detail=f"対応していないファイル形式です: {file_ext}"
            )

        # モデル名チェック
        if model not in AVAILABLE_MODELS:
            raise HTTPException(status_code=400, detail=f"無効なモデル名です: {model}")

        # 一時ファイルとして保存
        file_id = str(uuid.uuid4())
        temp_file = UPLOAD_DIR / f"{file_id}{file_ext}"

        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"ファイル保存完了: {temp_file.name} ({len(content)} bytes)")

        # 文字起こし実行
        result = transcription_service.transcribe(
            audio_path=temp_file, model_name=model, language="ja"
        )

        # バックグラウンドでファイル削除
        background_tasks.add_task(cleanup_file, temp_file)

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/transcribe-stream")
async def transcribe_stream(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    model: Annotated[str, Form()] = DEFAULT_MODEL,
):
    """
    音声ファイルを文字起こし（進捗をリアルタイムで送信）

    Args:
        file: 音声ファイル
        model: 使用するモデル（medium, large-v3）

    Returns:
        Server-Sent Eventsストリーム
    """

    async def event_stream():
        temp_file = None
        try:
            # ファイル拡張子チェック
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                yield f"data: {json.dumps({'error': f'対応していないファイル形式です: {file_ext}'})}\n\n"
                return

            # モデル名チェック
            if model not in AVAILABLE_MODELS:
                yield f"data: {json.dumps({'error': f'無効なモデル名です: {model}'})}\n\n"
                return

            # 進捗: ファイル保存開始
            yield f"data: {json.dumps({'progress': 0, 'status': 'ファイル保存中...'})}\n\n"
            await asyncio.sleep(0.1)  # イベント送信を確実にするための待機

            # 一時ファイルとして保存
            file_id = str(uuid.uuid4())
            temp_file = UPLOAD_DIR / f"{file_id}{file_ext}"

            with open(temp_file, "wb") as f:
                content = await file.read()
                f.write(content)

            logger.info(f"ファイル保存完了: {temp_file.name} ({len(content)} bytes)")

            # 進捗: モデル読み込み開始
            # モデル存在チェック
            from transcribe import check_model_exists

            model_info = check_model_exists(model)
            if not model_info["exists"]:
                # モデルが未ダウンロード - ダウンロードに数分かかることを明示
                status_msg = f"モデルをダウンロード中（約{model_info['size_gb']}GB）\nしばらくお待ちください（数分かかります）\nダウンロード後、自動的に文字起こしを開始します"
                yield f"data: {json.dumps({'progress': 5, 'status': status_msg})}\n\n"
            else:
                yield f"data: {json.dumps({'progress': 5, 'status': '音声認識モデル起動中...'})}\n\n"
            await asyncio.sleep(0.1)

            # 進捗コールバック関数（同期関数から非同期で呼び出し可能にする）
            progress_queue = asyncio.Queue()
            loop = asyncio.get_event_loop()

            def progress_callback(progress: float):
                """進捗を受け取ってキューに入れる"""
                percentage = int(progress * 100)
                # キューに進捗を追加（イベントループ経由で安全に追加）
                try:
                    loop.call_soon_threadsafe(progress_queue.put_nowait, percentage)
                except Exception as e:
                    logger.warning(f"進捗通知エラー: {e}")

            # 文字起こしを別スレッドで実行
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 文字起こしタスクを開始
                future = executor.submit(
                    transcription_service.transcribe,
                    audio_path=temp_file,
                    model_name=model,
                    language="ja",
                    progress_callback=progress_callback,
                )

                # 進捗を送信しながら完了を待つ
                last_progress = 5
                while not future.done():
                    try:
                        # 100ms待機して進捗をチェック
                        progress = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                        if progress > last_progress:
                            last_progress = progress
                            yield f"data: {json.dumps({'progress': progress, 'status': '文字起こし中...'})}\n\n"
                    except TimeoutError:
                        # タイムアウトしても継続
                        pass

                # 結果を取得
                result = future.result()

            if result.get("success"):
                # 結果をグローバル変数に保存
                last_transcription["text"] = result.get("text", "")
                last_transcription["processing_time"] = result.get("duration", 0)
                last_transcription["timestamp"] = datetime.now()

                # 完了
                yield f"data: {json.dumps({'progress': 100, 'status': '完了', 'result': result})}\n\n"
            else:
                # エラー
                yield f"data: {json.dumps({'error': result.get('error', '不明なエラー')})}\n\n"

            # バックグラウンドでファイル削除
            if temp_file:
                background_tasks.add_task(cleanup_file, temp_file)

        except Exception as e:
            logger.error(f"❌ ストリーム処理エラー: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

            # エラー時もファイル削除
            if temp_file:
                background_tasks.add_task(cleanup_file, temp_file)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.delete("/models/{model_name}")
async def delete_model_endpoint(model_name: str):
    """
    モデル削除

    Args:
        model_name: 削除するモデル名

    Returns:
        削除結果
    """
    from transcribe import delete_model

    result = delete_model(model_name)

    if result["success"]:
        return JSONResponse(content=result)
    return JSONResponse(content=result, status_code=400)


@app.post("/save-transcription")
async def save_transcription():
    """
    最後の文字起こし結果をtxt形式で保存

    Returns:
        テキストファイルのダウンロードレスポンス
    """
    if not last_transcription["text"]:
        return JSONResponse(
            content={"error": "保存する文字起こし結果がありません"}, status_code=400
        )

    # ファイル名生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcription_{timestamp}.txt"

    # テキスト内容生成
    text = last_transcription["text"]
    char_count = len(text.replace("\n", "").replace(" ", ""))
    processing_time = last_transcription["processing_time"]

    content = f"{text}\n\n"
    content += "=" * 50 + "\n"
    content += f"文字数: {char_count}文字\n"
    content += f"処理時間: {processing_time:.2f}秒\n"

    logger.info(f"📥 文字起こし結果保存: {filename} ({char_count}文字)")

    # レスポンス
    return Response(
        content=content.encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


if __name__ == "__main__":
    # 開発環境かどうかを判定
    IS_DEV = os.getenv("GAQ_DEV", "true").lower() == "true"

    logger.info("=== GaQ Transcription API 起動 ===")
    logger.info(f"URL: http://{HOST}:{PORT}")
    logger.info(f"利用可能モデル: {AVAILABLE_MODELS}")

    if IS_DEV:
        logger.info("🔄 開発モード: ファイル変更時に自動リロード")
        # リロードモードではアプリケーションを文字列で指定
        uvicorn.run("main:app", host=HOST, port=PORT, log_level="info", reload=True)
    else:
        # 本番モードでは通常通りアプリケーションオブジェクトを指定
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
