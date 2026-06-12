const CACHE_NAME = 'edukangola-v1';
const OFFLINE_URL = '/offline/';

const ASSETS_TO_CACHE = [
  '/',
  OFFLINE_URL,
  '/static/assets/images/icons/pwa-192x192.png',
  '/static/assets/images/icons/pwa-512x512.png',
  '/static/manifest.json',
  // You can add more critical CSS/JS paths here if needed
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      // Setting {cache: 'reload'} in the new request will ensure that the
      // response isn't fulfilled from the HTTP cache; i.e., it will be from
      // the network.
      await cache.addAll(ASSETS_TO_CACHE.map(url => new Request(url, { cache: 'reload' })));
      self.skipWaiting();
    })()
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      // Enable navigation preload if it's supported.
      if ('navigationPreload' in self.registration) {
        await self.registration.navigationPreload.enable();
      }
      
      // Clean up old caches
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
      self.clients.claim();
    })()
  );
});

self.addEventListener('fetch', (event) => {
  // We only want to call event.respondWith() if this is a navigation request
  // for an HTML page.
  if (event.request.mode === 'navigate') {
    event.respondWith(
      (async () => {
        try {
          // First, try to use the navigation preload response if it's supported.
          const preloadResponse = await event.preloadResponse;
          if (preloadResponse) {
            return preloadResponse;
          }

          // Always try the network first.
          const networkResponse = await fetch(event.request);
          return networkResponse;
        } catch (error) {
          // catch is only triggered if an exception is thrown, which is likely
          // due to a network error.
          // If fetch() returns a valid HTTP response with a response code in
          // the 4xx or 5xx range, the catch() will NOT be called.
          console.log('Fetch failed; returning offline page instead.', error);

          const cache = await caches.open(CACHE_NAME);
          const cachedResponse = await cache.match(OFFLINE_URL);
          return cachedResponse;
        }
      })()
    );
  } else {
    // For non-HTML requests (CSS, JS, images), use cache-first strategy
    event.respondWith(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }
        
        try {
          const networkResponse = await fetch(event.request);
          // Don't cache api requests or third party domains heavily, 
          // but for basic usage we just fetch it
          return networkResponse;
        } catch (error) {
          // Return nothing or a fallback image if it's an image request
          return new Response('', { status: 408, headers: { 'Content-Type': 'text/plain' } });
        }
      })()
    );
  }
});

// Push Notifications Listener
self.addEventListener('push', function(event) {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/static/assets/images/icons/pwa-192x192.png',
      badge: '/static/assets/images/icons/pwa-192x192.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: '2'
      }
    };
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Tratamento do clique na notificação
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});
