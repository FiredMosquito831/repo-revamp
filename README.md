# repo-revamp

A Claude Code plugin that turns a GitHub repository into a live, polished, search-optimised product site — end to end, without breaking the product.

It is the complete playbook distilled from nine public repository revamps and one private product site: read-only recon, a numbered spec with the owner's binding decisions, a delegated build of a generated static site in `docs/`, a deterministic builder with hard gates, a reviewed screenshot pipeline, an original design system, full SEO, deployment to GitHub Pages or Cloudflare Pages, PR and merge discipline, and an exhaustive verification recipe.

The plugin documents itself at <https://reporevamp.danubelabs.net>, generated from this repository.

## Install

One step, from the marketplace in this repository:

```
/plugin install repo-revamp --marketplace FiredMosquito831/repo-revamp
```

Or add the marketplace first, then install from it:

```sh
/plugin marketplace add FiredMosquito831/repo-revamp
/plugin install repo-revamp@danube-labs
```

From a local clone:

```sh
/plugin marketplace add /absolute/path/to/repo-revamp
/plugin install repo-revamp@danube-labs
```

## Use

```sh
/repo-revamp:revamp my-old-project
```

The command loads the skill and drives the state machine:

```
INTAKE → SPEC → BUILD → REVIEW → DEPLOY → SEO → SHIP → CLOSE
```

At every phase boundary it writes `_revamp/<repo>/STATE.md`, so a fresh session resumes where the last one stopped.

Other commands:

| Command | What it does |
|---|---|
| `/repo-revamp:revamp-status [repo]` | phase, gates, open questions, leftovers, live state |
| `/repo-revamp:revamp-verify <url-or-dir>` | the verification recipe: HTTP sweep, redirects, `og.png`, sitemap, local `--check` |
| `/repo-revamp:revamp-deploy <repo>` | the deployment walk, including the owner-only steps |
| `/repo-revamp:revamp-batch <repo...>` | one agent per repository, deploys serialised |

The skill itself is model-invocable: say "revamp this repo" and it loads.

## What is in this repository

```
.claude-plugin/
  plugin.json                 the plugin manifest
  marketplace.json            the marketplace manifest (this repo is its own marketplace)
skills/repo-revamp/
  SKILL.md                    the contract, the state machine, the non-negotiables
  references/
    00-project-profile.md     owner, domain, attribution, defaults
    01-intake.md              read-only recon, feature and config inventory, hosting decision
    02-spec.md                numbered questions, USER DECISIONS, change control
    03-build.md               page inventory per site shape, build order, the brief
    04-builder.md             determinism, gates, secret scan, CI
    05-content-truth.md       claims ledger, sourcing, what never gets published, legal texts
    06-screenshots.md         inventory, dedupe, pHash clustering, review, redaction, manifest
    07-design.md              tokens, contrast, responsive, accessibility, ui-ux-pro-max
    08-seo.md                 metadata, JSON-LD, sitemap, robots, Search Console, repo metadata
    09-deployment.md          GitHub Pages and Cloudflare Pages, DNS, HTTPS, cert nudge
    10-pr-and-merge.md        commits, PR body, merge, revert, launch-branch posture
    11-verification.md        the recipe the orchestrator runs itself
    12-orchestration.md       delegation, tracking, handoff, lessons
    13-batch-mode.md          several repositories at once
    14-pitfalls.md            every trap that bit, with its fix
    15-private-repos.md       a public site without publishing the source
    16-maintenance.md         after launch
    templates/                STATE, SPEC, BRIEF-SITE-BUILDER, BRIEF-INVESTIGATOR, PR-BODY, VERIFY-RECIPE, CLAUDE-MD-BLOCK
commands/                     the five slash commands
agents/                       site-builder, repo-investigator, revamp-verifier
scripts/
  verify_site.py              live and local verification, standard library only
  shots_inventory.py          inventory, SHA dedupe, pHash clustering, contact sheets
```

## The rules it enforces

1. **Truth before beauty.** Every fact traces to code, tests, the README or the user docs. A claims ledger records each one. No invented numbers. A thin page is cut, never padded.
2. **Product code is frozen** unless the spec explicitly says rebuild. The boundary diff must print nothing.
3. **Nothing is deleted or rewritten.** Originals are read-only. No history rewrite, no force push.
4. **Secrets never appear anywhere public.** Report a hit by file and line only.
5. **No placeholders.** The build fails on them.
6. **The build is deterministic.** No wall clock, no git history, no randomness. `--check` is the gate.
7. **No third-party requests.** No fonts, CDNs, analytics or embeds.
8. **Accessibility is part of done.** WCAG 2.2 AA, focus, keyboard, 44 px targets, reduced motion.
9. **Responsive at 390, 768 and 1440.** No horizontal overflow.
10. **Screenshots are reviewed, redacted on copies, captioned and manifested.**
11. **Design derives from the product.** Tokens only. Contrast computed.
12. **SEO is complete per page.** Title, description, canonical, OG, Twitter, JSON-LD, sitemap, robots, `og.png` 1200×630.
13. **Deployment is verified at the served commit**, not just at the URL.
14. **Merge only on the owner's explicit go.** Revert, never force. Retain the site branch.
15. **Report CONFIRMED / UNVERIFIED / NOT DONE.** The final message is the deliverable.

## The two modes

- **Presentation-only (default):** only README, docs, site, builder, requirements and the site workflow change.
- **Rebuild (explicit opt-in):** the product itself is rebuilt or fixed, scoped by the spec, with tests and CI, in its own PR before the site PR.

## The three site shapes

- **Product site** — home, features with deep pages, quick start, architecture with deep pages, configuration, gallery, glossary, FAQ, troubleshooting, about, license, 404.
- **Docs site** — home, install, quick start, a generated reference from real data, guides, FAQ, about, license, 404.
- **Research / data site** — home, explorer, methodology, sources, findings, about, license, 404.

## Companion skills

The playbook integrates with these when they are installed. It works without them, with a documented fallback.

- **`working-notes`** — the orchestration layer (queue, handoff, lessons). If present, the revamp uses its `_orchestration/` folder instead of duplicating tracking.
- **`ui-ux-pro-max`** — the design-intelligence suite. The skill names the process and records adopted and rejected guidance.
- **`frontend-design`** — the craft reference for a distinctive result.
- **Playwright MCP** — the browser proofs.
- **GitHub, Cloudflare and Search Console MCPs** — deployment and submission.

## Requirements

- Claude Code with plugin support.
- `git`, `gh` (authenticated), `python` 3.12.
- For deployment: access to the repository and, for Cloudflare Pages, the owner's dashboard for the one-time GitHub App authorisation.
- For the screenshot pipeline's clustering and contact sheets: `Pillow` and `imagehash` in a scratch venv. The inventory and SHA de-duplication need only the standard library.

## License

MIT. See `LICENSE`.

## Attribution

Built from the working playbook of Danube Labs. Commits and PR bodies in the revamped repositories end with the attribution line configured in the project profile.
