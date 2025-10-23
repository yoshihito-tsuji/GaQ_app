# Apple Developer Program 登録ガイド

**対象**: iOS版GaQ TranscriberのTestFlight配布準備
**作成日**: 2025-10-23
**担当**: Claude Code
**対象者**: Yoshihitoさん（初心者向け）

---

## 📋 目次

1. [Apple Developer Programとは](#apple-developer-programとは)
2. [登録前の準備](#登録前の準備)
3. [登録手順](#登録手順)
4. [アクティベーションまでのタイムライン](#アクティベーションまでのタイムライン)
5. [App Store Connectの初期設定](#app-store-connectの初期設定)
6. [トラブルシューティング](#トラブルシューティング)

---

## Apple Developer Programとは

### 概要

**Apple Developer Program**（アップル デベロッパー プログラム）は、iOSアプリを実機でテスト・配布するために必要な**有料会員制度**です。

### 主な機能

| 機能 | 説明 |
|------|------|
| **TestFlight配布** | ベータテスター（最大10,000名）にアプリを配布 |
| **App Store配布** | 正式リリース（一般公開） |
| **証明書管理** | コード署名証明書の発行 |
| **Push通知** | APNs（Apple Push Notification service）の利用 |
| **開発者サポート** | 技術サポートフォーラムへのアクセス |

### 費用

- **年間費用**: ¥12,980（税込）
- **支払方法**: クレジットカード（Visa、Mastercard、JCB、American Express）
- **自動更新**: 毎年自動的に更新（解約も可能）

### 無料アカウントとの違い

| 項目 | 無料アカウント | Apple Developer Program |
|------|----------------|-------------------------|
| Xcode使用 | ✅ 可能 | ✅ 可能 |
| Simulator使用 | ✅ 可能 | ✅ 可能 |
| 実機デバッグ | ✅ 可能（7日間制限） | ✅ 可能（無制限） |
| TestFlight配布 | ❌ 不可 | ✅ 可能 |
| App Store配布 | ❌ 不可 | ✅ 可能 |

**注意**:
- 無料アカウントでも実機デバッグは可能ですが、**7日間ごとに再インストール**が必要
- TestFlight配布には**Apple Developer Programへの登録が必須**

---

## 登録前の準備

### 必要なもの

#### 1. Apple ID
- ✅ 既存のApple IDを使用可能（新規作成も可）
- ✅ **2ファクタ認証（2FA）**が有効化されていること
  - 未設定の場合は[こちら](https://support.apple.com/ja-jp/HT204915)から設定

#### 2. クレジットカード
- ✅ Visa、Mastercard、JCB、American Express
- ✅ デビットカードも一部対応（発行会社に要確認）

#### 3. 身分証明情報
- ✅ 氏名（ローマ字表記）
- ✅ 住所（英語表記）
- ✅ 電話番号

**住所の英語表記例**:
```
日本語: 〒123-4567 東京都渋谷区桜丘町1-2-3 ABCマンション101
英語: 101 ABC Mansion, 1-2-3 Sakuragaoka-cho, Shibuya-ku, Tokyo 123-4567, Japan
```

**住所変換ツール**（参考）:
- [JuDress](http://judress.tsukuenoue.com/) - 日本語住所を英語に変換

#### 4. 組織の場合（個人の場合は不要）
- ✅ D-U-N-S Number（企業識別番号）
- ✅ 法人登記書類

**GaQ Transcriber の場合**:
- Yoshihitoさんが**個人**として登録する想定
- 組織登録は不要

---

## 登録手順

### 手順1: Apple Developer Programページにアクセス

1. ブラウザで以下のURLを開く:
   - https://developer.apple.com/programs/
2. 右上の「**Enroll**」（登録）ボタンをクリック

![Apple Developer Programページ](https://via.placeholder.com/600x400?text=Apple+Developer+Program)

### 手順2: Apple IDでサインイン

1. 「**Sign in with your Apple ID to get started**」と表示される
2. Apple IDとパスワードを入力
3. 2ファクタ認証コードを入力（SMSまたは他のデバイスに送信される）

### 手順3: 個人情報の入力

**Entity Type（登録種別）の選択**:
```
○ Individual / Sole Proprietor / Single Person Business
  （個人／個人事業主／個人経営）

○ Organization（Company / Educational Institution）
  （組織／企業／教育機関）
```

→ **「Individual」を選択**

**個人情報の入力**:
| 項目 | 入力内容 |
|------|----------|
| **Legal Name** | 氏名（ローマ字、パスポート表記に合わせる） |
| **Country/Region** | Japan |
| **Address** | 住所（英語表記） |
| **City** | 市区町村（例: Shibuya-ku） |
| **State/Province** | 都道府県（例: Tokyo） |
| **Postal Code** | 郵便番号（例: 123-4567） |
| **Phone Number** | 電話番号（+81-90-1234-5678形式） |

**注意事項**:
- ⚠️ 氏名は**パスポートまたは公的書類と一致**させてください
- ⚠️ 後から変更する場合、Appleのサポートに連絡が必要

### 手順4: 利用規約の同意

1. 「**Apple Developer Program License Agreement**」を確認
2. 内容を読み、「**Agree**」にチェック
3. 「**Continue**」をクリック

### 手順5: 購入手続き

**支払情報の入力**:
| 項目 | 入力内容 |
|------|----------|
| **Payment Method** | Credit Card |
| **Card Number** | カード番号（16桁） |
| **Expiration Date** | 有効期限（MM/YY） |
| **Security Code** | セキュリティコード（3桁または4桁） |
| **Billing Address** | 請求先住所（カード登録住所と一致） |

**金額の確認**:
```
Apple Developer Program
Annual Membership          ¥12,980
Tax                        ¥0（非課税）
────────────────────────────────
Total                      ¥12,980
```

**注意**:
- ⚠️ 初年度から自動更新されます
- ⚠️ 解約する場合は、更新日の24時間前までに手続きが必要

### 手順6: 購入完了

1. 「**Purchase**」ボタンをクリック
2. クレジットカード決済が実行される
3. 「**Thank you for your purchase**」と表示される
4. 登録したメールアドレスに確認メールが届く

**確認メール（例）**:
```
件名: Apple Developer Program - Enrollment Confirmation

Thank you for enrolling in the Apple Developer Program.

Your enrollment is currently being processed.
You will receive another email within 24-48 hours when your enrollment is complete.
```

---

## アクティベーションまでのタイムライン

### 標準的な流れ

| タイミング | 内容 |
|------------|------|
| **即時** | 購入完了メール受信 |
| **数分後** | Apple IDに「Developer」ロールが付与される |
| **24-48時間以内** | アクティベーション完了メール受信 |
| **完了後** | App Store Connect、証明書管理が利用可能 |

### 遅延する場合

**原因**:
- クレジットカード認証の確認中
- Apple側の手動審査が必要（稀）
- 祝日・週末を挟んだ場合

**対処方法**:
1. **48時間以内**: そのまま待つ
2. **48時間経過後**: Appleサポートに問い合わせ
   - https://developer.apple.com/contact/

**問い合わせ方法**:
1. 上記URLにアクセス
2. 「**Membership and Account**」を選択
3. 「**Enrollment**」を選択
4. 「**Request a Call**」または「**Email Us**」

---

## App Store Connectの初期設定

### App Store Connectとは

**App Store Connect**は、アプリの管理・配布を行うWebポータルです。

**主な機能**:
- TestFlightでのベータ版配布
- App Storeへの正式リリース
- アプリの分析データ確認
- ユーザーレビュー管理

### アクセス方法

1. ブラウザで以下のURLを開く:
   - https://appstoreconnect.apple.com/
2. Apple IDでサインイン
3. 2ファクタ認証コードを入力

### 初期設定項目

#### 1. 利用規約の同意（初回のみ）

初回アクセス時、以下の規約への同意が求められます:

- **Paid Applications Agreement**（有料アプリ配布用、無料アプリのみの場合は不要）
- **Free Applications Agreement**（無料アプリ配布用）

**GaQ Transcriberの場合**:
- ✅ 無料アプリなので「**Free Applications Agreement**」のみ同意

**手順**:
1. 「**Agreements, Tax, and Banking**」をクリック
2. 「**Free Applications**」の「**Request**」をクリック
3. 規約を確認し、「**Agree**」にチェック
4. 「**Submit**」をクリック

#### 2. チーム情報の確認

**App Store Connect**の「**Users and Access**」で、自分が「**Account Holder**」（アカウント所有者）になっていることを確認します。

**確認手順**:
1. 左メニューから「**Users and Access**」をクリック
2. 「**People**」タブで自分の名前を確認
3. 「**Role**」が「**Account Holder**」になっていればOK

#### 3. Appレコードの作成（まだ不要）

**重要**: Phase 1では**Appレコードを作成しません**。

**理由**:
- App IDやBundle Identifierが確定していない段階で作成すると、後で変更が困難
- Phase 2でアプリのプロトタイプが完成してから作成する方が効率的

**いつ作成するか**:
- **Phase 3（TestFlight配布準備）** の段階で作成します
- その時点で改めてガイドを提供します

**現時点でやること**:
- ✅ App Store Connectにアクセスできることを確認
- ✅ 「My Apps」ページが表示されることを確認
- ✅ それ以上は何もしない

---

## トラブルシューティング

### Q1: 2ファクタ認証が設定できない

**症状**: 「2ファクタ認証を有効にしてください」と表示される

**対処方法**:
1. iPhoneまたはMacで「**設定**」→「**Apple ID**」→「**パスワードとセキュリティ**」
2. 「**2ファクタ認証を有効にする**」をタップ
3. 指示に従って設定
4. 信頼できるデバイス（iPhone）を登録

**詳細**: [Apple公式ガイド](https://support.apple.com/ja-jp/HT204915)

---

### Q2: クレジットカードが拒否される

**症状**: 「お支払い方法が承認されませんでした」

**原因**:
- カード情報の入力ミス
- カード会社の海外決済制限
- カードの利用限度額超過

**対処方法**:
1. カード情報を再確認（番号、有効期限、セキュリティコード）
2. カード会社に連絡し、海外決済（Apple Inc.）を許可
3. 別のクレジットカードを試す

---

### Q3: 48時間経ってもアクティベーションされない

**症状**: 「Enrollment Pending」のまま変わらない

**対処方法**:
1. Apple Developer サポートに問い合わせ:
   - https://developer.apple.com/contact/
2. 「**Membership and Account**」→「**Enrollment**」を選択
3. 「**Request a Call**」で電話サポートを依頼（英語対応）
4. または「**Email Us**」で問い合わせ（日本語対応の場合あり）

**必要な情報**:
- Apple ID
- 登録時の氏名
- 購入日時

---

### Q4: App Store Connectにアクセスできない

**症状**: サインインしても「アクセス権限がありません」と表示される

**原因**: アクティベーションが未完了

**対処方法**:
1. アクティベーション完了メールが届いているか確認
2. Apple Developer Program会員ページにアクセス:
   - https://developer.apple.com/account/
3. 「**Membership**」ステータスが「**Active**」になっているか確認
4. まだ「Pending」の場合は、Q3の手順で問い合わせ

---

### Q5: 住所の英語表記が分からない

**対処方法**:
- JuDressツールを利用: http://judress.tsukuenoue.com/
- 郵便番号を入力すると自動変換されます

**手動変換の例**:
```
日本語: 東京都渋谷区桜丘町1-2-3
英語: 1-2-3 Sakuragaoka-cho, Shibuya-ku, Tokyo

日本語: 北海道函館市若松町12-34
英語: 12-34 Wakamatsu-cho, Hakodate-shi, Hokkaido
```

---

## ✅ 登録完了チェックリスト

以下がすべて✅になれば、登録完了です！

- [ ] Apple Developer Programに登録し、支払いが完了
- [ ] アクティベーション完了メールを受信
- [ ] App Store Connectにアクセス可能
- [ ] 「Free Applications Agreement」に同意済み
- [ ] 「My Apps」ページが表示される

---

## 📚 次のステップ

登録完了後は、以下のドキュメントに進んでください：

1. **[WhisperKit概要](whisperkit_realtime_overview.md)** - 文字起こしエンジンの理解
2. **[性能計測ガイド](performance_measurement_guide.md)** - 10分音声のテスト方法
3. **Phase 2開始準備** - SwiftUI学習とプロトタイプ実装

---

**最終更新**: 2025-10-23
**作成**: Claude Code
**レビュー**: Codex（予定）
