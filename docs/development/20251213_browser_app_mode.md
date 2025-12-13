# 開発ログ - 2025-12-13 (ブラウザアプリモード採用)

**From**: Claude Code（実装エンジニア）
**To**: Codex（アーキテクト）
**CC**: Yoshihitoさん（プロジェクトオーナー）

---

## 報告概要

Windows版 v1.2.10 をリリース。pythonnet依存を完全に解消し、ブラウザアプリモードをデフォルトに変更。

## 問題の経緯

### 発生した問題

v1.2.8〜v1.2.9 で pythonnet 初期化の修正を試みたが、GitHub Actionsでビルドした配布版では依然として起動に失敗していた。

```text
❌ EdgeChromium backendの読み込みに失敗: No module named 'clr'
```

ローカルビルドは動作するが、GitHubダウンロード版は動作しないという状況が続いていた。

### 根本原因

- pywebview の Windows バックエンド（winforms）は pythonnet を経由して .NET の WebView2 を利用
- pythonnet は PyInstaller でのバンドルが複雑で、環境依存の問題が発生しやすい
- GitHub Actions 環境と実行環境の差異により、正しく初期化できないケースがあった

## 採用した解決策

### ブラウザアプリモード

Codex（アーキテクト）の提案により、pythonnet/pywebview に依存しない方式に切り替え：

1. **デフォルト動作**: Edge/Chrome のアプリモード（`--app` フラグ）で起動
2. **UIの最適化**: アプリモードはブラウザUIを非表示にし、専用アプリのような見た目を実現
3. **フォールバック**: ネイティブウィンドウが必要な場合は `GAQ_USE_NATIVE_WINDOW=1` 環境変数で選択可能

### 実装詳細

```python
# Edge を優先的に探す（Windows標準）
edge_path = shutil.which("msedge")
if not edge_path:
    edge_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in edge_candidates:
        if os.path.exists(candidate):
            edge_path = candidate
            break

# アプリモードで起動
if edge_path:
    browser_process = subprocess.Popen([
        edge_path,
        f"--app={url}",
        "--new-window",
        "--disable-extensions",
    ])
```

## 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| `release/windows/src/main_app.py` | ブラウザアプリモード実装、Edge/Chrome検出ロジック追加 |
| `release/windows/src/config.py` | APP_VERSION を 1.2.10 に更新 |
| `release/windows/src/main.py` | HTMLタイトルにバージョン追加（表示は要調整） |
| `docs/handbook/release_status.md` | v1.2.10 情報に更新 |

## メリット

1. **安定性向上**: pythonnet の複雑なバンドル問題を完全に回避
2. **軽量化**: pythonnet/clr_loader のDLLが不要になり、バイナリサイズ削減の可能性
3. **互換性向上**: Edge は Windows 10/11 に標準搭載されており、追加インストール不要
4. **保守性向上**: pywebview のバージョン更新による pythonnet 互換性問題を回避

## 動作確認

### ローカルテスト

- ✅ Edge アプリモードで起動確認
- ✅ ファイル選択機能
- ✅ 文字起こし処理
- ✅ 結果表示・コピー

### GitHub Actions ビルド

- ✅ ビルド成功（Run ID: 20190278878、3分33秒）
- ✅ リリース公開: [v1.2.10](https://github.com/yoshihito-tsuji/GaQ_app/releases/tag/vv1.2.10)
- ✅ GitHubダウンロード版の動作確認完了（Yoshihitoさん確認）

## 環境変数オプション

| 変数 | 値 | 効果 |
|------|-----|------|
| `GAQ_USE_NATIVE_WINDOW` | `1` | ネイティブウィンドウ（pywebview）を強制使用 |

## 今後の検討事項

1. **タイトルバーのバージョン表示**: 現状では反映されていない（優先度低）
2. **Chrome フォールバック**: Edge が見つからない場合は Chrome を使用（実装済み）
3. **ブラウザなしフォールバック**: どちらも見つからない場合は標準ブラウザで開く（実装済み）

---

**作成日時**: 2025-12-13 18:45 JST
**報告者**: Claude Code
