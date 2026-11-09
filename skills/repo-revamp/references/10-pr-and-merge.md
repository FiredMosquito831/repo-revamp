# 10 — PR, merge and the revert

The site ships as a pull request. This file is the commit shape, the PR body, the merge discipline and the recovery if something goes wrong.

## The branch

- One branch per revamp: `revamp` (or the repository's existing site branch).
- Base: the default branch, unless the spec says the site launches from the branch itself.
- Worktree: absolute path, never the primary checkout.

## Commits

**One commit per logical family**, so a reviewer can follow the work:

1. the builder, the requirements file and the CI workflow
2. the tokens, templates and CSS
3. the content data, page by page family
4. the screenshots and the manifest
5. the diagrams
6. the SEO assets (`og.png`, favicon, sitemap inputs)
7. the README and docs index
8. the final gate fixes

**Message shape:**

```
<type>: <what changed>

<what was missing or broken> → <the mechanism, the cause>
<what the change does and any non-obvious choice>
<verification: the exact command and its real result>
<what was deliberately not done>

by <attribution>
```

Types: `docs:`, `site:`, `build:`, `chore:`.

Rules:

- **Stage explicit paths.** Never `git add -A`, never `git add .`.
- **Never commit** a database, a log, a scratch file, a venv, a `.env`, or a screenshot that did not pass review.
- **Never commit** anything under `_revamp/` or `_tmp/`.
- **Every commit ends with the attribution line.**

## Before every commit

```sh
git status --porcelain
git diff --name-only
```

Every changed path must match the spec's allowed list. Anything else: unstage and fix.

## The product-boundary check

```sh
git diff --name-only <base>...HEAD \
  | grep -vE '^(site/|docs/|scripts/build_site\.py$|requirements-site\.txt$|\.github/workflows/site\.yml$|README\.md$|\.gitignore$)'
```

Must print nothing. If it prints a product path, the PR is out of scope.

Also confirm no existing image changed:

```sh
git diff --name-status <base>...HEAD | grep -E '^M'
```

The only modified files should be the READMEs and `.gitignore`.

## The PR body

Use `references/templates/PR-BODY.template.md`. Sections, in order:

1. **Title** — specific, not "Revamp".
2. **Summary** — three sentences: what the PR adds, what it does not change, how it was verified.
3. **What changed** — a table: folder, file count, what.
4. **What did not change** — the product paths, the existing docs, the licence, the settings.
5. **Page inventory** — every page, word count, image count, diagram count.
6. **Diagram inventory** — every SVG and where it renders.
7. **Design decisions** — adopted and rejected, with reasons; the contrast summary.
8. **Screenshot pipeline numbers** — inventory, duplicates, reviewed, included, redacted, excluded by reason, gallery size, total size.
9. **Verification** — the V-table with one line of evidence each.
10. **Content cut or not verified** — what was removed and why.
11. **Owner-only steps** — the exact dashboard steps, verbatim.
12. **Residual risks** — always present; "none" if none.
13. **Attribution** — the final line.

Rules:

- **Real output in fenced blocks**, not descriptions.
- **Never claim verification beyond what ran.**
- **No secrets, no internal file names, no audit references.**
- **The owner-only steps are copy-paste ready.**

## Opening the PR

```sh
git push -u origin revamp
gh pr create --repo <owner>/<repo> --base <default> --head revamp \
  --title "<specific title>" --body-file <path under _revamp>
```

Open it as a **draft** as soon as the code is frozen, so CI runs while the proofs are finished. Mark it ready when the body is complete.

## CI

- Read every check's conclusion by name. Never trust a `--watch` return.
- A cancelled job with no FAILED lines is a runner hang: rerun it.
- A private repository's Actions can be blocked by billing. Record the message, run the gate locally, and say so in the PR body. Do not weaken the gate.
- Merge only on green **on the final commit**.

## The merge

**Only on the owner's explicit go.**

```sh
gh pr merge <n> --repo <owner>/<repo> --merge \
  --subject "<subject>" --body "<body ending with the attribution>"
```

- Prefer `--merge` (a merge commit) over squash when the branch history is part of the presentation.
- Delete nothing. **Retain the site branch.**
- Never force-push. Never rewrite history.

## After the merge

1. Sync the local default branch.
2. If Pages serves the default branch, repoint it and force a rebuild.
3. Poll `builds/latest.commit` until it equals the default branch head.
4. Verify the live site again.
5. Keep the site branch.

## If the merge was wrong: the revert

If a merge happened before the owner's go, or the PR was wrong:

```sh
git -C <checkout> checkout <default>
git -C <checkout> pull --ff-only
git -C <checkout> revert -m 1 <merge-sha> --no-edit
git -C <checkout> push
```

Rules:

- **`-m 1`** reverts the merge relative to the first parent (the default branch).
- **No force push.** The revert is a new commit.
- **Before reverting**, save the work: a patch of the full diff and a content-only patch, under the scratch tree.
- **After reverting**, verify the default branch is back to its pre-merge tree:

```sh
git -C <checkout> diff <pre-merge-sha> <default> --stat
```

- The site branch stays. The work is not lost.

## The launch-branch posture

When the owner wants presentation isolation:

- the site launches from `revamp` (Cloudflare Pages production branch, or a Pages source pointing at it);
- nothing merges to the default branch;
- the default branch keeps the product exactly as it was;
- the site branch is the presentation artifact and is retained indefinitely;
- any future site change goes on the same branch and redeploys.

Record this posture in the spec and the tracker. Never "tidy up" by merging it later without a new decision.

## Exit gate

- The PR exists with the full body and the attribution.
- CI is green on the final commit (or the local gate is recorded with the reason).
- The product-boundary diff is empty.
- The owner said merge (or the launch-branch posture is recorded and the owner approved it).
- After the merge: the served commit equals the new head; the branch is retained; the live site is verified.
