# Verification — v1.0.0

Performed 22 October 2026:

- PASS: Node.js syntax checks for app.js, config.js and preview.cjs.
- PASS: Every local asset referenced by index.html exists.
- PASS: Every nonempty section anchor in index.html has a matching ID.
- PASS: Link logic exercised in an isolated Node context with a minimal document test double: empty config adds no buttons; valid HTTPS config enables Discord and both dashboard links; non-Discord invitation host, JavaScript URL and credential-bearing URL are rejected. Test URLs were examples only and were not added to production config or visited.
- Preview server printed its local listening URL. Browser access timed out; a local HTTP request was blocked by the environment's socket permissions. No successful HTTP response or rendered browser inspection was obtained.

Not verified: visual rendering, mobile overflow, keyboard behavior in a real browser, Cloudflare header application, live DNS, live Discord invitations, dashboard availability, GitHub push or deployment. Follow README's manual checks before production launch. No live accounts or DNS records were changed.
