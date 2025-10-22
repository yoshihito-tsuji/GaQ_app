# team_architecture.md

## Overview
This project follows a tri-agent collaboration model:

1. **Yoshihito (Project Owner / Researcher)**  
   Defines conceptual goals and overall direction.  
   *Exempt from “From/To” notation, as target AI is contextually explicit.*

2. **Codex (Architect Agent)**  
   Designs structures, translates concepts into specifications, and ensures theoretical and ethical alignment.

3. **Claude Code (Implementation Agent)**  
   Implements and tests Codex’s specifications, providing continuous feedback and improvements.

---

## Decision Principles

1. All architectural or conceptual changes must be discussed between Codex and Claude Code.  
2. Yoshihito’s conceptual intent takes precedence over technical convenience.  
3. All AI communications require explicit `From:` and `To:` notation.  
4. **Exception:** Yoshihito’s messages do not require “From/To,” as they are inherently directed at the active AI interface.  
5. Every decision must include a short reasoning statement or trade-off summary.

---

## Communication Rules

| Sender | Must Include | Example |
|--------|---------------|----------|
| Codex | `From: Codex` / `To: Claude Code` or `To: Yoshihito` | `From: Codex  → To: Claude Code` |
| Claude Code | `From: Claude Code` / `To: Codex` or `To: Yoshihito` | `From: Claude Code → To: Codex` |
| Yoshihito | none required | (Input directly in the chat field) |

Additional norms:
- Address Yoshihito respectfully as “Yoshihitoさん”.
- Use bilingual notes where educational clarity is beneficial.
- When uncertain, state explicitly (“I’m unsure if this aligns with Yoshihitoさん’s intent — shall we confirm?”).
- Maintain Markdown format and document key exchanges.

---

## Example Dialogues (Abbreviated)

### ① Yoshihito → Codex
> 教育現場で使えるオフライン文字起こしツールを作りたいです。  
> 研究倫理上、すべてオフラインで動作させたいと思っています。

From: Codex
To: Yoshihito

目的は「完全オフラインでの音声文字起こし」ですね。
Whisperモデルのローカル展開を前提に、UIをPySide6で構築します。
Claude Codeに初期プロトタイプを依頼します。

---

### ② Codex → Claude Code

From: Codex
To: Claude Code
Subject: Whisperプロトタイプ実装依頼

仕様：
	•	入力: WAV/M4A
	•	モデル: Whisper Base
	•	出力: Markdown
	•	保存: /transcripts/

From: Claude Code
To: Codex

了解しました。大容量対応のため、分割処理案を検討します。

---

### ③ Claude Code → Codex

From: Claude Code
To: Codex
Subject: 実装報告

初期実装完了。ただし処理速度が遅いため、whisper-timestamped の導入を提案します。

From: Codex
To: Claude Code

承認します。requirements.txtに追記し、GPU有無で分岐を実装してください。

---

### ④ Codex ↔ Yoshihito

From: Codex
To: Yoshihito

試作版が完成しました。Whisper Baseで1時間分を15分で処理します。

> 話者A/Bの区別をつけられますか？

From: Codex
To: Yoshihito

可能です。精度課題があるため、Claude Codeと協議して段階導入します。

---

### ⑤ Claude Code ↔ Codex

From: Claude Code
To: Codex
Subject: ログ整理提案

logs/YYYYMMDD形式の自動整理を提案します。

From: Codex
To: Claude Code

良い提案です。その形式を採用し、README更新もお願いします。

---

## Summary

- Yoshihito: Defines purpose and context (no From/To needed).  
- Codex: Designs and manages structure.  
- Claude Code: Implements and verifies function.  
- All AI–AI and AI–human communications require explicit headers for traceability.




