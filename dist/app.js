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
  // The Railway member portal is supplied in backend/.
  // A real authentication service must be deployed before setting memberLoginUrl.
  const login = httpsUrl(config.memberLoginUrl);
  if (login) {
    document.querySelectorAll("[data-member-login], [data-member-enter]").forEach(link => {
      link.href = login.href;
      link.hidden = false;
    });
    const faq = document.querySelector("[data-member-faq]");
    if (faq) faq.textContent = "Approved SEA members can sign in with Discord using Member Login. Access depends on your guild role. Raid sign-ups are not available yet; check Discord for current activities.";
    document.querySelector("[data-member-status]").textContent = "Sign in with Discord.";
    document.querySelector("[data-member-note]").textContent = "Sign in with Discord to verify your SEA membership. Access requires an approved guild role. Raid sign-ups are not available yet.";
  }
})();
