// Al-Furqan AI - Progressive Web App (PWA) & Trusted Web Activity (TWA) Service Worker v15.0
const CACHE_NAME = 'alfurqan-twa-v15.0-cache';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/index.css?v=14.0',
    '/app.js?v=14.0',
    '/i18n.js?v=14.0',
    '/manifest.json',
    'https://fonts.googleapis.com/css2?family=Amiri+Quran&family=Amiri:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap'
];

// 1. INSTALL & PRE-CACHE CORE ASSETS
self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch((err) => {
                console.warn('[SW] Pre-cache warning:', err);
            });
        })
    );
});

// 2. ACTIVATE & CLEAN UP STALE CACHES
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// 3. FETCH STRATEGY: Stale-While-Revalidate for UI, Network-First for API, Cache-First for Audio/Fonts
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Bypass non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // API Routes: Network First with graceful error handling
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return new Response(JSON.stringify({ 
                        status: 'offline', 
                        message: 'Офлайн режим. Пожалуйста, проверьте подключение к интернету.' 
                    }), {
                        headers: { 'Content-Type': 'application/json' }
                    });
                })
        );
        return;
    }

    // Audio files: Cache First for offline playback
    if (url.pathname.endsWith('.mp3') || url.hostname.includes('everyayah.com')) {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) return cachedResponse;
                return fetch(event.request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const clone = networkResponse.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                    }
                    return networkResponse;
                });
            })
        );
        return;
    }

    // Static Assets & UI: Stale-While-Revalidate
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    const clone = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return networkResponse;
            }).catch(() => cachedResponse);

            return cachedResponse || fetchPromise;
        })
    );
});

// 4. PUSH NOTIFICATIONS FOR PRAYER TIMES & DAILY AYAHS (TWA Compliant)
self.addEventListener('push', (event) => {
    let data = { title: 'Al-Furqan AI', body: 'Уақыт намазы жақындады / Время намаза' };
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: 'https://cdn-icons-png.flaticon.com/512/3247/3247167.png',
        badge: 'https://cdn-icons-png.flaticon.com/512/3247/3247167.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1,
            url: data.url || '/'
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// 5. NOTIFICATION CLICK ROUTING
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const targetUrl = (event.notification.data && event.notification.data.url) ? event.notification.data.url : '/';
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then((clientList) => {
            for (let client of clientList) {
                if (client.url === targetUrl && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});

