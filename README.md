# Zeekr EN/UA — English & Ukrainian for the Zeekr 001 head unit

Translates the Chinese / Russian user interface of the **Zeekr 001 (2024, pre-facelift)** head unit into
**English** and **Ukrainian** — **without modifying any system app**.

It works with Android **Runtime Resource Overlays (RRO)**: small APKs that contain only translated text
and that Android layers on top of the original app. The manager app **"Zeekr EN/UA"** installs,
switches and removes these overlays. If you remove everything, the car goes back to the original text.

> [!WARNING]
> **This project was vibe-coded with an AI assistant.** The code, the translations and this README were
> written with the help of an AI coding assistant, and then tested by hand on one car.
> It is shared as-is, with no warranty (see [LICENSE](LICENSE)). Read the code before you install it.
> Only use it while parked. You use it at your own risk.
>
> **Tested only on Zeekr OS 5.1.5.** On any other Zeekr OS version there is no warranty that it installs,
> works, or translates everything. Apps and string names change between firmware versions.

---

## Contents

- [What gets translated](#what-gets-translated)
- [Compatibility](#compatibility)
- [Installing](#installing)
- [Using the app](#using-the-app)
- [Using it together with zSupport or "Жабка translator"](#using-it-together-with-zsupport-or-жабка-translator)
- [Apps you don't have](#apps-you-dont-have)
- [Chinese app names in the app drawer (fixing labels)](#chinese-app-names-in-the-app-drawer-fixing-labels)
- [Uninstalling](#uninstalling)
- [Known limitations](#known-limitations)
- [Building from source](#building-from-source)
- [Making a release (tag + APK)](#making-a-release-tag--apk)
- [Adding or fixing translations](#adding-or-fixing-translations)
- [Porting to another Zeekr OS version](#porting-to-another-zeekr-os-version)
- [Adding a new language](#adding-a-new-language)
- [Adding a new language button](#adding-a-new-language-button)
- [Repository layout](#repository-layout)
- [Contributing](#contributing)

---

## What gets translated

| Area | Package |
|---|---|
| Vehicle Settings (Driving, Zeekr AD, Safety, Connectivity, Energy) | `com.geely.pma.settings` |
| Climate | `com.geely.pma.climate` |
| Phone | `com.ecarx.btphone` |
| Sentry mode | `zeekr.bx.sentry` |
| Camera / Dashcam | `ecarx.camera.dvr` |
| 3D car view (pet mode, rest mode, car wash) | `com.zeekr.carlauncher3d` |
| Home screen (cards, weather, app editor; replaces Russian) | `ecarx.launcher3` |
| Status bar | `com.android.systemui` |
| User center & driving profiles | `ecarx.membercenter` |
| Quick panel | `ecarx.notificationcenterui` |
| Housekeeper, Car Manager | `com.zeekr.housekeeper`, `com.zeekr.managerapplication` |
| ZEEKR App Store | `com.zeekrlife.market` |
| My car (trips, energy, tires) | `com.ecarx.mycar` |
| Voice assistant settings | `com.zeekr.speech.setting` |
| System updates (OTA) | `ecarx.upgrade` |
| NZP / driver assistance pilot | `com.zeekr.autopilot` |
| Scene modes, Light Show, Smart scenes | `com.geely.pma.bs.modes`, `com.geely.pma.lightshow`, `com.ecarx.smartscene` |
| Media: ZEEKR Music, media center, radio / USB / Bluetooth music, media switcher, video casting | `com.zeekr.media`, `com.zeekr.mediacenter`, `com.ecarx.multimedia`, `com.zeekr.mediaswitch`, `com.zeekr.dlnavideo` |
| User manual, feedback, account center, profile | `com.ecarx.usermanual`, `com.zeekr.feedback`, `com.ecarx.accountcenter`, `com.ecarx.profile` |
| **App names in the drawer** (English) for the apps above and for MX Player, PDF Reader – Hi Read, microG, 语言切换 (Language Switch), iQIYI, Bilibili, Thunder KTV | `com.zeekrenglish.lbl.*` |

The English layer is always on. Ukrainian is an optional extra layer on top of it. Any string that has
no Ukrainian translation yet is shown in English.

## Compatibility

- **Car:** Zeekr 001, model year 2024, pre-facelift head unit, **Zeekr OS 5.1.5** (Android 9,
  `msmnile_gvmq-userdebug`, build signed with **test-keys**). This is the only combination that has been tested.
- **Other Zeekr OS versions: no warranty.** It may install and partly work, but newer or older firmware can
  rename, add or remove strings and apps. Then some text stays Chinese/Russian, or an overlay has no effect.
  Overlays never modify the original apps, so the worst case is untranslated text. **Turn all OFF** /
  **Remove everything** restores the original state. If you test on another version, please open an issue and
  say what works and what doesn't. To support your firmware, see
  [Porting to another Zeekr OS version](#porting-to-another-zeekr-os-version).
- The manager app uses `android:sharedUserId="android.uid.system"` and is signed with the **public AOSP
  test platform key**. That is the only way it can install and switch overlays without root. **On a head unit
  signed with release keys, Android will refuse to install it.** Other Zeekr models and firmware versions
  are untested.
- The instrument cluster (driver display) runs a separate OS, so its text cannot be translated from Android.

## Installing

1. Download `ZeekrEnglish-<version>.apk` from the
   [Releases](https://github.com/tlytvyn/Zeekr_001_chinese_translator_app/releases) page.
2. Install it on the head unit, using either method:
   - **adb** (USB debugging enabled):
     ```bash
     adb install -r ZeekrEnglish-<version>.apk
     ```
     The USB link on these cars drops on large transfers. The APK is about 2 MB, so this is usually fine.
     If it fails, retry or use the flash-drive method.
   - **Flash drive:** copy the APK to a FAT32 USB stick (on macOS:
     `diskutil eraseDisk FAT32 ZEEKR MBRFormat /dev/diskN`, then eject properly). Open it with a file
     manager on the car (e.g. FX File Explorer) and tap it to install.
3. Open **"Zeekr EN/UA"** from the app drawer.
4. Tap **Install / update**. The app installs every bundled overlay whose target app exists on your car and
   switches it on. This takes about a minute.
5. Tap **Restart head unit** (parked only). The home screen, status bar and drawer only reload their text after
   a restart. Other apps pick it up the next time you open them.

**Updating:** install the newer APK over the old one (`adb install -r …`), open the app, and tap
**Install / update** again. Only overlays with a newer version are reinstalled.

## Using the app

| Control | What it does |
|---|---|
| **Switch per row** | Turns the translation for one app on or off. The status line shows `ON` / `OFF`, `Not installed`, or `App not present on this car`. |
| **Українська / English** | Picks the interface language. **English** turns off the Ukrainian layer, so you see English only. **Українська** turns on the Ukrainian overlays on top of English. Both buttons also set the system language and the vehicle (HMI) language to English (see below). |
| **Install / update** | Installs any missing or outdated overlays. Apps that are not on your car are skipped. |
| **Turn all OFF** | Disables every overlay. The apps show their original text again, and nothing is uninstalled. |
| **Restart head unit** | Reboots the head unit, needed for the launcher, SystemUI and drawer. |
| **Remove everything** | Uninstalls all overlays and then the manager app itself. |

Why the system language stays **English** even in Ukrainian mode: SystemUI keeps the Android system language
in sync with the vehicle (HMI) language. Many Zeekr apps also fall back to Chinese when they see a locale they
don't ship, such as `uk`. So the Ukrainian text is written *into the English resources* of each app, and the
system locale stays `en`.

If an app still shows the old text after you switch, close and reopen it. For the home screen, status bar and
drawer, restart the head unit.

## Using it together with zSupport or "Жабка translator"

Many cars already have **zSupport** and/or **"Жабка" translator** installed. This app was designed to sit
next to them:

- **No system app is modified, and no locale guard runs.** This app does not fight other tools over the system
  language in the background.
- **Language:** zSupport can switch the system language. Pressing **Українська** or **English** in this app
  sets the system and vehicle language to **English**, which is what the overlays need. If you later pick
  another language in zSupport, zSupport wins until you press one of our language buttons again. To keep things
  simple, set the language in zSupport to **English** and pick EN/UA only in this app.
- **Other translation overlays (e.g. Жабка):** if two tools translate the same app with overlays, Android uses
  the overlay with the **higher priority** for each string. Ours use priority **10** (English text), **20**
  (app names) and **30** (Ukrainian). If you see mixed or unexpected text in an app, use the per-app switch in
  this app (or in the other tool) so that only one translation is active for that app. To list everything that
  is installed:
  ```bash
  adb shell cmd overlay list
  ```
- **Turn all OFF** and **Remove everything** only touch our own packages (`com.zeekrenglish.*`). Overlays and
  settings from zSupport or Жабка are never changed.

## Apps you don't have

Not every car has every app (Tencent, iQIYI, Bilibili, KTV, microG, MX Player, …). This is handled
automatically:

- **Install / update** skips every overlay whose target app is not installed. This covers English, Ukrainian
  and app-name overlays.
- The row shows **"App not present on this car"**, and its switch is disabled.
- If you install the app later, tap **Install / update** again and its translation is added.

## Chinese app names in the app drawer (fixing labels)

The app drawer belongs to SystemUI (`statusbar/pma`). It reads each app's launcher label and **caches** it in
`/data/user_de/0/com.android.systemui/files/app_current.xml`. If an app still shows a Chinese name, either:

- that app has no label overlay yet (only the apps listed above are covered), or
- the drawer is still showing its cached name.

### Option A — quick fix on your car (root, no rebuild)

The head unit's `adb shell` can become root with `su 0`. Back up the cache file, edit the labels on your
computer, and put the file back:

```bash
# 1. copy the cache to /sdcard and pull it (small file, safe over adb)
adb shell su 0 cp /data/user_de/0/com.android.systemui/files/app_current.xml /sdcard/app_current.xml
adb pull /sdcard/app_current.xml
cp app_current.xml app_current.xml.orig            # keep a backup

# 2. edit app_current.xml: change the text inside <label>…</label> for the app, e.g.
#    <label>腾讯爱趣听</label>  ->  <label>Tencent Music</label>
#    Keep the file on ONE line, and do not change <package_name> or <activity>.

# 3. push it back without changing the file's owner or permissions, then restart SystemUI
adb push app_current.xml /sdcard/app_current.xml
adb shell su 0 sh -c 'cat /sdcard/app_current.xml > /data/user_de/0/com.android.systemui/files/app_current.xml'
adb shell su 0 sh -c 'kill -9 $(pidof com.android.systemui)'
```

SystemUI may rebuild this cache when an app is installed or updated, which brings the original name back.
For a fix that survives that, use Option B.

### Option B — permanent: add a label overlay (rebuild)

1. Get the app's APK from the car. Use the chunked puller, because it survives USB drops:
   ```bash
   adb shell pm list packages | grep -i <part-of-name>      # find the package name
   tools/chunkpull.sh <package> ~/zeekr_tr/apks
   ```
2. Find the string resource that is used as the launcher label:
   ```bash
   python3 tools/label_refs.py ~/zeekr_tr/apks/<package>.apk
   # -> <package>.apk 0x7f1200ab app_name
   ```
3. Add a line to `LABELS` in [`tools/build_labels.py`](tools/build_labels.py):
   ```python
   "com.example.chineseapp": ("exampleapp", {"app_name": "Example App"}),
   ```
   The short name (`exampleapp`) must be unique, lower case, and `[a-z0-9]` only.
4. Add a row to `OVERLAYS` in
   [`app/src/com/zeekrenglish/MainActivity.java`](app/src/com/zeekrenglish/MainActivity.java):
   ```java
   {"com.zeekrenglish.lbl.exampleapp", "com.example.chineseapp", "App name: exampleapp"},
   ```
5. Build (see [Building from source](#building-from-source)), install, tap **Install / update**, and restart the
   head unit.

The label overlay writes the English name into **every** default / zh / en variant the app already has for
that string. It never adds a new locale, because adding one breaks locale selection in many Zeekr apps.

Please send a pull request with new labels so that everyone gets them.

## Uninstalling

Open the app and tap **Remove everything**. This uninstalls every `com.zeekrenglish.*` overlay and then the app.
Restart the head unit afterwards. Manual alternative:

```bash
adb shell cmd overlay list | grep zeekrenglish
adb shell pm list packages | grep zeekrenglish | cut -d: -f2 | while read p; do adb uninstall "$p"; done
```

## Known limitations

- The **instrument cluster** has its own OS, so it cannot be translated from Android.
- The **clock / calendar / volume popup** text and "调试模式" are hard-coded in SystemUI code, not in
  resources, so overlays cannot change them.
- Some Zeekr components (SystemUI drawer, launcher cards, quick panel) ignore `values-en`. The build handles
  this by also writing English into the default and `zh` variants that the app already ships.
- **Exterior Sound** (`com.mrbattery.exterioraudioplaydemo`) is a WebView, and its content comes from a web
  page. Only its app name is translated.
- `ecarx.launcher3` on many cars is a Russian-modded launcher. The overlay replaces its Russian defaults with
  English.

---

## Building from source

The repository contains the **translations, the build tools and the manager app source**. It does **not**
contain Zeekr's original APKs, which are proprietary. You pull those from your own car.

### Requirements

- macOS or Linux, `bash`, `python3` (3.8+), `curl`, `openssl`, `zip`
- JDK 11+ (`javac`)
- Android SDK with **build-tools** (`aapt2`, `zipalign`, `apksigner`, `d8`) and **platforms;android-30**
  ```bash
  sdkmanager "build-tools;36.1.0" "platforms;android-30"
  ```
- [`apktool`](https://apktool.org/) (to decode the original APKs)
- `adb` and a car to pull the APKs from

Paths can be changed with environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `ZEEKR_WORK` | `~/zeekr_tr` | Work folder: `apks/`, `dec/`, `build/`, `dist/` (never committed) |
| `ANDROID_HOME` | `~/Library/Android/sdk` | Android SDK |
| `ZEEKR_BUILD_TOOLS` | newest `$ANDROID_HOME/build-tools/*` | build-tools folder |
| `ZEEKR_ANDROID_JAR` | `$ANDROID_HOME/platforms/android-30/android.jar` | link-time framework jar |

### Steps

```bash
# 1. signing key: the PUBLIC AOSP test platform key (the car runs a test-keys build)
tools/get_keys.sh            # -> keys/platform.pk8, keys/platform.x509.pem (git-ignored)

# 2. original APKs from the car -> $ZEEKR_WORK/apks/<package>.apk
mkdir -p ~/zeekr_tr/apks
for p in com.geely.pma.settings com.geely.pma.climate com.android.systemui ecarx.launcher3; do  # ...all targets
  tools/chunkpull.sh "$p" ~/zeekr_tr/apks
done
#    Big APKs (SystemUI, settings): if adb keeps dropping, copy them on the car to /sdcard,
#    tar them, and move them with a FAT32 flash drive. Check the md5 afterwards.

# 3. decode them (resources only)
for a in ~/zeekr_tr/apks/*.apk; do
  apktool d -s -f -o ~/zeekr_tr/dec/$(basename "$a" .apk) "$a"
done

# 4. build the overlays, the app-name overlays, then the manager app
python3 tools/build_overlays.py          # or: build_overlays.py climate settings   (short names)
python3 tools/build_labels.py            # or: build_labels.py mxplayer
tools/build_app.sh                       # -> ~/zeekr_tr/dist/ZeekrEnglish.apk
```

Targets whose APK is not in `$ZEEKR_WORK/apks/` are **skipped with a message**, so you can build with only the
apps you have. `build_overlays.py` stops with `PROBLEMS:` if a translation has a placeholder mismatch
(`%s`, `%1$s`, `%d`), or if Chinese/Russian text is left in an English value. It also writes
`$ZEEKR_WORK/build/width_<short>.txt`, a list of translations that are probably too wide for their UI slot.

Quick test without the manager app (root):

```bash
adb install -r ~/zeekr_tr/build/overlays/com.zeekrenglish.ov.climate.apk
adb shell cmd overlay enable com.zeekrenglish.ov.climate
adb shell am force-stop com.geely.pma.climate
```

## Making a release (tag + APK)

1. **Bump versions:**
   - Manager app: `android:versionCode` (+1) and `android:versionName` in
     [`app/AndroidManifest.xml`](app/AndroidManifest.xml).
   - **If any translation or overlay changed:** bump `VERSION` in
     [`tools/build_overlays.py`](tools/build_overlays.py) **and** `OVERLAY_VERSION` in
     [`MainActivity.java`](app/src/com/zeekrenglish/MainActivity.java) to the same value. Otherwise
     **Install / update** treats the installed overlays as current and does not replace them.
   - ⚠️ **Never use versionCode `1`.** Zeekr CarService (`AppPolicyWrapper.handleOTAInstallLimit`) blocks any
     app with versionCode 1: it shows a cloud icon and cannot be opened or uninstalled. Current versions are
     110+.
2. **Build:** `python3 tools/build_overlays.py && python3 tools/build_labels.py && tools/build_app.sh`
3. **Check** the result:
   ```bash
   $ANDROID_HOME/build-tools/36.1.0/aapt2 dump badging ~/zeekr_tr/dist/ZeekrEnglish.apk | head -1
   $ANDROID_HOME/build-tools/36.1.0/apksigner verify --print-certs ~/zeekr_tr/dist/ZeekrEnglish.apk | grep SHA-1
   # expect SHA-1 27:19:6e:38:6b:87:5e:76:ad:f7:00:e7:ea:84:e4:c6:ee:e3:3d:fa  (AOSP test platform key)
   ```
   Then install it on a car and test it.
4. **Commit, tag, publish:**
   ```bash
   V=3.5
   cp ~/zeekr_tr/dist/ZeekrEnglish.apk /tmp/ZeekrEnglish-$V.apk
   shasum -a 256 /tmp/ZeekrEnglish-$V.apk > /tmp/ZeekrEnglish-$V.apk.sha256
   git commit -am "Release $V"
   git tag -a v$V -m "Zeekr EN/UA $V"
   git push origin main --tags
   gh release create v$V /tmp/ZeekrEnglish-$V.apk /tmp/ZeekrEnglish-$V.apk.sha256 \
     --title "Zeekr EN/UA $V" --notes "What changed …"
   ```
   APKs are **release assets only**. `*.apk` is git-ignored and is never committed.

## Adding or fixing translations

All translations are plain UTF-8 **TSV** files, one per app:

| Folder | File | Columns |
|---|---|---|
| `tr/` | `<pkg>.src.tsv` / `<pkg>.en.tsv` | `name ⇥ text` (first English batch: source / English) |
| `tr2/` | `<pkg>.todo.tsv` | `kind ⇥ name ⇥ budget ⇥ reason ⇥ source ⇥ current_en` (generated) |
| `tr2/` | `<pkg>.en.tsv` | `kind ⇥ name ⇥ English` |
| `tr_uk/` | `<pkg>.todo.tsv` | `kind ⇥ name ⇥ budget ⇥ English ⇥ Chinese` (generated) |
| `tr_uk/` | `<pkg>.uk.tsv` | `kind ⇥ name ⇥ Ukrainian` |

`kind` is `string`, `array`, or `fix` (`fix` = shorten an existing English string). The items of an `array` are
joined with ` ‖ `, and the item count must match the source.

**English:** `python3 tools/find_gaps.py <pkg>` writes `tr2/<pkg>.todo.tsv` with every string that would not
show proper English. Translate the lines into `tr2/<pkg>.en.tsv`.
**Ukrainian:** `python3 tools/ua_extract.py <pkg>` writes `tr_uk/<pkg>.todo.tsv` with every visible string
and its English. Translate into `tr_uk/<pkg>.uk.tsv`.

Rules:
- Placeholders must match the source exactly: `%s`, `%1$s`, `%d`, `%%`. Keep `\n` and markup.
- Do not translate voice-assistant keywords (`VR_*` resources).
- **Width:** one CJK character is about 1.8 Latin characters. Keep short labels within about 1.8× the source
  width (the `budget` column). Descriptions may wrap.
- After a change, restart the target app (`adb shell am force-stop <pkg>`). For the launcher or SystemUI,
  restart the head unit.

To support a **new app**, add `"<package>": "<short>"` to `TARGETS` in `tools/build_overlays.py`. Pull and
decode its APK, run `find_gaps.py`, translate, and add an `{"com.zeekrenglish.ov.<short>", "<package>",
"Description"}` row to `OVERLAYS` in `MainActivity.java`.

## Porting to another Zeekr OS version

The released APK is built from **Zeekr OS 5.1.5** apps. On other firmware, Zeekr may have changed string names,
added strings or added apps. Overlays match strings **by resource name**. Unchanged names keep working, renamed
or new ones stay untranslated, and nothing breaks. To build for your firmware:

1. **Work on a branch,** so that you can see exactly what changed:
   ```bash
   git checkout -b zeekr-os-<your-version>
   ```
2. **Pull and decode the APKs from *your* car.** Follow steps 1–3 of [Building from source](#building-from-source)
   for every package in `TARGETS` (`tools/build_overlays.py`) and `LABELS` (`tools/build_labels.py`) that
   exists on your car. Also check whether the package names are still the same:
   ```bash
   adb shell pm list packages -f | grep -E "zeekr|ecarx|geely"
   ```
3. **Find the gaps for your firmware.** This regenerates the work lists from your APKs:
   ```bash
   python3 tools/find_gaps.py  com.geely.pma.settings com.geely.pma.climate …   # all TARGETS
   python3 tools/ua_extract.py com.geely.pma.settings com.geely.pma.climate …
   git diff --stat tr2/ tr_uk/      # what is new or different compared with 5.1.5
   ```
   Existing translations in `tr2/<pkg>.en.tsv` and `tr_uk/<pkg>.uk.tsv` are matched by name and kept.
   New lines in `*.todo.tsv` that have no translation are the strings you still need to translate.
4. **Build and read the log:**
   ```bash
   python3 tools/build_overlays.py
   ```
   - `skip <kind> <name>: not in todo`: this string no longer exists in your firmware. Harmless, or remove
     the line.
   - `PROBLEMS: … placeholder mismatch`: the source changed (for example `%s` became `%1$s`). Fix the
     translation.
   - `rej N` on a language: N translations no longer match the English placeholders. Fix or retranslate them.
5. **Translate the missing lines** (see [Adding or fixing translations](#adding-or-fixing-translations)).
   Rebuild, install, and check on the car.
6. **Bump the versions.** You can include the firmware in `versionName`, for example `3.5-os5.2.0`. Then open a
   pull request or publish your own release. Say which Zeekr OS version it is for.

### Finding text that is still untranslated

1. Open the screen on the car, and note the Chinese/Russian text and which app is in front:
   ```bash
   adb shell dumpsys activity activities | grep -E "mResumedActivity|mFocusedActivity"
   ```
2. Search for that text in the decoded resources:
   ```bash
   grep -rn "座椅加热" ~/zeekr_tr/dec/*/res/values*/strings.xml ~/zeekr_tr/dec/*/res/values*/arrays.xml
   ```
3. What you find tells you what to do next:
   - **Found, in a package that is already in `TARGETS`:** add `string ⇥ <name> ⇥ English` to
     `tr2/<pkg>.en.tsv`. If the name is not in `tr2/<pkg>.todo.tsv` yet, re-run `find_gaps.py <pkg>`
     first. Also add the Ukrainian line to `tr_uk/<pkg>.uk.tsv` (re-run `ua_extract.py <pkg>`).
   - **Found, in a package that is not in `TARGETS`:** add it as a new app (see the end of
     [Adding or fixing translations](#adding-or-fixing-translations)).
   - **Not found anywhere:** the text is hard-coded in Java/Kotlin code (like the SystemUI clock or volume
     popup), comes from a server or web page (like Exterior Sound), or is shown on the instrument cluster.
     Overlays cannot change it.
4. If the text is in the app's **default** (`values/`) resources but the app still ignores `values-en`, that is
   expected. The build writes the translation into every default / en / zh variant that the app already has.

## Adding a new language

Example: **Polish (`pl`)**. Every language works like Ukrainian. It is an extra overlay set,
`com.zeekrenglish.<code>.<short>`, layered on top of English, while the system locale stays `en`.

1. **Create the work lists.** These list every visible string together with its English:
   ```bash
   python3 tools/ua_extract.py --dir tr_pl com.geely.pma.settings com.geely.pma.climate …   # all TARGETS
   ```
   This writes `tr_pl/<pkg>.todo.tsv` (`kind ⇥ name ⇥ budget ⇥ English ⇥ Chinese`).
2. **Translate** each file into `tr_pl/<pkg>.pl.tsv`, one line per item:
   ```
   string	climate_auto	Auto
   array	adas_remind_type	Dźwięk ‖ Wibracja
   ```
   You can leave lines out. Anything missing falls back to English. Lines whose placeholders don't match
   are rejected, and the build log counts them (`PL 120+4 (rej 2)`).
3. **Register the language** in `LANGS` in [`tools/build_overlays.py`](tools/build_overlays.py):
   ```python
   LANGS = {
       "uk": {"dir": "tr_uk", "priority": 30, "label": "Ukrainian"},
       "pl": {"dir": "tr_pl", "priority": 31, "label": "Polish"},
   }
   ```
   Use a two-letter code that is not `ov` or `lbl`. Give each language its own priority above 20. Only one
   extra language is on at any time.
4. Add the **button** (next section), bump the versions, and build.

> Do **not** add a real `values-pl` locale or switch the system language to Polish. Many Zeekr apps don't ship
> that locale, fall back to Chinese, and SystemUI resets the system language to match the vehicle language.

## Adding a new language button

Language buttons are defined in `LANGS` at the top of
[`app/src/com/zeekrenglish/MainActivity.java`](app/src/com/zeekrenglish/MainActivity.java):

```java
private static final String[][] LANGS = {
        {"uk", "Українська"},
        {"pl", "Polski"},        // <- new button: {code, text shown on the button}
        {"en", "English"},
};
```

The code must match the key in `LANGS` in `build_overlays.py`. Nothing else needs to change:

- **Install / update** installs all bundled `com.zeekrenglish.<code>.*` overlays and switches on only the ones
  for the currently chosen language.
- Pressing a button turns on that language's overlays and turns off every other extra language. `en` means
  "English only".
- **Turn all OFF** and **Remove everything** cover every language automatically.

Then bump `versionCode` / `versionName`, rebuild, and release.

## Repository layout

```
app/                 manager app "Zeekr EN/UA" (plain Java, built without Gradle: aapt2 + javac + d8)
  AndroidManifest.xml
  src/com/zeekrenglish/MainActivity.java   overlay list, language buttons, install/toggle/remove
tools/
  paths.py           shared paths / SDK detection (env overrides)
  get_keys.sh        downloads the public AOSP test platform key into keys/
  chunkpull.sh       pulls an APK from the car in 4 MB chunks (survives USB drops)
  find_gaps.py       -> tr2/<pkg>.todo.tsv   (strings missing proper English)
  ua_extract.py      -> tr_uk/<pkg>.todo.tsv (all visible strings; --dir tr_<code> for other languages)
  label_refs.py      shows which string an APK uses as its launcher label
  build_overlays.py  -> com.zeekrenglish.ov.<short> (EN, prio 10) + com.zeekrenglish.<lang>.<short> (prio 30+)
  build_labels.py    -> com.zeekrenglish.lbl.<short> (app names, prio 20)
  build_app.sh       -> dist/ZeekrEnglish.apk (manager app with all overlays bundled as assets)
tr/ tr2/             English translations (TSV)
tr_uk/               Ukrainian translations (TSV)
```

Not in git (see [`.gitignore`](.gitignore)): original Zeekr APKs and decoded resources, build outputs and
APKs, signing keys, and dumps from a car.

## Contributing

Issues and pull requests are welcome. Good contributions include translation fixes, new languages, app-name
labels for apps on your car, and firmware compatibility reports. Please:

- **never** commit Zeekr APKs, decoded resources, `keys/`, or anything from your car that contains personal
  data (VIN, account names, Wi-Fi, logs);
- run `python3 tools/build_overlays.py` before you open a PR, and make sure it shows no `PROBLEMS:`;
- say which car, firmware and region you tested on.

## License

[MIT](LICENSE). Zeekr, Geely and ECARX are trademarks of their owners. This project is not affiliated with them.
It ships only its own translated strings, never any original Zeekr code or resources.
