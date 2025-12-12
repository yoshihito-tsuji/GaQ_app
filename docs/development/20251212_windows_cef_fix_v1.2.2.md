# 開発ログ - 2025-12-12

## 作業概要
- **日付**: 2025-12-12
- **担当者**: Claude Code（実装）、Codex（設計指示）、Yoshihitoさん（検証・承認）
- **ブランチ**: main

## 作業内容

### 実施した作業

#### 1. Windows版起動不能問題の調査・修正（v1.2.1）

**問題**: 一部のWindows環境でアプリが起動しない

**原因調査結果**:
- `pywebview[cef]` が `cefpython3` を依存として引き込んでいた
- `cefpython3 v66.1` は Python 3.8 以下のみサポート
- GitHub Actions のビルド環境は Python 3.12 を使用
- ビルドログに `python38.dll`, `python37.dll` の警告が多数出力

**修正内容**:
1. `release/windows/src/requirements.txt`
   - `pywebview[cef]>=4.0.0` → `pywebview>=4.0.0`（CEF依存を削除）

2. `release/windows/GaQ_Transcriber.spec`
   - pywebview EdgeChromium バックエンド用の hiddenimports を追加:
     - `webview`, `webview.platforms`, `webview.platforms.edgechromium`
     - `bottle`, `proxy_tools`

**効果**:
- Windows 10/11 の標準 WebView2 (EdgeChromium) を使用
- パッケージサイズ: 約150MB → 約100MB（CEF削除で約50MB削減）
- 起動不能問題を解消

#### 2. リリースアセット名の固定化（v1.2.2）

**目的**: `/releases/latest/download/` URL で常に最新版をダウンロード可能にする

**修正内容** (`.github/workflows/build-release.yml`):
- macOS: バージョン付きファイルに加え `GaQ_Transcriber_macOS.dmg` を生成
- Windows: バージョン付きファイルに加え `GaQ_Transcriber_Windows.zip` を生成

**ダイレクトダウンロードURL**:
- Windows: `https://github.com/yoshihito-tsuji/GaQ_app/releases/latest/download/GaQ_Transcriber_Windows.zip`
- macOS: `https://github.com/yoshihito-tsuji/GaQ_app/releases/latest/download/GaQ_Transcriber_macOS.dmg`

### 変更したファイル

| ファイル | 変更内容 |
|---------|---------|
| `release/windows/src/requirements.txt` | CEF依存を削除 |
| `release/windows/GaQ_Transcriber.spec` | EdgeChromium hiddenimports追加 |
| `release/windows/src/config.py` | APP_VERSION: 1.1.1 → 1.2.2 |
| `release/mac/src/config.py` | APP_VERSION: 1.1.1 → 1.2.2 |
| `.github/workflows/build-release.yml` | 固定名アセット生成を追加 |

## 問題と解決

### 発生した問題
**問題の内容**: Windows版が一部のユーザー環境で起動しない

**原因**:
- cefpython3 が Python 3.12 と非互換（Python 3.8以下のみサポート）
- pywebview の CEF バックエンドが正しく機能しない
- WebView2 がインストールされている環境では成功、ない環境ではCEFにフォールバックして失敗

**解決策**:
- CEF依存を完全に削除
- EdgeChromium (WebView2) バックエンドのみを使用
- Windows 10/11 には WebView2 が標準搭載されているため問題なし

## テスト結果

### テスト項目
- [x] Windows 11 での起動確認（Yoshihitoさんによる実機テスト）
- [x] 文字起こし機能の動作確認
- [x] GitHub Actions ビルド成功確認
- [x] リリースアセットの確認（固定名ファイルの存在）

### テスト環境
- OS: Windows 11
- Python: 3.12（GitHub Actions）
- pywebview バックエンド: EdgeChromium (WebView2)

## リリース情報

| バージョン | リリース日 | 主な変更 |
|-----------|-----------|---------|
| v1.2.1 | 2025-12-12 | CEF依存削除、Windows起動問題修正 |
| v1.2.2 | 2025-12-12 | 固定名アセット追加（latest URL対応） |

**リリースURL**: https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.2.2

## 次のステップ
- [x] v1.2.1 テストビルド削除
- [x] v1.2.2 正式リリース
- [ ] README.md のバージョン情報更新（任意）

## メモ・備考

### pywebview バックエンド優先順位（Windows）
1. EdgeChromium (WebView2) - Windows 10/11 標準
2. MSHTML (IE) - レガシー
3. CEF (Chromium Embedded Framework) - 今回削除

### Windows 10/11 以前の対応
Windows 10 より前のバージョン（8.1以下）は WebView2 が標準搭載されていないため、
手動でのインストールが必要になる可能性がある。今回は Windows 11 を基準とした。

---

**作成日時**: 2025-12-12 14:50
