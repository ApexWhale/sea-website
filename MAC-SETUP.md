# macOS setup — v1.1.1

## Fix the lupa installation error

Version 1.1.0's tests requested fakeredis[lua], which pulled in lupa. The screenshot
shows that lupa's native build failed; the earlier compiler error is not visible.
Version 1.1.1 removes that dependency and uses Redis transactions instead of Lua.
No compiler installation or existing environment deletion is required for this fix.

1. Extract the v1.1.1 archive in Downloads, separately from your existing website.
2. In your existing INNER sea-website folder (the one containing .venv/backend/dist),
   replace these files with the complete files from the archive at matching paths:
   - backend/app.py
   - backend/requirements-test.txt
   - backend/tests/test_auth.py
   - backend/templates/portal.html
   - VERSION
   - CHANGELOG.md
   - VERIFICATION.md
   Copy MAC-SETUP.md there too. Keep your .venv, config.js and any private .env intact.
3. In VS Code, right-click the INNER sea-website folder → Open in Integrated Terminal.
4. Run:

```bash
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r backend/requirements-test.txt
cd backend
../.venv/bin/python -m unittest discover -s tests -v
cd ..
```

Expected: 14 tests ending with OK. Do not use the old requirements-test.txt. If pip
still asks to install lupa, check that the updated file says fakeredis==2.40.0
without [lua]. A previously installed lupa can remain; the updated code does not
use it. You do not need to regenerate an encryption key you already saved.

## New macOS Python environment (only if you do not already have one)

Install a supported standard Python from https://www.python.org/downloads/macos/.
Complete Install Certificates.command in its Applications/Python folder and reopen
VS Code. From the INNER website folder:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r backend/requirements-test.txt
```

Generate a key only if you have not already generated and saved one:

```bash
./.venv/bin/python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Save the complete value in Railway as TOKEN_ENCRYPTION_KEY. Do not send it in chat
or commit it to GitHub. Use Command+S to save files on macOS.

## Your nested layout and deployment paths

Your screenshot shows:

```text
sea-website/              ← Git repository and .git
  sea-website/            ← run Python commands from here
    .venv/
    backend/
    dist/
```

As long as you retain that layout, use:
- Railway Root Directory: /sea-website/backend
- Cloudflare Pages Root Directory: sea-website
- Cloudflare Pages output directory: dist
- Cloudflare Pages build command: exit 0

Follow README.md for the Discord application, Railway variables, Redis, custom
DNS, live login tests and public login activation. Its root-directory instructions
assume a flat layout; use the nested values above instead for your current folder.
The dashboard has not been deployed or live-tested by this update.

## Commit

After tests pass, review changes in VS Code Source Control, confirm .venv and .env
are excluded, stage the updated files, commit and Sync Changes. Suggested message:

Fix macOS test installation by removing Lua dependency (v1.1.1)
