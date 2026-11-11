"""Optional browser-local bookmarks for public stories and exercises only."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def button(esc, kind, slug, title):
    if kind not in ("story", "exercise") or not isinstance(slug, str) or not SLUG.fullmatch(slug):
        return ""
    return (f'<div class="bookmark-action"><button type="button" class="bookmark-button" '
            f'data-save-id="{kind}:{esc(slug)}" data-save-title="{esc(title)}" '
            'aria-pressed="false" hidden>احفظ على جهازي</button></div>')


def notice():
    return '''<aside class="bookmark-notice" aria-label="حفظ العناوين">
<p><a href="/saved/">محفوظاتي</a> · احفظ الحكايات والتمارين اللي عايز ترجع لها على المتصفح ده بس، من غير حساب. الحفظ ده للعناوين فقط، مش إجاباتك أو ملاحظاتك.</p>
<p>لو الجهاز مشترك، أي حد بيستخدم نفس المتصفح ممكن يشوف المحفوظات. مفيش مزامنة بين الأجهزة، ومسح بيانات الموقع ممكن يمسحها.</p>
<p class="bookmark-status" role="status" aria-live="polite"></p>
<noscript><p>حفظ العناوين محتاج JavaScript؛ تقدر تقرأ المحتوى عادي من غيره.</p></noscript>
</aside>'''


def catalog():
    from build_extras import _load, eligible_stories
    records = {}
    for n, item in enumerate(eligible_stories(), 1):
        slug = item.get("id")
        if isinstance(slug, str) and SLUG.fullmatch(slug):
            records["story:" + slug] = {
                "title": item["title"], "kind": "story", "url": f"/stories/#story-{n}"}
    for item in _load("exercises.json", {"items": []})["items"]:
        if SLUG.fullmatch(item["slug"]):
            records["exercise:" + item["slug"]] = {
                "title": item["title"], "kind": "exercise", "url": "/exercise/#" + item["slug"]}
    return records


def write_catalog():
    text = json.dumps(catalog(), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    (ROOT / "assets/bookmarks-catalog.js").write_text(
        "// Public content metadata only; visitor bookmarks never enter this file.\n"
        "window.DMBookmarkCatalog=" + text + ";\n", encoding="utf-8")


def attach(html):
    def asset(name):
        digest = hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest()[:12]
        return f"/assets/{name}?v={digest}"
    html = html.replace("</head>", f'<link rel="stylesheet" href="{asset("bookmarks.css")}">\n</head>', 1)
    scripts = "".join(f'<script src="{asset(name)}" defer></script>\n'
                      for name in ("bookmarks-catalog.js", "bookmarks.js"))
    return html.replace("</body>", scripts + "</body>", 1)


def build(ba, page, write, SITE):
    body = '''<section class="section bookmarks-page"><div class="wrap narrow">
<p class="crumbs"><a href="/">الصفحة الرئيسية</a></p>
<p class="bookmark-kicker">حاجات حابب ترجع لها</p>
<h1>محفوظاتي</h1>
<p class="section-intro">حكاية لمستك، أو تمرين عايز تجربه بعدين؟ احفظه من صفحته، وهتلاقيه هنا على نفس الجهاز والمتصفح.</p>
''' + notice() + '''
<div class="bookmark-toolbar" hidden>
<div class="bookmark-filters" role="group" aria-label="نوع المحتوى المحفوظ">
<button type="button" data-saved-filter="all" aria-pressed="true">الكل</button>
<button type="button" data-saved-filter="story" aria-pressed="false">الحكايات</button>
<button type="button" data-saved-filter="exercise" aria-pressed="false">التمارين</button>
</div><button type="button" id="bookmark-clear" disabled>امسح المحفوظات</button>
</div>
<h2 id="bookmark-heading" tabindex="-1">العناوين المحفوظة</h2>
<p id="bookmark-count"></p>
<div id="bookmark-empty" class="bookmark-empty" hidden>
<h3>لسه مفيش عناوين محفوظة هنا</h3>
<p>افتح حكاية أو تمرين واضغط «احفظ على جهازي». ولو حفظت من جهاز تاني، المحفوظات مش هتظهر هنا.</p>
</div>
<ul id="bookmark-list" class="bookmark-list" aria-labelledby="bookmark-heading"></ul>
<div class="bookmark-browse"><a class="btn" href="/stories/">اختار حكاية</a>
<a class="btn" href="/exercise/">اختار تمرين</a></div>
<dialog id="bookmark-confirm" aria-labelledby="bookmark-confirm-title">
<h2 id="bookmark-confirm-title">تمسح كل المحفوظات من المتصفح ده؟</h2>
<p>ده بيمسح عناوين الحكايات والتمارين المحفوظة بس. ملاحظات التمارين وتقدم التحديات مش هيتغيّروا، وتقدر تحفظ العناوين تاني وقت ما تحب.</p>
<div class="bookmark-dialog-actions"><button type="button" id="bookmark-cancel" autofocus>لا، رجوع</button>
<button type="button" id="bookmark-confirm-clear">امسح المحفوظات فقط</button></div>
</dialog>
</div></section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "محفوظاتي",
          "url": SITE + "/saved/", "inLanguage": "ar"}
    write("saved", attach(page("saved", "محفوظاتي",
          "احفظ حكايات وتمارين د. ميلاد ميخائيل للرجوع لها على نفس المتصفح، من غير حساب.", body, ld)))
