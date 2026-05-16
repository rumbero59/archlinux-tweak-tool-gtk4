# Claude AI Learning Log

Tips and techniques discovered while building ATT and alacritty-tweak-tool.
One entry per insight — no repeats.

---

## Using Claude Effectively

### Tip 001 — Scope before you code
When starting a new feature or project, describe WHAT you want and WHY before asking Claude to write any code. Claude produces better designs when it understands the goal, not just the implementation request. The alacritty-tweak-tool session is a good example: options + questions before a single line of code.

### Tip 002 — Ask for options, not solutions
When you don't know how to design something, ask "give me 3 design options" instead of "build this". You get to pick a direction that fits your skill level and timeline. Cheaper tokens, better outcome.

### Tip 003 — Answer Claude's clarifying questions fully
Claude asks questions to avoid rework. A half-answered question means Claude will make an assumption — and assumptions cost you a full re-do. Take 2 minutes to answer all questions before saying "go ahead".

### Tip 004 — Use Plan Mode for multi-file work
Any task touching more than 2 files should start in Plan Mode (/plan). Claude lays out every file it will touch and why, you approve or redirect, THEN it executes. Skipping this on large tasks is the #1 source of wasted tokens and broken sessions.

### Tip 005 — One task per prompt
"Fix the theme preview AND add the font tab AND clean up the logging" in one message produces mediocre results on all three. Break it into three separate prompts. Claude focuses better, and you can review each change before moving to the next.

---

## Project-Specific Lessons

*(filled in as we build)*
