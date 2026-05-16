---
name: systemd-boot entry paths — Kiro vs other systems
description: Kiro uses /boot/efi/loader/entries; other systems use /boot/loader/entries or /efi or /EFI variants — always scan all paths
type: project
originSessionId: b78d56e9-f049-42fb-9d83-603ba9d30ce1
---
When scanning for systemd-boot loader entries, always check ALL of these directories (collect .conf files from every path that exists):

```
/boot/loader/entries        # standard Arch
/boot/efi/loader/entries    # Kiro
/boot/EFI/loader/entries    # some UEFI setups
/efi/loader/entries         # alternate ESP mount
/EFI/loader/entries         # rare, bare EFI partition
```

Detection of systemd-boot (loader.conf presence):
```
/boot/loader/loader.conf
/boot/efi/loader/loader.conf
/boot/EFI/loader/loader.conf
/efi/loader/loader.conf
/EFI/loader/loader.conf
```

**Why:** Kiro mounts the ESP at /boot/efi rather than /boot, so the standard /boot/loader path does not exist on Kiro. Scanning all variants means the same code works across all supported distros without special-casing.

**How to apply:** Any function that reads or writes systemd-boot entries must iterate the full list and act on every path that exists — never hardcode a single path.
