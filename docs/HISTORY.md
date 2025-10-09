# GaQ Offline Transcriber - 開発履歴

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

**最終更新**: 2025-10-09 21:40
**ブランチ**: dev
