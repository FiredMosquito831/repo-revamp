# 05 — Content truth: the claims ledger, sourcing and what never gets published

A site is a set of factual claims. This file is how each one earns its place.

## The sourcing hierarchy

When two sources disagree, the higher one wins:

1. **The code and the tests.** What the product actually does.
2. **The user-facing docs shipped with the product.** What the product says it does.
3. **The README.** What the project says about itself.
4. **The owner's brief.** What the owner wants said.
5. **Nothing else.** Not memory, not inference, not a plausible guess.

If the README and the code disagree, the README is wrong. Record the discrepancy in the report and describe only the verified behaviour on the site.

## The claims ledger

One row per factual statement that appears on the site. Opinions, navigation labels and calls to action are not claims.

```markdown
| # | Page | Claim (exact wording) | Evidence | Status |
|---|---|---|---|---|
| 1 | / | "Runs many local stacks behind one entry port" | README.md §"front door"; packages/supabase-wrapper/src/proxy.ts:41 | verified |
| 2 | /architecture/port-bands/ | "The allocator uses a block size of 11" | packages/supabase-wrapper/src/ports.ts:88 | verified |
| 3 | /features/backups/ | "Backups can be restored" | src/backup.ts:120; tests/backup.spec.ts:44 | verified |
| 4 | / | "Supports Windows, macOS and Linux" | package.json engines; CI matrix | verified |
| 5 | /features/edge-functions/ | (cut) | no approved screenshot and no verified UI | removed |
```

Rules:

- **Exact wording.** The ledger quotes the site, not a paraphrase.
- **Evidence is a path with a line, a doc section, or a command with its output.** "The code" is not evidence.
- **Status is `verified` or `removed`.** A removed claim stays in the ledger with the reason.
- **Every number is recomputed or recorded.** Ports, counts, versions, file counts, table counts, word counts.
- **The ledger lives outside the repository** (`_revamp/<repo>/CLAIMS.md`). It is internal.
- **The builder can enforce it:** each page's content file carries a `claims` list; the builder fails if a page has a claim without evidence. The ledger is generated from those lists.

## Numbers

A number on the site must be one of:

1. **Computed at build time** from the source (the version from the manifest, the count of config keys from the schema, the number of providers from the data file).
2. **Verified by hand and recorded** in the ledger with the command that produced it.

Never:

- a number copied from an old README without re-checking;
- a rounded or "about" number presented as exact;
- a count that will drift (write the builder to read it instead);
- a fabricated zero ("0 known issues").

The canonical failure: a site claimed "21 tables" when the schema had 12. It was caught in review and fixed. Every number gets the same treatment.

## The forbidden strings

The build fails on any of these in `site/` or `docs/`:

```text
TODO  TBD  lorem  YOUR_  placeholder  XXX  example.com  coming soon  [insert  FIXME
```

If a sentence legitimately needs one of these words, rewrite the sentence.

## What never gets published

Regardless of how interesting it is:

- **Security audit findings, reports or summaries.** Not even "we fixed X".
- **Verification logs, scenario files, agent prompts, internal planning.**
- **Known bugs and open issues**, unless the owner explicitly wants a public roadmap.
- **The internal process used to build the product**, beyond an honest "how this got built" narrative the owner already wrote.
- **The repository's own `.claude/` configuration.**
- **Real credentials, tokens, keys, connection strings, private IPs, owner file paths, email addresses.**
- **Third-party personal data** in screenshots or examples.
- **Customer or user records** of any kind.
- **Internal file names that leak the process** (`vfy491`, `verify-808-live`, `feature-114-conflict-modal`). Derivatives get descriptive slugs.

The public surface is the curated user guide. Everything else is a source, not a publication.

## The secret scan

The builder scans every text file. The rules:

- **Zero hits is the only pass.**
- **Report file and line, never the value.**
- **Scan the rendered output, the manifest and the alt text.**
- **A real-looking secret is a stop-the-line event:** report the location and the variable name only, stop publishing work that depends on it, hand it to the owner.

Patterns are in `04-builder.md` §the secret scan.

## `.env.example` handling

Read the file for **names only**. For each variable, check whether its value is a placeholder:

- empty
- `change-me`, `changeme`, `replace-me`
- `your-...`
- angle-bracket forms `<...>`
- obvious dummy text

Record the verdict per variable. If a value looks real:

- do **not** print it;
- report file, line and variable name with the verdict "non-placeholder-looking value present";
- stop any publication that depends on it;
- hand it to the owner.

On the public configuration page: **names and purposes only.** Never an example value, not even a placeholder, for a secret-like variable.

## Legal and brand texts

These are quoted verbatim wherever they apply. Store them once in `site/content/site.json` and render them from there.

**Non-affiliation** (when the product name contains someone else's mark):

> <Product> is an independent project. It is not affiliated with, endorsed by, or sponsored by <Company>. <Mark> is a trademark of its owner.

**Licence:**

> Licensed under the <licence name> (<SPDX identifier>).

**Early access** (when the source is private):

> The source code is in early access and currently private. Request access to get involved.

**Trademarks:** never use another company's logo or brand artwork. Plain-text references are fine.

**Call to action:** a real contact channel. The owner's GitHub profile is the default. Never invent an email address.

## Tone

- Direct, technical, honest, warm.
- Short sentences. One idea each.
- Say what it does and how to run it.
- No hype words: revolutionary, game-changing, best, ultimate, seamless, cutting-edge, blazing.
- Define jargon once on first use ("port band", "front door").
- Prefer concrete numbers when verified; omit them when not.

## The discrepancy log

Every place the sources disagree goes in the report and, where it affects a page, in the spec:

| Discrepancy | Sources | What the site says |
|---|---|---|
| Documented `PORT_BLOCK_SIZE=10`; allocator uses 11 | `.env.example` vs `ports.ts:88` | 11 everywhere; the configuration page explains the discrepancy |

Never silently pick one. Never publish both as if both were true.

## Exit gate

- Every page's `claims` list is complete; the ledger has a row per claim.
- Every number is computed or recorded with its command.
- The secret scan is zero.
- The placeholder scan is zero.
- The legal texts appear verbatim on every page footer and on `/license/`.
- The discrepancy log is in the report.
