---
name: Multi-Machine Development Workflow
description: ATT is developed from two or more machines; session files like CHANGELOG.md and CLAUDE.md will diverge and need periodic merging
type: project
originSessionId: ee004e9f-c88d-49b5-b54c-85dea3a0ab09
---
Erik develops ATT from multiple machines simultaneously:
- Primary: Kiro Arch Linux
- Secondary/Testing: other Arch-based distros (Omarchy, CachyOS confirmed; more expected)

**Why:** Testing ATT on real target distros; some features (Plymouth, SDDM guard, desktop detection) require the actual target OS to verify.

**How to apply:**
- CHANGELOG.md, CLAUDE.md, and IDEAS.md will diverge between machines; expect merge conflicts on these files at session start
- When git pull shows conflicts on these files, treat the merge as a consolidation task: preserve all entries from both sides, de-duplicate if the same change was noted on both machines
- CHANGELOG.md entries are date-keyed — two machines on the same date produce two entries for the same date; merge into one consolidated entry
- CLAUDE.md "Recent Work" section is the most likely conflict point; keep the union of both machines' entries, sorted newest-first
- Code files (.py, .sh) should not conflict if each machine works on different features; if they do, use git diff to understand both sides before resolving
- Always `git pull` before starting a session on either machine to minimize divergence
