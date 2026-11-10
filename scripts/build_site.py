#!/usr/bin/env python3
"""Build the repo-revamp documentation site into docs/.

Deterministic by construction: the output depends only on files in the
repository, never on the wall clock, git history or randomness. Every list is
sorted and every file is written with LF newlines.

Usage:
  python scripts/build_site.py            build docs/ (gates first)
  python scripts/build_site.py --check    build to a temp dir and byte-compare with docs/
  python scripts/build_site.py --gates    build to a temp dir and print every gate
  python scripts/build_site.py --claims   print the claims ledger as Markdown
"""

from __future__ import annotations

import argparse
import ast
import html
import json
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
DOCS_DIR = ROOT / "docs"
SKILL_DIR = ROOT / "skills" / "repo-revamp"
REFERENCES_DIR = SKILL_DIR / "references"
TEMPLATES_DIR = REFERENCES_DIR / "templates"
CONTENT_DIR = SITE_DIR / "content"
STATIC_DIR = SITE_DIR / "static"
SHOTS_DIR = SITE_DIR / "shots"
TEMPLATE_DIR = SITE_DIR / "templates"
TOKENS_PATH = SITE_DIR / "design-tokens.json"
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"

TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".xml", ".txt", ".svg", ".md", ".webmanifest"}

SECRET_PATTERNS = [
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("stripe-key", re.compile(r"sk_(live|test)_[A-Za-z0-9]{8,}")),
    ("service-role", re.compile(r"service_role\s*[:=]\s*[A-Za-z0-9._-]{20,}")),
    ("postgres-url", re.compile(r"postgres(ql)?://[^\s\"'<]+")),
    ("mysql-url", re.compile(r"mysql://[^\s\"'<]+")),
    ("credential-assignment", re.compile(r"(?i)(password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*[^\s<]{6,}")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("private-ip", re.compile(r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")),
    ("hosted-project", re.compile(r"\b[a-z]{20}\.supabase\.co\b")),
    ("owner-path", re.compile(r"C:\\Users\\|/home/|/Users/")),
]

FORBIDDEN_STRINGS = [
    "TODO", "TBD", "lorem", "YOUR_", "placeholder", "XXX",
    "example.com", "coming soon", "[insert", "FIXME",
]

INTERNAL_PATTERNS = [
    ("internal-notes", re.compile(r"_revamp/repo-revamp")),
    ("scratch-dir", re.compile(r"_tmp[/\\]")),
    ("claims-file", re.compile(r"CLAIMS\.md")),
    ("brief-file", re.compile(r"BRIEF-SITE\.md")),
    ("account-name", re.compile(r"fgghk", re.IGNORECASE)),
    ("workspace-name", re.compile(r"githubStuff", re.IGNORECASE)),
]

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta name="description" content="(.*?)">', re.S)
CANON_RE = re.compile(r'<link rel="canonical" href="(.*?)">', re.S)
H1_RE = re.compile(r"<h1\b", re.I)
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
ALT_RE = re.compile(r'\balt="([^"]*)"', re.I)
JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
HREF_RE = re.compile(r'(?:href|src)="([^"]+)"', re.I)
ID_RE = re.compile(r'\bid="([^"]+)"')
MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S)
HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")


# --------------------------------------------------------------------------
# small utilities
# --------------------------------------------------------------------------

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def slugify(text: str) -> str:
    text = re.sub(r"`", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return text.strip("-")


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def inline(text: str) -> str:
    """Escape text, then apply the three inline markers the content uses."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    return out


def word_count(page_html: str) -> int:
    match = MAIN_RE.search(page_html)
    body = match.group(1) if match else page_html
    body = re.sub(r"<nav\b.*?</nav>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<pre\b.*?</pre>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<script\b.*?</script>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<style\b.*?</style>", " ", body, flags=re.S | re.I)
    text = html.unescape(strip_tags(body))
    return len(text.split())


def first_h1(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("<!--"):
            return stripped
    return ""


def frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    key = None
    for line in text[3:end].splitlines():
        match = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if match:
            key = match.group(1).strip()
            result[key] = match.group(2).strip()
        elif key and line.strip():
            result[key] = (result[key] + " " + line.strip()).strip()
    return result


def script_docstring(path: Path) -> str:
    try:
        tree = ast.parse(read_text(path))
    except SyntaxError:
        return ""
    doc = ast.get_docstring(tree) or ""
    lines = [line.strip() for line in doc.strip().splitlines() if line.strip()]
    return lines[0] if lines else ""


def truncate(text: str, limit: int = 150) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


# --------------------------------------------------------------------------
# stats computed from the real files
# --------------------------------------------------------------------------

def compute_stats() -> dict[str, object]:
    references = sorted(REFERENCES_DIR.glob("*.md"))
    templates = sorted(TEMPLATES_DIR.glob("*.md"))
    commands = sorted((ROOT / "commands").glob("*.md"))
    agents = sorted((ROOT / "agents").glob("*.md"))
    all_scripts = sorted((ROOT / "scripts").glob("*.py"))
    plugin_scripts = [p for p in all_scripts if p.name != "build_site.py"]
    markdown_files = references + templates + commands + agents + [SKILL_DIR / "SKILL.md"]
    markdown_lines = sum(len(read_text(p).splitlines()) for p in sorted(markdown_files))
    python_lines = sum(len(read_text(p).splitlines()) for p in plugin_scripts)
    plugin = read_json(PLUGIN_JSON)
    return {
        "product": plugin["name"],
        "version": plugin["version"],
        "license": plugin["license"],
        "references": len(references),
        "templates": len(templates),
        "commands": len(commands),
        "agents": len(agents),
        "plugin_scripts": len(plugin_scripts),
        "all_scripts": len(all_scripts),
        "markdown_lines": markdown_lines,
        "python_lines": python_lines,
    }


def fill(text: str, stats: dict[str, object]) -> str:
    """Render the computed counts inside a content string."""
    return Template(text, undefined=StrictUndefined).render(**stats)


def fill_deep(value: object, stats: dict[str, object]) -> object:
    if isinstance(value, str):
        return fill(value, stats)
    if isinstance(value, list):
        return [fill_deep(item, stats) for item in value]
    if isinstance(value, dict):
        return {key: fill_deep(item, stats) for key, item in value.items()}
    return value


# --------------------------------------------------------------------------
# content loading
# --------------------------------------------------------------------------

def load_site() -> dict:
    return read_json(SITE_DIR / "content" / "site.json")


def load_pages(stats: dict[str, object]) -> list[dict]:
    pages = []
    for path in sorted(CONTENT_DIR.glob("*.json")):
        if path.name == "site.json":
            continue
        page = fill_deep(read_json(path), stats)
        page["source"] = str(path.relative_to(ROOT))
        pages.append(page)
    pages.sort(key=lambda p: (p.get("nav_order", 99), p["path"]))
    return pages


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

class PageRenderer:
    def __init__(self, site: dict, stats: dict[str, object], manifest: dict, diagrams: dict[str, str]):
        self.site = site
        self.stats = stats
        self.manifest = manifest
        self.diagrams = diagrams
        self.page: dict = {}

    def render_blocks(self, blocks: list[dict]) -> tuple[str, list[dict]]:
        out: list[str] = []
        toc: list[dict] = []
        used_ids: dict[str, int] = {}
        for block in blocks:
            out.append(self.render_block(block, toc, used_ids))
        return "\n".join(part for part in out if part), toc

    def render_block(self, block: dict, toc: list[dict], used_ids: dict[str, int]) -> str:
        kind = block["type"]
        if kind in {"h2", "h3"}:
            level = 2 if kind == "h2" else 3
            plain = strip_tags(inline(block["text"])).strip()
            base = slugify(plain)
            count = used_ids.get(base, 0) + 1
            used_ids[base] = count
            anchor = base if count == 1 else f"{base}-{count}"
            if level == 2:
                toc.append({"id": anchor, "text": plain})
            return f'<h{level} id="{anchor}">{inline(block["text"])}</h{level}>'
        if kind == "p":
            return f'<p>{inline(block["text"])}</p>'
        if kind in {"ul", "ol"}:
            items = "".join(f"<li>{inline(item)}</li>" for item in block["items"])
            return f'<{kind} class="list">{items}</{kind}>'
        if kind == "code":
            label = block.get("label")
            caption = f"<figcaption>{inline(label)}</figcaption>" if label else ""
            return (
                f'<figure class="code-block">{caption}'
                f'<pre><code>{html.escape(block["text"].strip(chr(10)))}</code></pre></figure>'
            )
        if kind == "file":
            source = ROOT / block["path"]
            if not source.exists():
                raise FileNotFoundError(f"content references a missing file: {block['path']}")
            label = block.get("label", block["path"])
            return (
                f'<figure class="code-block"><figcaption>{inline(label)}</figcaption>'
                f'<pre><code>{html.escape(read_text(source).strip(chr(10)))}</code></pre></figure>'
            )
        if kind == "table":
            head = "".join(f'<th scope="col">{inline(cell)}</th>' for cell in block["head"])
            rows = "".join(
                "<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>"
                for row in block["rows"]
            )
            caption = f"<caption>{inline(block['caption'])}</caption>" if block.get("caption") else ""
            return (
                f'<div class="table-wrap"><table>{caption}'
                f"<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>"
            )
        if kind == "figure":
            svg = self.diagrams[block["diagram"]]
            caption = f"<figcaption>{inline(block['caption'])}</figcaption>" if block.get("caption") else ""
            alt = inline(block["text_alt"])
            return (
                f'<figure class="figure" id="figure-{block["diagram"]}">'
                f'<div class="figure-scroll" tabindex="0" role="group" aria-label="Scrollable diagram">{svg}</div>'
                f'<p class="figure-hint">Scroll the diagram sideways to see all of it.</p>'
                f"{caption}"
                f'<p class="figure-alt"><span class="figure-alt-label">Text alternative:</span> {alt}</p>'
                f"</figure>"
            )
        if kind == "shot":
            item = self.manifest[block["slug"]]
            width = item["width"]
            height = item["height"]
            link = f'<a class="shot-link" href="/assets/shots/{item["slug"]}.webp">'
            return (
                f'<figure class="shot">{link}'
                f'<img src="/assets/shots/{item["slug"]}.webp" alt="{html.escape(item["alt"], quote=True)}" '
                f'width="{width}" height="{height}" loading="lazy" decoding="async">'
                f"</a>"
                f"<figcaption>{inline(item['caption'])}</figcaption></figure>"
            )
        if kind == "cards":
            cards = []
            for card in block["cards"]:
                meta = f'<span class="card-meta">{inline(card["meta"])}</span>' if card.get("meta") else ""
                cards.append(
                    f'<li class="card"><a class="card-link" href="{card["href"]}">'
                    f'<span class="card-title">{inline(card["title"])}</span>{meta}'
                    f'<span class="card-text">{inline(card["text"])}</span></a></li>'
                )
            return f'<ul class="card-grid">{"".join(cards)}</ul>'
        if kind == "callout":
            title = f'<p class="callout-title">{inline(block["title"])}</p>' if block.get("title") else ""
            return f'<aside class="callout callout-{block["tone"]}">{title}<p>{inline(block["text"])}</p></aside>'
        if kind == "cta":
            items = "".join(
                f'<a class="btn btn-{item.get("style", "secondary")}" href="{item["href"]}">{inline(item["label"])}</a>'
                for item in block["items"]
            )
            return f'<div class="hero-actions">{items}</div>'
        if kind == "steps":
            items = "".join(
                f'<li><span class="step-title">{inline(item["title"])}</span>'
                f'<span class="step-text">{inline(item["text"])}</span></li>'
                for item in block["items"]
            )
            return f'<ol class="steps">{items}</ol>'
        if kind == "facts":
            items = "".join(
                f'<div class="fact"><dt>{inline(item["label"])}</dt><dd>{inline(item["value"])}</dd></div>'
                for item in block["items"]
            )
            return f'<dl class="facts">{items}</dl>'
        if kind == "faq":
            items = "".join(
                f'<details class="faq-item"><summary>{inline(item["q"])}</summary>'
                f'<div class="faq-answer"><p>{inline(item["a"])}</p></div></details>'
                for item in block["items"]
            )
            return f'<div class="faq">{items}</div>'
        if kind == "faq-group":
            selected = [item for item in self.page["faq_items"] if item.get("group") == block["group"]]
            if not selected:
                raise ValueError(f"no FAQ items in group {block['group']}")
            items = "".join(
                f'<details class="faq-item"><summary>{inline(item["q"])}</summary>'
                f'<div class="faq-answer"><p>{inline(item["a"])}</p></div></details>'
                for item in selected
            )
            return f'<div class="faq">{items}</div>'
        if kind == "phase-rail":
            items = "".join(
                f'<li class="phase"><span class="phase-dot" aria-hidden="true"></span>'
                f'<span class="phase-name">{phase["name"]}</span>'
                f'<span class="phase-gate">{inline(phase["gate"])}</span></li>'
                for phase in self.site["phases"]
            )
            return f'<ol class="phase-rail">{items}</ol>'
        if kind == "ref-list":
            items = "".join(
                f'<li class="ref-entry" id="{entry["anchor"]}">'
                f'<span class="ref-name">{html.escape(entry["name"])}</span>'
                f'<span class="ref-desc">{inline(entry["description"])}</span>'
                f'<span class="ref-path">{html.escape(entry["path"])}</span></li>'
                for entry in block["entries"]
            )
            return f'<ul class="ref-list">{items}</ul>'
        raise ValueError(f"unknown block type: {kind}")


def breadcrumbs_for(page: dict, site: dict) -> list[dict]:
    if page["path"] == "/":
        return []
    crumbs = [{"label": "Home", "path": "/"}]
    if page.get("noindex"):
        crumbs.append({"label": page["h1"], "path": ""})
        return crumbs
    crumbs.append({"label": page["nav"] if page.get("nav") else page["h1"], "path": ""})
    return crumbs


def jsonld_blocks(page: dict, site: dict, stats: dict[str, object]) -> list[str]:
    url = site["url"] + page["path"]
    blocks: list[dict] = [
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": page["h1"],
            "url": url,
            "description": page["description"],
        }
    ]
    if page["path"] != "/" and not page.get("noindex"):
        crumbs = breadcrumbs_for(page, site)
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": site["url"] + "/"}
        ]
        items.append({"@type": "ListItem", "position": 2, "name": page["nav"], "item": url})
        blocks.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    if page["path"] == "/":
        blocks.append(
            {
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": stats["product"],
                "alternateName": stats["product"],
                "description": page["description"],
                "applicationCategory": "DeveloperApplication",
                "operatingSystem": "Claude Code",
                "softwareVersion": stats["version"],
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                "license": "https://opensource.org/license/mit",
                "isAccessibleForFree": True,
                "featureList": site["feature_list"],
                "author": {"@type": "Person", "name": site["author"]["name"], "url": site["author"]["url"]},
            }
        )
    if page["path"] == "/faq/":
        blocks.append(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": item["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                    }
                    for item in page["faq_items"]
                ],
            }
        )
    return [json.dumps(block, ensure_ascii=False, separators=(",", ":")) for block in blocks]


def render_pages(env: Environment, site: dict, pages: list[dict], stats: dict[str, object], manifest: dict, diagrams: dict[str, str]) -> dict[str, str]:
    renderer = PageRenderer(site, stats, manifest, diagrams)
    output: dict[str, str] = {}
    for page in pages:
        renderer.page = page
        body, toc = renderer.render_blocks(page["sections"])
        template = env.get_template("404.html" if page.get("noindex") else "page.html")
        rendered = template.render(
            site=site,
            page=page,
            stats=stats,
            tokens=TOKENS,
            body=body,
            toc=toc if page.get("toc", True) else [],
            breadcrumbs=breadcrumbs_for(page, site),
            jsonld=jsonld_blocks(page, site, stats),
            og_alt=site["og_alt"],
            lead_html=inline(page["lead"]) if page.get("lead") else "",
        )
        output[page["path"]] = rendered
    return output


# --------------------------------------------------------------------------
# the generated reference page
# --------------------------------------------------------------------------

def reference_entries() -> dict[str, list[dict]]:
    commands = []
    for path in sorted((ROOT / "commands").glob("*.md")):
        meta = frontmatter(path)
        commands.append(
            {
                "name": path.stem,
                "description": meta.get("description", ""),
                "path": str(path.relative_to(ROOT)),
                "anchor": f"ref-command-{slugify(path.stem)}",
            }
        )
    agents = []
    for path in sorted((ROOT / "agents").glob("*.md")):
        meta = frontmatter(path)
        agents.append(
            {
                "name": meta.get("name", path.stem),
                "description": meta.get("description", ""),
                "path": str(path.relative_to(ROOT)),
                "anchor": f"ref-agent-{slugify(path.stem)}",
            }
        )
    references = []
    for path in sorted(REFERENCES_DIR.glob("*.md")):
        references.append(
            {
                "name": path.name,
                "description": first_h1(read_text(path)),
                "path": str(path.relative_to(ROOT)),
                "anchor": f"ref-reference-{slugify(path.stem)}",
            }
        )
    templates = []
    for path in sorted(TEMPLATES_DIR.glob("*.md")):
        text = read_text(path)
        title = first_h1(text) or first_line(text)
        title = re.sub(r"^#+\s*", "", title)
        title = re.sub(r"<([^>]+)>", r"\1", title)
        templates.append(
            {
                "name": path.name,
                "description": truncate(title),
                "path": str(path.relative_to(ROOT)),
                "anchor": f"ref-template-{slugify(path.stem)}",
            }
        )
    scripts = []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        scripts.append(
            {
                "name": path.name,
                "description": script_docstring(path),
                "path": str(path.relative_to(ROOT)),
                "anchor": f"ref-script-{slugify(path.stem)}",
            }
        )
    return {"commands": commands, "agents": agents, "references": references, "templates": templates, "scripts": scripts}


def reference_page(stats: dict[str, object]) -> dict:
    families = reference_entries()
    sections: list[dict] = [
        {"type": "p", "text": (
            "This page is generated at build time from the files in the repository. "
            "Every command, agent, reference file, template and script below exists in the tree; "
            "the counts are computed by `scripts/build_site.py`, not typed by hand."
        )},
        {"type": "h2", "text": "Commands"},
        {"type": "p", "text": (
            f"{len(families['commands'])} slash commands. Each one loads the skill and drives part of the state machine."
        )},
        {"type": "ref-list", "entries": families["commands"]},
        {"type": "h2", "text": "Agents"},
        {"type": "p", "text": (
            f"{len(families['agents'])} subagents. One builds, one investigates, one verifies."
        )},
        {"type": "ref-list", "entries": families["agents"]},
        {"type": "h2", "text": "Reference files"},
        {"type": "p", "text": (
            f"{len(families['references'])} reference files, numbered 00 to 16. "
            "Each carries the depth for one phase or one concern."
        )},
        {"type": "ref-list", "entries": families["references"]},
        {"type": "h2", "text": "Templates"},
        {"type": "p", "text": (
            f"{len(families['templates'])} templates. They are the written artifacts the playbook produces: "
            "state, spec, both briefs, the PR body, the verify recipe and the managed CLAUDE.md block."
        )},
        {"type": "ref-list", "entries": families["templates"]},
        {"type": "h2", "text": "Scripts"},
        {"type": "p", "text": (
            f"{len(families['scripts'])} Python files in `scripts/`. "
            f"{stats['plugin_scripts']} are the plugin's tools; `build_site.py` is the generator that builds this site."
        )},
        {"type": "ref-list", "entries": families["scripts"]},
    ]
    return {
        "slug": "reference",
        "path": "/reference/",
        "nav": "Reference",
        "nav_order": 9,
        "title": "Reference | repo-revamp",
        "description": (
            "Every command, agent, reference file, template and script in repo-revamp, "
            "generated from the real files at build time with stable anchors and live counts."
        ),
        "h1": "Reference",
        "eyebrow": "Generated",
        "lead": "Every component in the repository, read from the files themselves at build time.",
        "priority": "0.8",
        "words": [250, 4000],
        "sections": sections,
        "claims": [
            {
                "claim": "The reference page lists every command, agent, reference file, template and script in the repository.",
                "evidence": "commands/*.md; agents/*.md; skills/repo-revamp/references/*.md; skills/repo-revamp/references/templates/*.md; scripts/*.py",
                "status": "verified",
            },
            {
                "claim": "The counts on the reference page are computed by the builder from the real files.",
                "evidence": "scripts/build_site.py",
                "status": "verified",
            },
        ],
    }


# --------------------------------------------------------------------------
# assets
# --------------------------------------------------------------------------

def tokens_css(tokens: dict) -> str:
    lines = [":root {"]
    for name, value in tokens["color"].items():
        lines.append(f"  --color-{name}: {value};")
    for name, value in tokens["font"].items():
        lines.append(f"  --font-{name}: {value};")
    for name, value in tokens["space"].items():
        lines.append(f"  --space-{name}: {value};")
    for name, value in tokens["radius"].items():
        lines.append(f"  --radius-{name}: {value};")
    for name, value in tokens["motion"].items():
        lines.append(f"  --motion-{name}: {value};")
    lines.append(f"  --focus-ring: {tokens['focus']['ring']};")
    lines.append(f"  --focus-offset: {tokens['focus']['offset']};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def load_manifest() -> dict:
    items = read_json(SHOTS_DIR / "manifest.json")
    return {item["slug"]: item for item in items}


def load_diagrams(stats: dict[str, object]) -> dict[str, str]:
    return {
        path.stem: Template(read_text(path), undefined=StrictUndefined).render(**stats)
        for path in sorted((STATIC_DIR / "diagrams").glob("*.svg"))
    }


def sitemap_xml(pages: list[dict], site: dict) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for page in pages:
        if page.get("noindex"):
            continue
        lines.append("  <url>")
        lines.append(f"    <loc>{site['url']}{page['path']}</loc>")
        lines.append(f"    <lastmod>{site['lastmod']}</lastmod>")
        lines.append(f"    <priority>{page['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def robots_txt(site: dict) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {site['url']}/sitemap.xml\n"


def copy_assets(out: Path, tokens: dict, stats: dict[str, object]) -> None:
    assets = out / "assets"
    (assets / "diagrams").mkdir(parents=True, exist_ok=True)
    (assets / "shots").mkdir(parents=True, exist_ok=True)
    write_text(assets / "style.css", tokens_css(tokens) + read_text(STATIC_DIR / "style.css"))
    shutil.copyfile(STATIC_DIR / "site.js", assets / "site.js")
    shutil.copyfile(STATIC_DIR / "favicon.svg", out / "favicon.svg")
    shutil.copyfile(STATIC_DIR / "icon.png", assets / "icon.png")
    shutil.copyfile(STATIC_DIR / "og.png", out / "og.png")
    for name, svg in sorted(load_diagrams(stats).items()):
        write_text(assets / "diagrams" / f"{name}.svg", svg)
    for path in sorted(SHOTS_DIR.glob("*.webp")):
        shutil.copyfile(path, assets / "shots" / path.name)


# --------------------------------------------------------------------------
# gates
# --------------------------------------------------------------------------

def text_files(*roots: Path) -> list[Path]:
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                found.append(path)
    return found


def gate_secret_scan(out: Path) -> list[str]:
    problems = []
    for path in text_files(SITE_DIR, out):
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    problems.append(f"{path.relative_to(path.parents[len(path.parents) - 1])}:{number}: {name}")
                    break
    return problems


def gate_forbidden_strings(out: Path) -> list[str]:
    problems = []
    for path in text_files(SITE_DIR, out):
        text = read_text(path)
        lowered = text.lower()
        for needle in FORBIDDEN_STRINGS:
            if needle in {"YOUR_", "[insert"}:
                hit = needle in text
            else:
                hit = needle.lower() in lowered
            if hit:
                line = next(
                    (i for i, value in enumerate(text.splitlines(), start=1) if needle.lower() in value.lower()),
                    1,
                )
                problems.append(f"{path}:{line}: {needle}")
    return problems


def resolve_target(out: Path, page_path: str, href: str) -> Path | None:
    if href.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = href.split("#", 1)[0]
    if not target:
        return out / page_path.lstrip("/")
    if target.startswith("/"):
        relative = target.lstrip("/")
    else:
        base = Path(page_path.lstrip("/")).parent
        relative = str(base / target) if str(base) != "." else target
    candidate = out / relative
    if relative == "" or relative.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def gate_links(out: Path) -> list[str]:
    problems = []
    ids: dict[Path, set[str]] = {}
    html_files = sorted(out.rglob("*.html"))
    for path in html_files:
        ids[path] = set(ID_RE.findall(read_text(path)))
    for path in html_files:
        page_path = "/" + str(path.relative_to(out)).replace("\\", "/")
        text = read_text(path)
        for href in HREF_RE.findall(text):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            if href.startswith("#"):
                fragment = href[1:]
                if fragment and fragment not in ids[path]:
                    problems.append(f"{page_path}: missing fragment #{fragment}")
                continue
            target = resolve_target(out, page_path, href)
            if target is None:
                continue
            if not target.exists():
                problems.append(f"{page_path}: {href} does not resolve")
                continue
            if "#" in href:
                fragment = href.split("#", 1)[1]
                if fragment and target in ids and fragment not in ids[target]:
                    problems.append(f"{page_path}: {href} fragment does not resolve")
    return problems


def gate_metadata(out: Path, site: dict) -> list[str]:
    problems = []
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    for path in sorted(out.rglob("*.html")):
        page_path = "/" + str(path.relative_to(out)).replace("\\", "/")
        text = read_text(path)
        title_match = TITLE_RE.search(text)
        desc_match = DESC_RE.search(text)
        canon_match = CANON_RE.search(text)
        if not title_match:
            problems.append(f"{page_path}: no title")
            continue
        title = html.unescape(title_match.group(1))
        if len(title) > 60:
            problems.append(f"{page_path}: title is {len(title)} characters")
        if title in titles:
            problems.append(f"{page_path}: duplicate title with {titles[title]}")
        titles[title] = page_path
        if not desc_match:
            problems.append(f"{page_path}: no description")
        else:
            description = html.unescape(desc_match.group(1))
            if not 120 <= len(description) <= 160:
                problems.append(f"{page_path}: description is {len(description)} characters")
            if description in descriptions:
                problems.append(f"{page_path}: duplicate description with {descriptions[description]}")
            descriptions[description] = page_path
        if not canon_match:
            problems.append(f"{page_path}: no canonical")
        else:
            canonical = canon_match.group(1)
            expected = site["url"] + ("/404.html" if page_path.endswith("404.html") else page_path.replace("index.html", ""))
            if page_path.endswith("index.html") and not page_path.endswith("/index.html"):
                expected = site["url"] + "/"
            if canonical != expected:
                problems.append(f"{page_path}: canonical {canonical} != {expected}")
        if len(H1_RE.findall(text)) != 1:
            problems.append(f"{page_path}: {len(H1_RE.findall(text))} h1 elements")
        for needle in ('property="og:title"', 'property="og:description"', 'property="og:url"',
                       'property="og:image"', 'property="og:image:alt"', 'property="og:locale"',
                       'name="twitter:card"', 'name="twitter:title"', 'name="twitter:description"',
                       'name="twitter:image"', 'name="theme-color"'):
            if needle not in text:
                problems.append(f"{page_path}: missing {needle}")
        theme = re.search(r'<meta name="theme-color" content="([^"]+)">', text)
        if theme and theme.group(1) != TOKENS["color"]["bg"]:
            problems.append(f"{page_path}: theme-color is not the background token")
    return problems


def gate_alt_text(out: Path) -> list[str]:
    problems = []
    for path in sorted(out.rglob("*.html")):
        page_path = "/" + str(path.relative_to(out)).replace("\\", "/")
        for tag in IMG_RE.findall(read_text(path)):
            match = ALT_RE.search(tag)
            if not match or not match.group(1).strip():
                problems.append(f"{page_path}: image without alt text")
    return problems


def gate_jsonld(out: Path) -> list[str]:
    problems = []
    for path in sorted(out.rglob("*.html")):
        page_path = "/" + str(path.relative_to(out)).replace("\\", "/")
        for block in JSONLD_RE.findall(read_text(path)):
            try:
                json.loads(block)
            except json.JSONDecodeError as error:
                problems.append(f"{page_path}: JSON-LD does not parse ({error.msg})")
    return problems


def gate_sitemap(out: Path) -> list[str]:
    problems = []
    path = out / "sitemap.xml"
    if not path.exists():
        return ["sitemap.xml missing"]
    root = ET.fromstring(read_text(path))
    for loc in root.iter():
        if loc.tag.rpartition("}")[2] != "loc":
            continue
        url = loc.text or ""
        relative = url.split("://", 1)[-1].split("/", 1)[-1]
        target = out / relative / "index.html" if relative else out / "index.html"
        if not target.exists():
            problems.append(f"sitemap URL has no file: {url}")
    return problems


def gate_og_image(out: Path) -> list[str]:
    path = out / "og.png"
    if not path.exists():
        return ["og.png missing"]
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return ["og.png is not a PNG"]
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1200, 630):
        return [f"og.png is {width}x{height}, not 1200x630"]
    return []


def gate_tokens(out: Path, tokens: dict) -> list[str]:
    allowed = {value.upper() for value in tokens["color"].values()}
    problems = []
    for path in sorted(list((SITE_DIR / "templates").glob("*.html")) + list((STATIC_DIR / "diagrams").glob("*.svg")) + [STATIC_DIR / "style.css", STATIC_DIR / "favicon.svg"]):
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            for value in HEX_RE.findall(line):
                if value.upper() not in allowed:
                    problems.append(f"{path}:{number}: colour {value} is not a token")
    for path in sorted(out.rglob("*.css")):
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            for value in HEX_RE.findall(line):
                if value.upper() not in allowed:
                    problems.append(f"{path.name}:{number}: colour {value} is not a token")
    return problems


def gate_reference(out: Path) -> list[str]:
    problems = []
    path = out / "reference" / "index.html"
    if not path.exists():
        return ["reference page missing"]
    text = read_text(path)
    families = reference_entries()
    total = 0
    for family, entries in families.items():
        if not entries:
            problems.append(f"reference family {family} is empty")
        for entry in entries:
            total += 1
            if f'id="{entry["anchor"]}"' not in text:
                problems.append(f"reference page is missing {entry['path']}")
    if text.count('class="ref-entry"') != total:
        problems.append(f"reference page lists {text.count('class=\"ref-entry\"')} entries, expected {total}")
    return problems


def gate_word_counts(out: Path, pages: list[dict]) -> list[str]:
    problems = []
    for page in pages:
        if page["path"] == "/":
            path = out / "index.html"
        elif page["path"].endswith(".html"):
            path = out / page["path"].lstrip("/")
        else:
            path = out / page["path"].strip("/") / "index.html"
        if not path.exists():
            problems.append(f"{page['path']}: output missing")
            continue
        count = word_count(read_text(path))
        low, high = page["words"]
        if not low <= count <= high:
            problems.append(f"{page['path']}: {count} words, outside {low}-{high}")
    return problems


def gate_diagrams() -> list[str]:
    problems = []
    for path in sorted((STATIC_DIR / "diagrams").glob("*.svg")):
        text = read_text(path)
        for needle in ('role="img"', "aria-labelledby=", "<title", "<desc"):
            if needle not in text:
                problems.append(f"{path.name}: missing {needle}")
    return problems


def gate_cname(out: Path, site: dict) -> list[str]:
    path = out / "CNAME"
    if not path.exists():
        return ["CNAME missing"]
    value = read_text(path).strip()
    if value != site["host"]:
        return [f"CNAME is {value}, expected {site['host']}"]
    return []


def gate_legal(out: Path, site: dict) -> list[str]:
    problems = []
    for path in sorted(out.rglob("*.html")):
        text = read_text(path)
        for key in ("non_affiliation", "license"):
            if site["legal"][key] not in text:
                problems.append(f"{path.name}: missing legal text {key}")
    return problems


def gate_external_requests(out: Path) -> list[str]:
    problems = []
    for path in sorted(out.rglob("*.html")):
        text = read_text(path)
        for pattern in (r'<script[^>]+src="https?://', r'<link[^>]+rel="stylesheet"[^>]+href="https?://',
                        r"@import\s+url", r"<iframe\b", r"fonts\.googleapis", r"fonts\.gstatic",
                        r"google-analytics", r"googletagmanager"):
            if re.search(pattern, text, re.I):
                problems.append(f"{path.name}: external request ({pattern})")
    css = out / "assets" / "style.css"
    if css.exists() and re.search(r"@import|url\(\s*['\"]?https?://", read_text(css), re.I):
        problems.append("style.css: external request")
    return problems


def gate_internal_process(out: Path) -> list[str]:
    problems = []
    for path in text_files(out):
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            for name, pattern in INTERNAL_PATTERNS:
                if pattern.search(line):
                    problems.append(f"{path.name}:{number}: {name}")
    return problems


def gate_claims(pages: list[dict]) -> list[str]:
    problems = []
    for page in pages:
        if not page.get("claims"):
            problems.append(f"{page['path']}: no claims")
            continue
        for claim in page["claims"]:
            if not claim.get("claim") or not claim.get("evidence"):
                problems.append(f"{page['path']}: claim without evidence")
                continue
            if claim.get("status") not in {"verified", "removed"}:
                problems.append(f"{page['path']}: claim status {claim.get('status')}")
            evidence = claim["evidence"]
            tokens = [part.strip() for part in re.split(r"[;]", evidence) if part.strip()]
            resolved = False
            for token in tokens:
                candidate = token.split(":")[0].split("§")[0].strip()
                if candidate and (ROOT / candidate).exists():
                    resolved = True
                    break
            if not resolved and not evidence.startswith(("computed", "command", "the builder")):
                problems.append(f"{page['path']}: evidence does not resolve: {evidence}")
    return problems


def run_gates(out: Path, site: dict, pages: list[dict], tokens: dict) -> list[tuple[str, list[str]]]:
    return [
        ("secret scan", gate_secret_scan(out)),
        ("forbidden strings", gate_forbidden_strings(out)),
        ("links", gate_links(out)),
        ("page metadata", gate_metadata(out, site)),
        ("alt text", gate_alt_text(out)),
        ("JSON-LD", gate_jsonld(out)),
        ("sitemap", gate_sitemap(out)),
        ("og.png 1200x630", gate_og_image(out)),
        ("tokens only", gate_tokens(out, tokens)),
        ("reference completeness", gate_reference(out)),
        ("word counts", gate_word_counts(out, pages)),
        ("diagrams", gate_diagrams()),
        ("CNAME", gate_cname(out, site)),
        ("legal texts", gate_legal(out, site)),
        ("no external requests", gate_external_requests(out)),
        ("no internal process", gate_internal_process(out)),
        ("claims ledger", gate_claims(pages)),
    ]


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def build(out: Path) -> dict:
    stats = compute_stats()
    site = load_site()
    pages = load_pages(stats)
    pages.append(reference_page(stats))
    pages.sort(key=lambda p: (p.get("nav_order", 99), p["path"]))
    manifest = load_manifest()
    diagrams = load_diagrams(stats)
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    rendered = render_pages(env, site, pages, stats, manifest, diagrams)
    for path, text in sorted(rendered.items()):
        if path == "/":
            write_text(out / "index.html", text)
        elif path.endswith(".html"):
            write_text(out / path.lstrip("/"), text)
        else:
            write_text(out / path.strip("/") / "index.html", text)
    write_text(out / "sitemap.xml", sitemap_xml(pages, site))
    write_text(out / "robots.txt", robots_txt(site))
    write_text(out / "CNAME", site["host"] + "\n")
    copy_assets(out, TOKENS, stats)
    return {"pages": pages, "site": site, "stats": stats}


def compare_trees(left: Path, right: Path) -> list[str]:
    def listing(root: Path) -> dict[str, bytes]:
        files = {}
        for path in sorted(root.rglob("*")):
            if path.is_file():
                files[str(path.relative_to(root)).replace("\\", "/")] = path.read_bytes()
        return files

    a = listing(left)
    b = listing(right)
    differing = []
    for name in sorted(set(a) | set(b)):
        if name not in a or name not in b or a[name] != b[name]:
            differing.append(name)
    return differing


def sync_docs(source: Path) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.rglob("*")):
        if path.is_file():
            target = DOCS_DIR / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    for path in sorted(DOCS_DIR.rglob("*"), reverse=True):
        if path.is_file() and not (source / path.relative_to(DOCS_DIR)).exists():
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def claims_markdown(pages: list[dict]) -> str:
    lines = [
        "# Claims ledger — repo-revamp site",
        "",
        "Generated from the `claims` list in every `site/content/*.json` by",
        "`python scripts/build_site.py --claims`. One row per factual statement.",
        "",
        "| # | Page | Claim (exact wording) | Evidence | Status |",
        "|---|---|---|---|---|",
    ]
    index = 0
    for page in pages:
        for claim in page["claims"]:
            index += 1
            lines.append(
                f"| {index} | {page['path']} | {claim['claim']} | {claim['evidence']} | {claim['status']} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="build to a temp dir and byte-compare with docs/")
    parser.add_argument("--gates", action="store_true", help="print every gate result")
    parser.add_argument("--claims", action="store_true", help="print the claims ledger as Markdown")
    args = parser.parse_args()

    if args.claims:
        stats = compute_stats()
        pages = load_pages(stats)
        pages.append(reference_page(stats))
        pages.sort(key=lambda p: (p.get("nav_order", 99), p["path"]))
        print(claims_markdown(pages))
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        result = build(out)
        pages = result["pages"]
        site = result["site"]
        failures = 0
        for name, problems in run_gates(out, site, pages, TOKENS):
            if problems:
                failures += len(problems)
                print(f"FAIL  {name}")
                for problem in problems:
                    print(f"      {problem}")
            elif args.gates:
                print(f"PASS  {name}")
        if failures:
            print(f"{failures} gate failure(s)")
            return 1
        if args.check:
            differing = compare_trees(out, DOCS_DIR)
            if differing:
                print("check: docs/ differs from a fresh build:")
                for name in differing:
                    print(f"  {name}")
                return 1
            print("check: docs/ is byte-identical to a fresh build")
            return 0
        sync_docs(out)
        print(f"built {len(pages)} pages into docs/")
        return 0


TOKENS = read_json(TOKENS_PATH)


if __name__ == "__main__":
    sys.exit(main())
