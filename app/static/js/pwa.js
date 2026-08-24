let installPrompt = null;
const installButton = document.querySelector("#install-app-button");

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/service-worker.js"));
}

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPrompt = event;
  if (installButton) installButton.hidden = false;
});

installButton?.addEventListener("click", async () => {
  if (!installPrompt) return;
  await installPrompt.prompt();
  installPrompt = null;
  installButton.hidden = true;
});

document.querySelector("#mobile-more")?.addEventListener("click", () => {
  document.body.classList.add("menu-open");
});

const hashTarget = window.location.hash ? document.querySelector(window.location.hash) : null;
if (hashTarget instanceof HTMLDetailsElement) hashTarget.open = true;
