#!/usr/bin/env python3
"""«جديد» ticker under the header: always shows the newest things on the site.

His rule (2026-11-10): anything new that goes up on the site shows on the bar;
if nothing new went up, whatever was there before keeps showing.

How it works:
  * catalog() lists every piece of content (articles, tests, glossary terms,
    research papers, stories, exercises, challenges, worksheets, questions,
    videos). Items with their own date (articles, glossary "added", research
    "added", video "published") use it. Items without a date get the date the
    builder FIRST SAW them, remembered in content/news-state.json. So a new
    test or worksheet becomes "new" on the day it is built.
  * pick() takes the newest item of each kind, then the newest 3 of those
    (one per kind, for variety). Nothing new → the same 3 stay.
  * apply() writes them into every Arabic page as
    <script type="application/json" id="site-news"> (data only, not executed,
    so the CSP is unaffected); assets/nav.js turns it into the scrolling bar.
    No extra download, no layout jump from a late fetch.
Called by tools/add_analytics.py on every build. 18+ questions never go on the bar.
"""
import datetime
import html
import json
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "content", "news-state.json")
BASELINE = "2000-01-01"   # undated items that existed before the bar was automated
N = 3
SKIP_DIRS = {".git", ".github", "tools", "node_modules", "content", "en", "gifts", "docs", "test-artifacts"}
# tie-break when two kinds share a date (lower = first)
PRIORITY = {"article": 0, "test": 1, "video": 2, "worksheet": 3, "challenge": 4, "exercise": 5,
            "story": 6, "question": 7, "glossary": 8, "research": 9}


def _load(rel, default=None):
    path = os.path.join(ROOT, rel)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _items(data, key="items"):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get(key) or []
    return []


def catalog():
    out = []

    def add(kind, key, label, url, date=None):
        if label and url:
            out.append({"kind": kind, "k": f"{kind}:{key}", "t": label.strip(), "u": url, "d": date})

    for a in _items(_load("articles/articles.json", [])):
        add("article", a.get("slug"), "مقال جديد: " + (a.get("title") or ""), f"/articles/{a.get('slug')}/", a.get("date"))
    try:
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import build_tests
        for t in build_tests.TESTS:
            add("test", t["slug"], "اختبار جديد: " + (t.get("short") or t.get("title") or ""), f"/tests/{t['slug']}/", t.get("added"))
    except Exception:
        pass
    for g in _items(_load("content/glossary.json", {})) + _items(_load("content/glossary-more.json", {})):
        add("glossary", g.get("slug"), "مصطلح جديد في القاموس النفسي: " + (g.get("title") or ""), f"/glossary/{g.get('slug')}/", g.get("added"))
    for r in _items(_load("content/research-library.json", [])):
        rid = r.get("pmid") or r.get("doi")
        if rid:
            add("research", rid, "بحث جديد في مكتبة الأبحاث: " + (r.get("title_ar") or r.get("title") or ""),
                "/research/library/#" + quote("p" + str(rid), safe=""), r.get("added"))
    for s in _items(_load("content/stories.json", {}), "stories"):
        add("story", s.get("id"), "حكاية جديدة: " + (s.get("title") or ""), "/stories/", s.get("added"))
    for e in _items(_load("content/exercises.json", {})):
        add("exercise", e.get("slug"), "تمرين جديد: " + (e.get("title") or ""), "/exercise/", e.get("added"))
    for c in _items(_load("content/challenges.json", [])):
        add("challenge", c.get("id"), "تحدي جديد: " + (c.get("title") or ""), "/challenges/", c.get("added"))
    for w in _items(_load("content/worksheets.json", {})):
        add("worksheet", w.get("slug"), "ورقة تمرين جديدة: " + (w.get("title") or ""), "/worksheets/", w.get("added"))
    qs = _load("content/questions.json", {}) or {}
    adult = {s.get("slug") for s in qs.get("sections", []) if s.get("adult")}
    for q in qs.get("items", []):
        if q.get("section") in adult:
            continue
        add("question", q.get("id"), "سؤال جديد: " + (q.get("q") or ""), f"/questions/#{q.get('id')}", q.get("added"))
    vids = _load("assets/videos.json", {}) or {}
    hidden = set(vids.get("hidden", []))
    for v in vids.get("videos", []):
        if v.get("id") in hidden or v.get("short"):
            continue
        add("video", v.get("id"), "فيديو جديد: " + (v.get("title") or ""), "/videos/", (v.get("published") or "")[:10] or None)
    return out


def dated(items, today=None, write=True):
    """Give every item a date: its own, or the day the builder first saw it.
    write=False (used when a single page is rebuilt, e.g. build_research.py)
    never touches content/news-state.json."""
    today = today or datetime.date.today().isoformat()
    state = _load("content/news-state.json", None)
    first_run = state is None
    state = state or {}
    changed = False
    for it in items:
        if it["d"]:
            continue
        if it["k"] not in state:
            state[it["k"]] = BASELINE if first_run else today
            changed = True
        it["d"] = state[it["k"]]
    if changed and write:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(state.items())), f, ensure_ascii=False, indent=1)
            f.write("\n")
    return items


def pick(items, n=N):
    today = datetime.date.today().isoformat()
    newest = {}
    for it in items:
        if it["d"] > today:           # scheduled for later: not on the bar yet
            continue
        cur = newest.get(it["kind"])
        if cur is None or it["d"] > cur["d"]:
            newest[it["kind"]] = it
    ranked = sorted(newest.values(), key=lambda it: (it["d"], -PRIORITY.get(it["kind"], 99)), reverse=True)
    return [{"k": it["k"], "t": _short(it["t"]), "u": it["u"]} for it in ranked[:n]]


def _short(text, limit=110):
    text = re.sub(r"\s+", " ", text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


BLOCK_RE = re.compile(r'<script type="application/json" id="site-news">.*?</script>\n?', re.S)
_CACHE = {}


def _block(news):
    payload = json.dumps(news, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/json" id="site-news">{payload}</script>\n'


def inject(t, block=None):
    """Put the ticker data into one Arabic page (idempotent). Used by apply() and
    by builders that rebuild a page after add_analytics (build_research.py)."""
    if block is None:
        if "block" not in _CACHE:
            _CACHE["block"] = _block(pick(dated(catalog(), write=False)))
        block = _CACHE["block"]
    if "/assets/nav.js" not in t or 'lang="ar"' not in t[:400]:
        return t
    new = BLOCK_RE.sub("", t)
    i = new.find('<script src="/assets/nav.js')
    if i < 0:
        return t
    return new[:i] + block + new[i:]


def apply(root=ROOT):
    news = pick(dated(catalog()))
    block = _block(news)
    _CACHE["block"] = block
    changed = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                t = f.read()
            new = inject(t, block)
            if new != t:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                changed += 1
    print(f"news ticker: {len(news)} item(s), updated {changed} page(s): " + " | ".join(html.unescape(x['t'])[:40] for x in news))
    return news


if __name__ == "__main__":
    apply()
