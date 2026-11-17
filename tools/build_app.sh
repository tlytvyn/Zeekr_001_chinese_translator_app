#!/bin/bash
# Builds ZeekrEnglish.apk (manager app + all overlays from $ZEEKR_WORK/build/overlays bundled as assets),
# signed with the public AOSP test platform key (keys/, fetch with tools/get_keys.sh).
# Output: $ZEEKR_WORK/dist/ZeekrEnglish.apk
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
R="${ZEEKR_WORK:-$HOME/zeekr_tr}"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}"
BT="${ZEEKR_BUILD_TOOLS:-$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)}"
JAR="${ZEEKR_ANDROID_JAR:-$SDK/platforms/android-30/android.jar}"
[ -f "$REPO/keys/platform.pk8" ] || { echo "keys/ missing: run tools/get_keys.sh"; exit 1; }
ls "$R"/build/overlays/*.apk >/dev/null 2>&1 || { echo "no overlays: run build_overlays.py and build_labels.py first"; exit 1; }
W=$R/build/app; rm -rf "$W"; mkdir -p "$W/flat" "$W/classes" "$W/assets/ov" "$W/dex"
cp "$R"/build/overlays/*.apk "$W/assets/ov/"
"$BT/aapt2" compile --dir "$REPO/app/res" -o "$W/flat/res.zip"
"$BT/aapt2" link -o "$W/base.apk" -I "$JAR" --manifest "$REPO/app/AndroidManifest.xml" -A "$W/assets" \
  --java "$W/gen" -0 apk "$W/flat/res.zip"
javac --release 8 -nowarn -encoding UTF-8 -classpath "$JAR" -d "$W/classes" \
  $(find "$REPO/app/src" "$W/gen" -name '*.java') 2>&1 | grep -v "bootstrap\|^Note:\|^warning: \[options\]\|^1 warning" || true
ls "$W"/classes/com/zeekrenglish/MainActivity.class >/dev/null || { echo "javac failed"; exit 1; }
"$BT/d8" --min-api 26 --lib "$JAR" --output "$W/dex" $(find "$W/classes" -name '*.class')
cp "$W/base.apk" "$W/unsigned.apk"; (cd "$W/dex" && zip -q -j "$W/unsigned.apk" classes.dex)
"$BT/zipalign" -f -p 4 "$W/unsigned.apk" "$W/aligned.apk"
mkdir -p "$R/dist"
"$BT/apksigner" sign --key "$REPO/keys/platform.pk8" --cert "$REPO/keys/platform.x509.pem" \
  --out "$R/dist/ZeekrEnglish.apk" "$W/aligned.apk"
rm -f "$R"/dist/*.idsig
ls -la "$R/dist/ZeekrEnglish.apk"
