# 06 — The screenshot pipeline

A gallery is the most persuasive part of a product site and the easiest place to leak something. This pipeline is mandatory: inventory, de-duplicate, review every candidate, redact on a copy, derive, record, cover.

## 1. Inventory

```sh
git ls-files | grep -iE '\.(png|jpe?g|webp|gif|svg)$'
```

Write `_revamp/<repo>/SHOTS/inventory.csv`:

```csv
id,path,bytes,width,height,sha256,group
1,my-app/apps/web/public/dashboard.png,182344,1440,900,3f2a...,S1
2,qa/login-verified.png,91200,1280,800,9c11...,S2
3,assets/logo.svg,2048,64,64,aa01...,other
```

Groups:

- **S1** — product UI captures shipped with the app (the best source: they show the real product).
- **S2** — QA, verification or regression captures elsewhere in the repository (the richest source: they show every state).
- **other** — diagrams, icons, logos, screenshots of internal documents.

Exclusions before review:

- anything under internal folders (`audit/`, `verification/`, `scenarios/`, `.claude/`, `prompts/`) — record `EXCLUDE-forbidden-folder` and do not open it;
- anything that is not a UI capture (logos, diagrams, icons) — `EXCLUDE-not-ui`;
- anything below a usable resolution (for example under 600 px wide) — `EXCLUDE-too-small`.

## 2. Exact duplicates

Identical SHA-256. Keep one, record the rest as `EXCLUDE-duplicate` with the kept id.

## 3. Near-duplicates

Perceptual hash (pHash) with Hamming distance ≤ 4. Install `Pillow` and `imagehash` into a scratch venv, **never into the repository**.

```python
import imagehash
from PIL import Image

def phash(path):
    with Image.open(path) as im:
        return imagehash.phash(im.convert("RGB"))
```

Cluster the hashes. Keep the clearest representative per cluster (sharpest, most complete state, no cursor, no toast covering content). Record the others as `EXCLUDE-near-duplicate` with the cluster id.

Write `clusters.csv`: cluster id, member ids, representative id.

## 4. Contact sheets

Build sheets outside the repository: 4 columns × 3 rows, each tile labelled with its inventory id, under `_revamp/<repo>/SHOTS/sheets/`.

Review every tile. For any tile where sensitive content might be present, open the full-size original (read-only) and inspect it at full resolution before deciding.

## 5. The review checklist

Any hit makes the image `REDACT` (if cleanly fixable) or `EXCLUDE`:

- keys, tokens, JWTs, service-role or anon key values, API secrets, webhook secrets
- passwords or filled password fields
- SMTP or database credentials
- connection strings, database URLs, `postgres://` text
- email addresses, personal names, avatars
- invoices or billing details
- project references or project IDs that identify a real account
- IP addresses or hostnames of private infrastructure
- file-system paths that reveal the owner's account (`C:\Users\...`, `/home/...`)
- real third-party data (customer records, messages, emails in tables)
- internal file names or numbering that leaks the process

Synthetic test data is allowed only if it contains no real-looking secrets. `demo-project` and `test@example.invalid` pass; a realistic JWT does not.

## 6. Verdicts

`_revamp/<repo>/SHOTS/review.csv`:

```csv
id,path,group,verdict,reason,area,alt_text,redactions
1,my-app/apps/web/public/dashboard.png,S1,INCLUDE,clean,dashboard,"Project overview showing the local services and their status.", 
2,qa/settings-backup.png,S2,REDACT,account email visible,admin,"Settings page with the backup controls and the account section.","120,340,260,28"
```

Verdicts:

- **INCLUDE** — clean, public-safe.
- **REDACT** — useful, with sensitive regions that can be blacked out cleanly.
- **EXCLUDE-<reason>** — one of: duplicate, near-duplicate, forbidden-folder, not-ui, too-small, wrong-content, broken-layout, loading-state, error-state, email-present, real-data, unclear.

Every candidate gets a verdict. The counts must reconcile:

```
inventory = duplicates + near-duplicates + excluded-before-review + reviewed
reviewed = INCLUDE + REDACT + EXCLUDE
```

## 7. Redaction

- Done on a **copy**, with solid black rectangles over the exact regions identified at full size.
- **Never modify an original.**
- Record each rectangle as `x,y,w,h` in original pixel coordinates.
- After redaction, re-open the derivative and confirm visually that the sensitive text is unreadable and that nothing else was hidden.
- Re-run the full review on the crop or the redacted derivative. A crop can reveal what the full image hid.

## 8. Derivatives

For each INCLUDE or REDACT image:

```
site/shots/<slug>.webp          max width 1600, quality ~80
site/shots/<slug>-thumb.webp    max width 640, quality ~75
```

Slug rules:

- feature area plus a descriptive name, lowercase, hyphenated
- no internal ids or numbering (`observability-api-overview`, never `vfy491` or `feature-114-conflict-modal`)
- unique

Budgets (adjust in the spec; these are the revision-2 defaults):

- each `.webp` ≤ 300 KB
- `site/shots/` ≤ 90 MB
- total `docs/` ≤ 120 MB
- gallery ≤ 200 images, ≥ 80

If the approved pool is larger than the gallery budget, rank by feature coverage and sharpness and keep the best.

## 9. Detail derivatives

Encouraged, because they make a page feel real:

- **Zoom crops** from the original (read-only) into a new derivative, to show a control or a status closely. Re-run the full review on the crop.
- **Numbered callout overlays** drawn on a copy, pointing to the relevant UI element. The callout text is written by the author, verified against the screen, and must not expose sensitive content. Record the overlay coordinates in the manifest.
- **Before-and-after pairs** only when both states are real product screens from the repository's QA material.

## 10. The manifest

`site/shots/manifest.json`:

```json
[
  {
    "slug": "dashboard-overview",
    "area": "dashboard",
    "alt": "Project overview showing the local services and their status for a single stack.",
    "caption": "The project overview: every local service and its current state.",
    "source": "my-app/apps/web/public/dashboard.png",
    "verdict": "INCLUDE",
    "redacted": false,
    "width": 1440,
    "height": 900,
    "callouts": []
  }
]
```

Rules:

- `source` is for traceability only; the builder never copies originals.
- `alt` and `caption` are required for every entry.
- `redacted` is true when rectangles were applied.
- `callouts` records the overlay coordinates when present.

## 11. Alt text

- Describe what the screen shows and what a visitor learns, in one or two sentences, plain English.
- Never include secrets, paths, emails, project references or internal jargon.
- Never say "screenshot of a verification run".
- Pattern: "Project overview showing the local services and their status for a single Supabase stack."

## 12. Captions

- One sentence: what it shows and why it matters.
- Every image has one, including gallery images.
- Correct the caption when the state is an empty state, a loading state or an error state. Do not caption an empty state as if it showed data.

## 13. Coverage

`_revamp/<repo>/SHOTS/coverage.md`:

```markdown
| Feature area | Page | Images |
|---|---|---|
| dashboard | /features/dashboard/ | 11 |
| database | /features/database/ | 6 |
| edge functions | (no deep page) | 0 |
```

Rules:

- Every feature area shown on `/features/` with an image has at least one approved image.
- A feature area with no approved image shows **no image slot**. Never a placeholder.
- Every distinct product screen found in the app source is represented at least once, or explicitly justified as excluded.
- Every feature deep page has 3–8 images, or the page is not built.

## 14. The report numbers

The final report states:

- inventory total, S1 and S2 counts
- exact duplicates removed, near-duplicates removed
- candidates reviewed
- INCLUDE, REDACT, EXCLUDE counts, with the top EXCLUDE reasons
- gallery size and total derivative size
- redactions applied and where
- captions corrected

## Exit gate

- Every candidate has a verdict; the counts reconcile.
- Every INCLUDE and REDACT has alt text and a caption.
- Every REDACT has recorded rectangles and a visually confirmed derivative.
- No original image is modified (`git diff --name-status` shows no image as modified).
- The manifest validates as JSON and every entry has its required fields.
- The coverage matrix is complete.
