import unittest
from unittest.mock import patch, Mock
from urllib.parse import urlsplit, parse_qs
import fakeredis
from cryptography.fernet import Fernet
from app import create_app, COOKIE

ORIGIN = 'https://dashboard.example.com'
MEMBER = '11111111111111111'
OFFICER = '22222222222222222'

class AuthTests(unittest.TestCase):
    def setUp(self):
        self.db = fakeredis.FakeRedis(decode_responses=True)
        self.env = dict(DISCORD_CLIENT_ID='33333333333333333', DISCORD_CLIENT_SECRET='test-only',
            DISCORD_GUILD_ID='44444444444444444', MEMBER_ROLE_IDS=MEMBER,
            OFFICER_ROLE_IDS=OFFICER, PUBLIC_BASE_URL=ORIGIN,
            TOKEN_ENCRYPTION_KEY=Fernet.generate_key().decode(), REDIS_URL='redis://unused')
        self.app = create_app(self.env, self.db)
        self.client = self.app.test_client()
        self.roles = [MEMBER]
        self.pending = False
        self.status = 200
        self.calls = patch('app.requests.request', side_effect=self.discord).start()
        self.addCleanup(patch.stopall)

    def discord(self, method, url, **kwargs):
        if url.endswith('/oauth2/token'):
            body = {'access_token': 'private-token', 'token_type':'Bearer', 'expires_in':3600,
                    'scope':'identify guilds.members.read'}
        elif url.endswith('/users/@me'):
            body = {'id':'55555555555555555', 'username':'<script>alert(1)</script>'}
        else:
            body = {'roles': self.roles, 'pending':self.pending}
        return Mock(status_code=self.status, headers={}, json=lambda: body)

    def get(self, path):
        return self.client.get(path, base_url=ORIGIN)

    def start(self):
        r = self.get('/auth/discord')
        self.assertEqual(r.status_code, 302)
        return parse_qs(urlsplit(r.location).query)['state'][0]

    def login(self):
        return self.get('/auth/discord/callback?code=test&state=' + self.start())

    def test_member_login_and_officer_denial(self):
        r = self.login()
        self.assertEqual(r.status_code, 303)
        self.assertIn('Secure', r.headers['Set-Cookie'])
        self.assertIn('HttpOnly', r.headers['Set-Cookie'])
        self.assertIn('SameSite=Lax', r.headers['Set-Cookie'])
        r = self.get('/members')
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(b'<script>alert', r.data)
        self.assertNotIn(b'private-token', r.data)
        self.assertEqual(self.get('/officers').status_code, 403)
        self.assertEqual(r.headers['Cache-Control'], 'no-store')
        for k in self.db.scan_iter('sea:session:*'):
            self.assertNotIn('private-token', self.db.get(k))

    def test_officer_and_live_role_removal(self):
        self.roles = [OFFICER]
        self.assertEqual(self.login().status_code,303)
        self.assertEqual(self.get('/officers').status_code,200)
        self.roles = [MEMBER]
        self.assertEqual(self.get('/officers').status_code,403)
        self.roles = []
        self.assertEqual(self.get('/members').status_code,403)

    def test_no_session(self):
        self.assertEqual(self.get('/members').status_code,401)
        self.assertEqual(self.get('/officers').status_code,401)

    def test_state_required_bound_and_one_time(self):
        state = self.start()
        other = self.app.test_client()
        self.assertEqual(other.get('/auth/discord/callback?code=x&state='+state,base_url=ORIGIN).status_code,400)
        url = '/auth/discord/callback?code=x&state='+state
        self.assertEqual(self.get(url).status_code,303)
        self.assertEqual(self.get(url).status_code,400)

    def test_expired_state_and_cancel(self):
        state = self.start()
        for k in self.db.scan_iter('sea:oauth:*'): self.db.delete(k)
        self.assertEqual(self.get('/auth/discord/callback?code=x&state='+state).status_code,400)
        state = self.start()
        self.assertEqual(self.get('/auth/discord/callback?error=access_denied&state='+state).status_code,400)
        self.calls.assert_not_called()

    def test_pending_and_wrong_roles(self):
        self.pending = True
        self.assertEqual(self.login().status_code,403)
        self.pending = False
        self.roles = ['66666666666666666']
        self.assertEqual(self.login().status_code,403)

    def test_logout_csrf_and_invalidation(self):
        import re
        self.login()
        csrf = re.search(rb'name="csrf" value="([^"]+)"', self.get('/members').data)[1].decode()
        self.assertEqual(self.client.post('/logout',base_url=ORIGIN).status_code,403)
        self.assertEqual(self.client.post('/logout',base_url=ORIGIN,data={'csrf':csrf},headers={'Origin':'https://evil.example'}).status_code,403)
        self.assertEqual(self.client.post('/logout',base_url=ORIGIN,data={'csrf':csrf},headers={'Origin':ORIGIN}).status_code,303)
        self.assertEqual(self.get('/members').status_code,401)

    def test_expired_session(self):
        self.login()
        for k in self.db.scan_iter('sea:session:*'): self.db.delete(k)
        self.assertEqual(self.get('/members').status_code,401)

    def test_upstream_failure_fails_closed(self):
        self.login()
        for status, expected in [(401,403),(404,403),(500,503),(429,503)]:
            self.status = status
            self.assertEqual(self.get('/members').status_code,expected)

    def test_redis_outage(self):
        with patch.object(self.db,'get',side_effect=ConnectionError):
            self.client.set_cookie(COOKIE, 'a'*43, domain='dashboard.example.com')
            self.assertEqual(self.get('/members').status_code,503)

    def test_global_rate_limit(self):
        self.db.set('sea:limit:login',120)
        self.assertEqual(self.get('/auth/discord').status_code,429)

    def test_invalid_config(self):
        for field, value in [('MEMBER_ROLE_IDS',''),('PUBLIC_BASE_URL','http://example.com'),('DISCORD_GUILD_ID','guild-name'),('MEMBER_ROLE_IDS',self.env['DISCORD_GUILD_ID'])]:
            with self.assertRaises(ValueError): create_app(dict(self.env,**{field:value}),self.db)

if __name__ == '__main__': unittest.main()
