# 12 — Orchestration: delegation, tracking, handoff and lessons

How the revamp is run across sessions, agents and pauses.

## The roles

| Role | Does | Never does |
|---|---|---|
| **Owner** | decides, approves, clicks the owner-only steps, says merge | — |
| **Orchestrator** | recon, spec, briefs, verification, deployment, merge, reporting, tracking | builds the site itself, merges without a go |
| **Implementer agent** | builds the site in a worktree, commits, pushes, opens the draft PR | merges, deploys, touches DNS or settings, edits the tracking files |
| **Investigator agent** | read-only research, writes a spec | commits, edits outside its scratch and the spec |

## The loop

1. **Re-anchor.** Default branch head, site branch head, open PRs, worktrees, live URLs, `ListAgents`.
2. **Recon.** Read-only, into `RECON.md`.
3. **Spec.** Numbered questions with recommendations, into `SPEC.md`.
4. **Owner answers.** Append `USER DECISIONS (<time>)`.
5. **One implementer.** A complete brief, a fresh worktree, the hard rules.
6. **The agent ships the branch and the draft PR.** It stops there.
7. **Verify yourself.** The full recipe.
8. **Deploy.** On the owner's go, the owner-only steps first.
9. **Report.** What shipped, what you verified, deviations, not done.
10. **Record.** Tracker, lessons, handoff, state file.

## Concurrency

- **Single repository:** at most two agents, one implementer, read-only investigators may run beside it.
- **Batch:** one agent per repository, launched together in one message. The coordinator deploys one repository at a time. Never two agents on one repository. Never two agents touching the same DNS zone or the same Cloudflare account at once.
- **One production PR at a time** per repository. Version files and generated output collide.

## The brief

A brief is a spec, not a summary. Use `references/templates/BRIEF-SITE-BUILDER.template.md`.

It contains:

1. Role line.
2. Spec path and the binding decisions, with the timestamp.
3. Repository facts: default branch, base SHA, visibility, licence.
4. Numbered scope, and an explicit NOT-in-scope list.
5. Hard rules: frozen paths, forbidden reads, secret rules, no merge, no DNS.
6. The verification bar: exact commands and what success looks like.
7. The ship sequence: commits, push, draft PR, stop.
8. Progress files: `PROGRESS.md` and `HANDOFF.md` from the first edit.
9. The report format: the final message is the deliverable.

## What goes wrong with agents, and the counter-measure

| Failure | Counter-measure |
|---|---|
| Silence | the brief says the final message IS the deliverable; partial is acceptable, silence is not |
| A kill (limit, crash) | `PROGRESS.md` and `HANDOFF.md` from the first edit, WIP committed early; resume the same agent by message with the on-disk state |
| A resume fails ("No assistant messages found") | spawn a fresh agent with the complete brief; do not re-derive the work |
| Waiting or polling forever | bounded loops with timeouts only; no foreground sleep over ten minutes |
| A stray agent | `ListAgents` before every dispatch |
| Wrong claims | budget half to be wrong; check every `file:line`; require the before and after for "unchanged" |
| Writing to the wrong file | briefs forbid editing the tracking files |
| A cut-off launch brief | check `ListAgents`, re-send the complete brief by message |
| A skill claimed but not loaded | name the skill by full path and require the path in the report; a checklist is not the skill |
| Reading the repository's own `.claude/` | briefs name the plugin-cache copies only |
| A relative worktree path | absolute paths in every brief |

## Tracking

Three files, updated at every boundary:

### STATE.md

The live state machine. Phase, repository, branch, head, URL, gates, open questions, the next action. A fresh session reads this first.

### The queue

If the project uses the `working-notes` skill, its `QUEUE.md` is the queue. Otherwise a short table in `STATE.md`:

| # | Item | Status | Spec | Notes |
|---|---|---|---|---|

Statuses: RUNNING, QUEUED, FINISHED, HELD.

### The handoff

Written before every pause or compaction:

1. The read order.
2. The state at the handoff, with what is CONFIRMED.
3. The remaining queue in order.
4. What the owner still owes.
5. The lessons of the arc.
6. The verify commands for the next session.
7. The environment facts.

## Lessons

A lesson qualifies when it is one of:

- a wrong premise that cost time;
- an agent slip that a rule now forbids;
- a trap of the machine, tool or vendor that bit once;
- a false positive (looked broken, was not) or a false negative (green hid a defect);
- a measurement that overturned an assumption.

It is written as: the lesson first, then the evidence that makes it memorable (the number, the row, the error text), then its origin (date, PR, repository). Deduplicate: if it exists, add the new origin.

The rule that follows goes into the normative file the same day. The lesson keeps the "why"; the normative file keeps the "what".

## Context discipline

- The orchestrator does not run investigations beyond a re-anchor. Delegate them.
- Take conclusions, not file dumps.
- A subagent's report is a summary; verify the claims that matter.
- When the context is near its limit, write the handoff, then compact.

## Exit gate

- The state file matches reality.
- The queue is current.
- The handoff exists before any pause.
- Every dispatch was announced.
- Every lesson is recorded with its evidence.
