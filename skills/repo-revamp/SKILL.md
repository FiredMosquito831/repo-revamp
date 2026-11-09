---
name: repo-revamp
description: Turn a GitHub repository into a live, polished, search-optimised product site and documentation surface, end to end — read-only recon, a numbered spec with the owner's binding decisions, a delegated build of a generated static site committed in docs/ with a deterministic builder and hard gates, a reviewed screenshot pipeline, an original design system, full SEO, deployment to GitHub Pages or Cloudflare Pages, PR and merge discipline, and an exhaustive verification recipe. Use when the user says revamp, rebuild the site, make this repo presentable, add a website or docs site, deploy a repo site, give this project a landing page, or asks to run the repo revamp playbook.
---

# repo-revamp

The complete operating playbook for revamping a GitHub repository: from "here is an old repo" to a live, verified, search-indexed site with documentation, without breaking the product.

This skill is exhaustive on purpose. The main file is the contract and the state machine. The `references/` files carry the depth: read the one for the phase you are in, not all of them at once.

## What this skill produces

A repository that has, at the end:

1. A generated static site committed in `docs/`, built by a deterministic generator with gates.
2. A reviewed, redacted, captioned screenshot set with a manifest and a coverage matrix.
3. An original design system derived from the product, with tokens and computed contrast.
4. Per-page SEO: title, description, canonical, Open Graph, Twitter, JSON-LD, sitemap, robots, a 1200×630 `og.png`, a custom 404.
5. A README that presents the project honestly and links the site.
6. A live deployment on GitHub Pages or Cloudflare Pages, on the owner's subdomain, over HTTPS.
7. A PR with a full evidence body, merged only on the owner's explicit go, with the site branch retained.
8. A verification record: every claim CONFIRMED, UNVERIFIED or NOT DONE.

## When to use it

Use it when the request is any of:

- "revamp this repo", "make this repo presentable", "give it a website", "add a docs site"
- "deploy a site for this project", "put it on my domain"
- "the repo is old, rebuild it properly and make it live"
- a batch of repositories handed over for the same treatment
- a private repository that needs a public-facing site without becoming public

Do not use it for a one-off README edit, a code review, or a product feature. Those are different jobs.

## The contract: what "done" means

**Done is not "the code is written".** Done is all of:

| # | Criterion | Proof |
|---|---|---|
| 1 | The site builds deterministically | `python scripts/build_site.py --check` exits 0 on a clean worktree at the head SHA |
| 2 | Every gate passes | secret scan 0, placeholder scan 0, links resolve, one `<h1>`, title ≤ 60, description 120–160, alt text non-empty, JSON-LD parses, sitemap files exist, `og.png` is 1200×630 |
| 3 | Every fact is traceable | the claims ledger has a row per factual statement, each with evidence |
| 4 | Every screenshot has a verdict | inventory = duplicates + reviewed + excluded-before-review; every INCLUDE has alt text and a caption |
| 5 | The live site answers | HTTP → HTTPS 301; root 200; every sitemap URL 200; `og.png` 200 |
| 6 | The served commit is the expected one | Pages `builds/latest.commit` equals the source head, or the Cloudflare deployment's commit equals it |
| 7 | The product is untouched | the frozen-boundary diff prints nothing |
| 8 | The owner can see it | a screenshot looked at by the orchestrator; the URL reported |

If any row is not true, the job is not done. Say which row and why.

## The state machine

Every revamp moves through these phases in order. A phase's exit gate must be green before the next phase starts. Phases 2–4 may overlap only in the narrow ways noted.

| Phase | Name | Who | Exit gate | Reference |
|---|---|---|---|---|
| 0 | INTAKE | orchestrator, read-only | a RECON file exists with the repo facts, the feature inventory, the hosting decision and the proposed subdomain | `references/01-intake.md` |
| 1 | SPEC | orchestrator → owner | the spec exists with numbered questions; the owner answered; a `USER DECISIONS (<time>)` block is appended | `references/02-spec.md` |
| 2 | BUILD | one delegated agent | the branch has the site, the builder, the screenshots, the design system and the README; the local gate passes; a draft PR exists; the product diff is empty | `references/03-build.md` |
| 3 | REVIEW | orchestrator | V1–V16 (or the project's adapted set) are green or named as exceptions; the orchestrator looked at screenshots | `references/11-verification.md` |
| 4 | DEPLOY | coordinator + owner | the live URLs answer; the served commit is the expected head; HTTPS is enforced | `references/09-deployment.md` |
| 5 | SEO | coordinator | the sitemap is submitted; repo description, homepage and topics are set | `references/08-seo.md` |
| 6 | SHIP | coordinator, on the owner's go | merged (or the launch branch is the deployment source), Pages repointed, rebuild verified, branch retained | `references/10-pr-and-merge.md` |
| 7 | CLOSE | orchestrator | tracker updated; lessons recorded; handoff written; the owner has the report | `references/12-orchestration.md` |

**Never skip INTAKE or SPEC.** A revamp that starts with "let me just build the site" produces invented claims, a design nobody asked for, and a PR that has to be reverted.

## The two modes

### Mode A — presentation-only (default)

Change only: `README.md`, `docs/`, `site/`, the site builder, the site requirements file, the site CI workflow, and append-only `.gitignore` lines. Product code, tests, manifests, existing workflows and existing docs are frozen.

This is the default because it is the safest and it is what most revamps need. The frozen-boundary diff is the proof.

### Mode B — rebuild (explicit opt-in only)

The owner explicitly asks for the product itself to be rebuilt or fixed (the original "old repo → full rebuild" request). Then product changes are allowed, but they are scoped by the spec, covered by tests, and never mixed into the site PR. Two PRs: the rebuild PR, then the site PR.

Mode B carries the extra rules: no placeholders, no hardcoded business rules (configuration belongs in data), every visible control works, demo data is seeded not faked, tests and CI ship with the change. See `references/03-build.md` §"Rebuild mode".

## The three site shapes

Pick the shape in INTAKE; it determines the page inventory.

1. **Product site** — the repo is an application or tool with a UI. Pages: home, features hub plus one deep page per verified feature area, quick start plus platform pages, architecture hub plus one deep page per subsystem, configuration, gallery, glossary, FAQ, troubleshooting, about, license, 404. This is the revision-2 shape and the deepest.
2. **Docs site** — the repo is a library, CLI, config schema or specification. Pages: home, install, quick start, a generated reference from real data (options, keys, commands, schema), guides, FAQ, about, license, 404.
3. **Research / data site** — the repo is a dataset, an atlas, a curated list or a study. Pages: home, the explorer or search surface, methodology, sources, findings, about, license, 404. Every number is recomputed from the data at build time.

`references/03-build.md` has the page inventory, word-count targets and content rules for each shape.

## The non-negotiables

These hold in every mode, every shape, every repository. They are the rules that were learned the hard way; each one has a reference section with the evidence.

1. **Truth before beauty.** Every factual statement traces to code, tests, the README or the user-facing docs. If it cannot be traced, delete it. Never soften it into vagueness. (`05-content-truth.md`)
2. **No invented numbers.** Counts, versions, ports, table counts and file counts are computed from the repository at build time or verified by hand and recorded. A number that appears in no source is a bug. (`05-content-truth.md`)
3. **Product code is frozen in Mode A.** The frozen-boundary diff must print nothing. If a page seems to need a product change, stop and report. (`03-build.md`)
4. **Nothing is deleted, moved, renamed, re-encoded or overwritten.** No history rewrite, no force push. Originals are read-only; derivatives are new files. (`03-build.md`)
5. **Secrets never appear anywhere public.** Not in chat, logs, files, PR bodies, commit messages, alt text, captions or manifests. Scan every text file; report a hit by file and line only, never the value. (`05-content-truth.md` §secret scan)
6. **No placeholders, ever.** `TODO`, `TBD`, `lorem`, `YOUR_`, `placeholder`, `XXX`, `example.com`, `coming soon`, `[insert`, `FIXME` fail the build. A thin page is cut or folded, never padded. (`05-content-truth.md`)
7. **The build is deterministic.** No wall clock, no git-history reads, no random IDs, sorted lists. The committed `docs/` is byte-identical to a fresh build. (`04-builder.md`)
8. **No third-party requests.** No analytics, cookies, external CDNs, external fonts, embeds or trackers. Everything is generated locally. (`07-design.md`, `03-build.md`)
9. **Accessibility is part of done.** WCAG 2.2 AA contrast, visible focus, keyboard operation, skip link, landmarks, alt text, 44×44 targets, reduced motion, one `<h1>` per page. (`07-design.md`)
10. **Responsive at 390, 768 and 1440.** No horizontal overflow at any width. Screenshots reviewed at all three. (`07-design.md`)
11. **Screenshots are reviewed, not collected.** Every candidate gets a verdict; sensitive regions are redacted on a copy; originals are never modified; the manifest records everything. (`06-screenshots.md`)
12. **Design is derived from the product.** Tokens only, no hard-coded hex in templates, contrast computed over every pair, no generic template look, no copied brand marks. (`07-design.md`)
13. **SEO is complete per page.** Title, description, canonical, OG, Twitter, JSON-LD, sitemap, robots, `og.png` 1200×630, custom 404. (`08-seo.md`)
14. **Deployment is verified at the served commit.** Pages `builds/latest.commit` equals the source head; every sitemap URL returns 200; HTTP redirects to HTTPS. (`09-deployment.md`, `11-verification.md`)
15. **Merge only on the owner's explicit go.** Revert, never force. Retain the site branch. (`10-pr-and-merge.md`)

## Working files

The skill keeps its working state outside the repository, beside it, so nothing internal is ever committed:

```
<workspace>/
├── <repo>/                      the checkout
└── _revamp/<repo>/
    ├── STATE.md                 phase, branch, head, URL, gates, open questions
    ├── RECON.md                 phase 0 output
    ├── SPEC.md                  phase 1 output, with USER DECISIONS
    ├── CLAIMS.md                the claims ledger
    ├── SHOTS/
    │   ├── inventory.csv
    │   ├── clusters.csv
    │   ├── review.csv
    │   ├── coverage.md
    │   └── sheets/              contact sheets
    ├── BRIEFS/                  every brief given to an agent
    └── VERIFY/                  gate outputs, HTTP sweeps, screenshots of the site
```

If the project already uses the `working-notes` skill (`_orchestration/`), put `STATE.md`, `SPEC.md` and the queue there instead and keep `CLAIMS.md` and `SHOTS/` under `_revamp/`. Do not duplicate tracking.

`references/templates/STATE.template.md` is the state file. Update it at every phase boundary; it is what a fresh session reads first.

## Commands

| Command | What it does |
|---|---|
| `/repo-revamp:revamp <repo-or-path>` | Start or resume a revamp: locate, recon, and drive the state machine from the current phase |
| `/repo-revamp:revamp-status [repo]` | Print the state file, the phase, the gates and the open questions |
| `/repo-revamp:revamp-verify <url-or-dir>` | Run the verification recipe: HTTP sweep, redirects, `og.png`, sitemap, local `--check` |
| `/repo-revamp:revamp-deploy <repo>` | Walk the deployment for the chosen host, including the owner-only steps |
| `/repo-revamp:revamp-batch <repo...>` | Plan and run a batch: one agent per repo, deploys serialised |

## Delegation in one page

- **One implementer per repository.** In batch mode, one agent per repo, launched together in one message.
- **The orchestrator does not build the site itself.** It reconnoitres, writes the spec, writes the brief, verifies, deploys and reports. Protect its context.
- **Every agent gets a written brief** from `references/templates/BRIEF-SITE-BUILDER.template.md`, with the spec path, the binding decisions, the hard rules and the report format.
- **Every agent keeps `PROGRESS.md` and `HANDOFF.md` in its worktree from the first edit** and commits WIP early.
- **Announce every dispatch** in the same message. Run `ListAgents` first.
- **Bounded waits only.** No infinite polling, no foreground sleep over ten minutes.
- **Agents never merge, deploy, touch DNS, change repository settings, or edit the tracking files.** Those belong to the coordinator and the owner.

Full protocol: `references/12-orchestration.md`.

## Verification in one page

After the agent says "shipped", before relaying anything:

```sh
# 1. Re-anchor
git -C <checkout> fetch origin --tags
git -C <checkout> log -1 --format='%h %s' origin/<default>
git -C <checkout> log -1 --format='%h %s' origin/revamp

# 2. Product boundary
git -C <checkout> diff --name-only <base> origin/revamp \
  | grep -vE '^(site/|docs/|scripts/build_site\.py$|requirements-site\.txt$|\.github/workflows/site\.yml$|README\.md$|\.gitignore$)'
# must print nothing

# 3. Gate on a clean worktree
git -c core.autocrlf=false worktree add --detach <tmp> origin/revamp
python scripts/build_site.py --check

# 4. Live
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://<host>/
curl -s -o /dev/null -w "%{http_code}\n" https://<host>/og.png
curl -s https://<host>/sitemap.xml | grep -o "<loc>" | wc -l
# then every loc must return 200

# 5. Pages served commit
gh api repos/<owner>/<repo>/pages/builds/latest --jq '.commit'
```

Then look at a screenshot, read the agent's deviations and not-done list, and report CONFIRMED / UNVERIFIED / NOT DONE.

The full recipe, including the local serve, the Playwright matrix and the V1–V16 table, is `references/11-verification.md`. The reusable script is `scripts/verify_site.py`.

## Reference map

| File | Read it when |
|---|---|
| `references/00-project-profile.md` | first run: fill the profile (owner, domain, attribution, defaults) |
| `references/01-intake.md` | phase 0: recon, feature inventory, hosting decision, subdomain |
| `references/02-spec.md` | phase 1: writing the spec and the decisions block |
| `references/03-build.md` | phase 2: the page inventory per shape, the build order, rebuild mode |
| `references/04-builder.md` | phase 2: the generator contract, determinism, gates, CI |
| `references/05-content-truth.md` | phase 2: claims ledger, sourcing, forbidden content, legal texts |
| `references/06-screenshots.md` | phase 2: inventory, dedupe, review, redaction, derivatives, coverage |
| `references/07-design.md` | phase 2: design system, tokens, contrast, responsive, motion, ui-ux-pro-max |
| `references/08-seo.md` | phases 2 and 5: metadata, JSON-LD, sitemap, robots, Search Console, repo metadata |
| `references/09-deployment.md` | phase 4: GitHub Pages and Cloudflare Pages, DNS, HTTPS, cert nudge |
| `references/10-pr-and-merge.md` | phases 2 and 6: branch, commits, PR body, merge, revert, repoint |
| `references/11-verification.md` | phase 3 and after every "shipped" |
| `references/12-orchestration.md` | throughout: delegation, tracking, handoff, lessons |
| `references/13-batch-mode.md` | when several repositories are handed over at once |
| `references/14-pitfalls.md` | when something looks wrong; every real trap we hit |
| `references/15-private-repos.md` | when the repository must stay private |
| `references/16-maintenance.md` | after launch: adding a page, changing a domain, re-running gates |

Templates: `references/templates/`. Scripts: `scripts/`.

## The one-paragraph version

Reconnoitre read-only. Write a numbered spec and wait for the owner's one-line answers. Give one agent a complete brief and a worktree. It builds a generated site in `docs/` with a deterministic builder, hard gates, a reviewed screenshot set, an original design system and full SEO, and opens a draft PR without touching product code. You verify every claim yourself, deploy on the owner's go, submit the sitemap, merge only when told, repoint the deployment, retain the branch, and record what you learned. Then the repository is live.
