#!/usr/bin/env python3
"""Build Ukrainian work lists: every visible string/array of each app.
Output tr_uk/<pkg>.todo.tsv (or --dir tr_<code>): kind  name  budget  english  chinese
English = our translation (tr/, tr2/) > Zeekr values-en > default (if not foreign).
"""
import os, re, sys, glob
sys.path.insert(0, os.path.dirname(__file__))
from find_gaps import load, NOISE, FOREIGN, width, flat  # noqa

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import REPO, WORK  # noqa: E402
ROOT = WORK
SEP = " ‖ "


def ours(pkg):
    d = {}
    for f in (f"{REPO}/tr/{pkg}.en.tsv",):
        if os.path.exists(f):
            for l in open(f, encoding="utf-8"):
                p = l.rstrip("\n").split("\t", 1)
                if len(p) == 2:
                    d[("string", p[0])] = p[1]
    f = f"{REPO}/tr2/{pkg}.en.tsv"
    if os.path.exists(f):
        for l in open(f, encoding="utf-8"):
            p = l.rstrip("\n").split("\t", 2)
            if len(p) == 3:
                kind = "string" if p[0] == "fix" else p[0]
                d[(kind, p[1])] = p[2].split(SEP) if kind == "array" else p[2]
    return d


def main(pkg):
    res = f"{ROOT}/dec/{pkg}/res"
    default = load(f"{res}/values")
    en = {}
    for d in sorted(glob.glob(f"{res}/values-en*")):
        if re.search(r"values-en(-r(US|GB))?$", d):
            en.update(load(d))
    zh = load(f"{res}/values-zh-rCN") if os.path.isdir(f"{res}/values-zh-rCN") else {}
    mine = ours(pkg)
    uk = {}
    for d in glob.glob(f"{res}/values-uk*"):
        uk.update(load(d))
    rows, missing_en = [], 0
    for key, dv in sorted(default.items()):
        kind, name = key
        if kind == "plurals" or NOISE.match(name) or name.startswith("VR_") or key in uk:
            continue
        e = mine.get(key) or en.get(key) or (dv if not _foreign(dv) else None)
        if e is None or _foreign(e):
            missing_en += 1
            continue
        c = zh.get(key) or (dv if _foreign(dv) else "")
        ef, cf = flat(e), flat(c) if c else ""
        if not re.search(r"[A-Za-z]", ef):
            continue
        if re.fullmatch(r"[\W\d_]*[A-Za-z]{0,2}[\W\d_]*", ef):   # units, symbols
            continue
        base = width(cf.split(SEP)[0]) if cf else width(ef.split(SEP)[0]) / 1.0
        rows.append((kind, name, str(int(base * 1.35) + 2), ef.replace("\n", "\\n").replace("\t", " "),
                     cf.replace("\n", "\\n").replace("\t", " ")))
    os.makedirs(f"{REPO}/{OUT}", exist_ok=True)
    with open(f"{REPO}/{OUT}/{pkg}.todo.tsv", "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"{pkg}\t{len(rows)}\t(no English yet: {missing_en})")


def _foreign(v):
    if isinstance(v, list):
        return any(FOREIGN.search(x) for x in v)
    return bool(FOREIGN.search(v))


OUT = "tr_uk"

if __name__ == "__main__":
    # Usage: ua_extract.py [--dir tr_<code>] <pkg>...   (default folder: tr_uk)
    args = sys.argv[1:]
    if args[:1] == ["--dir"]:
        OUT, args = args[1], args[2:]
    for p in args:
        main(p)
