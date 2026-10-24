# Verification — v1.2.1

Performed 24 October 2026:
- 22 backend tests passed with fake Redis and mocked Discord requests.
- Includes login/state replay, session expiry, member/officer authorization, role
  removal, screening, CSRF-protected sign-out, rate windows, fail-closed Redis and
  Discord failures, safe diagnostics, startup configuration and health responses.
- Health tests verify unauthenticated HTTP 200/Redis connected, HTTP 503 on Redis
  connection failure or negative ping, no Discord calls, and no exception details
  or credentials in the health JSON/logs.
- Frontend syntax and link configuration checks passed for app.js and config.js.
- Public member-access coming-soon section removed; header buttons grouped.
- Local HTML assets and anchors resolve; artwork unchanged from the supplied ZIP.

Limits:
- Backend tests ran locally with Python 3.9 on macOS; Docker targets Python 3.12.
  The local urllib3 warning about LibreSSL did not affect mocked HTTP tests.
- No production Redis/Discord request, Docker build, visual browser/mobile check,
  GitHub push, Cloudflare deployment or Railway deployment performed for this release.
- Discord login errors on the user's deployment are not confirmed resolved. The
  package supplies safe diagnostic references for any remaining failure.
- The health endpoint checks Redis, not Discord credentials or configured roles.
