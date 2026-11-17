#!/usr/bin/env python3
"""Build «سينما على الشيزلونج» (/cinema/): psychological readings of films, in simple Egyptian Arabic.

Source of truth:
  content/cinema.json             one entry per film (see the fields below)
  content/cinema/<slug>.html      the body (HTML fragment, same classes as articles:
                                  h2, ul/ol, .exercise, .safety, plus .film-facts and .spoiler-note)
  assets/cinema/<image>.svg/.jpg  an ORIGINAL illustration (never a film poster or still: copyright)

Each entry: {"slug", "film", "film_ar", "year", "director", "title", "theme", "description",
             "summary", "date", "minutes", "image", "image_alt", "spoilers", "related", "refs",
             "trailer" (optional: {"youtube_id", "channel", "title"}), "reviewed_on"}
Trailer: only an OFFICIAL trailer (studio channel or a licensed trailer channel such as Movieclips),
never a clip that spoils the ending. It is click-to-play via assets/videos.js (youtube-nocookie,
nothing loads from YouTube until the visitor presses play).
Review rule (content/REVIEW-POLICY.md): an entry goes live only when it has "reviewed_on"
(the date Dr. Millad approved it). Without it the entry is skipped, and /cinema/ isn't built
until at least one entry is reviewed. CINEMA_PREVIEW=1 builds unreviewed entries for a local
preview only — never commit a preview build.

Writing rules: we read a FICTIONAL character, we don't diagnose anyone (or the actor); say
clearly where the film exaggerates; spoiler warning before the ending; safety note with crisis
lines; at least 2 refs you actually opened; no ratings/stars (this is not a film review).

Called from tools/build_pages.py; the sitemap entries are added by tools/build_articles.py.
"""
import json
import os
import re
from pathlib import Path

import build_articles as ba
from site_header import header_for

ROOT = Path(__file__).resolve().parents[1]
SITE = ba.SITE
esc = ba.esc
REQUIRED = ("slug", "film", "year", "director", "title", "theme", "description", "summary",
            "date", "image", "image_alt", "refs")


def load(root=ROOT, preview=None):
    preview = os.environ.get("CINEMA_PREVIEW") == "1" if preview is None else preview
    path = Path(root) / "content" / "cinema.json"
    if not path.exists():
        return []
    items, seen = [], set()
    for f in json.loads(path.read_text(encoding="utf-8"))["items"]:
        for k in REQUIRED:
            if not f.get(k):
                raise SystemExit(f"cinema {f.get('slug')}: missing '{k}'")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", f["slug"]) or f["slug"] in seen:
            raise SystemExit(f"cinema: bad or duplicate slug {f['slug']}")
        seen.add(f["slug"])
        if len(f["refs"]) < 2:
            raise SystemExit(f"cinema {f['slug']}: needs at least 2 refs")
        if not (Path(root) / "content" / "cinema" / (f["slug"] + ".html")).exists():
            raise SystemExit(f"cinema {f['slug']}: content/cinema/{f['slug']}.html not found")
        if not (Path(root) / "assets" / "cinema" / (f["image"] + ".jpg")).exists():
            raise SystemExit(f"cinema {f['slug']}: assets/cinema/{f['image']}.jpg not found")
        reviewed = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f.get("reviewed_on", ""))))
        if reviewed or preview:
            items.append(f)
    return sorted(items, key=lambda f: (f["date"], f["slug"]), reverse=True)


def pic(f, eager=False, sizes="(max-width: 700px) 100vw, 700px"):
    n = f["image"]
    load_attr = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/webp" srcset="/assets/cinema/{n}-600.webp 600w, /assets/cinema/{n}.webp 1200w" sizes="{sizes}">'
            f'<img src="/assets/cinema/{n}.jpg" width="1200" height="800" alt="{esc(f["image_alt"])}" {load_attr}></picture>')


def shell(rel, title, description, og, kind, ld, body):
    url = f"{SITE}/{rel}/"
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | د. ميلاد ميخائيل</title>
<meta name="description" content="{esc(description)}">
<meta name="author" content="د. ميلاد ميخائيل">
<link rel="canonical" href="{url}">
{ba.social(url, title, description, og, title, kind)}
<meta name="theme-color" content="#2f6f62">
{ba.FONTS}
<link rel="stylesheet" href="/assets/cinema.css?v=1">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("<", chr(92) + "u003c")}</script>
</head>
<body class="cinema-page">
{header_for(rel + "/index.html")}
<main id="main">{body}</main>
{ba.FOOTER}
<script src="/assets/nav.js" defer></script>
<script src="/assets/helper.js" defer></script>
<script src="/assets/videos.js" defer></script>
</body>
</html>
'''


def card(f):
    return f'''<li class="card film-card">
        <a href="/cinema/{f["slug"]}/">
          {pic(f, sizes="(max-width: 640px) 100vw, 380px")}
          <span class="card-body">
            <span class="film-label" lang="en" dir="ltr">{esc(f["film"])} · {esc(f["year"])}</span>
            <h2>{esc(f["title"])}</h2>
            <span class="card-desc">{esc(f["theme"])}</span>
          </span>
        </a>
      </li>'''


def trailer_block(f):
    t = f.get("trailer")
    if not t or not re.fullmatch(r"[\w-]{11}", t.get("youtube_id", "")):
        return ""
    vid = t["youtube_id"]
    return f'''<figure class="film-trailer">
        <a class="yt" href="https://www.youtube.com/watch?v={vid}" data-id="{vid}" target="_blank" rel="noopener" aria-label="شغّل الفيديو: الإعلان الرسمي لفيلم {esc(f["film"])}">
          <img src="https://i.ytimg.com/vi_webp/{vid}/hqdefault.webp" width="480" height="360" alt="" loading="lazy" decoding="async">
          <span class="yt-play" aria-hidden="true"><svg viewBox="0 0 68 48"><path class="bg" d="M66.5 7.7a8.5 8.5 0 0 0-6-6C55.2.4 34 .4 34 .4s-21.2 0-26.5 1.3a8.5 8.5 0 0 0-6 6C.2 13 .2 24 .2 24s0 11 1.3 16.3a8.5 8.5 0 0 0 6 6c5.3 1.3 26.5 1.3 26.5 1.3s21.2 0 26.5-1.3a8.5 8.5 0 0 0 6-6C67.8 35 67.8 24 67.8 24s0-11-1.3-16.3Z"/><path class="fg" d="M45 24 27 14v20"/></svg></span>
        </a>
        <figcaption>الإعلان الرسمي للفيلم من قناة <span lang="en" dir="ltr">{esc(t.get("channel", "YouTube"))}</span> على يوتيوب. مفيهوش حرق للنهاية، والفيديو مش بيشتغل غير لما تضغط.</figcaption>
      </figure>'''


def film_page(f, others):
    rel = f"cinema/{f['slug']}"
    url = f"{SITE}/{rel}/"
    body_html = (ROOT / "content" / "cinema" / (f["slug"] + ".html")).read_text(encoding="utf-8").strip()
    ids = iter(range(1, 100))
    body_html = re.sub(r"<h2>", lambda m: f'<h2 id="s{next(ids)}">', body_html)
    toc = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in re.findall(r'<h2 id="(s\d+)">(.*?)</h2>', body_html)
                  if not t.startswith("المصادر"))
    og = f"{SITE}/assets/og/cinema-{f['slug']}.jpg"
    if not (ROOT / "assets" / "og" / f"cinema-{f['slug']}.jpg").exists():
        og = f"{SITE}/assets/cinema/{f['image']}.jpg"
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f["title"],
        "description": f["description"],
        "image": og,
        "datePublished": f["date"],
        "dateModified": f.get("updated", f["date"]),
        "inLanguage": "ar",
        "mainEntityOfPage": url,
        "articleSection": "سينما على الشيزلونج",
        "about": [{"@type": "Movie", "name": f["film"], "dateCreated": f["year"],
                   "director": {"@type": "Person", "name": f["director"]}},
                  {"@type": "Thing", "name": f["theme"]}],
        "author": {"@id": f"{SITE}/#person"},
        "publisher": {"@id": f"{SITE}/#person"},
        "citation": [r["url"] for r in f["refs"]],
    }
    more = "".join(card(o) for o in others[:3])
    more_block = (f'<aside class="more"><h2>أفلام تانية</h2><ul class="cards">{more}</ul></aside>' if more else "")
    body = f'''
  <article class="post">
    <div class="wrap narrow">
      <nav class="crumbs" aria-label="مسار التصفح"><a href="/">الرئيسية</a> · <a href="/cinema/">سينما على الشيزلونج</a></nav>
      <h1>{esc(f["title"])}</h1>
      <p class="post-meta"><a href="/about/" rel="author">د. ميلاد ميخائيل</a> · <time datetime="{f["date"]}">{ba.ar_date(f["date"])}</time>{f" · {f['minutes']} دقايق قراءة" if f.get("minutes") else ""}</p>
      <figure class="post-hero">{pic(f, eager=True)}<figcaption>رسم توضيحي، مش من الفيلم</figcaption></figure>
      <aside class="answer-box" aria-labelledby="ans-{f["slug"]}"><h2 id="ans-{f["slug"]}">باختصار</h2><p>{esc(f["summary"])}</p>
      <nav class="toc" aria-label="في التحليل ده"><p class="toc-title">في التحليل ده</p><ol>{toc}</ol></nav></aside>
      {trailer_block(f)}
      <div class="post-body">
{body_html}
      </div>
      <p class="film-note">«سينما على الشيزلونج» قراءة نفسية لشخصيات خيالية بهدف التوعية. مش تقييم للفيلم، ولا تشخيص لأي حد.</p>
      {more_block}
      <p class="back-link"><a class="btn" href="/cinema/">كل الأفلام</a></p>
    </div>
  </article>'''
    return shell(rel, f["title"], f["description"], og, "article", ld, body)


def index_page(items):
    cards = "\n      ".join(card(f) for f in items)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "سينما على الشيزلونج: تحليل نفسي للأفلام",
          "url": f"{SITE}/cinema/", "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "hasPart": [{"@type": "Article", "headline": f["title"], "url": f"{SITE}/cinema/{f['slug']}/"} for f in items]}
    desc = "تحليل نفسي للأفلام بالعربي البسيط: نفهم الشخصيات ومشاعرها، ونشوف نفسنا فيها، من غير ما نشخّص حد."
    body = f'''
  <section class="section cinema-hero">
    <div class="wrap">
      <nav class="crumbs" aria-label="مسار التصفح"><a href="/">الرئيسية</a> · سينما على الشيزلونج</nav>
      <h1>سينما على الشيزلونج</h1>
      <p class="cinema-sub">تحليل نفسي للأفلام</p>
      <p class="section-intro">بنتفرّج على الأفلام بعين نفسية: نفهم ليه الشخصيات بتعمل اللي بتعمله، ونشوف نفسنا فيها، من غير ما نشخّص حد.</p>
    </div>
  </section>
  <section class="section cinema-list">
    <div class="wrap">
      <ul class="cards">
      {cards}
      </ul>
      <p class="film-note">كل التحليلات قراءة لشخصيات خيالية بهدف التوعية، وفيها تنبيه قبل حرق الأحداث. الرسومات أصلية، مش صور من الأفلام.</p>
    </div>
  </section>'''
    return shell("cinema", "سينما على الشيزلونج: تحليل نفسي للأفلام", desc, f"{SITE}/assets/og/home.jpg", "website", ld, body)


def build(root=ROOT):
    items = load(root)
    if not items:
        return []
    pages = {"cinema": index_page(items)}
    for i, f in enumerate(items):
        pages[f"cinema/{f['slug']}"] = film_page(f, items[:i] + items[i + 1:])
    for rel, html in pages.items():
        p = Path(root) / rel / "index.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists() or p.read_text(encoding="utf-8") != html:
            p.write_text(html, encoding="utf-8")
    return list(pages)


def sitemap_urls(root=ROOT):
    items = load(root, preview=False)
    if not items:
        return []
    newest = max(f.get("updated", f["date"]) for f in items)
    return [(f"{SITE}/cinema/", newest, False)] + [
        (f"{SITE}/cinema/{f['slug']}/", f.get("updated", f["date"]), False) for f in items]


if __name__ == "__main__":
    print("Built cinema:", ", ".join(build()) or "(nothing reviewed yet)")
