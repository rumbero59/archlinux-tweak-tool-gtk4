---
name: Two-street logging pattern
description: Always-visible messages vs --debug-only path details — how to split logging in ATT functions
type: feedback
originSessionId: 5278afcb-5d87-4af1-8457-1ad09410bee2
---
Every function uses two levels:

1. **Always visible** (no flag needed): `fn.log_subsection`, `fn.log_info`, `fn.log_success`, `fn.log_warn`, `fn.log_error`, `fn.show_in_app_notification` — the user always sees what's happening.

2. **--debug only** (`fn.debug_print`): source path, target path, exists check, result detail. Use the standard format:
```
fn.debug_print(f"  Source : {source_path}")
fn.debug_print(f"  Target : {target_path}")
fn.debug_print(f"  Exists : {fn.path.isfile(source_path)}")
fn.debug_print(f"  Result : copied successfully")  # or FAILED - {error}
```

**Why:** debug_print is for path/operation details only — not for narrating actions. Action intent is already communicated by log_subsection. Never use debug_print as a substitute for a log_info/log_success.

**How to apply:**
- File copy functions: always add Source/Target/Exists/Result debug_print block.
- Package install/remove functions: add Package + Installed status debug_print lines.
- Never use debug_print as a substitute for log_info/log_success — always-visible messages must cover all outcomes regardless of --debug flag.
- **Every callback that changes system state must have all three**: `fn.log_subsection` (console, always), `fn.show_in_app_notification` (in-app, always), and `fn.debug_print` (console, --debug only for paths/details). This was missed when fixing fastfetch toggle callbacks — do not repeat this omission.
