---
name: No changes without confirmation
description: Never add, remove, or modify code without explicit user confirmation first
type: feedback
originSessionId: 3abf85be-09af-4673-b2a8-93f2d95639b2
---
Never make code changes without the user's explicit confirmation.

**Why:** Claude made several unilateral changes (added invented constants, removed functions, deleted GUI widgets, changed file structure) that broke working code and required a full git revert. The user was clear: ask first, act after confirmation.

**How to apply:** Before writing any Edit, Write, or destructive Bash command — state what you intend to change and why, then explicitly ask "Confirm?" and wait for the user to say yes. Describing the plan is not enough — the confirmation request must be explicit. This applies even when the fix seems obvious, even when the root cause is clear, and even when the change is a one-liner. No exceptions except reverting a change the user explicitly asked to undo. Reinforced 2026-05-13, 2026-05-16.
