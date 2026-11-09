---
description: Run the revamp verification recipe against a live site or a local docs directory
argument-hint: <url-or-docs-dir> [--local-dir docs] [--json out.json]
allowed-tools: Read, Grep, Glob, Bash
---

Run the verification recipe for: **$ARGUMENTS**

1. If the argument is an `https://` URL, run:

```sh
python "${CLAUDE_PLUGIN_ROOT}/scripts/verify_site.py" --base-url <url>
```

2. If the argument is a directory containing `docs/`, run both the local and the live checks:

```sh
python "${CLAUDE_PLUGIN_ROOT}/scripts/verify_site.py" --base-url <the recorded site URL> --local-dir <dir>/docs
```

3. If a checkout is available, also run the gate on a clean worktree:

```sh
git -C <checkout> -c core.autocrlf=false worktree add --detach <tmp> origin/<site-branch>
cd <tmp> && python scripts/build_site.py --check
```

4. Report every check as PASS or FAIL with its status and detail. Then state:
   - CONFIRMED: what the commands proved.
   - UNVERIFIED: what needs a browser, a screenshot review or the host's dashboard.
   - NOT DONE: what you skipped and why.

Never report a site as verified on the strength of a 200 from the root alone.
