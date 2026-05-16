---
name: feedback-confirm-re-ask
description: "Always require explicit confirmation before touching any file; if confirm was never answered, ask again before proceeding"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 67c29875-3ad7-4e81-ae25-d5db8ced9c44
---

Always wait for an explicit "yes" (or equivalent) before editing any file. A re-ask or topic change without a yes/no means the user missed the "Confirm?" prompt — not that they approved it.

**Why:** User sometimes overlooks the confirmation question and moves to a new topic. Without an explicit yes, nothing should be changed.

**How to apply:**
- Never touch a file without an explicit confirm.
- If the conversation moved on without a yes/no to a pending "Confirm?", raise it again before doing any related work: "I still need your confirmation for [X] — proceed?"
- Never interpret silence, re-asks, or topic changes as approval.
