#!/usr/bin/env python3
"""Build the Arabic articles section of drmilladmikhail.com.

Source of truth:
  articles/articles.json          list of articles (newest last is fine; sorted by date here)
  articles/content/<slug>.html    the article body (HTML fragment, Arabic, uses site classes)

Each entry in articles.json:
  {"slug": "why-we-choose-the-same-person",
   "title": "...", "description": "one sentence for Google/cards",
   "date": "2026-11-04", "image": "love-p09",            # file in /assets/book/<image>.jpg
   "image_alt": "...", "chapter": "الفصل الأول", "minutes": 5}

Run:  python3 tools/build_articles.py
It writes articles/<slug>/index.html, articles/index.html, the "latest articles"
block on the home page (between ARTICLES markers in index.html) and sitemap.xml.
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
MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو",
          "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=Noto+Naskh+Arabic:wght@600;700'
         '&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;1,6..72,500&display=swap" rel="stylesheet">\n'
         '<link rel="stylesheet" href="/assets/site.css">')

TOPBAR = '''<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/">د. ميلاد منير ميخائيل</a>
    <nav class="nav" aria-label="أقسام الموقع">
      <a href="/">الرئيسية</a>
      <a href="/articles/">المقالات</a>
      <a href="/#book">الكتب</a>
      <a class="lang" href="/en/" hreflang="en" lang="en">English</a>
    </nav>
  </div>
</header>'''

FOOTER = f'''<footer class="footer">
  <div class="wrap">
    <div>
      <p class="names">د. ميلاد منير ميخائيل <span lang="en" dir="ltr">· Dr. Millad Mikhail</span></p>
      <p>© 2026. المحتوى لأغراض التوعية والتثقيف، ومش تشخيص ولا بديل عن العلاج النفسي.</p>
    </div>
    <ul>
      <li><a href="/articles/">المقالات</a></li>
      <li><a href="https://www.youtube.com/@DrMilladMikhail" target="_blank" rel="noopener">يوتيوب</a></li>
      <li><a href="https://www.amazon.com/author/drmilladmikhail" target="_blank" rel="noopener">أمازون</a></li>
      <li><a href="https://blog.drmilladmikhail.com/" target="_blank" rel="noopener">المدونة</a></li>
    </ul>
  </div>
</footer>'''


def ar_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def esc(s):
    return html.escape(s, quote=True)


def load():
    with open(os.path.join(ROOT, "articles", "articles.json"), encoding="utf-8") as f:
        items = json.load(f)
    slugs = set()
    for a in items:
        for k in ("slug", "title", "description", "date", "image", "image_alt"):
            if not a.get(k):
                sys.exit(f"article missing '{k}': {a}")
        if not re.fullmatch(r"[a-z0-9-]+", a["slug"]):
            sys.exit(f"bad slug (use a-z 0-9 -): {a['slug']}")
        if a["slug"] in slugs:
            sys.exit(f"duplicate slug: {a['slug']}")
        slugs.add(a["slug"])
        if not os.path.exists(os.path.join(ROOT, "assets", "book", a["image"] + ".jpg")):
            sys.exit(f"image not found: assets/book/{a['image']}.jpg")
        if not os.path.exists(os.path.join(ROOT, "articles", "content", a["slug"] + ".html")):
            sys.exit(f"content not found: articles/content/{a['slug']}.html")
    return sorted(items, key=lambda a: (a["date"], a["slug"]), reverse=True)


def article_page(a, prev_items):
    url = f"{SITE}/articles/{a['slug']}/"
    img = f"{SITE}/assets/book/{a['image']}.jpg"
    with open(os.path.join(ROOT, "articles", "content", a["slug"] + ".html"), encoding="utf-8") as f:
        body = f.read().strip()
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["title"],
        "description": a["description"],
        "image": img,
        "datePublished": a["date"],
        "dateModified": a.get("updated", a["date"]),
        "inLanguage": "ar",
        "mainEntityOfPage": url,
        "author": {"@type": "Person", "@id": f"{SITE}/#person", "name": "Dr. Millad Mikhail",
                   "alternateName": "د. ميلاد منير ميخائيل", "url": f"{SITE}/"},
        "publisher": {"@type": "Person", "@id": f"{SITE}/#person", "name": "Dr. Millad Mikhail"},
        "isBasedOn": {"@type": "Book", "name": "ليه بنحب اللي بيوجعنا؟", "url": BOOK_AR},
    }
    more = "".join(
        f'<li><a href="/articles/{p["slug"]}/">{esc(p["title"])}</a></li>' for p in prev_items[:3]
    )
    more_block = (f'<aside class="more"><h2>مقالات تانية</h2><ul>{more}</ul></aside>' if more else "")
    meta = ar_date(a["date"]) + (f" · {a['minutes']} دقايق قراءة" if a.get("minutes") else "")
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(a["title"])} | د. ميلاد ميخائيل</title>
<meta name="description" content="{esc(a["description"])}">
<meta name="author" content="Dr. Millad Mikhail">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(a["title"])}">
<meta property="og:description" content="{esc(a["description"])}">
<meta property="og:image" content="{img}">
<meta property="og:locale" content="ar_EG">
<meta name="theme-color" content="#2f6f62">
{FONTS}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{TOPBAR}
<main>
  <article class="post">
    <div class="wrap narrow">
      <p class="crumbs"><a href="/articles/">المقالات</a>{(" · " + esc(a["chapter"])) if a.get("chapter") else ""}</p>
      <h1>{esc(a["title"])}</h1>
      <p class="post-meta">د. ميلاد منير ميخائيل · {meta}</p>
      <figure class="post-hero"><img src="/assets/book/{a["image"]}.jpg" width="1200" height="800" alt="{esc(a["image_alt"])}"></figure>
      <div class="post-body">
{body}
      </div>
      <aside class="book-box">
        <picture class="cover-img">
          <source srcset="/assets/love-cover-ar.webp" type="image/webp">
          <img src="/assets/love-cover-ar.jpg" width="480" height="768" alt="غلاف كتاب ليه بنحب اللي بيوجعنا؟" loading="lazy">
        </picture>
        <div>
          <p class="book-box-title">المقال ده من كتاب «ليه بنحب اللي بيوجعنا؟»</p>
          <p>دليل عملي تفهم بيه نمط تعلقك وتختار شريك حياتك صح، فيه تمارين واختبارات ورسومات.</p>
          <div class="actions">
            <a class="btn primary" href="{BOOK_AR}" target="_blank" rel="noopener">اقرأ الكتاب على أمازون</a>
            <a class="btn" href="{BOOK_EN}" target="_blank" rel="noopener" lang="en">English edition</a>
          </div>
        </div>
      </aside>
      <aside class="author-box">
        <img src="/assets/millad.jpg" width="96" height="96" alt="د. ميلاد منير ميخائيل" loading="lazy">
        <p><strong>د. ميلاد منير ميخائيل</strong><br>حاصل على الدكتوراه في الصحة النفسية من جامعة قناة السويس، وعضو الجمعية الأمريكية لعلم النفس (APA). <a href="/">اعرف أكتر</a></p>
      </aside>
      {more_block}
    </div>
  </article>
</main>
{FOOTER}
</body>
</html>
'''


def card(a, heading="h2"):
    return f'''<li class="card">
        <a href="/articles/{a["slug"]}/">
          <img src="/assets/book/{a["image"]}.jpg" width="1200" height="800" alt="{esc(a["image_alt"])}" loading="lazy">
          <span class="card-body">
            <{heading}>{esc(a["title"])}</{heading}>
            <span class="card-desc">{esc(a["description"])}</span>
            <span class="card-date">{ar_date(a["date"])}</span>
          </span>
        </a>
      </li>'''


def index_page(items):
    cards = "\n      ".join(card(a) for a in items)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "مقالات د. ميلاد ميخائيل",
          "url": f"{SITE}/articles/", "inLanguage": "ar",
          "author": {"@id": f"{SITE}/#person"},
          "hasPart": [{"@type": "Article", "headline": a["title"], "url": f"{SITE}/articles/{a['slug']}/"} for a in items]}
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>مقالات | د. ميلاد منير ميخائيل</title>
<meta name="description" content="مقالات بالعامية عن الحب والتعلق والعلاقات المؤذية واختيار شريك الحياة، من كتب د. ميلاد منير ميخائيل.">
<link rel="canonical" href="{SITE}/articles/">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/articles/">
<meta property="og:title" content="مقالات د. ميلاد منير ميخائيل">
<meta property="og:image" content="{SITE}/assets/millad.jpg">
<meta name="theme-color" content="#2f6f62">
{FONTS}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{TOPBAR}
<main>
  <section class="section articles-index">
    <div class="wrap">
      <h1>المقالات</h1>
      <p class="section-intro">مقالات بالعامية عن الحب والتعلق والعلاقات، مأخوذة من كتبي. مقال جديد كل اثنين وخميس.</p>
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


def update_home(items):
    path = os.path.join(ROOT, "index.html")
    with open(path, encoding="utf-8") as f:
        t = f.read()
    start, end = "<!-- ARTICLES:START -->", "<!-- ARTICLES:END -->"
    if start not in t:
        return
    latest = "\n        ".join(card(a, "h3") for a in items[:3])
    block = f'''{start}
  <section class="section" id="articles" aria-labelledby="art-h">
    <div class="wrap">
      <div class="section-head">
        <svg class="icon" viewBox="0 0 32 32" aria-hidden="true"><rect x="5" y="5" width="22" height="22" rx="3"/><path d="M10 12h12M10 17h12M10 22h7"/></svg>
        <h2 id="art-h">أحدث المقالات</h2>
      </div>
      <ul class="cards">
        {latest}
      </ul>
      <div class="actions"><a class="btn" href="/articles/">كل المقالات</a></div>
    </div>
  </section>
  {end}'''
    t = re.sub(re.escape(start) + r".*?" + re.escape(end), block, t, flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(t)


def sitemap(items):
    newest = items[0]["date"] if items else "2026-11-04"
    urls = [
        (f"{SITE}/", newest, True),
        (f"{SITE}/en/", "2026-11-04", True),
        (f"{SITE}/articles/", newest, False),
    ] + [(f"{SITE}/articles/{a['slug']}/", a.get("updated", a["date"]), False) for a in items]
    parts = []
    for loc, mod, alt in urls:
        alts = ""
        if alt:
            alts = (f'\n    <xhtml:link rel="alternate" hreflang="ar" href="{SITE}/"/>'
                    f'\n    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/"/>')
        parts.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>{alts}\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(parts) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def main():
    items = load()
    for i, a in enumerate(items):
        d = os.path.join(ROOT, "articles", a["slug"])
        os.makedirs(d, exist_ok=True)
        others = items[:i] + items[i + 1:]
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(article_page(a, others))
    with open(os.path.join(ROOT, "articles", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(items))
    update_home(items)
    sitemap(items)
    print(f"built {len(items)} article(s): " + ", ".join(a["slug"] for a in items))


if __name__ == "__main__":
    main()
