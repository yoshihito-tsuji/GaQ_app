# Xcode セットアップガイド

**対象**: iOS版GaQ Transcriber開発の環境構築
**作成日**: 2025-10-23
**担当**: Claude Code
**対象者**: Yoshihitoさん（初心者向け）

---

## 📋 目次

1. [動作環境](#動作環境)
2. [Xcodeインストール](#xcodeインストール)
3. [初回起動時の設定](#初回起動時の設定)
4. [iPhone実機デプロイ準備](#iphone実機デプロイ準備)
5. [トラブルシューティング](#トラブルシューティング)

---

## 動作環境

### 必要な環境

| 項目 | 要件 |
|------|------|
| **macOS** | macOS 13.5 (Ventura) 以降 |
| **空き容量** | **40GB以上推奨**（Xcode本体 + iOS Simulator） |
| **メモリ** | 8GB以上（16GB推奨） |
| **プロセッサ** | Intel または Apple Silicon (M1/M2/M3) |

### インストールするもの

- **Xcode 15.x** (最新安定版)
  - サイズ: 約7GB（ダウンロード時）
  - インストール後: 約15GB
  - iOS Simulator: 約5GB（iOS 17の場合）
  - **合計**: 約25GB

### 確認方法

macOSバージョンの確認:
```bash
sw_vers
```

**出力例**:
```
ProductName:		macOS
ProductVersion:		14.6.1
BuildVersion:		23G93
```

空き容量の確認:
```bash
df -h /
```

**出力例**:
```
Filesystem     Size   Used  Avail Capacity  Mounted on
/dev/disk3s1  466Gi  200Gi  226Gi    47%    /
                            ^^^^
                            この値が40GB以上あればOK
```

---

## Xcodeインストール

### 手順1: Mac App Storeを開く

1. **Launchpad**または**Spotlight**から「App Store」を起動
2. 右上の検索欄に「**Xcode**」と入力

![App Store検索](https://via.placeholder.com/600x400?text=App+Store+%E6%A4%9C%E7%B4%A2)

### 手順2: Xcodeをインストール

1. 検索結果から「**Xcode**」（Appleが提供）を選択
2. 「**入手**」または「**ダウンロード**」ボタンをクリック
3. Apple IDでサインイン（未サインインの場合）
4. ダウンロード＆インストール開始

**所要時間**:
- Wi-Fi速度により異なります（目安: 20分〜1時間）
- ダウンロード中は他の作業を進めても問題ありません

**注意事項**:
- ⚠️ ダウンロード中はMacをスリープさせないでください
- ⚠️ Wi-Fi接続が安定していることを確認してください

### 手順3: インストール完了の確認

1. **Launchpad**から「Xcode」アイコンを探す
2. アイコンをクリックして起動

**初回起動時の確認ダイアログ**:
```
追加コンポーネントをインストールしますか？
[インストール]
```
→ 「**インストール**」を選択してください

**所要時間**: 約5分

---

## 初回起動時の設定

### 手順1: ライセンス同意

初回起動時、ライセンス同意画面が表示されます。

```
Xcode and Apple SDKs Agreement
[同意する]
```

1. 内容を確認（英語）
2. 「**同意する**」をクリック
3. macOSのパスワード入力（管理者権限確認）

### 手順2: Command Line Toolsの選択

Xcodeが起動したら、以下の設定を確認します。

**操作手順**:
1. メニューバーから「**Xcode**」→「**Settings...**」（または`⌘,`）
2. 「**Locations**」タブをクリック
3. 「**Command Line Tools**」のドロップダウンを確認

**正しい設定**:
```
Command Line Tools: Xcode 15.x (15Axxxx)
```

**もし「None」の場合**:
1. ドロップダウンをクリック
2. 最新のXcodeバージョンを選択

![Command Line Tools設定](https://via.placeholder.com/600x400?text=Command+Line+Tools+%E8%A8%AD%E5%AE%9A)

### 手順3: iOS Simulatorの確認

iPhoneの実機がない場合でも、Simulator（シミュレータ）で動作確認ができます。

**操作手順**:
1. Xcodeのメニューバーから「**Window**」→「**Devices and Simulators**」
2. 「**Simulators**」タブをクリック
3. 以下のデバイスがあることを確認:
   - iPhone 15 Pro (iOS 17.x)
   - iPhone 14 (iOS 17.x)

**もし何も表示されない場合**:
1. 左下の「**+**」ボタンをクリック
2. 「**Device Type**」から「iPhone 15 Pro」を選択
3. 「**Create**」をクリック

**注意**:
- ⚠️ Simulatorは音声入力に対応していません
- ⚠️ 文字起こしアプリのテストには**実機が必須**です
- ✅ UI確認やビルドテストには使用できます

---

## iPhone実機デプロイ準備

### 必要なもの

- ✅ iPhone（iOS 15以降推奨）
- ✅ Lightning/USB-Cケーブル（Mac ⇔ iPhone接続用）
- ✅ Apple ID（無料でOK、Apple Developer Programは後で登録）

### 手順1: iPhoneをMacに接続

1. **Lightningケーブル**（またはUSB-C）でiPhoneとMacを接続
2. iPhone側で「**このコンピュータを信頼しますか?**」ダイアログが表示される
3. 「**信頼**」をタップ
4. iPhoneのパスコードを入力

![iPhone信頼設定](https://via.placeholder.com/600x400?text=iPhone+%E4%BF%A1%E9%A0%BC%E8%A8%AD%E5%AE%9A)

### 手順2: Xcodeでデバイス登録

**操作手順**:
1. Xcodeのメニューバーから「**Window**」→「**Devices and Simulators**」
2. 「**Devices**」タブをクリック
3. 左側のリストに接続したiPhoneが表示されることを確認

**表示例**:
```
Devices
├─ Yoshihito's iPhone (15.6)
   ├─ Identifier: 00008xxx-xxxxx
   ├─ Model: iPhone 14
   └─ Status: 準備完了
```

**もし「準備中...」と表示される場合**:
- 数分待ってください（シンボルファイルの準備中）
- 初回接続時は5-10分かかることがあります

### 手順3: 開発者モードの有効化（iOS 16以降）

iOS 16以降では、開発者モードを手動で有効化する必要があります。

**iPhone側の操作**:
1. 「**設定**」アプリを開く
2. 「**プライバシーとセキュリティ**」をタップ
3. 一番下にスクロールして「**デベロッパモード**」をタップ
4. スイッチをオンにする
5. 再起動を求められるので、「**再起動**」をタップ

**再起動後**:
1. 「デベロッパモードを有効にしますか?」ダイアログが表示される
2. 「**有効にする**」をタップ
3. iPhoneのパスコードを入力

![開発者モード](https://via.placeholder.com/600x400?text=%E9%96%8B%E7%99%BA%E8%80%85%E3%83%A2%E3%83%BC%E3%83%89)

### 手順4: デプロイテスト（簡易確認）

実際にiPhoneでアプリを実行できるか、テストしてみます。

**操作手順**:
1. Xcodeを起動
2. メニューバーから「**File**」→「**New**」→「**Project...**」
3. 「**iOS**」タブ → 「**App**」を選択 → 「**Next**」
4. 以下を入力:
   - **Product Name**: `TestApp`
   - **Team**: （まだ設定不要、後で設定します）
   - **Organization Identifier**: `com.yourname`（任意）
   - **Interface**: `SwiftUI`
   - **Language**: `Swift`
5. 「**Next**」→ 保存先を選択 → 「**Create**」

**ビルドターゲットの選択**:
1. Xcodeウィンドウ上部の「**デバイス選択**」ドロップダウンをクリック
2. 接続したiPhoneを選択（例: `Yoshihito's iPhone`）

**ビルド＆実行**:
1. `⌘R`（または再生ボタン▶️）を押す
2. **初回のみ**: 署名エラーが表示される場合があります

**署名エラーの対処**:
```
Signing for "TestApp" requires a development team.
Select a development team in the Signing & Capabilities editor.
```

**解決方法**:
1. プロジェクトナビゲータで「**TestApp**」（青いアイコン）を選択
2. 「**Signing & Capabilities**」タブをクリック
3. 「**Team**」ドロップダウンから**自分のApple ID**を選択
   - まだ追加していない場合は「**Add Account...**」から追加

**再度ビルド**:
1. `⌘R`を押す
2. ビルドが成功し、iPhoneにアプリがインストールされます

**iPhone側の操作**（初回のみ）:
1. アプリを起動しようとすると「**信頼されていない開発元**」エラーが表示される
2. 「**設定**」→「**一般**」→「**VPNとデバイス管理**」
3. 「**デベロッパApp**」セクションで自分のApple IDをタップ
4. 「**信頼**」をタップ

**成功確認**:
- iPhoneのホーム画面に「TestApp」アイコンが表示される
- アプリを起動すると「Hello, world!」と表示される

✅ **ここまで完了すれば、実機デプロイ準備は完了です！**

---

## トラブルシューティング

### Q1: Xcodeのダウンロードが遅い・途中で止まる

**原因**: Wi-Fi接続が不安定、またはAppleサーバーの混雑

**対処方法**:
1. Wi-Fi接続を確認（有線LANがあれば切り替え）
2. 時間帯を変更（深夜・早朝は比較的空いています）
3. ダウンロードが止まった場合:
   - App Storeを終了
   - Macを再起動
   - App Storeから再度「ダウンロード」を開始（中断したところから再開されます）

---

### Q2: 「ディスク容量不足」エラーが表示される

**原因**: 空き容量が40GB未満

**対処方法**:
1. 不要なファイルを削除
2. 「ストレージ管理」で容量確保:
   - **Appleメニュー** → 「**このMacについて**」→「**ストレージ**」→「**管理...**」
   - 「書類」「ダウンロード」「ゴミ箱」を確認
3. 外付けSSDへの移動も検討

---

### Q3: Command Line Toolsが「None」から変更できない

**原因**: Xcodeのインストールが未完了、または破損

**対処方法**:
1. Xcodeを完全に終了
2. ターミナルを開く
3. 以下のコマンドを実行:
   ```bash
   sudo xcode-select --install
   ```
4. パスワードを入力
5. インストール完了後、Xcodeを再起動

---

### Q4: iPhoneが「準備中...」から進まない

**原因**: シンボルファイルの準備に時間がかかっている

**対処方法**:
1. **10分以上待つ**（初回接続時は時間がかかります）
2. それでも進まない場合:
   - iPhoneをMacから取り外す
   - Xcodeを再起動
   - 再度iPhoneを接続

---

### Q5: 「信頼されていない開発元」エラーが消えない

**原因**: iPhoneの設定でデベロッパプロファイルを信頼していない

**対処方法**:
1. iPhone「**設定**」→「**一般**」→「**VPNとデバイス管理**」
2. 「**デベロッパApp**」セクションを確認
3. 自分のApple IDが表示されていることを確認
4. タップして「**信頼**」を選択
5. 確認ダイアログで再度「**信頼**」をタップ

---

## ✅ セットアップ完了チェックリスト

以下がすべて✅になれば、セットアップ完了です！

- [ ] Xcodeがインストールされている（バージョン15.x）
- [ ] Command Line Toolsが設定されている
- [ ] iOS Simulatorが利用可能
- [ ] iPhoneがMacに接続され、「準備完了」状態
- [ ] 開発者モードが有効化されている（iOS 16以降）
- [ ] テストアプリがiPhone実機で起動できる

---

## 📚 次のステップ

セットアップ完了後は、以下のドキュメントに進んでください：

1. **[Apple Developer登録ガイド](apple_developer_registration.md)** - TestFlight配布に必要
2. **[WhisperKit概要](whisperkit_realtime_overview.md)** - 文字起こしエンジンの理解
3. **[性能計測ガイド](performance_measurement_guide.md)** - 10分音声のテスト方法

---

**最終更新**: 2025-10-23
**作成**: Claude Code
**レビュー**: Codex（予定）
