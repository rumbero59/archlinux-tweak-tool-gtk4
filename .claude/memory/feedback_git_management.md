---
name: feedback-git-management
description: "Claude owns all git operations including pull, commit, and push; must git pull before starting any task due to multiple tabs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 548d5f0d-dc3e-4893-8404-7db3c5490d5a
---

Claude is responsible for all git management on ATT — pull, commit, and push.

**Why:** Multiple Claude tabs are always open on the same repo. Without pulling first, a tab will duplicate work that another tab already committed and pushed, or cause conflicts.

**How to apply:**
- Run `git pull` before starting any coding task, every time, no exceptions
- After confirming the current state, proceed with the task
- Commit and push specific files after every approved change (no `git add .`)
- If `git pull` shows the feature was already done by another tab, report that and stop — do not re-implement

[[feedback_user_commits]]
