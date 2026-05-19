---
name: feedback-defer-tab-map-refresh
description: "Pages built via _defer_tab must call their refresh function immediately at build time, not only via map signal"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d5cdcb35-36c8-43ad-b860-983942cfdd13
---

Always call the refresh/init function immediately after connecting it to the `map` signal on any deferred page.

**Why:** `_defer_tab` in gui.py lazy-builds the page GUI on the first `map` signal. By the time `gui()` runs and connects `_refresh` to `map`, that signal has already fired — so `_refresh` is never called on first load, leaving buttons permanently greyed out until the user navigates away and back.

**How to apply:** Every time you connect a refresh to `map` on a deferred page, add the direct call on the next line:

```python
vboxstack_foo.connect("map", lambda _w: _refresh(self, fn))
_refresh(self, fn)   # must also call immediately
```

For named callbacks: call `_on_foo_map(None)` directly after the connect.

Exception: `kernel_gui.py`'s `on_map` is a chaotic-AUR status change detector — initial population already runs before the connect, so no immediate call is needed there.

Confirmed fixed in: services_gui, network_gui, performance_gui, privacy_gui, wallpaper_gui, themer_gui (2026-05-19).
