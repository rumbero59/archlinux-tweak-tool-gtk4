---
name: Always Communicate Without --debug
description: User-facing actions must use log_success/log_info, not debug_print, so output shows without --debug
type: feedback
originSessionId: 51fded40-8f3b-41b1-bbd6-338701f8b4cb
---
User-facing actions (install, remove, apply, change) must communicate via `log_success`, `log_info`, or `log_warn` — never just `debug_print`. `debug_print` is invisible without `--debug` and must not be the only console output for an action the user triggered.

**Why:** Without `--debug`, the user has no console feedback. Silent actions violate the "Dual Logging" and "User Communication" objectives.

**How to apply:** Every user-triggered action needs two layers:
1. `log_success` / `log_info` + `show_in_app_notification` — always visible, communicates the outcome
2. `debug_print` lines — visible only with `--debug`, show command/user/path/result detail (source, target, exists, result pattern)

Never use `debug_print` as the only console output for a user action. Never add a notification without a matching console log.
