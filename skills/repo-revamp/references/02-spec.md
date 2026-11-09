# 02 — SPEC: the numbered questions and the binding decisions

Phase 1. The spec is how a revamp stops being the orchestrator's guess and becomes the owner's decision.

## Why it exists

A revamp touches things the owner cares about: the product's public face, a domain, a repository's settings, and sometimes its visibility. The spec makes every one of those an explicit, dated decision before any agent is dispatched. It also gives the implementing agent a document to be held to.

The failure it prevents: a PR that is technically good and has to be reverted because it answered a question nobody asked.

## Structure

```markdown
# SPEC — <product>: <what this job is>

Status: <draft | approved by the owner on YYYY-MM-DD>
This document is the single source of truth for the job. Read it end to end before running any command. Where this spec and a habit conflict, this spec wins. Where this spec is silent and the risk is real, stop and report instead of guessing.

## 0. The owner's decisions (verbatim intent)
| Topic | Decision |

## 1. Mission and success criteria
## 2. Hard rules (R1..Rn)
## 3. Repository facts (verify again; do not trust blindly)
## 4. Allowed and forbidden paths
## 5. Secrets and privacy
## 6. Naming, legal and tone
## 7. Site architecture
## 8. Content sourcing rules
## 9. Claims ledger
## 10. Screenshot pipeline
## 11. Design system
## 12. Build system contract
## 13. SEO specification
## 14. Accessibility and performance budgets
## 15. Deployment
## 16. Git and pull request workflow
## 17. Verification checklist
## 18. Surprises and judgement calls
## 19. Final report

## QUESTIONS FOR THE OWNER
1. ...
```

`references/templates/SPEC.template.md` is the fill-in version.

## The questions

### Rules

1. **Numbered, plain language, one decision each.** The owner answers in one line ("all rec", "1 yes / 2 whatever is correct").
2. **Every question carries a recommendation.** "Rec: Cloudflare Pages, because the repo is private and GitHub Pages on a private repo requires a paid plan."
3. **Only ask what the owner can see or decide.** Never ask which CSS technique to use. Ask whether the site should show the private repo link.
4. **Never relay an agent's question unchecked.** Rephrase it into a decision.
5. **Ask before dispatch, not after.** A question that arrives after the build is a rework.
6. **Ten questions is a lot.** Most revamps need five to eight. Group the trivial ones under "all rec".

### The questions almost every revamp needs

1. **Hosting.** GitHub Pages or Cloudflare Pages? (Rec depends on visibility and preview needs.)
2. **Domain.** Which subdomain? (Rec: the keyword-rich one, checked free.)
3. **Visibility.** Does the repository stay as it is? If private, what may be published? (Rec: unchanged; curated user guide only.)
4. **Scope.** Presentation only, or may the product itself be rebuilt? (Rec: presentation only.)
5. **Indexing.** Index now, or noindex until launch? (Rec: index now.)
6. **Screenshots.** May QA/verification captures be used, with redaction? (Rec: yes, both sources, every candidate reviewed.)
7. **Call to action.** Where should the early-access or contact button point? (Rec: the owner's GitHub profile; never invent an email.)
8. **Merge.** Merge after verification, or keep the branch as the launch source? (Rec: keep the branch until the owner says merge.)
9. **Existing docs.** May the README and docs index be rewritten, and what must be preserved verbatim? (Rec: presentation layer only; keep the honest narrative, licence and contributing sections.)
10. **Anything the recon found.** The licence mismatch, the failing suite, the documented default the code ignores. Each becomes a question with a recommendation.

## The USER DECISIONS block

After the owner answers, append to the spec, verbatim:

```markdown
## USER DECISIONS (2026-10-23 21:40, binding)

> all rec

1. Hosting: Cloudflare Pages. The repository stays private.
2. Domain: supabasedatabasemanager.danubelabs.net.
3. Visibility: unchanged (private). Publish the curated user guide only.
4. Scope: presentation only. Product code frozen.
5. Indexing: index now.
6. Screenshots: both sources, every candidate reviewed, redact on copies.
7. CTA: https://github.com/FiredMosquito831.
8. Merge: no merge. The site launches from `revamp`.
9. Docs: presentation layer only; keep the honest narrative, licence and contributing sections.
10. Licence: state GPL-3.0-or-later, consistent with package.json.
```

Rules for the block:

- **The owner's words first, verbatim**, even if they are "all rec".
- **Then each resolved decision**, one line, unambiguous.
- **Timestamp it.** Local time with the offset.
- **Only the orchestrator writes it.** Never an agent.
- **It is binding.** An agent that disagrees reports; it does not deviate.

## Change control

- A new question after approval goes into a **new dated block**, not an edit to the old one.
- A decision the owner reverses is recorded as a reversal with its date and reason. The old line stays.
- If the owner's answer contradicts a hard rule (for example "publish the audit findings"), say so and ask again. Do not silently comply and do not silently refuse.

## What the spec must pin down

Every spec, regardless of shape, must state:

- the exact allowed paths and the exact forbidden paths
- the hard rules, numbered, with "violating any of these is a stop-and-report event"
- the site architecture with per-page word targets
- the content sourcing rules (what may be read, what may be published)
- the claims ledger location and format
- the screenshot pipeline and its budgets
- the design constraints (derived from the product, no external requests, contrast)
- the builder contract and its gates
- the SEO requirements per page
- the deployment steps, split into agent-doable and owner-only
- the git workflow and the PR body contents
- the verification checklist, numbered
- the report format

## Exit gate

- The spec file exists and every section is filled.
- The questions are numbered and each has a recommendation.
- The owner has answered.
- The `USER DECISIONS` block is appended, verbatim, timestamped.
- No agent has been dispatched.
