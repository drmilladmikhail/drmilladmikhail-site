"""A public, consent-gated content directory with entirely local text search."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = {"story": "حكاية", "exercise": "تمرين", "concept": "معنى من القاموس"}


def records():
    import build_extras
    import build_glossary
    import build_saved
    aliases = build_extras._load("explore-aliases.json", {})
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in aliases.items()):
        raise ValueError("Explore aliases must be plain text")
    groups = {"story": [], "exercise": [], "concept": []}
    for n, item in enumerate(build_extras.eligible_stories(), 1):
        sid = item.get("id", "")
        if not isinstance(sid, str) or not build_saved.SLUG.fullmatch(sid):
            continue
        tag = item.get("tag", "")
        groups["story"].append({
            "id": "story:" + sid, "kind": "story", "title": item["title"],
            "summary": "عن " + tag + ". للقراءة والتأمل، مش للتشخيص.",
            "search": " ".join((item["title"], tag, sid.replace("-", " "), "حكاية تجربة",
                               aliases.get("story:" + sid, ""))),
            "href": f"/stories/#story-{n}"})
    for item in build_extras._load("exercises.json", {"items": []})["items"]:
        groups["exercise"].append({
            "id": "exercise:" + item["slug"], "kind": "exercise", "title": item["title"],
            "summary": item["goal"], "search": " ".join((item["title"], item["goal"],
                item["slug"].replace("-", " "), "تمرين تدريب", aliases.get("exercise:" + item["slug"], ""))),
            "href": "/exercise/#" + item["slug"]})
    for item in build_glossary.load(ROOT)["items"]:
        groups["concept"].append({
            "id": "concept:" + item["slug"], "kind": "concept", "title": item["title"],
            "summary": item["summary"], "search": " ".join((item["title"], item["english"],
                item["summary"], item["category"], *item["aliases"])),
            "href": "/glossary/" + item["slug"] + "/"})
    # Show all three kinds in the opening results, rather than an entire group first.
    output = [group[i] for i in range(max(map(len, groups.values())))
              for group in groups.values() if i < len(group)]
    if len({x["id"] for x in output}) != len(output):
        raise ValueError("Duplicate explore catalog IDs")
    return output


def build(ba, page, write, SITE):
    esc = ba.esc
    items = records()
    cards = "".join(
        f'<li class="explore-item" data-kind="{r["kind"]}" data-title="{esc(r["title"])}" '
        f'data-search="{esc(r["search"])}"><a class="explore-link" href="{esc(r["href"])}" '
        'target="_blank" rel="noopener">'
        f'<span class="explore-kind">{LABELS[r["kind"]]}</span>'
        f'<h2>{esc(r["title"])}</h2><p>{esc(r["summary"])}</p>'
        '<span class="explore-open">افتح المحتوى<span class="sr-only">، في لسان جديد</span></span>'
        '</a></li>' for r in items)
    body = f'''<section class="section explore-page"><div class="wrap explore-wrap">
<p class="crumbs"><a href="/">الصفحة الرئيسية</a></p>
<p class="explore-kicker">حكاية تقراها، تمرين تجربه، ومعنى تفهمه</p>
<h1>دوّر واكتشف</h1>
<p class="section-intro">ابحث في الحكايات والتمارين ومعاني القاموس. اكتب كلمة أو اختار موضوع، وبعدها افتح اللي يهمّك بالترتيب اللي يناسبك.</p>
<p class="explore-privacy">كلمات البحث بتفضل في الصفحة دي فقط؛ مش بتتبعت للموقع، ومش بتتحفظ عندنا أو في بيانات المتصفح أو رابط الصفحة. ده بحث في المحتوى، مش أداة تشخيص.</p>
<div class="explore-controls" hidden>
<form id="explore-form" role="search">
<label for="explore-query">بتدوّر على إيه؟</label>
<div class="explore-input-row"><input id="explore-query" type="search" maxlength="120"
autocomplete="off" spellcheck="false" placeholder="زي: القلق، الحدود، الحزن"
aria-describedby="explore-hint" aria-controls="explore-results">
<button type="submit">ابحث</button><button type="button" id="explore-clear" disabled>امسح البحث</button></div>
<p id="explore-hint">تقدر تبحث بالعربي أو بالمصطلح الإنجليزي الموجود في القاموس. النتائج بتتحدث وإنت بتكتب، ومفيش إجابات شخصية مطلوبة.</p>
</form>
<div class="explore-topics" role="group" aria-label="موضوعات للبحث">
<span>جرّب موضوع:</span>
{"".join(f'<button type="button" data-explore-topic="{t}">{t}</button>' for t in ("القلق", "العلاقات", "فقدان الشغف", "الحدود", "الوحدة", "الحزن"))}
</div>
<div class="explore-filters" role="group" aria-label="نوع المحتوى">
<button type="button" data-explore-kind="all" aria-pressed="true">الكل</button>
<button type="button" data-explore-kind="story" aria-pressed="false">الحكايات</button>
<button type="button" data-explore-kind="exercise" aria-pressed="false">التمارين</button>
<button type="button" data-explore-kind="concept" aria-pressed="false">القاموس</button>
</div></div>
<p class="explore-reading">المحتوى كله متاح للتصفح تحت. لو البحث التفاعلي مش ظاهر، تقدر تفتح أي عنوان مباشرة.</p>
<div class="explore-result-head"><p id="explore-count" role="status" aria-live="polite">{len(items)} مادة متاحة للتصفح</p>
<a href="/saved/">افتح محفوظاتي</a></div>
<div id="explore-empty" class="explore-empty" hidden><h2>مفيش نتيجة بالبحث ده</h2>
<p>جرّب كلمة أبسط أو غيّر نوع المحتوى. عدم وجود نتيجة مش معناه تقييم لحالتك.</p>
<button type="button" id="explore-reset">اعرض كل المحتوى</button></div>
<ul id="explore-results" class="explore-results">{cards}</ul>
<button type="button" id="explore-more" hidden>اعرض المزيد</button>
<p class="explore-footnote">الروابط بتفتح في لسان جديد علشان بحثك يفضل قدامك. تقدر تقفل الصفحة وقت ما تحب؛ مفيش تسجيل ولا خطوات لازم تخلصها.</p>
<p class="related">المقالات والأبحاث مش ضمن البحث ده: افتح <a href="/articles/">المقالات</a> أو <a href="/research/library/">مكتبة الأكاديميين والباحثين</a>.</p>
<p class="safety">لو إنت أو حد معاك في خطر حالًا، افتح <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>
</div></section>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "دوّر واكتشف",
          "url": SITE + "/explore/", "inLanguage": "ar"}
    html = page("explore", "دوّر واكتشف",
                "بحث موحّد في الحكايات والتمارين والقاموس النفسي، مع تصفية حسب نوع المحتوى ومن غير حفظ كلمات البحث.", body, ld)
    def asset(name):
        return "/assets/" + name + "?v=" + hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest()[:12]
    html = html.replace("</head>", f'<link rel="stylesheet" href="{asset("explore.css")}">\n</head>', 1)
    html = html.replace("</body>", f'<script src="{asset("explore.js")}" defer></script>\n</body>', 1)
    write("explore", html)
