# DMMA Certificate Verification API (staging scaffold)

This Worker is designed to run independently of the domain's current Netlify DNS registration. Initial testing can use the Worker `*.workers.dev` address. Do not change nameservers or DNS records for this setup.

## Files
- `src/index.js`: public lookup and protected admin endpoints.
- `migrations/0001_create_certificates.sql`: D1 schema.
- `wrangler.toml.example`: configuration template; replace the D1 database ID only in your local deployment config.

## Endpoints
- `GET /api/certificates/DMMA-2026-0001`: public verification lookup.
- `POST /api/admin/certificates`: protected issuance endpoint.
- `PATCH /api/admin/certificates/DMMA-2026-0001/revoke`: protected revocation endpoint.

Admin endpoints require `Authorization: Bearer <ADMIN_API_KEY>`. Store this value as a Cloudflare Worker secret; never place it in the website, GitHub, browser code, or chat.

## Setup (not yet deployed)
1. Create a D1 database named `dmma-certificates`.
2. Copy `wrangler.toml.example` to `wrangler.toml` locally and replace the database ID.
3. Apply the migration with Wrangler.
4. Set the Worker secret `ADMIN_API_KEY` using Wrangler secret management.
5. Deploy the Worker and test on its `workers.dev` URL.
6. Configure a Cloudflare rate-limiting rule for public lookups and admin routes before production use.
7. Connect the verification page to the Worker URL and update the page's Content Security Policy `connect-src` to allow that exact Worker origin.

## Important limitations
- This is a staging scaffold, not a deployed or audited production service.
- The API only records and verifies certificates issued by the Academy. It does not confer US accreditation, university credit, or professional licensure.
- Public responses reveal recipient name, course title, issue date, and optional hours. Confirm the Academy's privacy policy and recipient consent before entering real learner records.
- Add an authenticated admin interface and an audit trail before routine issuance. Do not expose admin credentials in a static page.
- Certificate numbers are validated against the example format `DMMA-YYYY-NNNN`; ensure issuance is controlled and numbers are unique.
