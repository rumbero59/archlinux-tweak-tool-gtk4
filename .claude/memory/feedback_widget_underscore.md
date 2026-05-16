---
name: GTK Callback Parameter — _widget Not widget
description: All GTK signal callback parameters that are not used must be prefixed with underscore
type: feedback
originSessionId: 51fded40-8f3b-41b1-bbd6-338701f8b4cb
---
GTK4 signal callbacks receive a widget/sender as their second argument. When it is not used in the function body, name it `_widget` not `widget`. Same rule applies to other unused GTK signal params (`_active`, `_x`, `_y`, etc.).

**Why:** The IDE (Pylance/pyright) flags unused parameters as hints. Using `_` prefix is the Python convention for intentionally unused parameters and silences the warning cleanly.

**How to apply:**
- Every callback with an unused sender: `def on_foo(self, _widget):`
- Multi-arg signals with unused params: `def on_bar(self, _widget, _active):`
- This pattern appears project-wide across all `*.py` and `*_gui.py` modules — when touching a file, rename any bare `widget` in signatures that aren't accessed.
- Use `sed -i '/^def /s/, widget)/, _widget)/g; /^def /s/, widget,/, _widget,/g' file.py` to batch-rename a whole file.
