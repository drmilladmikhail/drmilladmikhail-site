#!/usr/bin/env python3
"""Build the English articles section (/en/articles/) of drmilladmikhail.com.

Source of truth:
  en/articles/articles.json          English adaptations of Arabic articles (same slug as articles/<slug>/)
  en/articles/content/<slug>.html    the English body (HTML fragment, same classes as the Arabic bodies)

Each entry: {"slug", "title", "description", "date", "reviewed_on", "image", "image_alt",
             "chapter", "minutes", "summary", "refs": [{"title", "url"}]}
Every English page needs an Arabic original (articles/content/<slug>.html) and a "reviewed_on" date
(content/REVIEW-POLICY.md: no health content goes live before his review).

Called from tools/build_articles.py (pages + sitemap entries + hreflang on the Arabic pages).
Wording rule: in English he is a "Mental Health Educator / Author" — never a clinical psychologist,
and no sessions / therapy / booking are offered.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://drmilladmikhail.com"
BOOK_AR = "https://www.amazon.com/dp/B0HPNCYWWS"
BOOK_EN = "https://www.amazon.com/dp/B0HPRPSPWF"
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

TOPBAR = '''<a class="skip-link" href="#main">Skip to content</a>
<header class="topbar topbar-dark">
  <div class="wrap">
    <a class="brand" href="/en/">Dr. Millad Mikhail</a>
    <nav class="nav" aria-label="Site sections">
      <a href="/en/">Home</a>
      <a href="/en/#book">Books</a>
      <a href="/en/#about">About</a>
      <a href="/en/articles/"{cur}>Articles</a>
      <a href="/articles/" hreflang="ar">Articles (Arabic)</a>
      <a class="lang" href="{ar_url}" hreflang="ar" lang="ar">العربية</a>
    </nav>
    <details class="menu">
      <summary aria-label="Menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
      <nav aria-label="Menu">
        <a href="/en/">Home</a>
        <a href="/en/#book">Books</a>
        <a href="/en/#about">About</a>
        <a href="/en/articles/"{cur}>Articles</a>
        <a href="/articles/" hreflang="ar">Articles (Arabic)</a>
        <a href="/tests/" hreflang="ar">Self-tests (Arabic)</a>
        <a href="{ar_url}" hreflang="ar" lang="ar">العربية</a>
      </nav>
    </details>
  </div>
</header>'''

FOOTER = '''<footer class="footer">
  <div class="wrap footer-grid">
    <div>
      <p class="names">Dr. Millad Mikhail <span lang="ar" dir="rtl">· د. ميلاد ميخائيل</span></p>
      <p>Mental health educator and author. Ph.D. in Mental Health, Suez Canal University.</p>
      <p class="fine">© 2026. Content is for education and awareness, not diagnosis or treatment.</p>
    </div>
    <div>
      <h2>Read</h2>
      <ul>
        <li><a href="/en/#book">Books</a></li>
        <li><a href="/en/articles/">Articles</a></li>
        <li><a href="/articles/" hreflang="ar">Articles (Arabic)</a></li>
        <li><a href="/tests/" hreflang="ar">Self-tests (Arabic)</a></li>
      </ul>
    </div>
    <div>
      <h2>Follow</h2>
      <ul>
        <li><a href="https://www.youtube.com/@DrMilladMikhail" target="_blank" rel="noopener">YouTube</a></li>
        <li><a href="https://www.amazon.com/stores/author/B0HQ931MJP" target="_blank" rel="noopener">Amazon</a></li>
        <li><a href="https://www.linkedin.com/in/dr-millad-mikhail-a57b0b215" target="_blank" rel="noopener">LinkedIn</a></li>
        <li><a href="https://orcid.org/0009-0002-9254-367X" target="_blank" rel="me noopener">ORCID</a></li>
        <li><a href="/" hreflang="ar" lang="ar">العربية</a></li>
      </ul>
    </div>
  </div>
</footer>'''

FONTS = '<link rel="stylesheet" href="/assets/site.css">'
BANNED = re.compile(r"clinical psychologist|book a session|book now|therapy sessions?\b|counseling sessions?", re.I)


def esc(s):
    return html.escape(s, quote=True)


def en_date(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"


def pic(name, alt, eager=False, sizes="(max-width: 700px) 100vw, 700px"):
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/webp" srcset="/assets/book/{name}-600.webp 600w, /assets/book/{name}.webp 1000w" sizes="{sizes}">'
            f'<img src="/assets/book/{name}.jpg" width="1200" height="800" alt="{esc(alt)}" {load}></picture>')


IMG_RE = re.compile(r'<img src="/assets/book/((?:love-p\d+|art-[a-z0-9-]+))\.jpg" width="1200" height="800" alt="([^"]*)"[^>]*>')
H2_RE = re.compile(r'<h2(\s[^>]*)?>(.*?)</h2>', re.S)


def number_sections(body):
    toc, n = [], 0

    def repl(m):
        nonlocal n
        attrs, text = m.group(1) or "", m.group(2)
        n += 1
        if 'id="' not in attrs:
            attrs = f' id="q{n}"' + attrs
        sid = re.search(r'\bid="([^"]+)"', attrs).group(1)
        plain = re.sub(r"<[^>]+>", "", text).strip()
        if not re.search(r"sources|further reading|references", plain, re.I):
            toc.append((sid, esc(plain)))
        return f"<h2{attrs}>{text}</h2>"
    return H2_RE.sub(repl, body), toc


def load():
    p = os.path.join(ROOT, "en", "articles", "articles.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        items = json.load(f)
    seen = set()
    for a in items:
        for k in ("slug", "title", "description", "date", "image", "image_alt", "summary"):
            if not a.get(k):
                sys.exit(f"en article missing '{k}': {a.get('slug')}")
        s = a["slug"]
        if s in seen:
            sys.exit(f"duplicate en slug: {s}")
        seen.add(s)
        if not os.path.exists(os.path.join(ROOT, "articles", "content", s + ".html")):
            sys.exit(f"en article {s}: no Arabic original articles/content/{s}.html")
        if not os.path.exists(os.path.join(ROOT, "en", "articles", "content", s + ".html")):
            sys.exit(f"en article {s}: content not found en/articles/content/{s}.html")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(a.get("reviewed_on", ""))):
            sys.exit(f"en article {s}: not published — missing 'reviewed_on' (date of his review)")
        if len(a.get("refs") or []) < 2:
            sys.exit(f"en article {s}: needs at least 2 'refs'")
        with open(os.path.join(ROOT, "en", "articles", "content", s + ".html"), encoding="utf-8") as f:
            body = f.read()
        if BANNED.search(body + a["title"] + a["description"] + a["summary"]):
            sys.exit(f"en article {s}: banned wording (clinical psychologist / sessions / booking)")
    return sorted(items, key=lambda a: (a["date"], a["slug"]), reverse=True)


def slugs():
    return {a["slug"] for a in load()}


def card(a, heading="h2"):
    return f'''<li class="card">
        <a href="/en/articles/{a["slug"]}/">
          {pic(a["image"], a["image_alt"], sizes="(max-width: 640px) 100vw, 380px")}
          <div class="card-body">
            <{heading}>{esc(a["title"])}</{heading}>
            <span class="card-desc">{esc(a["description"])}</span>
            <span class="card-date">{en_date(a["date"])}</span>
          </div>
        </a>
      </li>'''


def head(title, desc, url, ar_url, og, og_alt, kind):
    return f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Dr. Millad Mikhail">
<link rel="alternate" hreflang="ar" href="{ar_url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="x-default" href="{ar_url}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Dr. Millad Mikhail">
<meta property="og:type" content="{kind}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title.split(' | ')[0])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og}">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title.split(' | ')[0])}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{og}">
<meta name="theme-color" content="#2f6f62">
{FONTS}'''


def article_page(a, others):
    s = a["slug"]
    url, ar_url = f"{SITE}/en/articles/{s}/", f"{SITE}/articles/{s}/"
    img = f"{SITE}/assets/book/{a['image']}.jpg"
    with open(os.path.join(ROOT, "en", "articles", "content", s + ".html"), encoding="utf-8") as f:
        body = IMG_RE.sub(lambda m: pic(m.group(1), html.unescape(m.group(2))), f.read().strip())
    body, toc = number_sections(body)
    ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["description"], "abstract": a["summary"],
        "image": [img], "datePublished": a["date"], "dateModified": a.get("updated", a["date"]),
        "inLanguage": "en", "mainEntityOfPage": url,
        "author": {"@type": "Person", "@id": f"{SITE}/#person", "name": "Dr. Millad Mikhail",
                   "jobTitle": "Mental Health Educator / Author", "url": f"{SITE}/en/about/"},
        "publisher": {"@type": "Person", "@id": f"{SITE}/#person", "name": "Dr. Millad Mikhail"},
        "translationOfWork": {"@type": "Article", "url": ar_url, "inLanguage": "ar"},
        "isBasedOn": {"@type": "Book", "name": "Why Do We Love What Hurts Us?", "url": BOOK_EN},
        "citation": [r["url"] for r in a["refs"]],
    }
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/en/"},
        {"@type": "ListItem", "position": 2, "name": "Articles", "item": f"{SITE}/en/articles/"},
        {"@type": "ListItem", "position": 3, "name": a["title"], "item": url}]}
    items = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)
    answer = (f'<aside class="answer-box" aria-labelledby="ans-{s}"><h2 id="ans-{s}">In short</h2><p>{esc(a["summary"])}</p>'
              + (f'<nav class="toc" aria-label="In this article"><p class="toc-title">In this article</p><ol>{items}</ol></nav>' if items else "")
              + '</aside>')
    disclaimer = ("" if "Safety note" in body else
                  '<p class="post-disclaimer"><strong>Safety note:</strong> This article is for education and awareness, '
                  'not diagnosis or a substitute for professional care. If you are in crisis, call or text 988 in the US, or call 105 in Egypt.</p>')
    refs = ('<section class="refs" aria-labelledby="refs-' + s + '"><h2 id="refs-' + s + '">References</h2><ol>'
            + "".join(f'<li><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["title"])}</a></li>' for r in a["refs"])
            + "</ol></section>")
    meta = f'<time datetime="{a["date"]}">{en_date(a["date"])}</time>' + (f" · {a['minutes']} min read" if a.get("minutes") else "")
    more = "\n        ".join(card(o, "h3") for o in others[:3])
    more_block = f'<div class="more"><h2>More articles</h2><ul class="cards">\n        {more}\n      </ul></div>' if more else ""
    return head(f'{a["title"]} | Dr. Millad Mikhail', a["description"], url, ar_url, img, a["image_alt"], "article") + f'''
<meta property="article:published_time" content="{a["date"]}">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(crumbs, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{TOPBAR.format(cur="", ar_url=f"/articles/{s}/")}
<main id="main">
  <article class="post">
    <div class="wrap narrow">
      <p class="crumbs"><a href="/en/articles/">Articles</a>{(" · " + esc(a["chapter"])) if a.get("chapter") else ""} · <a href="/articles/{s}/" hreflang="ar" lang="ar">اقرأ بالعربي</a></p>
      <h1>{esc(a["title"])}</h1>
      <p class="post-meta"><a href="/en/about/" rel="author">Dr. Millad Mikhail</a> · {meta}</p>
      <figure class="post-hero">{pic(a["image"], a["image_alt"], eager=True)}</figure>
      {answer}
      <div class="post-body">
{body}
      </div>
      {disclaimer}
      <div class="book-box">
        <picture class="cover-img">
          <source srcset="/assets/love-cover-en.webp" type="image/webp">
          <img src="/assets/love-cover-en.jpg" width="480" height="768" alt="Cover of the book Why Do We Love What Hurts Us?" loading="lazy">
        </picture>
        <div>
          <p class="book-box-title">{"This article is from the book “Why Do We Love What Hurts Us?”" if a.get("chapter") else "From Dr. Millad's book “Why Do We Love What Hurts Us?”"}</p>
          <p>A practical guide to understanding your attachment style and choosing a partner well, with exercises, self-tests and illustrations.</p>
          <div class="actions">
            <a class="btn primary" href="{BOOK_EN}" target="_blank" rel="noopener">Read the English edition on Amazon</a>
            <a class="btn" href="{BOOK_AR}" target="_blank" rel="noopener" lang="ar" hreflang="ar">النسخة العربية</a>
          </div>
        </div>
      </div>
      {refs}
      <div class="author-box">
        <img src="/assets/millad.jpg" width="96" height="96" alt="Dr. Millad Mikhail" loading="lazy">
        <p><strong><a href="/en/about/" rel="author">Dr. Millad Mikhail</a></strong><br>Mental Health Educator / Author. Ph.D. in Mental Health, Suez Canal University.<br><a href="/en/about/">About</a> · <a href="/en/#book">Books</a></p>
      </div>
      {more_block}
    </div>
  </article>
</main>
{FOOTER}
</body>
</html>
'''


def index_page(items):
    url = f"{SITE}/en/articles/"
    desc = ("English articles by Dr. Millad Mikhail, mental health educator and author: attachment, relationships "
            "and emotional well-being, adapted from his Arabic articles and book.")
    cards = "\n      ".join(card(a) for a in items)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Articles", "url": url, "inLanguage": "en",
          "description": desc, "author": {"@id": f"{SITE}/#person"}, "isPartOf": {"@id": f"{SITE}/#website"},
          "hasPart": [{"@type": "Article", "headline": a["title"], "url": f"{SITE}/en/articles/{a['slug']}/"} for a in items]}
    return head("Articles | Dr. Millad Mikhail", desc, url, f"{SITE}/articles/", f"{SITE}/assets/og/home.jpg",
                "Articles by Dr. Millad Mikhail", "website") + f'''
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{TOPBAR.format(cur=' aria-current="page"', ar_url="/articles/")}
<main id="main">
  <section class="section articles-index">
    <div class="wrap">
      <h1>Articles</h1>
      <p class="section-intro">Plain-language articles on attachment, relationships and emotional well-being. Each one answers a real question and lists its sources. More of the <a href="/articles/" hreflang="ar">Arabic articles</a> are being adapted into English.</p>
      <ul class="cards">
      {cards}
      </ul>
    </div>
  </section>
</main>
{FOOTER}
</body>
</html>
'''


def build():
    items = load()
    if not items:
        return []
    for i, a in enumerate(items):
        d = os.path.join(ROOT, "en", "articles", a["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(article_page(a, items[:i] + items[i + 1:]))
    with open(os.path.join(ROOT, "en", "articles", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(items))
    print(f"built {len(items)} English article(s): " + ", ".join(a["slug"] for a in items))
    return items


if __name__ == "__main__":
    build()
