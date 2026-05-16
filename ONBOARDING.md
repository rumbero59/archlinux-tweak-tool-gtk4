# Onboarding — ATT & the Claude Code Workflow

This file is for anyone who wants to contribute to ATT, fork it as the base for their own tool, or learn how this project is built and maintained using Claude Code as a long-term AI collaborator.

---

## What ATT Is

ArchLinux Tweak Tool (ATT) is a GTK4 Python application that lets users manage an Arch-based Linux system through a graphical interface — themes, packages, services, shell config, boot, display managers, and more. It targets all Arch-based distros (Kiro, Artix, CachyOS, Manjaro, Omarchy, PrismLinux, and others) while guarding against stepping on distro-specific territory.

- **60+ Python modules** across 24 active pages
- **Feature-based module pattern**: `feature.py` (logic) + `feature_gui.py` (GTK4 UI)
- **Central utilities** in `functions.py` — logging, subprocess, file I/O, GTK helpers
- **Single entry point**: `usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py`

---

## Key Files to Read First

Read these in order before touching any code:

| File | What it tells you |
| ---- | ----------------- |
| `CLAUDE.md` | Architecture, conventions, patterns, objectives — the full rulebook |
| `DISTRO_GUARDS.md` | Which distros get special treatment and why — never bypass a guard without reading this |
| `CHANGELOG.md` | What changed and when — fastest way to understand recent decisions |
| `DISTRO_TESTING.md` | Which distros have been verified working and at what version |
| `.claude/memory/MEMORY.md` | Index of accumulated AI-collaboration decisions (see below) |

---

## The AI Collaboration Workflow

This project is built with **Claude Code** (Anthropic's CLI) as a persistent collaborator. If you use Claude Code too, you get the full accumulated context immediately. If you don't, the same files are still useful as documentation.

### How it works

1. **`CLAUDE.md`** — checked into the repo root. Claude Code reads this automatically when you open the project. It contains the architecture, naming conventions, patterns to follow, and objectives. Think of it as the project's constitution.

2. **`.claude/memory/`** — 53 markdown files recording non-obvious decisions, lessons from bugs, established patterns, and things that were tried and rejected. These are the institutional knowledge that normally lives nowhere and gets lost. Claude Code loads these at the start of each session.

3. **Session workflow** — every session starts by reading `CLAUDE.md` + memory, then `CHANGELOG.md`. Every session ends by updating `CHANGELOG.md`, syncing memory to the repo, and committing. The goal: the next session starts with full context, zero re-explanation.

### Memory file types

| Type | Purpose | Examples |
| ---- | ------- | ------- |
| `feedback_*.md` | How to approach work — corrections and confirmed good choices | widget naming, logging pattern, callback convention |
| `project_*.md` | Ongoing project state, decisions, constraints | multi-distro scope, functions file design intent |
| `incident_*.md` | Bugs and near-misses worth remembering | orphan removal cascade bug |
| `reference_*.md` | Where to find things | reference copy location |

---

## Architecture in 60 Seconds

```
usr/share/archlinux-tweak-tool/
├── archlinux-tweak-tool.py   # Entry point — GTK app setup, lazy-loads everything else
├── functions.py               # Central utilities (logging, subprocess, file I/O, helpers)
├── gui.py                     # Assembles all pages into the sidebar stack
├── <feature>.py               # Business logic for one page
├── <feature>_gui.py           # GTK4 UI for that page
└── data/                      # Config files, scripts, distro-specific assets
```

**The cardinal rule:** never put business logic in `_gui.py` and never put GTK widgets in `.py`. Keep them strictly separated.

---

## Conventions That Matter

These are the ones that will burn you if you ignore them:

**GTK4 callbacks always take `_widget`:**
```python
def on_button_click(self, _widget):   # correct — unused param named _widget
    ...
```

**Ampersands in `set_markup()` must be escaped:**
```python
label.set_markup("Save &amp; Apply")  # correct
label.set_markup("Save & Apply")      # silently renders nothing
```

**Never launch alacritty with `subprocess.call()`:**
```python
# wrong — blocks the GUI
subprocess.call(["alacritty", "-e", "bash", "-c", script])

# correct — daemon thread keeps ATT responsive
threading.Thread(target=lambda: subprocess.Popen([...]), daemon=True).start()
```

**Logging — never `print()`:**
```python
fn.log_section("Major step")      # bold green header
fn.log_info("Informational")      # blue
fn.log_success("Done")            # green
fn.log_warn("Watch out")          # yellow
fn.log_error("Failed", lineno=X)  # red
fn.debug_print("Internal detail") # only with --debug flag
```

**Page vs Tab:**
- **Page** = top-level sidebar entry (Plymouth, Services, SDDM)
- **Tab** = sub-section within a page (Audio, Bluetooth, Printing inside Services)

---

## Distro Guards

ATT runs on many Arch-based distros and some pages must be hidden or behave differently per distro. All guards are documented in `DISTRO_GUARDS.md`.

The short version:
- **`fn.distr`** — canonical distro name, set once at import time in `functions.py`; never re-detect inline
- **Page visibility guards** — in `gui.py`, controlled by `_SDDM_HIDDEN_DISTROS` and service checks
- **Per-module guards** — distro-specific behaviour inside individual modules
- **Never remove a guard** without testing on that distro first

---

## Starting Your Own Project From This

If you want to build a similar tool for a different distro, desktop, or purpose:

1. **Keep `CLAUDE.md`** — edit the Project Overview and objectives to match your project; the patterns and conventions are worth keeping
2. **Keep `.claude/memory/`** — the feedback files (`feedback_*.md`) record GTK4 and Python patterns that apply to any GTK4 project; the project-specific files (`project_*.md`) you can delete or replace
3. **Keep the module pattern** — `feature.py` + `feature_gui.py` scales well; don't put everything in one file
4. **Keep `functions.py` as your utility hub** — centralising logging, subprocess, and file I/O means consistent output and easy debugging
5. **Start your own `DISTRO_GUARDS.md`** if you target multiple systems — knowing which guards exist and why is more valuable than the code itself

---

## Running ATT

```bash
# Requires root for system operations
sudo python3 usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py

# With debug output
sudo python3 usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py --debug

# With experimental UI visible
sudo python3 usr/share/archlinux-tweak-tool/archlinux-tweak-tool.py --dev
```

Or install via the nemesis repo and run `archlinux-tweak-tool` from your launcher.

---

## Development Checklist

Before opening a PR or committing work:

- [ ] `flake8 usr/share/archlinux-tweak-tool/<file>.py --max-line-length=120` passes clean
- [ ] Callbacks use `_widget` not `widget` for unused parameters
- [ ] No `print()` — only `fn.log_*` calls
- [ ] No `subprocess.call()` for terminal launches
- [ ] Ampersands escaped in all `set_markup()` calls
- [ ] New pages follow `feature.py` + `feature_gui.py` pattern
- [ ] Any new distro guard documented in `DISTRO_GUARDS.md`
- [ ] `CHANGELOG.md` updated with what changed and why
