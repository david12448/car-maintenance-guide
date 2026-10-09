# URL Architecture — Auto

Status: pilot
Custom domain: deferred

## 1. Target structure

The path structure is independent of the final root domain.

- `/` — 자동차 생활 홈
- `/maintenance/` — 정비·리콜
- `/maintenance/{maker-slug}/` — 제조사
- `/maintenance/{maker-slug}/{vehicle-slug}/` — 차량/세대
- `/fuel/` — 주유소·유가
- `/purchase/` — 차량 구매

Examples:
- `/maintenance/hyundai/sonata-nf/`
- `/maintenance/kia/sportage-sl/`
- `/maintenance/mercedes-benz/e-class-w212/`

The same paths can later live under either:
- `auto.evococoons.com`
- `auto.prince-in-wonderworld.com`

## 2. Central origin configuration

Canonical URLs and sitemap URLs are generated from one value.

1. GitHub Actions variable `PUBLIC_SITE_ORIGIN`
2. fallback: `config/site.json -> defaultOrigin`

Current fallback:
`https://david12448.github.io/car-maintenance-guide`

Do not scatter either candidate root domain through templates.

## 3. Slug rules

- lowercase ASCII
- words separated by `-`
- no internal database identifier unless it is also a meaningful public generation/platform code
- no unnecessary dates
- once published, keep the slug stable
- renames/ended products keep the old slug as a compatibility route or alias
- collisions are resolved by category/maker context first, then a meaningful generation/platform suffix

Examples:
- maker: `hyundai`, `kia`, `mercedes-benz`
- vehicle: `sonata-nf`, `sportage-sl`, `e-class-w212`

Internal `id` remains the data key and is not removed.

## 4. Pilot

Three representative pages use the new canonical path:
- Hyundai NF Sonata
- Kia Sportage SL
- Mercedes-Benz E-Class W212

Other vehicles stay on the existing `/vehicles/{id}/` path during the pilot.

## 5. Legacy compatibility

For pilot vehicles:
- old `/vehicles/{id}/` remains a real static file
- it is `noindex,follow`
- it points canonical to the new URL
- it performs static meta-refresh plus JavaScript replacement and provides a normal fallback link

The older `vehicle.html?id=...` route remains supported. It reads the public vehicle registry and sends pilot vehicles directly to the new route; non-pilot vehicles keep the previous route.

GitHub Pages cannot provide repository-controlled server-side 301 rules, so the pilot uses static compatibility pages rather than pretending a client redirect is a 301.

## 6. SEO

Build output includes:
- unique title and description for vehicle pages
- absolute canonical
- `sitemap.xml`
- `robots.txt`
- crawlable manufacturer and maintenance landing pages
- BreadcrumbList JSON-LD on pilot vehicle pages
- legacy paths excluded from sitemap

Do not generate large groups of near-identical pages merely for search coverage.

## 7. Static hosting decision

Current pilot choice: data-driven static HTML generation.

Why:
- direct URL and refresh work without client routing
- compatible with current GitHub Pages
- keeps existing JSON-driven source data
- no framework migration required
- easiest rollback and regression testing

JavaScript routing alone is rejected for content URLs because refresh/direct access can 404 on static hosting.

A full SSG can be reconsidered once templates/content volume make the current generator hard to maintain.

GitHub Pages remains suitable for the pilot. At much larger scale, watch repository/site size, build duration, deployment frequency and bandwidth. Cloudflare Pages remains an alternative when deployment/CDN/routing requirements justify migration.

## 8. Public/private boundary

Pretty URLs change only the public presentation contract. They do not expose:
- source registry
- raw snapshots
- collectors/parsers
- original URL mappings
- API credentials
- reconciliation rules

## 9. Embed compatibility

No existing embed route is changed by this pilot. Future widgets should use explicit `/embed/`, `/calendar/`, or `/widget/` paths and lightweight layouts.
