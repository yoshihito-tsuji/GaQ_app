# Windows フォルダ構成ガイド (v1.2.3 以降)

```
release/windows/
├── artifacts/           # 生成物一式（Git には含めない想定）
│   ├── dist/            # PyInstaller 出力先
│   ├── build/           # PyInstaller 作業フォルダ
│   ├── releases/        # 公開用パッケージ（旧 distribution を移動）
│   ├── uploads/         # 一時アップロード置き場（旧 uploads を移動）
│   └── legacy_test/     # 旧 test_portable を保管（必要に応じ整理）
├── installer/           # Inno Setup などのインストーラスクリプト
├── src/                 # アプリ本体（Python ソース、spec が参照）
├── venv/                # ビルド用仮想環境
├── build.bat            # ビルドエントリポイント（dist/build を artifacts 配下に出力）
├── GaQ_Transcriber.spec # PyInstaller 設定
└── *.md / *.py          # 開発ドキュメント・補助スクリプト
```

## 運用ルール
- 生成物は `artifacts/` 配下に集約し、リポジトリ直下をクリーンに保つ。
- ビルドは `build.bat` を実行すれば `artifacts/dist` と `artifacts/build` を自動作成する。
- 旧 CEF (`cefpython3`) の残骸は削除済み。今後も WebView2 (winforms) をデフォルトとし、不要な依存は追加しない。
- 旧パッケージや一時ファイルは `artifacts/legacy_test` / `artifacts/uploads` に隔離。不要になれば整理・削除可。

## チェックリスト（新しい開発者向け）
1. Python 3.12.x をインストール。
2. `build.bat` を実行（venv 自動作成 + 依存インストール + PyInstaller 実行）。
3. 成果物は `artifacts/dist/GaQ_Transcriber/GaQ_Transcriber.exe` を確認。
4. リリースパッケージは `artifacts/releases` に配置し、GitHub Release へアップロード。

