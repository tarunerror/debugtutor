// Service Worker for DebugTutor PWA
const CACHE_NAME = 'debugtutor-v1.0.0';
const STATIC_CACHE_NAME = 'debugtutor-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'debugtutor-dynamic-v1.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  // Add other static assets as needed
];

// API endpoints that should be cached
const CACHEABLE_APIS = [
  '/api/parse',
  '/api/analyze'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static files
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_FILES.map(url => new Request(url, {
          cache: 'reload'
        })));
      }).catch((error) => {
        console.log('Service Worker: Error caching static files:', error);
      }),
      
      // Initialize dynamic cache
      caches.open(DYNAMIC_CACHE_NAME)
    ])
  );
  
  // Force activation of new service worker
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME &&
                cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Take control of all pages
      self.clients.claim()
    ])
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  event.respondWith(
    handleFetch(request)
  );
});

async function handleFetch(request) {
  const url = new URL(request.url);
  
  try {
    // Strategy 1: Network First for API calls (with fallback)
    if (isAPIRequest(url)) {
      return await networkFirstStrategy(request);
    }
    
    // Strategy 2: Cache First for static assets
    if (isStaticAsset(url)) {
      return await cacheFirstStrategy(request);
    }
    
    // Strategy 3: Stale While Revalidate for HTML pages
    if (isHTMLRequest(request)) {
      return await staleWhileRevalidateStrategy(request);
    }
    
    // Default: Network First
    return await networkFirstStrategy(request);
    
  } catch (error) {
    console.log('Service Worker: Fetch error:', error);
    
    // Return offline fallback
    return getOfflineFallback(request);
  }
}

// Network First Strategy - try network, fallback to cache
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Cache First Strategy - try cache, fallback to network
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Not in cache, fetch from network
  const networkResponse = await fetch(request);
  
  if (networkResponse.ok) {
    const cache = await caches.open(STATIC_CACHE_NAME);
    cache.put(request, networkResponse.clone());
  }
  
  return networkResponse;
}

// Stale While Revalidate Strategy
async function staleWhileRevalidateStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  // Fetch from network in background
  const networkResponsePromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      const cache = caches.open(DYNAMIC_CACHE_NAME);
      cache.then(c => c.put(request, networkResponse.clone()));
    }
    return networkResponse;
  }).catch(() => {
    // Network failed, but we might have cache
    return cachedResponse;
  });
  
  // Return cached version immediately if available
  return cachedResponse || networkResponsePromise;
}

// Helper functions
function isAPIRequest(url) {
  return url.pathname.startsWith('/api/') || 
         CACHEABLE_APIS.some(api => url.pathname.startsWith(api));
}

function isStaticAsset(url) {
  return url.pathname.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/);
}

function isHTMLRequest(request) {
  return request.headers.get('accept')?.includes('text/html');
}

async function getOfflineFallback(request) {
  const url = new URL(request.url);
  
  // Try to return cached version
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Return offline page for HTML requests
  if (isHTMLRequest(request)) {
    const offlinePage = await caches.match('/offline.html');
    if (offlinePage) {
      return offlinePage;
    }
  }
  
  // Return a basic offline response
  return new Response(
    JSON.stringify({
      error: 'Offline',
      message: 'This feature requires an internet connection.',
      offline: true
    }),
    {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
}

// Handle background sync for failed requests
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered');
  
  if (event.tag === 'background-sync') {
    event.waitUntil(
      handleBackgroundSync()
    );
  }
});

async function handleBackgroundSync() {
  // Handle any queued requests when connection is restored
  console.log('Service Worker: Handling background sync');
  
  // This could be expanded to handle queued API requests
  // For now, just log that sync is working
  return Promise.resolve();
}

// Handle push notifications (for future enhancement)
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New update available!',
    icon: '/static/icon-192x192.png',
    badge: '/static/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Open DebugTutor',
        icon: '/static/icon-192x192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/close-icon.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('DebugTutor', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification click received');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  console.log('Service Worker: Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      type: 'VERSION',
      version: CACHE_NAME
    });
  }
});
