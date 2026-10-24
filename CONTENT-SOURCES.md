# Content sources and boundaries — v1.2.1

The uploaded sea-website.zip is the source of truth for the existing website. Its
Alliance/PvE copy, class descriptions, SEA branding, artwork and Discord invitation
are preserved. This release does not independently verify those guild facts or the
invitation. No new raid times, member counts, recruitment claims or officer names
have been invented. The regional FAQ wording was explicitly supplied by the owner.

The target dashboard.sleepeatafk.com address is a proposed setup address, not a
claim that a service or DNS record already exists. No credentials were supplied.
The public login now links to the requested dashboard Discord sign-in endpoint.

Official references checked for the implementation and deployment guide:
- Discord OAuth2: https://docs.discord.com/developers/topics/oauth2
- Current user guild member: https://docs.discord.com/developers/resources/user#get-current-user-guild-member
- Cloudflare static HTML: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- Cloudflare custom domains: https://developers.cloudflare.com/pages/configuration/custom-domains/
- Railway domains: https://docs.railway.com/networking/domains/working-with-domains
- Railway healthchecks: https://docs.railway.com/deployments/healthchecks

The portal verifies a Discord server membership and configured Discord roles. It
does not verify in-game character ownership or communicate automatically with WoW.
