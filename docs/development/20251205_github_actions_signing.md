# 開発ログ: GitHub Actions CI/CD & macOS署名・公証の導入

**日付**: 2025-12-05
**担当**: Claude Code
**バージョン**: v1.2.0

---

## 概要

macOS版のコード署名・Apple公証をGitHub Actionsで自動化し、v1.2.0としてリリースを完了した。

---

## 実装内容

### 1. GitHub Actions ワークフロー作成

**ファイル**: `.github/workflows/build-release.yml`

- **トリガー**: `v*`タグプッシュ、手動実行（workflow_dispatch）
- **macOSビルド**: 署名・公証付きDMG生成
- **Windowsビルド**: ポータブルZIP生成
- **Release作成**: Draft状態で自動作成

### 2. build.sh の拡張

**ファイル**: `release/mac/build.sh`

新規オプション:
- `--sign`: Developer ID署名のみ
- `--notarize`: 署名 + Apple公証
- `--skip-dmg`: DMG作成をスキップ

機能:
- Keychainから証明書を自動検出
- notarytool によるKeychain認証情報サポート
- 署名・公証済み版用のシンプルなインストール方法を自動生成
- DMGへの署名とSHA256ハッシュ生成

### 3. GitHub Secrets 設定

| Secret名 | 用途 |
|----------|------|
| APPLE_DEVELOPER_ID_CERT_BASE64 | Developer ID証明書（base64） |
| APPLE_DEVELOPER_ID_CERT_PASSWORD | 証明書パスフレーズ |
| APPLE_ID | Apple ID |
| APPLE_TEAM_ID | Team ID |
| APPLE_APP_SPECIFIC_PASSWORD | App固有パスワード |

### 4. ドキュメント更新

- `docs/handbook/development_workflow.md`: GitHub Actionsセクション追加
- `docs/guides/BUILD_GUIDE.md`: 署名・公証セクション追加

---

## テスト結果

| テスト | 結果 |
|--------|------|
| v1.2.0-rc2（フル公証テスト） | ✅ 成功 |
| v1.2.0（正式リリース） | ✅ 成功 |

---

## 発生した問題と対応

### 問題1: skip_notarization条件が機能しない

**原因**: GitHub Actionsのboolean inputは文字列として扱われる

**対応**:
```yaml
# Before
if: ${{ !github.event.inputs.skip_notarization }}

# After
if: ${{ github.event.inputs.skip_notarization != 'true' }}
```

### 問題2: 403 Resource not accessible by integration

**原因**: Release作成権限がない

**対応**: ワークフローに権限を追加
```yaml
permissions:
  contents: write
```

---

## リリース情報

### v1.2.0 成果物

| ファイル | 説明 |
|----------|------|
| GaQ_Transcriber_v1.2.0_mac.dmg | macOS版（署名・公証済み） |
| GaQ_Transcriber_v1.2.0_mac.dmg.sha256 | SHA256ハッシュ |
| GaQ_Transcriber_Windows_v1.2.0_Portable.zip | Windows版 |
| GaQ_Transcriber_Windows_v1.2.0_Portable.zip.sha256 | SHA256ハッシュ |

### ダウンロードURL

```
# 最新版リリースページ
https://github.com/yoshihito-tsuji/GaQ_app/releases/latest

# Mac版直接DL
https://github.com/yoshihito-tsuji/GaQ_app/releases/latest/download/GaQ_Transcriber_v1.2.0_mac.dmg

# Windows版直接DL
https://github.com/yoshihito-tsuji/GaQ_app/releases/latest/download/GaQ_Transcriber_Windows_v1.2.0_Portable.zip
```

---

## 今後のリリース手順

1. コード変更をコミット・プッシュ
2. バージョンタグを作成: `git tag v1.x.x`
3. タグをプッシュ: `git push origin v1.x.x`
4. GitHub Actionsが自動でビルド・Draft Release作成
5. Releasesタブで確認後、「Publish release」で公開

---

## 備考

- Windows版のコード署名（MSIX）は見送り（PoPuPプロジェクトと同様）
- macOS版は署名・公証済みのため、Gatekeeperで警告なしにインストール可能
