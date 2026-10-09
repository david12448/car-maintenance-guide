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
