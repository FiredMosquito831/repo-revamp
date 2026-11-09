# 16 — Maintenance after launch

The site is live. These are the jobs that keep it true.

## Adding a page

1. Add `site/content/<page>.json` with its `claims` list.
2. Add the page to the navigation and the sitemap inputs.
3. Run the builder.
4. Run `--check`.
5. Add screenshots if the page needs them (the pipeline applies).
6. Commit the source and the regenerated `docs/`.
7. Push. The deployment rebuilds.
8. Verify the live URL.

Never hand-edit `docs/`. It is generated.

## Changing a fact

1. Find the claim in the ledger.
2. Verify the new value against the code.
3. Change the content file.
4. Update the ledger row.
5. Rebuild, `--check`, commit, push, verify.

If the fact is a number, prefer making the builder read it from the source so it cannot drift again.

## Changing the domain

1. Update the site URL in `site/content/site.json` (one constant).
2. Rebuild: canonical, OG, sitemap, robots all derive from it.
3. Update the host's custom domain.
4. Update the DNS record.
5. Update the repository homepage.
6. Submit the new sitemap to Search Console.
7. Keep the old domain redirecting if possible.
8. Verify every URL.

## Updating the product and the site together

- Product change first, in its own PR.
- Site change second, in the site PR, on top of the merged product change.
- Re-verify every claim the product change touches.

## Re-running the gates

```sh
git -c core.autocrlf=false worktree add --detach <tmp> origin/<site-branch>
cd <tmp>
python -m pip install --requirement requirements-site.txt
python scripts/build_site.py --check
```

If it fails, the committed output is stale or the environment differs. Fix the cause, regenerate, commit.

## The monthly check

- Every sitemap URL returns 200.
- `og.png` returns 200.
- HTTP redirects to HTTPS.
- The served commit is the expected head.
- Search Console has no new errors.
- The repository description and homepage are still correct.
- No dependency has a security advisory that affects the builder.

## When the site is stale after a deploy

1. Check the deployment's commit.
2. If it is old, trigger a rebuild.
3. If it is current, check the CDN cache.
4. If the page is still old, check that `docs/` was committed.

## Retiring a site

- Remove the custom domain.
- Remove the DNS record.
- Archive the repository or leave it.
- Do not delete the site branch without the owner's go.
- Keep the tracker row with a "retired" note.

## Exit gate

- The builder is deterministic after every change.
- The ledger matches the site.
- The live URLs are verified after every deploy.
- The tracker is current.
