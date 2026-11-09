You are the SOLE implementer of the public site for `<repo>` (`<owner>/<repo>`), repository `<visibility>`, default branch `<default>`, base SHA `<sha>`. ONE branch, `<site-branch>`. ONE draft PR into `<base>`. **You do not merge. You do not deploy. You do not touch DNS, Cloudflare, Search Console, or repository settings.**

Spec (READ ALL FIRST): `<spec path>` — sections `<list>`, and the BINDING block `USER DECISIONS (<time>)` (`<summarise each decision in one clause>`). Standing rules: `<references/03-build.md, 04-builder.md, 05-content-truth.md, 06-screenshots.md, 07-design.md, 08-seo.md, 10-pr-and-merge.md>`.

## The job

<two to five sentences: what the site must be, for whom, and what it must prove>

## Scope (numbered)

1. `<deliverable, with the exact path>`
2. ...

NOT in scope: `<list>`.

## Allowed paths (nothing else)

`README.md`, `docs/**`, `site/**`, `scripts/build_site.py`, `requirements-site.txt`, `.github/workflows/site.yml`, `.gitignore` (append-only).

## Hard rules (binding)

1. **Worktree.** `<exact git worktree add command>` with absolute paths. Never the primary checkout. Never `git stash`, `git checkout <file>`, or `git reset`. Never delete scratch. List every directory left behind.
2. **Product frozen.** The diff filter must print nothing:
   ```sh
   git diff --name-only <base>...HEAD | grep -vE '^(site/|docs/|scripts/build_site\.py$|requirements-site\.txt$|\.github/workflows/site\.yml$|README\.md$|\.gitignore$)'
   ```
3. **Nothing deleted or rewritten.** No history rewrite, no force push, no re-encoding an original image.
4. **Secrets.** Never read `<forbidden files>`. Never print a value, a key, a token, a process command line, or an environment value. Report a hit by file and line only. Scan every text file in `site/` and `docs/`.
5. **No placeholders.** `TODO`, `TBD`, `lorem`, `YOUR_`, `placeholder`, `XXX`, `example.com`, `coming soon`, `[insert`, `FIXME` fail the build.
6. **Truth.** Every factual statement has a claims row with evidence. No invented numbers. Cut what cannot be verified.
7. **Tooling.** `python` with `requirements-site.txt` only (venv at `<venv>`). Scripts as files, run by path. Never `-c` one-liners or heredocs into an interpreter. Never `sed -i` on tracked files. LF in the site output.
8. **Browser proofs.** Serve `docs/` on port `<port>`. Chrome rejects `file://`. Use the Playwright MCP tools already available. No global installs.
9. **Design.** Invoke `<design skill path>` if installed; record adopted and rejected guidance in `site/design-system/<product>/DECISIONS.md`. Tokens only. No external fonts, CDNs, analytics or embeds.
10. **Extend, never narrow.** If the work seems to require a product change, STOP and report.

## Verification bar (binding)

- `python scripts/build_site.py --check` exits 0 on a clean worktree at the head.
- Every gate passes: secret 0, placeholder 0, links, metadata, alt, JSON-LD, sitemap, og 1200×630, tokens, revision-2 minimums.
- Every page: one `h1`, unique title ≤ 60, unique description 120–160.
- Every page at 390 / 768 / 1440: no horizontal overflow, no console errors.
- Contrast: every pair computed; body 4.5:1, large 3:1, UI 3:1.
- Every screenshot reviewed; counts reconcile; originals unmodified.
- The claims ledger is complete and every evidence path exists.
- The local serve returns 200 for every page, asset, screenshot, sitemap, robots and `og.png`.

## Ship

1. Commit in logical steps, explicit paths, each message ending with `<attribution>`.
2. `git push -u origin <site-branch>`.
3. `gh pr create --repo <owner>/<repo> --base <base> --head <site-branch> --draft --title "<title>" --body-file <path>`.
4. Fill the PR body per `references/templates/PR-BODY.template.md`.
5. Stop. Do not merge.

## Progress

- `<worktree>/PROGRESS.md` and `<worktree>/HANDOFF.md` from the FIRST edit, kept current.
- Commit WIP early.
- Bounded loops only. No foreground sleep over ten minutes.

## Report (the final message IS the deliverable; partial is acceptable, silence is not)

1. Branch, head SHA, PR URL.
2. Files changed, grouped, with counts; the product-boundary output.
3. Page inventory: path, words, images, diagrams.
4. Screenshot pipeline numbers.
5. Gate results with real output.
6. Verification table with one line of evidence each.
7. Deviations from the spec, residual risks, what was not done.
8. Every directory left behind.
9. Lessons for the orchestrator (do not edit the tracking files).
