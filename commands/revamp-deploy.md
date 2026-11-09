---
description: Walk the deployment for a revamped repository, including the owner-only steps
argument-hint: <repo> [github-pages | cloudflare-pages]
allowed-tools: Read, Grep, Glob, Bash, Write
---

Prepare and verify the deployment for: **$ARGUMENTS**

1. Read `_revamp/<repo>/STATE.md` and the spec's deployment section. If the host is not recorded, stop and ask the owner (one question, with a recommendation).
2. Confirm the gate is green first: `build_site.py --check` on a clean worktree at the site branch head. A deploy with a failing gate is a stop.
3. **GitHub Pages:** follow `references/09-deployment.md` §A — create the site, poll the build, check the certificate, nudge it if stuck, enforce HTTPS only after `approved`, force a rebuild, verify the served commit.
4. **Cloudflare Pages:** follow §B — print the owner-only dashboard steps verbatim, wait for the owner, then confirm the project settings read-only before attaching the custom domain.
5. Verify: HTTP → HTTPS 301, root 200, `og.png` 200 and 1200×630, every sitemap URL 200, served commit equals the expected head.
6. Report the deployment id, the commit it built from, and every check with its status.

Never change DNS, repository settings or the production branch without the owner's explicit go. Never claim a deployment succeeded without the served-commit check.
