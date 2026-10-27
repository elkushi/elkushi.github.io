// Service worker: makes repeat visits and page changes load from the device
// instead of the network. Free, and it helps most where the connection is slow.
//
//   pages   network first, but if the network takes more than 3 s, the copy
//           saved on the last visit is shown instead
//   assets  served from the saved copy at once, refreshed in the background
//
// Other sites on this domain (the obby game) are left alone.
const CACHE = "site-v1";
const SKIP = /^\/alisa-obby\//;

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    for (const key of await caches.keys()) if (key !== CACHE) await caches.delete(key);
    await self.clients.claim();
  })());
});

async function fromNetwork(req) {
  const res = await fetch(req);
  if (res.ok && res.type === "basic") (await caches.open(CACHE)).put(req, res.clone());
  return res;
}

async function page(req) {
  const net = fromNetwork(req);
  const saved = await caches.match(req, { ignoreSearch: true });
  if (!saved) return net;
  const timeout = new Promise((resolve) => setTimeout(() => resolve(saved), 3000));
  return Promise.race([net.catch(() => saved), timeout]);
}

async function asset(req) {
  const saved = await caches.match(req);
  const net = fromNetwork(req).catch(() => saved);
  return saved || net;
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin || SKIP.test(url.pathname)) return;
  if (req.headers.has("range")) return;  // video seeking: let the browser handle it
  e.respondWith(req.mode === "navigate" ? page(req) : asset(req));
});

// The page sends the links it shows; save those pages quietly so the next
// click opens from the device.
self.addEventListener("message", (e) => {
  const urls = (e.data && e.data.warm) || [];
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    for (const u of urls) {
      if (await cache.match(u, { ignoreSearch: true })) continue;
      try { const res = await fetch(u); if (res.ok) await cache.put(u, res); } catch (err) { /* offline */ }
    }
  })());
});
