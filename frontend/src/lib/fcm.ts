/**
 * FCM token helper. Initialized by the firebase boot file so components
 * can call getFCMToken() without importing the boot module (avoids circular deps).
 */
import type { Messaging } from 'firebase/messaging';
import { getToken } from 'firebase/messaging';
import { getApps, initializeApp } from 'firebase/app';
import { getMessaging, isSupported } from 'firebase/messaging';
import { getFirebaseWebConfig, getMissingFirebaseConfigKeys } from './firebaseConfig';

let messagingInstance: Messaging | null = null;
let vapidKeyValue: string | undefined;

export function initFCM(messaging: Messaging, vapidKey: string | undefined): void {
  messagingInstance = messaging;
  vapidKeyValue = vapidKey;
}

async function ensureMessagingInitialized(): Promise<void> {
  if (messagingInstance) {
    return;
  }

  const supported = await isSupported();
  if (!supported) {
    throw new Error('Firebase messaging is not supported in this browser.');
  }

  const firebaseConfig = getFirebaseWebConfig();
  const missingConfig = getMissingFirebaseConfigKeys(firebaseConfig);
  if (missingConfig.length > 0) {
    throw new Error(
      `Missing Firebase app config: ${missingConfig.join(', ')}. ` +
      'Set FB_* values in frontend/.env and restart Quasar dev server.'
    );
  }

  const app = getApps().length > 0 ? getApps()[0] : initializeApp(firebaseConfig);
  messagingInstance = getMessaging(app);
}

export async function getFCMToken(): Promise<string | null> {
  await ensureMessagingInitialized();

  if (!vapidKeyValue) {
    throw new Error('Missing Firebase VAPID key (FB_VAPID_KEY).');
  }

  if (!('serviceWorker' in navigator)) {
    throw new Error('Service workers are not supported in this browser.');
  }

  const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
  await navigator.serviceWorker.ready;

  return getToken(messagingInstance, {
    vapidKey: vapidKeyValue,
    serviceWorkerRegistration: registration,
  });
}
