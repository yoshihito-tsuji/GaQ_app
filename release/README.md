# ⚠️ このディレクトリについて

## 🚨 重要な注意事項

**このディレクトリ内の `src/` ファイルは自動生成されるべきファイルです。**

### ❌ 禁止事項

以下のファイルを**直接編集しないでください**：

```
release/mac/src/main.py
release/mac/src/main_app.py
release/mac/src/transcribe.py
release/mac/src/config.py

release/windows/src/main.py
release/windows/src/main_app.py
release/windows/src/transcribe.py
release/windows/src/config.py
```

### ✅ 正しい編集手順

#### 現在（暫定）

1. **Mac版とWindows版の両方を編集**
   ```bash
   # Mac版を編集
   vim release/mac/src/transcribe.py

   # Windows版も同じ内容に編集
   vim release/windows/src/transcribe.py

   # 差分がないことを確認
   ./scripts/check_sync.sh
   ```

2. **共通コードは必ず両方に反映**
   - `transcribe.py` - 文字起こし処理（完全に共通）
   - `config.py` - 設定ファイル（完全に共通）

3. **プラットフォーム固有コードの注意点**
   - `main.py` - FastAPI + pywebview統合（Mac版が最新）
   - `main_app.py` - アプリケーションエントリーポイント（Mac版が最新）
   - これらは行数が異なるが、共通部分は同期すること

#### 将来（理想）

```bash
# 1. src/ で編集
vim src/common/transcribe.py

# 2. 全環境にソースを同期
./scripts/sync_sources.sh

# 3. 差分がないことを確認
./scripts/check_sync.sh

# 4. 各環境でビルド
cd release/mac && ./build.sh
cd release/windows && ./build.bat
```

---

## 📁 ディレクトリ構成

```
release/
├── README.md              # ← このファイル
├── mac/                   # Mac版ビルド環境
│   ├── src/               # ⚠️ 自動生成されるべき（現在は手編集）
│   ├── build.sh           # ビルドスクリプト
│   └── GaQ_Transcriber.spec
└── windows/               # Windows版ビルド環境
    ├── src/               # ⚠️ 自動生成されるべき（現在は手編集）
    ├── build.bat          # ビルドスクリプト
    └── GaQ_Transcriber.spec
```

---

## 🔍 差分確認方法

### 差分チェックスクリプトの実行

```bash
# プロジェクトルートで実行
./scripts/check_sync.sh
```

**出力例**:
```
✓ transcribe.py - 同期済み
✗ config.py - 差分あり
```

### 手動での差分確認

```bash
# transcribe.py の差分確認
diff release/mac/src/transcribe.py release/windows/src/transcribe.py

# config.py の差分確認
diff release/mac/src/config.py release/windows/src/config.py
```

---

## 🛠️ 問題が起きた場合

### 「片方だけ修正してしまった」場合

1. **最新版を確認**
   ```bash
   # 最終更新日時を比較
   git log -1 --format="%ai %s" release/mac/src/transcribe.py
   git log -1 --format="%ai %s" release/windows/src/transcribe.py
   ```

2. **新しい方をコピー**
   ```bash
   # Mac版が最新の場合
   cp release/mac/src/transcribe.py release/windows/src/transcribe.py

   # Windows版が最新の場合
   cp release/windows/src/transcribe.py release/mac/src/transcribe.py
   ```

3. **差分がなくなったことを確認**
   ```bash
   ./scripts/check_sync.sh
   ```

---

## 📚 関連ドキュメント

- [リポジトリ構成改善提案](../docs/development/20251018_repository_restructure_proposal.md)
- [開発ワークフロー](../README.md#開発者向け開発ワークフロー)
- [開発履歴](../docs/HISTORY.md)

---

**最終更新**: 2025-10-18
**目的**: 手編集禁止の明示、再発防止
