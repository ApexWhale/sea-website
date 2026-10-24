# Sleep Eat AFK website — v1.2.1

This is the complete website and Railway member portal, consolidated from the
previous updates. It has not been deployed by this download. Use this guide instead
of the older setup steps. GitHub's Code view is the source of truth for deployment
paths: your confirmed repository has backend and dist directly at its top level.

## Included

- Public page with the requested regional FAQ preserved.
- Removed For Guild Members / Member access / Coming soon section.
- Member Login immediately beside Join Discord on desktop and smaller layouts.
- Member Login starts https://dashboard.sleepeatafk.com/auth/discord, the backend
  redirects to Discord, and approved users return to /members on the dashboard.
- Member and officer verification, encrypted temporary sessions and safe error codes.
- Public /health readiness check that verifies Redis without Discord login.
- Complete files, tests, Dockerfile and configuration examples. No real credentials.

Raid sign-ups and officer management tools are not implemented. Login requires a
correct Discord application, membership and roles; this package does not bypass
checks or prove your current production login issue is resolved.

## 1. Replace files on your Mac

1. Back up the website folder you currently edit.
2. Extract sea-website-v1.2.1.zip in Downloads.
3. Open the extracted sea-website folder. Its contents include backend and dist.
4. Copy the supplied files into matching locations in your EXISTING website folder.
   Replace matching files; merge folder contents so your private .env, .venv and .git
   stay in place. Do not create another nested sea-website folder.
5. If you prefer explicit replacements, replace the four public files
   dist/index.html, dist/styles.css, dist/app.js and dist/config.js, then copy the
   supplied backend files to their matching locations and update the supplied docs
   and VERSION. Original artwork is included and unchanged.
6. Open that existing website folder in VS Code. Use Command+S to save edits.
7. Keep existing Railway variables. Do not paste secrets into any dist file.

The supplied config.js already points to your requested dashboard and preserves
https://discord.gg/DPmpEAwGxE. If you changed that invitation yourself, keep your
current invitation when applying the complete config file. No application data is
migrated; existing session records remain compatible with the same encryption key.

## 2. Test locally

From the folder containing backend and your existing .venv, in VS Code Terminal:

```bash
./.venv/bin/python -m pip install -r backend/requirements-test.txt
cd backend
../.venv/bin/python -m unittest discover -s tests -v
cd ..
```

Expected: 22 tests ending with OK. These simulate Discord and Redis; no real secrets
are needed. The test dependencies no longer require lupa. If your virtual environment
is called venv without a dot, adjust only that folder name in the commands.

Optional public-site preview (requires Node.js):

```bash
node preview.cjs
```

Open http://127.0.0.1:4173. Stop with Ctrl+C. Real OAuth testing uses your deployed
HTTPS dashboard, not the local public-site preview.

## 3. GitHub

In VS Code Source Control, inspect changed files. .venv and private .env files must
not be staged. Stage the changed website/backend files, commit, then Sync Changes.

Commit message:

```text
Release v1.2.1: streamline member login and add Redis health check
```

In GitHub's Code view, confirm backend and dist are visible directly at the root.
If an extra sea-website folder exists there, the files are nested differently; the
settings below assume the flat GitHub layout you confirmed in this conversation.
Local parent folder names do not determine Railway or Cloudflare repository paths.

## 4. Railway settings — website service only

Keep the existing sea-website service; do not create duplicates or change your bot.

| Setting | Value |
| --- | --- |
| Source repository | Your website GitHub repository |
| Branch | main (or the branch you actually pushed) |
| Root Directory | /backend |
| Custom Build Command | Empty |
| Custom Start Command | Empty; Dockerfile supplies it |
| Healthcheck Path | /health |
| Healthcheck Timeout | 120 seconds |

If a manually required start-command field cannot be left empty, use:

```text
gunicorn --config gunicorn.conf.py 'app:create_app()'
```

The app listens on Railway's PORT variable, with 8080 as its fallback. The previously
provided production logs showed 8080. Use the actual current listening port for
Railway public networking.

Required variables on the WEBSITE service in the production environment:

| Name | Source/value |
| --- | --- |
| DISCORD_CLIENT_ID | Client ID from Discord Developer Portal → application → OAuth2 |
| DISCORD_CLIENT_SECRET | Client Secret from the same application; private |
| DISCORD_GUILD_ID | Right-click SEA Discord server icon → Copy Server ID |
| MEMBER_ROLE_IDS | Approved member role ID(s), comma-separated |
| OFFICER_ROLE_IDS | Optional officer role ID(s), comma-separated |
| PUBLIC_BASE_URL | https://dashboard.sleepeatafk.com |
| TOKEN_ENCRYPTION_KEY | Keep your private, generated Fernet key |
| REDIS_URL | Reference to your Redis service's REDIS_URL |

For IDs in Discord, enable User Settings → Advanced → Developer Mode. Copy role
IDs from Server Settings → Roles. Do not use @everyone. Officer roles grant both
member and officer access; member roles grant only member access. Guild ownership
or Discord Administrator permission alone does not bypass the configured role checks.

For Redis, add a Redis database service in the SAME project/environment if absent.
On sea-website → Variables use Add Reference → actual Redis service → REDIS_URL.
If the service is named Redis, the reference is ${{Redis.REDIS_URL}}. Do not enter
just REDIS_URL as the value. Keep the database private; no public proxy is needed.

Only if no encryption key exists yet, generate one locally:

```bash
./.venv/bin/python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Save it privately in Railway. A key exposed in screenshots should be rotated;
changing the key invalidates previous sessions. No bot token is required here.
Apply pending Railway changes and deploy the new GitHub commit.

## 5. Discord and the dashboard domain

In https://discord.com/developers/applications select the SAME application as the
client ID/secret. Under OAuth2 → Redirects save exactly:

```text
https://dashboard.sleepeatafk.com/auth/discord/callback
```

In Railway sea-website → Settings → Networking add dashboard.sleepeatafk.com to
THIS web service. Set its target to the current listening port (previously 8080).
In Cloudflare DNS add the exact CNAME and verification records Railway supplies.
Use DNS only for the dashboard CNAME during this setup, preserving apex, www and
email records. Wait for Railway domain verification and HTTPS to finish. Adding
DNS alone does not register the custom domain with Railway.

## 6. Cloudflare Pages settings

Keep your existing Pages project linked to the website repository:

| Setting | Value |
| --- | --- |
| Production branch | main (or your actual production branch) |
| Framework preset | None |
| Root directory | Empty |
| Build command | exit 0 |
| Build output directory | dist |
| Start command | None; Pages does not need one |
| Discord/Redis secrets | None; keep them in Railway |

Only dist is public. Do not publish backend or the repository root. Keep the existing
Pages custom domain sleepeatafk.com and optional www. After pushing, wait for Pages
to deploy, then reload the website with Command+Shift+R.

## 7. Verify health and login

Open https://dashboard.sleepeatafk.com/health. Healthy HTTP 200 response:

```json
{"status":"ok","redis":"connected","version":"1.2.1"}
```

Redis failure returns HTTP 503:

```json
{"status":"unavailable","redis":"unavailable","version":"1.2.1"}
```

This endpoint confirms backend/Redis readiness, not Discord credentials. If the app
cannot start because variables are missing, no health endpoint can be served yet.
Railway healthchecks gate deployments; they do not replace ongoing monitoring.

Then open https://sleepeatafk.com/:
- The member-access coming-soon section must be gone.
- Member Login must sit immediately beside Join Discord.
- Click Member Login → Discord consent → dashboard /members.
- A configured officer can open /officers. An ordinary member must be denied there.
- An account without an approved role must not enter the member area.
- Sign out; /members must then require sign-in.
- Check mobile layout, FAQ/class accordions, images and invitation links.

If login fails, note the visible Reference and the Railway log line starting
'Discord request rejected'. These diagnostics exclude tokens, secrets and raw
Discord response text. TOKEN refers to login exchange, PROFILE to profile lookup,
MEMBERSHIP to the server check. ROLE-MISSING means membership succeeded but no
approved role matched. SCREENING-PENDING means complete Discord server screening.
Start each test from the dashboard home or website button; never refresh/reuse an
old callback URL. Do not share callback URLs containing authorization codes.

## Rollback

Restore your backup's changed files, commit and push. Cloudflare Pages can roll back
to a previous successful deployment; revert GitHub too so the next push does not
restore the change. Railway can redeploy its previous successful deployment. Keep
existing environment variables unless diagnosing a confirmed configuration error.
No stored data migration is required.

## Verification and official references

See VERIFICATION.md for checks performed and limits. This download did not commit,
push, change DNS or deploy your services.

- https://docs.discord.com/developers/topics/oauth2
- https://docs.discord.com/developers/resources/user#get-current-user-guild-member
- https://docs.railway.com/builds/dockerfiles
- https://docs.railway.com/deployments/healthchecks
- https://docs.railway.com/networking/domains/working-with-domains
- https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
