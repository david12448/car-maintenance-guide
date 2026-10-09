# URL Migration Progress

## 2026-10-10 — Pilot design

### Current state confirmed
- Public hosting: GitHub Pages via custom GitHub Actions workflow
- Existing vehicle route: `/vehicles/{internal-id}/`
- Older compatibility route: `/vehicle.html?id={internal-id}`
- Vehicle pages are already pre-rendered static HTML, so direct access/refresh is reliable
- Fuel and purchase modules use fixed static paths
- Private collectors/source mappings remain outside the public repository
- Open governance PR is preserved and not modified by this work

### Pilot decision
Use data-driven static HTML and add readable canonical paths without removing legacy paths.

### Pilot vehicles
- `/maintenance/hyundai/sonata-nf/`
- `/maintenance/kia/sportage-sl/`
- `/maintenance/mercedes-benz/e-class-w212/`

### Regression gates
- exact canonical static file exists
- old `/vehicles/{id}/` file exists and redirects with fallback link
- `vehicle.html?id=` remains supported
- JavaScript syntax checks remain
- public JSON validation remains
- sitemap contains canonical paths and excludes pilot legacy paths
- root/fuel/purchase canonical is generated
- no DNS or Custom Domain change

### Common-rule candidate
A reusable cross-project pattern is emerging:
- central `PUBLIC_SITE_ORIGIN`
- stable slug fields separate from internal IDs
- pre-rendered static canonical routes
- legacy noindex compatibility pages
- generated sitemap/robots
- CI route regression validation

This is a candidate for future project-common-rules guidance after the pilot is verified.


## 2026-10-10 — Pilot CI correction

- Symptom: first PR #19 route validation failed after page generation.
- Impact: no deployment or merge occurred; existing public site remained unchanged.
- Root cause: verified. The canonical URL helper stripped the trailing slash from directory-style URLs, while the documented public URL contract requires stable trailing slashes.
- Fix: canonical URL generation now preserves the trailing slash for directory routes and preserves a single slash for the site root.
- Regression test: `validators/validate_routes.py` checks exact canonical strings for all pilot routes, root/fuel/purchase, sitemap membership, and legacy-route exclusion.
- Prevention: treat trailing-slash policy as part of the public URL contract rather than presentation formatting.
