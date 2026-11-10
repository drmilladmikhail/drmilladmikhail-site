#!/usr/bin/env python3
"""Interactive pages added 2026-11-07 (called by tools/build_pages.py):
  /exercise/  «تمرين الأسبوع النفسي»  — content/exercises.json, assets/extras.js (notes saved only on the visitor's device)
  /stories/   «حكايات التعافي»        — de-identified owner accounts, labelled fiction and consented reader submissions
  /shelf/     «رفّ الترشيحات»          — content/shelf.json
"""
import json
import hashlib
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WA = "https://wa.me/12012758490"


def _asset(name):
    with open(os.path.join(ROOT, "assets", name), "rb") as source:
        digest = hashlib.sha256(source.read()).hexdigest()[:12]
    return f"/assets/{name}?v={digest}"


def _extras_script():
    return f'<script src="{_asset("extras.js")}" defer></script>\n</body>'


def _load(name, default):
    p = os.path.join(ROOT, "content", name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return default


def exercise_page(ba, page, write, SITE, next_steps=None):
    import build_saved
    import build_next_steps
    esc = ba.esc
    data = _load("exercises.json", {"items": []})
    items = data["items"]
    arts = []
    for n, e in enumerate(items):
        steps = "".join(f"<li>{esc(s)}</li>" for s in e["steps"])
        fields = "".join(
            f'<label class="jr-field"><span>{esc(p)}</span><textarea rows="3" data-k="{k}"></textarea></label>'
            for k, p in enumerate(e["prompts"]))
        breathing = ('''<div class="breath" aria-live="off"><div class="breath-circle"><span class="breath-word">جاهز؟</span></div>
          <button type="button" class="btn primary breath-go">ابدأ التنفس معايا</button></div>''' if e.get("breathing") else "")
        rel = (f'<p class="related">جرّب كمان: <a href="{e["related"][0]}">{esc(e["related"][1])}</a></p>' if e.get("related") else "")
        share_txt = quote(f"«{e['quote']}»\nتمرين الأسبوع من د. ميلاد ميخائيل: {e['title']}\n{SITE}/exercise/#{e['slug']}", safe="")
        arts.append(f'''<article class="ex" id="{e["slug"]}" data-n="{n}"{"" if n == 0 else " hidden"}>
        <p class="ex-kicker"><span class="ex-when">تمرين الأسبوع</span> · {e["minutes"]} دقايق</p>
        <h2>{esc(e["title"])}</h2>
        {build_saved.button(esc, "exercise", e["slug"], e["title"])}
        <p class="ex-goal"><b>الهدف:</b> {esc(e["goal"])}</p>
        <ol class="ex-steps">{steps}</ol>
        {breathing}
        <form class="journal" data-slug="{e["slug"]}">
          <p class="jr-title">✍️ مساحتك الخاصة</p>
          <p class="jr-note">🔒 اللي بتكتبه بيتحفظ على جهازك انت بس، ومحدش يقدر يشوفه (ولا حتى أنا).</p>
          {fields}
          <div class="jr-actions"><span class="jr-saved" role="status"></span>
            <button type="button" class="btn jr-dl">نزّل اللي كتبته كملف</button>
            <button type="button" class="btn jr-clear">امسح</button></div>
        </form>
        <blockquote class="ex-quote"><p>«{esc(e["quote"])}»</p></blockquote>
        <div class="share-row ex-share"><a class="sh sh-wa" href="https://wa.me/?text={share_txt}" target="_blank" rel="noopener">شارك الاقتباس على واتساب</a>
          <a class="sh sh-fb" href="https://www.facebook.com/sharer/sharer.php?u={quote(SITE + '/exercise/', safe='')}" target="_blank" rel="noopener">فيسبوك</a>
          <a class="sh sh-x" href="https://x.com/intent/post?text={share_txt}" target="_blank" rel="noopener">X</a></div>
        {rel}
        {build_next_steps.render(esc, "exercise", e["slug"], (next_steps or {}).get("exercise", {}).get(e["slug"]))}
      </article>''')
    archive = "".join(f'<li><a href="#{e["slug"]}" data-n="{n}">{esc(e["title"])}</a></li>' for n, e in enumerate(items))
    body = f'''  <section class="section extras" data-start="{data.get("start", "2026-11-02")}" data-count="{len(items)}">
    <div class="wrap narrow">
      <p class="crumbs"><a href="/">الصفحة الرئيسية</a></p>
      <h1>تمرين الأسبوع النفسي</h1>
      {build_saved.notice()}
      <p class="section-intro">كل أسبوع تمرين عملي قصير من العلاج النفسي: تدوين المشاعر، الحدود الصحية، التنفس الواعي، والبحث عن المعنى. اقرا الخطوات، جرّبها، واكتب تأملاتك لنفسك.</p>
      <p class="safety exercise-readonly">كل التمارين متاحة هنا للقراءة. لو تفاعل الصفحة مش شغّال، مساحة كتابة الملاحظات وتشغيل التنفس التفاعلي مش متاحين؛ تقدر تتبع الخطوات المكتوبة عادي.</p>
      {"".join(arts)}
      <p class="related">عايز أدوات قصيرة تانية؟ شوف <a href="/life-tools/">أدوات لحياتك</a>.</p>
      <details class="ex-archive"><summary>كل التمارين (تقدر ترجع لأي تمرين)</summary><ol>{archive}</ol></details>
      <p class="safety">التمارين دي للعناية بالنفس، ومش بديل عن العلاج. لو حاسس إنك في خطر دلوقتي، روح لصفحة <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "تمرين الأسبوع النفسي", "url": f"{SITE}/exercise/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    html = page("exercise", "تمرين الأسبوع النفسي", "تمرين نفسي عملي جديد كل أسبوع: تدوين المشاعر، الحدود الصحية، التنفس الواعي ورسالة حنية لنفسك، مع مساحة تكتب فيها لنفسك.", body, ld)
    html = html.replace("</head>", f'<link rel="stylesheet" href="{_asset("exercise-fallback.css")}">\n</head>', 1)
    if next_steps is not None:
        html = build_next_steps.attach(html)
    write("exercise", build_saved.attach(html.replace("</body>", _extras_script(), 1)))


def story_reflections():
    """Load optional, separately labelled educational prompts, never case events."""
    records = {}
    for item in _load("story-reflections.json", {"items": []}).get("items", []):
        sid = item.get("story_id", "")
        options = item.get("options", [])
        if (not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid)
                or sid in records or not isinstance(item.get("question"), str)
                or not item["question"].strip() or not isinstance(options, list)
                or len(options) != 3
                or any(not isinstance(option, dict)
                       or any(not isinstance(option.get(key), str) or not option[key].strip()
                              for key in ("label", "text"))
                       for option in options)):
            raise ValueError("Invalid or duplicate story reflection: " + repr(sid))
        records[sid] = item
    return records


def story_reflection_html(esc, item):
    """Native disclosures: no scripts, submissions, storage, scores or diagnosis."""
    sid = esc(item["story_id"])
    choices = "".join(
        f'''<details class="reflection-option" name="reflection-{sid}">
          <summary><span class="reflection-number" aria-hidden="true">{number}</span>
            <span>{esc(option["label"])}</span><span class="reflection-toggle" aria-hidden="true"></span></summary>
          <div class="reflection-explanation"><p>{esc(option["text"])}</p></div>
        </details>'''
        for number, option in zip(("١", "٢", "٣"), item["options"])
    )
    return f'''<section class="story-reflection" aria-labelledby="reflect-{sid}">
        <p class="reflection-kicker">وقفة مع الحكاية</p>
        <h3 id="reflect-{sid}">لو كنت مكانه، كنت هتعمل إيه؟</h3>
        <p class="reflection-note">موقف افتراضي للتفكير، مش تكملة لأحداث الحكاية. مفيش درجات أو تشخيص؛ افتح أي اختيار وشوف زاوية للفهم.</p>
        <p class="reflection-question">{esc(item["question"])}</p>
        <div class="reflection-choices">{choices}</div>
      </section>'''


def eligible_stories():
    stories = []
    for story in _load("stories.json", {"stories": []}).get("stories", []):
        if story.get("kind") == "illustrative_fiction":
            stories.append(story)
        elif (story.get("kind") == "clinician_provided_account"
              and story.get("owner_approved") is True and story.get("deidentified") is True
              and story.get("patient_publication_consent") is True):
            stories.append(story)
        elif story.get("kind", "reader_submission") == "reader_submission" and story.get("consent") is True:
            stories.append(story)
    return stories


def stories_page(ba, page, write, SITE, next_steps=None):
    import build_saved
    import build_next_steps
    esc = ba.esc
    reflections = story_reflections()
    stories = eligible_stories()
    if stories:
        parts = []
        for n, s in enumerate(stories, 1):
            fictional = s.get("kind") == "illustrative_fiction"
            clinical = s.get("kind") == "clinician_provided_account"
            paragraphs = "".join(f"<p>{esc(p)}</p>" for p in s["text"])
            reflection = (story_reflection_html(esc, reflections[s["id"]])
                          if s.get("id") in reflections else "")
            onward = build_next_steps.render(esc, "story", s.get("id"),
                        (next_steps or {}).get("story", {}).get(s.get("id")))
            attribution = (
                '<p class="story-by">حكاية توضيحية متخيّلة، مش حالة حقيقية من العيادة.</p>'
                if fictional else
                '<p class="story-by">من داخل العيادة · صياغة تحريرية على لسان صاحب الحكاية، وليست اقتباسًا حرفيًا.</p>'
                if clinical else
                f'<p class="story-by">{esc(s.get("alias", "صاحب/ة الحكاية"))}، '
                'نُشرت بإذنه/ا وبعد إخفاء أي تفاصيل تكشف هويته/ا</p>'
            )
            parts.append(f'''<article class="story story-card" id="story-{n}">
        <details class="story-details"><summary>
          <span class="story-tag">{esc(s.get("tag", ""))}</span>
          <h2>{esc(s["title"])}</h2>
          <span class="story-read"><span class="story-open-label">اقرا الحكاية وجرّب الموقف</span><span class="story-close-label">اقفل الحكاية</span><span class="story-chevron" aria-hidden="true">⌄</span></span>
        </summary><div class="story-text">{paragraphs}</div>{reflection}{onward}</details>
        {attribution}{build_saved.button(esc, "story", s.get("id"), s["title"])}</article>''')
        cards = '<div class="stories-grid">' + "".join(parts) + "</div>"
    else:
        cards = '''<div class="story-empty"><p class="story-tag">قريبًا</p><h2>الحكايات بتتجهز</h2>
        <p>أي حكاية متخيّلة هنا هتكون مكتوب عليها إنها للتوضيح. ومش هننشر تجربة حقيقية يبعتها قارئ من غير موافقته.</p>
        <p>تقدر تبعت تجربتك من النموذج تحت، من غير تفاصيل تكشف هويتك.</p></div>'''
    cats = ["القلق والتوتر", "التعلّق والعلاقات", "التعافي من علاقة مؤذية", "تقدير الذات وجلد الذات", "الفراغ والبحث عن المعنى", "حاجة تانية"]
    opts = "".join(f"<option>{c}</option>" for c in cats)
    body = f'''  <section class="section extras stories-page">
    <div class="wrap stories-wrap">
      <p class="crumbs"><a href="/">الصفحة الرئيسية</a></p>
      <h1>حكايات من داخل العيادة</h1>
      <p class="section-intro">ورا كل حكاية فيه وجع ومحاولة للفهم والتغيير. افتح الكارت واقرا عن رحلة مختلفة، وبعدها جرّب تختار رد فعل في موقف افتراضي، من غير مقارنة بين تجربة والتانية.</p>
      <aside class="stories-note" aria-label="عن طبيعة الحكايات"><h2>من غير أسماء أو تفاصيل تعريفية</h2>
        <p>الحكايات دي من واقع عيادتي، وبنشرها بموافقة أصحابها، من غير أسماء أو تفاصيل تكشف هويتهم. كل حكاية مكتوبة على لسان صاحبها، مع إعادة الصياغة لحماية الخصوصية؛ مش نقل حرفي لكلامه.</p>
        <p>كل حكاية بتعرض تجربة فردية، مش تشخيص ولا خطة علاج ولا وعد بنفس النتيجة لكل الناس. وماينفعش تبدأ أو توقف دواء أو تغيّر جرعته اعتمادًا على حكاية هنا.</p></aside>
      <p class="reflection-privacy">التفاعل اختياري. اختياراتك بتفتح شرحها هنا بس، ومش بتتبعت أو بتتحفظ.</p>
      {cards}
      <p class="safety">التجارب دي للتوعية والمساندة، مش لتشخيص نفسك أو تغيير علاجك. لو انت في خطر دلوقتي، افتح <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>
      <section class="story-send" aria-labelledby="send-h">
        <h2 id="send-h">احكي حكايتك (من غير اسمك)</h2>
        <ul class="story-promise"><li>اكتب باسم مستعار، ومتكتبش أسماء ناس أو أماكن أو أي حاجة تكشفك.</li><li>هقرا الحكاية بنفسي، وممكن أعدّل صياغتها بسيط وأشيل أي تفاصيل حساسة قبل النشر.</li><li>مش هنشر أي حكاية من غير موافقتك الواضحة، وتقدر تطلب حذفها في أي وقت.</li></ul>
        <form class="story-form">
          <label>اسم مستعار<input type="text" name="alias" maxlength="40" placeholder="مثلاً: «نور»" autocomplete="off"></label>
          <label>الحكاية عن إيه؟<select name="cat">{opts}</select></label>
          <label>كنت فين؟ وإيه اللي كان صعب؟<textarea name="before" rows="4" required></textarea></label>
          <label>إيه اللي ساعدك تتحسن؟<textarea name="helped" rows="4" required></textarea></label>
          <label>تحب تقول إيه لحد لسه في أول الطريق؟<textarea name="msg" rows="3"></textarea></label>
          <label class="chk"><input type="checkbox" name="ok" required> موافق إن الحكاية تتنشر على الموقع من غير اسمي، بعد إخفاء أي تفاصيل تكشفني.</label>
          <p class="form-err" hidden>اكتب الحكاية ووافق على النشر الأول.</p>
          <button type="submit" class="btn primary">ابعت الحكاية على واتساب</button>
          <p class="fine">الزرار بيفتح واتساب برسالة جاهزة ليا. واتساب بيوريني رقمك أنا بس، والرقم مش بيتنشر ولا بيتشارك مع حد. لو انت في خطر دلوقتي، متكتبش هنا: روح <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>
        </form>
      </section>
      {ba.discussion_block("stories", SITE + "/stories/", "حكايات التعافي", "كلمة دعم لكل حد لسه في أول الطريق: إيه اللي كنت تتمنى حد يقولهولك؟", "مساحة الدعم")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "حكايات من داخل العيادة", "url": f"{SITE}/stories/", "inLanguage": "ar",
          "author": {"@id": f"{SITE}/#person"}}
    html = page("stories", "حكايات من داخل العيادة", "١٠ حكايات من واقع عيادتي، بنشرها بموافقة أصحابها على لسانهم، من غير أسماء أو تفاصيل تعريفية، مع الحفاظ على خصوصيتهم.", body, ld)
    html = html.replace("</head>", '<link rel="stylesheet" href="/assets/stories.css?v=20261110-4">\n</head>', 1)
    html = html.replace('<div class="stories-grid">', build_saved.notice() + '<div class="stories-grid">', 1)
    if next_steps is not None:
        html = build_next_steps.attach(html)
    write("stories", build_saved.attach(html.replace("</body>", _extras_script(), 1)))


def shelf_page(ba, page, write, SITE):
    esc = ba.esc
    d = _load("shelf.json", {"books": [], "mine": [], "tools": []})
    topics = sorted({b["topic"] for b in d["books"]})
    chips = '<button type="button" class="chip on" data-t="">الكل</button>' + "".join(f'<button type="button" class="chip" data-t="{esc(t)}">{esc(t)}</button>' for t in topics)
    stars = lambda bid: "".join(f'<button type="button" class="star" data-v="{v}" aria-label="{v} من 5">★</button>' for v in range(1, 6))
    books = "".join(f'''<li class="bk" data-t="{esc(b["topic"])}" data-id="{esc(b["id"])}">
        <div class="bk-spine" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 7c4-2 8-2 12 1 4-3 8-3 12-1v18c-4-2-8-2-12 1-4-3-8-3-12-1Z"/><path d="M16 8v18"/></svg></div>
        <div class="bk-body"><p class="bk-topic">{esc(b["topic"])}</p><h3>{esc(b["title"])}</h3>
        <p class="bk-by">{esc(b["author"])} · {b["year"]} · <span lang="en" dir="ltr">{esc(b["orig"])}</span></p>
        <p><b>رأيي فيه:</b> {esc(b["why"])}</p><p class="bk-for"><b>مناسب لـ:</b> {esc(b["for"])}</p>
        <div class="rate" role="group" aria-label="قيّم الكتاب ده">قرأته؟ قيّمه: {stars(b["id"])}<span class="rate-msg"></span></div></div></li>''' for b in d["books"])
    mine = "".join(f'<li><a href="{x["url"]}"><b>{esc(x["title"])}</b><span>{esc(x["note"])}</span></a></li>' for x in d["mine"])
    ext = ' target="_blank" rel="noopener"'
    tools = "".join(f'<li><a href="{x["url"]}"{ext if x["url"].startswith("http") else ""}><b>{esc(x["title"])}</b><span>{esc(x["note"])}</span></a></li>' for x in d["tools"])
    body = f'''  <section class="section extras">
    <div class="wrap">
      <p class="crumbs"><a href="/">الصفحة الرئيسية</a></p>
      <h1>رفّ الترشيحات</h1>
      <p class="section-intro">كتب نفسية قرأتها وبرشّحها، مع رأيي فيها ولمين تنفع، وأدوات ومحتوى مسموع يساعدك. قرأت كتاب منهم؟ قيّمه، واقترح علينا كتاب فرق معاك.</p>
      <h2 class="shelf-h">📚 كتب برشّحها</h2>
      <div class="chips" role="group" aria-label="فلترة حسب الموضوع">{chips}</div>
      <ul class="shelf">{books}</ul>
      <p class="fine">تقييمك بيتحفظ على جهازك بس. التقييمات العامة والمراجعات هتظهر في التعليقات تحت لما تفتح.</p>
      <div class="two shelf-more"><div><h2>من كتبي</h2><ul class="res-list">{mine}</ul></div>
      <div><h2>أدوات ومحتوى مسموع</h2><ul class="res-list">{tools}</ul></div></div>
      <section class="story-send suggest" aria-labelledby="sug-h">
        <h2 id="sug-h">اقترح كتاب أو أداة فرقت معاك</h2>
        <form class="suggest-form">
          <label>اسم الكتاب أو الأداة<input type="text" name="title" maxlength="120" required></label>
          <label>الكاتب (لو كتاب)<input type="text" name="author" maxlength="80"></label>
          <label>تقييمك من 5<select name="rate"><option>5</option><option>4</option><option>3</option><option>2</option><option>1</option></select></label>
          <label>فرق معاك في إيه؟<textarea name="why" rows="3"></textarea></label>
          <p class="form-err" hidden>اكتب اسم الكتاب أو الأداة الأول.</p>
          <button type="submit" class="btn primary">ابعت الاقتراح على واتساب</button>
        </form>
      </section>
      {ba.discussion_block("shelf", SITE + "/shelf/", "رفّ الترشيحات", "قريت كتاب منهم؟ اكتب تقييمك ومراجعة قصيرة، أو رشّح كتاب للناس.", "مراجعات القرّاء")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "رفّ الترشيحات: كتب نفسية وأدوات", "url": f"{SITE}/shelf/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "hasPart": [{"@type": "Book", "name": b["orig"], "author": b["author"], "datePublished": str(b["year"])} for b in d["books"]]}
    html = page("shelf", "رفّ الترشيحات: كتب نفسية وأدوات", "أفضل كتب علم النفس اللي برشّحها مع رأيي فيها ولمين تنفع: المعنى، التعلّق، التعاطف مع الذات، العادات. وأدوات مجانية ومحتوى مسموع.", body, ld)
    write("shelf", html.replace("</body>", _extras_script(), 1))


def build_all(ba, page, write, SITE):
    import build_explore
    build_explore.build(ba, page, write, SITE)
    import build_saved
    import build_next_steps
    next_steps = build_next_steps.load()
    build_saved.write_catalog()
    build_saved.build(ba, page, write, SITE)
    exercise_page(ba, page, write, SITE, next_steps)
    stories_page(ba, page, write, SITE, next_steps)
    import build_your_path
    build_your_path.build(ba, page, write, SITE)
    shelf_page(ba, page, write, SITE)
    import build_life_tools
    build_life_tools.build(ba, page, write, SITE)
    import build_discover_feelings
    build_discover_feelings.build(ba, page, write, SITE)
