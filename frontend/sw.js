// =============================================
// NexCRM — Service Worker (PWA + Offline)
// =============================================

const CACHE_NAME = 'nexcrm-v1';
const STATIC_ASSETS = [
  '/',
  '/dashboard.html',
  '/contacts.html',
  '/deals.html',
  '/tasks.html',
  '/emails.html',
  '/notes.html',
  '/reports.html',
  '/settings.html',
  '/login.html',
  '/register.html',
  '/index.html',
  '/css/main.css',
  '/js/app.js',
  '/js/storage.js',
  '/js/contacts.js',
  '/js/dashboard.js',
  '/js/deals.js',
  '/js/tasks.js',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/manifest.json',
];

// Install — cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch — network-first for API, cache-first for static assets
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // API calls: network-first with offline queue
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Clone and cache successful API responses
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
          return response;
        })
        .catch(() => {
          // Serve from cache if offline
          return caches.match(event.request).then((cached) => {
            if (cached) return cached;
            // Return a generic offline JSON response for API
            return new Response(
              JSON.stringify({ offline: true, message: 'You are offline. Data will sync when connection is restored.' }),
              { headers: { 'Content-Type': 'application/json' }, status: 503 }
            );
          });
        })
    );
    return;
  }

  // Google Fonts and external resources: cache-first
  if (url.origin !== location.origin) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached;
        return fetch(event.request).then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        }).catch(() => cached);
      })
    );
    return;
  }

  // Static assets: cache-first, then network
  event.respondWith(
    caches.match(event.request).then((cached) => {
      const networkFetch = fetch(event.request).then((response) => {
        // Update cache with fresh version
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      }).catch(() => cached);

      return cached || networkFetch;
    })
  );
});
