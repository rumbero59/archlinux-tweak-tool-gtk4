---
name: feedback-docstring-rule
description: "Docstring rule changed from \"no docstrings\" to PEP 257 — public functions get one-liner, private functions don't require them"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2248d95-5e3c-461a-88b1-6aca3e767a98
---

Follow PEP 257 for docstrings, not the old "no docstrings unless asked" rule.

**Why:** User confirmed docstrings have no speed impact and PEP 257 is the Python standard. Complex functions (bootloader detection, CPU compat, config parsing) benefit from a one-line docstring explaining what they return.

**How to apply:**
- Public functions/methods: one-line docstring if the name alone doesn't fully describe return value or behavior
- Private functions (prefixed `_`): no docstring required
- Never write multi-paragraph docstrings
- During reviews: don't flag existing docstrings on public functions as issues; only remove trivially redundant ones (e.g. `"""create a gui"""`)
- Both CLAUDE.md files updated 2026-05-15
