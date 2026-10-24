# Sleep Eat AFK — v1.1.1

Complete replacement website plus Discord member portal. Public landing page:
Cloudflare Pages. Private member and officer pages: a separate Railway Python web
service with Redis. Nothing has been committed, deployed, or connected to Discord.

## What changed

- The requested regional FAQ wording is applied exactly.
- Existing artwork, styling, public sections, class content and invitations are retained.
- `backend/` adds Discord sign-in, a verified member page, an officer-only page and sign-out.
- `dist/app.js` supports the real member portal link after you enable it.
- `dist/config.js` intentionally keeps memberLoginUrl empty until deployment succeeds.
- `.gitignore`, VERSION, release notes and documentation are updated.
- No existing file must be deleted. The ZIP excludes old `.git` history and Mac metadata.

This release provides member access, not raid scheduling or officer management tools.
An officer role grants both member and officer access. A member role grants only
member access. Discord Administrator permission alone does not grant website access.

For macOS setup and the nested folder layout, see MAC-SETUP.md.

## 1. Apply the complete files in Windows / VS Code

1. Download and extract the ZIP using File Explorer → right-click → Extract All.
2. Back up your existing website folder. Keep its `.git` folder in place.
3. Copy everything INSIDE the extracted `sea-website` folder into your existing
   website repository folder. Choose **Replace the files in the destination**.
   Include `.gitignore`. Do not create a second nested `sea-website` folder.
4. Open VS Code → File → Open Folder → choose your existing repository folder.
   You should see `dist`, `backend`, README.md and VERSION at the top level.
5. Save any subsequent configuration edits with Ctrl+S. No secrets go in `dist`.

All supplied source files are complete replacements; no code merging is required.

## 2. Discord application and roles

1. Open https://discord.com/developers/applications → New Application. Name it
   `Sleep Eat AFK Members`. Use an application you control; a separate application
   avoids changing your existing Discord bot.
2. Open OAuth2. Copy Client ID and Client Secret into Railway variables later.
   Reset/generate the client secret there if necessary. Never send it in chat or GitHub.
3. Under OAuth2 → Redirects add exactly:
   `https://dashboard.sleepeatafk.com/auth/discord/callback`
   Save Changes. This must exactly match your chosen PUBLIC_BASE_URL plus the callback path.
4. In the Discord desktop app → User Settings → Advanced → enable Developer Mode.
5. Right-click your SEA server icon → Copy Server ID. This is DISCORD_GUILD_ID.
6. Server Settings → Roles → use the role menu/Copy Role ID for the approved guild
   member role. Put that ID into MEMBER_ROLE_IDS. Separate multiple IDs with commas.
7. Copy officer role IDs into OFFICER_ROLE_IDS, or leave it empty to disable officers.
   Do not use @everyone or a role automatically given to every server visitor.
8. Assign those roles only to approved members/officers. Complete server membership
   screening before testing. Existing Discord role assignment remains your authority.

No bot token, bot installation, Administrator permission, privileged intents, or
email scope is required. The app requests only `identify guilds.members.read` and
checks `/users/@me/guilds/{your server ID}/member` on the server.

## 3. GitHub

For an EXISTING repository, open VS Code → Terminal → New Terminal (PowerShell):

```powershell
git status
git add .
git diff --cached --stat
git commit -m "Release v1.1.1: Discord member login and regional FAQ update"
git push
```

Before committing, use Source Control to review staged files; `.env` must not appear.
If Git asks for your identity, use your own GitHub name/email. You can also enter the
commit message in Source Control, click Commit, then Sync Changes.

For a NEW repository: Source Control → Initialize Repository → stage and commit →
Publish Branch → Publish to GitHub private repository. A private repository can
still serve a public Cloudflare website. Use the provided `.gitignore`. Do not add
a license unless you intend to grant reuse rights; this package adds none. Existing
repository licensing remains your responsibility.

## 4. Railway backend (a separate web service)

Do not replace your running Discord bot service or its start command.

1. In Railway create a new project, or open your existing project and add a NEW
   service → GitHub Repo → select the website repository and branch `main`.
2. Open the new service → Settings → Source → Root Directory: `/backend`.
   The Dockerfile is inside that folder and supplies the start command. Leave custom
   build/start commands empty. The public website is not served by this service.
3. In the same project choose New → Database → Redis. Keep Redis private; do not
   create a public TCP proxy just for this app.
4. On the web service → Variables, add the settings below. Use Add Reference to
   connect REDIS_URL to the Redis service's REDIS_URL. If that service is named
   `Redis`, Railway's reference is `${{Redis.REDIS_URL}}`; select your actual service.
5. Generate a fresh encryption key locally. Install Python 3.12 on Windows (tick
   Add Python to PATH), then run from the website repository in VS Code PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-test.txt
.\.venv\Scripts\python.exe -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy that generated key ONLY into Railway's TOKEN_ENCRYPTION_KEY. It is secret.
Keep the same key across deployments; changing it signs everyone out.

| Railway variable | Value to supply | Secret? |
| --- | --- | --- |
| DISCORD_CLIENT_ID | Your Discord OAuth2 Client ID | No |
| DISCORD_CLIENT_SECRET | Your Discord OAuth2 Client Secret | Yes |
| DISCORD_GUILD_ID | SEA server ID | No |
| MEMBER_ROLE_IDS | Approved member role IDs, comma separated | No |
| OFFICER_ROLE_IDS | Officer role IDs, comma separated; may be blank | No |
| PUBLIC_BASE_URL | `https://dashboard.sleepeatafk.com` | No |
| TOKEN_ENCRYPTION_KEY | Fresh key generated above | Yes |
| REDIS_URL | Reference to the private Redis connection URL | Yes |

Railway supplies PORT automatically. No Flask signing secret or Discord bot token
is needed: cookies contain random identifiers; sessions live encrypted in Redis.
The backend refuses to start with missing required settings or invalid role IDs.

6. Settings → Deploy → Healthcheck Path: `/health`. Set healthcheck timeout to 120
   seconds if available. This checks Redis connectivity, not Discord credentials.
7. Deploy. Check Logs for a successful Gunicorn start and a healthy deployment.
8. Settings → Networking → Public Networking → Custom Domain → add
   `dashboard.sleepeatafk.com`. If Railway asks for a target port, use the service's
   actual PORT shown in Variables/logs; the app listens on that value (8080 fallback).
9. In Cloudflare → sleepeatafk.com → DNS → Records, add the exact CNAME and any
   verification record Railway displays. Do not guess the CNAME target. Set the
   dashboard CNAME to DNS only during setup, and leave it DNS only for this guide.
   Preserve unrelated DNS and email records.
10. Wait for Railway domain verification and HTTPS to be ready. Open
    `https://dashboard.sleepeatafk.com/health`, then the dashboard home page.
11. Complete the live test checklist below BEFORE enabling the public login link.

If that subdomain already hosts another dashboard, do not overwrite it. Choose a
free subdomain such as `members.sleepeatafk.com` and use it consistently in Railway,
Discord Redirects, PUBLIC_BASE_URL and the full config.js replacement below.

## 5. Cloudflare Pages and enable the button

Keep your existing Pages project if you already have one. Otherwise Cloudflare →
Workers & Pages → Create application → Pages → Connect to Git / Import repository.
Select your website repository and use:

| Setting | Value |
| --- | --- |
| Production branch | main |
| Framework preset | None |
| Root directory | blank (repository root) |
| Build command | exit 0 |
| Build output directory | dist |
| Environment variables | None |

Only `dist` is published. Never select the repository root or `backend` as output.
In the Pages project → Custom domains → Set up a custom domain → add
`sleepeatafk.com`. Add `www.sleepeatafk.com` there too if wanted. Follow the Pages
DNS setup and wait for HTTPS. Do not replace the separate Railway subdomain record.

Once the dashboard passes live tests, replace the ENTIRE `dist/config.js` with:

```javascript
// Public links only. Never add tokens, passwords or private keys.
window.SEA_CONFIG = Object.freeze({
  discordUrl: "https://discord.gg/DPmpEAwGxE",
  memberLoginUrl: "https://dashboard.sleepeatafk.com/auth/discord"
});
```

Save with Ctrl+S. Commit and push:

```powershell
git add dist/config.js
git commit -m "Enable deployed SEA Discord member login"
git push
```

Wait for Pages deployment. The Member Login links now redirect to Discord via your
Railway backend. The static site needs no API keys, cross-origin cookies or CORS.
The default empty value is intentional and safe to publish before backend setup.
The original invitation is preserved; confirm it is still valid for your server.

## 6. How to test locally

Public site: install Node.js LTS, open a new VS Code terminal in the repository:

```powershell
node preview.cjs
```

Open http://127.0.0.1:4173. Confirm exact FAQ copy, navigation, class accordion,
FAQ accordions, artwork and invitation links at desktop and phone width. Ctrl+C stops it.

Backend automated tests, after the Python installation commands above:

```powershell
cd backend
..\.venv\Scripts\python.exe -m unittest discover -s tests -v
cd ..
```

These tests use fake Redis and fake Discord responses. They need no real secrets,
server role changes or network calls. Production cookies require HTTPS; plain
localhost is intentionally not a complete live OAuth test environment. Use the
Railway HTTPS deployment for real sign-in. Do not run Gunicorn directly on Windows.

## 7. Live verification checklist

- Sign in with a member role: /members works; /officers returns a denial.
- Sign in with an officer role: both pages work.
- Sign in with an account outside SEA, without an approved role, or still pending
  server screening: access is denied. No member data should be shown.
- Remove the officer role while signed in, then reload /officers: denied. Remove
  all approved roles or leave the server, then reload /members: denied.
- Cancel Discord consent: helpful error page, with a fresh sign-in option.
- Sign out and reload /members: session is rejected. Visiting /members in a fresh
  private browser window without signing in is also rejected.
- Check the landing page at phone width, Tab through buttons, and open FAQ/class
  sections. Confirm the region answer matches your request exactly.
- Verify Railway /health and Cloudflare HTTPS. Live consent and DNS are not tested
  by the automated suite. Wait for Redis/Discord recovery if a temporary error appears.

## Security and operational notes

- One-use, browser-bound OAuth state expires after ten minutes. Callback reuse fails.
- Sessions expire within one hour or earlier if the Discord token expires. No refresh
  tokens are retained. Users sign in again. Session expiration is not extended by browsing.
- Cookies are Secure, HttpOnly, SameSite=Lax and host-only with the __Host- prefix.
- Redis holds encrypted profile/token/CSRF records with expiry. Sign-out deletes
  the current session. It does not remove Discord's Authorized Apps permission;
  users can revoke it there themselves. Redis is not a permanent member database.
- Guild roles and screening are checked on every protected page request. Already
  displayed content cannot be recalled from a user's screen; reloading checks again.
- Missing roles, Discord/Redis outages and malformed responses fail closed. Discord
  rate-limit responses temporarily block new API calls. Global sign-in/callback limits
  are 120/minute each; protected page requests are limited to 30/minute per session.
  Global login limits can briefly affect everyone during abuse; tune only with care.
- No OAuth tokens are stored in browser storage or returned in HTML. Gunicorn access
  logging is disabled so callback codes are not recorded by the application. Avoid
  adding proxy/request logging that records callback query strings or request bodies.
- No protected information is shipped in the Cloudflare static files. Future sensitive
  pages/actions must repeat backend authorization; hiding buttons is insufficient.
- Both backend and Redis are Railway services and may incur hosting costs.
- This verifies Discord membership/roles, not game characters or guild roster data.

## Rollback

To disconnect login, replace all of dist/config.js with the original empty-link
version supplied in this ZIP, commit and push. Roll back the Pages deployment if
needed and revert the GitHub change too. Railway supports redeploying the preceding
working deployment. Keep credentials out of rollback commits. If you suspect a
secret leak, reset the Discord secret, rotate TOKEN_ENCRYPTION_KEY and redeploy;
existing sessions become unusable. There is no permanent member-data migration.

## Files and verification

See CHANGELOG.md and VERIFICATION.md. Complete frontend and backend files are in
this folder. The archive includes no repository history, real credentials or session
records. All newly added dependencies are listed under backend/requirements*.txt.

## Official references

- Discord OAuth2: https://docs.discord.com/developers/topics/oauth2
- Discord membership API: https://docs.discord.com/developers/resources/user#get-current-user-guild-member
- Railway domains: https://docs.railway.com/networking/domains/working-with-domains
- Railway healthchecks: https://docs.railway.com/deployments/healthchecks
- Cloudflare Pages: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- Cloudflare custom domains: https://developers.cloudflare.com/pages/configuration/custom-domains/

## Git commit message

Release v1.1.1: Discord member login and regional FAQ update
