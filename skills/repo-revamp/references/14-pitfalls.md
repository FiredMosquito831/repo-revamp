# 14 — Pitfalls: every trap that bit, with its fix

Each row is a real failure from this playbook. Read this file when something looks wrong.

## Build and determinism

| Symptom | Cause | Fix |
|---|---|---|
| `--check` reports differences on every page | the sitemap `lastmod` is read from git history | a fixed value in `site/content/site.json` |
| `--check` reports differences on every text file | CRLF from `core.autocrlf=true` | run the check in a worktree created with `-c core.autocrlf=false`; never change the shared config |
| `--check` reports differences in assets only | the asset is git-ignored and was never committed | `git check-ignore -v <path>`; add a `!` exception |
| `--check` passes locally, fails in CI | a different Python or Jinja2 version | pin exact versions in `requirements-site.txt` |
| The build changes between two days | a wall clock or a random id | remove it; sort every list |
| The builder writes outside `docs/` | a path bug | the builder owns `docs/` only; assert it |

## Git and line endings

| Symptom | Cause | Fix |
|---|---|---|
| A worktree appears in the wrong place | a relative path after `git -C` | absolute worktree paths |
| "284 files with CR" | the count included binary images | count text files only |
| A generated file is not in the commit | `.gitignore` has `*.png` | `!docs/og.png`, `!site/static/og.png` |
| A merge happened before the go | no gate on the merge | revert with `-m 1`, no force; record the lesson |
| The PR contains a product change | a broad `git add` | explicit paths; the boundary filter |

## Screenshots

| Symptom | Cause | Fix |
|---|---|---|
| Lazy-loaded images look broken | the screenshot was taken before scrolling | scroll, wait, then judge |
| A screenshot leaks an email | it was not reviewed at full size | review every candidate; redact on a copy |
| The gallery has near-duplicates | only SHA dedupe was run | pHash clustering at distance ≤ 4 |
| An original image is modified | the derivative overwrote it | derivatives are new files; originals read-only |
| A caption describes data that is not there | an empty state captioned as a populated one | correct the caption |

## Content

| Symptom | Cause | Fix |
|---|---|---|
| An invented number ships | it was copied from an old README | recompute at build time or record the command |
| The build fails on "placeholder" | the word appears legitimately | rewrite the sentence |
| A page is thin | it was padded | cut it or fold it into a parent |
| A feature is claimed but does not exist | it was inferred | code or tests prove it, or it is not published |
| The FAQ JSON-LD and the page disagree | two sources | generate both from one array |

## Design and accessibility

| Symptom | Cause | Fix |
|---|---|---|
| Contrast fails on borders | the border token is too light | change the token, not the threshold |
| Horizontal scroll at 390 | a fixed width or a wide table | fluid layout; test at 390 |
| Focus is invisible | no focus style | a visible ring from the focus token |
| Motion ignores the preference | no `prefers-reduced-motion` rule | disable or reduce |
| A hard-coded colour | a template bypassed the tokens | the token gate |

## Deployment

| Symptom | Cause | Fix |
|---|---|---|
| `og.png` 404 live | it was git-ignored | commit it; verify |
| Certificate stuck on `none` | the site predates DNS | clear the cname, wait, re-add |
| "The certificate does not exist yet" | HTTPS enforced too early | wait for `approved` |
| Pages serves an old commit | no rebuild | `POST /pages/builds`, poll the commit |
| HTTPS fails on GitHub Pages | the CNAME is proxied | DNS-only |
| Cloudflare Pages domain fails | the record is DNS-only | leave it proxied |
| `*.pages.dev` does not resolve | project URL or DNS | check the dashboard; cosmetic |
| A private repo's CI never starts | account billing | run the gate locally; record it |

## Agents

| Symptom | Cause | Fix |
|---|---|---|
| Resume fails | "No assistant messages found" | a fresh agent with the complete brief |
| An agent claims a skill it did not load | it used a checklist | require the path it read |
| An agent read the repo's `.claude/` | discovery picked it up | name the plugin-cache copies only |
| An agent merges | the brief did not forbid it | forbid it explicitly; revert if it happened |
| An agent leaves servers running | no cleanup step | list PIDs; stop only what it started |
| An agent's "unchanged" claim | no before and after | require the diff |

## Process

| Symptom | Cause | Fix |
|---|---|---|
| A PR has to be reverted | the spec was skipped | recon and spec first |
| The owner is surprised by a domain | it was not in the spec | every domain in the decisions block |
| The same question is asked twice | the standing decisions were not recorded | the profile and the decisions block |
| Work is lost at a pause | no handoff | write it before pausing |
| A lesson is forgotten | written from memory at the end | write it at the moment it is learned |
