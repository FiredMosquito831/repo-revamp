# 03 — BUILD: the page inventory, the build order and the brief

Phase 2. One delegated agent, one worktree, one branch. This file is the content side; `04-builder.md` is the generator side.

## The branch and the worktree

```sh
git -C <checkout> fetch origin
git -C <checkout> worktree add -b revamp <absolute-worktree-path> origin/<base>
```

- **Absolute paths.** A relative path after `git -C` resolves against the wrong base and creates the worktree in the wrong place.
- **Base:** the repository's default branch, unless the spec says the site launches from an existing branch.
- **Never** the primary checkout, never `git stash`, never `git checkout <file>`, never `git reset`.
- **Never delete** anything in the scratch tree. List leftovers in the report.

## The build order

Build in this order. Each step depends on the previous one.

1. **Skeleton.** `site/` structure, the builder, the requirements file, the CI workflow, the `.gitignore` append. Get `--check` passing on an empty site before writing content.
2. **Tokens and templates.** `site/design-tokens.json`, `site/templates/base.html`, `page.html`, `404.html`, the CSS. Tokens only; no hard-coded hex in templates.
3. **Content data.** One JSON file per page under `site/content/`, with a `claims` list per page.
4. **Screenshots.** The pipeline in `06-screenshots.md`; the manifest; the coverage matrix.
5. **Diagrams.** Original SVGs in `site/static/diagrams/`.
6. **SEO.** The builder emits metadata from the content; the sitemap, robots, `og.png`, favicon.
7. **README and docs index.** Presentation layer only; keep the honest narrative, licence and contributing sections.
8. **Gates and the local serve.** `--check`, the HTTP sweep, the Playwright matrix.
9. **Commits.** One per logical family, then push and open the draft PR.

## Page inventory by shape

### Shape 1 — product site

The deepest shape. Every page is directory-style (`/features/database/index.html`), one `<h1>`, shared header and footer, breadcrumbs on every non-home page, a sticky table of contents on every deep page.

| Page | Target words | Required content |
|---|---:|---|
| `/` | 1,200–1,800 | hero, value proposition, the front-door or core diagram, a 12–18 image gallery teaser, a feature grid linking every deep page, an architecture teaser, verified quick facts, an FAQ teaser, the CTA, footer |
| `/features/` | 400–700 | every feature area as a card linking its deep page, one overview image |
| `/features/<area>/` | 900–1,600 | what it is, why it matters, numbered usage steps, 3–8 screenshots with captions and callouts, "where you see it", "configuration" (names only), "limits and behaviour", related links |
| `/quick-start/` | 500–800 | overview, prerequisites matrix (verified platforms and versions only), links to platform pages |
| `/quick-start/<platform>/` | 400–600 | numbered steps with copy-paste commands exactly as the repo supports them, expected output in words (never invented logs), "if it goes wrong" |
| `/quick-start/first-stack/` | 500–800 | a guided walkthrough of the first real use, 6–10 screenshots |
| `/architecture/` | 700–1,000 | system overview, at least three diagrams, the subsystem map, glossary links |
| `/architecture/<subsystem>/` | 800–1,400 | at least two original SVG diagrams, a "code map" at product level, the lifecycle or flow, failure and recovery from user-facing docs, related links |
| `/configuration/` | 500–800 | how settings are provided, links to sub-pages |
| `/configuration/<topic>/` | 400–700 | variable names, purpose, required or optional, where read; never values |
| `/gallery/` | 60–200 intro | every image grouped by area, a sticky area index, a caption on every image |
| `/glossary/` | 1,500–2,500 | at least 40 terms with verified definitions and anchors |
| `/faq/` | 1,500–2,500 | 20–30 real questions, answers mirrored exactly in the FAQPage JSON-LD |
| `/troubleshooting/` | 800–1,200 | common problems: symptom, verified cause, verified fix |
| `/troubleshooting/<issue>/` | 300–600 | one issue, a screenshot where it helps |
| `/about/` | 500–800 | author, project status, the honest "how this got built" story condensed from the README |
| `/license/` | 400–600 | licence summary, third-party attributions, trademark and non-affiliation notice |
| `/404.html` | 60–100 | friendly, `noindex`, links home and to features |

Rules:

- Create a deep page **only** when code or tests prove the feature exists.
- A feature that is planned or partial is labelled as such or omitted.
- A page that would be thin is cut or folded into a richer parent. Never padded.
- Every deep page answers, in order: what it is, why the user needs it, how to use it (numbered, verified), what you see (real screenshots), behaviour and limits, configuration (names), related.

### Shape 2 — docs site

| Page | Target words | Required content |
|---|---:|---|
| `/` | 600–1,200 | what it is, install, a real example, the reference teaser, FAQ teaser, CTA |
| `/install/` | 400–800 | every supported install path, verified commands |
| `/quick-start/` | 400–800 | the shortest path to a working result |
| `/reference/` | generated | every option, key, command or schema entry, generated from the real data, with a stable anchor per entry |
| `/guides/<topic>/` | 600–1,200 | one task per guide, verified steps |
| `/faq/` | 800–1,500 | real questions |
| `/about/` | 300–600 | author, status, licence |
| `/license/` | 300–500 | licence and attributions |
| `/404.html` | 60–100 | friendly, noindex |

The reference page is the heart of this shape. It is generated from the real data file (schema, manifest, CLI help), never hand-written, and the builder fails if the count drifts from the source.

### Shape 3 — research / data site

| Page | Target words | Required content |
|---|---:|---|
| `/` | 800–1,500 | what the dataset is, the headline findings with their method, the explorer teaser, the sources summary, CTA |
| `/explorer/` or `/atlas/` | generated | the searchable or filterable surface over the data, works without JavaScript for reading |
| `/methodology/` | 600–1,200 | how the data was gathered, inclusion rules, limitations |
| `/sources/` | generated | every source with its URL and what it supports |
| `/findings/` | 800–1,500 | the findings, each with its evidence |
| `/about/` | 300–600 | author, status |
| `/license/` | 300–500 | data licence and attributions |
| `/404.html` | 60–100 | friendly, noindex |

Every number on this shape is recomputed from the data at build time. A hard-coded count is a bug.

## Content rules that apply to every shape

1. **One idea per paragraph.** Short sentences. Plain English. Define jargon once on first use.
2. **No hype words.** Not "revolutionary", "game-changing", "best", "ultimate", "seamless", "cutting-edge".
3. **Concrete numbers only when verified.** "Three services" only if the code starts three.
4. **The product's own words win.** If the UI says "front door", the site says "front door".
5. **Every command is copy-paste correct.** Run it once before publishing it.
6. **Every link resolves.** Internal and external.
7. **No screenshot without a caption and alt text.**
8. **No placeholder image slot.** If there is no approved image, there is no image slot.
9. **Cross-link.** Features ↔ gallery ↔ architecture ↔ configuration. Every page links home, features and FAQ in the footer.
10. **The footer carries the legal texts verbatim**, on every page.

## Rebuild mode (explicit opt-in)

Only when the owner asks for the product itself to be rebuilt.

Additional rules:

- **No placeholders and no dead controls.** Every visible button does something real.
- **No hardcoded business rules.** Rates, limits, branding and maintenance flags live in data (a settings table, a config file), not in code.
- **Demo data is seeded, not faked.** A seed script creates the demo state; the UI reads it.
- **Tests and CI ship with the change.** A new feature without a test is not done.
- **Two PRs, never one.** The rebuild PR first; the site PR after, on top of the merged rebuild.
- **The rebuild PR gets its own spec questions.** Scope, data model, what "real" means for each control.

## The brief

Use `references/templates/BRIEF-SITE-BUILDER.template.md`. It must contain, in this order:

1. **Role line.** "You are the SOLE implementer of the site for `<repo>`."
2. **Spec path and the binding decisions**, with the timestamp.
3. **The repository facts**: default branch, base SHA, visibility, licence.
4. **The numbered scope**: every deliverable, and an explicit NOT-in-scope list.
5. **The hard rules**: frozen paths, forbidden reads, secret rules, no merge, no DNS.
6. **The verification bar**: the exact commands and what success looks like.
7. **The ship sequence**: commits, push, draft PR, stop.
8. **The progress files**: `PROGRESS.md` and `HANDOFF.md` from the first edit.
9. **The report format**: the final message is the deliverable.

The brief is a spec, not a summary. An agent that has to guess will guess wrong.

## What the agent must never do

- Merge, push to the default branch, or change repository settings.
- Touch DNS, Cloudflare, Search Console, or the owner's accounts.
- Read the forbidden files (databases, logs, `.env` values, internal audit folders, the repo's own `.claude/`).
- Modify any original image.
- Use `git add -A` or `git add .`. Stage explicit paths.
- Delete, move, rename or re-encode an existing tracked file.
- Claim verification it did not run.

## Exit gate

- The branch exists with the site, the builder, the screenshots, the design system, the README and the PR.
- `--check` passes on a clean worktree at the head.
- The product-boundary diff prints nothing.
- The draft PR exists with the full body.
- `PROGRESS.md` and `HANDOFF.md` are committed.
- The agent's final message lists every proof, every deviation, every leftover directory.
