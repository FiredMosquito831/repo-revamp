# The verify recipe — run after every "shipped" report, before relaying

```sh
# 1. Re-anchor
git -C <checkout> fetch origin --tags
git -C <checkout> log -1 --format='%h %s' origin/<default>
git -C <checkout> log -1 --format='%h %s' origin/<site-branch>
git -C <checkout> log --oneline HEAD..origin/<default> | wc -l

# 2. Product boundary — must print nothing
git -C <checkout> diff --name-only <base> origin/<site-branch> \
  | grep -vE '^(site/|docs/|scripts/build_site\.py$|requirements-site\.txt$|\.github/workflows/site\.yml$|README\.md$|\.gitignore$)'

# 3. Gate on a clean worktree
git -C <checkout> -c core.autocrlf=false worktree add --detach <tmp> origin/<site-branch>
cd <tmp>
python scripts/build_site.py --check

# 4. Local serve
python -m http.server <port> --directory docs
# sweep every page, asset, shot, sitemap, robots, og.png

# 5. Live
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://<host>/
curl -s -o /dev/null -w "%{http_code}\n" https://<host>/og.png
curl -s https://<host>/sitemap.xml | grep -o "<loc>" | wc -l
# every loc must return 200

# 6. Served commit
gh api repos/<owner>/<repo>/pages/builds/latest --jq '{status,commit}'
git -C <checkout> rev-parse origin/<default>
# must match

# 7. Open PRs
gh pr list --repo <owner>/<repo> --state open

# 8. CI conclusions, each read by name
gh run list --repo <owner>/<repo> --branch <site-branch> --limit 5
```

Then:

- Look at at least one screenshot the agent named (Read tool). Scan images for key prefixes.
- Read the agent's deviations, residual risks and not-done list.
- Check the claims ledger and the legal texts.
- Append the dated "SHIPPED AND VERIFIED BY ME" line.
- Add the release-history row.
- Flip the queue row to FINISHED with the proofs.
- Port the lessons.
- Tell the owner: what shipped, what you verified, deviations, not done.
- Announce the next dispatch.
