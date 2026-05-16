---
name: Widget Naming Convention — No hbox1/hbox2
description: Use descriptive names for layout boxes and widgets, never hbox1/hbox2/vbox1 etc.
type: feedback
originSessionId: 51fded40-8f3b-41b1-bbd6-338701f8b4cb
---
Never use generic numbered names like `hbox1`, `hbox2`, `vbox3` for layout containers or widgets. Use descriptive names that reflect the content or purpose.

**Why:** Generic numbered names make code unreadable and impossible to maintain. When something breaks or needs updating, you can't tell what `hbox14` contains without reading all surrounding code.

**How to apply:**
- New code: always use descriptive names (e.g. `hbox_autologin`, `hbox_bash_buttons`, `vbox_theme_section`)
- When renaming existing code: find and update ALL references to the variable in the same file — if stored as `self.hbox3`, grep for every usage before renaming
- Local variables (not stored on `self`) only need renaming within their function scope
- `self.*` attributes need a project-wide grep before renaming
