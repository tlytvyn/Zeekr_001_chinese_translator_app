#!/usr/bin/env python3
"""Build text-only RRO overlay APKs (values-en) for Zeekr apps.

Inputs per target package:
  tr/<pkg>.src.tsv   name \t "original"            (v1 source strings)
  tr/<pkg>.en.tsv    name \t English               (v1 translations)
  tr2/<pkg>.todo.tsv kind name budget reason source current_en   (from find_gaps.py)
  tr2/<pkg>.en.tsv   kind \t name \t English       (v2; arrays: items joined with ' ‖ ')
Strings in todo that have no translation are auto-translated by phrase substitution
(SUBST) when that removes every foreign character (used for markup-heavy strings).
"""
import os, re, subprocess, sys, shutil, html, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import REPO, WORK, BT, JAR, KEY, CERT  # noqa: E402
ROOT = WORK  # backwards-compatible name
VERSION = 111

TARGETS = {
    "com.geely.pma.settings": "settings",
    "com.geely.pma.climate": "climate",
    "com.ecarx.btphone": "btphone",
    "zeekr.bx.sentry": "sentry",
    "ecarx.camera.dvr": "dvr",
    "com.zeekr.carlauncher3d": "carlauncher3d",
    "ecarx.launcher3": "launcher3",
    "com.mrbattery.exterioraudioplaydemo": "extsound",
    "com.android.systemui": "systemui",
    "ecarx.membercenter": "membercenter",
    "ecarx.notificationcenterui": "quickpanel",
    "com.zeekr.housekeeper": "housekeeper",
    "com.zeekrlife.market": "market",
    "com.ecarx.mycar": "mycar",
    "com.zeekr.speech.setting": "speechsetting",
    "ecarx.upgrade": "upgrade",
    "com.zeekr.autopilot": "autopilot",
    "com.zeekr.dlnavideo": "dlnavideo",
    "com.geely.pma.bs.modes": "modes",
    "com.zeekr.managerapplication": "manager",
    "com.ecarx.usermanual": "usermanual",
    "com.zeekr.media": "media",
    "com.zeekr.mediacenter": "mediacenter",
    "com.ecarx.multimedia": "multimedia",
    "com.ecarx.smartscene": "smartscene",
    "com.zeekr.feedback": "feedback",
    "com.ecarx.accountcenter": "accountcenter",
    "com.ecarx.profile": "profile",
    "com.zeekr.mediaswitch": "mediaswitch",
    "com.geely.pma.lightshow": "lightshow",
}
SUBST = {
    "剩余时间：": "Time left: ", "已预约：": "Scheduled: ",
    "Оставшееся время": "Time left", "Статистика электропитания": "Total supplied",
    "Источник питания": "Power supplied", "Резервирование для зарядки": "Scheduled charging",
    "Запланированная зарядка": "Scheduled charging", "Запланирована зарядка": "Scheduled charging",
    "Каждый день": "Daily", "Ежедневно": "Daily", "с приоритетом на полную зарядку": "full charge first",
    "до заданного лимита": "to set limit",
}
FOREIGN = re.compile(r"[\u3000-\u303f\u3400-\u9fff\uff00-\uffef\u0400-\u04ff]")
SPEC = re.compile(r"%(?:(\d+)\$)?[-#+0,(]*\d*(?:\.\d+)?([a-zA-Z%])")
SEP = " ‖ "


def specs(s):
    types, pct = [], 0
    for m in SPEC.finditer(s):
        if m.group(2) == "%":
            pct += 1
        else:
            types.append(m.group(2))
    return sorted(types), pct


def has_spec(s):
    return any(m.group(2) != "%" for m in SPEC.finditer(s))


def esc(s):
    """Escape for an Android string resource; keeps literal \\n escapes."""
    s = s.replace("\\n", "\x00")
    s = s.replace("\\", "\\\\").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = s.replace("'", "\\'").replace('"', '\\"').replace("\x00", "\\n")
    if s[:1] in ("@", "?"):
        s = "\\" + s
    if s[:1] == " " or s[-1:] == " ":
        s = '"' + s.replace('\\"', '\\"') + '"'
    return s


def unq(v):
    return v[1:-1] if len(v) >= 2 and v[0] == '"' and v[-1] == '"' else v


def tsv(path, ncols):
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.count("\t") >= ncols - 1:
                rows.append(line.split("\t", ncols - 1) if ncols > 1 else [line])
    return rows


def promote_zeekr_en(pkg, strings, arrays):
    """Where the target's DEFAULT text is Chinese/Russian but Zeekr ships an English value,
    reuse Zeekr's English so components that ignore values-en still show English."""
    import glob as _g
    sys.path.insert(0, os.path.dirname(__file__))
    from find_gaps import load as _load
    res = f"{WORK}/dec/{pkg}/res"
    if not os.path.isdir(res):
        return 0
    default = _load(f"{res}/values")
    en = {}
    for d in sorted(_g.glob(f"{res}/values-en*")):
        if re.search(r"values-en(-r(US|GB))?$", d):
            en.update(_load(d))
    n = 0
    for (kind, name), dv in default.items():
        if kind == "string" and name in strings or kind == "array" and name in arrays:
            continue
        ev = en.get((kind, name))
        if ev is None:
            continue
        if kind == "string":
            if FOREIGN.search(dv) and not FOREIGN.search(ev) and specs(dv) == specs(ev) and "@" not in ev[:1]:
                strings[name] = (dv, ev.replace("\n", "\\n") if False else ev); n += 1
        elif kind == "array" and isinstance(dv, list) and isinstance(ev, list):
            if len(dv) == len(ev) and any(FOREIGN.search(x) for x in dv) and not any(FOREIGN.search(x) for x in ev):
                arrays[name] = (dv, ev); n += 1
    return n


def collect(pkg):
    """Return (strings{name:(src,en)}, arrays{name:(src_items,en_items)})."""
    strings, arrays = {}, {}
    src1 = {k: unq(v) for k, v in tsv(f"{REPO}/tr/{pkg}.src.tsv", 2)}
    for k, v in tsv(f"{REPO}/tr/{pkg}.en.tsv", 2):
        if k in src1:
            strings[k] = (src1[k], v.strip())
    todo = {}
    for r in tsv(f"{REPO}/tr2/{pkg}.todo.tsv", 6):
        todo[(r[0], r[1])] = unq(r[4])
    # v1 substitution strings (Chinese markup)
    for k, v in src1.items():
        if k not in strings and any(a in v for a in SUBST):
            nv = v
            for a, b in SUBST.items():
                nv = nv.replace(a, b)
            if not FOREIGN.search(nv):
                strings[k] = (v, nv)
    for kind, name, val in tsv(f"{REPO}/tr2/{pkg}.en.tsv", 3):
        if kind == "fix":          # shorten an existing English string (no Chinese source)
            strings[name] = (val, val)
            continue
        src = todo.get((kind, name))
        if src is None:
            print(f"  [{pkg}] skip {kind} {name}: not in todo")
            continue
        val = html.unescape(val)
        if kind == "array":
            arrays[name] = (src.split(SEP), [x.strip() for x in val.split(SEP)])
        else:
            strings[name] = (src, val)
    for (kind, name), src in todo.items():
        if kind == "string" and name not in strings and any(a in src for a in SUBST):
            nv = src
            for a, b in SUBST.items():
                nv = nv.replace(a, b)
            if not FOREIGN.search(nv):
                strings[name] = (src, nv)
    return strings, arrays


def width(s):
    s = re.sub(r"<[^>]+>", "", re.sub(r"%\d*\$?[sd]", "00", s)).replace("\\n", "\n")
    w = 0.0
    for ch in max(s.split("\n"), key=len):
        if "\u3400" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f" or "\uff00" <= ch <= "\uffef":
            w += 1.8
        elif "\u0400" <= ch <= "\u04ff":
            w += 1.1
        else:
            w += 1.0
    return w


def width_report(short, strings, arrays):
    out = []
    pairs = [(k, s, e, False) for k, (s, e) in strings.items()]
    for k, (s, e) in arrays.items():
        pairs += [(f"{k}[{i}]", a, b, True) for i, (a, b) in enumerate(zip(s, e))]
    for k, s, e, seg in pairs:
        if not FOREIGN.search(s):
            continue
        ws, we = width(s), width(e)
        label = ws <= 16 and "\\n" not in s
        limit = ws * (1.8 if seg else 3.0 if label else 1.6) + 2
        if we > limit:
            out.append(f"{we/ws:4.1f}x  {k}\t{s}\t{e}")
    with open(f"{WORK}/build/width_{short}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(out, reverse=True)) + "\n")
    return len(out)


# Extra UI languages offered by the manager app (English is the base layer, always ON).
# code -> folder with <pkg>.todo.tsv / <pkg>.uk.tsv-style files, overlay priority, label.
# Overlay packages are named com.zeekrenglish.<code>.<short>. To add a language, add a line
# here, create tr_<code>/ and add a button in app/src/com/zeekrenglish/MainActivity.java (LANGS).
LANGS = {
    "uk": {"dir": "tr_uk", "priority": 30, "label": "Ukrainian"},
}


def collect_lang(pkg, code):
    """Translations for an extra language: <dir>/<pkg>.todo.tsv (kind name budget en zh, from
    ua_extract.py) + <dir>/<pkg>.<code>.tsv (kind name text). Settings may be split into
    <dir>/settings_part_*.<code>.tsv."""
    d = f"{REPO}/{LANGS[code]['dir']}"
    src = {(r[0], r[1]): unq(r[3]) for r in tsv(f"{d}/{pkg}.todo.tsv", 5)}
    files = [f"{d}/{pkg}.{code}.tsv"]
    if pkg == "com.geely.pma.settings":
        files += sorted(glob.glob(f"{d}/settings_part_*.{code}.tsv"))
    strings, arrays, bad = {}, {}, []
    for fpath in files:
        for kind, name, val in tsv(fpath, 3):
            en = src.get((kind, name))
            if en is None:
                continue
            val = html.unescape(unq(val.strip()))
            if kind == "array":
                a, b = en.split(SEP), [x.strip() for x in val.split(SEP)]
                if len(a) != len(b) or any(specs(x) != specs(y) for x, y in zip(a, b)):
                    bad.append(name); continue
                arrays[name] = (a, b)
            else:
                if specs(en) != specs(val) and not (re.search(r"% ?1 ?\$ ?s", en) and specs(val) == (["s"], 0)):
                    bad.append(name); continue
                strings[name] = (en, val)
    return strings, arrays, bad


def collect_uk(pkg):
    return collect_lang(pkg, "uk")


def xml_lines(strings, arrays):
    lines = []
    for k in sorted(strings):
        lines.append(f'    <string name="{k}" formatted="false">{esc(strings[k][1])}</string>')
    for k in sorted(arrays):
        items = "".join(f"\n        <item>{esc(x)}</item>" for x in arrays[k][1])
        lines.append(f'    <string-array name="{k}" formatted="false">{items}\n    </string-array>')
    return lines


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(cmd), "\n", r.stdout, r.stderr)
        sys.exit(1)


_CFG_CACHE = {}


def target_configs(pkg):
    """name -> list of resource-folder names (values, values-en, values-zh-rCN, ...) the TARGET already has.
    Only default / English / Chinese variants: never introduces a locale the app does not have."""
    if pkg in _CFG_CACHE:
        return _CFG_CACHE[pkg]
    apk = f"{WORK}/apks/{pkg}.apk"
    out = subprocess.run([f"{BT}/aapt2", "dump", "resources", apk], capture_output=True, text=True).stdout
    res, cur = {}, None
    for line in out.splitlines():
        m = re.match(r"\s+resource 0x[0-9a-f]+ (string|array)/(\S+)", line)
        if m:
            cur = m.group(2); res.setdefault(cur, set()); continue
        if re.match(r"\s+resource ", line) or re.match(r"\s+type ", line):
            cur = None; continue
        m = re.match(r"\s+\(([^)]*)\)", line)
        if cur and m:
            c = m.group(1)
            if c == "":
                res[cur].add("values")
            elif re.fullmatch(r"(en|zh)(-[A-Z]{2}|-r[A-Z]{2}|-Hans|-Hant)?(-[A-Z]{2})?", c):
                res[cur].add("values-" + re.sub(r"-([A-Z]{2})$", r"-r\1", c))
    _CFG_CACHE[pkg] = res
    return res


def emit(pkg, short, kind, priority, strings, arrays, cfgs):
    """Write each translated item into every default/en/zh variant the target has."""
    folders = {}
    for k, (_, val) in strings.items():
        for fo in cfgs.get(k, ["values-en"]):
            folders.setdefault(fo, []).append(f'    <string name="{k}" formatted="false">{esc(val)}</string>')
    for k, (_, items) in arrays.items():
        body = "".join(f"\n        <item>{esc(x)}</item>" for x in items)
        for fo in cfgs.get(k, ["values-en"]):
            folders.setdefault(fo, []).append(f'    <string-array name="{k}" formatted="false">{body}\n    </string-array>')
    work = f"{WORK}/build/{kind}_{short}"
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(f"{work}/flat")
    flats = []
    for fo, lines in folders.items():
        os.makedirs(f"{work}/res/{fo}")
        with open(f"{work}/res/{fo}/strings.xml", "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + "\n".join(lines) + "\n</resources>\n")
        run([f"{BT}/aapt2", "compile", f"{work}/res/{fo}/strings.xml", "-o", f"{work}/flat"])
        flats.append(f"{work}/flat/{fo}_strings.arsc.flat")
    label = LANGS[kind]["label"] if kind in LANGS else "English"
    with open(f"{work}/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.zeekrenglish.{kind}.{short}" android:versionCode="{VERSION}" android:versionName="{VERSION}">
    <overlay android:targetPackage="{pkg}" android:priority="{priority}" />
    <application android:hasCode="false" android:label="Zeekr {label} ({short})" />
</manifest>
''')
    run([f"{BT}/aapt2", "link", "--no-resource-removal", "-o", f"{work}/unsigned.apk", "-I", JAR,
         "--manifest", f"{work}/AndroidManifest.xml", "--min-sdk-version", "26", "--target-sdk-version", "28", *flats])
    run([f"{BT}/zipalign", "-f", "4", f"{work}/unsigned.apk", f"{work}/aligned.apk"])
    out = f"{WORK}/build/overlays/com.zeekrenglish.{kind}.{short}.apk"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run([f"{BT}/apksigner", "sign", "--key", KEY, "--cert", CERT, "--out", out, f"{work}/aligned.apk"])
    if os.path.exists(out + ".idsig"):
        os.remove(out + ".idsig")
    return sorted(folders)


def build(pkg, short):
    if not os.path.exists(f"{WORK}/apks/{pkg}.apk"):
        print(f"[{short}] SKIP: {WORK}/apks/{pkg}.apk not found (pull it from the car first)")
        return
    os.makedirs(f"{WORK}/build", exist_ok=True)
    strings, arrays = collect(pkg)
    problems, lines = [], []
    for k in sorted(strings):
        src, en = strings[k]
        if specs(src) != specs(en):
            problems.append(f"{k}: placeholder mismatch src={specs(src)} en={specs(en)}")
            continue
        if FOREIGN.search(re.sub(r'["“「『][^"”」』]*["”」』]', "", en).replace("\u3000", "")):
            problems.append(f"{k}: translation still contains foreign text")
            continue
        attr = ' formatted="false"'
        lines.append(f'    <string name="{k}"{attr}>{esc(en)}</string>')
    for k in sorted(arrays):
        src, en = arrays[k]
        if len(src) != len(en):
            problems.append(f"{k}: array size {len(en)} != {len(src)}")
            continue
        bad = [i for i, (a, b) in enumerate(zip(src, en)) if specs(a) != specs(b)]
        if bad:
            problems.append(f"{k}: placeholder mismatch in items {bad}")
            continue
        items = "".join(f"\n        <item>{esc(x)}</item>" for x in en)
        lines.append(f'    <string-array name="{k}" formatted="false">{items}\n    </string-array>')
    if problems:
        print(f"[{short}] PROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)

    promoted = promote_zeekr_en(pkg, strings, arrays)
    cfgs = target_configs(pkg)
    emit(pkg, short, "ov", 10, strings, arrays, cfgs)
    extra = []
    for code, cfg in LANGS.items():
        l_s, l_a, l_bad = collect_lang(pkg, code)
        if l_s or l_a:
            emit(pkg, short, code, cfg["priority"], l_s, l_a, cfgs)
        extra.append(f"{code.upper()} {len(l_s)}+{len(l_a)} (rej {len(l_bad)})")
    width_report(short, strings, arrays)
    print(f"[{short}] ok  promoted {promoted}  EN {len(strings)}+{len(arrays)}  {'  '.join(extra)}  variants {sorted(set(f for v in cfgs.values() for f in v))[:5]}")


if __name__ == "__main__":
    only = sys.argv[1:]
    for t, s in TARGETS.items():
        if not only or s in only or t in only:
            build(t, s)
