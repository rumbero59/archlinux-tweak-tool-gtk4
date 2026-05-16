---
name: alacritty --hold conflicts with read
description: Never use --hold with alacritty when the script ends with read -p; --hold keeps the window open after read exits so Enter never closes it
type: feedback
originSessionId: de7c78ac-8b02-4fd8-93ac-79bc8496be87
---
Never combine `alacritty --hold` with a script that ends in `read -p "Press Enter to close..."`.

**Why:** `--hold` keeps the alacritty window open after the process exits. So when the user presses Enter, the script exits but the window stays open — Enter appears to do nothing.

**How to apply:** Use either `--hold` (window stays until manually closed, no read needed) OR `read -p` at the end of the script (window closes when user presses Enter, no --hold). Never both. ATT preference is `read -p` without `--hold` so the user has an explicit close action.
