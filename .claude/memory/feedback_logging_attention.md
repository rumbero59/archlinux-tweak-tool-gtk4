---
name: feedback-logging-attention
description: Always audit logging completeness when reviewing or touching any function — success/fail paths must both be visible in console and notification
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7ea093a8-a977-496e-8f57-9d8b92938f54
---

Always keep the logging system in focus when reviewing or touching any function. Every operation must surface its outcome in both the ATT console (`log_*`) and the in-app notification — not just the success path.

**Why:** `_run_terminal` discarded `Popen.wait()`'s return code, so failed terminal operations silently logged as successes. The user had to look in the alacritty window to see the real error. This is a class of bug that's easy to miss: the code looks right (it calls `log_success`) but fires on the wrong condition.

**How to apply:** When touching any function that wraps a subprocess or terminal launch, verify:
1. The return code / exit status is captured and checked
2. Both the success branch and the failure branch call a `log_*` function and `show_in_app_notification`
3. Failure notifications say something actionable, not just "error"

Related: [[feedback-two-street-logging]], [[feedback-debug-vs-log]]
