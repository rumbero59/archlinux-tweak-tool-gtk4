---
name: Install/Uninstall Pattern — Alacritty Terminal
description: ALL install and uninstall operations must use alacritty terminal with visible commands, daemon thread, and in-function logging
type: feedback
originSessionId: 284296e9-1f36-4198-8ed9-5d8649d32e29
---
Every install and uninstall function in ATT must follow this pattern. No exceptions.

**Why:** Transparency is a core principle. The user must always see exactly what is happening to their system — every package operation, every systemctl command — in the terminal window.

**How to apply:** Any time an install or uninstall function is written or reviewed, enforce this structure:

```python
def install_something(self):
    import shutil
    if not shutil.which("alacritty"):
        log_info("alacritty not found, installing...")
        proc = subprocess.run(
            ["pacman", "-S", "--noconfirm", "--needed", "alacritty"],
            capture_output=True, text=True
        )
        if proc.returncode != 0:
            log_error(f"Failed to install alacritty: {proc.stderr}")
            return

    log_subsection("Install Something")
    script = """
pacman -S --noconfirm --needed some-package
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Package installed'
    echo ''
    echo 'Enabling service...'
    systemctl enable something.service --now
    echo '✓ Service enabled'
else
    echo '✗ Package installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""

    def _launch():
        try:
            subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
            GLib.idle_add(show_in_app_notification, self, "Installing something...")
        except Exception as error:
            GLib.idle_add(log_error, f"Failed to install something: {error}")

    threading.Thread(target=_launch, daemon=True).start()
```

**Rules:**
- `log_subsection` lives INSIDE the function, not in the callback
- All commands (pacman, systemctl, cp, mkdir) run INSIDE the alacritty script — never silently
- `Popen` always in a daemon thread — never block the GTK main loop
- Notification via `GLib.idle_add(show_in_app_notification, ...)` from inside the thread
- Callback in services.py just calls the function and handles exceptions — no duplicate logging
- For uninstall: if packages can't be removed due to dependencies, show a note in the terminal with the manual command — never fail silently
- Never use `subprocess.call()` for these operations — always `Popen` in daemon thread
