# SPEC — <Product>: <what this job is>

Status: draft. This document is the single source of truth for the job. Read it end to end before running any command. Where this spec and a habit conflict, this spec wins. Where this spec is silent and the risk is real, stop and report instead of guessing.

## 0. The owner's decisions (verbatim intent)

| Topic | Decision |
|---|---|
| Hosting | <GitHub Pages | Cloudflare Pages> |
| Repository | <stays private | stays public>; <what may be published> |
| Brand | <product name> |
| Domain | `<sub>.<zone>` |
| Indexing | <index now | noindex until launch> |
| Public docs | <curated user guide only | the existing docs> |
| Screenshots | <sources, review rule> |
| Delegation | <one agent, model, stop point> |

## 1. Mission and success criteria

<one paragraph>

Success means ALL of the following are true:

1. A pull request from `<site-branch>` into `<base>` exists. It changes only the paths in §4. Nothing is merged.
2. `python scripts/build_site.py --check` passes on the PR branch.
3. Every public claim is traceable to repository evidence (§9).
4. Every candidate screenshot has a recorded verdict; included images are secret-free; originals are untouched.
5. The secret scan (§5.1) finds zero hits in `docs/**` and `site/**`.
6. The verification checklist (§17) is fully green, with evidence.
7. The owner-only deployment steps are documented precisely and handed back.

## 2. Hard rules — violating any of these is a stop-and-report event

- **R1 — Stay <public|private>.** Never change repository visibility, settings, collaborators, Actions secrets, environments, branch protection, default branch, topics, or name. Never archive, fork, transfer, or delete anything.
- **R2 — Product code is frozen.** Do not modify anything outside §4.1.
- **R3 — Nothing is deleted or rewritten.** Do not delete, move, rename, re-encode, or overwrite any existing tracked file. Do not rewrite git history. Do not force-push.
- **R4 — Secret values are NEVER printed.** Not in chat, logs, files, PR bodies, commit messages, or manifests. Names only.
- **R5 — Forbidden reads.** <list: databases, logs, .env values, internal folders, .claude>
- **R6 — No merges, no pushes to the default branch.** Work only on `<site-branch>`. Open the PR. Stop there.
- **R7 — No DNS or zone changes by hand.** <the host's flow only>.
- **R8 — No placeholders anywhere in public output.** Forbidden strings: `TODO`, `TBD`, `lorem`, `YOUR_`, `placeholder`, `XXX`, `example.com`, `coming soon`, `[insert`, `FIXME`.
- **R9 — Verify every claim.** If a claim cannot be traced to code, tests, or the user-facing docs, delete it. Do not soften it into vagueness.
- **R10 — Publish only the curated surface.** Never mention or quote: <internal material>.
- **R11 — Trademarks.** No third-party logos or brand artwork. Plain-text references are fine. The non-affiliation statement appears on every footer.
- **R12 — No trackers, no third-party requests.** No analytics, cookies, external CDNs, external fonts, embeds.
- **R13 — Explicit staging only.** `git add <paths>`. Never `git add -A` or `git add .`.
- **R14 — Originals are read-only.** Derivatives go into `site/shots/` and `docs/assets/`.

## 3. Repository facts (verify again; do not trust this list blindly)

- Repository: `<owner>/<repo>` — <visibility>. Default branch: `<branch>`.
- Product name: `<name>`. Package: `<manifest name and version>`.
- Licence: `<LICENSE header>`; manifest: `<SPDX>`; GitHub detects: `<detected>`.
- README: `<lines>`, headings: `<list>`.
- Docs: `<folder, count, approximate words>`.
- Code layout: `<folders and what they are>`.
- Environment variable NAMES: `<list>`.
- Size: `<tracked files>`, `<tracked images>`.

## 4. Allowed and forbidden paths

### 4.1 ALLOWED to create or modify (nothing else)

| Path | Action | Notes |
|---|---|---|
| `README.md` | Rewrite the presentation layer | Keep <sections> |
| `docs/` | Generated output only | Owned by the builder |
| `site/` | Site source | Templates, static, content, shots, design system |
| `scripts/build_site.py` | New file | Do not edit other scripts |
| `requirements-site.txt` | New file | Pin versions |
| `.github/workflows/site.yml` | New file | Do not modify existing workflows |
| `.gitignore` | Append-only | Site cache paths only |

### 4.2 FORBIDDEN

- <product paths>
- <internal folders>
- <existing workflows>
- Git history, other branches, tags, repository settings.

## 5. Secrets and privacy

### 5.1 Secret-scan contract

Scan every text file in `docs/**` and `site/**` for: <patterns from 04-builder.md>. Any hit fails the build with file and line only.

### 5.2 `.env.example` handling

Read for names only. Check each value against the placeholder allowlist. Record the verdict per variable. If a value looks real: do not print it; report file, line and name; stop.

### 5.3 Stop-the-line events

<list>

## 6. Naming, legal and tone

- Brand: `<name>`. Domain: `<url>`.
- Non-affiliation: `<exact text>`
- Licence: `<exact text>`
- Early access: `<exact text>`
- CTA: `<url>`
- Tone: direct, technical, honest, warm. No hype words.

## 7. Site architecture

| # | URL path | Purpose | Target words | Required content |
|---|---|---|---|---|

Navigation: `<list>`.
Internal linking: `<rules>`.

## 8. Content sourcing rules

- READ: `<list>`
- NEVER READ: `<list>`
- Writing source: `site/content/*.json`, one file per page, with a `claims` list.

## 9. Claims ledger

`_revamp/<repo>/CLAIMS.md`. One row per factual statement: claim, page, evidence, status.

## 10. Screenshot pipeline

<the rules from 06-screenshots.md, with the project's budgets>

## 11. Design system

<the rules from 07-design.md, with the product's sampled colours and the identity>

## 12. Build system contract

<the rules from 04-builder.md>

## 13. SEO specification

<the rules from 08-seo.md>

## 14. Accessibility and performance budgets

<the rules from 07-design.md>

## 15. Deployment

### 15.1 Owner-only step

<the exact dashboard steps>

### 15.2 Project settings

<the table>

### 15.3 After the owner completes 15.1

<what the agent may do>

### 15.4 Verification after deployment

<the checks>

## 16. Git and pull request workflow

<the rules from 10-pr-and-merge.md>

## 17. Verification checklist

<the V-table>

## 18. Surprises and judgement calls

- If a claim cannot be verified, delete it.
- If a screenshot is unclear at review size, inspect it at full size. If it is still unclear, exclude it.
- If the product differs from its README, the README is wrong: record the discrepancy and describe only verified behaviour.
- If you are tempted to add a page, a roadmap or a testimonial that is not backed by evidence, don't.
- If a fact in this spec is wrong, verify it, record the correction, and proceed with the verified fact.

## 19. Final report

1. PR URL and branch name.
2. Files changed, grouped, with counts. Confirmation of §4 scope.
3. Screenshot pipeline numbers.
4. Secret-scan and placeholder-scan results, and the `.env.example` verdict table (names only).
5. Verification V1–V16 with one line of evidence each.
6. Owner-only actions outstanding, and the exact settings.
7. Anything not verified, any discrepancies, any stop-the-line event.
8. The `SITE_URL` used.
9. The final line: `<attribution>`.

## QUESTIONS FOR THE OWNER

1. **<question>** — Rec: <recommendation>.
2. **<question>** — Rec: <recommendation>.

## USER DECISIONS (<yyyy-mm-dd hh:mm>, binding)

> <the owner's answer verbatim>

1. <resolved decision>
2. <resolved decision>
