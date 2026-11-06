#!/usr/bin/env python3
"""Pull the videos of the YouTube channel «جلسة شيزلونج» and show them on the site.

Run:  python3 tools/build_videos.py            (fetch from YouTube, then build)
      python3 tools/build_videos.py --offline  (build from assets/videos.json only)

The GitHub Action .github/workflows/videos.yml runs it every day, so a new upload
appears on the site by itself.

Where the list comes from:
  1. yt-dlp (if installed): every video on the channel's Videos and Shorts tabs,
     plus date + description for videos we don't know yet.
  2. The channel's RSS feed: the newest 15 uploads with date and description.
Everything is merged into assets/videos.json, which keeps growing (a video that
drops out of the feed is not lost). In that file:
  "hidden":   ids that never show on the site
  "featured": ids shown on the home page, in this order (else the newest)
  "categories": the sections of /videos/ (slug, name, optional note), in order
  "category_of": video id -> category slug. A new upload gets a guess from its
                 title (GUESS below); change it here if the guess is wrong.

What it writes:
  assets/videos.json   the data
  videos/index.html    page with every video (VideoObject structured data for Google)
  index.html           "فيديوهات" block between VIDEOS markers (newest 6)
  en/index.html        "Videos" block between VIDEOS markers (newest 3)
  sitemap.xml          via build_articles.sitemap()

Players are "click to play": the page only loads a small WebP thumbnail; the
YouTube player (privacy-enhanced youtube-nocookie.com) loads when someone clicks.
See assets/videos.js.
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_articles as ba  # noqa: E402  (shared header, footer, fonts, sitemap)

CHANNEL_ID = "UCTR2Y82KQ3743gUk6GgsIgA"
HANDLE = "https://www.youtube.com/@DrMilladMikhail"
DATA = os.path.join(ROOT, "assets", "videos.json")
SITE = ba.SITE
esc = ba.esc
UA = {"User-Agent": "Mozilla/5.0 (site build; drmilladmikhail.com)", "Accept-Language": "ar,en;q=0.8"}


# ---------------------------------------------------------------- fetching
def load_data():
    if os.path.exists(DATA):
        with open(DATA, encoding="utf-8") as f:
            return json.load(f)
    return {"channel": "جلسة شيزلونج", "hidden": [], "videos": []}


def from_rss():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
          "media": "http://search.yahoo.com/mrss/"}
    out = []
    for i, e in enumerate(root.findall("a:entry", ns)):
        vid = e.findtext("yt:videoId", namespaces=ns)
        link = (e.find("a:link", ns).get("href") if e.find("a:link", ns) is not None else "") or ""
        out.append({
            "id": vid,
            "title": (e.findtext("a:title", namespaces=ns) or "").strip(),
            "published": (e.findtext("a:published", namespaces=ns) or "")[:10],
            "description": (e.findtext("media:group/media:description", namespaces=ns) or "").strip(),
            "short": "/shorts/" in link,
        })
    print(f"rss: {len(out)} video(s)")
    return out


def ytdlp(args, timeout=300):
    r = subprocess.run(["yt-dlp", "--no-warnings", "--ignore-errors", *args],
                       capture_output=True, text=True, timeout=timeout)
    return [json.loads(ln) for ln in r.stdout.splitlines() if ln.startswith("{")]


def from_ytdlp():
    """Every video id on the Videos and Shorts tabs (newest first)."""
    out = []
    for tab, short in (("videos", False), ("shorts", True)):
        rows = ytdlp(["--flat-playlist", "-j", f"{HANDLE}/{tab}"])
        for i, x in enumerate(rows):
            if x.get("id") and len(x["id"]) == 11:
                out.append({"id": x["id"], "title": (x.get("title") or "").strip(), "short": short, "order": i})
        print(f"yt-dlp {tab}: {len(rows)} video(s)")
    return out


def details(ids):
    """Date + description for videos we only know by id (one light request each, no download)."""
    if not ids:
        return {}
    rows = ytdlp(["--skip-download", "-j", *[f"https://www.youtube.com/watch?v={i}" for i in ids]], timeout=900)
    got = {}
    for x in rows:
        d = x.get("upload_date") or ""
        got[x["id"]] = {
            "published": f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else "",
            "description": (x.get("description") or "").strip(),
            "title": (x.get("title") or "").strip(),
            "duration": x.get("duration") or 0,
        }
    print(f"yt-dlp details: {len(got)} of {len(ids)}")
    return got


def refresh(data):
    known = {v["id"]: v for v in data["videos"]}
    found = []
    try:
        found += from_ytdlp()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print("yt-dlp skipped:", e)
    try:
        found += from_rss()
    except Exception as e:  # network trouble must not break the site build
        print("rss skipped:", e)
    for f in found:
        v = known.setdefault(f["id"], {"id": f["id"]})
        for k in ("title", "published", "description"):
            if f.get(k):
                v[k] = f[k]
        if f.get("short"):
            v["short"] = True
        if "order" in f:
            v["order"] = f["order"] + (10000 if f.get("short") else 0)
    missing = [i for i, v in known.items() if not v.get("published") or not v.get("title")]
    try:
        for i, d in details(missing[:80]).items():
            for k, val in d.items():
                if val and not known[i].get(k):
                    known[i][k] = val
            if d.get("duration") and d["duration"] <= 180 and "short" not in known[i]:
                known[i]["short"] = d["duration"] <= 60
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print("details skipped:", e)
    # Newest first. The channel tab order (from yt-dlp) is the most reliable; a brand-new
    # upload seen only in the RSS feed has no order yet and goes on top.
    fresh = sorted((v for v in known.values() if "order" not in v), key=lambda v: v.get("published") or "", reverse=True)
    listed = sorted((v for v in known.values() if "order" in v), key=lambda v: v["order"])
    data["videos"] = fresh + listed
    return data


# Guess a category for a new upload from words in its title (first match wins).
GUESS = [
    ("immunity", r"مناع|قيمة|ثقة|سعاد"),
    ("anxiety", r"قلق|وسواس|وسواس|اكتئاب|ضغط|توتر|خوف|هلع"),
    ("sexuality", r"جنس|مراهق|تحرش"),
    ("behavior", r"[إا]دمان|غضب|عنف|عاد[ةه]"),
    ("understanding", r"مرض نفس|دكتور نفس|طبيب نفس|معالج|فصام|توحد|علاج"),
    ("success", r"نجاح|تفكير|شغل|هدف"),
]


def categorize(data):
    cats = data.setdefault("category_of", {})
    for v in data["videos"]:
        if v["id"] not in cats:
            t = v.get("title", "")
            cats[v["id"]] = next((slug for slug, rx in GUESS if re.search(rx, t)), "other")
    return data


# ---------------------------------------------------------------- rendering
PLAY = '<span class="yt-play" aria-hidden="true"><svg viewBox="0 0 68 48"><path class="bg" d="M66.5 7.7a8.5 8.5 0 0 0-6-6C55.2.4 34 .4 34 .4s-21.2 0-26.5 1.3a8.5 8.5 0 0 0-6 6C.2 13 .2 24 .2 24s0 11 1.3 16.3a8.5 8.5 0 0 0 6 6c5.3 1.3 26.5 1.3 26.5 1.3s21.2 0 26.5-1.3a8.5 8.5 0 0 0 6-6C67.8 35 67.8 24 67.8 24s0-11-1.3-16.3Z"/><path class="fg" d="M45 24 27 14v20"/></svg></span>'


def visible(data):
    hidden = set(data.get("hidden", []))
    return [v for v in data["videos"] if v["id"] not in hidden and v.get("title")]


def en_date(iso):
    m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    y, mo, d = iso.split("-")
    return f"{m[int(mo) - 1]} {int(d)}, {y}"


def vcard(v, heading="h3", lang="ar", tag=""):
    vid, t = v["id"], v["title"]
    label = (f"شغّل الفيديو: {t}" if lang == "ar" else f"Play video: {t}")
    date = ""
    if v.get("published"):
        date = f'<span class="card-date">{ba.ar_date(v["published"]) if lang == "ar" else en_date(v["published"])}</span>'
    kind = " vcard-short" if v.get("short") else ""
    title_attr = '' if lang == "ar" else ' lang="ar" dir="rtl"'
    return f'''<li class="vcard{kind}">
          <a class="yt" href="https://www.youtube.com/watch?v={vid}" data-id="{vid}" target="_blank" rel="noopener" aria-label="{esc(label)}">
            <img src="https://i.ytimg.com/vi_webp/{vid}/hqdefault.webp" width="480" height="360" alt="" loading="lazy" decoding="async">
            {PLAY}
          </a>
          <span class="card-body">
            {f'<span class="vtag">{esc(tag)}</span>' if tag else ""}
            <{heading}{title_attr}>{esc(t)}</{heading}>
            {date}
          </span>
        </li>'''


def pick_home(vs, n, featured=()):
    """Home page shows the "featured" ids from videos.json (your choice, in that order);
    if fewer than n are featured, the newest videos fill the rest."""
    by_id = {v["id"]: v for v in vs}
    out = [by_id[i] for i in featured if i in by_id][:n]
    longs = [v for v in vs if not v.get("short")]
    out += [v for v in (longs or vs) if v not in out][: n - len(out)]
    return out


def home_block_ar(vs, featured=(), names=None, cat_of=None):
    names, cat_of = names or {}, cat_of or {}
    cards = "\n        ".join(vcard(v, tag=names.get(cat_of.get(v["id"]), "")) for v in pick_home(vs, 6, featured))
    return f'''<!-- VIDEOS:START -->
  <section class="section" id="videos" aria-labelledby="vid-h">
    <div class="wrap">
      <div class="section-head">
        <svg class="icon" viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="7" width="26" height="18" rx="4"/><path d="m13 12 7 4-7 4Z"/></svg>
        <h2 id="vid-h">فيديوهات من «جلسة شيزلونج»</h2>
      </div>
      <p class="section-intro">اتفرّج هنا على طول، من غير ما تخرج من الموقع.</p>
      <ul class="vcards">
        {cards}
      </ul>
      <div class="actions"><a class="btn primary" href="/videos/">كل الفيديوهات</a> <a class="btn" href="{HANDLE}?sub_confirmation=1" target="_blank" rel="noopener">اشترك في القناة</a></div>
    </div>
  </section>
  <!-- VIDEOS:END -->'''


def home_block_en(vs, featured=()):
    cards = "\n        ".join(vcard(v, lang="en") for v in pick_home(vs, 3, featured))
    return f'''<!-- VIDEOS:START -->
  <section class="section" id="videos" aria-labelledby="vid-h">
    <div class="wrap">
      <div class="section-head">
        <svg class="icon" viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="7" width="26" height="18" rx="4"/><path d="m13 12 7 4-7 4Z"/></svg>
        <h2 id="vid-h">Videos <span class="muted">(in Arabic)</span></h2>
      </div>
      <p class="section-intro">From my YouTube channel «Glset Shezlong»: relationships, anxiety and finding meaning.</p>
      <ul class="vcards">
        {cards}
      </ul>
      <div class="actions"><a class="btn primary" href="/videos/" hreflang="ar">All videos</a> <a class="btn" href="{HANDLE}?sub_confirmation=1" target="_blank" rel="noopener">Subscribe</a></div>
    </div>
  </section>
  <!-- VIDEOS:END -->'''


def put_block(path, block, before):
    """Replace the VIDEOS block, or insert it once just before `before`."""
    with open(path, encoding="utf-8") as f:
        t = f.read()
    start, end = "<!-- VIDEOS:START -->", "<!-- VIDEOS:END -->"
    if start in t:
        t = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, t, flags=re.S)
    elif before in t:
        t = t.replace(before, block + "\n" + before, 1)
    else:
        print("no place for videos block in", path)
        return
    if "/assets/videos.js" not in t:
        t = t.replace("</body>", '<script src="/assets/videos.js" defer></script>\n</body>', 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(t)


def ld_video(v):
    d = {"@type": "VideoObject", "name": v["title"],
         "description": (v.get("description") or v["title"])[:500],
         "thumbnailUrl": [f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"],
         "uploadDate": v["published"],
         "contentUrl": f"https://www.youtube.com/watch?v={v['id']}",
         "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}",
         "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    return d


def page(vs, data=None):
    data = data or {}
    cats = data.get("categories") or [{"slug": "other", "name": "فيديوهات"}]
    cat_of = data.get("category_of", {})
    known = {c["slug"] for c in cats}
    groups = {c["slug"]: [] for c in cats}
    groups.setdefault("other", [])
    for v in vs:
        groups[cat_of.get(v["id"]) if cat_of.get(v["id"]) in known else "other"].append(v)
    if "other" not in known:
        cats = cats + [{"slug": "other", "name": "متنوع"}]
    cats = [c for c in cats if groups.get(c["slug"])]
    chips = "\n        ".join(f'<a href="#{c["slug"]}">{esc(c["name"])} <span>{len(groups[c["slug"]])}</span></a>' for c in cats)
    sec = f'<nav class="vchips" aria-label="تصنيفات الفيديوهات">\n        {chips}\n      </nav>' if len(cats) > 1 else ""
    for c in cats:
        items = groups[c["slug"]]
        longs = [v for v in items if not v.get("short")]
        shorts = [v for v in items if v.get("short")]
        note = f'\n        <p class="vnote">{esc(c["note"])}</p>' if c.get("note") else ""
        body = ""
        if longs:
            body += '<ul class="vcards">\n          ' + "\n          ".join(vcard(v, "h3") for v in longs) + "\n        </ul>"
        if shorts:
            body += '\n        <ul class="vcards vcards-short">\n          ' + "\n          ".join(vcard(v, "h3") for v in shorts) + "\n        </ul>"
        sec += f'''
      <section class="vcat" id="{c["slug"]}" aria-labelledby="h-{c["slug"]}">
        <h2 id="h-{c["slug"]}">{esc(c["name"])} <span class="vcount">{len(items)} فيديو</span></h2>{note}
        {body}
      </section>'''
    if not vs:
        sec = f'<p>الفيديوهات هتظهر هنا قريب. لحد ما تظهر، تقدر تتفرّج على <a href="{HANDLE}">القناة على يوتيوب</a>.</p>'
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "فيديوهات د. ميلاد ميخائيل",
          "url": f"{SITE}/videos/", "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "hasPart": [ld_video(v) for v in vs if v.get("published")]}
    desc = "فيديوهات بالعامية عن الحب والتعلق والقلق والبحث عن المعنى، من قناة «جلسة شيزلونج» لـ د. ميلاد ميخائيل."
    first = vs[0]["id"] if vs else None
    og = f"https://i.ytimg.com/vi/{first}/hqdefault.jpg" if first else f"{SITE}/assets/og/home.jpg"
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>فيديوهات «جلسة شيزلونج» | د. ميلاد ميخائيل</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/videos/">
{ba.social(SITE + "/videos/", "فيديوهات د. ميلاد ميخائيل", desc, f"{SITE}/assets/og/home.jpg", "د. ميلاد ميخائيل", "website")}
<meta name="theme-color" content="#2f6f62">
<link rel="preconnect" href="https://i.ytimg.com">
{ba.FONTS}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{ba.TOPBAR}
<main id="main">
  <section class="section videos-index">
    <div class="wrap">
      <h1>فيديوهات «جلسة شيزلونج»</h1>
      <p class="section-intro">{len(vs)} فيديو مقسّمين حسب الموضوع. اختار الموضوع اللي يهمك، ودوس على أي فيديو يشتغل هنا على طول. الفيديوهات الجديدة بتظهر لوحدها أول ما تنزل على القناة.</p>
      {sec}
      <div class="actions"><a class="btn" href="{HANDLE}?sub_confirmation=1" target="_blank" rel="noopener">اشترك في القناة على يوتيوب</a></div>
    </div>
  </section>
</main>
{ba.FOOTER}
<script src="/assets/videos.js" defer></script>
<script src="/assets/helper.js" defer></script>
</body>
</html>
'''


def main():
    data = load_data()
    if "--offline" not in sys.argv:
        data = refresh(data)
    categorize(data)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    vs = visible(data)
    os.makedirs(os.path.join(ROOT, "videos"), exist_ok=True)
    with open(os.path.join(ROOT, "videos", "index.html"), "w", encoding="utf-8") as f:
        f.write(page(vs, data))
    if vs:
        put_block(os.path.join(ROOT, "index.html"), home_block_ar(vs, data.get("featured", []), {c["slug"]: c["name"] for c in data.get("categories", [])}, data.get("category_of")), '<section class="book-feature" id="book"')
        put_block(os.path.join(ROOT, "en", "index.html"), home_block_en(vs, data.get("featured", [])), '<section class="section" id="blog"')
    ba.sitemap(ba.load())
    print(f"videos: {len(vs)} shown ({sum(1 for v in vs if v.get('short'))} short)")



def _analytics():
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "add_analytics.py")], check=True)

if __name__ == "__main__":
    main()
    _analytics()
