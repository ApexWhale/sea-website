# Changelog

## 1.1.2 — 24 October 2026
- Replaced ambiguous Discord failures with stage-specific diagnostic references.
- Added sanitized error logging without tokens, secrets, user IDs or response bodies.
- Distinguished missing roles from pending server screening.
- Startup errors now name missing variables and explain invalid Redis/key settings.
- Uses the canonical Discord OAuth token endpoint documented by Discord.
- Existing access rules and session storage remain compatible.

## 1.1.1 — 24 October 2026
- Removed the native lupa dependency that blocked macOS test installation.
- Replaced Lua rate limiting with atomic Redis transactions, preserving fixed expiry.
- Added expiry and concurrent-update failure tests.
- Added macOS instructions and nested-folder deployment settings.

## 1.1.0 — 24 October 2026
- Updated the regional FAQ with the exact requested wording.
- Added a Python Railway member portal using Discord authorization-code OAuth2.
- Added live guild membership, screening and role checks, with a separate officer page.
- Added encrypted temporary Redis sessions, one-use OAuth state, secure host-only cookies,
  sign-out CSRF protection, rate limits and safe error pages.
- Preserved public-site artwork, styles, sections, class content, anchors and invitation links.
- Added deployment instructions, complete backend configuration, tests and secret settings.
- Login stays unconnected until the backend is deployed and the public URL is enabled.
- Raid registration and officer management tools are not included.

## 1.0.0
- Original static landing page supplied in sea-website.zip.
