# STATE — <repo>

Updated at every phase boundary. A fresh session reads this first.

## Identity

- Repository: `<owner>/<repo>`
- Visibility: `<public | private>`
- Default branch: `<branch>` at `<sha>`
- Site branch: `<branch>` at `<sha>`
- Base SHA for the boundary diff: `<sha>`
- Host: `<GitHub Pages | Cloudflare Pages>`
- Subdomain: `<sub>.<zone>`
- Live URL: `<url>`
- Shape: `<product | docs | research>`
- Mode: `<presentation-only | rebuild>`

## Phase

- Current phase: `<0 INTAKE | 1 SPEC | 2 BUILD | 3 REVIEW | 4 DEPLOY | 5 SEO | 6 SHIP | 7 CLOSE>`
- Started: `<date>`
- Last updated: `<date time>`

## Gates

| Gate | State | Evidence |
|---|---|---|
| Recon complete | `<pass / fail / pending>` | `RECON.md` |
| Spec approved | `<pass / fail / pending>` | `SPEC.md` USER DECISIONS |
| Builder `--check` | `<pass / fail / pending>` | `<command output>` |
| Product boundary empty | `<pass / fail / pending>` | `<diff output>` |
| Secret scan zero | `<pass / fail / pending>` | `<output>` |
| Placeholder scan zero | `<pass / fail / pending>` | `<output>` |
| Claims ledger complete | `<pass / fail / pending>` | `<row count>` |
| Screenshots reviewed | `<pass / fail / pending>` | `<counts>` |
| Responsive matrix | `<pass / fail / pending>` | `<widths>` |
| Live URLs 200 | `<pass / fail / pending>` | `<count>` |
| Served commit matches | `<pass / fail / pending>` | `<sha>` |
| Sitemap submitted | `<pass / fail / pending>` | `<response>` |

## Open questions for the owner

1. `<question>` — Rec: `<recommendation>`

## Agents

| Agent | Worktree | Branch | Started | Status | HANDOFF |
|---|---|---|---|---|---|

## Leftovers

- `<path>` — `<what it is>`

## Next action

`<one sentence>`
