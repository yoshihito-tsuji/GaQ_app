# Codexへの報告 - 2025-12-12

**From**: Claude Code（実装エンジニア）
**To**: Codex（アーキテクト）
**CC**: Yoshihitoさん（プロジェクトオーナー）

---

## 報告概要

Windows版起動不能問題の調査・修正を完了し、v1.2.2 をリリースしました。

## 実施内容

### 1. 原因調査

Codexの指示に従い、Windows版の起動不能問題を調査しました。

**調査結果**:
- `pywebview[cef]` が `cefpython3` を依存として引き込んでいた
- `cefpython3 v66.1` は **Python 3.8以下のみサポート**
- GitHub Actions は Python 3.12 を使用しており、互換性がない
- ビルドログに以下の警告が多数出力:
  ```
  Library not found: could not resolve 'python38.dll', dependency of 'cefpython3\cefpython_py38.pyd'
  ```

**不安定動作の原因**:
- WebView2 がインストール済みの環境 → EdgeChromium バックエンドで起動成功
- WebView2 がない環境 → CEF にフォールバック → Python バージョン不整合で起動失敗

### 2. 修正実施

| ファイル | 変更内容 |
|---------|---------|
| `release/windows/src/requirements.txt` | `pywebview[cef]>=4.0.0` → `pywebview>=4.0.0` |
| `release/windows/GaQ_Transcriber.spec` | EdgeChromium用 hiddenimports 追加 |

**追加した hiddenimports**:
```python
'webview',
'webview.platforms',
'webview.platforms.edgechromium',
'bottle',
'proxy_tools',
```

### 3. リリース

| バージョン | 内容 |
|-----------|------|
| v1.2.1 | CEF依存削除、Windows起動問題修正 |
| v1.2.2 | 固定名アセット追加（latest URL対応） |

**v1.2.2 リリースURL**: https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/v1.2.2

## 成果

1. **起動問題解消**: Windows 11 での動作確認完了（Yoshihitoさん検証済み）
2. **パッケージサイズ削減**: 約150MB → 約100MB（CEF削除で約50MB削減）
3. **latest URL対応**: 固定名アセットにより常に最新版へのダイレクトリンクが可能に

## ダイレクトダウンロードURL

```
Windows: https://github.com/yoshihito-tsuji/GaQ_app/releases/latest/download/GaQ_Transcriber_Windows.zip
macOS:   https://github.com/yoshihito-tsuji/GaQ_app/releases/latest/download/GaQ_Transcriber_macOS.dmg
```

## 技術的補足

### pywebview バックエンド選択（Windows）

pywebview は以下の優先順位でバックエンドを選択:
1. **EdgeChromium (WebView2)** - Windows 10/11 標準搭載
2. **MSHTML (IE)** - レガシー
3. **CEF** - 今回削除

Windows 10/11 では WebView2 が標準搭載されているため、CEF は不要と判断しました。

### 対応OS

- **Windows 11**: 動作確認済み
- **Windows 10**: WebView2 標準搭載のため問題なし
- **Windows 8.1以下**: WebView2 の手動インストールが必要な可能性あり（非対応方針）

## 確認依頼

1. 修正方針に問題がないか
2. 追加で必要な対応があるか
3. Mac版への影響確認（変更なし、動作確認のみ）

---

**報告日時**: 2025-12-12
**報告者**: Claude Code
