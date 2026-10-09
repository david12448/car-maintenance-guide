# Custom Domain Setup — NOT YET APPLIED

This document is preparatory. Do not change DNS or GitHub Pages Custom domain until separately approved.

## A. GitHub Pages option

Target hostname example:
- `auto.evococoons.com`
- or `auto.prince-in-wonderworld.com`

When approved:

1. Verify the root domain in GitHub first.
2. In the public repository, open Settings → Pages.
3. Set the chosen custom subdomain.
4. At the DNS provider, create a CNAME for `auto` pointing to `david12448.github.io` — not to the repository path.
5. Verify DNS resolution.
6. Enable Enforce HTTPS when available.
7. Set repository Actions variable `PUBLIC_SITE_ORIGIN` to the final HTTPS origin.
8. Rebuild and verify canonical, sitemap, old URLs and HTTPS before announcing the domain.

This repository deploys Pages through a custom GitHub Actions workflow, so a committed `CNAME` file is not required for the planned configuration.

Avoid wildcard DNS for project subdomains.

## B. Cloudflare Pages option

If later migration is justified:
1. create a Pages project from the public repository/build
2. associate the chosen custom domain in the Cloudflare Pages dashboard
3. for a subdomain, point its CNAME to the project `*.pages.dev` hostname as instructed by Cloudflare
4. change `PUBLIC_SITE_ORIGIN` only after the production custom hostname is active
5. re-run canonical/sitemap/legacy regression tests

Do not create only a DNS CNAME without associating the custom domain with the Pages project.

## C. Domain switch

Because canonical and sitemap use `PUBLIC_SITE_ORIGIN`, switching between candidate roots should not require template edits.

Required checks:
- root/fuel/purchase canonical
- pilot vehicle canonical
- sitemap host
- robots sitemap URL
- old GitHub Pages URLs
- old query parameter URLs
- Blogger/Tistory iframe or shared links if any are known at that time

## D. No DNS action in this pilot

Current canonical origin remains the GitHub Pages origin until a final domain is approved.
