---
description: Plan and run a batch revamp — one agent per repository, deploys serialised
argument-hint: <repo...> [--dry-run]
allowed-tools: Read, Grep, Glob, Bash, Write, Agent, Skill, ListAgents
---

Plan and run a batch revamp for: **$ARGUMENTS**

Follow `references/13-batch-mode.md`.

1. **Recon every repository first**, read-only, and record each one's shape, host, subdomain and risks.
2. **Ask the owner the batch questions once** — hosting, subdomain pattern, visibility, scope, indexing, screenshots, CTA, merge posture — with a recommendation each. Record the answers once, applying to every repository unless one differs.
3. **Write one spec per repository** (or one spec with a section per repository) and append the decisions block.
4. **Launch one agent per repository in one message**, each with the full brief. Announce every dispatch. Run `ListAgents` first.
5. **Deploy one repository at a time**, never two agents on the same DNS zone or Cloudflare account.
6. **Merge one repository at a time**, only on the owner's go, checking each default branch first.
7. **Retain every site branch.** Verify every site before moving on.

If `--dry-run` is present, stop after step 3 and print the plan: repository, shape, host, subdomain, agent, and the order of deploys.
