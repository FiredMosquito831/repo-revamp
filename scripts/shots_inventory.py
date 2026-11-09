#!/usr/bin/env python3
"""Inventory, de-duplicate and contact-sheet the screenshots of a repository.

Stages:
  inventory   list every tracked image with size, dimensions and SHA-256
  dedupe      remove exact duplicates by SHA-256
  cluster     remove near-duplicates by perceptual hash (needs Pillow + imagehash)
  sheets      build labelled contact sheets for visual review (needs Pillow)

Standard library for `inventory`; Pillow (and imagehash for `cluster`) for the rest.
The script never writes into the repository: every output goes to --out.

Usage:
  python shots_inventory.py inventory --repo <checkout> --out _revamp/<repo>/SHOTS
  python shots_inventory.py dedupe    --out _revamp/<repo>/SHOTS
  python shots_inventory.py cluster   --out _revamp/<repo>/SHOTS --threshold 4
  python shots_inventory.py sheets    --out _revamp/<repo>/SHOTS --per-sheet 12
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def tracked_images(repo: Path) -> list[Path]:
    output = subprocess.run(
        ["git", "-C", str(repo), "ls-files"],
        check=True, capture_output=True, text=True,
    ).stdout
    return [repo / line for line in output.splitlines() if Path(line).suffix.lower() in IMAGE_SUFFIXES]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dimensions(path: Path) -> tuple[int, int] | None:
    try:
        from PIL import Image  # type: ignore
        with Image.open(path) as image:
            return image.size
    except Exception:
        return None


def group_for(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if "audit" in parts or "verification" in parts or "scenarios" in parts or ".claude" in parts:
        return "forbidden"
    if "apps" in parts or "src" in parts or "public" in parts:
        return "S1"
    if path.suffix.lower() == ".svg":
        return "other"
    return "S2"


def stage_inventory(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, path in enumerate(sorted(tracked_images(repo)), start=1):
        relative = path.relative_to(repo)
        size = path.stat().st_size
        width, height = dimensions(path) or (0, 0)
        rows.append({
            "id": index,
            "path": str(relative).replace("\\", "/"),
            "bytes": size,
            "width": width,
            "height": height,
            "sha256": sha256(path),
            "group": group_for(relative),
        })
    with (out / "inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else
                                ["id", "path", "bytes", "width", "height", "sha256", "group"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"inventory: {len(rows)} images -> {out / 'inventory.csv'}")


def read_inventory(out: Path) -> list[dict]:
    with (out / "inventory.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stage_dedupe(args: argparse.Namespace) -> None:
    out = Path(args.out)
    rows = read_inventory(out)
    seen: dict[str, int] = {}
    result = []
    for row in rows:
        digest = row["sha256"]
        if digest in seen:
            result.append({**row, "verdict": "EXCLUDE-duplicate", "kept": seen[digest]})
        else:
            seen[digest] = row["id"]
            result.append({**row, "verdict": "", "kept": ""})
    write_csv(out / "dedupe.csv", result, list(rows[0].keys()) + ["verdict", "kept"])
    removed = sum(1 for row in result if row["verdict"])
    print(f"dedupe: {len(rows)} rows, {removed} exact duplicates, {len(rows) - removed} unique")


def stage_cluster(args: argparse.Namespace) -> None:
    try:
        import imagehash  # type: ignore
        from PIL import Image  # type: ignore
    except ImportError:
        print("cluster: needs Pillow and imagehash in a scratch venv", file=sys.stderr)
        raise SystemExit(2)

    out = Path(args.out)
    rows = [row for row in read_inventory(out) if not row.get("verdict")]
    hashes = {}
    for row in rows:
        path = Path(args.repo) / row["path"] if args.repo else None
        if path is None or not path.is_file():
            continue
        try:
            with Image.open(path) as image:
                hashes[row["id"]] = imagehash.phash(image.convert("RGB"))
        except Exception:
            continue

    clusters: list[list[str]] = []
    assigned: set[str] = set()
    for identifier, digest in hashes.items():
        if identifier in assigned:
            continue
        members = [identifier]
        assigned.add(identifier)
        for other, other_digest in hashes.items():
            if other in assigned:
                continue
            if digest - other_digest <= args.threshold:
                members.append(other)
                assigned.add(other)
        clusters.append(members)

    cluster_rows = []
    for index, members in enumerate(clusters, start=1):
        for position, member in enumerate(members):
            cluster_rows.append({
                "cluster": index,
                "id": member,
                "representative": members[0],
                "verdict": "" if position == 0 else "EXCLUDE-near-duplicate",
            })
    write_csv(out / "clusters.csv", cluster_rows, ["cluster", "id", "representative", "verdict"])
    near = sum(1 for row in cluster_rows if row["verdict"])
    print(f"cluster: {len(clusters)} clusters from {len(hashes)} hashes, {near} near-duplicates")


def stage_sheets(args: argparse.Namespace) -> None:
    try:
        from PIL import Image, ImageDraw  # type: ignore
    except ImportError:
        print("sheets: needs Pillow in a scratch venv", file=sys.stderr)
        raise SystemExit(2)

    out = Path(args.out)
    sheets = out / "sheets"
    sheets.mkdir(parents=True, exist_ok=True)
    rows = [row for row in read_inventory(out) if not row.get("verdict")]
    columns, tile_w, tile_h = 4, 360, 240
    per_sheet = args.per_sheet
    for start in range(0, len(rows), per_sheet):
        batch = rows[start:start + per_sheet]
        rows_count = (len(batch) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * tile_w, rows_count * tile_h), (24, 24, 24))
        draw = ImageDraw.Draw(sheet)
        for position, row in enumerate(batch):
            path = Path(args.repo) / row["path"] if args.repo else None
            if path is None or not path.is_file():
                continue
            try:
                with Image.open(path) as image:
                    image = image.convert("RGB")
                    image.thumbnail((tile_w - 8, tile_h - 28))
                    x = (position % columns) * tile_w + 4
                    y = (position // columns) * tile_h + 24
                    sheet.paste(image, (x, y))
                    draw.text((x, y - 18), f"#{row['id']}", fill=(255, 255, 255))
            except Exception:
                continue
        name = sheets / f"sheet-{start // per_sheet + 1:02d}.jpg"
        sheet.save(name, quality=85)
        print(f"sheet: {name} ({len(batch)} tiles)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Screenshot inventory pipeline.")
    sub = parser.add_subparsers(dest="stage", required=True)

    inventory = sub.add_parser("inventory")
    inventory.add_argument("--repo", required=True)
    inventory.add_argument("--out", required=True)
    inventory.set_defaults(func=stage_inventory)

    dedupe = sub.add_parser("dedupe")
    dedupe.add_argument("--out", required=True)
    dedupe.set_defaults(func=stage_dedupe)

    cluster = sub.add_parser("cluster")
    cluster.add_argument("--out", required=True)
    cluster.add_argument("--repo")
    cluster.add_argument("--threshold", type=int, default=4)
    cluster.set_defaults(func=stage_cluster)

    sheets = sub.add_parser("sheets")
    sheets.add_argument("--out", required=True)
    sheets.add_argument("--repo")
    sheets.add_argument("--per-sheet", type=int, default=12)
    sheets.set_defaults(func=stage_sheets)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
