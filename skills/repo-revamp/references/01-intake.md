# 01 — INTAKE: read-only recon

Phase 0. Nothing is written to the repository in this phase. The output is `_revamp/<repo>/RECON.md` and a proposed spec.

The rule that matters: **understand the product before touching it.** Every invented claim, every wrong page and every reverted PR in this playbook traces back to skipping a step here.

## 1. Locate and anchor

```sh
gh repo view <owner>/<repo> --json name,visibility,defaultBranchRef,description,homepageUrl,licenseInfo,isArchived,isFork
gh repo list <owner> --limit 100 --json name,visibility,defaultBranchRef
```

Record:

- visibility (public / private)
- default branch (never assume `main`; `master` is common)
- archived or fork status (stop if archived)
- licence as GitHub detects it, and the licence in the manifest (they disagree often)
- description and homepage as they are today
- size: `git ls-files | wc -l`, and the count of tracked images

## 2. Read the repository

Read, in this order:

1. `README.md` (root) — the product's own words.
2. Every other README and every file under `docs/` that is not generated output.
3. The manifest(s): `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `composer.json`, `*.csproj`, `Makefile`.
4. The CI workflows under `.github/workflows/`.
5. The test tree: names and descriptions, not every line.
6. The source tree: entry points, routes, UI pages, CLI commands, config schema.
7. `.env.example` or equivalent — **names only**, never values.

What you are building is an inventory, not an opinion. Write down what exists.

## 3. Run the product's own checks

```sh
# adapt to the stack
npm test          # or pytest, cargo test, go test ./...
npm run lint
npm run build
```

Record the exact command and the real result. If the suite cannot run (missing service, missing credentials, platform-specific), record why. **A suite that does not run is a finding**, not a reason to skip the step: it belongs in the spec as a question ("the tests need Docker; should the site claim the project is tested?").

Never "fix" a failing test in INTAKE. Record it.

## 4. Build the feature inventory

A feature is something the product actually does. For each, record:

| Field | Source |
|---|---|
| Name (user-facing) | README, UI labels, CLI help |
| What it does | code path + user docs |
| Where it appears | route, menu, command, screen |
| Evidence | `file:line` or doc section |
| Status | shipped / partial / planned |
| Screenshot available | yes (path) / no |

Methods that work:

- **Routes:** grep the router for path definitions. Every route is a screen.
- **CLI:** run `--help` and read the command table.
- **UI:** list the page components and their headings.
- **Tests:** a test file named after a feature is evidence the feature exists; read its assertions to learn the behaviour.
- **Docs:** the user-facing docs are the best source of the *words* the product uses.
- **Schema:** a config schema or settings table is the best source of the configuration page.

Rules:

- A feature that is planned or partial is labelled as such on the site, or omitted. Never presented as shipped.
- A feature with no verified behaviour is not a page.
- A feature with no screenshot may still be a page if the code proves it; it just shows no image slot (never a placeholder).
- Internal audit files, verification logs, scenario files and agent prompts are **not** feature sources for publication. They may be read to cross-check completeness, never quoted or linked.

## 5. Build the configuration inventory

From `.env.example`, config schemas, settings tables and code reads:

| Variable / setting | Purpose | Required or optional | Where read | Secret-like |
|---|---|---|---|---|

Rules:

- **Names only.** Never publish a value, not even a placeholder, for a secret-like variable.
- Verify "required or optional" against the code, not the comment.
- If the example file and the code disagree (a documented default the code does not read), record the discrepancy. It becomes a site fact and a spec question.

## 6. Inventory the screenshots

```sh
git ls-files | grep -iE '\.(png|jpe?g|webp|gif|svg)$' | wc -l
git ls-files | grep -iE '\.(png|jpe?g|webp|gif|svg)$' | sed 's#/[^/]*$##' | sort | uniq -c | sort -rn | head -30
```

Record:

- total tracked images
- the top folders they live in
- which folders are product UI captures, which are docs/diagrams, which are internal (exclude)
- whether the repository has a QA/verification capture set (often the richest source)
- whether any are obviously sensitive (settings pages with keys)

Do not open images yet. That is phase 2 (`06-screenshots.md`).

## 7. Decide the site shape

| Signal | Shape |
|---|---|
| The repo is an app or tool with a UI | product site |
| The repo is a library, CLI, schema or spec | docs site |
| The repo is a dataset, atlas, list or study | research/data site |
| The repo is a config manager with hundreds of keys | docs site with a generated explorer |
| The repo has both a UI and a large config surface | product site with a configuration hub |

The shape decides the page inventory (`03-build.md`).

## 8. Decide the hosting

| Condition | Host |
|---|---|
| Repository is public | GitHub Pages from `<default-branch>:/docs` |
| Repository is private, site must be public | Cloudflare Pages from the site branch, output `docs` |
| Repository is public but needs preview deployments per PR | Cloudflare Pages |
| Repository is public and the owner wants Cloudflare | Cloudflare Pages |
| The site needs headers, redirects or a build step | Cloudflare Pages |
| No owner control of DNS | GitHub Pages with the `github.io` URL, or ask |

Key difference to state in the spec:

- **GitHub Pages custom domain:** the DNS record is a CNAME to `<owner>.github.io`, **DNS-only (grey cloud)**. Proxying GitHub Pages causes HTTPS problems.
- **Cloudflare Pages custom domain:** the record is created by Cloudflare and is **proxied (orange cloud)**. Do not switch it to DNS-only.

## 9. Propose the subdomain and the site name

Apply `00-project-profile.md` §subdomain rules. Check availability:

```sh
dig +short <sub>.<zone>
```

Record the proposed subdomain and one alternative.

## 10. Risk assessment

Before writing the spec, list:

- **Sensitive content:** does the repo contain real credentials, personal data, customer records, internal audit findings? (This drives the secret scan and the forbidden-reads list.)
- **Licence risk:** does the manifest licence match the LICENSE file? Are there third-party assets that cannot be republished?
- **Trademark risk:** does the product name contain someone else's mark? (Needs a non-affiliation statement.)
- **Platform claims:** which platforms are actually supported, per `engines`, scripts and CI? Never claim all three by default.
- **Legal text:** is there an existing non-affiliation or licence statement that must be preserved verbatim?
- **Private-repo constraints:** if private, what may be published (curated user guide only) and what must never be (audit, verification, scenarios, prompts, internal planning)?

## 11. Write RECON.md

Structure:

```markdown
# RECON — <repo> (<date>)

## Facts
- visibility, default branch, licence, size, stack, platforms

## What the product is (three sentences, from its own README)

## Feature inventory
| Feature | What it does | Where | Evidence | Status | Screenshot |

## Configuration inventory
| Name | Purpose | Required | Where read | Secret-like |

## Screenshot sources
- counts by folder, which are usable, which are excluded

## Checks run
- exact commands and results

## Risks
- sensitive content, licence, trademark, platform claims

## Proposed shape, host, subdomain

## Questions for the spec
- the numbered questions this recon raises
```

## Exit gate

- RECON.md exists and every section is filled.
- The feature inventory has evidence for every row.
- The hosting decision is stated with its reason.
- The subdomain is checked.
- No file in the repository has been modified. Verify: `git status --porcelain` is empty.
