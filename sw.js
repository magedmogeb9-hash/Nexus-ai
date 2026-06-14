// NexusAI Service Worker — Offline Support
const CACHE_NAME = 'nexusai-v1.0';
const ASSETS = [
  '/',
  '/index.html',
  '/style.css',
  '/app.js',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap',
];

// Install — cache all assets
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.allSettled(
        ASSETS.map(url => cache.add(url).catch(() => {}))
      );
    })
  );
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
  clients.claim();
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
});

// Fetch — cache first for assets, network first for API
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API calls — always network, never cache
  if (url.hostname === 'api.anthropic.com' || url.pathname.includes('/v1/')) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(JSON.stringify({
          error: { message: 'لا يوجد اتصال بالإنترنت. يعمل NexusAI في الوضع المحلي.' }
        }), { headers: { 'Content-Type': 'application/json' } })
      )
    );
    return;
  }

  // Google Fonts — cache first
  if (url.hostname.includes('fonts.')) {
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(event.request, clone));
        return res;
      }))
    );
    return;
  }

  // App assets — cache first, fallback to index.html
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(res => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(event.request, clone));
        }
        return res;
      }).catch(() => caches.match('/index.html'));
    })
  );
});

// Background sync for cloud saves
self.addEventListener('sync', (event) => {
  if (event.tag === 'cloud-sync') {
    event.waitUntil(doCloudSync());
  }
});

async function doCloudSync() {
  // Sync pending data when back online
  console.log('NexusAI: Background sync triggered');
}
