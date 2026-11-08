const CACHE = 'dzvonymo-v3';
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './locales/uk.json',
  './locales/ru.json',
  './locales/en.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png',
  './fonts/oswald-cyrillic-700-normal.woff2',
  './fonts/oswald-latin-700-normal.woff2',
  './fonts/manrope-cyrillic-500-normal.woff2',
  './fonts/manrope-latin-500-normal.woff2',
  './fonts/manrope-cyrillic-600-normal.woff2',
  './fonts/manrope-latin-600-normal.woff2',
  './fonts/manrope-cyrillic-800-normal.woff2',
  './fonts/manrope-latin-800-normal.woff2'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function put(req, res) {
  if (res && (res.ok || res.type === 'opaque')) {
    const copy = res.clone();
    caches.open(CACHE).then(c => c.put(req, copy));
  }
  return res;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(res => put('./index.html', res)).catch(() => caches.match('./index.html'))
    );
    return;
  }

  if (url.origin === location.origin && url.pathname.includes('/locales/')) {
    e.respondWith(
      caches.match(req).then(hit => {
        const fresh = fetch(req).then(res => put(req, res)).catch(() => hit);
        return hit || fresh;
      })
    );
    return;
  }

  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => put(req, res))));
});
