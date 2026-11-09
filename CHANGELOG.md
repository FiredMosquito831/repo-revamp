# Changelog

All notable changes to this plugin are recorded here. The format follows Keep a Changelog; the project uses semantic versioning.

## [1.0.0] — 2026-11-10

### Added

- The `repo-revamp` skill: the complete playbook for turning a repository into a live, verified, search-indexed site.
- The phase state machine: INTAKE, SPEC, BUILD, REVIEW, DEPLOY, SEO, SHIP, CLOSE, with an exit gate per phase.
- Sixteen reference files covering recon, the spec, the page inventory per site shape, the deterministic builder and its gates, content truth and the claims ledger, the screenshot pipeline, the design system, SEO, deployment to GitHub Pages and Cloudflare Pages, PR and merge discipline, verification, orchestration, batch mode, pitfalls, private repositories and maintenance.
- Seven templates: STATE, SPEC, BRIEF-SITE-BUILDER, BRIEF-INVESTIGATOR, PR-BODY, VERIFY-RECIPE, CLAUDE-MD-BLOCK.
- Five slash commands: `revamp`, `revamp-status`, `revamp-verify`, `revamp-deploy`, `revamp-batch`.
- Three subagents: `site-builder`, `repo-investigator`, `revamp-verifier`.
- `scripts/verify_site.py`: live and local verification with the standard library only.
- `scripts/shots_inventory.py`: image inventory, SHA-256 de-duplication, perceptual clustering and contact sheets.
- The marketplace manifest, so this repository can be added with `/plugin marketplace add`.
