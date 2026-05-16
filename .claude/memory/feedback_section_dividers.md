---
name: feedback-section-dividers
description: "Section dividers (# ── Name ──) are kept in long functions as navigation aids; only remove comments that restate a single line"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2248d95-5e3c-461a-88b1-6aca3e767a98
---

Keep `# ── Section name ──────` style dividers in long functions (50+ lines) where they help navigate distinct logical phases.

**Why:** These dividers help the developer scroll through code and orient quickly without reading every line. In a 190-line `gui()` with 7 phases, they're essential. In a 15-line helper, they're noise.

**How to apply:**
- Long functions (50+ lines) with distinct phases: keep or add dividers
- Short functions: no dividers needed
- Only remove inline comments that restate what a single line obviously does (e.g. `# find which ones are installed` above a loop that does exactly that)
- Don't remove dividers during review passes — they're intentional structure
- Both CLAUDE.md files updated 2026-05-15
