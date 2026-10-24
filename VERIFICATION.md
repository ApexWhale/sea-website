# Verification — v1.1.0

Performed 24 October 2026 against the supplied ZIP and updated files.

## Passed

- 12 backend unittest cases using Flask's request client, fake Redis (including Lua)
  and simulated Discord API responses: member/officer access, live role removal,
  missing sessions, one-use/browser-bound state, state expiry and consent cancellation,
  screening and role denial, sign-out CSRF/origin checks and session invalidation,
  expired sessions, upstream failures, Redis outage, rate limits and invalid config.
- HTML escaping of the simulated Discord display name; tokens absent from response
  HTML and plaintext Redis session values; Secure/HttpOnly/SameSite cookie flags.
- JavaScript syntax checks for the updated app.js and supplied config.js.
- Five frontend configuration cases: empty URL, JavaScript URL, HTTP URL and a URL
  with embedded credentials are rejected; a valid HTTPS login URL enables links.
- Local assets and section anchor references in index.html resolve.
- Local HTTP preview returned status 200.
- Compared against the original ZIP: no source file was removed; original styles,
  images/assets, invite configuration, Cloudflare headers, error page, sitemap,
  robots.txt and preview server were preserved byte-for-byte.

Tests ran with Python 3.9 on this Mac. The deployable Dockerfile targets Python 3.12.
The local urllib3 library warned about this Mac Python's LibreSSL; tests mocked
external HTTP and made no real Discord requests. The Docker image was not built here.

## Not verified

- Actual Discord consent/token exchange, actual server membership or role IDs.
- A live Redis service; Redis behavior was simulated in tests.
- Browser visual rendering, responsive layout and keyboard behavior. The browser
  control tool failed to bind the preview tab; HTTP preview itself worked.
- Railway container build, production healthchecks, DNS, HTTPS certificate issuance,
  Cloudflare header application or live invitation validity.
- GitHub commit/push, Railway deployment or Cloudflare publication. None performed.

Follow README.md for setup and live acceptance tests before enabling the public
login link. Secrets were not provided or invented. Tests use clearly synthetic IDs
and a temporary encryption key; no test credentials are production configuration.
