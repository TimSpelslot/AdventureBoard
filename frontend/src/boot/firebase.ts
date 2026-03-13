import { boot } from 'quasar/wrappers';
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, isSupported, Messaging } from 'firebase/messaging';
import { initFCM } from '../lib/fcm';
import { getFirebaseWebConfig, getMissingFirebaseConfigKeys } from '../lib/firebaseConfig';

const firebaseConfig = getFirebaseWebConfig();

const missingConfig = getMissingFirebaseConfigKeys(firebaseConfig);
const firebaseApp = missingConfig.length === 0
  ? initializeApp(firebaseConfig)
  : null;

// 3. Extend the Vue interface so TypeScript knows about $messaging
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $messaging: Messaging;
  }
}

export default boot(({ app }) => {
  void (async () => {
    if (missingConfig.length > 0 || !firebaseApp) {
      console.warn(
        `Firebase config is incomplete. Missing: ${missingConfig.join(', ')}. ` +
          'Set FB_* values in frontend/.env and restart Quasar dev server.'
      );
      return;
    }

    const supported = await isSupported();
    if (!supported) {
      console.warn('Firebase messaging is not supported in this browser.');
      return;
    }

    const messaging = getMessaging(firebaseApp);
    app.config.globalProperties.$messaging = messaging;
    initFCM(messaging, process.env.FIREBASE_VAPID_KEY);
  })();
});

// We export these for direct use in the component logic
export { getToken };