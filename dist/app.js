(() => {
  "use strict";
  const config = window.SEA_CONFIG || {};
  function connect(key, selector, note, message) {
    let url;
    try { url = new URL(config[key]); } catch { return; }
    if (url.protocol !== "https:" || url.username || url.password) return;
    if (key === "discordUrl" && !["discord.gg", "discord.com"].includes(url.hostname)) return;
    document.querySelectorAll(selector).forEach(link => {
      link.href = url.href;
      link.hidden = false;
    });
    document.querySelector(note).textContent = message;
  }
  connect("discordUrl", "[data-discord]", "[data-discord-note]", "Connect with Sleep Eat AFK on Discord.");
  connect("dashboardUrl", "[data-dashboard]", "[data-dashboard-note]", "Continue to the Sleep Eat AFK member dashboard.");
})();
