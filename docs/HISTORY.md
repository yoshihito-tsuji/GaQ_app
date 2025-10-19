# GaQ Offline Transcriber - 開発履歴

## 2025-10-19: JavaScript完全停止問題の解決（緊急対応）

### 問題概要
- **発生日時**: 2025-10-16 15:30 ビルド以降
- **症状**: アプリは起動するが、すべてのJavaScriptが実行されず、UI完全無反応
  - ドラッグ&ドロップ不可
  - すべてのボタン無反応
  - モデル管理機能停止
  - コンソールログ出力なし
- **影響**: アプリケーション全機能停止
- **ステータス**: ✅ 解決完了

### 根本原因

**Python triple-quoted stringでの`\n`エスケープ問題**

[release/mac/src/main.py:1462, 1466](../../release/mac/src/main.py#L1462)において、JavaScript内のalert文字列で改行を表現する際に、Pythonの`\n`がそのまま**literal newline**として出力されていた：

```python
# ❌ 問題のコード（Pythonトリプルクォート内）
alert('モデル「' + modelName + '」を削除しますか？\n\n削除後は再度ダウンロードが必要です。');
# → 生成されたJavaScriptに実際の改行が含まれ、SyntaxErrorが発生
```

JavaScriptのシングルクォート文字列内では**literal newlineは許可されない**ため、`SyntaxError: Unexpected EOF`が発生し、スクリプト全体の実行が停止していた。

### 解決方法

**バックスラッシュのエスケープ**

```python
# ✅ 修正後のコード
alert('モデル「' + modelName + '」を削除しますか？\\n\\n削除後は再度ダウンロードが必要です。');
# → Pythonで \\n と書くことで、生成されたJavaScriptには \n が出力される
```

### 問題発見の経緯

#### Phase 1: 誤った仮説（スコープ問題）
- 初期仮説: `showConfirmDialog` が未定義
- 対応: 関数をグローバルスコープに移動、`window.*`バインディング
- 結果: **改善なし**

#### Phase 2: pywebview環境問題の疑い
- 仮説: pywebviewのJavaScript実行環境の問題
- 対応: デバッグメッセージ追加、テストインフラ構築
- 結果: **改善なし**

#### Phase 3: Safari検証による突破口（Codex助言）
- **Codexの指示**: 「まずSafariブラウザで検証すること」
- 実施: `/tmp/gaq_debug.html` をSafariで開く
- 発見: **JavaScriptコンソールに `SyntaxError: Unexpected EOF at line 1397`**
- 結果: **根本原因特定** 🎯

### 実装した修正と改善

#### 1. 緊急修正
- **main.py L1462, L1466**: `\n` → `\\n` に修正

#### 2. 恒久的な改善
- **グローバルエラーハンドラー追加** ([main.py:661-679](../../release/mac/src/main.py#L661)):
  ```javascript
  window.addEventListener('error', function(event) { ... });
  window.addEventListener('unhandledrejection', function(event) { ... });
  ```
- **テストインフラ整備**:
  - `/test` エンドポイント追加（極小JavaScript検証ページ）
  - `test_javascript.sh` スクリプト作成
  - `GAQ_TEST_MODE=1` 環境変数によるテストモード起動

#### 3. ドキュメント整備
- **README.md トラブルシューティングセクション追加** ([README.md:531-677](../../README.md#L531)):
  - 🚨 アプリが起動しない場合
  - 🖱️ 画面が動作しない場合（UI無反応）
  - 📝 その他の問題
- **Codex情報共有ドキュメント作成**: [codex_report_20251019.md](../../codex_report_20251019.md)
- **開発ログ更新**: [20251019_smoke_test_and_sync_check.md](development/20251019_smoke_test_and_sync_check.md)

### 教訓

#### ✅ 効果的だった手法
1. **Safari検証の最優先実施**
   - pywebviewの問題切り分けにはブラウザ検証が最速
   - JavaScriptコンソールでのエラー確認が決定打

2. **生成されたHTMLの直接確認**
   - Pythonソースと生成結果の比較
   - `/tmp/gaq_debug.html` の保存による検証可能性

3. **段階的なデバッグインフラ構築**
   - テストモード、極小ページ、詳細ログ

#### ❌ 時間を浪費した手法
1. pywebview固有の問題と思い込んだ（約4時間）
2. 複雑な仮説から検証開始（単純な構文エラーの可能性を軽視）
3. ログ出力だけに依存（ブラウザツールを後回し）

#### 📌 今後のベストプラクティス
- **JavaScript問題発生時の確認順序**:
  1. Safari + JavaScript Console（最優先）
  2. 生成HTMLの構文チェック
  3. pywebview特有の問題調査
  4. 複雑なデバッグ実装

### 成果物

**v1.1.1 最終ビルド** (2025-10-19 20:14):
- ファイル名: `GaQ_Transcriber_v1.1.1_mac.dmg`
- サイズ: 78MB
- 内容:
  - JavaScript構文エラー修正済み
  - デバッグメッセージ削除（プロダクションクリーン）
  - グローバルエラーハンドラー実装
  - テストインフラ保持
- 動作確認: ✅ すべての機能正常動作

### 関連ファイル

**修正**:
- [release/mac/src/main.py](../../release/mac/src/main.py) - JavaScript文字列エスケープ修正

**ドキュメント**:
- [README.md](../../README.md) - トラブルシューティング追加
- [codex_report_20251019.md](../../codex_report_20251019.md) - 問題分析レポート
- [docs/development/20251019_smoke_test_and_sync_check.md](development/20251019_smoke_test_and_sync_check.md) - 詳細調査ログ

**テストツール**:
- [release/mac/test_javascript.sh](../../release/mac/test_javascript.sh) - JavaScript実行検証スクリプト

---

## 2025-10-16: Mac版 v1.1.1 リリース（パッチリリース）

### リリース概要
- **バージョン**: Mac版 v1.1.1 / Windows版 v1.1.0（変更なし）
- **リリース種別**: パッチリリース（バグフィックス）
- **作業時間**: 2025-10-16
- **ステータス**: ✅ 完了

### v1.1.1での変更内容

#### 1. Mac版起動エラーの修正
**問題**:
- Mac版アプリが起動しない（Dockでアイコンがバウンドするのみ）
- Python 3.13.5環境でのFastAPI type annotation互換性問題

**修正内容**:
- [release/mac/src/main.py](../release/mac/src/main.py): 型ヒント構文を修正
  - `Annotated[UploadFile, File()]` → `UploadFile = File(...)`
  - `/transcribe`エンドポイント (lines 969-970)
  - `/transcribe-stream`エンドポイント (lines 1024-1025)

#### 2. Python 3.12固定ビルド対応
**背景**:
- Python 3.13でのFastAPI互換性問題を恒久的に回避

**実施内容**:
- Python 3.12.12をHomebrew経由でインストール
- `.python-version`ファイル作成（Mac/Windows）
- 自動ビルドスクリプト作成:
  - [release/mac/build.sh](../release/mac/build.sh) - Python 3.12チェック + DMG自動生成
  - [release/windows/build.bat](../release/windows/build.bat) - Python 3.12チェック

#### 3. ビルドスクリプトの改行コード修正
**問題**:
- build.shがCRLF改行で`/bin/bash^M`エラー

**修正**:
- sedコマンドでCRLF → LF変換
- .gitattributes作成による改行コード管理
  - `*.sh` → LF固定
  - `*.bat` → CRLF固定
  - `.python-version` → LF固定

#### 4. DMGセットアップ簡略化
**追加機能**:
- DMG内配置ファイル:
  - `インストール方法.txt` - 詳細なインストール手順
  - `GaQ セットアップ.command` - 自動セットアップスクリプト
- build.shにDMG自動生成機能を追加
- Applicationsフォルダへのシンボリックリンク作成

### 配布パッケージ

**Mac版 v1.1.1**:
- ファイル名: `GaQ_Transcriber_v1.1.1_mac.dmg`
- サイズ: 約187MB
- 内容:
  - GaQ Offline Transcriber.app (Python 3.12.12同梱)
  - インストール方法.txt
  - GaQ セットアップ.command

**Windows版 v1.1.0**:
- 変更なし（既存パッケージをそのまま使用）

### 技術詳細

**ビルド環境**:
- Python: 3.12.12
- PyInstaller: 6.16.0
- faster-whisper: 1.2.0
- FastAPI: 0.104.1
- macOS: Darwin 24.6.0

**ファイルサイズ比較**:
- Python 3.13.5ビルド: 186MB
- Python 3.12.12ビルド: 187MB
- DMG (圧縮後): 約187MB

### ドキュメント

詳細な作業ログ:
- [development/20251016_mac_launch_error.md](development/20251016_mac_launch_error.md)
- [development/20251016_python_version_lock_SUMMARY.md](development/20251016_python_version_lock_SUMMARY.md)
- [development/20251016_build_script_fix.md](development/20251016_build_script_fix.md)
- [development/20251016_windows_build_script_check.md](development/20251016_windows_build_script_check.md)
- [development/20251016_mac_v1.1.1_release.md](development/20251016_mac_v1.1.1_release.md)

### 主な変更ファイル

**修正**:
- release/mac/src/main.py
- release/mac/build.sh
- release/mac/GaQ_Transcriber.spec

**新規**:
- release/mac/.python-version
- release/windows/.python-version
- release/windows/build.bat
- release/mac/dmg_assets/インストール方法.txt
- release/mac/dmg_assets/GaQ セットアップ.command
- .gitattributes

**更新**:
- README.md
- docs/guides/BUILD_GUIDE.md
- docs/HISTORY.md (このファイル)

---

## 2025-10-03: 配布方針の確定と過去の問題

### 配布バージョンの決定

**✅ 採用：完全パッケージ版（build_standard）**
- Python環境込み（350MB）
- ユーザーは追加ソフトウェアのインストール不要
- ドラッグ&ドロップですぐに使用可能

**❌ 不採用：軽量インストーラー版（launcher_final）**
- Python環境なし（188KB）
- ユーザーがPython 3をインストール必要
- Homebrewの使用が必要
- 一般ユーザーには困難

### 発生した問題

**背景:**
1. プロジェクト内に2つの異なる配布方式が共存
   - `build_standard/`：完全パッケージ版（356MB）
   - `launcher_final/`：軽量インストーラー版（188KB）

2. 誤って軽量版をDMGに含めようとした
   - DMGサイズ：1.4MB（異常に小さい）
   - Python環境が含まれていなかった
   - ユーザーがインストール不可能な状態

3. リリース直前に発覚
   - 他Mac環境での検証時に問題が明らかになった
   - 配布していたら誰も使えないアプリになっていた

**原因:**
- 開発過程でファイルサイズ削減を試みて軽量版を作成
- 両方のバージョンが残ったまま、誤って軽量版を選択
- 開発機ではPython環境があるため問題に気づかなかった

**教訓:**
- ✅ 配布前に別環境で必ず実機テスト
- ✅ DMGサイズを確認（150MB未満は異常）
- ✅ Python環境の存在を確認
- ✅ 「誰でも使える」ことを最優先

### 配布前チェックリスト（策定）

DMG作成後、必ず以下を確認：

- [ ] DMGサイズが150MB〜200MBである
- [ ] アプリサイズが350MB前後である
- [ ] Python環境が含まれている（python/ディレクトリ）
- [ ] Python 3.12.7が実行できる
- [ ] FastAPI, Uvicorn, faster-whisperがインストール済み
- [ ] 開発機で再インストールして動作確認
- [ ] 別のMac（検証機）でインストールして動作確認
- [ ] Applicationsショートカットが機能する
- [ ] インストール手順書が表示される

---

## 2025-10-02 ~ 2025-10-03: v1.1.0機能実装と修正

### 実装済み機能

詳細は[releases/COMPLETION_REPORT.md](releases/COMPLETION_REPORT.md)を参照

**主要実装:**
- Webview統合（FastAPI + pywebview）
- クロスプラットフォーム対応（Mac/Windows）
- PyInstaller設定
- リアルタイムプログレスバー
- 改行処理改善
- Chrome独立プロファイル起動

### 修正作業

#### 修正1: 改行処理とChrome起動の改善
- **作業時間**: 2025-10-03 09:29 - 09:51（22分）
- 文字起こし結果の改行処理改善（句読点・80文字折り返し）
- Chrome独立プロファイル使用（`~/.gaq/chrome_profile`）
- 成果物: `GaQ_Transcriber_v1.1.0_Final.dmg` (163MB)

#### 修正2: プログレスバー進行問題の修正
- **作業時間**: 2025-10-03 10:01 - 10:15（14分）
- **問題**: プログレスバーが5%で停止
- **原因**: progress_callbackがtranscribe()メソッドに渡されていなかった
- 詳細は[releases/PROGRESS_BAR_FIX_REPORT.md](releases/PROGRESS_BAR_FIX_REPORT.md)を参照
- 成果物: `GaQ_Transcriber_v1.1.0_Final.dmg` (164MB)

---

## 2025-10-05: Windows版コードレビュー

### 作業概要
- **作業時間**: 21:40 - 22:10（約30分）
- **内容**: Windows版リリース構成の妥当性評価とコード品質チェック

### 発見された問題

**🔴 重大な問題（3件）**
1. PyInstaller実行時のパス解決問題（config.py）
2. 静的ファイル配信のパス問題（main.py）
3. スレッド例外の伝播不足（main_app.py）

**🟠 中程度の問題（3件）**
1. モデルダウンロード時の初回起動UX
2. 依存ライブラリの明示不足
3. 一時ファイル削除タイミング

**🟡 軽微な問題（4件）**
- ログレベルの不一致
- 未使用パッケージ（aiofiles）
- 開放的なCORS設定
- UI層のみのモデル削除防止

詳細は[releases/COMPLETION_REPORT.md](releases/COMPLETION_REPORT.md)の該当セクションを参照

---

## 2025-10-06: Windows版 v1.1.0リリース

### 作業概要
- **作業時間**: 約4時間
- **ステータス**: ✅ リリース準備完了

### 完了した作業

#### 1. コードレビュー指摘事項の修正（6件）
1. **config.py** - PyInstaller対応（sys.frozen判定）
2. **main.py** - 静的ファイルパス修正（sys._MEIPASS対応）
3. **requirements.txt** - 依存関係明記（ctranslate2, av追加）
4. **main_app.py** - 本番モード設定（debug=False）
5. **transcribe.py** - WinError 1314対策強化
6. **GaQ_Transcriber.spec** - faster_whisper assets収集

#### 2. PyInstallerビルド成功
- Python 3.13.0
- PyInstaller 6.16.0
- 成果物: `dist/GaQ_Transcriber/GaQ_Transcriber.exe` (11MB)

#### 3. 動作確認テスト完全成功（全6項目通過）
- ✅ ウィンドウタイトル表示
- ✅ uploadsディレクトリ自動生成
- ✅ Mediumモデル文字起こし成功
- ✅ Large-v3モデル操作成功
- ✅ WinError 1314 fallback動作確認
- ✅ UIアイコン正常表示

#### 4. 配布パッケージ作成完了
- **ポータブルZIP版**: GaQ_Transcriber_Windows_v1.1.0_Portable.zip（138MB）
- **インストーラ版**: GaQ_Transcriber_Windows_v1.1.0_Setup.exe（95MB）

詳細は[releases/COMPLETION_REPORT.md](releases/COMPLETION_REPORT.md)の該当セクションを参照

---

## 2025-10-09: ドキュメント構造の再編

### 作業内容
- docs/ディレクトリ構造の整備
- 既存ドキュメントの整理と移動
- 開発記録用テンプレートの作成
- READMEの簡潔化
- **READMEに開発ワークフローセクションを追加**

### 新しいdocs構造
```
docs/
├── PROJECT_OVERVIEW.md          # プロジェクト概要
├── HISTORY.md                   # 開発履歴（このファイル）
├── README.md                    # docsガイド
├── development/                 # 日々の開発記録
│   ├── README.md                # 開発記録の書き方
│   ├── DAILY_LOG_TEMPLATE.md   # 日次ログテンプレート
│   ├── ERROR_LOG_TEMPLATE.md   # エラーログテンプレート
│   └── 20251009_docs_restructure.md  # 今回の作業ログ
├── releases/                    # リリース履歴・レポート
│   ├── COMPLETION_REPORT.md
│   └── PROGRESS_BAR_FIX_REPORT.md
├── guides/                      # ガイド・手順書
│   └── BUILD_GUIDE.md
├── distribution/                # 配布関連資料
│   ├── distribution_description.txt
│   └── install_readme_template.txt
└── troubleshooting/             # トラブルシューティング
```

### 方針
- すべての開発記録、エラーログをdocs/に集約
- devブランチで開発・検証・エラー対策を実施
- READMEは基本情報のみ、詳細はdocs/を参照
- **開発開始時はREADMEを読むだけで開発ログの確認・作成方法がわかる**

### 主な改善点
1. **開発ワークフローの明文化**: README.mdに作業開始・開発中・終了時の手順を追加
2. **テンプレート提供**: 日次ログとエラーログのテンプレートを作成
3. **ファイル命名規則の策定**: 統一的なファイル命名ルールを確立
4. **ドキュメント一元管理**: すべての開発関連ドキュメントをdocs/に集約

詳細は[development/20251009_docs_restructure.md](development/20251009_docs_restructure.md)を参照

---

## 2025-10-16: Mac版起動エラー修正とPython 3.12固定ビルド対応

### 作業概要
- **作業時間**: 2025-10-16 20:01 - 20:11（約10分）
- **担当**: Claude Code
- **ステータス**: ✅ 完了

### 発生した問題

#### 問題1: Mac版アプリが起動しない
- **症状**: アプリアイコンがDockでバウンドするが起動しない
- **原因**: Python 3.13.5 + FastAPI 0.104.1 + Pydantic 2.12.2環境で`Annotated[UploadFile, File()]`型ヒント構文の互換性問題
- **エラー**: `AssertionError: Param: file can only be a request body, using Body()`

#### 問題2: Python 3.13との互換性問題
- FastAPI/Pydanticの型アノテーション処理が変更され、従来構文が必要
- Python 3.12.xでは問題なし

### 実施した修正

#### 1. FastAPI type annotation修正
[release/mac/src/main.py](../release/mac/src/main.py):
- Line 12: `Annotated`インポート削除
- Lines 969-970: `/transcribe`エンドポイント修正
  ```python
  # 修正前: file: Annotated[UploadFile, File()]
  # 修正後: file: UploadFile = File(...)
  ```
- Lines 1024-1025: `/transcribe-stream`エンドポイント修正

#### 2. Python 3.12固定ビルド対応

**Python 3.12.12のインストール**:
```bash
brew install python@3.12
# インストール確認: Python 3.12.12
```

**作成したファイル**:
- [release/mac/.python-version](../release/mac/.python-version) - Python 3.12.12指定
- [release/mac/build.sh](../release/mac/build.sh) - Python 3.12チェック機能付きビルドスクリプト
- [release/windows/.python-version](../release/windows/.python-version) - Python 3.12.12指定
- [release/windows/build.bat](../release/windows/build.bat) - Python 3.12チェック機能付きビルドスクリプト

**ドキュメント更新**:
- [docs/guides/BUILD_GUIDE.md](guides/BUILD_GUIDE.md) - Python 3.12要件を明記

#### 3. ビルド検証

**Python 3.12.12でビルド**:
```bash
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate
python --version  # Python 3.12.12
pyinstaller --clean -y GaQ_Transcriber.spec
```

**成果物**:
- `dist/GaQ Offline Transcriber.app` (187MB)
- ✅ 起動確認成功

### 技術詳細

**Python 3.12を選択した理由**:
1. Python 3.13ではFastAPIの型アノテーション互換性問題が発生
2. Python 3.12.7以降の3.12.xが安定版として推奨
3. HomebrewではPython 3.12.12が提供される

**ビルドスクリプトの機能**:
- Python 3.12のバージョンチェック
- 仮想環境の自動作成/再作成
- 依存パッケージの自動インストール
- PyInstallerでのビルド自動化

**サイズ比較**:
- Python 3.13.5ビルド: 186MB
- Python 3.12.12ビルド: 187MB
- **差異**: +1MB（ほぼ同等）

### ドキュメント

詳細な作業ログ:
- [development/20251016_mac_launch_error.md](development/20251016_mac_launch_error.md) - Mac起動エラー修正の詳細
- [development/20251016_python_version_lock_SUMMARY.md](development/20251016_python_version_lock_SUMMARY.md) - Python 3.12固定対応の完了報告

### 次のステップ
- [ ] Windows環境でPython 3.12.12のビルドテスト
- [ ] build.shの改行コード修正（LF固定）
- [ ] mainブランチへのマージ（検証完了後）

---

**最終更新**: 2025-10-16 20:11
**ブランチ**: dev
