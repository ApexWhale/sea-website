"""SEA member portal: confidential OAuth client; all authorization is server-side."""
import hashlib
import json
import os
import re
import secrets
from urllib.parse import urlencode, urlsplit

import redis
import requests
from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, abort, g, make_response, redirect, render_template, request
from werkzeug.exceptions import HTTPException

API = 'https://discord.com/api/v10'
COOKIE = '__Host-sea_session'
STATE_COOKIE = '__Host-sea_oauth'
SCOPES = {'identify', 'guilds.members.read'}


def create_app(settings=None, store=None):
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=8192)
    env = dict(os.environ if settings is None else settings)
    required = ('DISCORD_CLIENT_ID', 'DISCORD_CLIENT_SECRET', 'DISCORD_GUILD_ID',
                'MEMBER_ROLE_IDS', 'PUBLIC_BASE_URL', 'TOKEN_ENCRYPTION_KEY', 'REDIS_URL')
    if any(not env.get(k, '').strip() for k in required):
        raise ValueError('Set every required variable listed in backend/.env.example.')
    base = env['PUBLIC_BASE_URL'].rstrip('/')
    parsed = urlsplit(base)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.path or
            parsed.query or parsed.fragment or parsed.username or parsed.password or parsed.port):
        raise ValueError('PUBLIC_BASE_URL must be an HTTPS origin without a path or port.')
    def ids(name):
        result = {v.strip() for v in env.get(name, '').split(',') if v.strip()}
        if any(not re.fullmatch(r'[0-9]{17,20}', v) for v in result):
            raise ValueError(name + ' must contain Discord IDs, not role names.')
        return result
    members, officers = ids('MEMBER_ROLE_IDS'), ids('OFFICER_ROLE_IDS')
    for key in ('DISCORD_CLIENT_ID', 'DISCORD_GUILD_ID'):
        if not re.fullmatch(r'[0-9]{17,20}', env[key]):
            raise ValueError(key + ' must be a Discord ID.')
    if not members or env['DISCORD_GUILD_ID'] in members | officers:
        raise ValueError('Use explicit member roles; @everyone cannot grant access.')
    cipher = Fernet(env['TOKEN_ENCRYPTION_KEY'].encode())
    db = store if store is not None else redis.Redis.from_url(
        env['REDIS_URL'], socket_connect_timeout=3, socket_timeout=3, decode_responses=True)
    callback = base + '/auth/discord/callback'

    def key(prefix, value):
        return 'sea:' + prefix + ':' + hashlib.sha256(value.encode()).hexdigest()

    def cookie(response, name, value, ttl):
        response.set_cookie(name, value, max_age=ttl, secure=True, httponly=True,
                            samesite='Lax', path='/')

    def clear(response, name):
        response.delete_cookie(name, secure=True, httponly=True, samesite='Lax', path='/')

    def limited(bucket, limit, seconds):
        # Global buckets avoid trusting user-supplied proxy/IP headers.
        k = 'sea:limit:' + bucket
        # WATCH keeps concurrent workers from creating or updating a stale window.
        # Redis transactions avoid a Lua/native-library dependency in local tests.
        for _ in range(5):
            with db.pipeline() as pipe:
                try:
                    pipe.watch(k)
                    count = int(pipe.get(k) or 0)
                    if count >= limit:
                        abort(429, 'Too many requests. Please wait a minute and try again.')
                    pipe.multi()
                    pipe.incr(k)
                    if count == 0:
                        pipe.expire(k, seconds)
                    pipe.execute()
                    return
                except redis.WatchError:
                    continue
        abort(503, 'Member access is busy. Please try again shortly.')

    def discord(method, path, token=None, data=None):
        if db.exists('sea:discord_backoff'):
            abort(503, 'Discord is busy. Please try again shortly.')
        try:
            response = requests.request(method, API + path, data=data,
                headers={'Authorization': 'Bearer ' + token} if token else {},
                timeout=(3, 10), allow_redirects=False)
        except requests.RequestException:
            abort(503, 'Discord is unavailable. Please try again shortly.')
        if response.status_code == 429:
            try:
                delay = min(3600, max(1, int(float(response.headers.get('Retry-After', '60'))) + 1))
            except ValueError:
                delay = 60
            db.setex('sea:discord_backoff', delay, '1')
            abort(503, 'Discord is busy. Please try again shortly.')
        if response.status_code in (401, 403, 404):
            abort(403, 'Access could not be verified. Sign in again or ask a guild officer to check your membership and roles.')
        if not 200 <= response.status_code < 300:
            abort(503, 'Discord could not complete the request. Please try signing in again shortly.')
        try:
            result = response.json()
            if not isinstance(result, dict):
                raise ValueError()
            return result
        except ValueError:
            abort(503, 'Discord returned an unexpected response. Please try again later.')

    def membership(token):
        member = discord('GET', '/users/@me/guilds/' + env['DISCORD_GUILD_ID'] + '/member', token)
        roles = set(member.get('roles', []))
        if member.get('pending') or not roles.intersection(members | officers):
            abort(403, 'You need an approved SEA member role and completed Discord server screening. Please contact a guild officer.')
        return bool(roles & officers)

    def session():
        sid = request.cookies.get(COOKIE, '')
        if not re.fullmatch(r'[A-Za-z0-9_-]{43}', sid):
            return None
        raw = db.get(key('session', sid))
        if not raw:
            return None
        try:
            return json.loads(cipher.decrypt(raw.encode()).decode())
        except (InvalidToken, ValueError):
            db.delete(key('session', sid))
            return None

    def verified(officer=False):
        record = session()
        if not record:
            abort(401, 'Your session has ended. Please sign in with Discord.')
        limited('session:' + key('id', request.cookies[COOKIE]), 30, 60)
        is_officer = membership(record['token'])
        if officer and not is_officer:
            abort(403, 'This page is available only to SEA officers.')
        g.record, g.officer = record, is_officer
        return record

    @app.after_request
    def headers(response):
        response.headers.update({
            'Cache-Control': 'no-store', 'Pragma': 'no-cache',
            'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'no-referrer', 'X-Robots-Tag': 'noindex, nofollow',
            'Strict-Transport-Security': 'max-age=31536000',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
            'Content-Security-Policy': "default-src 'none'; style-src 'self'; img-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        })
        return response

    @app.errorhandler(Exception)
    def error(exc):
        if isinstance(exc, HTTPException):
            status, message = exc.code, exc.description
        else:
            # Never log exception bodies, URLs, credentials, tokens or authorization codes.
            app.logger.error('Request failed (%s)', type(exc).__name__)
            status, message = 503, 'Member access is temporarily unavailable. Please try again shortly.'
        return render_template('portal.html', error=message, title='Member access'), status

    @app.get('/health')
    def health():
        db.ping()
        return {'status': 'ok'}

    @app.get('/')
    def home():
        return render_template('portal.html', title='Your SEA home', login=True)

    @app.get('/auth/discord')
    def login():
        limited('login', 120, 60)
        old = request.cookies.get(STATE_COOKIE, '')
        if old:
            db.delete(key('oauth', old))
        browser, state = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        db.setex(key('oauth', browser), 600, state)
        response = redirect('https://discord.com/oauth2/authorize?' + urlencode({
            'client_id': env['DISCORD_CLIENT_ID'], 'response_type': 'code',
            'redirect_uri': callback, 'scope': 'identify guilds.members.read',
            'state': state, 'prompt': 'consent'}))
        cookie(response, STATE_COOKIE, browser, 600)
        return response

    @app.get('/auth/discord/callback')
    def oauth_callback():
        limited('callback', 120, 60)
        browser = request.cookies.get(STATE_COOKIE, '')
        expected = db.getdel(key('oauth', browser)) if browser else None
        state = request.args.get('state', '')
        if not expected or not secrets.compare_digest(expected, state):
            abort(400, 'This sign-in link expired or was already used. Please start again.')
        if request.args.get('iss', 'https://discord.com') != 'https://discord.com':
            abort(400, 'Unexpected sign-in provider. Please start again.')
        if 'error' in request.args:
            abort(400, 'Discord sign-in was cancelled. You can try again when ready.')
        code = request.args.get('code', '')
        if not code or len(code) > 2048:
            abort(400, 'Missing sign-in code. Please start again.')
        result = discord('POST', '/oauth2/token', data={
            'client_id': env['DISCORD_CLIENT_ID'], 'client_secret': env['DISCORD_CLIENT_SECRET'],
            'grant_type': 'authorization_code', 'code': code, 'redirect_uri': callback})
        if not SCOPES.issubset(set(result.get('scope', '').split())):
            abort(403, 'Discord did not grant the permissions needed to verify your membership.')
        token = result.get('access_token')
        if not isinstance(token, str) or result.get('token_type', '').lower() != 'bearer':
            abort(503, 'Discord did not return a valid sign-in token.')
        user = discord('GET', '/users/@me', token)
        if not user.get('id') or user.get('bot'):
            abort(403, 'A personal Discord account is required.')
        membership(token)
        ttl = min(3600, int(result.get('expires_in', 0)) - 30)
        if ttl <= 0:
            abort(401, 'Your Discord authorization expired. Please start again.')
        sid = secrets.token_urlsafe(32)
        record = {'token': token, 'name': user.get('global_name') or user.get('username') or 'Member',
                  'user_id': user['id'], 'csrf': secrets.token_urlsafe(32)}
        db.setex(key('session', sid), ttl, cipher.encrypt(json.dumps(record).encode()).decode())
        old = request.cookies.get(COOKIE)
        if old:
            db.delete(key('session', old))
        response = redirect('/members', code=303)
        cookie(response, COOKIE, sid, ttl)
        clear(response, STATE_COOKIE)
        return response

    @app.get('/members')
    def member_page():
        record = verified()
        return render_template('portal.html', title='Welcome home, ' + record['name'],
                               record=record, officer=g.officer)

    @app.get('/officers')
    def officer_page():
        record = verified(officer=True)
        return render_template('portal.html', title='Officer area', record=record, officer=True, officer_page=True)

    @app.post('/logout')
    def logout():
        record = session()
        if (request.headers.get('Origin') != base or not record or
                not secrets.compare_digest(record['csrf'], request.form.get('csrf', ''))):
            abort(403, 'The sign-out request could not be verified. Reload your member page and try again.')
        db.delete(key('session', request.cookies[COOKIE]))
        response = redirect('/', code=303)
        clear(response, COOKIE)
        return response

    return app
