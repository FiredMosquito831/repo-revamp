# Design decisions — repo-revamp

Source of truth: `site/design-system/repo-revamp/MASTER.md` (the ui-ux-pro-max output,
persisted once with `--design-system --persist` and no `--stack`). The page overrides folder
is empty; this record is the adopted-and-rejected log.

## Stack decision

Plain HTML/CSS/vanilla JS with no framework and no Tailwind, so no `--stack` was passed.
The site loads no external fonts, CDNs, analytics or embeds.

## Adopted

- The FAQ/Documentation landing pattern: a documentation site with a hub of cards and an FAQ.
- The Minimalism and Swiss style: grid-based, high-contrast, geometric sans, generous space.
- Subtle hover states in the 150 to 300 millisecond band, with reduced-motion respected.
- The pre-delivery checklist: no emoji icons, visible focus, 4.5:1 body contrast, 44px targets,
  and a responsive matrix at 375, 768, 1024 and 1440.
- The idea of a visible legend on every diagram.

## Rejected

- The tool's exact palette (a slate/navy set). The site instead uses the brief's tokens,
  which are sampled from the plugin's own icon. The colours are a darker, greener set and pass
  contrast at the same thresholds.
- The recommended Google Fonts pairing (JetBrains Mono, IBM Plex Sans). No external fonts; the
  system stacks in the tokens carry the same intent: monospace identifiers and a system sans.
- The GSAP scroll-reveal snippet. No external scripts; motion is CSS transitions only.
- The anti-pattern list (buried endpoints, broken version switching, missing rate-limit state)
  does not apply: the site has no API surface.
- The persisted MASTER.md still quotes a Google Fonts URL. It stays as the tool's raw output in
  the internal design-system record; the site itself makes no such request.

## Identity

The control room for a revamp: a phase rail, gate cards with status dots, monospace
identifiers and a subtle grid. Dark first, system fonts only.

## Contrast (WCAG 2.2 AA, every final token pair)

| Pair | Ratio | Minimum | Note | Verdict |
|---|---|---|---|---|
| text on bg | 16.27:1 | 4.5:1 | Body text on the page background. | pass |
| text-muted on bg | 8.64:1 | 4.5:1 | Muted text on the page background. | pass |
| accent on bg | 7.57:1 | 4.5:1 | Accent text on the page background. | pass |
| focus on bg | 7.61:1 | 4.5:1 | Focus-blue text on the page background. | pass |
| success on bg | 7.57:1 | 4.5:1 | Success text on the page background. | pass |
| warning on bg | 7.61:1 | 4.5:1 | Warning text on the page background. | pass |
| error on bg | 5.73:1 | 4.5:1 | Error text on the page background. | pass |
| text on surface | 15.11:1 | 4.5:1 | Body text on a card surface. | pass |
| text-muted on surface | 8.03:1 | 4.5:1 | Muted text on a card surface. | pass |
| accent on surface | 7.03:1 | 4.5:1 | Accent text on a card surface. | pass |
| error on surface | 5.32:1 | 4.5:1 | Error text on a card surface. | pass |
| text on surface-2 | 13.75:1 | 4.5:1 | Body text on the secondary surface. | pass |
| text-muted on surface-2 | 7.31:1 | 4.5:1 | Muted text on the secondary surface. | pass |
| accent on surface-2 | 6.39:1 | 4.5:1 | Accent text on the secondary surface. | pass |
| accent-contrast on accent | 7.50:1 | 4.5:1 | Accent-contrast text on the accent fill. | pass |
| border on bg | 4.46:1 | 3.0:1 | Border lines against the page background. | pass |
| border on surface | 4.14:1 | 3.0:1 | Border lines against a card surface. | pass |
| border on surface-2 | 3.77:1 | 3.0:1 | Border lines against the secondary surface. | pass |
| focus on bg | 7.61:1 | 3.0:1 | Focus ring against the page background. | pass |
| accent on bg | 7.57:1 | 3.0:1 | Accent status dots against the page background. | pass |

Lowest body-text pair: 5.32:1. Lowest UI pair: 3.77:1. Every pair passes.

