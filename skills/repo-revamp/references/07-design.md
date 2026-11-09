# 07 — Design: derived from the product, verified by measurement

The site must look like it belongs to the product, not like a template with the product's name dropped in. This file is the design process and its proof.

## The principle

**Derive, do not invent.** The product's own screenshots are the primary colour and typography source. The site borrows the product's palette, its density, its vocabulary and its motifs, then applies a stronger hierarchy and more whitespace than the product UI can afford.

## Step 1 — Sample the product

From the approved screenshots (not from the brand's marketing site, not from a palette generator):

- dominant background, surface, text and accent colours
- the accent used for status states (success, warning, error)
- the type feel: geometric, humanist, monospace-heavy
- the density: compact tables, generous cards, mixed
- the motifs: grids, port numbers, status dots, sidebars

Record the sampled hex values and the source image for each in `site/design-system/<product>/DECISIONS.md`.

## Step 2 — Run the design-intelligence tool when available

If the `ui-ux-pro-max` skill is installed, invoke it by its full path and read its `SKILL.md` before using the script. The process:

1. **Stack detection.** Plain HTML/CSS/vanilla JS has no framework and no Tailwind. Do **not** pass `--stack`. Use `--design-system` and `--domain` only. Record the decision.
2. **Design system.** Run once, persisting into `site/design-system/<product>/`:

```sh
python "<plugin-root>/scripts/search.py" "<generic product description>" \
  --design-system --persist -p "<Product>" --output-dir "<repo>/site" \
  --variance 6 --motion 3 --density 6
```

The query contains only generic product wording. Never private data, names, keys, URLs or internal terms.

3. **Read MASTER.md fully.** Verify each recommendation against the product's screenshots and the requirements. Record every adopted and rejected recommendation, with the reason, in `DECISIONS.md`.
4. **Domain searches**, one concern each: accessibility outcomes (`--domain ux`), icons (`--domain icons`), colour and contrast (`--domain color`), typography (`--domain typography`), landing structure (`--domain landing`), product structure (`--domain product`), style (`--domain style`). Confirm the returned domain and category match the question before applying anything.
5. **Per-page overrides** for home, features, architecture, gallery, quick start, FAQ, glossary: `--design-system --persist -p "<Product>" --output-dir "<repo>/site" --page "<page>"`. Overrides live in `pages/<page>.md` and override MASTER only where they say so.
6. **Tokens.** Write `site/design-tokens.json` so it exactly matches the adopted decisions. The builder reads it and emits CSS custom properties. Hard-coded hex in templates is forbidden.

If the tool is not installed, or its output is empty or off-topic, say so and use a hand-built system from the sampled product colours. Label it as a fallback. Never persist unverified output.

Motion: a GSAP snippet in the tool's output is reference, not code to ship. This site loads no external scripts. Use CSS transitions and keyframes only.

## Step 3 — The token file

```json
{
  "color": {
    "bg": "#0B0F14",
    "surface": "#111821",
    "surface-2": "#18212C",
    "text": "#E6EDF3",
    "text-muted": "#9FB0C0",
    "accent": "#3FB950",
    "accent-contrast": "#04130A",
    "border": "#6B7B92",
    "focus": "#58A6FF",
    "success": "#3FB950",
    "warning": "#D29922",
    "error": "#F85149"
  },
  "font": {
    "sans": "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
    "mono": "ui-monospace, SFMono-Regular, 'Cascadia Mono', Consolas, monospace"
  },
  "space": { "1": "4px", "2": "8px", "3": "12px", "4": "16px", "6": "24px", "8": "32px", "12": "48px", "16": "64px" },
  "radius": { "sm": "6px", "md": "10px", "lg": "16px" },
  "shadow": { "card": "0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.25)" },
  "motion": { "fast": "120ms", "base": "200ms", "ease": "cubic-bezier(.2,.7,.2,1)" },
  "focus": { "ring": "2px solid #58A6FF", "offset": "2px" }
}
```

Rules:

- Every colour used in the CSS comes from a token. The builder's token gate enforces it.
- Dark is the primary theme. Provide a light theme only if the product UI has one, derived from its screenshots.
- No external fonts. System stacks only.

## Step 4 — Contrast

Compute WCAG 2.2 AA contrast for every text/background pair and every UI component pair, with a short standard-library script. Record the table in `DECISIONS.md`.

Thresholds:

- body text 4.5:1
- large text (≥ 24 px, or ≥ 18.66 px bold) 3:1
- UI components and borders 3:1

Fix failures by changing the token, not by changing the threshold. The canonical failure: border tokens at 2.9:1 were replaced (`#6B7B92` dark, `#74879F` light) to reach 3.1:1.

## Step 5 — Layout and hierarchy

- **One `<h1>` per page.** Logical `<h2>`/`<h3>` order.
- **A skip link** as the first focusable element.
- **Landmarks:** `header`, `nav`, `main`, `footer`.
- **Breadcrumbs** on every non-home page.
- **A sticky table of contents** on every deep page, with the current section marked.
- **A consistent grid.** Define the max width and the gutters in tokens.
- **Density:** the product shape is dense; the site is calmer. More whitespace than the product, never less.
- **Cards** for hubs and feature grids; **prose columns** for deep pages; **figures** for diagrams.
- **A visible focus ring** on every interactive element.
- **44×44 CSS px minimum** touch targets.
- **No horizontal scroll at 360, 390, 768, 1024, 1280, 1440, 1920.**

## Step 6 — Motion

- Subtle, purposeful, CSS-only.
- Disabled or reduced to non-moving changes under `prefers-reduced-motion: reduce`.
- No hover scale transforms that shift layout.
- No autoplay media.
- No decorative glow, ticker or parallax effects unless the product itself uses them.

## Step 7 — The responsive matrix

Use the Playwright MCP tools already available. Do not install global packages.

Widths: 360, 390, 768, 1024, 1280, 1440, 1920.

For every page:

- no horizontal scroll at any width
- one `<h1>`
- landmarks present
- every image has a name or is decorative and hidden
- heading order is logical
- every link has descriptive text
- no console errors
- the gallery lazy-loads (scroll, wait, then count)

Screenshot at least 390, 768 and 1440 for every page and review them by eye.

## Step 8 — Accessibility tree

Use the accessibility snapshot on every page:

- every image has a meaningful name or is decorative and hidden
- every landmark is present
- heading order is logical
- every link has descriptive text
- every form control (if any) has a label

## Step 9 — Print

A print stylesheet for documentation pages: no navigation chrome, readable line length, links expanded where useful, page breaks before major headings.

## Step 10 — The identity

The site needs one idea a visitor remembers. Examples that worked:

- **control room** — port bands as stacked cards, a front-door diagram, a subtle grid, monospace port numbers
- **literary** — parchment and oxblood, a serif face, chapter-like navigation
- **audio studio** — waveform motifs, a dark console palette
- **atlas** — a map-like index, coordinate labels, a blueprint grid

The identity comes from the product's domain, not from a style catalogue. One motif, applied consistently, beats five effects.

## What the design must never do

- Copy another company's logo, brand mark or exact palette.
- Load an external font, CDN, analytics script or embed.
- Use a hard-coded colour outside the tokens.
- Use a generic "AI landing page" composition: a centred hero, three identical feature cards, a gradient blob, a testimonial nobody gave.
- Hide content behind JavaScript. The site reads without it.
- Use a carousel for anything essential.
- Put a search box on a static site that does not search.

## Exit gate

- `site/design-tokens.json` is valid JSON and every CSS colour comes from it.
- The contrast table is complete and every pair passes.
- The responsive matrix is complete with zero issues.
- The accessibility snapshot is clean on every page.
- The print stylesheet exists.
- `DECISIONS.md` records every adopted and rejected recommendation with its reason.
