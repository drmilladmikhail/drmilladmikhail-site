#!/usr/bin/env python3
"""Build /discover-feelings/ («اكتشاف مشاعرك») from content/discover-feelings/ (called by build_extras.build_all).

Reuses the scoping/renaming helpers of build_life_tools. Nothing a visitor types is stored or sent.
Runs only when content/discover-feelings/index.html exists, so unreviewed drafts stay in docs/drafts/.
"""
import os
import re

import build_life_tools as bl

ROOT = bl.ROOT
SLUG = "discover-feelings"
ASSETS = os.path.join(ROOT, "assets", SLUG)
CARD_BLURB = "ابحث عن اللي جواك بكلماتك، وسمّي إحساسك، وجرّب مهارة صغيرة، وراجع تجربتك."


def available():
    return os.path.exists(os.path.join(ROOT, "content", SLUG, "index.html"))


def card_html(esc):
    return f'''      <li class="test-card">
        <a href="/{SLUG}/">
          <div class="tc-body">
            <h2>اكتشاف مشاعرك</h2>
            <span class="card-desc">{esc(CARD_BLURB)}</span>
          </div>
        </a>
      </li>'''


def build(ba, page, write, SITE):
    if not available():
        return
    old_src = bl.SRC
    bl.SRC = os.path.join(ROOT, "content")
    try:
        title, desc, main = bl.parse(SLUG)
        os.makedirs(ASSETS, exist_ok=True)
        with open(os.path.join(ASSETS, "tool.css"), "w", encoding="utf-8") as f:
            f.write(bl.VARS + bl.scope_css(bl.read(SLUG, "tool.css")) + "\n" + bl.PRINT_CSS)
        scripts = []
        for js in ("data.js", "tool.js"):
            code = bl.read(SLUG, js)
            code = re.sub(r"(className = ')(" + "|".join(bl.RENAME) + r")(')", r"\1xt-\2\3", code)
            with open(os.path.join(ASSETS, js), "w", encoding="utf-8") as f:
                f.write(code)
            scripts.append(f'<script src="/assets/{SLUG}/{js}" defer></script>')
    finally:
        bl.SRC = old_src
    body = f'  <section class="section">\n    <div class="wrap narrow xtool">{main}</div>\n  </section>'
    url = f"{SITE}/{SLUG}/"
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "inLanguage": "ar",
          "description": desc, "author": {"@id": f"{SITE}/#person"}, "dateModified": bl.MODIFIED,
          "isPartOf": {"@type": "CollectionPage", "name": "أدوات لحياتك", "url": f"{SITE}/life-tools/"}}
    html = page(SLUG, title, desc, body, ld)
    # premium.css (2026-11-10, his request «خلي الصفحة برميم تصميم») is hand-written, loaded after tool.css
    html = html.replace("</head>", f'<link rel="stylesheet" href="/assets/{SLUG}/tool.css">\n'
                        f'<link rel="stylesheet" href="/assets/{SLUG}/premium.css">\n</head>', 1)
    html = html.replace("</body>", "\n".join(scripts) + "\n</body>", 1)
    write(SLUG, html)
