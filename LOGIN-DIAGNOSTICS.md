# Login diagnostics — v1.1.2

The old message combined Discord HTTP 401, 403 and 404 errors from three different
requests. A screenshot of that message cannot identify the failed request. This
update adds stage-specific references without bypassing membership or role checks.
It does not claim the live Discord configuration has been fixed.

## Apply on macOS

1. Extract sea-website-login-diagnostics-v1.1.2.zip in Downloads.
2. Open the extracted sea-website folder.
3. Copy the supplied files into the matching paths in your existing website folder:
   backend/app.py, backend/tests/test_auth.py, backend/templates/portal.html,
   VERSION, CHANGELOG.md, VERIFICATION.md and LOGIN-DIAGNOSTICS.md.
   Replace only those files. Keep dist/config.js, .venv, .env and Railway variables.
4. In VS Code open a terminal in the folder containing backend and .venv. Run:

```bash
cd backend
../.venv/bin/python -m unittest discover -s tests -v
cd ..
```

Expected: 19 tests ending with OK. Dependencies are unchanged from v1.1.1.
5. In VS Code Source Control stage these files and commit:
   Add safe Discord login diagnostics (v1.1.2)
6. Click Sync Changes. Wait for Railway to deploy that commit successfully. Your
   verified GitHub layout has backend directly at the root, so Railway Root
   Directory remains /backend. Do not change it based on local nesting.
7. Open https://dashboard.sleepeatafk.com/ and start a fresh Discord login.
   Do not reuse or refresh an old callback URL.
8. If it fails, report the new Reference text. In Railway Deploy Logs search for
   'Discord request rejected' and share that line. It contains no credentials,
   user IDs, OAuth codes, access tokens or raw Discord error text.

## What references mean

- TOKEN-401: the token exchange received HTTP 401. Check application credentials.
  An allowlisted oauth_error=invalid_client in logs confirms client rejection.
- TOKEN-400: login exchange rejected; the logged OAuth error distinguishes
  invalid_client, invalid_grant and other recognized errors.
- PROFILE-401/403: Discord rejected the profile request, before guild role checks.
- MEMBERSHIP-403/404: Discord rejected the server membership lookup. Verify the
  signed-in account belongs to the configured server, the server ID is correct,
  and the app has the requested guilds.members.read scope. This is not yet a
  verdict on the account's role IDs.
- MEMBERSHIP-401: Discord rejected the bearer authorization; sign in again.
- ROLE-MISSING: Discord returned membership successfully, but none of its roles
  match configured member/officer roles.
- SCREENING-PENDING: Discord returned membership with screening still pending.
- A 429 reference: Discord rate limited the request; wait before retrying.
- A NETWORK reference: the backend could not complete the network request.

Unknown/raw response text is intentionally not logged. No access checks have been
removed. Tokens remain encrypted in Redis and cookies remain host-only and secure.
Startup errors now name missing variable names and explain invalid Redis/key values
without printing their values. The token URL now matches Discord's documented
canonical endpoint, https://discord.com/api/oauth2/token; this is not proof that
the prior URL caused the observed failure.

Official references:
https://docs.discord.com/developers/topics/oauth2
https://docs.discord.com/developers/resources/user#get-current-user-guild-member

No deployment, production login or DNS change was performed by this update.
Rollback: restore the previous app.py/template/tests/VERSION from v1.1.1 and commit
and push. Existing session format is unchanged; keep your current encryption key.
