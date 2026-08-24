const CACHE = "finansys-shell-v2";
const SHELL = [
  "/static/css/app.css",
  "/static/js/theme.js",
  "/static/js/pwa.js",
  "/static/icons.svg",
  "/static/app-icon.svg",
  "/static/app-icon-192.png",
  "/static/app-icon-512.png",
  "/manifest.webmanifest"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || url.pathname.startsWith("/api/")) return;
  if (request.mode === "navigate") return;
  if (!url.pathname.startsWith("/static/") && url.pathname !== "/manifest.webmanifest") return;
  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request).then((response) => {
      if (response.ok) caches.open(CACHE).then((cache) => cache.put(request, response.clone()));
      return response;
    }))
  );
});
