#!/usr/bin/env python3
"""Label overlays: force English app names in the launcher/drawer.
For each (package, string, English) override that string in EVERY config the
target app already defines for it (default, zh-rCN, zh, en ...). Never adds a
locale the target does not have (that broke locale selection before).
Output: build/overlays/com.zeekrenglish.lbl.<short>.apk
"""
import os, re, subprocess, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from build_overlays import ROOT, BT, JAR, KEY, CERT, VERSION, esc, run  # noqa

LABELS = {
    "com.ecarx.btphone": ("btphone", {"phone_app_name2": "Phone"}),
    "com.ecarx.mycar": ("mycar", {"app_name": "My Car"}),
    "ecarx.gallery": ("gallery", {"app_name": "Gallery"}),
    "com.geely.pma.lightshow": ("lightshow", {"app_name": "Light Show"}),
    "com.ecarx.multimedia": ("multimedia", {"usb_name": "USB Music", "bt_music": "Bluetooth Music", "radio_name": "Radio"}),
    "ecarx.membercenter": ("membercenter", {"app_name": "User Center"}),
    "com.ecarx.usermanual": ("usermanual", {"app_name": "User Manual"}),
    "ecarx.camera.dvr": ("dvr", {"app_name": "Camera"}),
    "com.zeekr.gamepad": ("gamepad", {"app_name": "Gamepad"}),
    "com.zeekr.dlnavideo": ("dlnavideo", {"app_name": "Screen Cast"}),
    "com.zeekr.speech.setting": ("speechsetting", {"app_name": "Voice Settings"}),
    "com.zeekrlife.market": ("market", {"app_name": "App Store"}),
    "com.mrbattery.exterioraudioplaydemo": ("extsound", {"app_name": "Exterior Sound"}),
    "com.zeekr.managerapplication": ("manager", {"app_name": "Car Manager"}),
    "com.zeekr.media": ("media", {"app_name": "ZEEKR Music"}),
    "com.mxtech.videoplayer.ad": ("mxplayer", {"app_name_universal": "MX Player"}),
    "pdf.reader.pdfviewer.pdfeditor": ("pdfhiread", {"pdf_reader_app_name_hi_read": "PDF Reader - Hi Read"}),
    "app.revanced.android.gms": ("microg", {"gms_settings_name": "microG Settings"}),
    "com.geely.pma.settings.launage": ("langswitch", {"app_name": "Language Switch"}),
    "com.tencent.wecarflow": ("wecarflow", {"app_name": "Tencent Music"}),
    "com.arcvideo.car.video": ("iqiyi", {"app_name": "iQIYI"}),
    "com.bilibili.bilithings": ("bilibili", {"app_name": "Bilibili"}),
    "com.thunder.carplay": ("thunderktv", {"app_name": "Thunder KTV"}),
}


def configs_for(apk, name):
    out = subprocess.run([f"{BT}/aapt2", "dump", "resources", apk], capture_output=True, text=True).stdout
    m = re.search(r"resource 0x[0-9a-f]+ string/" + re.escape(name) + r"\n((?:\s+\(.*\n)+)", out)
    if not m:
        return []
    return [re.match(r"\s+\(([^)]*)\)", l).group(1) for l in m.group(1).splitlines() if re.match(r"\s+\(", l)]


def build(pkg, short, names):
    apk = f"{ROOT}/apks/{pkg}.apk"
    if not os.path.exists(apk):
        print(f"[{short}] SKIP: {apk} not found (pull it from the car first)"); return
    work = f"{ROOT}/build/lbl_{short}"
    shutil.rmtree(work, ignore_errors=True)
    files = {}
    for name, en in names.items():
        for cfg in configs_for(apk, name):
            folder = "values" if cfg == "" else "values-" + re.sub(r"-([A-Z]{2})$", r"-r\1", cfg)
            files.setdefault(folder, []).append(f'    <string name="{name}" formatted="false">{esc(en)}</string>')
    if not files:
        print(f"[{short}] no label configs found"); return
    os.makedirs(f"{work}/flat")
    os.makedirs(f"{ROOT}/build/overlays", exist_ok=True)
    flats = []
    for folder, lines in files.items():
        os.makedirs(f"{work}/res/{folder}", exist_ok=True)
        with open(f"{work}/res/{folder}/strings.xml", "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + "\n".join(lines) + "\n</resources>\n")
        run([f"{BT}/aapt2", "compile", f"{work}/res/{folder}/strings.xml", "-o", f"{work}/flat"])
        flats.append(f"{work}/flat/{folder}_strings.arsc.flat")
    with open(f"{work}/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.zeekrenglish.lbl.{short}" android:versionCode="{VERSION}" android:versionName="{VERSION}">
    <overlay android:targetPackage="{pkg}" android:priority="20" />
    <application android:hasCode="false" android:label="Zeekr English labels ({short})" />
</manifest>
''')
    run([f"{BT}/aapt2", "link", "--no-resource-removal", "-o", f"{work}/unsigned.apk", "-I", JAR,
         "--manifest", f"{work}/AndroidManifest.xml", "--min-sdk-version", "26", "--target-sdk-version", "28", *flats])
    run([f"{BT}/zipalign", "-f", "4", f"{work}/unsigned.apk", f"{work}/aligned.apk"])
    out = f"{ROOT}/build/overlays/com.zeekrenglish.lbl.{short}.apk"
    run([f"{BT}/apksigner", "sign", "--key", KEY, "--cert", CERT, "--out", out, f"{work}/aligned.apk"])
    if os.path.exists(out + ".idsig"):
        os.remove(out + ".idsig")
    print(f"[{short}] ok  configs: {sorted(files)}")


if __name__ == "__main__":
    only = sys.argv[1:]
    for pkg, (short, names) in LABELS.items():
        if not only or short in only or pkg in only:
            build(pkg, short, names)
