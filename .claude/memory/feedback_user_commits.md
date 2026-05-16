---
name: user-handles-all-commits
description: "Claude commits and pushes automatically after every approved change — never reminds the user to do it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 35e191b5-3afa-49a1-8855-7c8bac6f7e4a
---

When the user confirms a code change ("yes", "go ahead", etc.), that single confirmation authorizes the full sequence: make the change → run flake8 → fix any lint issues → commit → `git push origin`.

Never say "Remember to commit to the github" — just do it silently as part of the workflow.

**Why:** User commits from now on via Claude — the reminder is redundant noise.

**How to apply:**
- State exactly what will change and why, then wait for yes
- After yes: edit → flake8 → fix lint → `git add <specific files>` → `git commit` → `git push`
- Never `git add .` or `git add -A` — stage only files touched in this change
- Never amend a published commit; always create a new one
- Never force-push
- Commit message format: `type(scope): description` — concise, imperative, lowercase
- Never follow up with any reminder about committing or pushing
