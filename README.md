# Ну шо, дзвонимо?

Одноекранна PWA-забавка: дисковий номеронабирач вирішує, чи дзвонити тобі комусь
просто зараз. Відповідь майже завжди «ТАК» — і до неї додається свіжа відмазка.

Побудовано за зразком [«Ну шо, додеп?»](https://super-dodep-228.netlify.app/),
але на іншу тему: замість ставок — телефонні дзвінки, замість зеленого сукна —
нічний бурштин, а замість кубика — диск старого апарата.

Диск можна крутити пальцем: встроми в отвір, протягни до упору й відпусти. Він
поїде назад із тріскотінням, як справжній, і відповідь загориться на зеленому
дисплеї в центрі — там, де на справжньому апараті лежить картка з номером.
Цифри на диску нічого не означають, це просто цифри; шанс на «ТАК» задається
лише в налаштуваннях. Кнопка «Крути диск!» робить те саме для тих, хто не тягне.

## Що всередині

| Файл | Призначення |
| --- | --- |
| `index.html` | уся сторінка: CSS і JS вбудовані, без збірки |
| `locales/{uk,ru,en}.json` | тексти інтерфейсу + репліки «ТАК» і «НІ» |
| `manifest.webmanifest`, `sw.js` | PWA: встановлення на телефон і офлайн |
| `icons/` | іконки, згенеровані `tools/make-icons.py` |
| `tools/make-icons.py` | малює іконки з того самого контуру слухавки, що й сайт |
| `tools/inline-locales.py` | вшиває локалі у сторінку, щоб вона працювала й без мережі |
| `fonts/` | шрифти Oswald і Manrope (woff2, кирилиця + латиниця), підключені через `@font-face` |
| `package.json`, `capacitor.config.json` | Android-обгортка на Capacitor |
| `tools/build-web.mjs` | копіює сайт у `www/` перед пакуванням в APK |
| `tools/make-android-icons.py` | малює іконки лаунчера в `android/app/src/main/res/` |
| `android/` | згенерований Capacitor-проєкт Android |

Мова визначається так: `?lang=uk` в URL → збережений вибір (cookie / localStorage) →
`uk` за замовчуванням. Якщо в неукраїнському файлі бракує репліки, береться українська.

## Запуск

```bash
python -m http.server 5173
```

Далі http://127.0.0.1:5173/. Відкрити `index.html` просто з диска теж можна — усі
тексти вшиті в сторінку, тож усі три мови працюють і без сервера.

Перегенерувати іконки:

```bash
python tools/make-icons.py
```

## Налаштування

- Повзунок «Шанс на «ТАК»» у налаштуваннях — від 0% (режим «не турбувати») до 100%.
- Звук вимикається там же. Тріскотіння, удар об упор і поклик синтезуються через
  Web Audio просто в браузері — жодних аудіофайлів у репозиторії немає.
- Нові репліки додаються в `locales/*.json`: однаковий `id` у всіх мовах, текст свій.
  Після правок треба оновити вшиті копії — `python tools/inline-locales.py`
  (а `--check` скаже, чи вони розійшлись із файлами).
- Посилання на банку: заповнити `DONATE_URL` на початку скрипта в `index.html`.
  Поки воно порожнє, кнопка показує жартівливий тост.

## Деплой

Статика без збірки — будь-який хостинг. Для Netlify: publish directory — корінь
репозиторію, build command не потрібен.

## Android-додаток (повністю офлайн)

Той самий сайт пакується в APK через [Capacitor](https://capacitorjs.com): сторінка,
локалі, іконки й шрифти лежать усередині додатка, мережа не потрібна. Шрифти вшиті
в `fonts/`, а не тягнуться з Google Fonts. Сервіс-воркер в APK не потрібен, тож
`sw.js` і маніфест у збірку не потрапляють. Орієнтація зафіксована портретна.

### Що потрібно встановити (один раз)

| Що | Версія | Примітка |
| --- | --- | --- |
| Node.js + npm | 18+ | перевірено на 24 |
| JDK | **21** | Capacitor 7 не збирається на 17: `invalid source release: 21` |
| Android SDK | platform `android-35`, build-tools `35.0.0`, platform-tools | досить command-line tools, Android Studio не обов'язкова |

Windows:

```powershell
winget install EclipseAdoptium.Temurin.21.JDK
```

Android command-line tools: завантажити `commandlinetools-win-*_latest.zip` з
https://developer.android.com/studio#command-line-tools-only і розпакувати так, щоб
`sdkmanager.bat` лежав у `%LOCALAPPDATA%\Android\Sdk\cmdline-tools\latest\bin\`.
Потім (у Git Bash, `yes` приймає ліцензії Google):

```bash
export JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-21..."   # ваш шлях до JDK 21
SDK="$LOCALAPPDATA/Android/Sdk"
yes | "$SDK/cmdline-tools/latest/bin/sdkmanager.bat" --sdk_root="$SDK" --licenses
"$SDK/cmdline-tools/latest/bin/sdkmanager.bat" --sdk_root="$SDK" "platform-tools" "platforms;android-35" "build-tools;35.0.0"
```

Android Studio замість цього теж підходить: вона сама ставить SDK і JDK.

### Збірка debug-APK

```bash
npm install
echo "sdk.dir=C:/Users/<ви>/AppData/Local/Android/Sdk" > android/local.properties
export JAVA_HOME="..."   # JDK 21
npm run apk
```

`local.properties` у `.gitignore`, його треба створити на кожній машині. `npm run apk`
робить три речі: `build:web` (копіює сайт у `www/`), `cap sync android` (кладе
`www/` в Android-проєкт) і `gradlew assembleDebug`. Результат:
`android/app/build/outputs/apk/debug/app-debug.apk` (~4,5 МБ).

Після будь-яких змін у `index.html`, `locales/`, `icons/` чи `fonts/` достатньо знову
`npm run apk`. Лише оновити вміст без збірки: `npm run sync`.

### Встановлення на телефон

Перекинути APK на телефон (кабель, месенджер), відкрити й дозволити встановлення з
цього джерела. Або через USB із увімкненим налагодженням:
`adb install -r app-debug.apk`.

### Іконки лаунчера

`python tools/make-android-icons.py` перемальовує `mipmap-*` тим самим рендерером,
що й веб-іконки. Фон адаптивної іконки (`#0A0613`) задано в
`android/app/src/main/res/values/ic_launcher_background.xml`.

### Для Google Play

Debug-APK підписаний тимчасовим ключем, для магазину він не годиться. Потрібні release-збірка
`.aab` (`gradlew bundleRelease`), власний keystore (його не губити й не комітити),
акаунт розробника Google Play ($25 одноразово) і політика конфіденційності.
Ідентифікатор додатка: `com.orddreamer.dzvonymo` (змінюється в `capacitor.config.json`,
після зміни в магазині його вже не поміняти).

### Підводні камені

- `Failed to find ... JDK` / `invalid source release: 21`: `JAVA_HOME` вказує не на JDK 21.
- `SDK location not found`: немає `android/local.properties` або `ANDROID_HOME`.
- `license ... not accepted`: прийняти ліцензії командою `sdkmanager --licenses`.
- Папки `www/`, `node_modules/`, `android/build/` і `*.apk` не комітяться (див. `.gitignore`).
