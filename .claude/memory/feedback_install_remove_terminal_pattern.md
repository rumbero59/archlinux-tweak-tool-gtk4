---
name: Install/Remove Terminal Pattern with systemctl
description: ATT template for packages that have services — install+enable in one terminal, disable+remove in one terminal
type: feedback
originSessionId: 62661336-b8e4-485d-b9fa-3beac9a52295
---
When a package has a systemd service, ALL install and remove operations follow this two-part pattern in a single alacritty terminal:

**Install template:**
```bash
pacman -S --noconfirm --needed <package>
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo '✓ Installation successful'
    echo 'Enabling <service>...'
    systemctl enable --now <service> && echo '✓ enabled' || echo '✗ Failed'
else
    echo '✗ Installation failed'
fi
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
```

**Remove template:**
```bash
echo 'Disabling <service>...'
systemctl disable --now <service> && echo '✓ disabled' || echo '✗ Failed'
echo 'Removing packages...'
pacman -R --noconfirm <package>
RESULT=$?
if [ $RESULT -eq 0 ]; then echo '✓ Removal successful'; else echo '✗ Removal failed'; fi
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
```

**Why:** Transparency is a core ATT principle — user must see every action taken on their system in the terminal window. Splitting into two terminals is wrong; everything goes in one window.

**How to apply:** Any time a new install/remove button is added for a package with a service (irqbalance, ananicy, gamemode, tuned, etc.), use this combined single-terminal pattern instead of silent `fn.enable_service`/`fn.disable_service` + separate `fn.install_package`/`fn.remove_package` calls.
