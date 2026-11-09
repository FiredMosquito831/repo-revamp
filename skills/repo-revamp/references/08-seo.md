# 08 — SEO: metadata, structured data, sitemap and submission

Every page is generated with complete metadata. Nothing is left to a plugin or a crawler's guess.

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

- **Description:** one line, no hype, the search snippet under the repo name.
- **Homepage:** the live URL.
- **Topics:** 10–15, lowercase, hyphenated, accurate. No topic the project does not earn.
- **Never change visibility, name, default branch or settings** as part of SEO.

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
