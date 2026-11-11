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


AUTO_RE = re.compile(r'<script type="application/ld\+json" id="breadcrumb-ld-auto">.*?</script>\n?', re.S)
SKIP_TOP = {".git", ".github", "tools", "content", "docs", "node_modules", "gifts", "test-artifacts", "en"}


def auto_ld(root):
    """2026-11-11 SEO brief: BreadcrumbList data for every other Arabic page
    (Home › section › page), built from the pages' own H1s. Pages that already
    describe their breadcrumb (BreadcrumbList) are left alone."""
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            dirnames[:] = [d for d in dirnames if d not in SKIP_TOP and not d.startswith(".")]
            continue
        if "index.html" not in filenames:
            continue
        path = os.path.join(dirpath, "index.html")
        with open(path, encoding="utf-8") as f:
            t = old = f.read()
        base = AUTO_RE.sub("", t)
        if "BreadcrumbList" in base or 'lang="ar"' not in base[:400] or "noindex" in base.split("</head>")[0]:
            t = base
        else:
            items = [("الرئيسية", "/")]
            parts = rel.split(os.sep)
            for i in range(1, len(parts)):
                parent = os.path.join(root, *parts[:i], "index.html")
                if os.path.exists(parent):
                    with open(parent, encoding="utf-8") as f:
                        name = h1_text(f.read())
                    if name:
                        items.append((name, "/" + "/".join(parts[:i]) + "/"))
            title = h1_text(base)
            if not title:
                continue
            items.append((title, "/" + "/".join(parts) + "/"))
            block = jsonld(items).replace('id="breadcrumb-ld"', 'id="breadcrumb-ld-auto"')
            t = base.replace("</head>", block + "</head>", 1)
        if t != old:
            with open(path, "w", encoding="utf-8") as f:
                f.write(t)
            n += 1
    return n


def apply(root):
    n = sum(process(p, s, root) for p, s in targets(root))
    m = auto_ld(root)
    print(f"breadcrumbs: updated {n} page(s), breadcrumb data added/refreshed on {m}")
    return n + m


if __name__ == "__main__":
    apply(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
