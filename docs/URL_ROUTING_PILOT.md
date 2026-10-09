# EvoCocoons URL and custom-domain migration pilot

Status: **proposal, branch-only; no DNS changes or production deployment**  
Date: 2026-10-10 (KST)

## Current observed deployment contract
- Public repository: david12448/car-maintenance-guide
- Private source repository: david12448/car-maintenance-source
- Current GitHub Pages target: https://david12448.github.io/car-maintenance-guide/
- Existing direct pages: \`/\`, \`/fuel/\`, \`/purchase/\`, \`/vehicles/{vehicle-id}/\` under the Pages project prefix.
- Existing legacy link: \`/vehicle.html?id={vehicle-id}\` uses JS location.replace to the direct static \`/vehicles/{vehicle-id}/\` page. **Preserve this file and JS behavior.**
- \`/purchase/\` and \`/fuel/\` retain existing UI and public-data status. Unverified or placeholder offers must not be fabricated.
- Existing vehicle IDs already work as stable, human-readable slugs (e.g. \`hyundai-sonata-nf\`). Do not re-slug them automatically.
- No existing iframe/embed contract was identified in the inspected public repository. Check external Blogger/Tistory pages independently before any domain cutover.

## Implemented in this pilot
1. Build-time canonical for existing index pages at root, fuel, purchase, and vehicle details; all pages are real HTML files so direct-load and refresh do not depend on JS routing.
2. A curated \`sitemap.xml\` containing the home page and vehicle pages with a recorded detail dataset. Deliberately exclude empty fuel/purchase feed pages and placeholder vehicles from the sitemap (this does not by itself prevent indexing).
3. A single GitHub Actions variable \`PUBLIC_SITE_URL\` overrides the default GitHub Pages project base. If unset, Actions uses the owner/repository GitHub Pages address.
4. Tests cover project-path deployment, domain-root deployment, invalid URL rejection, sitemap selection, and repeated builds.
5. Existing relative asset links, legacy \`vehicle.html?id=\` redirects, UI and data JSON remain intact.

## Slug and route policy
- Slugs: lowercase ASCII letters/digits/hyphens; stable after publication; avoid dates and internal identifiers unless essential for a collision.
- Compose collisions with category or durable disambiguator, and record previous slugs in a redirect/alias registry.
- Route structure: \`/{category}/{subcategory}/{item}/\` when a meaningful hierarchy helps; stable \`/vehicles/{vehicle-slug}/\` is retained for compatibility, not renamed gratuitously.
- Only publish individual item pages with useful unique information. URL generation must not manufacture incomplete product pages.
- Public IDs and public slugs are not equivalent to private collector/source identifiers.
- Keep a testable legacy-to-new mapping with fixtures before changing any route; shared/embedded old links remain valid.

## Canonical, sitemap, robots and SEO
- The canonical URL is generated from the **currently live** deployment URL, not a future brand-domain example.
- The sitemap uses this same base, so canonical and sitemap agree. At domain cutover, only the controlled \`PUBLIC_SITE_URL\` configuration should change.
- Project-site \`/car-maintenance-guide/robots.txt\` is **not** the domain-root robots control: crawlers fetch \`https://david12448.github.io/robots.txt\` for this host. Do not claim path-level robots.txt works before root-domain hosting.
- A custom subdomain with root-level \`/robots.txt\` can host a domain-specific robots file later.
- Avoid thin generated pages, duplicate title/description, and mass content cloning.
- Use visible navigable HTML links and descriptive headings. Add structured data only when its source facts are independently verified.
- GitHub Pages alone cannot provide server-side HTTP 301 for individual project paths. Preserve old static pages and existing redirect shim; do not promise HTTP 301. At a future reverse-proxy/Cloudflare edge, evaluate precise permanent redirects after verifying old links.

## Migration and DNS playbook (documentation only)
1. Confirm root brand: \`evococoons.com\` **or** \`prince-in-wonderworld.com\`; neither is selected by this pilot.
2. Retain old project-pages links and iframe targets. Inventory external references and create redirect test cases.
3. Run the test build with \`PUBLIC_SITE_URL=https://auto.<approved-domain>\` in a non-production environment, and ensure canonical, sitemap and assets match that host.
4. If GitHub Pages custom domain is chosen, configure GitHub Pages Custom Domain for the public repository and use the GitHub-documented subdomain CNAME target \`david12448.github.io\` at the DNS provider. Verify host, certificate/HTTPS and DNS propagation before changing canonical.
5. If Cloudflare Pages is chosen, configure the Pages project and custom domain there instead. Confirm build output path, HTTPS, caching and rewrite rules. Do not configure both providers for the same host.
6. After successful deployment and live HTTPS checks, set \`PUBLIC_SITE_URL\` to the **actual** custom-domain URL for canonical and sitemap. Submit new sitemap and verify Search Console / Naver site registration as applicable.
7. During transition, avoid allowing two domains to publish contradictory canonical URLs. Preserve stable legacy access; only introduce HTTP redirects after verified support and no iframe regressions.
8. DNS records, CNAME files, Custom Domain settings, remote secrets and domain ownership verification require explicit user approval. **None are performed in this PR.**

## Limitations / next steps
- This is a build-level pilot: production URL checks await review, merge, deploy, and live smoke testing.
- Test active blog/iframe links independently; repository inspection alone cannot prove their behavior.
- Private finance repository is not yet present in accessible repositories. Define finance routing separately after its repo exists; existing auto/card public IDs can be used without guessing financial products.
- Roll out the method to card, finance, telecom, mart, travel and other projects **only after** their current routes/PRs/CI are independently audited and a common policy PR is reviewed.
- External public URLs, once navigated to, cannot be hidden from users; only protect private collection logic, bulk source registries, secrets and internal mapping.
