#!/usr/bin/env python3
"""For each APK: launcher activities and the string resource used as their label."""
import subprocess, sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import BT  # noqa: E402
A = f"{BT}/aapt2"
for apk in sys.argv[1:]:
    x = subprocess.run([A, "dump", "xmltree", "--file", "AndroidManifest.xml", apk], capture_output=True, text=True).stdout
    app_label = None; cur = None; out = []
    for line in x.splitlines():
        s = line.strip()
        if s.startswith("E: application"): cur = "app"
        elif s.startswith("E: activity") or s.startswith("E: activity-alias"): cur = {"label": None, "launcher": False}; out.append(cur)
        m = re.search(r':label\(0x01010001\)=@(0x[0-9a-f]+)', s)
        if m:
            if cur == "app": app_label = m.group(1)
            elif isinstance(cur, dict): cur["label"] = m.group(1)
        if "android.intent.category.LAUNCHER" in s and isinstance(cur, dict): cur["launcher"] = True
    ids = {a["label"] or app_label for a in out if a["launcher"]}
    if not any(a["launcher"] for a in out): continue
    r = subprocess.run([A, "dump", "resources", apk], capture_output=True, text=True).stdout
    for rid in ids:
        if not rid: continue
        m = re.search(r"resource " + rid + r" string/(\S+)", r)
        print(os.path.basename(apk), rid, m.group(1) if m else "?")
