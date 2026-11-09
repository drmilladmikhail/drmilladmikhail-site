#!/usr/bin/env python3
"""Post-build: accessible breadcrumb nav + BreadcrumbList JSON-LD on deep pages.

Covers /articles/<slug>/, /tests/<slug>/ and /research/library/. Idempotent.
"""
import glob
import html
import json
import os
import re

SITE = "https://drmilladmikhail.com"
LABEL = "مسار التصفح"
SECTIONS = {"articles": ("المقالات", "/articles/"), "tests": ("اختبارات نفسية", "/tests/"),
            "life-tools": ("أدوات لحياتك", "/life-tools/")}


def targets(root):
    for sec in SECTIONS:
        for p in sorted(glob.glob(os.path.join(root, sec, "*", "index.html"))):
            yield p, sec
    df = os.path.join(root, "discover-feelings", "index.html")
    if os.path.exists(df):
        yield df, "life-tools"  # «اكتشاف مشاعرك» sits under «أدوات لحياتك»
    lib = os.path.join(root, "research", "library", "index.html")
    if os.path.exists(lib):
        yield lib, "library"


def h1_text(t):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def jsonld(items):
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
                                for i, (n, u) in enumerate(items)]}
    return ('<script type="application/ld+json" id="breadcrumb-ld">\n'
            + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>\n")


def process(path, sec, root):
    with open(path, encoding="utf-8") as f:
        t = old = f.read()
    rel = "/" + os.path.relpath(os.path.dirname(path), root).replace(os.sep, "/") + "/"
    title = h1_text(t)
    if not title:
        return False
    home = ("الرئيسية", "/")
    if sec == "library":
        items = [home, ("مرصد الأبحاث النفسية", "/research/"), (title, rel)]
        t = re.sub(r'(<main id="main"[^>]*>)<p>(<a href="/">الرئيسية</a> / .*?)</p>',
                   lambda m: m.group(1) + f'<nav class="crumbs" aria-label="{LABEL}">' + m.group(2) + "</nav>",
                   t, count=1, flags=re.S)
    else:
        name, url = SECTIONS[sec]
        items = [home, (name, url), (title, rel)]
        t = re.sub(r'<p class="crumbs"><a href="/(?:articles|tests|life-tools)/">(.*?)</a>(.*?)</p>',
                   lambda m: f'<nav class="crumbs" aria-label="{LABEL}"><a href="/">الرئيسية</a> · '
                             f'<a href="{url}">{m.group(1)}</a>{m.group(2)}</nav>',
                   t, count=1, flags=re.S)
    t = re.sub(r'<script type="application/ld\+json" id="breadcrumb-ld">.*?</script>\n?', "", t, flags=re.S)
    t = t.replace("</head>", jsonld(items) + "</head>", 1)
    if t != old:
        with open(path, "w", encoding="utf-8") as f:
            f.write(t)
        return True
    return False


def apply(root):
    n = sum(process(p, s, root) for p, s in targets(root))
    print(f"breadcrumbs: updated {n} page(s)")
    return n


if __name__ == "__main__":
    apply(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
