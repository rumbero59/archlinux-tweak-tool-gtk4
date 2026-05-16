---
name: arco-chadwm skel path is intentional
description: /etc/skel/.config/arco-chadwm is the real folder name on disk — not an ArcoLinux brand ref, do not rename
type: project
originSessionId: 5fb4fe9c-d68b-408c-a66d-04f09c0c2778
---
**CRITICAL: `/etc/skel/.config/arco-chadwm` is the folder where the desktop is located on disk. MUST KEEP UNCHANGED.**

This is the actual directory name of the chadwm skel config on the system. It is NOT a brand reference.

**Why:** Changing this folder name breaks desktop installation. The folder structure is fixed and required by the system.

**How to apply:** 
- When grepping for arco refs, skip this path entirely
- Never rename, abbreviate, or replace with alternatives
- Always reference exactly as: `/etc/skel/.config/arco-chadwm`
- This is non-negotiable
