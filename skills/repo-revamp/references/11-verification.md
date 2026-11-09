# 11 — Verification: the recipe the orchestrator runs itself

After every "shipped" report, before relaying anything. An agent's claim is a hypothesis; this is the proof.

## The principle

**Budget half of an agent's findings to be wrong or overstated.** Check every `file:line`. "Could not verify" is not "does not exist". "Unchanged" claims about machine state are worthless without the before and after shown.

## The recipe

### 1. Re-anchor

```sh
git -C <checkout> fetch origin --tags
git -C <checkout> log -1 --format='%h %s' origin/<default>
git -C <checkout> log -1 --format='%h %s' origin/revamp
git -C <checkout> log --oneline HEAD..origin/<default> | wc -l
```

A stale checkout produces a wrong audit. Always fetch first.

### 2. The product boundary

```sh
git -C <checkout> diff --name-only <base> origin/revamp \
  | grep -vE '^(site/|docs/|scripts/build_site\.py$|requirements-site\.txt$|\.github/workflows/site\.yml$|README\.md$|\.gitignore$)'
```

Must print nothing. If it prints a path, the PR changed product code.

### 3. The gate on a clean worktree

```sh
git -C <checkout> -c core.autocrlf=false worktree add --detach <tmp> origin/revamp
cd <tmp>
python -m pip install --requirement requirements-site.txt   # once, in a venv
python scripts/build_site.py --check
```

Expected: `check: docs/ is byte-identical to a fresh build`, exit 0.

If it reports differences on every page, suspect configuration before content:

1. CRLF from `autocrlf` — use `-c core.autocrlf=false`.
2. Git-ignored assets — `git check-ignore -v` every generated file.
3. Stale committed output — regenerate and commit.
4. A git-history `lastmod` — move it to a fixed value.

### 4. The local serve

```sh
python -m http.server 8130 --directory docs
```

Then the HTTP sweep against `http://127.0.0.1:8130`:

- every page, asset, screenshot, the sitemap, `robots.txt`, `og.png` returns 200
- `og.png` is 1200×630
- every internal link resolves

The reusable script is `scripts/verify_site.py`.

### 5. The live site

```sh
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://<host>/
curl -s -o /dev/null -w "%{http_code}\n" https://<host>/og.png
curl -s https://<host>/sitemap.xml | grep -o "<loc>" | wc -l
```

Then every `<loc>` must return 200. A sitemap with 48 URLs means 48 HTTP checks.

### 6. The served commit

GitHub Pages:

```sh
gh api repos/<owner>/<repo>/pages/builds/latest --jq '{status,commit}'
git -C <checkout> rev-parse origin/<default>
```

Cloudflare Pages: read the production deployment's commit in the dashboard or the API, and compare.

They must match. A site that answers is not proof it serves the commit you think.

### 7. The screenshots

- **Look at at least one page screenshot the agent names**, with the Read tool.
- Scan images for key prefixes and sensitive strings.
- Check the gallery lazy-loads: scroll, wait, then count.

Lazy-loaded images look broken in a full-page screenshot taken before scrolling. They are not broken; scroll first.

### 8. The claims ledger

- Every page has a `claims` list.
- Every evidence path exists.
- Every number is computed or recorded.
- No claim without evidence.

### 9. The legal texts

- The non-affiliation, licence and early-access strings appear verbatim on every footer and on `/license/`.
- The CTA points at a real channel.

### 10. The report

Read the agent's final message and extract:

- deviations from the spec
- residual risks
- what was not done
- every leftover directory

Then verify each deviation is acceptable and each leftover is listed.

## The V-table

Adapt the numbering to the project; keep the categories.

| # | Check | Evidence required |
|---|---|---|
| V1 | Path scope | `git diff --name-only` output; the product filter prints nothing |
| V2 | Builder | `--check` exits 0 on a clean worktree |
| V3 | Links and sitemap | the builder gates pass; the local sweep returns 200 for every path |
| V4 | Secret scan | zero hits |
| V5 | Placeholder scan | zero hits |
| V6 | Alt text | no image without non-empty alt |
| V7 | Page metadata | one `h1`, unique title ≤ 60, unique description 120–160 |
| V8 | JSON-LD | every block parses; FAQ equals the visible FAQ |
| V9 | Local serve | every path 200; `og.png` 1200×630 |
| V10 | Responsive | every page at 390 / 768 / 1440; no overflow, no console errors |
| V11 | Claims | every claim has a ledger row with evidence |
| V12 | Screenshots | every candidate has a verdict; counts reconcile; redactions recorded |
| V13 | Originals | no image appears as modified in the diff |
| V14 | Coverage | every feature page has 3+ images or no image slot |
| V15 | Legal | the exact texts on every page |
| V16 | Internal process | no audit, verification, scenario, prompt or agent-configuration reference |

## The report to the owner

Five lines or fewer, then the detail:

- what shipped
- what you verified (CONFIRMED, with the numbers)
- what you could not verify (UNVERIFIED)
- what was not done (NOT DONE, and why)
- the next dispatch

Lead with the negative when it is negative.

## Recording

After verification:

1. A dated "SHIPPED AND VERIFIED BY ME" line in the diary or archive.
2. A release-history row (or a tracker row).
3. The queue row flipped to FINISHED with the proofs.
4. The lessons ported.
5. The state file updated.

## Exit gate

- Every V-item is green or named as an exception with its reason.
- The live site answers.
- The served commit matches.
- The product boundary is empty.
- The screenshots were looked at.
- The report separates CONFIRMED, UNVERIFIED and NOT DONE.
