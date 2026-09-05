/* HM16 Library Service Worker - v6: 192 icon everywhere, 512 splash only */
const CACHE = 'hm16-v6';
// Only cache files that are guaranteed to exist. Missing PNGs must NOT
// fail install (c.addAll is atomic — one 404 used to block v3 forever).
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then(async (c) => {
      await Promise.all(
        APP_SHELL.map((u) => c.add(u).catch(() => null))
      );
      // Best-effort: cache icons / catalog if they exist, ignore if not.
      await Promise.all([
        './HM16LIB_192.png',
        './HM16LIB_512.png',
        './Bookicon.png',
        './api/books.json'
      ].map((u) => c.add(u).catch(() => null)));
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // API JSON: stale-while-revalidate
  if (url.pathname.endsWith('/api/books.json')) {
    e.respondWith(
      caches.open(CACHE).then(async (cache) => {
        const cached = await cache.match(req);
        const network = fetch(req).then((res) => {
          if (res.ok) cache.put(req, res.clone());
          return res;
        }).catch(() => cached);
        return cached || network;
      })
    );
    return;
  }

  // EPUB/PDF: network-first (large, don't bloat cache), fallback to cache
  if (/\.(epub|pdf)$/i.test(url.pathname)) {
    e.respondWith(fetch(req).catch(() => caches.match(req)));
    return;
  }

  // App shell: network-first for pages (so updates show immediately),
  // cache-first for static assets, network fallback when offline
  if (req.mode === 'navigate' || req.destination === 'document') {
    e.respondWith(
      fetch(req).then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => caches.match(req).then((hit) => hit || caches.match('./index.html')))
    );
    return;
  }
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok && url.origin === self.location.origin) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }))
  );
});
