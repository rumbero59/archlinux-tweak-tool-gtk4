---
name: feedback-ui-naming-convention
description: ATT UI hierarchy vocabulary — page vs tab means different things; use the right term
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b8c22086-6439-4a2c-a014-60af0b54d3e7
---

Use the correct ATT UI vocabulary at all times:

- **Page** — a top-level sidebar entry (Plymouth, Services, SDDM, Kernels, Packages, etc.)
- **Tab** — a sub-section within a page (Audio, Bluetooth, Printing are tabs *inside* the Services page)

**Why:** The user drew this distinction explicitly; mixing the terms causes confusion when discussing guards, guards docs, and UI layout.

**How to apply:** In code comments, docs (DISTRO_GUARDS.md), conversation, and the Dev diagnostics UI — always say "Plymouth page" not "Plymouth tab", "page visibility guard" not "tab visibility guard". Only use "tab" when referring to a stack switcher sub-item inside an existing page.
