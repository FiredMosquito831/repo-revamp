# 15 — Private repositories: a public site without publishing the source

The repository stays private. The site is public. That combination has its own rules.

## What changes

| Topic | Public repo | Private repo |
|---|---|---|
| Host | GitHub Pages | Cloudflare Pages (GitHub Pages needs a paid plan for private repos) |
| Repository link on the site | allowed | **never** — no link, no clone command that points at it |
| Install instructions | real clone command | "request access" or a public mirror if one exists |
| Docs published | the user guide | a **curated** user guide only |
| Source of screenshots | the repo | the repo, reviewed and redacted |
| CI | Actions | Actions may be billing-blocked; the local gate is the gate |
| Search indexing | index now | index now, unless the owner says otherwise |

## What may be published

- The product name, the value proposition, the verified feature descriptions.
- The curated user guide, rewritten for readers, derived from the internal docs.
- Screenshots that passed review.
- The licence and the third-party attributions.
- The non-affiliation statement.
- A real contact channel (the owner's GitHub profile).

## What must never be published

- The repository URL, the clone command, the package registry link (if private).
- Internal audit, verification, scenario, prompt or planning material.
- Known bugs, open issues, internal roadmaps.
- File names that leak the process.
- Any secret, path, email or project reference.
- The internal docs verbatim. They are sources, not publications.

## The curated guide

The internal docs are often tens of thousands of words written for the maintainer. The public guide is:

- written for a user who has never seen the code;
- organised by task, not by module;
- stripped of internal references, audit notes and implementation detail that is not user-facing;
- verified against the code, not copied from the docs.

If the internal docs and the code disagree, the code wins and the discrepancy is recorded.

## The early-access framing

When the source is private and there is no public release:

> The source code is in early access and currently private. Request access to get involved.

Use it wherever the product is described for visitors. The CTA points at a real channel.

## The secret scan is stricter

- Zero hits, no allowlist.
- Scan the rendered output, the manifest, the alt text and the captions.
- A real-looking secret is a stop-the-line event: report the location and the variable name only.

## The forbidden reads

Name them in the spec and the brief:

- databases, logs, `.env` values, raw response dumps;
- the internal audit, verification, scenario and prompt folders;
- the repository's own `.claude/` configuration;
- any file that is not needed to describe the product.

The agent may read the product source, the user docs, the manifests and the tests. Nothing else without a reason in the spec.

## The Cloudflare Pages flow

1. The owner authorises the Cloudflare GitHub App for the private repository (owner-only).
2. The project is created with the settings in `09-deployment.md`.
3. The production branch is the site branch (often `revamp`), so the site is isolated.
4. The custom domain is attached; the record is proxied.
5. The site is verified.

## The isolation posture

When the owner wants the site to launch without merging:

- the site branch is the production branch;
- the default branch keeps the product exactly as it was;
- the site branch is retained;
- any future site change goes on the same branch and redeploys.

Record it in the spec. Never merge it later without a new decision.

## Exit gate

- No repository link or clone command appears anywhere in the output.
- No internal material appears anywhere in the output.
- The secret scan is zero.
- The curated guide is verified against the code.
- The early-access framing and the non-affiliation text are on every page.
- The deployment is from the site branch, with the owner's approval.
