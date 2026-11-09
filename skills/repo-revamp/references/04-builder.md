# 04 — The builder: determinism, gates and CI

The generator is the only thing that writes `docs/`. It is small, deterministic, and fails loudly. This file is the contract; the repository's own `scripts/build_site.py` is the implementation.

## Language and dependencies

- **Python 3.12 standard library plus Jinja2.** Nothing else. Pin both in `requirements-site.txt`.
- **Never add site dependencies to the product's manifest.** The site requirements live in their own file so the product's install is untouched.
- **No Node dependency** for the builder. If the product is Node, the builder is still Python: one tool, one lockfile, one CI job.
- A venv under the scratch tree (`_tmp/ci-venv`) holds the site requirements. The builder runs from there.

```text
Jinja2==3.1.6
MarkupSafe==3.0.3
```

Pin exact versions. A floating version makes the build non-reproducible.

## Inputs and outputs

**Inputs, read-only:**

```
site/content/*.json        one file per page, plus site.json
site/templates/**          base.html, page.html, 404.html
site/static/**             style.css, site.js, favicon.svg, og.png, diagrams/
site/shots/**              derivatives plus manifest.json
site/design-tokens.json    the token source
site/design-system/**      MASTER.md, DECISIONS.md, pages/ (documentation, not rendered)
```

**Output:** `docs/` only. The builder owns the whole directory. It must never write outside it.

```
docs/
├── index.html
├── <page>/index.html
├── 404.html
├── sitemap.xml
├── robots.txt
├── og.png
├── favicon.svg
└── assets/
    ├── style.css
    ├── site.js
    ├── diagrams/*.svg
    └── shots/*.webp
```

## Determinism

The build must be byte-identical across machines, checkouts and days.

Rules:

1. **No wall clock.** No `datetime.now()`, no `time.time()`, no generated timestamp.
2. **No git-history reads.** The sitemap `lastmod` is a fixed value in `site/content/site.json`. Reading `git log` makes two checkouts disagree and fails `--check` on every page.
3. **No random IDs.** Slugs are derived from names, deterministically.
4. **Sorted lists.** Every iteration over a set or dict is sorted.
5. **Stable file ordering.** The output walk is sorted.
6. **No environment-dependent output.** No absolute paths in the HTML.
7. **LF newlines.** `write_text(path, text)` with `newline="\n"`.

The proof: `--check` passes on a clean worktree, twice, on two different days.

## `--check`

```python
def build(output: Path) -> None: ...
def main() -> int:
    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp))
            diff = compare(tmp, DOCS)
            if diff:
                print("check: docs/ differs from a fresh build:")
                for name in diff:
                    print(f"  {name}")
                return 1
            print("check: docs/ is byte-identical to a fresh build")
            return 0
```

- The comparison is **byte-for-byte**, not a hash of a subset.
- It prints the differing file names, not a wall of diff.
- Exit 1 on any difference; exit 0 only on identical.
- `--check` never writes to `docs/`.

## The gates

Run before writing output, fail fast, print the file and line, never the matched value for secrets.

| # | Gate | Fails when | Message |
|---|---|---|---|
| 1 | Secret scan | any pattern in §secret scan matches a text file under `site/` or `docs/` | file:line and the pattern name |
| 2 | Placeholder scan | any forbidden string matches | file:line and the string |
| 3 | Link check | an internal `href` or `src` does not resolve to a file in `docs/`, or a fragment does not resolve to an id | page and target |
| 4 | Page metadata | not exactly one `<h1>`, a title over 60 characters, a description outside 120–160, a duplicate title or description | page and the value |
| 5 | Alt text | an `<img>` without a non-empty `alt` | page and the src |
| 6 | JSON-LD | a `<script type="application/ld+json">` that does not parse | page |
| 7 | Sitemap | a URL in `sitemap.xml` has no file in `docs/` | URL |
| 8 | OG image | `docs/og.png` missing or not exactly 1200×630 | the measured size |
| 9 | Tokens | a colour in the CSS that is not a token | the value |
| 10 | Revision-2 gates (product shape) | a page below its word minimum, an architecture page with fewer than two diagrams, a feature page with fewer than three images, a gallery below 80 images, a diagram without `<title>`/`<desc>` | page and the shortfall |

A gate that cannot fail is not a gate. Prove each one against a deliberately broken input once, and record it.

## The secret scan

Patterns, applied to every text file under `site/` and `docs/` (HTML, JSON, JSON-LD, sitemap, manifests, alt text, captions):

```text
eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}          # JWT
sk_(live|test)_[A-Za-z0-9]{8,}                     # Stripe-style
service_role\s*[:=]\s*[A-Za-z0-9._-]{20,}          # service role
postgres(ql)?://[^\s"'<]+                          # connection string
mysql://[^\s"'<]+
(?i)(password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*[^\s<]{6,}
[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}     # email (zero by default)
\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b
\b[a-z]{20}\.supabase\.co\b
C:\\Users\\ | /home/ | /Users/                     # owner paths
```

Rules:

- **Report file and line only.** Never the matched value.
- **Zero hits is the only pass.** An allowlist entry needs the owner's written approval and a comment saying why.
- **Scan the rendered output too**, not just the source. A value can arrive through a template.
- **Scan the manifest and the alt text.** They are published.

## Placeholder scan

```text
TODO  TBD  lorem  YOUR_  placeholder  XXX  example.com  coming soon  [insert  FIXME
```

Case-insensitive for the word-shaped ones; `YOUR_` and `[insert` are literal.

A hit fails the build. There is no allowlist. If a legitimate word contains one (for example "placeholder" in a sentence about placeholders), rewrite the sentence.

## The page metadata gate

- Exactly one `<h1>` per page. The header logo is not an `<h1>`.
- `<title>` ≤ 60 characters, unique, page-specific.
- `<meta name="description">` 120–160 characters, unique.
- `<link rel="canonical">` absolute, with the trailing slash for directory pages.
- `og:title`, `og:description`, `og:url`, `og:image`, `og:image:alt`, `og:locale`.
- `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`.
- `theme-color` matching the token background.

## The link gate

- Every internal `href` and `src` resolves to a file under `docs/`.
- Directory links resolve to `index.html`.
- Fragments resolve to an `id` in the target page.
- External links are not fetched at build time (no network in the builder). They are checked by the verification recipe instead.

## The sitemap

- Every public page, absolute URLs, trailing slashes.
- `<lastmod>` from `site/content/site.json`, a fixed date the owner updates deliberately.
- Priorities: home 1.0, features and quick start 0.9, architecture and configuration 0.8, gallery and FAQ 0.7, about 0.5, license 0.4.
- The 404 page is not in the sitemap and carries `noindex`.

## `robots.txt`

```text
User-agent: *
Allow: /

Sitemap: https://<host>/sitemap.xml
```

## CI

A workflow that runs the gate on every push and PR touching the site paths:

```yaml
name: Site check

on:
  pull_request:
    paths: ["docs/**", "site/**", "scripts/build_site.py", "requirements-site.txt"]
  push:
    branches: [<default>]
    paths: ["docs/**", "site/**", "scripts/build_site.py", "requirements-site.txt"]

permissions:
  contents: read

jobs:
  build-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install --requirement requirements-site.txt
      - run: python scripts/build_site.py --check
```

Rules:

- **New file only.** Never modify an existing workflow.
- **The same command locally and in CI.** If CI runs something else, the gate is not the gate.
- **Private repositories:** Actions can be blocked by account billing ("The job was not started because recent account payments have failed or your spending limit needs to be increased"). Record it, run the gate locally, and say so in the PR body. Do not weaken the gate.

## `site/README.md`

A short internal file explaining how to rebuild and what the gates are. It lives under `site/`, so it is allowed. It must not contain a forbidden string (the placeholder scan caught "placeholder" in it once).

## Exit gate

- `--check` exits 0 on a clean worktree.
- Every gate has been proven against a broken input at least once.
- CI runs the same command.
- The builder writes only under `docs/`.
- No wall clock, no git history, no randomness.
