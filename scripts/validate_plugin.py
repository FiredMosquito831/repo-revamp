#!/usr/bin/env python3
"""Validate the plugin repository before publishing.

Checks:
  1. .claude-plugin/plugin.json parses and has the required fields
  2. .claude-plugin/marketplace.json parses and has the required fields
  3. every plugin entry in the marketplace points at a directory that exists
  4. every SKILL.md has YAML frontmatter with name and description
  5. every command and agent file has frontmatter with description
  6. every referenced reference/template file exists
  7. no unfilled `<<slot>>` markers left in the shipped files
  8. every Python script compiles

The forbidden-string list that a built site must not contain is documented by
this plugin on purpose, so it is not scanned here. It belongs to the site
builder's gate, not to the plugin repository.

Standard library only. Exit 0 only when everything passes.

Usage:
  python scripts/validate_plugin.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNFILLED_SLOT = re.compile(r"<<[A-Z][A-Z0-9 ,_/-]*>>")


def fail(message: str) -> None:
    print(f"FAIL  {message}")
    errors.append(message)


def ok(message: str) -> None:
    print(f"PASS  {message}")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    result: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if re.match(r"^[A-Za-z_-]+:", line):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
        elif key and line.strip():
            result[key] += " " + line.strip()
    return result


errors: list[str] = []


def main() -> int:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"

    if not plugin_path.is_file():
        fail("missing .claude-plugin/plugin.json")
    else:
        try:
            plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            fail(f"plugin.json does not parse: {error}")
            plugin = {}
        for field in ("name", "description", "version"):
            if not plugin.get(field):
                fail(f"plugin.json missing required field: {field}")
        if plugin.get("name") and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", plugin["name"]):
            fail(f"plugin name is not lowercase-kebab: {plugin['name']}")
        if plugin.get("name"):
            ok(f"plugin.json: {plugin['name']} {plugin.get('version', '')}")

    if not marketplace_path.is_file():
        fail("missing .claude-plugin/marketplace.json")
    else:
        try:
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            fail(f"marketplace.json does not parse: {error}")
            marketplace = {}
        for field in ("name", "owner", "plugins"):
            if field not in marketplace:
                fail(f"marketplace.json missing required field: {field}")
        if marketplace.get("name") and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", marketplace["name"]):
            fail(f"marketplace name is not lowercase-kebab: {marketplace['name']}")
        for entry in marketplace.get("plugins", []):
            if not entry.get("name"):
                fail("marketplace plugin entry without a name")
            if not entry.get("source"):
                fail(f"marketplace plugin entry {entry.get('name')} without a source")
            else:
                source = entry["source"]
                if isinstance(source, str):
                    target = (ROOT / source).resolve()
                    if not target.exists():
                        fail(f"marketplace source does not exist: {source}")
        if marketplace.get("name"):
            ok(f"marketplace.json: {marketplace['name']} ({len(marketplace.get('plugins', []))} plugins)")

    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        meta = frontmatter(skill)
        if not meta.get("name"):
            fail(f"{skill.relative_to(ROOT)} missing frontmatter name")
        if not meta.get("description"):
            fail(f"{skill.relative_to(ROOT)} missing frontmatter description")
        if meta.get("name") and meta["name"] != skill.parent.name:
            fail(f"{skill.relative_to(ROOT)} name '{meta['name']}' does not match folder '{skill.parent.name}'")
        if meta.get("name"):
            ok(f"skill: {meta['name']}")

    for folder, label in (("commands", "command"), ("agents", "agent")):
        for path in sorted((ROOT / folder).glob("*.md")):
            meta = frontmatter(path)
            if not meta.get("description"):
                fail(f"{path.relative_to(ROOT)} missing frontmatter description")
            else:
                ok(f"{label}: {path.stem}")

    skill_root = ROOT / "skills" / "repo-revamp"
    referenced = set(re.findall(r"`(references/[^`]+\.md)`", (skill_root / "SKILL.md").read_text(encoding="utf-8")))
    for relative in sorted(referenced):
        if not (skill_root / relative).is_file():
            fail(f"SKILL.md references a missing file: {relative}")
    if referenced:
        ok(f"SKILL.md references: {len(referenced)} files, all present")

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".json", ".py", ".yml", ".yaml"}:
            continue
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in UNFILLED_SLOT.finditer(text):
            fail(f"{path.relative_to(ROOT)} contains an unfilled slot: {match.group(0)}")
    ok("no unfilled slots")

    for script in sorted((ROOT / "scripts").glob("*.py")):
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as error:
            fail(f"{script.relative_to(ROOT)} does not compile: {error}")
    ok(f"scripts: {len(list((ROOT / 'scripts').glob('*.py')))} compile")

    print()
    if errors:
        print(f"{len(errors)} problem(s)")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
