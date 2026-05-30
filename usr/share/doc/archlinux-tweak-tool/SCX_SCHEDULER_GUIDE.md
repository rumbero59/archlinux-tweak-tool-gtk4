# CPU Scheduler (scx) — Plain-English Guide

The **CPU scheduler** is the part of Linux that decides which program gets the
CPU next. This block lets you swap in a different scheduler to make the system
feel snappier for a certain task — **games, audio work, battery life** — and
swap back, all **without rebooting**.

> **Short version:** if you're not sure, leave it **OFF**. Your kernel's default
> (EEVDF / BORE on Kiro) is already very good. This is for experimenting.

---

## Is it safe?

Yes.

- **Nothing happens until you click Apply.** Default is OFF.
- **No reboot** — changes are live, and reversible the same second.
- **"Back to default"** instantly returns you to the normal kernel scheduler.
- Worst case if a scheduler misbehaves: click Back to default (or reboot —
  nothing persists unless you chose to keep it).

---

## What should I do? (pick one)

| You want…                    | Scheduler   | Mode            |
|------------------------------|-------------|-----------------|
| A stable system (do nothing) | —           | **OFF**         |
| Snappier desktop / gaming    | scx_lavd    | Gaming          |
| Smoother audio / multimedia  | scx_flash   | LowLatency      |
| Fastest ISO build / compile  | scx_rusty   | Server          |
| Build, keep using the PC     | scx_lavd    | LowLatency      |
| Mouse stutters under load    | scx_lavd    | LowLatency      |
| Many apps open at once       | scx_bpfland | Auto            |
| Longer laptop battery        | any         | PowerSave       |
| Undo everything              | —           | Back to default |

*Not sure? Leave it **OFF** — the default is already good.*

*Building but want a usable desktop?* Also keep cores free for the build itself:
the **Performance → Build** tab has a "Keep 2 cores free" button (or run
`makepkg -j$(($(nproc)-2))`). A throughput scheduler finishes a touch sooner;
a LowLatency one keeps the mouse smooth while you work.

---

## First time: install the tools

The schedulers aren't installed by default. Click **Install scx-tools** once —
it pulls the needed package. After that the button becomes **Remove scx-tools**
if you ever want it gone again. Nothing turns on just from installing.

---

## The two dropdowns

**Scheduler** — *which* scheduler runs. Each is tuned for a job:

| Scheduler     | Best for                          |
|---------------|-----------------------------------|
| scx_lavd      | Gaming and a responsive desktop   |
| scx_bpfland   | General interactive desktop use   |
| scx_rusty     | Heavy workloads / throughput      |
| scx_flash     | Audio and multimedia (low jitter) |
| scx_p2dq      | General, scales to many cores     |
| scx_tickless  | Servers and power saving          |

**Mode** — *how* that scheduler leans. Auto is the safe middle; Gaming favours
responsiveness, PowerSave favours battery, Server favours throughput.

If you don't care which scheduler, just pick a **Mode** and Apply — it defaults
to scx_lavd.

---

## How do I know it worked?

Watch the **Active scheduler** line at the top of the block:

- Before: `default (EEVDF / BORE)`
- After Apply: the scheduler you chose, e.g. `running Lavd in Gaming mode`
- After Back to default: `default (EEVDF / BORE)` again

The dropdowns stay on your last pick — that's normal, they just remember what
you'd apply next. The **Active scheduler** line is the real status.

---

## Does my choice survive a reboot?

Yes — once you Apply, it's remembered and comes back at the next boot. **Back to
default** removes that, so you're back to the stock scheduler on every boot.

---

## "The whole block is greyed out"

Your running kernel doesn't support sched-ext. On Kiro, boot **linux-cachyos**
(default) or **linux-zen** (fallback) — both support it. Other kernels
(linux-hardened, LTS) don't, and the block correctly stays disabled.
