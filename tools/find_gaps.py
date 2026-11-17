#!/usr/bin/env python3
"""Find every string / string-array / plural that would NOT show proper English
when the system language is English. Writes tr2/<pkg>.todo.tsv.

Columns: kind  name  budget  source  [current_en]
  kind   = string | array | plurals
  budget = max English width in "Latin-char units" (see width())
  source = original default text (arrays/plurals items joined with ' ‖ ')
"""
import os, re, sys, glob
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import REPO, WORK  # noqa: E402
ROOT = WORK
NOISE = re.compile(r"^(sensors_|srl_|VR_HOT_|abc_|mtrl_|material_|m3_|exo_|common_google|fab_|bottomsheet|"
                   r"character_counter|search_menu|status_bar_notification|sdk_debug|sensor_str_|hms_|upsdk|"
                   r"jpush|umeng|tt_|ksad|ali_|com_facebook|preference_|password_toggle|item_view_role|"
                   r"appbar_scrolling|hide_bottom|icon_content|path_password|clear_text|error_icon|"
                   r"bottom_sheet|androidx_|call_notification|copy_toast|searchview|side_sheet|"
                   r"library_|define_|app_demo_version)")
FOREIGN = re.compile(r"[\u3000-\u303f\u3400-\u9fff\uff00-\uffef\u0400-\u04ff]")


def width(s):
    """Approximate rendered width in units of an average Latin character."""
    w = 0.0
    for ch in s:
        if "\u3400" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f" or "\uff00" <= ch <= "\uffef":
            w += 1.8          # CJK is ~1 em; Latin avg ~0.55 em -> 1.8 Latin chars
        elif "\u0400" <= ch <= "\u04ff":
            w += 1.1
        else:
            w += 1.0
    return w


def budget(src):
    w = width(re.sub(r"%\d*\$?[sd]", "000", src))
    long = len(src) > 25 or "\n" in src or "\\n" in src
    return int(w * (1.4 if long else 1.15)) + 2


def text(el):
    # inner XML (keeps <b>, <xliff:g> etc.) as raw text
    s = (el.text or "") + "".join(ET.tostring(c, encoding="unicode") for c in el)
    return s.strip()


def load(dirpath):
    out = {}
    for f in glob.glob(os.path.join(dirpath, "*.xml")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for el in root:
            n = el.get("name")
            if not n:
                continue
            if el.tag == "string":
                out[("string", n)] = text(el)
            elif el.tag in ("string-array", "array"):
                items = [text(i) for i in el.findall("item")]
                if items and all(not i.startswith("@") for i in items):
                    out[("array", n)] = items
            elif el.tag == "plurals":
                out[("plurals", n)] = {i.get("quantity"): text(i) for i in el.findall("item")}
    return out


def has_foreign(v):
    if isinstance(v, list):
        return any(FOREIGN.search(x) for x in v)
    if isinstance(v, dict):
        return any(FOREIGN.search(x) for x in v.values())
    return bool(FOREIGN.search(v))


def flat(v):
    if isinstance(v, list):
        return " ‖ ".join(v)
    if isinstance(v, dict):
        return " ‖ ".join(f"{k}={x}" for k, x in v.items())
    return v


def main(pkg):
    res = os.path.join(ROOT, "dec", pkg, "res")
    default = load(os.path.join(res, "values"))
    en = {}
    for d in sorted(glob.glob(os.path.join(res, "values-en*"))):
        if re.search(r"values-en(-r(US|GB))?$", d):
            en.update(load(d))
    done = set()
    for f in glob.glob(os.path.join(REPO, "tr", f"{pkg}.en.tsv")):
        done |= {l.split("\t")[0] for l in open(f, encoding="utf-8") if "\t" in l}
    rows = []
    for (kind, n), v in sorted(default.items()):
        if NOISE.match(n) or (kind == "string" and n in done):
            continue
        cur = en.get((kind, n))
        reason = None
        if has_foreign(v) and cur is None:
            reason = "missing"
        elif cur is not None and has_foreign(cur):
            reason = "en_foreign"
        elif kind == "string" and cur is not None and has_foreign(v) and width(cur) > budget(v) + 6:
            reason = "en_too_long"
        if reason:
            src = flat(v)
            rows.append((kind, n, str(budget(src.split(" ‖ ")[0] if kind != "string" else src)),
                         reason, src.replace("\n", "\\n").replace("\t", " "),
                         (flat(cur) if cur is not None else "").replace("\n", "\\n").replace("\t", " ")))
    os.makedirs(os.path.join(REPO, "tr2"), exist_ok=True)
    with open(os.path.join(REPO, "tr2", f"{pkg}.todo.tsv"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
    c = {}
    for r in rows:
        c[(r[0], r[3])] = c.get((r[0], r[3]), 0) + 1
    print(pkg, len(rows), dict(sorted(c.items())))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
