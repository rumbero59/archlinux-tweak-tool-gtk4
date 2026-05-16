---
name: Guard Remove Buttons With Package Check
description: Always check package is installed before launching terminal for removal; show message+notification instead of opening Alacritty
type: feedback
originSessionId: 51fded40-8f3b-41b1-bbd6-338701f8b4cb
---
Every remove button must call `fn.check_package_installed("package-name")` before launching the pacman removal terminal. If the package is not installed, show `fn.log_info(...)` + `fn.show_in_app_notification(...)` and return — no Alacritty window.

**Why:** pacman exits with "error: target not found" and the terminal shows a confusing error screen. Silent guard is much cleaner UX.

**How to apply:**
```python
def on_remove_foo_clicked(self, widget):
    if not fn.check_package_installed("foo"):
        fn.log_info("foo is not installed")
        fn.GLib.idle_add(fn.show_in_app_notification, self, "foo is not installed")
        return
    fn.log_subsection("Removing foo...")
    process = fn.launch_pacman_remove_in_terminal("foo")
    ...
```
Apply to every remove button in every tab — not just shell.
