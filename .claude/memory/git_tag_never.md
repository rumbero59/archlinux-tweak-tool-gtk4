---
name: Never Establish Git Tags
description: User explicitly forbids creating git tags — do not suggest or implement
type: feedback
originSessionId: 2a60f01d-b4ca-4151-ad28-48141fb328d5
---
**Rule:** Never create, establish, or suggest git tags for this project.

**Why:** User is explicit: "we will never ever establish git tag ever - do not meddle with that"

**How to apply:** Remove any task involving `git tag` from task lists. Never suggest git tag baselines, rollback points, or checkpoints. When planning checkpoints, use branches or commit messages only.
