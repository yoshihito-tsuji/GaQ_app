# 開発ログ - 2025-12-13

## 作業概要
- **日付**: 2025-12-13
- **担当者**: Claude Code（実装）、Codex（設計指示）、Yoshihitoさん（検証・承認）
- **ブランチ**: main

## 作業内容

### 実施した作業

Codexからの指示に基づき、Windows版の堅牢性向上のための8項目を実装しました。

#### 1. ログとフェイルファスト強化（診断基盤）

**変更ファイル**:
- `release/windows/src/main_app.py`
- `release/windows/src/transcribe.py`

**実装内容**:
- `faulthandler`モジュールによるクラッシュログ出力を有効化
- クラッシュ時のスタックトレースを`~/.gaq/logs/crash.log`に保存
- 起動時のシステム情報ログ出力（OS、メモリ、Python版など）
- モデルロード時のエラー種別診断ログを追加

#### 2. CPU命令未対応チェック（AVX系）

**変更ファイル**:
- `release/windows/src/main_app.py`

**実装内容**:
- `check_cpu_features()`関数を追加
- PowerShellでCPU情報を取得してログ出力
- ctranslate2の対応compute_typesを確認
- 古いCPU（Core2、Pentium、Phenom等）を検出時に警告

#### 3. VC++再頒布/UCRT/SSL欠品の明示同梱・起動チェック

**変更ファイル**:
- `release/windows/GaQ_Transcriber.spec`
- `release/windows/src/main_app.py`

**実装内容**:
- PyInstaller specファイルにDLL明示収集を追加
  - vcruntime140*.dll, msvcp140*.dll, ucrtbase.dll
  - libcrypto*.dll, libssl*.dll
  - ctranslate2, av (PyAV) のDLLを明示収集
- `check_runtime_dependencies()`関数を追加
- 起動時にDLL存在チェック、不足時はダイアログで通知

#### 4. pywebview/WebView2起動失敗対策（GPUオプション含む）

**変更ファイル**:
- `release/windows/src/main_app.py`

**実装内容**:
- `check_webview2_runtime()`関数を追加
- レジストリでWebView2の存在を確認
- 不在時はダウンロードページへの誘導ダイアログを表示
- `--disable-gpu`コマンドライン引数と`GAQ_DISABLE_GPU`環境変数に対応

#### 5. モデル破損検知とリカバリ（ハッシュ検証）

**変更ファイル**:
- `release/windows/src/transcribe.py`

**実装内容**:
- `verify_model_integrity()`関数を追加
- 必須ファイルの存在確認（model.bin, config.json等）
- ファイルサイズ0の破損チェック
- config.jsonの読み取りテスト
- `repair_corrupted_model()`関数で破損モデルを自動削除・再ダウンロード

#### 6. 書き込み権限/OneDriveフォールバック

**変更ファイル**:
- `release/windows/src/config.py`
- `release/windows/src/main_app.py`

**実装内容**:
- `get_app_data_dir()`関数を追加（LOCALAPPDATA配下を優先）
- `verify_write_permission()`関数で書き込み権限を確認
- `get_upload_dir()`関数でフォールバックパスを自動選択
  1. EXE隣接ディレクトリ
  2. LOCALAPPDATA配下
  3. TEMP配下（最終フォールバック）

#### 7. ffmpeg/コーデック対策

**変更ファイル**:
- `release/windows/src/transcribe.py`

**実装内容**:
- `setup_ffmpeg_path()`関数を追加
- PyInstallerバンドル時、PyAVのffmpegをPATHの先頭に追加
- 音声フォーマットエラーの詳細診断とユーザーフレンドリーなメッセージ

#### 8. SmartScreen/AVドキュメント

**変更ファイル**:
- `docs/handbook/troubleshooting.md`

**実装内容**:
- SmartScreen警告の回避手順を追加
- アンチウイルス誤検知の対処方法を追加
- SHA256によるファイル整合性確認手順を追加
- GPU無効化モードの起動方法を追加

## 変更したファイル一覧

| ファイル | 変更内容 |
|---------|---------|
| `release/windows/GaQ_Transcriber.spec` | DLL明示収集、ctranslate2/av動的ライブラリ収集追加 |
| `release/windows/src/main_app.py` | faulthandler、システム情報ログ、DLL/WebView2チェック、GPUオプション追加 |
| `release/windows/src/transcribe.py` | ffmpegパス設定、モデル整合性チェック、エラー診断強化 |
| `release/windows/src/config.py` | LOCALAPPDATA対応、書き込み権限チェック、フォールバック実装 |
| `docs/handbook/troubleshooting.md` | SmartScreen/AV対策、GPU問題対処、ログ確認手順を追加 |

## テスト項目

### 確認ポイント

- [ ] Windows 11 クリーン環境での起動テスト
- [ ] DLL依存チェックが正しく動作するか
- [ ] WebView2未インストール環境での誘導ダイアログ
- [ ] GPU無効化モード（`--disable-gpu`）での起動
- [ ] モデル破損時の自動修復
- [ ] OneDriveリダイレクト環境でのフォールバック動作
- [ ] 特殊音声フォーマット（マルチチャンネル等）のエラーメッセージ

### ログ確認手順

```powershell
# アプリログ
Get-Content "$env:LOCALAPPDATA\GaQ\logs\app.log" -Tail 50

# クラッシュログ
Get-Content "$env:LOCALAPPDATA\GaQ\logs\crash.log" -Tail 50
```

## 次のステップ

- [ ] Windows実機でのビルド・テスト
- [ ] GitHub Actionsでのビルド確認
- [ ] v1.2.3リリース準備

---

**作成日時**: 2025-12-13
**報告者**: Claude Code
