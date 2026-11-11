#!/usr/bin/env python3
"""Curated, non-diagnostic journeys through existing public site resources."""
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SLUG = "your-path"
KINDS = ("story", "concept", "exercise")
LABELS = {"story": "حكاية من العيادة", "concept": "معنى من القاموس", "exercise": "تمرين اختياري"}
ACTIONS = {"story": "افتح الحكاية", "concept": "افتح المعنى", "exercise": "افتح التمرين"}


def load(root=ROOT):
    import build_glossary
    root = Path(root)
    topics = json.loads((root / "content/your-path.json").read_text(encoding="utf-8"))["topics"]
    stories = json.loads((root / "content/stories.json").read_text(encoding="utf-8"))["stories"]
    # Match the consent-gated order in build_extras.stories_page.
    approved = [
        s for s in stories
        if s.get("kind") == "illustrative_fiction"
        or (s.get("kind") == "clinician_provided_account"
            and all(s.get(key) is True for key in
                    ("owner_approved", "deidentified", "patient_publication_consent")))
        or (s.get("kind", "reader_submission") == "reader_submission" and s.get("consent") is True)
    ]
    story_map = {s["id"]: (n, s) for n, s in enumerate(approved, 1) if s.get("id")}
    terms = {t["slug"]: t for t in build_glossary.load(root)["items"]}
    exercises = {e["slug"]: e for e in json.loads(
        (root / "content/exercises.json").read_text(encoding="utf-8"))["items"]}
    seen = set()
    for topic in topics:
        tid = topic.get("id", "")
        if (not isinstance(tid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", tid)
                or tid in seen or any(not isinstance(topic.get(key), str) or not topic[key].strip()
                                     for key in ("label", "blurb", "intro", *KINDS))):
            raise ValueError("Invalid or duplicate path topic: " + repr(tid))
        seen.add(tid)
        try:
            number, story = story_map[topic["story"]]
            term = terms[topic["concept"]]
            exercise = exercises[topic["exercise"]]
        except KeyError as error:
            raise ValueError("Missing approved path resource: " + repr(error)) from error
        topic["resources"] = [
            {"kind": "story", "title": story["title"], "href": f"/stories/#story-{number}"},
            {"kind": "concept", "title": term["title"], "href": f'/glossary/{term["slug"]}/'},
            {"kind": "exercise", "title": exercise["title"], "href": f'/exercise/#{exercise["slug"]}'},
        ]
    if not topics:
        raise ValueError("At least one path topic is required")
    return topics


def home_section():
    esc = html.escape
    cards = "".join(
        f'<a class="concern-card" href="/your-path/#{esc(t["id"])}">'
        f'<b>{esc(t["label"])}</b><small>{esc(t["blurb"])}</small>'
        '<i>ابدأ مسارك من هنا ←</i></a>' for t in load()
    )
    return f'''<section class="section concern-finder" aria-labelledby="concern-title">
    <div class="wrap"><div class="concern-heading">
      <p class="quiz-kicker">خلّينا نبدأ من اللي يهمك</p>
      <h2 id="concern-title">إيه اللي شاغل بالك النهارده؟</h2>
      <p>اختار موضوعًا، وهتلاقي مسارًا من حكاية ومعنى وتمرين. تقدر تبدأ بأي محطة أو تكتفي بخطوة واحدة.</p>
    </div><div class="concern-grid">{cards}</div>
    <p class="concern-note">اقتراحات توعوية حسب اختيارك، مش تقييمًا لشخصيتك أو تشخيصًا. من غير حساب أو حفظ لاختيارات المسار.</p>
    </div></section>'''


def body_html(topics):
    esc = html.escape
    choices = "".join(
        f'<a class="yp-topic" data-topic="{esc(t["id"])}" href="#{esc(t["id"])}">'
        f'<b>{esc(t["label"])}</b><span>{esc(t["blurb"])}</span></a>' for t in topics)
    routes = []
    for topic in topics:
        cards = []
        for resource in topic["resources"]:
            kind = resource["kind"]
            cards.append(f'''<li class="yp-step" data-kind="{kind}">
              <p class="yp-kind">{LABELS[kind]}</p><h3>{esc(resource["title"])}</h3>
              <a class="yp-open" href="{esc(resource["href"])}" target="_blank" rel="noopener">{ACTIONS[kind]} <span aria-hidden="true">↗</span><span class="sr-only">: {esc(resource["title"])}، في تبويب جديد</span></a>
              <button class="yp-complete" type="button" aria-pressed="false" data-complete hidden>خلصت الخطوة<span class="sr-only">: {esc(resource["title"])}</span></button>
            </li>''')
        tid = esc(topic["id"])
        routes.append(f'''<section class="yp-route" id="{tid}" aria-labelledby="yp-title-{tid}">
          <p class="yp-kicker">مسار للقراءة والتجربة</p>
          <h2 id="yp-title-{tid}" tabindex="-1">{esc(topic["label"])}</h2>
          <p>{esc(topic["intro"])}</p><ol class="yp-steps">{"".join(cards)}</ol>
          <a class="yp-back" href="#yp-topics">اختار موضوعًا تاني</a>
        </section>''')
    return f'''<section class="section your-path"><div class="wrap yp-wrap">
      <p class="crumbs"><a href="/">الصفحة الرئيسية</a></p>
      <p class="yp-kicker">خطوة على قدّك، من غير استعجال</p>
      <h1>مسارك النهارده</h1>
      <p class="yp-intro">حكاية تفهم منها تجربة، ومعنى يوضّح فكرة، وتمرين تختاره لو مناسب ليك. مش لازم تعمل كل حاجة، ومش مطلوب منك تثبت إنك اتحسّنت.</p>
      <aside class="yp-privacy"><p>دي اقتراحات حسب الموضوع اللي تختاره، مش تشخيصًا أو خطة علاج. من غير حساب أو إجابات مكتوبة؛ اختيارات المسار وعلامات إكماله مش بتتبعت أو بتتحفظ.</p>
      <p>الحكايات تجارب فردية، مش تفسيرًا أكيدًا للي بتمر بيه. لو في خطر فوري، افتح <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p></aside>
      <section id="yp-topics" aria-labelledby="yp-topic-title">
        <h2 id="yp-topic-title" tabindex="-1">إيه الأقرب للي شاغل بالك؟</h2>
        <div class="yp-topics">{choices}</div>
      </section>
      <section class="yp-preferences" id="yp-preferences" aria-labelledby="yp-preference-title" hidden>
        <h2 id="yp-preference-title" tabindex="-1">تحب تبدأ بإيه؟</h2>
        <p>غيّر ترتيب المحطات على راحتك؛ مفيش ترتيب إجباري.</p>
        <div class="yp-starts" role="group" aria-label="المحطة اللي تحب تبدأ بيها">
          <button type="button" data-start="story" aria-pressed="true">أقرا حكاية</button>
          <button type="button" data-start="concept" aria-pressed="false">أفهم معنى</button>
          <button type="button" data-start="exercise" aria-pressed="false">أجرّب تمرين</button>
        </div>
      </section>
      <div class="yp-toolbar"><p id="yp-status" role="status" aria-live="polite"></p>
        <button type="button" id="yp-restart" hidden>ابدأ من جديد</button></div>
      <p class="yp-reading-note">روابط المحطات بتفتح في تبويب جديد علشان تقدر ترجع للمسار هنا. أي ملاحظات تكتبها داخل صفحة التمرين ليها إعدادات الحفظ الموضّحة هناك.</p>
      <p id="yp-progress" class="yp-progress" hidden>خلصت ٠ من ٣ خطوات</p>
      <p class="yp-session-note" id="yp-session-note" hidden>علّم لنفسك على الخطوة اللي خلصتها. العلامات مؤقتة وبتتمسح عند إعادة تحميل الصفحة؛ مش سجلًا للتعافي ولا تقييمًا ليك.</p>
      <noscript><p class="yp-privacy">المسارات كلها ظاهرة تحت. اختار موضوعًا وروابطه؛ تغيير الترتيب وعلامات الإكمال محتاجين JavaScript.</p></noscript>
      <div class="yp-routes">{"".join(routes)}</div>
      <div class="yp-finish" id="yp-finish" hidden><h2>خد نفس… وكفاية لحد هنا لو حابب</h2>
        <p>علّمت المحطات الثلاثة. ده مش مقياس للتحسّن، ومش لازم تعمل خطوة زيادة. تقدر تختار موضوعًا تاني أو ترجع وقت ما تحب.</p></div>
      <p class="yp-other">مش لاقي وصف قريب؟ تقدر تستخدم <a href="/discover-feelings/">اكتشاف مشاعرك</a> أو تتصفّح <a href="/tests/">الاختبارات التوعوية</a>.</p>
    </div></section>'''


def build(ba, page, write, SITE):
    title = "مسارك النهارده"
    desc = "اختار موضوعًا وابدأ من حكاية أو معنى نفسي أو تمرين، من غير حساب أو حفظ لاختياراتك. مسارات توعوية وليست تشخيصًا."
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title,
          "url": f"{SITE}/{SLUG}/", "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    result = page(SLUG, title, desc, body_html(load()), ld)
    result = result.replace("</head>", '<link rel="stylesheet" href="/assets/your-path.css?v=20261110-1">\n</head>', 1)
    result = result.replace("</body>", '<script src="/assets/your-path.js?v=20261110-1" defer></script>\n</body>', 1)
    write(SLUG, result)
