# communication_log_template.md
## Purpose
This file provides a standardized format to record exchanges between Codex, Claude Code, and Yoshihito.  
All AI–AI or AI–human communications must follow this template to ensure transparency and reproducibility.

---

## Communication Entry Template

### Metadata
| Field | Description |
|--------|-------------|
| Date | YYYY-MM-DD HH:MM (JST) |
| Subject | Short description of topic |
| Related Files | (optional) filenames or modules affected |
| Decision Type | {Design / Implementation / Review / Issue / Note} |

---

### Message Content
From: [Codex / Claude Code / Yoshihito]
To: [Codex / Claude Code / Yoshihito]
Subject: [Short title]

[Main message body here, in Markdown or plain text]

### Discussion / Replies
From: [Responder]
To: [Original sender]
[Response content, including rationale, trade-offs, or confirmations]

---

### Decision Summary
- **Final Decision:** [concise summary]  
- **Reasoning:** [main rationale or supporting data]  
- **Confirmed by:** [Codex / Claude Code / Yoshihito]  
- **Next Action:** [task, assignee, deadline if applicable]

---

### Example Log
| Field | Example |
|--------|----------|
| Date | 2025-10-22 21:00 |
| Subject | Whisperモデル処理速度の改善 |
| Related Files | `main.py`, `requirements.txt` |
| Decision Type | Implementation |

From: Claude Code
To: Codex
Subject: Whisper処理速度の改善案

whisper-timestamped モジュールを導入し、速度改善を試みたいです。
互換性面に問題はありませんか？

From: Codex
To: Claude Code

承認します。requirements.txtに追記し、GPU環境での分岐を実装してください。

**Decision Summary:**  
採用。処理時間短縮を優先。Codexが設計修正を記録。  
**Confirmed by:** Codex, Yoshihitoさん  
**Next Action:** 実装・テスト報告を次回ミーティングで共有。

Usage Notes
	•	Store each log under /logs/YYYY/MM/DD/communication.md for traceability.
	•	One communication thread per topic.
	•	Append follow-up decisions chronologically.
	•	Avoid overwriting; use version control for historical preservation.

⸻

End of Template



