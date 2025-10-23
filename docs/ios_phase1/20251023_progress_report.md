# iOS版GaQ Transcriber - Phase 1 Week 1 進捗レポート

**作成日**: 2025-10-23
**作成者**: Claude Code
**レビュー**: Codex
**ステータス**: Week 1 ドキュメント作成完了、Yoshihitoさん着手待ち

---

## 📋 目次

1. [本日の主な作業内容](#本日の主な作業内容)
2. [現時点での進捗状況](#現時点での進捗状況)
3. [今後の課題・TODO](#今後の課題todo)
4. [次回再開の目印](#次回再開の目印)

---

## 本日の主な作業内容

### 1. 作成したドキュメント一覧（全5件）

#### ドキュメント1: Xcodeセットアップガイド
**ファイルパス**: [docs/ios_phase1/xcode_setup_guide.md](xcode_setup_guide.md)

**概要**:
- Xcode最新版のインストール手順（Mac App Store経由）
- 必要容量40GB、所要時間の明示
- 初回起動時の設定（Command Line Tools、Simulatorの確認）
- iPhone実機デプロイ準備（ケーブル接続、信頼設定、開発者モード有効化）
- トラブルシューティング5項目

**対象者**: iOS開発初心者（Yoshihitoさん）

**文字数**: 約8,000字

**完了条件**:
- [ ] Xcodeがインストールされている
- [ ] Command Line Toolsが設定されている
- [ ] iPhone実機でテストアプリが起動できる

---

#### ドキュメント2: Apple Developer Program登録ガイド
**ファイルパス**: [docs/ios_phase1/apple_developer_registration.md](apple_developer_registration.md)

**概要**:
- Apple Developer Programの概要（年間¥12,980、TestFlight配布に必須）
- 登録前の準備（Apple ID、2FA、クレジットカード、住所英語表記）
- 登録手順（6ステップ、詳細解説）
- アクティベーションタイムライン（24-48時間）
- App Store Connect初期設定（**重要**: Appレコードはまだ作成不要）
- トラブルシューティング5項目

**対象者**: Apple Developer Program未登録者

**文字数**: 約7,500字

**完了条件**:
- [ ] Apple Developer Programに登録済み
- [ ] アクティベーション完了メール受信
- [ ] App Store Connectにアクセス可能
- [ ] 「Free Applications Agreement」同意済み

**重要な決定事項**:
- ✅ Appレコード作成はPhase 3まで不要（Phase 1-2では作成しない）
- ✅ 理由: Bundle Identifierが確定していない段階での作成は非効率

---

#### ドキュメント3: WhisperKitリアルタイム概要
**ファイルパス**: [docs/ios_phase1/whisperkit_realtime_overview.md](whisperkit_realtime_overview.md)

**概要**:
- WhisperKitの基本情報（Swift製、MIT License、完全オフライン）
- 疑似リアルタイム推論の仕組み（3-5秒遅延のチャンク処理）
- `StreamingTranscriptionView.swift`の実装例（AsyncSequence、MainActor.run）
- チャンク処理の詳細（30秒チャンク、5秒オーバーラップ）
- wordTimestampsによる文境界整形（句読点検出、80文字折り返し）
- 留意点5項目（メモリ管理、エラーハンドリング、バックグラウンド実行、発熱対策、ユーザーフィードバック）

**対象者**: WhisperKit初学者、Swift初学者

**文字数**: 約9,000字

**技術的決定事項**:
- ✅ 疑似リアルタイム方式を採用（完全リアルタイムは困難）
- ✅ チャンク境界対策: オーバーラップ + wordTimestamps活用
- ✅ 句読点補完ロジックはMac/Windows版を参考に実装予定

---

#### ドキュメント4: 性能計測ガイド
**ファイルパス**: [docs/ios_phase1/performance_measurement_guide.md](performance_measurement_guide.md)

**概要**:
- 性能計測の目的と5つの指標（レイテンシ、CPU、メモリ、エネルギー、発熱）
- Xcode Instrumentsの使い方（Time Profiler、Allocations、Energy Log）
- 10分音声テストの詳細手順（5つの計測手順）
- 記録テンプレート（Markdown形式、コピー&ペースト可能）
- 計測結果の共有形式（Googleスプレッドシート、Markdown）
- トラブルシューティング4項目

**対象者**: Xcode Instruments初学者

**文字数**: 約10,000字

**目標値（Phase 1検証）**:

| 指標 | 目標値 | 重要度 |
|------|--------|--------|
| レイテンシ | 1分以内 | 🔴 高 |
| メモリ使用量 | 500MB以下 | 🔴 高 |
| CPU使用率 | 平均50%以下 | 🟡 中 |
| 発熱 | 「温かい」程度 | 🟡 中 |
| バッテリー消費 | 5%以下 | 🟢 低 |

**記録テンプレート提供済み**:
```markdown
| 日付 | デバイス | モデル | 処理時間 | CPU平均 | メモリピーク | Energy | 発熱 | 総合判定 |
```

---

#### ドキュメント5: サンプル音声README
**ファイルパス**: [docs/ios_phase1/sample_audio/README.md](sample_audio/README.md)

**概要**:
- サンプル音声ファイルの要件（10分、日本語、M4A/MP3/WAV）
- ファイル置き場の説明（Git管理外、ローカル配置）
- 利用上の注意（著作権クリア、外部公開不可、テスト専用）
- 推奨サンプル音声の取得方法（3つの選択肢）:
  1. 自分で録音（iPhoneボイスメモ）
  2. パブリックドメイン音源（青空朗読、NHKクリエイティブ・ライブラリー）
  3. 研究室録音（辻先生許可済み）

**対象者**: テスト音声準備者

**文字数**: 約6,000字

**重要な注意事項**:
- ⚠️ 著作権・権利クリアを厳守
- ⚠️ 外部公開禁止（GitHubにはREADMEのみ公開、音声ファイルは非公開）
- ⚠️ `.gitignore`で音声ファイル除外済み

**現状**:
- 疑似パス（`sample_10min.m4a`）のみ記載
- 実ファイルはYoshihitoさんが準備・配置する想定

---

### 2. 共有済みの調査結果・決定事項

#### A. iOS版開発方針の確定

**背景**:
- Yoshihitoさんから「10分程度の音声をリアルタイムで画面表示できるか」「その結果を保存できるか」の2点を重点検証したいという要望
- Large-v3等の長時間モデルは扱わず、短時間・軽量ユースケースに絞る

**決定事項**:
1. **モデル選定**: Small/Base優先、Medium以上は後回し
2. **リアルタイム表示**: WhisperKitの疑似リアルタイム方式を採用
3. **UI構成**: 最小構成（ファイル選択、リアルタイム表示、保存・共有ボタン）
4. **保存先**: アプリ内ファイル + 共有シート

**合意状況**: ✅ Codex承認済み

---

#### B. WhisperKit vs whisper.cpp の選択

**Phase 1での方針**:
- ✅ **WhisperKit採用**（早期検証・学習優先）
- ⏸️ whisper.cppはPhase 4で移行可否を評価（学習進捗次第）

**理由**:
- WhisperKitはSwift製で統合が容易
- whisper.cppはC++ブリッジが必要で学習コスト高
- Phase 1の目的は「技術的実現可能性の検証」

**合意状況**: ✅ Codex承認済み

---

#### C. 初回モデル取得フローの方針

**採用方式**: B. Mediumモデル同梱 + Large-v3は初回DL

**詳細**:
- Mediumモデル（約1.5GB）を初回から同梱
- Large-v3（約2.9GB）は任意ダウンロード
- Wi-Fi必須、サイズ警告、通信オプトイン明示

**推定アプリサイズ**:
- WhisperKit本体: 約50MB
- Mediumモデル: 約1.5GB
- アプリロジック: 約20MB
- **合計**: 約1.6GB（✅ TestFlight 4GB制限以内）

**合意状況**: ✅ Codex承認済み

---

#### D. UIアーキテクチャ

**採用方式**: A. フルネイティブ（SwiftUI + Combine）

**理由**:
- iOS固有UXやアクセシビリティに最適
- メモリ・スレッド制御が容易
- 長期的なメンテナンス性向上

**既存HTML/JavaScriptの扱い**:
- ロジック参照用として活用（直接再利用はしない）

**合意状況**: ✅ Codex承認済み

---

#### E. メモリ・パフォーマンス最適化戦略

**初期方針**:
- **A**: Large系を推奨しない、Medium/Small中心
- **B**: 量子化モデル（4bit/8bit）の効果検証

**段階付け**:
- Phase 1-2: A/Bを優先
- 安定稼働後: C（フォールバック機構）を検討

**合意状況**: ✅ Codex承認済み

---

#### F. 開発優先度（4フェーズ構成）

| Phase | 内容 | 期間 |
|-------|------|------|
| **Phase 1** | WhisperKit動作検証（Week 1-2） | 2週間 |
| **Phase 2** | SwiftUI基本機能実装（Week 3-4） | 2週間 |
| **Phase 3** | TestFlight配布体験 | 1-2週間 |
| **Phase 4** | whisper.cpp移行可否検討 | 未定 |

**現在地**: Phase 1 Week 1 完了、Yoshihitoさん着手待ち

**合意状況**: ✅ Codex承認済み

---

### 3. ディレクトリ構成（完成版）

```
docs/ios_phase1/
├── 20251023_progress_report.md      # このファイル（本日作成）
├── xcode_setup_guide.md              # Xcodeセットアップ（完成）
├── apple_developer_registration.md  # Apple Developer登録（完成）
├── whisperkit_realtime_overview.md  # WhisperKit解説（完成）
├── performance_measurement_guide.md # 性能計測手順（完成）
└── sample_audio/
    └── README.md                     # サンプル音声準備（完成）
```

**Git管理状況**:
- ✅ すべてのMarkdownファイル: コミット対象
- ❌ `sample_audio/*.{m4a,mp3,wav}`: `.gitignore`で除外

---

## 現時点での進捗状況

### Phase 1 Week 1の完了率

**総合進捗**: ✅ **100%完了**

| タスク | 担当 | ステータス |
|--------|------|-----------|
| Xcodeセットアップガイド作成 | Claude Code | ✅ 完了 |
| Apple Developer登録ガイド作成 | Claude Code | ✅ 完了 |
| WhisperKitリアルタイム概要作成 | Claude Code | ✅ 完了 |
| 性能計測ガイド作成 | Claude Code | ✅ 完了 |
| サンプル音声README作成 | Claude Code | ✅ 完了 |

**成果物**:
- ドキュメント: 5件
- 合計文字数: 約40,000字
- すべてMarkdown整形済み、Yoshihitoさんが即座に利用可能

---

### Yoshihitoさん側の次ステップ（着手状況）

**現状**: 📌 **ドキュメント提供済み、着手待ち**

#### ステップ1: 環境構築（推定所要時間: 1-2時間）

**タスク**:
- [ ] [xcode_setup_guide.md](xcode_setup_guide.md) を読む
- [ ] Xcodeをインストール（Mac App Store経由、約40GB）
- [ ] Command Line Toolsを設定
- [ ] iPhone実機を接続し、開発者モードを有効化
- [ ] テストアプリを実機で起動確認

**成功条件**:
- iPhoneで「Hello, world!」アプリが起動する

---

#### ステップ2: Apple Developer登録（推定所要時間: 30分 + 待機24-48時間）

**タスク**:
- [ ] [apple_developer_registration.md](apple_developer_registration.md) を読む
- [ ] Apple Developer Programに登録（¥12,980）
- [ ] アクティベーション完了を待つ（24-48時間）
- [ ] App Store Connectにアクセス確認

**成功条件**:
- 「Membership」ステータスが「Active」になる

---

#### ステップ3: WhisperKit理解（推定所要時間: 30分）

**タスク**:
- [ ] [whisperkit_realtime_overview.md](whisperkit_realtime_overview.md) を読む
- [ ] 疑似リアルタイムの仕組みを理解
- [ ] チャンク処理の流れを把握

**成功条件**:
- AsyncSequence、MainActor.runの概念を理解

---

#### ステップ4: サンプル音声準備（推定所要時間: 10分〜1時間）

**タスク**:
- [ ] [sample_audio/README.md](sample_audio/README.md) を読む
- [ ] 10分音声を準備（自分で録音 or パブリックドメイン音源）
- [ ] `docs/ios_phase1/sample_audio/sample_10min.m4a` に配置

**成功条件**:
- 10分前後の日本語音声ファイルが配置される
- 権利クリア済み（著作権問題なし）

---

#### ステップ5: 性能計測準備（推定所要時間: 30分）

**タスク**:
- [ ] [performance_measurement_guide.md](performance_measurement_guide.md) を読む
- [ ] Xcode Instrumentsの使い方を把握
- [ ] 記録テンプレートをGoogleスプレッドシートにコピー

**成功条件**:
- 計測手順を理解し、準備完了

---

**推定合計時間**: 4-8時間（Apple Developerアクティベーション待機を除く）

**次回Week 2への条件**:
- ✅ 上記ステップ1-5がすべて完了
- ✅ Yoshihitoさんから「環境構築完了」の報告

---

## 今後の課題・TODO

### Yoshihitoさん向け: これから着手していただきたい項目

#### 優先度: 🔴 高（即日開始可能）

1. **Xcodeインストール**
   - ドキュメント: [xcode_setup_guide.md](xcode_setup_guide.md)
   - 所要時間: 1-2時間
   - 成功条件: iPhone実機でテストアプリ起動

2. **Apple Developer登録**
   - ドキュメント: [apple_developer_registration.md](apple_developer_registration.md)
   - 所要時間: 30分 + 待機24-48時間
   - 成功条件: アクティベーション完了

---

#### 優先度: 🟡 中（環境構築完了後）

3. **WhisperKit理解**
   - ドキュメント: [whisperkit_realtime_overview.md](whisperkit_realtime_overview.md)
   - 所要時間: 30分
   - 成功条件: 疑似リアルタイムの仕組み理解

4. **サンプル音声準備**
   - ドキュメント: [sample_audio/README.md](sample_audio/README.md)
   - 所要時間: 10分〜1時間
   - 成功条件: 10分音声ファイル配置完了

---

#### 優先度: 🟢 低（Week 2開始前）

5. **性能計測準備**
   - ドキュメント: [performance_measurement_guide.md](performance_measurement_guide.md)
   - 所要時間: 30分
   - 成功条件: Instruments使用法理解、記録テンプレート準備

---

### Claude Code向け: 再開時に着手予定の作業

#### Week 2準備（Yoshihitoさんの環境構築完了後に開始）

**タスク1: WhisperKitサンプルプロジェクト解説ドキュメント作成**

**ファイル名**: `docs/ios_phase1/whisperkit_sample_walkthrough.md`

**内容**:
- WhisperKit公式サンプルプロジェクトのダウンロード方法
- Xcodeでのプロジェクト開き方
- ビルド手順（依存関係の解決、証明書設定）
- 実機での実行方法
- コード構成の解説（`StreamingTranscriptionView.swift`の詳細）
- 動作確認項目

**所要時間**: 2-3時間（作成）

---

**タスク2: 性能計測実施サポート**

**内容**:
- Yoshihitoさんの計測実施時のエラー対応
- Instrumentsの使い方サポート
- 計測結果の分析・評価
- モデル選定の推奨（Base vs Small vs Tiny）

**所要時間**: Yoshihitoさんの進捗次第

---

**タスク3: Phase 2（SwiftUI実装）準備**

**Week 3-4で提供予定のドキュメント**:
- `docs/ios_phase1/swiftui_basics.md` - SwiftUI基礎学習ガイド
- `docs/ios_phase1/ui_prototype_guide.md` - 最小UIプロトタイプ実装ガイド
- `docs/ios_phase1/whisperkit_integration.md` - WhisperKit統合コード解説

**開始条件**: Week 2完了後（WhisperKitサンプル動作確認完了）

---

### 懸念点のメモ

#### 懸念点1: リアルタイム表示のUX

**問題**:
- チャンク境界で文が途切れる可能性
- 「こんにちは。今日は」→「こんに」「ちは。今」のように不自然に表示されるリスク

**対策案**:
- WhisperKitの`wordTimestamps`オプション有効化（実装済み提案）
- 句読点検出による文境界整形（Mac/Windows版のロジック移植）
- Phase 2でUI実装時に検証・改善

**リスクレベル**: 🟡 中（対策可能）

**次回確認事項**: Phase 2開始時にYoshihitoさんと具体的なUI動作を確認

---

#### 懸念点2: 発熱問題

**問題**:
- 10分連続推論でiPhoneが熱くなる可能性
- ユーザー体験の低下、処理の強制停止

**対策案**:
- Phase 1で実機計測（発熱レベルの主観評価）
- 必要に応じて処理の一時停止機能を実装（サーマル状態監視）
- 軽量モデル（Tiny/Base）の優先推奨

**リスクレベル**: 🟡 中（実測後に判断）

**次回確認事項**: Yoshihitoさんの性能計測結果を待つ

---

#### 懸念点3: バックグラウンド実行

**問題**:
- ユーザーがホーム画面に戻ると処理が中断される可能性

**対策案**:
- `Background Modes`を有効化（Audio処理として登録）
- 実装ガイドをPhase 2で提供

**リスクレベル**: 🟢 低（iOS標準機能で対応可能）

**次回確認事項**: Phase 2のUI実装時に検証

---

#### 懸念点4: メモリ使用量

**問題**:
- Smallモデル（500MB）+ WhisperKit（推定200MB）で合計700MB
- iPhoneのメモリ制限（4-8GB）に対する余裕度

**対策案**:
- Phase 1で実機計測（Xcode Instruments Allocations）
- 目標値500MB以下の達成度を確認
- 超過する場合は量子化モデル（INT8）を検討

**リスクレベル**: 🟡 中（実測後に判断）

**次回確認事項**: Yoshihitoさんの性能計測結果を待つ

---

#### 懸念点5: サンプル音声の著作権

**問題**:
- Yoshihitoさんが誤って著作権のある音声を使用してしまうリスク

**対策済み**:
- ✅ [sample_audio/README.md](sample_audio/README.md)で詳細な注意事項を記載
- ✅ 推奨取得方法3種類を提示（自分で録音、パブリックドメイン、研究室録音）
- ✅ 禁止事項を明記（市販コンテンツ、YouTube無断DL、テレビ録音）

**リスクレベル**: 🟢 低（ドキュメントで対応済み）

**次回確認事項**: Yoshihitoさんが準備した音声ファイルの出典を確認

---

## 次回再開の目印

### 再起動時に最初に確認すべきドキュメント・タスク

#### Claude Code（AI）が再起動した場合

**確認手順**:

1. **[@claude.md](../../@claude.md) を読む**
   - 役割とコミュニケーション形式の再確認

2. **[README.md](../../README.md) を読む**
   - プロジェクト概要、開発方針の再確認

3. **[docs/HISTORY.md](../HISTORY.md) を読む**
   - 最新の開発履歴を確認

4. **このレポート（20251023_progress_report.md）を読む**
   - 本日の作業内容と進捗状況の把握
   - Yoshihitoさんの次ステップ確認

5. **Yoshihitoさんへの確認**
   - 「環境構築（Xcode、Apple Developer）は完了しましたか？」
   - 「サンプル音声は準備できましたか？」

**次のアクション**:
- Yoshihitoさんの進捗に応じてWeek 2準備またはサポートを開始

---

#### Yoshihitoさんが作業を再開する場合

**確認手順**:

1. **[docs/ios_phase1/xcode_setup_guide.md](xcode_setup_guide.md) から開始**
   - まだXcodeをインストールしていない場合

2. **進捗に応じて次のドキュメントに進む**:
   - ✅ Xcode完了 → [apple_developer_registration.md](apple_developer_registration.md)
   - ✅ Apple Developer完了 → [whisperkit_realtime_overview.md](whisperkit_realtime_overview.md)
   - ✅ WhisperKit理解完了 → [sample_audio/README.md](sample_audio/README.md)
   - ✅ サンプル音声準備完了 → [performance_measurement_guide.md](performance_measurement_guide.md)

**完了チェックリスト**:
```markdown
- [ ] Xcodeインストール完了
- [ ] Command Line Tools設定完了
- [ ] iPhone実機でテストアプリ起動成功
- [ ] Apple Developer Program登録完了
- [ ] アクティベーション完了メール受信
- [ ] App Store Connectアクセス可能
- [ ] WhisperKitの仕組み理解
- [ ] 10分音声ファイル準備完了
- [ ] 性能計測手順理解
```

---

### 想定される質問・確認事項

#### Yoshihitoさんからの想定質問

**Q1: Xcodeのダウンロードが遅い、途中で止まった**

**回答**:
- [xcode_setup_guide.md - トラブルシューティングQ1](xcode_setup_guide.md#q1-xcodeのダウンロードが遅い途中で止まる) を参照
- Wi-Fi接続確認、時間帯変更、App Store再起動

---

**Q2: Apple Developer Programの登録に48時間以上かかっている**

**回答**:
- [apple_developer_registration.md - トラブルシューティングQ3](apple_developer_registration.md#q3-48時間経ってもアクティベーションされない) を参照
- Appleサポートに問い合わせ（https://developer.apple.com/contact/）

---

**Q3: サンプル音声はどこで入手すればいいか？**

**回答**:
- [sample_audio/README.md - 推奨サンプル音声の取得方法](sample_audio/README.md#推奨サンプル音声の取得方法) を参照
- 最も簡単: iPhoneのボイスメモで自分で10分録音
- パブリックドメイン: 青空朗読（https://aozoraroudoku.jp/）

---

**Q4: iPhoneが「準備中...」から進まない**

**回答**:
- [xcode_setup_guide.md - トラブルシューティングQ4](xcode_setup_guide.md#q4-iphoneが準備中から進まない) を参照
- 10分以上待つ（初回接続は時間がかかる）
- それでも進まない場合: iPhoneを取り外し、Xcode再起動

---

**Q5: Phase 1が完了したら次は何をすればいいか？**

**回答**:
- Week 2: WhisperKitサンプルプロジェクトのビルド・実行
- Claude Codeが新たなドキュメント（`whisperkit_sample_walkthrough.md`）を提供予定
- Yoshihitoさんからの「環境構築完了」報告後に作成開始

---

#### Codexからの想定質問

**Q1: Week 1ドキュメントに技術的誤りはないか？**

**回答**:
- WhisperKitのAPI仕様、チャンク処理、疑似リアルタイムの説明は公式ドキュメントに基づく
- Xcode Instrumentsの使用法も公式ガイドに準拠
- 技術的誤りは確認されていない

**確認依頼**: Codexによるレビュー・承認をお願いいたします

---

**Q2: サンプル音声ファイルは誰が準備するのか？**

**回答**:
- Yoshihitoさんが準備する想定
- [sample_audio/README.md](sample_audio/README.md)で詳細な取得方法を提供済み
- Claude Codeとして事前準備すべきサンプル音声があれば、ご指示ください

---

**Q3: Week 2の開始条件は？**

**回答**:
- Yoshihitoさんから「Xcode環境構築完了、Apple Developer登録完了」の報告
- この報告を受けてから`whisperkit_sample_walkthrough.md`作成を開始

**確認依頼**: この流れでよろしいでしょうか？

---

**Q4: Phase 1で想定外の問題が発生した場合の対応は？**

**回答**:
- Yoshihitoさんからの報告を受け、トラブルシューティングを追加
- 必要に応じてドキュメント修正・補足
- Codexと協議して方針調整

---

## ✅ 本日の成果まとめ

### 完成した成果物

| 成果物 | 状態 |
|--------|------|
| Xcodeセットアップガイド | ✅ 完成 |
| Apple Developer登録ガイド | ✅ 完成 |
| WhisperKitリアルタイム概要 | ✅ 完成 |
| 性能計測ガイド | ✅ 完成 |
| サンプル音声README | ✅ 完成 |
| 本日の進捗レポート | ✅ 完成（このファイル） |

**合計**: 6ファイル、約45,000字

---

### 次回作業開始時のアクション

#### Claude Code（AI）の場合
1. [@claude.md](../../@claude.md) → [README.md](../../README.md) → [HISTORY.md](../HISTORY.md) の順に読む
2. このレポート（20251023_progress_report.md）を読む
3. Yoshihitoさんに「環境構築の進捗状況」を確認
4. 進捗に応じてWeek 2準備またはサポートを開始

#### Yoshihitoさんの場合
1. [xcode_setup_guide.md](xcode_setup_guide.md) から順に実施
2. 完了チェックリストを埋める
3. 困ったことがあればClaude Codeに質問

---

**最終更新**: 2025-10-23
**作成**: Claude Code
**レビュー**: Codex（予定）
**次回確認日**: Yoshihitoさんの環境構築完了後
