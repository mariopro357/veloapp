/* ═══════════════════════════════════════════════════
   VELOAPP — SERVICE WORKER (Offline First)
   Cache-first para assets estáticos
   ═══════════════════════════════════════════════════ */

const CACHE_NAME = 'veloapp-v5';
const ASSETS = [
  './',
  './index.html',
  './app.js',
  './style.css',
  './security.js',
  './ai_service.js',
  './manifest.json'
];

// Instalar y cachear assets core
self.addEventListener('install', evt => {
  evt.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

// Limpiar caches viejas al activar
self.addEventListener('activate', evt => {
  evt.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Estrategia: Cache First para assets locales, Network First para APIs externas
self.addEventListener('fetch', evt => {
  const url = new URL(evt.request.url);

  // Siempre online para APIs externas (BCV, Gemini)
  if (
    url.hostname === 've.dolarapi.com' ||
    url.hostname === 'generativelanguage.googleapis.com' ||
    url.hostname === 'tessdata.projectnaptha.com'
  ) {
    evt.respondWith(
      fetch(evt.request).catch(() => new Response('{"error":"offline"}', {
        headers: { 'Content-Type': 'application/json' }
      }))
    );
    return;
  }

  // Cache first para recursos locales y CDN estáticos
  evt.respondWith(
    caches.match(evt.request).then(cached => {
      if (cached) return cached;
      return fetch(evt.request).then(response => {
        // Sólo cachear respuestas válidas (no errores)
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(evt.request, clone));
        return response;
      }).catch(() => {
        // Fallback a index.html si falla todo (app shell)
        if (evt.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});
