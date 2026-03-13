importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// Initialize the Firebase app in the service worker
// Use the exact same config as your boot file
firebase.initializeApp({
  apiKey: "AIzaSyAIaw4iziendZyWpdWhZM-zMOXX9GRoXjw",
  authDomain: "event-board-a6a72.firebaseapp.com",
  projectId: "event-board-a6a72",
  storageBucket: "event-board-a6a72.firebasestorage.app",
  messagingSenderId: "408173153245",
  appId: "1:408173153245:web:41f010d01157d4f239c434",
});

const messaging = firebase.messaging();

// This handles background notifications automatically
messaging.onBackgroundMessage((payload) => {
  console.log('Received background message ', payload);

  // Use payload.data instead of payload.notification
  const notificationTitle = payload.data.title || 'Adventure Board Update';
  const notificationOptions = {
    body: payload.data.body || '',
    icon: '/spelslot-logo.png', 
    data: {
      // Pulling from our custom data key
      clickUrl: payload.data.click_action || '/' 
    }
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', (event) =>{
    event.notification.close();

    // If click_action is "OPEN_APP", we use the root origin (e.g., signup.spelslot.nl)
    let targetUrl = event.notification.data?.clickUrl;
    if (targetUrl === 'OPEN_APP' || !targetUrl) {
      targetUrl = self.location.origin + '/#/'; 
    }

    event.waitUntil(
        clients.matchAll({type: 'window', includeUncontrolled: true}).then((windowClients) => {
            for (let client of windowClients) {
                if (client.url.includes(targetUrl) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
