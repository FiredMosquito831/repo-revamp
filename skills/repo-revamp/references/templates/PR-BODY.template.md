# <Specific title: what this PR adds>

<Three sentences: what this PR adds, what it does not change, how it was verified.>

## What changed

| Folder | Files | What |
|---|---:|---|
| `docs/` | <n> | Generated site output (<pages> pages, assets, <shots> screenshot derivatives, sitemap, robots, 1200×630 OG image). Owned by the builder. |
| `site/` | <n> | Site source: <content files>, templates, static CSS/JS/favicon, <diagrams> diagrams, <shots> screenshot derivatives + manifest, design tokens, design-system records, site README. |
| `scripts/` | 1 | `build_site.py` (new file only). |
| `.github/workflows/` | 1 | `site.yml` (new file only). No existing workflow was modified. |
| root | <n> | `requirements-site.txt` (new), `.gitignore` (append-only), `README.md` (site link). |

## What did not change

- Product code (`<paths>`), manifests, `bin/`, `packages/`, `apps/`, tests and scripts.
- Existing product documentation other than the READMEs listed above.
- Licence, repository visibility, settings, topics, branch protection, Actions secrets, environments.
- Existing images: no tracked image is modified, deleted or re-encoded.

## Page inventory

| Page | Words | Images | Diagrams |
|---|---:|---:|---:|
| `/` | <n> | <n> | <n> |

Total: <n> pages, <n> visible words. Word counts are computed by the builder's gate from the rendered `<main>`.

## Diagram inventory

All are original SVGs in `site/static/diagrams/`, with `role="img"`, `<title>`, `<desc>`, a visible legend and a text alternative below the figure.

1. `<file>` — <what it shows>.

## Design decisions

Source of truth: `site/design-system/<product>/MASTER.md`, with page overrides in `pages/` and the full record in `DECISIONS.md`. <stack decision: no `--stack` because plain HTML/CSS>.

Adopted: <list>.
Rejected: <list, with reasons>.
Contrast (WCAG 2.2 AA, computed over every final token pair): lowest body pair <ratio>; lowest UI pair <ratio>. <what was fixed>.

## Screenshot pipeline numbers

- Inventory: <n> tracked images.
- SHA-256 de-duplication: <n> unique hashes; <n> exact duplicates removed.
- Perceptual clustering: <n> clusters; <n> near-duplicates removed.
- Candidates carried to visual review: <n>.
- Verdicts: <n> INCLUDE (<n> clean, <n> redacted on a copy), <n> EXCLUDE.
- EXCLUDE reasons: <list with counts>.
- Redactions: <where>. Rectangles recorded in `site/shots/manifest.json`; originals unmodified.
- Gallery: <n> images, <n> areas, every image with a caption and alt text.
- Size: <n> MB total; largest full image <n> KB.

## Verification

| Item | Evidence |
|---|---|
| V1 path scope | <the diff output; the product filter prints nothing> |
| V2 builder | `python scripts/build_site.py --check` → <result> |
| V3 links and sitemap | <n> HTTP paths returned 200 |
| V4 secret scan | zero hits |
| V5 forbidden strings | zero hits |
| V6 alt text | <n> checks, 0 missing |
| V7 page metadata | one `h1`, unique titles ≤ 60, unique descriptions 120–160 |
| V8 JSON-LD | <n> blocks parse; FAQ equals the visible FAQ |
| V9 local serve | <n> paths 200; `og.png` 1200×630 |
| V10 responsive review | <n> pages × 390/768/1440, 0 issues |
| V11 claims ledger | <n> rows; every evidence path exists |
| V12 screenshot review | <counts reconcile> |
| V13 originals unchanged | <the diff output> |
| V14 coverage | <every feature page has 3+ images or no slot> |
| V15 legal text | the exact strings on <n>/<n> pages |
| V16 internal-process scan | <what the grep found and why it is clean> |

## Content cut or not verified

- <what was cut and why>.
- <discrepancies found>.

## Owner-only steps

1. <exact dashboard step>.
2. <exact settings>.
3. <what to hand back>.

## Residual risks

<none, or the list>

<attribution>
