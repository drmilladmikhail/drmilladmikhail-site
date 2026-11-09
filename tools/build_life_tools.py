#!/usr/bin/env python3
"""Build /life-tools/ («أدوات لحياتك») from content/life-tools/<slug>/ (called by build_pages.main).

Each source folder holds index.html (only <main> is used), tool.css, tool.js and optionally data.js.
Nothing a visitor types is stored or sent: the JS keeps it in page memory only.
Tool CSS is scoped under .xtool and mapped to the site's colour variables (dark mode works).
"""
import html as _html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "life-tools")
ASSETS = os.path.join(ROOT, "assets", "life-tools")
MODIFIED = "2026-11-09"
STATUS_OLD = "مسودة، لم تُراجَع مهنيًا بعد."
STATUS_NEW = "نشرها الكاتب بعد إعدادها بنفسه. لم تخضع لمراجعة مستقلة من مختص آخر."

# (slug, short blurb for the hub) in display order
TOOLS = [
    ("situation-thought-feeling", "فرّق بين اللي حصل فعلًا، والفكرة اللي جت في بالك، والإحساس اللي حسّيته."),
    ("within-my-control", "افرز همّك: إيه اللي في إيدك وإيه اللي مش في إيدك، واختار خطوة صغيرة."),
    ("before-i-say-yes", "لحظة قبل ما ترد على طلب: شوف الكلفة والاختيارات وصيغ ردك."),
    ("what-do-i-need", "لاحظ اللي محتاجه دلوقتي واختار خطوة صغيرة تلبّيه."),
    ("rest-without-guilt", "اختار نوع الراحة المناسب وتعامل مع صوت الذنب وقت الراحة."),
    ("relationship-patterns", "تأمّل في موقف بيتكرر معاك في العلاقات وجرّب خطوة مختلفة."),
    ("communication-simulator", "مواقف خيالية: جرّب ردود مختلفة وشوف مميزات وتكلفة كل واحد."),
    ("overthinking-path", "خطوات لفهم التفكير الزائد والتعامل معاه."),
]

DROP_PREFIXES = ("*", "html", "body", ".skip-link", ".draft-banner", ".tool", ".crumbs", "h1", ":root")
COLOR_MAP = [("#4a5568", "var(--muted)"), ("#7b8b84", "var(--muted)"), ("#fafcfb", "var(--paper)"),
             ("#f3f8f5", "var(--mist)"), ("#1b4fd8", "var(--focus)"),
             ("background:#fff", "background:var(--surface)"), ("color:#fff", "color:var(--eucalyptus-ink)")]
VARS = ".xtool{--euc:var(--eucalyptus)}\n"
PRINT_CSS = ("@media print{body>*:not(main){display:none!important}.xtool>*{display:none!important}"
             ".xtool>.print-copy{display:block!important}.print-copy h2{font-size:16pt}"
             ".print-copy h3{margin:12px 0 2px;font-size:13pt}.print-copy p{margin:0;white-space:pre-wrap}}\n")


def _blocks(css):
    """Yield (prelude, body) for top-level blocks, keeping nested braces in body."""
    i, n = 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        depth, k = 1, j + 1
        while k < n and depth:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        yield css[i:j].strip(), css[j + 1:k - 1]
        i = k


def scope_css(css):
    out = []
    for pre, body in _blocks(css):
        if pre.startswith("@media"):
            if "print" in pre or "prefers-reduced-motion" in pre:
                continue
            inner = scope_css(body)
            if inner.strip():
                out.append(f"{pre}{{{inner}}}")
            continue
        sels = [s.strip() for s in pre.split(",") if s.strip()]
        keep = [s for s in sels if not s.startswith(DROP_PREFIXES)]
        if not keep:
            continue
        keep = [re.sub(r"\.card\b", ".xt-card", s) for s in keep]
        keep = [re.sub(r"\.(" + "|".join(RENAME) + r")(?![\w-])", r".xt-\1", s) for s in keep]
        out.append(",".join(".xtool " + s for s in keep) + "{" + body + "}")
    text = "\n".join(out)
    for a, b in COLOR_MAP:
        text = text.replace(a, b)
    return text


RENAME = ("step", "opt", "muted", "safety", "actions")  # names that collide with site.css


def _rename_classes_in_html(text):
    def fix(m):
        toks = [("xt-" + t if t in RENAME else t) for t in m.group(1).split()]
        return 'class="' + " ".join(toks) + '"'
    return re.sub(r'class="([^"]*)"', fix, text)


def read(slug, name):
    with open(os.path.join(SRC, slug, name), encoding="utf-8") as f:
        return f.read()


def parse(slug):
    src = read(slug, "index.html")
    title = _html.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1))
    title = re.sub(r"\s*\(مسودة\)\s*\|.*$", "", title).strip()
    desc = _html.unescape(re.search(r'<meta name="description" content="(.*?)">', src, re.S).group(1))
    desc = re.sub(r"\s*مسودة للمراجعة\.?$", "", desc).strip()
    main = re.search(r"<main[^>]*>(.*)</main>", src, re.S).group(1)
    main = re.sub(r'<nav class="crumbs".*?</nav>', '<p class="crumbs"><a href="/life-tools/">أدوات لحياتك</a></p>', main, count=1, flags=re.S)
    main = re.sub(r'class="card\b', 'class="xt-card', main)
    main = _rename_classes_in_html(main)
    assert STATUS_OLD in main, slug
    main = main.replace(STATUS_OLD, STATUS_NEW)
    assert "مسودة" not in main.replace("مسودة غير", ""), slug
    return title, desc, main


def build(ba, page, write, SITE):
    esc = ba.esc
    if not os.path.isdir(SRC):
        return
    os.makedirs(ASSETS, exist_ok=True)
    cards = []
    for slug, blurb in TOOLS:
        title, desc, main = parse(slug)
        adir = os.path.join(ASSETS, slug)
        os.makedirs(adir, exist_ok=True)
        with open(os.path.join(adir, "tool.css"), "w", encoding="utf-8") as f:
            f.write(VARS + scope_css(read(slug, "tool.css")) + "\n" + PRINT_CSS)
        scripts = []
        for js in ("data.js", "tool.js"):
            if os.path.exists(os.path.join(SRC, slug, js)):
                code = read(slug, js)
                code = re.sub(r"(className = ')(" + "|".join(RENAME) + r")(')", r"\1xt-\2\3", code)
                with open(os.path.join(adir, js), "w", encoding="utf-8") as f:
                    f.write(code)
                scripts.append(f'<script src="/assets/life-tools/{slug}/{js}" defer></script>')
        body = f'  <section class="section">\n    <div class="wrap narrow xtool">{main}</div>\n  </section>'
        url = f"{SITE}/life-tools/{slug}/"
        ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "inLanguage": "ar",
              "description": desc, "author": {"@id": f"{SITE}/#person"}, "dateModified": MODIFIED,
              "isPartOf": {"@type": "CollectionPage", "name": "أدوات لحياتك", "url": f"{SITE}/life-tools/"}}
        html = page(f"life-tools/{slug}", title, desc, body, ld)
        html = html.replace("</head>", f'<link rel="stylesheet" href="/assets/life-tools/{slug}/tool.css">\n</head>', 1)
        html = html.replace("</body>", "\n".join(scripts) + "\n</body>", 1)
        write(f"life-tools/{slug}", html)
        cards.append(f'''      <li class="test-card">
        <a href="/life-tools/{slug}/">
          <span class="tc-body">
            <h2>{esc(title)}</h2>
            <span class="card-desc">{esc(blurb)}</span>
          </span>
        </a>
      </li>''')
    body = f'''  <section class="section articles-index">
    <div class="wrap">
      <h1>أدوات لحياتك</h1>
      <p class="section-intro">أدوات قصيرة بتساعدك تلاحظ وتفكر وتجرب خطوة صغيرة. اللي بتكتبه بيفضل في الصفحة دي بس: مش بيتبعت لأي سيرفر ومش بيتحفظ في المتصفح، ولو قفلت الصفحة بيتمسح. الأدوات دي للتأمل الذاتي، ومش تشخيص ولا بديل عن العلاج.</p>
      <ul class="cards">
{chr(10).join(cards)}
      </ul>
      <p class="safety">لو حاسس إنك في خطر دلوقتي، روح لصفحة <a href="/help-now/">محتاج مساعدة دلوقتي؟</a>. في مصر <a href="tel:105">105</a>، وفي أمريكا <a href="tel:988">988</a>.</p>
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "أدوات لحياتك", "url": f"{SITE}/life-tools/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    write("life-tools", page("life-tools", "أدوات لحياتك",
                             "أدوات نفسية قصيرة بالمصري: افرز همّك، لاحظ احتياجك، جرّب ردودًا مختلفة في مواقف خيالية، وافهم التفكير الزائد. اللي بتكتبه مش بيتبعت ولا بيتحفظ.",
                             body, ld))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_pages as bp
    build(bp.ba, bp.page, bp.write, bp.SITE)
