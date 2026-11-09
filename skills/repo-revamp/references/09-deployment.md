# 09 — Deployment: GitHub Pages and Cloudflare Pages

Two hosts, two different sets of traps. Pick one in INTAKE and follow its section exactly.

## Decision recap

| Condition | Host |
|---|---|
| Public repo, no previews needed | GitHub Pages from `<default-branch>:/docs` |
| Private repo, public site | Cloudflare Pages from the site branch, output `docs` |
| Public repo, PR previews wanted | Cloudflare Pages |
| Public repo, owner prefers Cloudflare | Cloudflare Pages |

The two custom-domain records are **opposites**:

- **GitHub Pages:** CNAME to `<owner>.github.io`, **DNS-only (grey cloud)**.
- **Cloudflare Pages:** the record is created by Cloudflare, **proxied (orange cloud)**.

Getting this backwards causes HTTPS failures that look like certificate problems.

---

# A. GitHub Pages

## A1. Create the site

```sh
gh api -X POST repos/<owner>/<repo>/pages \
  -f 'source[branch]=<default-branch>' \
  -f 'source[path]=/docs'
```

The custom domain is read from `docs/CNAME`. Create that file with the bare hostname:

```text
<sub>.<zone>
```

No protocol, no trailing slash, one line.

## A2. Wait for the build

```sh
gh api repos/<owner>/<repo>/pages/builds/latest --jq '{status,commit,url}'
```

Poll until `status: built`. Then check the commit:

```sh
gh api repos/<owner>/<repo>/pages/builds/latest --jq '.commit'
git -C <checkout> rev-parse origin/<default-branch>
```

They must match. That is the proof Pages is serving the branch we think it is.

## A3. The certificate

```sh
gh api repos/<owner>/<repo>/pages --jq '.https_certificate.state'
```

States: `none`, `authorization_pending`, `authorized`, `approved`.

If it stays `none` (seen on a site created before DNS existed), **nudge it**:

```sh
gh api -X PUT repos/<owner>/<repo>/pages -f 'cname='          # clear
sleep 5
gh api -X PUT repos/<owner>/<repo>/pages \
  -f 'source[branch]=<default-branch>' -f 'source[path]=/docs' \
  -f 'cname=<sub>.<zone>'
```

Then poll until `approved`.

## A4. Enforce HTTPS

Only after `approved`:

```sh
gh api -X PUT repos/<owner>/<repo>/pages \
  -f 'source[branch]=<default-branch>' -f 'source[path]=/docs' \
  -f 'cname=<sub>.<zone>' -F 'https_enforced=true'
```

Enforcing before the certificate exists fails with "The certificate does not exist yet".

## A5. Force a rebuild after switching source

```sh
gh api -X POST repos/<owner>/<repo>/pages/builds
```

Then poll `builds/latest.commit` until it equals the new source head.

## A6. DNS

Create the record in Cloudflare:

```sh
# via the Cloudflare MCP or the dashboard
# type CNAME, name <sub>, content <owner>.github.io, proxied: false
```

Check for an existing record first. Never duplicate. Add a comment naming the project.

## A7. Verify

```sh
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://<host>/
curl -s -o /dev/null -w "%{http_code}\n" https://<host>/og.png
curl -s https://<host>/sitemap.xml | grep -o "<loc>" | wc -l
```

Then every `<loc>` must return 200.

---

# B. Cloudflare Pages

## B1. The owner-only step

Cloudflare Pages' GitHub integration needs the owner to authorise the Cloudflare GitHub App for the repository. An agent must not attempt to bypass this.

Owner instructions, verbatim:

1. Open the Cloudflare dashboard, go to Workers & Pages, choose Create application, then Pages, then Connect to Git.
2. Choose GitHub, sign in, and install or configure the Cloudflare Pages GitHub app on the `<owner>` account. Grant it access to the repository `<repo>` specifically, not all repositories.
3. Return to Cloudflare, select `<owner>/<repo>`, and begin the project setup with the settings below.
4. Confirm the production branch.

## B2. Project settings

| Setting | Value |
|---|---|
| Project name | `<sub>` (matches the subdomain) |
| Production branch | `<site-branch>` (often `revamp`, not the default branch) |
| Framework preset | None |
| Build command | empty (the site output is committed) |
| Build output directory | `docs` |
| Root directory | `/` |
| Environment variables | none |
| Preview deployments | enabled for PR branches |

## B3. After the owner connects it

Read-only first:

- confirm the project exists
- confirm the GitHub source is attached
- confirm the output directory is `docs`
- confirm the production branch

Only then attach the custom domain through the Pages project API, and only for this project. Record every call: method, path, status.

## B4. The custom domain

`<sub>.<zone>`. Because the zone is on Cloudflare, the record is created automatically and is **proxied (orange cloud)**. Do not switch it to DNS-only.

## B5. Verify

```sh
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://<host>/
curl -s -o /dev/null -w "%{http_code}\n" https://<host>/og.png
curl -s https://<host>/sitemap.xml | grep -o "<loc>" | wc -l
```

Also:

- the `*.pages.dev` URL serves the same content (if it resolves; if it does not, record it as a cosmetic finding and check the project URL in the dashboard);
- report the production deployment id and the commit it built from.

## B6. The production branch decision

The production branch is the branch Cloudflare builds. Two valid postures:

- **Launch from the site branch** (`revamp`): the site is isolated from the product branch. Nothing merges. This is the safest posture and the one used when the owner wants presentation isolation.
- **Launch from the default branch**: requires the site PR to be merged first, then the production branch changes, then a redeploy.

Record the choice in the spec. Never change the production branch without the owner's go.

---

# C. Traps that bit

| Symptom | Cause | Fix |
|---|---|---|
| `og.png` 404 on the live site | root `.gitignore` has `*.png` and `docs/og.png` was never committed | add `!docs/og.png`, commit, redeploy; verify with `git check-ignore -v` |
| Certificate stuck on `none` | site created before DNS existed | the clear-and-re-add nudge (A3) |
| "The certificate does not exist yet" | HTTPS enforced before `approved` | wait for `approved`, then enforce |
| Pages serves an old commit | no rebuild after switching source | `POST /pages/builds`, poll the commit |
| HTTPS fails on GitHub Pages | the CNAME is proxied (orange) | set it to DNS-only |
| Cloudflare Pages custom domain fails | the record was set to DNS-only | leave it proxied |
| The site works but the sitemap 404s | the sitemap is generated but not committed | `--check` would have caught it; commit the output |
| A page is live but stale | the builder output was not regenerated | run the builder, commit `docs/`, push |

## Exit gate

- The live root returns 200 over HTTPS.
- HTTP returns 301 to HTTPS.
- Every sitemap URL returns 200.
- `og.png` returns 200 and is 1200×630.
- The served commit equals the expected head.
- The custom-domain record has the correct proxy setting for the host.
- The deployment id and commit are recorded in the report.
