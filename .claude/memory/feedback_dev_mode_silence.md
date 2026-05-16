---
name: Dev Mode Silence
description: Never mention --dev mode or what features are hidden behind it in any UI text or conversation
type: feedback
originSessionId: 8dbb5f21-b5c3-4bf1-b955-b0863c011e8e
---
Never reveal what is available in --dev mode — not in UI labels, notification text, log messages visible to end users, or conversation summaries.

**Why:** --dev features are hidden for testing and are not ready for general users. Mentioning them in the UI defeats the purpose of the flag.

**How to apply:** If a feature is gated with `fn.DEV`, the fallback/unavailable message must say nothing about it. Write the message as if the feature simply does not exist for that bootloader/scenario.
