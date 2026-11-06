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

TOPBAR = '''<a class="skip-link" href="#main">تخطّى للمحتوى</a>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/">د. ميلاد ميخائيل</a>
    <nav class="nav" aria-label="أقسام الموقع">
      <a href="/articles/">المقالات</a>
      <a href="/tests/">اختبارات نفسية</a>
      <a href="/book/">الكتب</a>
      <a href="/#about">نبذة</a>
      <a href="/#credentials">المؤهلات</a>
      <a class="lang" href="/en/" hreflang="en" lang="en">English</a>
    </nav>
    <details class="menu">
      <summary aria-label="القائمة"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
      <nav aria-label="القائمة">
        <a href="/start/">ابدأ من هنا</a>
        <a href="/articles/">المقالات</a>
        <a href="/tests/">اختبارات نفسية</a>
        <a href="/videos/">فيديوهات</a>
        <a href="/questions/">أسئلة محرجة</a>
        <a href="/ask/">اسأل من غير اسمك</a>
        <a href="/challenges/">تحديات قصيرة</a>
        <a href="/feelings/">عجلة المشاعر</a>
        <a href="/relationship-check/">علاقتك صحية؟</a>
        <a href="/worksheets/">أوراق تمرين</a>
        <a href="/book/">الكتب</a>
        <a href="/#about">نبذة</a>
        <a href="/#credentials">المؤهلات</a>
        <a href="https://blog.drmilladmikhail.com/">المدونة</a>
        <a href="/en/" hreflang="en" lang="en">English</a>
      </nav>
    </details>
  </div>
</header>'''

FOOTER = '''<footer class="footer">
  <div class="wrap footer-grid">
    <div>
      <p class="names">د. ميلاد ميخائيل <span lang="en" dir="ltr">· Dr. Millad Mikhail</span></p>
      <p>حاصل على الدكتوراه في الصحة النفسية من جامعة قناة السويس، وعضو الجمعية الأمريكية لعلم النفس (APA).</p>
      <p class="fine">© 2026. المحتوى لأغراض التوعية والتثقيف، ومش تشخيص ولا بديل عن العلاج النفسي.</p>
      <p class="fine footer-links"><a href="/sessions/">الجلسات</a> · <a href="/contact/">تواصل</a> · <a href="/help-now/">محتاج مساعدة دلوقتي</a> · <a href="/privacy/">الخصوصية</a> · <a href="/terms/">الشروط</a></p>
    </div>
    <div>
      <h2>اقرأ وجرّب</h2>
      <ul>
        <li><a href="/articles/">المقالات</a></li>
        <li><a href="/tests/">اختبارات نفسية</a></li>
        <li><a href="/book/">الكتب</a></li>
        <li><a href="https://blog.drmilladmikhail.com/" target="_blank" rel="noopener">المدونة</a></li>
      </ul>
    </div>
    <div>
      <h2>تابعني</h2>
      <ul>
        <li><a href="https://www.youtube.com/@DrMilladMikhail" target="_blank" rel="noopener">يوتيوب</a></li>
        <li><a href="https://www.amazon.com/author/drmilladmikhail" target="_blank" rel="noopener">أمازون</a></li>
        <li><a href="https://www.linkedin.com/in/dr-millad-mikhail-a57b0b215" target="_blank" rel="noopener">LinkedIn</a></li>
        <li><a href="https://orcid.org/0009-0002-9254-367X" target="_blank" rel="me noopener">ORCID</a></li>
        <li><a href="/en/" hreflang="en" lang="en">English</a></li>
      </ul>
    </div>
  </div>
</footer>'''


def ar_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def esc(s):
    return html.escape(s, quote=True)


def pic(name, alt, eager=False, sizes="(max-width: 700px) 100vw, 700px"):
    """<picture> with WebP (600w + 1000w) and the JPG as fallback. name = e.g. 'love-p09'."""
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/webp" srcset="/assets/book/{name}-600.webp 600w, /assets/book/{name}.webp 1000w" sizes="{sizes}">'
            f'<img src="/assets/book/{name}.jpg" width="1200" height="800" alt="{esc(alt)}" {load}></picture>')


IMG_RE = re.compile(r'<img src="/assets/book/(love-p\d+)\.jpg" width="1200" height="800" alt="([^"]*)"[^>]*>')


def upgrade_imgs(body):
    """Turn plain book <img> tags in an article body into responsive <picture> tags."""
    return IMG_RE.sub(lambda m: pic(m.group(1), html.unescape(m.group(2))), body)


def chapter_no(a):
    order = ["الأول", "التاني", "التالت", "الرابع", "الخامس", "السادس", "السابع", "الخاتمة"]
    c = a.get("chapter", "")
    for i, w in enumerate(order):
        if w in c:
            return i
    return 99


def related(a, others, n=3):
    """Same chapter first, then neighbouring chapters, then newest."""
    me = chapter_no(a)
    return sorted(others, key=lambda o: (abs(chapter_no(o) - me), o["date"] < a["date"], o["date"]), )[:n]


def social(url, title, desc, image, alt, kind="article"):
    return f'''<meta property="og:site_name" content="د. ميلاد ميخائيل">
<meta property="og:type" content="{kind}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(alt)}">
<meta property="og:locale" content="ar_EG">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{image}">'''


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
    og = f"{SITE}/assets/og/{a['slug']}.jpg"
    with open(os.path.join(ROOT, "articles", "content", a["slug"] + ".html"), encoding="utf-8") as f:
        body = upgrade_imgs(f.read().strip())
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["title"],
        "description": a["description"],
        "image": [og, img],
        "datePublished": a["date"],
        "dateModified": a.get("updated", a["date"]),
        "inLanguage": "ar",
        "mainEntityOfPage": url,
        "author": {"@type": "Person", "@id": f"{SITE}/#person", "name": "Dr. Millad Mikhail",
                   "alternateName": "د. ميلاد ميخائيل", "url": f"{SITE}/"},
        "publisher": {"@type": "Person", "@id": f"{SITE}/#person", "name": "Dr. Millad Mikhail"},
        "isBasedOn": {"@type": "Book", "name": "ليه بنحب اللي بيوجعنا؟", "url": BOOK_AR},
    }
    rel = related(a, prev_items)
    more = "\n        ".join(card(p, "h3") for p in rel)
    more_block = (f'<div class="more"><h2>مقالات ممكن تعجبك</h2><ul class="cards">\n        {more}\n      </ul></div>' if more else "")
    tests_block = ('''<div class="tests-cta">
        <p class="tests-cta-title">عايز تعرف نمط تعلقك؟</p>
        <p>جرّب اختبار نمط التعلق المجاني على الموقع. بياخد دقيقتين، والنتيجة بتطلعلك على طول ومش بتتحفظ في أي مكان.</p>
        <div class="actions"><a class="btn primary" href="/tests/attachment-style/">ابدأ الاختبار</a> <a class="btn" href="/tests/">كل الاختبارات</a></div>
      </div>''')
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
{social(url, a["title"], a["description"], og, a["title"])}
<meta property="article:published_time" content="{a["date"]}">
<meta name="theme-color" content="#2f6f62">
{FONTS}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{TOPBAR}
<main id="main">
  <article class="post">
    <div class="wrap narrow">
      <p class="crumbs"><a href="/articles/">المقالات</a>{(" · " + esc(a["chapter"])) if a.get("chapter") else ""}</p>
      <h1>{esc(a["title"])}</h1>
      <p class="post-meta">د. ميلاد ميخائيل · {meta}</p>
      <figure class="post-hero">{pic(a["image"], a["image_alt"], eager=True)}</figure>
      <div class="post-body">
{body}
      </div>
      <div class="book-box">
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
      </div>
      <div class="author-box">
        <img src="/assets/millad.jpg" width="96" height="96" alt="د. ميلاد ميخائيل" loading="lazy">
        <p><strong>د. ميلاد ميخائيل</strong><br>حاصل على الدكتوراه في الصحة النفسية من جامعة قناة السويس، وعضو الجمعية الأمريكية لعلم النفس (APA). <a href="/">اعرف أكتر</a></p>
      </div>
      {share_block(url, a["title"])}
      {tests_block}
      {more_block}
    </div>
  </article>
</main>
{FOOTER}
<script src="/assets/helper.js" defer></script>
</body>
</html>
'''


def share_block(url, title, label="شارك المقال"):
    """Share buttons: plain links (work without JS); assets/share.js adds copy + phone share sheet."""
    from urllib.parse import quote
    u, t = quote(url, safe=""), quote(title + " " + url, safe="")
    return f'''<aside class="share" data-url="{esc(url)}" data-title="{esc(title)}" aria-label="{esc(label)}">
        <p class="share-title">{esc(label)} مع حد ممكن يحتاجه</p>
        <div class="share-row">
          <a class="sh sh-wa" href="https://wa.me/?text={t}" target="_blank" rel="noopener">واتساب</a>
          <a class="sh sh-fb" href="https://www.facebook.com/sharer/sharer.php?u={u}" target="_blank" rel="noopener">فيسبوك</a>
          <a class="sh sh-tg" href="https://t.me/share/url?url={u}&amp;text={quote(title, safe="")}" target="_blank" rel="noopener">تيليجرام</a>
          <a class="sh sh-x" href="https://x.com/intent/post?text={t}" target="_blank" rel="noopener">X</a>
          <button type="button" class="sh sh-copy" hidden>انسخ اللينك</button>
          <button type="button" class="sh sh-native" hidden>مشاركة…</button>
        </div>
      </aside>'''


def card(a, heading="h2"):
    return f'''<li class="card">
        <a href="/articles/{a["slug"]}/">
          {pic(a["image"], a["image_alt"], sizes="(max-width: 640px) 100vw, 380px")}
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
<title>مقالات | د. ميلاد ميخائيل</title>
<meta name="description" content="مقالات بالعامية عن الحب والتعلق والعلاقات المؤذية واختيار شريك الحياة، من كتب د. ميلاد ميخائيل.">
<link rel="canonical" href="{SITE}/articles/">
{social(SITE + "/articles/", "مقالات د. ميلاد ميخائيل", "مقالات بالعامية عن الحب والتعلق والعلاقات المؤذية واختيار شريك الحياة.", SITE + "/assets/og/articles.jpg", "مقالات د. ميلاد ميخائيل", "website")}
<meta name="theme-color" content="#2f6f62">
{FONTS}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{TOPBAR}
<main id="main">
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
<script src="/assets/helper.js" defer></script>
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
    tj = os.path.join(ROOT, "tests", "tests.json")
    if os.path.exists(tj):
        with open(tj, encoding="utf-8") as f:
            tests = json.load(f)
        urls += [(f"{SITE}/tests/", "2026-11-04", False)] + [(f"{SITE}/tests/{x['slug']}/", "2026-11-04", False) for x in tests]
    vj = os.path.join(ROOT, "assets", "videos.json")
    if os.path.exists(os.path.join(ROOT, "videos", "index.html")) and os.path.exists(vj):
        with open(vj, encoding="utf-8") as f:
            vids = [v for v in json.load(f).get("videos", []) if v.get("published")]
        urls.append((f"{SITE}/videos/", max([v["published"] for v in vids] or ["2026-11-05"]), False))
    # standalone pages built by tools/build_pages.py
    for slug in ("sessions", "contact", "help-now", "privacy", "terms", "start", "ask", "feelings", "relationship-check", "questions", "porn-addiction", "challenges", "worksheets", "book", "battery"):
        if os.path.exists(os.path.join(ROOT, slug, "index.html")):
            urls.append((f"{SITE}/{slug}/", "2026-11-05", False))
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


def llms_txt(items):
    """llms.txt: a plain summary of the site for AI assistants (ChatGPT, Claude, Perplexity...).
    Rebuilt on every run so new articles and tests appear automatically."""
    tests = []
    tp = os.path.join(ROOT, "tests", "tests.json")
    if os.path.exists(tp):
        with open(tp, encoding="utf-8") as f:
            tests = json.load(f)
    L = [
        "# Dr. Millad Mikhail | د. ميلاد ميخائيل",
        "",
        "> Dr. Millad Mikhail (Arabic: د. ميلاد ميخائيل; also known as Dr. Milad Mounir / د. ميلاد منير) "
        "is a mental health educator and author. He holds a Ph.D. in Mental Health from Suez Canal University, Egypt (2022), "
        "and is a member of the American Psychological Association (APA). He is the author of the book "
        "«ليه بنحب اللي بيوجعنا؟» (Why Do We Love What Hurts Us?) and runs the Arabic YouTube channel "
        "جلسة شيزلونج (Glset Shezlong). This site publishes his articles and free psychological self-tests in simple Arabic.",
        "",
        "Key facts:",
        "- Full name: Millad Mounir Hakim Bekheet Mikhail. Same person as: Dr. Milad Mounir, Milad Mounir, د. ميلاد منير, د. ميلاد منير ميخائيل, ميلاد منير حكيم (older name forms, e.g. in older YouTube videos).",
        "- Ph.D. in Mental Health, Suez Canal University, 2022. Dissertation: \"Effectiveness of Logo Counselling on Reducing the Level of Existential Anxiety and Improving Psychological Immunity for University Students\".",
        "- Master's in Education (Mental Health), Suez Canal University, 2018. Specialized Diploma in Counseling and Clinical Psychology, Tanta University, 2021.",
        "- Credentials evaluated by World Education Services (WES). Visiting graduate student, JFK School of Psychology, National University (USA).",
        "- ORCID: 0009-0002-9254-367X",
        "- Topics: attachment styles, relationships, anxiety, meaning (logotherapy), self-esteem.",
        "",
        "## About",
        "- [Home (Arabic)](https://drmilladmikhail.com/): bio, credentials, theses, books, FAQ",
        "- [Home (English)](https://drmilladmikhail.com/en/): bio, credentials, theses, books, FAQ",
        "",
        "## Articles (Arabic)",
    ]
    for a in items:
        L.append(f"- [{a['title']}](https://drmilladmikhail.com/articles/{a['slug']}/): {a.get('description', '')}")
    if tests:
        L += ["", "## Free self-tests (Arabic, validated scales)"]
        for t in tests:
            L.append(f"- [{t['title']}](https://drmilladmikhail.com/tests/{t['slug']}/)")
    L += ["", "## Books",
          "- [ليه بنحب اللي بيوجعنا؟ (Arabic, Amazon)](https://www.amazon.com/dp/B0HPNCYWWS)",
          "- [Why Do We Love What Hurts Us? (English, Amazon)](https://www.amazon.com/dp/B0HPRPSPWF)",
          "- [Amazon author page](https://www.amazon.com/author/drmilladmikhail)",
          "", "## Elsewhere",
          "- [YouTube: جلسة شيزلونج](https://www.youtube.com/@DrMilladMikhail)",
          "- [Blog: راحة البال](https://blog.drmilladmikhail.com/)",
          "- [LinkedIn](https://www.linkedin.com/in/dr-millad-mikhail-a57b0b215)",
          "- [ORCID](https://orcid.org/0009-0002-9254-367X)",
          "- [WES credential badge](https://www.credly.com/badges/5a6796c0-5e1a-4ad5-b1af-fb64254e81cf/public_url)",
          ""]
    with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    items = load()
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_images.py")], check=True)
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
    llms_txt(items)
    # small public index used by the on-site helper (assets/helper.js)
    with open(os.path.join(ROOT, "assets", "articles-index.json"), "w", encoding="utf-8") as f:
        json.dump([{"slug": a["slug"], "title": a["title"], "ch": chapter_no(a) + 1, "date": a["date"]} for a in items],
                  f, ensure_ascii=False, indent=0)
    print(f"built {len(items)} article(s): " + ", ".join(a["slug"] for a in items))
    # start / book / battery pages list the latest articles and tests
    if os.path.exists(os.path.join(ROOT, "tools", "build_pages.py")):
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_pages.py")], check=True)
        sitemap(items)



def _analytics():
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "add_analytics.py")], check=True)

if __name__ == "__main__":
    main()
    _analytics()
