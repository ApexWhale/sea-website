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
  // The backend starts Discord OAuth, then redirects approved users to /members.
  // A working default href in HTML also supports visitors without JavaScript.
  const login = httpsUrl(config.memberLoginUrl);
  if (login) {
    document.querySelectorAll("[data-member-login]").forEach(link => {
      link.href = login.href;
      link.hidden = false;
    });
  }
})();
