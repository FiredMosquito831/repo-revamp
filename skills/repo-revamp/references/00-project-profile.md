# 00 — The project profile

Fill this once per workspace. Every other reference assumes it exists.

The profile is not a config file the tooling reads. It is a short block the orchestrator writes into the workspace notes (`_revamp/PROFILE.md`, or the project's `CLAUDE.md` if it already has one) so a fresh session does not re-ask the same questions.

## The block

```markdown
## Revamp profile

- Owner / GitHub account: <owner>
- Attribution line (commits and PR bodies): <line>
- Domain zone: <zone>            # e.g. danubelabs.net, on Cloudflare
- DNS provider: <Cloudflare | other>
- Search Console property: <sc-domain:zone | url-prefix>
- Default hosting: <GitHub Pages | Cloudflare Pages>
- Hosting rule: <when to use the other host>
- Workspace root: <absolute path>
- Scratch root: <absolute path>
- Notes root: <absolute path>
- Default branch policy: <detect per repo | fixed>
- Repo visibility policy: <public by default | private by default>
- Site branch name: <revamp>
- Site output directory: <docs>
- Builder name: <scripts/build_site.py>
- Requirements file: <requirements-site.txt>
- Port for local serves: <8130>
- Timezone: <UTC+3>
- Standing decisions: <dated list, see below>
```

## The shipped defaults

These are the values this playbook was written against. Change them in the profile if the workspace differs; do not change them in the references.

```markdown
- Owner / GitHub account: FiredMosquito831
- Attribution line: by FiredMosquito831
- Domain zone: danubelabs.net (Cloudflare)
- Search Console property: sc-domain:danubelabs.net
- Default hosting: GitHub Pages for public repos; Cloudflare Pages for private repos
- Site branch: revamp (simple-banking-system keeps full-banking-demo)
- Site output: docs/
- Builder: scripts/build_site.py
- Requirements: requirements-site.txt
- Local serve port: 8130
- Timezone: UTC+3
```

## Standing decisions that must be recorded

Every workspace accumulates decisions that stop being questions. Record each with its date and never re-ask it:

- Which repositories are public and which are private.
- Whether revamp work may touch product code (default: no).
- Which branch the site launches from when it is not the default branch.
- Whether merges need an explicit go (default: yes).
- Which Cloudflare or DNS steps belong to the owner (default: all of them).
- The scratch location (default: a `_tmp` folder under the workspace root, never the system drive).
- The port range for scratch services.
- Any repository whose default branch is not `main`.
- Any repository whose licence text and manifest disagree.

## Subdomain rules

The subdomain is part of the brand and part of SEO. Rules:

1. **Lowercase, hyphen-free, one word if possible.** `bankingsystem`, `cachewarm`, `tts`, `gsd`, `providers`, `searxng`, `vellum`, `bugbounty`.
2. **Keyword-rich beats clever.** `supabasedatabasemanager` is long but it is what people search.
3. **Match the product name, not the repository name**, when the product name is the better search term.
4. **Never reuse a subdomain** for a different project.
5. **Check it is free** before promising it: `dig +short <sub>.<zone>` and the Cloudflare DNS list.
6. **Record it in the tracker** the moment it is chosen.

## Repository metadata rules

Set these once per repository, through the GitHub API, after the site is live:

- **Description:** one line, keyword-rich, truthful, no hype. It is the search snippet under the repo name.
- **Homepage:** the live site URL.
- **Topics:** 10–15 accurate topics, lowercase, hyphenated. No topic the project does not earn.

`references/08-seo.md` has the exact calls.

## What the profile is not

- It is not a place for secrets. No tokens, no keys, no account IDs that are not already public.
- It is not a changelog. Dated decisions only.
- It is not per-repository state. Repository state lives in `_revamp/<repo>/STATE.md`.
