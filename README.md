# Sleep Eat AFK [SEA] — landing page

Version **1.0.0**. Complete static website for **sleepeatafk.com**, ready for GitHub and Cloudflare Pages. No build tools, packages, API keys, or database required. All runtime assets are local, including original SVG landscape and crest. This package does not include a member dashboard application.

## What is included

- `dist/index.html`: complete landing page.
- `dist/styles.css`: desktop/mobile design and reduced-motion support.
- `dist/config.js`: optional public Discord and dashboard links.
- `dist/app.js`: validates HTTPS links and displays configured buttons.
- `dist/assets/`: original landscape illustration and SEA crest concept.
- `dist/_headers`: Cloudflare security headers.
- `dist/404.html`, `robots.txt`, `sitemap.xml`: error page and search discovery.
- `preview.cjs`: optional local preview server.
- `CONTENT-SOURCES.md`: factual boundaries and source audit.
- `CHANGELOG.md`, `VERSION`: release information.

## 1. Open on Windows

1. Download the project ZIP. Right-click it in File Explorer → **Extract All**. Extract to a new folder, for example `Documents\sleepeatafk-site`.
2. Open **Visual Studio Code** → **File → Open Folder** → select the extracted folder containing this README and `dist`.
3. For a quick look, open `dist` in File Explorer and double-click `index.html`. The main page also works directly from disk.
4. For HTTP preview, install the LTS version of Node.js from https://nodejs.org/ if needed. Restart VS Code after installing.
5. In VS Code select **Terminal → New Terminal**. Run:

```powershell
node preview.cjs
```

6. Open http://127.0.0.1:4173 in your browser. Stop the server with **Ctrl+C** when finished. No `npm install` is needed.

## 2. Add your real links (optional)

The site is deployable with both links empty. It honestly says the links will be shared when available and shows no broken buttons.

In VS Code, open `dist/config.js`. If you have a Discord invitation and a live dashboard, replace the entire file using this full-file pattern, filling in your actual public HTTPS URLs between the quotation marks. Leave either value empty until that destination exists:

```javascript
// Public links only. Never put tokens or passwords in this file.
// Empty links hide the corresponding buttons until real destinations are ready.
window.SEA_CONFIG = Object.freeze({
  discordUrl: "",
  dashboardUrl: ""
});
```

Press **Ctrl+S**, then refresh the browser. Discord URLs must use `discord.gg` or `discord.com`. The dashboard must use HTTPS. Links open in the same tab. All config is public; do not add secrets.

## 3. Put the project on GitHub

Simple option using VS Code:

1. Install Git for Windows from https://git-scm.com/downloads/win if needed, then restart VS Code.
2. In the VS Code left sidebar, click **Source Control** → **Initialize Repository**.
3. Enter `Release SEA landing page v1.0.0` in the commit message box. Click **Commit**, and accept staging all files if prompted. If Git asks for name/email, follow the displayed instructions using your GitHub identity.
4. Click **Publish Branch**, sign into GitHub, name the repository `sleepeatafk-site`, and choose private or public.
5. Ensure the repository root contains `dist`, rather than another enclosing folder. Do not include other guild projects or credentials.

Alternative initial commit commands from the project folder, after Git is installed:

```powershell
git init
git add .
git commit -m "Release SEA landing page v1.0.0"
git branch -M main
```

Then use **Publish Branch** in VS Code to create the remote repository.

For later edits: save, open Source Control, review changes, enter a commit message, click **Commit**, then **Sync Changes** to push.

## 4. Deploy to Cloudflare Pages

1. Sign into your Cloudflare account. Open **Workers & Pages → Create application → Pages → Import an existing Git repository** (sometimes labelled **Connect to Git**).
2. Connect GitHub and select `sleepeatafk-site`.
3. Use these exact settings:

| Setting | Value |
| --- | --- |
| Project name | `sleepeatafk` (or another available name) |
| Production branch | `main` |
| Framework preset | None |
| Build command | `exit 0` |
| Build output directory | `dist` |
| Root directory | Leave blank |
| Environment variables | None |

4. Click **Save and Deploy**. Open the returned `pages.dev` URL and check the page before connecting your domain.
5. In that Pages project select **Custom domains → Set up a custom domain**. Enter `sleepeatafk.com` and follow Cloudflare's DNS activation steps. Add the domain through Pages first; a manually added DNS record alone does not associate it with the project.
6. Wait for Cloudflare to show the domain as active and issue HTTPS. Open https://sleepeatafk.com/.
7. Optionally add `www.sleepeatafk.com` through the same Custom domains screen. This package serves the same page there and uses the apex domain as its canonical URL; it does not force a www redirect.

If existing apex DNS records conflict, review their purpose before replacing them; preserve unrelated email and subdomain records. Future GitHub pushes trigger Pages deployments automatically.

An alternate one-time upload is possible through Pages Direct Upload: upload the contents of `dist`, with `index.html` at the upload root. Prefer Git integration for ongoing edits; switching a Direct Upload project to Git integration requires creating a new Pages project.

## 5. Connect a Railway dashboard later

The landing page stays on Pages. Your dashboard is a separate Railway web service.

1. Open Railway → your dashboard project → the web service → **Settings → Networking → Public Networking → Custom Domain**.
2. Add `dashboard.sleepeatafk.com`. Use the service's correct listening port if asked.
3. Railway will show DNS record(s). In Cloudflare → `sleepeatafk.com` → **DNS → Records**, add the exact record types, names, and values Railway gives you, including any ownership verification record. Do not invent a Railway CNAME target. Start the CNAME as **DNS only** while verifying the service and certificate.
4. Wait until Railway confirms verification and HTTPS works at https://dashboard.sleepeatafk.com/.
5. Set `dashboardUrl` in `dist/config.js` to that working HTTPS URL, save, commit, and push. Pages will update the link.

This link does not add authentication or create the dashboard. Keep login and permission enforcement in your Railway application. Discord bot processes alone do not serve a web dashboard unless a web server is included.

## How to test

- Check at desktop width and at 390px / 320px phone widths: no horizontal scrolling; text and navigation remain readable.
- Use Tab and Enter to reach links. The skip link should appear when focused.
- Click The guild, Connect, Discover the guild, and Back to the top.
- Empty config: no Discord/dashboard buttons. Real config: buttons appear and open the intended destinations.
- Disable JavaScript: page content and section links still work; optional external buttons remain hidden.
- On HTTP preview, visit `/missing-page` to inspect the 404. On Pages confirm it returns HTTP 404.
- On Pages inspect HTTPS, favicon, and browser console for missing files/errors. Cloudflare headers apply on Pages, not on the simple local preview.

## Rollback

In Cloudflare Pages, open **Deployments**, find a known working production deployment, and use its rollback action. Also revert the corresponding change in GitHub so the next push does not restore the problem. This site stores no member data.

## Verification and release notes

See `VERIFICATION.md` for checks actually performed. Domain connection, GitHub push, Railway configuration and live deployment are not performed by this download.

## Official deployment references

- https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- https://developers.cloudflare.com/pages/configuration/custom-domains/
- https://developers.cloudflare.com/pages/get-started/git-integration/
- https://developers.cloudflare.com/pages/get-started/direct-upload/
- https://docs.railway.com/networking/domains/working-with-domains

## Ready-to-copy commit message

`Release SEA landing page v1.0.0`
