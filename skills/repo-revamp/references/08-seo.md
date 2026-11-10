# 08 — SEO: metadata, structured data, sitemap and submission

Every page is generated with complete metadata. Nothing is left to a plugin or a crawler's guess.

## Keywords

`<meta name="keywords">` is ignored by Google for ranking, but it is still read by several smaller engines, by site-search tools, and by the people who audit your page. Emit it, and keep it truthful.

Rules:

- **One keyword set per page**, not one for the site. A product page needs its product's terms; the home page needs the category terms.
- **Every keyword must be true of that page.** "gmail mcp server" belongs on the Gmail page, not on the home page.
- **Include the harness names** the product actually supports: `claude code`, `codex`, `opencode`, `antigravity`. These are the highest-intent queries for an MCP product.
- **Include the task phrasing** a person would type: "automate site index submission", "download moodle courses", not only the product name.
- **Include the local language** when the audience is local. A Romanian-audience product needs Romanian terms, not only English ones.
- **No keyword stuffing.** 8–14 terms per page. A term that appears on every page of the site is a site-level term, not a page term.
- **No invented capability.** A keyword that describes something the product does not do is a false claim and belongs in the claims ledger as `removed`.

## Per-product pages

When the repository ships many products (a plugin per product, a server per API), each product gets its own page with its own:

- `<title>`: the product name plus its category and one harness, ≤ 60 characters
- description: what it does, for whom, and the tool count, 120–160 characters
- keyword set: 8–14 terms, product-specific
- `SoftwareApplication` JSON-LD with `name`, `applicationCategory`, `operatingSystem`, `softwareVersion`, `offers` at zero, and the product's own `featureList`
- a "what you can do with it" list of real tasks, each traceable to a tool

The product page is the page that ranks for "`<product>` mcp server". The home page ranks for the category. Do not let the home page compete with its own product pages for the same term.

## Harness landing pages

When a product supports several agent harnesses, each harness gets a landing page (`/for/claude-code/`, `/for/codex/`, `/for/opencode/`, `/for/antigravity/`) with:

- a harness-specific title and description
- the exact install command for that harness
- the same product facts, not different ones
- a link back to the product pages and the install page

These pages answer "`<product>` for `<harness>`", which is a distinct query from "`<product>` mcp server".

## Machine-readable surfaces

Search engines are not the only readers. Add these files at the site root:

### `llms.txt`

A short Markdown index for language models and agent crawlers:

```markdown
# <Product>

> One sentence: what it is and who it is for.

<One paragraph of context: the category, the licence, the version.>

## Docs
- [Install](https://<host>/install/): one line on what it covers
- [Products](https://<host>/products/): the full list

## Optional
- [License](https://<host>/license/)
```

Rules: plain Markdown, absolute links, one line per link, no marketing language. It is a map, not a pitch.

### `llms-full.txt`

The same site as plain text, concatenated, for a model that wants the whole thing in one fetch. Optional; generate it from the same content as the HTML so it cannot drift.

### `security.txt`

Per RFC 9116, at `/.well-known/security.txt`:

```text
Contact: https://github.com/<owner>/<repo>/security/advisories/new
Expires: <a date within one year>
Preferred-Languages: en
Canonical: https://<host>/.well-known/security.txt
```

### `humans.txt` and `sitemap` index

Optional. A `sitemap` index is worth it only above 50,000 URLs.

## Structured data beyond the basics

| Page | Types |
|---|---|
| Home | `WebSite` with `potentialAction` (`SearchAction`) only if the site has search; `SoftwareApplication` or `WebApplication` |
| Product page | `SoftwareApplication` plus `BreadcrumbList` |
| Docs page | `TechArticle` with `about`, `proficiencyLevel` |
| FAQ | `FAQPage` |
| How-to page | `HowTo` with `step` items |
| Gallery | `ImageGallery` |
| License | `WebPage` with `license` |
| Every page | `WebPage`, and `Organization` once at the site level |

## Canonical, hreflang and duplicates

- **Canonical** on every page, absolute, with the trailing slash.
- **`hreflang`** on every page of a multilingual site: one alternate per language plus `x-default`. `x-default` points at the primary language, not at English by default.
- **No duplicate titles or descriptions** across pages. The builder's gate enforces uniqueness.
- **No `noindex`** on any page that should rank. The 404 and any staging page carry it.

## The keyword file

Keep the keyword sets in data, not in templates: `site/content/seo.json`, keyed by page path and language. The builder reads it and emits the tags. A page without a keyword set fails the build, so a new page cannot ship unoptimised.

Validate at build time:

- title ≤ 60 characters
- description 120–160 characters
- 8–14 keywords
- no keyword duplicated across more than three pages
- every keyword appears in the page's own text or is a documented synonym

## Per-page metadata

The builder emits these from the page's content data.

```html
<title>Features | <Product></title>                         <!-- ≤ 60 characters -->
<meta name="description" content="...">                      <!-- 120–160 characters, unique -->
<link rel="canonical" href="https://<host>/<path>/">         <!-- absolute, trailing slash -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="<Product>">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="https://<host>/<path>/">
<meta property="og:image" content="https://<host>/og.png">
<meta property="og:image:alt" content="...">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="https://<host>/og.png">
<meta name="theme-color" content="<token bg>">
```

Rules:

- **Title:** page-specific, ≤ 60 characters, ending with `| <Product>` where it fits. The home title may be longer if it is the product's full name plus a benefit.
- **Description:** unique, 120–160 characters, truthful, one primary keyword used naturally.
- **Keywords:** optional and truthful only. Never a keyword the product does not earn.
- **Canonical:** absolute, with the trailing slash for directory pages.
- **`og:image`:** absolute, 1200×630, served at the site root.
- **`theme-color`:** the token background.

## JSON-LD

Every page:

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "...",
  "url": "https://<host>/<path>/",
  "description": "..."
}
```

Non-home pages also get:

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://<host>/"},
    {"@type": "ListItem", "position": 2, "name": "Features", "item": "https://<host>/features/"}
  ]
}
```

Home also gets the product type:

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "<Product>",
  "alternateName": "<package name>",
  "description": "<verified>",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "<only verified platforms>",
  "softwareVersion": "<read from the manifest>",
  "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
  "license": "<licence URL>",
  "isAccessibleForFree": true,
  "featureList": ["<verified items only>"],
  "author": {"@type": "Person", "name": "<owner>", "url": "https://github.com/<owner>"}
}
```

FAQ page:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "...", "acceptedAnswer": {"@type": "Answer", "text": "..."}}
  ]
}
```

Gallery:

```json
{
  "@context": "https://schema.org",
  "@type": "ImageGallery",
  "image": [{"@type": "ImageObject", "contentUrl": "...", "description": "<alt>"}]
}
```

Rules:

- **The FAQ JSON-LD is generated from the same array as the visible FAQ.** They cannot drift.
- **`codeRepository` only if the owner approves exposing it.** For a private repo, omit it.
- **`operatingSystem` only for verified platforms.** Never "Windows, macOS, Linux" by default.
- **Every JSON-LD block must parse.** The builder's gate enforces it.

## Sitemap

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://<host>/</loc>
    <lastmod>2026-10-23</lastmod>
    <priority>1.0</priority>
  </url>
  ...
</urlset>
```

Rules:

- Every public page, absolute URLs, trailing slashes.
- `lastmod` is a fixed value in `site/content/site.json`. The owner updates it deliberately. Never read it from git history.
- Priorities: home 1.0, features and quick start 0.9, architecture and configuration 0.8, gallery and FAQ 0.7, about 0.5, license 0.4.
- The 404 page is not included.
- The builder's gate checks every URL has a file.

## Robots

```text
User-agent: *
Allow: /

Sitemap: https://<host>/sitemap.xml
```

## The social image

- Exactly 1200×630.
- Generated from an HTML mock served locally and screenshotted with Playwright (`file://` is blocked).
- Shows the product name, a one-line value proposition and a recognisable product visual.
- No text smaller than 24 px at that size.
- Served at `/og.png` and referenced absolutely.
- **Check it is committed.** A root `.gitignore` with `*.png` will silently exclude it; add `!docs/og.png` and `!site/static/og.png` and verify with `git check-ignore -v`.

## The 404 page

- Friendly, one sentence, links home and to the main hub.
- `noindex`.
- Not in the sitemap.

## Search Console

The domain property covers every subdomain when it is a domain property (`sc-domain:<zone>`).

1. Submit `https://<host>/sitemap.xml`.
2. Confirm the property exists and the sitemap is listed.
3. Re-check after the first crawl; a new site can take days.

If the Search Console MCP is unavailable, record the exact URL to submit and hand it to the owner. Never claim submission without the tool's response.

## Repository metadata

After the site is live:

```sh
gh repo edit <owner>/<repo> \
  --description "<one line, keyword-rich, truthful>" \
  --homepage "https://<host>"

gh api -X PUT repos/<owner>/<repo>/topics \
  -f names[]="topic-one" -f names[]="topic-two"
```

Rules:

- **Description:** one line, no hype, the search snippet under the repo name. Lead with the category term someone would search ("Google Workspace MCP servers"), then the differentiator.
- **Homepage:** the live URL.
- **Topics:** 10–15, lowercase, hyphenated, accurate. No topic the project does not earn.
- **Never change visibility, name, default branch or settings** as part of SEO.

### Topic sets that work

| Repository kind | Topics |
|---|---|
| MCP server | `mcp`, `mcp-server`, `model-context-protocol`, `claude-code`, `claude-code-plugin`, `codex`, `opencode`, `ai-agents`, `llm-tools`, plus one per product area |
| Plugin marketplace | `claude-code`, `claude-code-plugin`, `plugin`, `marketplace`, plus the domain terms |
| Documentation site | the product terms plus `documentation`, `static-site`, `seo` |

### Repository SEO beyond the description

- **Social preview:** GitHub renders `og:image` from the repository's social preview setting. Upload the same 1200×630 image the site uses, so a shared repository link looks like the site.
- **README first screen:** the first 300 characters are what search engines and social cards show. Put the category term and the value there, not a logo.
- **Releases:** a tagged release with notes ranks for "`<product>` release" and gives the repository a fresh timestamp.
- **Discussions and issues:** open, answered issues are indexed and rank for long-tail questions. Do not close a question without an answer.

## Verification

- Every sitemap URL returns 200.
- `http://` returns 301 to `https://`.
- `og.png` returns 200 and is 1200×630.
- Every page's canonical equals its live URL.
- The FAQ JSON-LD equals the visible FAQ.
- The sitemap is listed in Search Console.

## Exit gate

- Every page has complete, unique metadata.
- Every JSON-LD block parses.
- The sitemap and robots are correct and served.
- `og.png` is 1200×630 and committed.
- The sitemap is submitted (or handed to the owner with the exact URL).
- The repository description, homepage and topics are set.
