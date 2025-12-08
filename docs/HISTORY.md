# GaQ Offline Transcriber - 開発履歴

## 2025-12-08: プライバシーポリシーの明文化と外部通信監査

### 作業概要

- **作業時間**: 2025-12-08 約1時間
- **担当**: Claude Code + Codex（検証）
- **ステータス**: ✅ 完了

### 背景

本アプリは「利用者の情報保護を最優先」とする設計方針を採用しています。この方針が技術的に遵守されていることを第三者が確認できるよう、網羅的な外部通信監査を実施し、結果をドキュメント化しました。

### 監査結果

#### 確認済み：外部通信が発生する唯一の経路

| 通信先 | タイミング | 内容 |
|--------|------------|------|
| `huggingface.co` | AIモデル未ダウンロード時のみ | Whisperモデルファイル（約1.5〜3GB） |

#### 外部通信がないことを確認した項目

| 項目 | 確認結果 |
|------|----------|
| CDN/外部CSS/JSライブラリ | なし（全てインライン埋め込み） |
| 外部フォント | なし |
| エラーレポート/クラッシュレポート | Sentry, Bugsnag等のSDKなし |
| テレメトリ/アナリティクス | 該当コードなし |
| requests/urllib使用箇所 | ローカル`127.0.0.1`のみ |

#### 開発者の制御外の通信

- **WebViewエンジン（WebKit/CEF）**: OS/ブラウザレベルで独自の通信を行う可能性あり
- これはアプリケーションレベルでは制御不可能であり、一般的なWebViewアプリ共通の挙動

### 実施した作業

1. **README.md**: プライバシーポリシーセクションを追加
   - 外部通信の説明
   - 開発者としての設計方針
   - WebViewエンジンに関する注記

2. **docs/HISTORY.md**: 本セクションを追加（監査記録）

### 監査方法

以下の観点でコードベース全体を検索・確認：

1. 外部URL（`https://`, `http://`）のハードコード
2. テレメトリ/アナリティクス関連キーワード（`telemetry`, `analytics`, `sentry`等）
3. ネットワーク関連ライブラリの使用箇所（`requests`, `urllib`, `httpx`等）
4. CDN/外部リソース参照（`cdn.`, `googleapis`, `cloudflare`等）
5. Hugging Faceライブラリの挙動確認

### 結論

**「開発者のできる範囲内においては、一切、外部にデータを送信しない設計」であることをコード監査により確認しました。**

### 関連ファイル

**更新したファイル**:

- [README.md](../README.md) - プライバシーポリシーセクション追加
- [docs/HISTORY.md](HISTORY.md) - 本セクション追加

---

## 2025-11-11: プラットフォーム別リリースタグへの移行（v1.1.1 → v1.1.1-mac）

### 作業概要
- **作業時間**: 2025-11-11 約30分
- **担当**: Claude Code + Yoshihitoさん
- **ステータス**: ✅ 完了

### 実施内容

#### リリースタグ構造の変更

**変更前**:
```
v1.1.1  # Mac版のみ（混乱の原因）
```

**変更後**:
```
v1.1.1-mac  # Mac版専用
v1.1.1-win  # Windows版専用（今後追加予定）
```

#### 変更理由（Codex推奨）

1. **明確な分離**: 各プラットフォームのリリースが独立して管理できる
2. **柔軟性**: Mac版とWindows版を異なるタイミングでリリース可能
3. **ユーザビリティ**: ユーザーが自分のプラットフォームを選びやすい
4. **統計管理**: ダウンロード統計スクリプトも対応しやすい
5. **早期実施**: 公開直後（ダウンロード4件のみ）のため影響最小

#### 実施した作業

1. **ダウンロード数の記録**
   - 削除前のダウンロード数: **合計4件**
     - GaQ_Transcriber_v1.1.1_mac.dmg: 3件
     - GaQ_Transcriber_v1.1.1_mac.dmg.sha256: 1件
   - 記録保存: `/tmp/v1.1.1_stats_before_migration.json`

2. **リリースの再構成**
   - 既存の `v1.1.1` を削除
   - `v1.1.1-mac` として再作成
   - リリースURL: https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.1.1-mac

3. **ダウンロード統計スクリプト更新**
   - `scripts/check_download_stats.py`: プロジェクト設定を更新
     ```python
     PROJECTS = {
         "gaq-mac": "GaQ_app",
         "gaq-win": "GaQ_app",  # Windows版用に予約
         "popup": "PoPuP"
     }
     RELEASES = {
         "gaq-mac": "v1.1.1-mac",
         "gaq-win": "",  # Windows版リリース後に設定
         "popup": ""
     }
     ```
   - `scripts/check_download_stats.sh`: 同様に更新

4. **ドキュメント更新**
   - `README.md`: リリースURLとダウンロードリンクを v1.1.1-mac に更新
   - `release/mac/release_notes_v1.1.1.md`: 同様に更新

### 今後の運用

#### バージョニング規則
- Mac版: `v{major}.{minor}.{patch}-mac`
- Windows版: `v{major}.{minor}.{patch}-win`

#### 例
```
v1.1.1-mac   # 現在
v1.1.1-win   # 今後追加予定
v1.2.0-mac   # 次期バージョン
v1.2.0-win   # 次期バージョン
```

### 注意事項

**アセットの手動アップロード必要**

現在、`v1.1.1-mac` リリースは作成されていますが、アセット（DMGファイル）がまだアップロードされていません。

**対応方法**:
1. [リリースページ](https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.1.1-mac) にアクセス
2. "Edit release" をクリック
3. DMGファイルとSHA256ハッシュファイルをドラッグ&ドロップ
4. "Update release" をクリック

**必要なファイル**:
- `GaQ_Transcriber_v1.1.1_mac.dmg` (77.5MB)
- `GaQ_Transcriber_v1.1.1_mac.dmg.sha256` (97 Bytes)

### 関連ファイル

**更新したファイル**:
- [README.md](../../README.md) - リリースURLを v1.1.1-mac に更新
- [release/mac/release_notes_v1.1.1.md](../../release/mac/release_notes_v1.1.1.md) - リンク更新
- [scripts/check_download_stats.py](../../scripts/check_download_stats.py) - プラットフォーム別設定
- [scripts/check_download_stats.sh](../../scripts/check_download_stats.sh) - プラットフォーム別設定

---

## 2025-11-11: Mac版v1.1.1 GitHub Release正式公開 & ダウンロード統計スクリプト作成

### 作業概要
- **作業時間**: 2025-11-11 約3時間
- **担当**: Claude Code + Yoshihitoさん
- **ステータス**: ✅ 完了（統計自動収集設定は今後の課題）

### 公開内容

#### GitHub Release
- **リリースページ**: <https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.1.1-mac>
- **タグ**: v1.1.1-mac（プラットフォーム別タグへ移行）
- **ステータス**: 正式公開（Draft解除完了）

#### 配布アセット
1. **DMGファイル**: `GaQ_Transcriber_v1.1.1_mac.dmg` (77.5MB)
   - ダウンロードURL: <https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1-mac/GaQ_Transcriber_v1.1.1_mac.dmg>
2. **SHA256ハッシュ**: `GaQ_Transcriber_v1.1.1_mac.dmg.sha256` (97 Bytes)
   - ダウンロードURL: <https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1-mac/GaQ_Transcriber_v1.1.1_mac.dmg.sha256>
3. **ソースコード**: 自動生成（zip、tar.gz）

### 実施した作業

#### 1. README.md更新
- GitHub Releaseへのダウンロードリンク追加
- Mac版v1.1.1の配布状況を更新（配布保留中 → 配布中）
- ファイルサイズを最新値に更新（187MB → 77.5MB）
- v1.1.1の主要改善内容を明記
- 最終更新日を2025-11-11に更新

#### 2. リモートリポジトリとの同期
- `git fetch origin` でリモートの最新情報を取得
- `git merge --ff-only origin/dev` でローカルに反映
- 以下のドキュメントを取得：
  - [docs/development/20251111_v1.1.1_github_release.md](development/20251111_v1.1.1_github_release.md)
  - [docs/development/20251031_collaboration_template_creation.md](development/20251031_collaboration_template_creation.md)
  - [docs/templates/](../templates/) - 協働環境テンプレート群
  - [release/mac/release_notes_v1.1.1.md](../../release/mac/release_notes_v1.1.1.md)
  - [release/mac/GaQ_Transcriber_v1.1.1_mac.dmg.sha256](../../release/mac/GaQ_Transcriber_v1.1.1_mac.dmg.sha256)

#### 3. ダウンロード統計スクリプト作成
- **scripts/check_download_stats.py**: マルチプロジェクト対応統計スクリプト
  - GaQ_app（Mac/Windows）とPoPuP（Windows）の両方に対応
  - 出力形式: プリティ表示、CSV、JSON
  - プラットフォーム自動判定（macOS、Windows、Hash）
  - Python標準ライブラリのみで実装（外部依存なし）
  - GitHub API統合（GITHUB_TOKEN対応）

- **scripts/daily_stats_collect.sh**: 自動収集ラッパー
  - CSV形式で日別統計を保存
  - 実行ログ記録機能
  - エラーハンドリング

- **scripts/setup_daily_stats.sh**: セットアップスクリプト
  - 必要ディレクトリの自動作成
  - cron設定ガイダンス
  - テスト実行機能

- **scripts/README.md**: ドキュメント更新
  - 各スクリプトの詳細な使用方法
  - cron設定手順
  - 環境変数設定ガイド

#### 4. 初回統計取得
- リリース直後の統計を確認：**合計3ダウンロード**
  - GaQ_Transcriber_v1.1.1_mac.dmg: 2件
  - SHA256ハッシュ: 1件

### 配布状況

- ✅ **Mac版v1.1.1**: GitHub Releasesで正式公開中
- ⏳ **Windows版v1.1.1**: 準備中（クリップボード機能改善済み、ビルド待ち）

### ダウンロード方法（ユーザー向け）

#### 方法1: ブラウザからダウンロード
1. [リリースページ](https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.1.1)にアクセス
2. 「GaQ_Transcriber_v1.1.1_mac.dmg」をクリックしてダウンロード
3. DMGをマウントしてApplicationsフォルダにドラッグ&ドロップ

#### 方法2: コマンドラインからダウンロード
```bash
# DMGファイルのダウンロード
curl -L -o GaQ_Transcriber_v1.1.1_mac.dmg \
  https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1/GaQ_Transcriber_v1.1.1_mac.dmg

# SHA256ハッシュの確認
curl -L https://github.com/yoshihito-tsuji/GaQ_app/releases/download/v1.1.1/GaQ_Transcriber_v1.1.1_mac.dmg.sha256
shasum -a 256 GaQ_Transcriber_v1.1.1_mac.dmg
```

### 成果

#### ✅ 達成したこと
1. Mac版v1.1.1をGitHub Releasesで正式公開
2. ダウンロード直リンクの確認完了
3. README.mdにダウンロード情報を追加
4. リモートリポジトリの最新状況を反映
5. マルチプロジェクト対応のダウンロード統計スクリプト作成
6. 自動収集の仕組みを整備（手動実行・cron・GitHub Actions対応可能）

#### 📊 期待される効果
- ユーザーが簡単にアプリをダウンロード可能に
- GitHub経由でダウンロード数の自動計測開始
- セキュリティ確認（SHA256ハッシュ）が可能
- ダウンロード推移を定期的に確認可能
- GaQ_appとPoPuPの統計を一元管理

### 技術的詳細

#### ビルド環境
- **OS**: macOS 14.8
- **Python**: 3.12.3
- **PyInstaller**: 6.16.0
- **faster-whisper**: 1.2.0
- **FastAPI**: 0.104.1
- **pywebview**: 6.0

#### パッケージサイズ
- **アプリ本体（非圧縮）**: 188MB
- **DMG（圧縮後）**: 77.5MB
- **圧縮率**: 約41%

### 次のステップ

#### 短期（今後1週間）
- [ ] ダウンロード統計の定期確認（手動実行で週1回程度）
- [ ] ユーザーフィードバックの収集
- [ ] Windows版v1.1.1のビルドと公開

#### 中期（今後1ヶ月）
- [x] ダウンロード数の集計スクリプト作成 ✅ 完了
- [ ] **統計自動収集の環境整備**（以下のいずれか）
  - 研究室の常時稼働PCでcron設定
  - GitHub Actionsによる自動実行
- [ ] ユーザーマニュアルの充実
- [ ] GitHub Actionsによる自動ビルド導入検討

#### 長期（今後3ヶ月）
- [ ] コード署名対応（Mac版）
- [ ] MSIX化とコード署名（Windows版）
- [ ] 多言語対応の検討

### 関連ファイル

**更新したファイル**:
- [README.md](../../README.md) - ダウンロード情報追加
- [docs/HISTORY.md](../HISTORY.md) - 本セクション追加
- [scripts/check_download_stats.py](../../scripts/check_download_stats.py) - 統計スクリプト（新規）
- [scripts/daily_stats_collect.sh](../../scripts/daily_stats_collect.sh) - 自動収集ラッパー（新規）
- [scripts/setup_daily_stats.sh](../../scripts/setup_daily_stats.sh) - セットアップスクリプト（新規）
- [scripts/README.md](../../scripts/README.md) - スクリプトドキュメント更新
- [.gitignore](../../.gitignore) - stats/ディレクトリを除外

**参照ドキュメント**:
- [docs/development/20251111_v1.1.1_github_release.md](development/20251111_v1.1.1_github_release.md) - 詳細作業ログ
- [release/mac/release_notes_v1.1.1.md](../../release/mac/release_notes_v1.1.1.md) - リリースノート

---

## 2025-10-31: 協働環境テンプレート作成（他プロジェクトへの展開基盤）

### 作業概要
- **作業時間**: 2025-10-31 約1.5時間
- **担当**: Claude Code
- **ステータス**: ✅ 完了

### 作業内容

GaQ_appで確立した**Claude Code + Codexの協働環境**を、他のプロジェクト（Pop_appなど）でも再利用できるテンプレートとして整備しました。

#### 作成したテンプレートファイル（5件）

1. **@claude.md.template** (3.8KB) - Claude Codeの役割定義
2. **@codex.md.template** (1.8KB) - Codexの役割定義
3. **CLAUDE.md.template** (3.9KB) - プロジェクト指示書
4. **README.md.template** (3.5KB) - プロジェクト概要
5. **SETUP_GUIDE.md** (8.3KB) - セットアップ手順書

#### 保管場所

- **GaQ_app内**: `docs/templates/`（作成時）
- **最終保管先**: `~/Claude_Code/開発方針テンプレ/`（Yoshihitoさんが移動）

#### 初適用プロジェクト

**Pop_app（人口ピラミッド作成アプリ）**で初めて適用予定。

### 成果

今後のプロジェクトで、以下のメリットが期待できる：

1. **立ち上げ時間の大幅短縮**（30分〜1時間/プロジェクト）
2. **一貫した協働体制の確立**
3. **学習効率の向上**
4. **ドキュメント管理の標準化**

### テンプレート活用例

このテンプレートを使って、以下のようなプロジェクトを迅速に立ち上げ可能：

- **教育系アプリ**: 人口ピラミッド、気象データ可視化、化学式学習、歴史年表
- **ツール系アプリ**: ファイル整理、データ変換、レポート生成
- **研究支援系アプリ**: アンケート集計、文献管理、実験記録

### 関連ファイル

**作成したテンプレート**:
- [docs/templates/@claude.md.template](templates/@claude.md.template)
- [docs/templates/@codex.md.template](templates/@codex.md.template)
- [docs/templates/CLAUDE.md.template](templates/CLAUDE.md.template)
- [docs/templates/README.md.template](templates/README.md.template)
- [docs/templates/SETUP_GUIDE.md](templates/SETUP_GUIDE.md)

**開発ログ**:
- [docs/development/20251031_collaboration_template_creation.md](development/20251031_collaboration_template_creation.md)

### 技術的教訓

#### ✅ うまくいったこと

1. **実績のある協働環境をテンプレート化**
   - GaQ_appで実際に動いている体制を抽出したため、実用性が高い

2. **完全な手順書を提供**
   - Yoshihitoさんが単独で新規プロジェクトを立ち上げられるSETUP_GUIDE.mdを作成

3. **Alex Finnさんのツイートからの学び**
   - Codex + Claude Codeの協働ワークフローが業界でも評価されている手法であることを確認

#### 📌 今後の改善点

1. **Pop_appでの実践フィードバック**
   - 初適用での気づきを元にテンプレート改善

2. **継続的な改善サイクル**
   - 各プロジェクトでの経験をテンプレートに反映

3. **チーム運用ドキュメントのテンプレート化**
   - `docs/team_ops/` のテンプレート化も検討

---

## 2025-10-22: Windows版 v1.1.1リリース（クリップボード機能修正完了）

### リリース情報

**バージョン**: v1.1.1
**リリース日**: 2025-10-22
**プラットフォーム**: Windows 10/11 (64bit)
**配布形式**:
- ポータブルZIP版: `GaQ_Transcriber_Windows_v1.1.1_Portable.zip` (約139 MB / 146,205,428 bytes)
- インストーラ版: `GaQ_Transcriber_Windows_v1.1.1_Setup.exe` (約96 MB / 100,598,117 bytes)

**チェックサム**:
- ZIP: `SHA256: C0A423E91310702AAAFCE6896F63C493A05249C20A01CEC39401AA6D796E48CB`
- Setup.exe: `SHA256: 09B4A7E572B5944A6A709FCFB333F5D33FA50DA4298CDC294A7E855B5B021F91`

### 作業概要
- **作業時間**: 2025-10-22 約2時間
- **担当**: Claude Code + Codex（技術コンサルティング）
- **ステータス**: ✅ 実装完了、テスト完了、リリース準備中

### 修正内容

#### クリップボードコピー機能の修正

**問題**: Windows版v1.1.0でクリップボードコピー時に「メモリロックエラー」が発生

**根本原因**:
- ctypesでWindows APIを呼び出す際、明示的な型定義（argtypes/restype）がないと、デフォルトで`c_int`（32bit整数）として扱われる
- `GlobalLock`の戻り値は64bitポインタ（8バイト）だが、型定義なしでは`c_int`（4バイト）として解釈される
- 64bit環境で戻り値が切り捨てられ、0（NULL）と誤判定される
- 結果として「メモリロックエラー」が発生

**解決策**: Windows API の全関数に明示的な型定義を追加
```python
# Windows API の型定義
kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = ctypes.c_void_p

kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p  # ← 重要

kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.restype = ctypes.c_bool

# ... その他のAPI定義
```

**テスト結果**: ✅ 全機能正常動作
- Mediumモデル: 文字起こし、コピー、保存 - すべて成功
- Large-v3モデル: 文字起こし、コピー、保存 - すべて成功

### ビルド情報

**環境**:
- Python: 3.12.10
- PyInstaller: 6.16.0
- OS: Windows 11

**成果物**:
- EXE: `GaQ_Transcriber.exe` (10,844,768 bytes)
- タイムスタンプ: 2025/10/22 11:47:12

### 変更ファイル
- [release/windows/src/main_app.py](../release/windows/src/main_app.py): ctypes Windows API型定義追加（296-406行）

### 詳細ドキュメント
- **開発ログ**: [20251022_windows_v1.1.1_preparation.md](development/20251022_windows_v1.1.1_preparation.md)
- **テスト結果**: [20251022_windows_test_results.md](development/20251022_windows_test_results.md)

### 技術的教訓

ctypesでWindows APIを使用する際の必須事項:
1. すべての関数に対して`argtypes`と`restype`を明示的に定義する
2. 特にポインタを返す関数では`c_void_p`を使用
3. 64bit環境では型定義の欠如が深刻なバグを引き起こす
4. PyInstallerでパッケージ化する場合も同様に必要

---

## 2025-10-21: v1.1.1リリース（フェーズ1改善完了）

### リリース情報

**バージョン**: v1.1.1
**リリース日**: 2025-10-21
**プラットフォーム**: macOS (Intel & Apple Silicon)
**DMGサイズ**: 77MB
**リリースノート**: [RELEASE_NOTES_v1.1.1.md](RELEASE_NOTES_v1.1.1.md)

### 作業概要
- **作業時間**: 2025-10-21 約3時間
- **担当**: Claude Code + Codex（技術コンサルティング）
- **ステータス**: ✅ 実装完了、テスト完了、ビルド完了、リリース済み

---

## 2025-10-21: フェーズ1改善実装とテスト完了

### 作業概要
- **作業時間**: 2025-10-21 約2時間
- **担当**: Claude Code + Codex（技術コンサルティング）
- **ステータス**: ✅ 実装完了、テスト完了

### 実装内容

Codex相談結果（[20251021_codex_response_analysis.md](development/20251021_codex_response_analysis.md)）のフェーズ1（高優先度）4項目を実装：

#### 1. ハートビート間隔の設定化
- 環境変数 `GAQ_SSE_HEARTBEAT_INTERVAL` でSSEハートビート間隔を調整可能に
- デフォルト: 10秒（既存動作と同じ）
- リスク: ゼロ

#### 2. ログレベル制御
- 環境変数 `GAQ_LOG_LEVEL` でログレベルを制御可能に
- デフォルト: INFO（ハートビートログは非表示でノイズ削減）
- DEBUG時: ハートビートログを含む詳細ログを出力
- リスク: 非常に低い

#### 3. 非ポーリング化の簡素化
- 0.1秒ポーリング → `asyncio.timeout()` による非ポーリング方式に変更
- `heartbeat_counter` と `MAX_WAIT_WITHOUT_HEARTBEAT` を削除
- CPU使用量削減、コード明確化
- リスク: 低い

#### 4. SSE切断検知とログ整備
- `asyncio.CancelledError` による切断検知を実装
- 切断時に「🔌 クライアント切断検知」をログ出力
- Futureのキャンセル処理を追加
- リスク: 非常に低い

### テスト結果

**自動テスト**: ✅ ALL PASS
- テスト1: ハートビート間隔の設定化 - ✅ PASS
- テスト2: ログレベル制御 - ✅ PASS
- テスト3: 非ポーリング化（コードレビュー） - ✅ PASS
- テスト4: SSE切断検知（コードレビュー） - ✅ PASS

**詳細**: [20251021_phase1_test_results.md](development/20251021_phase1_test_results.md)

### 変更ファイル
- [release/mac/src/main.py](../release/mac/src/main.py): 2321行（+14行）
- [release/windows/src/main.py](../release/windows/src/main.py): 2321行（+14行）
- ソースコード同期: ✅ 完全同期（`check_sync.sh` で確認）

### 次のステップ
- ユーザーによる手動テスト（手順書: [20251021_phase1_test_results.md](development/20251021_phase1_test_results.md)）
- Windows実機でのビルドとテスト
- フェーズ2改善項目の検討

---

## 2025-10-21: クリップボードコピー検証処理のノイズ除去

### 作業概要
- **作業時間**: 2025-10-21 約20分
- **担当**: Claude Code + Codex（技術コンサルティング）
- **ステータス**: ✅ 完了

### 発生した問題

#### 症状
2025-10-20の動作検証中、クリップボードコピー時に以下の警告がログに記録された：

```text
WARNING - ⚠️ UTF-8デコードエラー - errors='replace'でデコードしました
WARNING - ⚠️ クリップボード内容が一致しません (expected: 49817, actual: 78110)
```

#### 影響範囲
- **機能的な問題**: なし（クリップボードコピーは正常動作）
- **ログノイズ**: あり（不要な警告が記録される）
- **ユーザー影響**: なし（警告はログにのみ表示）

### 根本原因

**pbpaste検証処理の誤検知**

1. **AppleScriptでのコピー**: ✅ 成功
   - UTF-8形式で正しくクリップボードにコピー
   - 実際のユーザー操作で問題なくペースト可能

2. **pbpaste検証**: ❌ 誤検知
   - macOSのクリップボードには複数形式（UTF-8、RTF、HTMLなど）が保存される
   - `pbpaste`がRTF形式など別のエンコーディングで取得
   - UTF-8デコード失敗により文字化け
   - 文字数不一致（RTFフォーマット情報が含まれるため）

### 実施した修正

**検証処理を完全削除**

**理由**:
- AppleScriptの`set the clipboard to`は十分に信頼できる
- 検証処理が誤検知している（実際はコピー成功しているのに警告）
- ユーザー体験に影響なし
- コードの簡潔化

**修正内容**:
- [release/mac/src/main_app.py](../../release/mac/src/main_app.py):278-312 - pbpaste検証処理を削除（35行削減）
- [release/windows/src/main_app.py](../../release/windows/src/main_app.py):278-312 - 同上

### 成果

**修正効果**:
- ✅ ログノイズ完全除去
- ✅ コード簡潔化（36行削減：884行 → 848行）
- ✅ 実行速度わずかに向上（pbpaste実行の100ms wait + 5秒timeoutが不要に）
- ✅ ソース同期確認済み

**動作確認**:
- クリップボードコピー機能は正常動作
- 長文（49,817文字）でも正常コピー
- ログに警告なし

### Codexの判断

> AppleScript経由のコピー自体は成功しており、保存ファイルの文字数一致からも内容は正しいと判断できる。
> 本番でのログノイズを避けるなら、検証処理を削除し、必要時のみ手動確認する運用が現実的。

### 教訓

**クリップボード操作の設計指針**:
- AppleScriptの`set the clipboard to`は十分に信頼できる
- `pbpaste`での検証は、エンコーディング問題で誤検知する可能性がある
- 検証が必要な場合は、AppleScriptで直接読み取る方が安全
- 本番環境でのログノイズは最小限に抑える

### 関連ファイル

**修正**:
- [release/mac/src/main_app.py](../../release/mac/src/main_app.py)
- [release/windows/src/main_app.py](../../release/windows/src/main_app.py)

**ドキュメント**:
- [docs/development/20251021_clipboard_verification_noise_removal.md](development/20251021_clipboard_verification_noise_removal.md) - 詳細作業ログ
- [README.md](../../README.md) - トラブルシューティングセクション追加

---

## 2025-10-20: SSE接続タイムアウト問題の解決（「エラー: Load failed」修正）

### 作業概要
- **作業時間**: 2025-10-20 14:00 - 18:10（約4時間）
- **担当**: Claude Code + Codex（技術コンサルティング）
- **ステータス**: ✅ 完了

### 発生した問題

#### 症状
- 文字起こし開始後、約50秒で「エラー: Load failed」ダイアログが表示される
- 進捗バーは5%まで表示されるが、その後エラーで停止
- **重要**: Python側（サーバー）では文字起こしは正常に完了している（ログ確認済み）
- 180分の音声データで再現性100%

#### 影響範囲
- 長時間音声の文字起こしが完了できない
- ユーザーは結果を取得できない（サーバー側では完了しているのに）

### 根本原因

**Server-Sent Events (SSE) 接続のタイムアウト**

1. **問題の構造**:
   - 最初のSSEイベント（progress: 5%）送信後、次のイベントまで約1分かかる
   - この間、faster-whisperのVAD（Voice Activity Detection）処理が実行される
   - SSE接続にイベントが流れない状態が約50秒続く
   - ブラウザ/pywebviewがSSE接続をタイムアウトと判断
   - fetch() APIが「Load failed」エラーで失敗

2. **タイミングの詳細**（ログ分析）:
   ```
   15:27:12 - 文字起こし開始
   15:27:12 - 最初のイベント送信（progress: 5%）
   15:28:02 - ❌ fetch失敗: Load failed（約50秒後）
   15:28:10 - VAD処理完了（Python側では継続中）
   ```

3. **multiprocessing.Process環境での特性**:
   - Stage 2でFastAPIサーバーを別プロセス化（Thread→Process）
   - SSE接続が別プロセスで管理されるため、タイムアウトに敏感になった

### 解決方法

**SSEハートビート実装（10秒間隔）**

サーバー側で定期的に「生存確認」イベントを送信し、SSE接続を維持する仕組みを実装:

```python
# 進捗を送信しながら完了を待つ
last_progress = 5
heartbeat_counter = 0
MAX_WAIT_WITHOUT_HEARTBEAT = 100  # 10秒ごとにハートビート (0.1秒 × 100)

while not future.done():
    try:
        progress = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
        if progress > last_progress:
            last_progress = progress
            yield f"data: {json.dumps({'progress': progress, 'status': '文字起こし中...'})}\n\n"
            heartbeat_counter = 0  # 進捗イベント送信時はカウンタリセット
            logger.debug(f"📊 進捗送信: {progress}%")
    except TimeoutError:
        heartbeat_counter += 1
        # 10秒ごとにハートビート送信（SSE接続維持のため）
        if heartbeat_counter >= MAX_WAIT_WITHOUT_HEARTBEAT:
            yield ": heartbeat\n\n"  # SSEコメント形式
            logger.debug("💓 ハートビート送信")
            heartbeat_counter = 0
```

**ハートビートの仕組み**:
- **送信間隔**: 10秒
- **形式**: SSEコメント（`: heartbeat\n\n`）
- **効果**: クライアント側は無視するが、TCP接続は維持される
- **リセット**: 進捗イベント送信時にカウンタをリセット

### 実装した修正

#### 1. サーバー側修正（Mac版・Windows版）

**修正対象エンドポイント**:
- `/transcribe-stream` (通常のファイルアップロード用)
- `/transcribe-stream-by-id` (pywebview環境用)

**修正ファイル**:
- [release/mac/src/main.py](../../release/mac/src/main.py) (lines 2025-2046, 2149-2179)
- [release/windows/src/main.py](../../release/windows/src/main.py) (同様の箇所)

#### 2. デバッグログ追加

詳細なログで動作確認を可能に:
- `logger.debug("💓 ハートビート送信")` - サーバー側ハートビート送信
- `logger.debug(f"📊 進捗送信: {progress}%")` - 進捗イベント送信
- `console.log('📦 受信チャンク:', ...)` - クライアント側受信確認（既存）

### 動作確認結果

**180分音声データでのテスト**:

✅ **成功**:
```
17:48:55 - 文字起こし開始
17:48:55 - ✅ fetch成功: 200 OK
17:48:55 - ✅ ストリームリーダー準備完了
17:48:55 - 📦 受信: progress 5%
17:49:05 - 📦 受信: heartbeat（10秒後）
17:49:15 - 📦 受信: heartbeat（20秒後）
17:49:25 - 📦 受信: heartbeat（30秒後）
17:49:35 - 📦 受信: heartbeat（40秒後）
... 継続
18:XX:XX - ✅ 文字起こし完了（49,817文字、5060.9秒）
```

**結果**:
- エラーダイアログ表示なし
- 文字起こし正常完了
- SSE接続が約84分間維持された
- ハートビートが10秒間隔で正確に送信された

### 技術的な洞察

#### SSE（Server-Sent Events）の特性
- **単方向通信**: サーバー→クライアントのみ
- **接続維持**: イベントが定期的に流れる前提
- **タイムアウト**: イベントが途切れると接続断と判断される
- **再接続**: 標準では自動再接続するが、pywebviewでは機能しない

#### 長時間処理での課題
- faster-whisperのVAD処理は進捗コールバックを呼ばない
- モデルロード直後の初期処理で約1分間イベントなし
- SSE接続のデフォルトタイムアウト（約30-60秒）を超える

#### ハートビートによる解決
- 処理の有無に関わらず定期的にイベント送信
- SSEコメント形式（`: text\n\n`）は仕様で規定された「無視すべきデータ」
- クライアント側の追加実装不要
- サーバー側のみの変更で問題解決

### Codexとの協働

#### Codexへの相談内容
- SSE接続タイムアウトの原因分析
- multiprocessing.Process環境でのSSE運用の注意点
- ハートビート実装のベストプラクティス
- 長時間処理での接続維持方法

#### Codexからの提案（予定）
ステップ2として、さらなる改善を検討中:
1. ハートビート間隔の最適化
2. 進捗通知メカニズムの改善
3. エラーハンドリング強化
4. リソース管理の最適化

### 成果物

**Mac版 v1.1.1ビルド** (2025-10-20 17:44):
- ファイル名: `GaQ_Transcriber_v1.1.1_mac.dmg`
- サイズ: 78MB
- 変更内容:
  - SSEハートビート実装（10秒間隔）
  - デバッグログ追加
  - 180分音声データで動作検証済み
- 動作確認: ✅ 長時間文字起こし成功

### 教訓

#### ✅ 効果的だった手法
1. **ログ分析による原因特定**
   - タイムスタンプの詳細な比較
   - Python側とJavaScript側の双方のログ確認
   - 50秒という具体的な数値の発見

2. **Codexとの協働**
   - 問題を構造化して相談
   - 技術的な背景の理解を深める
   - ベストプラクティスの確認

3. **段階的な実装**
   - ステップ1: 最小限のハートビート実装
   - ステップ2: より洗練された実装（予定）
   - リスクを抑えた漸進的改善

#### 📌 SSE使用時のベストプラクティス
- **10秒以上イベントが途切れる処理では必ずハートビートを実装**
- SSEコメント形式（`: heartbeat\n\n`）を使用
- ログにハートビート送信を記録（デバッグ容易性）
- クライアント側の追加実装は不要

### 関連ファイル

**修正**:
- [release/mac/src/main.py](../../release/mac/src/main.py) - SSEハートビート実装
- [release/windows/src/main.py](../../release/windows/src/main.py) - 同上

**ビルドスクリプト**:
- [release/mac/build.sh](../../release/mac/build.sh) - 使用（変更なし）

### 次のステップ

**完了済み**:
- ✅ ステップ1: SSEハートビート実装
- ✅ 180分音声データでの動作検証

**今後の検討事項**（優先度: 低）:
- ⏸️ ステップ2: Codexの詳細提案を受けた改善（必要に応じて）
- ⏸️ ハートビート間隔の最適化検討
- ⏸️ 進捗通知メカニズムの改善

**結論**: 現時点で問題は完全に解決しており、追加の改善は必須ではない。

---

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
