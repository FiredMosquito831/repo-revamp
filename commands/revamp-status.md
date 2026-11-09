---
description: Show the revamp state — phase, gates, open questions, leftovers
argument-hint: [repo]
allowed-tools: Read, Grep, Glob, Bash
---

Show the current revamp state for: **$ARGUMENTS** (or every revamp under `_revamp/` if none is named).

Read `_revamp/<repo>/STATE.md` and report:

1. **Phase** and the next action.
2. **Gates** — a compact table: pass / fail / pending, with the evidence line for each failure.
3. **Open questions** the owner still owes, each with its recommendation.
4. **Agents** — any running, with their worktree and HANDOFF path.
5. **Leftovers** — directories and files left in place.
6. **Live state** — if a URL is recorded, check it: root 200, `og.png` 200, HTTP → HTTPS, sitemap URL count. Mark each CONFIRMED or UNVERIFIED.

Do not dispatch anything. Do not change anything. Five lines of summary, then the table.
