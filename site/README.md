# The site

The generated public site for the repo-revamp plugin. It is built by `scripts/build_site.py`
into `docs/`. Everything under `docs/` is owned by the builder; edit the sources under `site/`
and the repository files, then run the builder.

## Rebuild

```sh
python -m pip install --requirement requirements-site.txt
python scripts/build_site.py            # run the gates, then write docs/
python scripts/build_site.py --check    # build to a temp dir and byte-compare with docs/
python scripts/build_site.py --gates    # print every gate's result
python scripts/build_site.py --claims   # print the claims ledger as Markdown
```

The builder is Python 3.12 plus Jinja2 only, both pinned in `requirements-site.txt`. It is
deterministic: no wall clock, no git history, no randomness. Every list is sorted and every file
is written with LF newlines, so the committed `docs/` is byte-identical to a fresh build.

## What the builder reads

- `site/content/*.json` — one file per page plus `site.json`, each with a `claims` list.
- `site/templates/` — `base.html`, `page.html`, `404.html`.
- `site/static/` — `style.css`, `site.js`, `favicon.svg`, `icon.png`, `og-source.html` and the
  four diagrams in `site/static/diagrams/`.
- `site/shots/manifest.json` — the three terminal captures and their alt text, captions and size.
- `site/design-tokens.json` — the colour, font, spacing, radius, motion and focus tokens.
- `commands/`, `agents/`, the reference files, the templates and the scripts — the inputs for the
  generated reference page.

## The gates

Run before anything is written; the first failure stops the build and leaves `docs/` untouched.

1. Secret scan — patterns for tokens, keys, connection strings, credentials, email, private IPs
   and owner paths. Reported by file and line, never the value.
2. Forbidden strings — a fixed list of unfinished-content markers.
3. Links — every internal `href` and `src` resolves, and every fragment resolves to an `id`.
4. Page metadata — exactly one `<h1>`, a title of at most 60 characters, a description of 120 to
   160, an absolute canonical, complete Open Graph and Twitter tags, and the background token as
   the theme colour.
5. Alt text — every image has non-empty `alt`.
6. JSON-LD — every structured-data block parses, and the FAQ data equals the visible FAQ.
7. Sitemap — every URL in `sitemap.xml` has a file in `docs/`.
8. Social image — `docs/og.png` is present and is exactly 1200 by 630.
9. Tokens only — every colour in the CSS, templates and diagrams is a design token.
10. Reference completeness — the generated reference lists exactly the files in the repository.
11. Word counts — each page is inside its declared range.
12. Diagrams — each SVG carries a `role`, a title, a description and an aria label.
13. CNAME — `docs/CNAME` holds the bare hostname.
14. Legal texts — the non-affiliation and licence strings are in every footer.
15. No external requests — no fonts, CDNs, analytics or embeds.
16. No internal process — the site's own working files do not leak into the output.
17. Claims ledger — every page has a claims list and every piece of evidence resolves.

## Design records

`site/design-system/repo-revamp/MASTER.md` is the design-intelligence output, persisted once.
`DECISIONS.md` records what was adopted and rejected, and the computed contrast table.

## Serving locally

```sh
python -m http.server 8130 --directory docs
```

Then the HTTP sweep: every page, asset, capture, the sitemap, robots and the social image should
answer 200.
