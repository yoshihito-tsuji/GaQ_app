# GaQ Offline Transcriber v1.1.0 開発ドキュメント

## プロジェクト概要

**GaQ Offline Transcriber**は、オフライン動作するAI文字起こしアプリケーションです。
- faster-whisperを使用
- macOS専用（Python 3.12.7同梱）
- 初回起動時のみ音声認識モデル（約1.5GB）のダウンロードが必要
- モデルダウンロード後は完全にオフラインで動作

---

## ⚠️ 重要：配布バージョンについて

### 配布方針（確定）

**✅ 採用：完全パッケージ版（build_standard）**
- Python環境込み（350MB）
- ユーザーは追加ソフトウェアのインストール不要
- ドラッグ&ドロップですぐに使用可能

**❌ 不採用：軽量インストーラー版（launcher_final）**
- Python環境なし（188KB）
- ユーザーがPython 3をインストール必要
- Homebrewの使用が必要
- 一般ユーザーには困難

### 過去の問題（2025-10-03）

**発生した問題：**
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

**原因：**
- 開発過程でファイルサイズ削減を試みて軽量版を作成
- 両方のバージョンが残ったまま、誤って軽量版を選択
- 開発機ではPython環境があるため問題に気づかなかった

**教訓：**
- ✅ 配布前に別環境で必ず実機テスト
- ✅ DMGサイズを確認（150MB未満は異常）
- ✅ Python環境の存在を確認
- ✅ 「誰でも使える」ことを最優先

---

## ディレクトリ構成

```
GaQ_Transcriber_v1.1.0_Release/
├── build_standard/              ← 配布に使用（完全版）
│   └── GaQ Offline Transcriber.app (356MB)
│       └── Contents/
│           └── Resources/
│               ├── python/      (350MB) - Python 3.12.7同梱
│               └── app/         - アプリケーション本体
│
├── launcher_final/              ← 使用しない（軽量版）
│   └── GaQ_Installer.app (188KB) - Python環境なし
│
├── dmg_contents/                - DMG作成用一時フォルダ
├── distribution/                - 配布用DMG格納
│   └── GaQ_Transcriber_v1.1.0_Final.dmg (164MB)
│
└── README.md                    - このファイル
```

---

## DMG作成手順（正しい方法）

### ステップ1：dmg_contents準備

```bash
cd ~/Claude_Code/GaQ_Transcriber_v1.1.0_Release/

# クリーンな状態から開始
rm -rf dmg_contents
mkdir -p dmg_contents

# ✅ 正しい：build_standardを使用
cp -R "build_standard/GaQ Offline Transcriber.app" dmg_contents/

# ❌ 間違い：launcher_finalは使用しない
# cp -R launcher_final/GaQ_Installer.app dmg_contents/

# Applicationsショートカット
ln -s /Applications dmg_contents/Applications

# インストール手順書
cat > dmg_contents/インストール方法.txt << 'EOF'
【インストール方法】
1. 「GaQ Offline Transcriber.app」を「Applications」にドラッグ
2. アプリケーションから起動

【動作環境】
- macOS 10.15以降
- 追加ソフトウェア不要
EOF
```

### ステップ2：サイズ確認（必須）

```bash
# アプリのサイズ確認
du -sh dmg_contents/GaQ\ Offline\ Transcriber.app
# 期待値：約350MB

# Python環境の確認
ls -lh dmg_contents/GaQ\ Offline\ Transcriber.app/Contents/Resources/python/
# 期待値：pythonディレクトリが存在

# ⚠️ 350MB未満の場合、何か問題がある
```

### ステップ3：DMG作成

```bash
hdiutil create -volname "GaQ Offline Transcriber v1.1.0" \
  -srcfolder dmg_contents \
  -ov -format UDZO \
  -imagekey zlib-level=9 \
  distribution/GaQ_Transcriber_v1.1.0_Final.dmg

# DMGサイズ確認
ls -lh distribution/GaQ_Transcriber_v1.1.0_Final.dmg
# 期待値：150MB〜200MB

# ⚠️ 150MB未満の場合、Python環境が含まれていない
```

### ステップ4：動作確認（必須）

```bash
# DMGをマウント
hdiutil attach distribution/GaQ_Transcriber_v1.1.0_Final.dmg

# Python環境の確認
ls "/Volumes/GaQ Offline Transcriber v1.1.0/GaQ Offline Transcriber.app/Contents/Resources/python/"

# Pythonバージョン確認
"/Volumes/GaQ Offline Transcriber v1.1.0/GaQ Offline Transcriber.app/Contents/Resources/python/bin/python3" --version
# 期待値：Python 3.12.7

# 必須パッケージ確認
"/Volumes/GaQ Offline Transcriber v1.1.0/GaQ Offline Transcriber.app/Contents/Resources/python/bin/python3" -c "import fastapi, uvicorn, faster_whisper; print('OK')"
# 期待値：OK
```

---

## 配布前チェックリスト

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

## 実装済み機能（v1.1.0）

### コア機能
- faster-whisper文字起こし（Medium/Large-v3対応）
- リアルタイムプログレスバー（SSE実装）
- 改行処理（句読点・80文字折り返し）
- 結果コピー・txt保存機能
- モデル管理機能

### UI/UX改善
- ウィンドウタイトル：「GaQ Offline Transcriber v1.1.0」
- 研究室表記：「公立はこだて未来大学：辻研究室（tsuji-lab.net）」
- プログレスバーのシャインエフェクト（4秒、明るさ50%）
- コピーメッセージ改善：「文字起こし結果をコピーしました。適切な位置にペーストしてください」

### ブラウザ起動
- Chrome推奨（アプリモード、独立プロファイル）
- フォールバック：デフォルトブラウザ

---

## 開発時の注意事項

### main.pyの修正

修正は常にbuild_standard/で行う：

```bash
# ✅ 正しい修正場所
build_standard/main.py
build_standard/GaQ Offline Transcriber.app/Contents/Resources/app/main.py

# ❌ ここを修正してはいけない（配布に使用しない）
launcher_final/app/main.py
```

### ブラウザキャッシュ

開発時は必ずキャッシュクリア：
- Chrome DevTools（F12）→ Network → "Disable cache"
- スーパーリロード（Cmd + Shift + R）

### Git管理

重要なマイルストーンでコミット：

```bash
git add .
git commit -m "feat: v1.1.0 完成 - 完全パッケージ版"
git tag v1.1.0
```

---

## トラブルシューティング

### DMGサイズが異常に小さい（150MB未満）

**原因：** Python環境が含まれていない

**対処：**
1. build_standard/を使用しているか確認
2. dmg_contents/のサイズを確認
3. Python環境の存在を確認
4. DMGを再作成

### アプリが起動しない

**原因：** Python環境の破損

**対処：**
1. Python実行ファイルが存在するか確認
2. 必須パッケージがインストールされているか確認
3. 起動スクリプト（launch.sh）を確認

---

## 連絡先

**公立はこだて未来大学：辻研究室**
- Website: https://tsuji-lab.net

---

**最終更新：** 2025-10-03
**バージョン：** v1.1.0
**ステータス：** 配布準備完了
