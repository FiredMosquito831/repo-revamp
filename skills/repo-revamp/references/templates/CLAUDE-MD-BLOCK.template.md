<!-- repo-revamp:begin (managed by the repo-revamp skill; edit inside only through the skill) -->
## How we revamp repositories

**Entry points:** `_revamp/<repo>/STATE.md` (phase, gates, next action) → the spec in `_revamp/<repo>/SPEC.md` with its binding `USER DECISIONS` block → the playbook reference for the current phase.

**Binding rules:**
1. Recon read-only before anything. Spec with numbered questions and a recommendation each. The owner answers. Append `USER DECISIONS (<time>)`. Only then dispatch one implementer.
2. Product code is frozen unless the spec explicitly says rebuild. The boundary diff must print nothing.
3. Every fact traces to code, tests, the README or the user docs. No invented numbers. No placeholders. A thin page is cut, never padded.
4. The build is deterministic: no wall clock, no git history, no randomness. `python scripts/build_site.py --check` is the gate.
5. Secrets never appear in output. Report a hit by file and line only.
6. Screenshots are reviewed, redacted on copies, captioned, manifested. Originals are read-only.
7. Design derives from the product. Tokens only. No external fonts, CDNs, analytics or embeds. WCAG 2.2 AA.
8. Deploy only after the gate is green. Verify the served commit, not just the URL.
9. Merge only on the owner's explicit go. Revert, never force. Retain the site branch.
10. Report CONFIRMED / UNVERIFIED / NOT DONE. The final message is the deliverable.

**Attribution:** commits and PR bodies end with `<attribution>`.
<!-- repo-revamp:end -->
