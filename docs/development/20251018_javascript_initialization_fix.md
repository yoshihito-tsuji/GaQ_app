# 2025-10-18: JavaScript初期化の根本的修正

**日付**: 2025-10-18
**担当**: Claude Code
**ステータス**: ⚠️ 実装完了・動作テスト中（一部問題解決）

---

## 📋 作業概要

Codexによる差分解析で指摘された**JavaScript初期化の致命的な設計ミス**を修正しました。

### 根本原因（Codexの分析）

1. **`window.__appInitialized`フラグが早すぎるタイミングで設定されていた**
   - `initializeApp()`の**冒頭**でフラグを立てていたため、イベントリスナー登録の途中で例外が発生すると、**フラグは立っているのにイベントリスナーは未登録**という状態になっていた
   - 再実行されないため、画面が永遠に無反応になる

2. **`pywebviewready`イベントが発火していない**
   - ログに `[JS] 📢 pywebviewready イベント検出` が出力されていない
   - つまり、`initializeApp()`自体が実行されていなかった可能性

3. **`DOMContentLoaded`のフォールバックが500ms遅延していた**
   - pywebview環境では即座に初期化すべきなのに、不要な遅延があった

---

## 🔧 実装した修正内容

### 修正1: `window.__appInitialized`を最後に設定

**変更前** ([main.py:496-503](../../release/mac/src/main.py#L496-L503)):
```javascript
function initializeApp(trigger) {
    if (window.__appInitialized) {
        return;
    }
    window.__appInitialized = true;  // ←ここで即座にフラグを立てていた
    window.__appInitialized_source = trigger || 'unknown';

    // ... 500行以上のイベントリスナー登録が続く
}
```

**変更後** ([main.py:496-1186](../../release/mac/src/main.py#L496-L1186)):
```javascript
function initializeApp(trigger) {
    if (window.__appInitialized) {
        return;
    }

    try {
        // すべてのDOM要素取得
        // すべてのイベントリスナー登録
        // ...

        // ★最後に成功フラグを立てる
        window.__appInitialized = true;
        window.__appInitialized_source = trigger || 'unknown';
        console.log('✅ initializeApp() 完了 - すべてのイベントリスナー設定完了');

    } catch (error) {
        console.error('❌ initializeApp() 失敗:', error);
        alert('アプリケーションの初期化に失敗しました...');
        // エラー時はフラグを立てない → 再試行可能
    }
}
```

**効果**:
- イベントリスナー登録が**成功した後に**のみフラグを立てる
- 例外発生時は再試行可能

---

### 修正2: ログ出力の大幅強化

**追加したログ**:

1. **JavaScript開始時**:
   ```javascript
   console.log('===== GaQ JavaScript starting =====');
   console.log('document.readyState:', document.readyState);
   console.log('window.pywebview:', !!window.pywebview);
   ```

2. **DOM要素取得時**:
   ```javascript
   console.log('📋 DOM要素の取得を開始...');
   console.log('✅ DOM要素取得完了:');
   console.log('  uploadArea:', !!uploadArea);
   console.log('  fileInput:', !!fileInput);
   console.log('  transcribeBtn:', !!transcribeBtn);
   ```

3. **イベントリスナー登録時**:
   ```javascript
   console.log('📝 イベントリスナーの登録を開始...');
   console.log('✅ uploadArea クリックイベント登録完了');
   console.log('✅ transcribeBtn clickイベント登録完了');
   console.log('✅ モデル管理ボタンのイベントリスナー設定完了');
   ```

4. **初期化トリガー時**:
   ```javascript
   console.log('🔍 safeInitialize() 呼び出し - source:', source);
   console.log('🔁 triggerInitializeApp():', source);
   console.log('🕐 タイムアウトチェック(2s) - __appInitialized:', window.__appInitialized);
   ```

---

### 修正3: DOMContentLoadedの即座実行

**変更前**:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    // pywebviewreadyが発火しなかった場合の保険として500ms待機後に初期化
    setTimeout(function() {
        safeInitialize('DOMContentLoaded (fallback)');
    }, 500);
});
```

**変更後**:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    console.log('📢 DOMContentLoaded イベント検出');
    safeInitialize('DOMContentLoaded');  // ← 即座に実行
});
```

**効果**:
- 不要な500ms遅延を削除
- より高速な初期化

---

### 修正4: タイムアウトフォールバックのログ強化

**変更前**:
```javascript
setTimeout(function() {
    if (!window.__appInitialized) {
        console.warn('⚠️ pywebviewready 未発火 - タイムアウトフォールバック(2s)');
        triggerInitializeApp('timeout-2s');
    }
}, 2000);
```

**変更後**:
```javascript
setTimeout(function() {
    console.log('🕐 タイムアウトチェック(2s) - __appInitialized:', window.__appInitialized);
    if (!window.__appInitialized) {
        console.warn('⚠️ 初期化未完了 - タイムアウトフォールバック(2s)で初期化実行');
        triggerInitializeApp('timeout-2s');
    } else {
        console.log('✅ 既に初期化済み - スキップ');
    }
}, 2000);
```

**効果**:
- タイムアウト時の状態を詳細に記録
- 初期化済みの場合もログを出力

---

## ✅ テスト結果

### pywebview環境（Mac版アプリ）

```bash
$ /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 src/main_app.py
```

**ログ出力**:
```
2025-10-18 13:18:44 - INFO - === GaQ Offline Transcriber v1.1.1 起動 ===
2025-10-18 13:18:49 - INFO - 🚀 FastAPIサーバー起動: http://127.0.0.1:8000
2025-10-18 13:18:50 - INFO - [JS] ✅ Console hook installed - JS logs will be forwarded to Python
2025-10-18 13:18:50 - INFO - ✅ コンソールログフック設定完了
```

**確認結果**:
- ✅ アプリは起動する
- ✅ コンソールフックは動作する
- ❌ **`console.log('===== GaQ JavaScript starting =====')`以降のログが出力されていない**

**原因**:
- コンソールフックが`window.events.loaded`イベントで注入されるため、HTML内の`<script>`タグ実行**後**に設定される
- つまり、`<script>`タグ内のログは、フックが設定される前に実行されている

---

## 🔍 残された問題

### 問題1: pywebviewready イベントが発火していない

**症状**:
- `[JS] 📢 pywebviewready イベント検出` がログに出力されない
- `initializeApp()`が実行されない可能性

**考察**:
1. `pywebviewready`イベント自体がpywebviewから発火していない
2. コンソールフックが設定される前にイベントが発火している
3. イベントリスナー登録自体が失敗している

**次回の対策**:
- `DOMContentLoaded`を優先して即座に初期化を試行
- タイムアウトフォールバックを1秒に短縮
- Safari Web Inspectorでデバッグ

---

### 問題2: コンソールログのタイミング問題

**症状**:
- `<script>`タグ内のログがPythonログに転送されていない

**原因**:
- `window.events.loaded`イベントが`<script>`実行後に発火
- コンソールフックの設定が遅すぎる

**次回の対策**:
- コンソールフックを`<script>`タグ内に直接埋め込む
- または、`window.events.loaded`ではなく、より早いタイミングでフック設定

---

## 📦 変更ファイル

- **[release/mac/src/main.py](../../release/mac/src/main.py)** - JavaScript初期化ロジック全面修正

---

## 📋 次回作業の推奨事項

### 最優先: pywebviewready問題の解決

1. **DOMContentLoadedを最優先にする**
   ```javascript
   // pywebviewreadyを待たず、DOMContentLoadedで即座に初期化
   if (document.readyState === 'loading') {
       document.addEventListener('DOMContentLoaded', function() {
           safeInitialize('DOMContentLoaded');
       });
   } else {
       // すでにDOM読み込み済み → 即座に初期化
       safeInitialize('DOM already loaded');
   }
   ```

2. **タイムアウトフォールバックを短縮**
   ```javascript
   // 1秒後に強制初期化
   setTimeout(function() {
       if (!window.__appInitialized) {
           triggerInitializeApp('timeout-1s');
       }
   }, 1000);
   ```

3. **Safari Web Inspectorでデバッグ**
   - DMGをマウント
   - Safari → 開発 → [マシン名] → GaQ Offline Transcriber
   - Consoleで`window.__appInitialized`を確認

---

## 🎯 まとめ

### 完了した修正

- ✅ `window.__appInitialized`フラグの設定タイミングを修正
- ✅ try-catch でエラーハンドリング追加
- ✅ ログ出力を大幅強化（50箇所以上追加）
- ✅ DOMContentLoadedの即座実行
- ✅ タイムアウトフォールバックのログ強化

### 未解決の問題

- ❌ `pywebviewready`イベントが発火していない
- ❌ コンソールログがPythonログに転送されていない（タイミング問題）

### 次回の作業

- 🔜 DOMContentLoadedを最優先にする
- 🔜 タイムアウトフォールバックを1秒に短縮
- 🔜 Safari Web Inspectorでデバッグ
- 🔜 DMGをビルドして実機テスト

---

**結論**: JavaScript初期化の設計ミスを修正し、ログ出力を大幅強化した。しかし、pywebview環境での`pywebviewready`イベント不発火問題は未解決。次回はDOMContentLoadedを最優先にして即座に初期化を試行する。
