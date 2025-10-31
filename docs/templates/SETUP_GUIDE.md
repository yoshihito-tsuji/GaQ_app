# 新規プロジェクトへの協働環境セットアップガイド

このガイドでは、GaQ_appで確立した**Claude Code + Codexの協働環境**を、新規プロジェクトに導入する手順を説明します。

---

## 📋 前提条件

- Mac上でCursor（Claude Code）が利用可能
- 新規プロジェクト用のフォルダを作成済み（例: `~/Claude_Code/Pop_app`）
- GaQ_appプロジェクトから以下の4つのテンプレートファイルが利用可能:
  - `@claude.md.template`
  - `@codex.md.template`
  - `CLAUDE.md.template`
  - `README.md.template`

---

## 🚀 セットアップ手順

### ステップ1: テンプレートファイルのコピー

新規プロジェクトフォルダに4つのテンプレートファイルをコピーします。

```bash
# 新規プロジェクトフォルダに移動（例: Pop_app）
cd ~/Claude_Code/Pop_app

# GaQ_appのテンプレートをコピー
cp ~/Claude_Code/GaQ_app/docs/templates/@claude.md.template ./@claude.md
cp ~/Claude_Code/GaQ_app/docs/templates/@codex.md.template ./@codex.md
cp ~/Claude_Code/GaQ_app/docs/templates/CLAUDE.md.template ./CLAUDE.md
cp ~/Claude_Code/GaQ_app/docs/templates/README.md.template ./README.md
```

### ステップ2: プロジェクト固有情報のカスタマイズ

コピーした4つのファイルを、プロジェクトの内容に合わせて編集します。

#### 2-1. CLAUDE.md の編集

以下の箇所をプロジェクト固有の内容に書き換えてください：

**必須編集箇所**:
- `## 🧭 開発の目的` セクション
  - プロジェクトの目的を具体的に記載
  - 例: 「小中学校の教員向けに、人口ピラミッドを視覚的に表現するツールを作成します」

**オプション編集箇所**:
- `## 🖥️ 開発環境・プラットフォーム方針` セクション
  - ターゲットプラットフォーム、配布形式などを記載（必要に応じて）

#### 2-2. README.md の編集

以下の箇所を書き換えてください：

**必須編集箇所**:
- `# 【プロジェクト名】` → 実際のプロジェクト名に変更
- `## 基本情報` セクション
  - 開発元、対応プラットフォーム、主要技術
- `## プロジェクトの目的` セクション
  - プロジェクトの具体的な目的
- `## 主要機能` セクション
  - 実装予定の主要機能を列挙

**オプション編集箇所**:
- `## ディレクトリ構成` セクション
  - プロジェクトのフォルダ構成に合わせて更新

#### 2-3. @claude.md と @codex.md

基本的には**そのまま使用可能**です。特別なカスタマイズは不要ですが、以下を確認してください：

- `@claude.md`:
  - `## Startup Procedure` セクションで、README.mdやHISTORY.mdへの参照パスが正しいか確認

- `@codex.md`:
  - 特にカスタマイズ不要（そのまま使用）

### ステップ3: ディレクトリ構成の作成

プロジェクトの基本的なフォルダ構成を作成します。

```bash
# 新規プロジェクトフォルダで実行
mkdir -p docs/development
mkdir -p docs/team_ops
mkdir -p src
mkdir -p test

# 開発履歴ファイルの作成
touch docs/HISTORY.md
```

**docs/HISTORY.md の初期内容**:
```markdown
# 【プロジェクト名】 - 開発履歴

## YYYY-MM-DD: プロジェクト開始

### 作業概要
- プロジェクト立ち上げ
- 協働環境セットアップ完了

### 初期構成
- Claude Code + Codex協働体制の確立
- 基本ディレクトリ構成の作成

---

**最終更新**: YYYY-MM-DD
**ブランチ**: main
```

### ステップ4: Git初期化（オプション）

プロジェクトをGit管理する場合は、以下を実行します。

```bash
# Gitリポジトリの初期化
git init

# 初期コミット
git add .
git commit -m "初期コミット: 協働環境セットアップ完了"
```

---

## 🎯 セットアップ完了後の確認事項

以下のチェックリストで、セットアップが正しく完了したか確認してください。

### 必須ファイルの存在確認

```bash
# 新規プロジェクトフォルダで実行
ls -la @claude.md @codex.md CLAUDE.md README.md
```

期待される出力:
```
-rw-r--r--  1 user  staff  【サイズ】 @claude.md
-rw-r--r--  1 user  staff  【サイズ】 @codex.md
-rw-r--r--  1 user  staff  【サイズ】 CLAUDE.md
-rw-r--r--  1 user  staff  【サイズ】 README.md
```

### ディレクトリ構成の確認

```bash
tree -L 2
```

期待される構成:
```
.
├── @claude.md
├── @codex.md
├── CLAUDE.md
├── README.md
├── docs/
│   ├── HISTORY.md
│   ├── development/
│   └── team_ops/
├── src/
└── test/
```

### カスタマイズ内容の確認

- [ ] CLAUDE.md の「開発の目的」セクションが編集されている
- [ ] README.md のプロジェクト名が変更されている
- [ ] README.md の「基本情報」「主要機能」が記載されている
- [ ] docs/HISTORY.md が初期化されている

---

## 📖 セットアップ完了後の次のステップ

セットアップが完了したら、以下の手順でClaude CodeとCodexに作業を開始してもらいます。

### Yoshihitoさんが実施する手順

#### 【手順1】Claude Codeに最初の指示を出す

新規プロジェクトのフォルダ（例: Pop_app）をCursorで開き、以下の指示を出してください：

```
@claude.md と CLAUDE.md を読んで、このプロジェクトの役割とコミュニケーション形式を確認してください。
その後、README.md と docs/HISTORY.md を読んで、プロジェクトの概要を把握してください。

準備ができたら、プロジェクトの開発方針と次のステップを提案してください。
```

#### 【手順2】Claude Codeからの応答を確認

Claude Codeが以下の内容を確認・報告します：
- プロジェクトの目的と開発方針の理解
- 現在のファイル構成の確認
- 次のステップの提案

#### 【手順3】Codexに設計を依頼（必要に応じて）

大きな機能実装や設計判断が必要な場合は、Codexに相談します。

```
@codex.md を読んで、あなたの役割を確認してください。

【プロジェクトの具体的な要望を記載】

例:
「人口ピラミッド作成アプリを開発したいです。
主な機能は、CSVデータの読み込み、グラフ表示、画像保存です。
UIはHTML/JavaScriptで、バックエンドはPythonを想定しています。

全体のアーキテクチャと開発ステップを提案してください。」
```

#### 【手順4】Codexの提案をClaude Codeに実装依頼

Codexが設計案を提示したら、Claude Codeに実装を依頼します。

```
From: Yoshihitoさん
To: Claude Code

Codexが提案した設計案を元に、以下の実装を開始してください：

【Codexの提案内容を要約】

まずは、基本的なディレクトリ構成とファイルの骨組みを作成してください。
```

---

## 🎉 セットアップ完了！

以上で、新規プロジェクトへの協働環境セットアップは完了です。

GaQ_appで確立したClaude Code + Codexの協働体制を活用して、効率的な開発を進めてください。

---

## 🆘 トラブルシューティング

### Q1: テンプレートファイルが見つからない
**回答**: GaQ_appプロジェクトの `docs/templates/` ディレクトリに移動し、ファイルが存在するか確認してください。

```bash
ls ~/Claude_Code/GaQ_app/docs/templates/
```

### Q2: Claude Codeが@claude.mdを読んでくれない
**回答**: Cursorで新規プロジェクトフォルダを開き、明示的に以下の指示を出してください：

```
@claude.md を読んで、あなたの役割とコミュニケーション形式を確認してください。
```

### Q3: README.mdのカスタマイズ箇所がわからない
**回答**: `【】` で囲まれた箇所をプロジェクト固有の内容に置き換えてください。例:
- `【プロジェクト名】` → `Pop_app（人口ピラミッド作成アプリ）`
- `【開発者名・組織名】` → `公立はこだて未来大学 辻研究室`

---

**最終更新**: 2025-10-31
**作成者**: Claude Code
**テンプレートバージョン**: v1.0
