# 13 — Batch mode: several repositories at once

When the owner hands over a list, the work fans out. The coordination is what makes it safe.

## The shape

1. **Recon every repository first**, read-only, in parallel or in sequence.
2. **One spec per repository**, or one spec with a section per repository if the decisions are identical.
3. **One agent per repository**, launched together in one message.
4. **The coordinator deploys one repository at a time.**
5. **The coordinator merges one repository at a time, on the owner's go.**

## Why one agent per repository

Repositories share no files, so parallel builds are safe and much faster. But the DNS zone, the Cloudflare account, the merge decisions and the deployment are shared state. Those belong to the coordinator.

## The standard brief for a batch

Every agent gets the same standards block plus a repository-specific brief:

- what the product is, in three sentences
- the proposed subdomain
- the visual direction
- which claims must be verified from code
- the page inventory for its shape
- the guardrails: do not merge, deploy, touch DNS or Cloudflare, or change repository settings
- finish by committing on the branch, pushing, and opening a PR ending with the attribution

## The deploy order

1. Create all DNS records in one call (if the host needs them), after checking for existing records.
2. Deploy each site sequentially: create the Pages project or the Cloudflare project, poll the build, check the certificate, enforce HTTPS.
3. Verify each site before moving to the next.

Never let two agents race the same zone. Never create two projects with the same name.

## The merge batch

1. Check each repository's **default branch** first (`main` or `master`).
2. Merge each PR with `--merge` and an attributed subject and body.
3. Per repository: sync the local default, repoint Pages if needed, force a rebuild, poll until `builds/latest.commit` equals the default head.
4. Verify the live site.
5. **Retain the site branch.**

## Crash recovery

If the session dies:

- the agents are marked stopped, but their transcripts survive;
- their uncommitted work is on disk in their worktrees;
- resume each with `SendMessage` to its agent id: tell it the work is intact, check `git status`, remove junk (local servers, logs), finish verification, commit, push, open the PR;
- do not re-derive its work.

If a resume fails with "No assistant messages found", spawn a fresh agent with the complete brief and the on-disk state.

## The batch tracker

One table, updated per repository:

| Repo | Shape | Host | Subdomain | Agent | Branch | PR | Deployed | Verified | Merged |
|---|---|---|---|---|---|---|---|---|---|

## Pitfalls seen

- Repositories with no `main` (only `master`). Check before setting a PR base.
- Pages certificates stalling on `none`. Nudge with clear-and-re-add.
- Agents leaving local servers and logs behind. Clean before commit.
- Agent sites pinning site dependencies in `requirements-site.txt` so the product's runtime deps stay untouched.
- Chrome and Playwright rejecting `file://`. Serve locally for screenshots.
- One repository's site failing and blocking the batch. Deploy independently, report the failure, continue with the others.
- Two agents editing the same shared file (a workspace-level README, a tracker). Keep shared files coordinator-only.

## Exit gate

- Every repository has its own state, spec and PR.
- Every deploy is serialised and verified.
- Every merge is on the owner's go.
- Every site branch is retained.
- The batch tracker is complete.
