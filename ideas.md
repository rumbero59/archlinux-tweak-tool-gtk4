# ATT - Ideas for future features

## Quick wins (low effort, high value)

- **CPU Governor** — dropdown in Performance tab, reads `/sys/devices/system/cpu/`, install cpupower
- **Sysctl Tweaks** — vm.swappiness slider + common gaming/desktop tweaks written to `/etc/sysctl.d/`
- **Flatpak** — install flatpak, add Flathub, update/cleanup buttons in Packages tab
- **Makepkg optimization** — `-march=native`, `MAKEFLAGS=-j$(nproc)`, build dir in tmpfs — in Maintenance tab

## Performance tab additions

- **earlyoom** (`earlyoom`) — prevents system freezes under memory pressure by killing OOM processes early; simple install/enable/disable service, same pattern as irqbalance
- **preload** (`preload`) — adaptive readahead daemon that prefetches frequently used binaries into memory; same install/enable/disable pattern
- **profile-sync-daemon** (`profile-sync-daemon`) — symlinks browser profiles to tmpfs to reduce disk I/O
- **IO scheduler** — dropdown to set the I/O scheduler (bfq, mq-deadline, kyber, none) per block device; useful for HDD vs NVMe

## New tabs worth adding

- **Kernel Manager** — biggest gap; install/remove kernels + headers, warn before removing running kernel
- **Gaming Stack** — Steam, Lutris, MangoHud, vkbasalt, vm.max_map_count tweak; could live in a dedicated Gaming tab
- **Firewall** — ufw install/enable/disable with presets (already detects firewalld in services)
- **System Info** — read-only hardware overview using inxi/lscpu/lspci; hw-probe already exists

## Systemd services viewer

A scrollable list of all enabled/active services with enable/disable toggles and start/stop buttons.
Similar to `systemd-manager` or KDE's systemd KCM.
Could live as a sub-tab in Services or its own tab.

## Already implemented this session

- Ananicy CPP + cachyos-ananicy-rules-git (Performance)
- GameMode (Performance)
- Tuned + tuned-ppd combined enable/disable (Performance)
- Swapfile size display + btrfs detection (Performance)
- AUR Helper — yay-git / paru-git with chaotic-aur detection (Pacman)
