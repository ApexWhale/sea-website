(() => {
  "use strict";
  const config = window.SEA_CONFIG || {};
  function httpsUrl(value) {
    try {
      const url = new URL(value);
      return url.protocol === "https:" && !url.username && !url.password ? url : null;
    } catch { return null; }
  }
  const discord = httpsUrl(config.discordUrl);
  if (discord && ["discord.gg", "discord.com"].includes(discord.hostname)) {
    document.querySelectorAll('a[data-discord], a[href^="https://discord.gg/"], a[href^="https://discord.com/invite/"]').forEach(link => {
      link.href = discord.href;
      link.hidden = false;
    });
  }
  // The dashboard is intentionally absent from this release.
  // A real authentication service must be deployed before setting memberLoginUrl.
  const login = httpsUrl(config.memberLoginUrl);
  if (login) {
    document.querySelectorAll("[data-member-login], [data-member-enter]").forEach(link => {
      link.href = login.href;
      link.hidden = false;
    });
    document.querySelector("[data-member-status]").textContent = "Continue to your account.";
    document.querySelector("[data-member-note]").textContent = "Use the connected member service to sign in. Available account features are managed by that service.";
  }
})();
