// Copies the static site into www/ - the folder Capacitor packs into the APK.
// sw.js and the manifest stay out: the app is already offline, a service worker adds nothing.
import { cpSync, rmSync, mkdirSync } from 'node:fs';

rmSync('www', { recursive: true, force: true });
mkdirSync('www');
for (const p of ['index.html', 'locales', 'icons', 'fonts']) cpSync(p, `www/${p}`, { recursive: true });
console.log('www/ ready');
