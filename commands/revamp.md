---
description: Start or resume a repository revamp — recon, spec, build, deploy, verify
argument-hint: <repo-or-path> [--resume | --batch]
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent, Skill, ListAgents
---

Load the `repo-revamp` skill and follow its state machine for: **$ARGUMENTS**

Do this now, in order:

1. **Locate.** Resolve the repository (a name under the owner's account, or a local path). Read `_revamp/<repo>/STATE.md` if it exists. If it does not, this is a new revamp: start at phase 0.
2. **Resume or start.** If a state file exists, report the phase, the gates and the open questions in five lines, then continue from the current phase only. If it does not, run INTAKE read-only per `references/01-intake.md` and write `RECON.md`.
3. **Never skip the spec.** Before any dispatch, the spec must exist with numbered questions, each with a recommendation, and the owner must have answered. Append the `USER DECISIONS (<time>)` block verbatim.
4. **Dispatch one implementer** with the brief from `references/templates/BRIEF-SITE-BUILDER.template.md`. Announce it. Run `ListAgents` first.
5. **Verify yourself** after the agent reports, per `references/11-verification.md`.
6. **Deploy only on the owner's go**, and only after the gate is green.
7. **Never merge** without the owner's explicit go.

Report in five lines or fewer at every step: phase, what you did, what passed, what is blocked, what you need.
