---
name: Auto-Fix All Flake8 Issues
description: User approves automatic flake8 fixes without asking permission
type: feedback
originSessionId: 2a60f01d-b4ca-4151-ad28-48141fb328d5
---
**Rule:** Answer yes to all flake8 violations automatically. Never ask permission — just run flake8 and fix all issues.

**Why:** User expects flake8 compliance as non-negotiable standard; asking for confirmation on each violation is unnecessary friction.

**How to apply:** When running code quality tasks:
1. Run flake8 on the file/module
2. Fix all violations automatically (Edit tool)
3. Re-run flake8 to verify pass
4. Move on — no "should I fix this?" needed

This applies to E402, W503, W504, E128, E203, and any other configured ignores.
