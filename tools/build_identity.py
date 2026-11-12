#!/usr/bin/env python3
"""Identity pages (2026-11-11, his SEO brief «مشروع تطوير الظهور الرقمي»):

  /about/                 عن د. ميلاد ميخائيل + السيرة المهنية   (ProfilePage → Person)
  /about/qualifications/  المؤهلات العلمية                       (WebPage, hasCredential)
  /about/publications/    الرسائل العلمية والأبحاث               (WebPage, Thesis)
  /family/                التوعية الأسرية والزوجية               (CollectionPage)
  /en/about/              About Dr. Millad Mikhail (English)     (ProfilePage)

RULE: only verified facts (the same ones already on the homepage / WES badge).
No invented credentials, licences, reviews or numbers. English pages: "Mental
Health Educator and Author"; no sessions on English pages.
Called from tools/build_pages.py main().
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://drmilladmikhail.com"
PERSON_ID = f"{SITE}/#person"
UPDATED = "2026-11-11"
NAME_AR = "د. ميلاد ميخائيل"
NAME_EN = "Dr. Millad Mikhail, PhD"
TITLE_AR = "استشاري العلاج النفسي والأسري"
ORCID = "https://orcid.org/0009-0002-9254-367X"
WES = "https://www.credly.com/badges/5a6796c0-5e1a-4ad5-b1af-fb64254e81cf/public_url"
YOUTUBE = "https://www.youtube.com/@DrMilladMikhail"
LINKEDIN = "https://www.linkedin.com/in/dr-millad-mikhail-a57b0b215"
BLOG = "https://blog.drmilladmikhail.com/"
BOOK_AR = "https://www.amazon.com/dp/B0HPNCYWWS"
BOOK_EN = "https://www.amazon.com/dp/B0HPRPSPWF"

SCU = {"@type": "CollegeOrUniversity", "name": "Suez Canal University", "alternateName": "جامعة قناة السويس"}
TANTA = {"@type": "CollegeOrUniversity", "name": "Tanta University", "alternateName": "جامعة طنطا"}

# Verified qualifications (same data as the homepage «المؤهلات العلمية»).
QUALS = [
    ("2022", "دكتوراه في الصحة النفسية", "Ph.D. in Education (Mental Health)", "قسم الصحة النفسية، كلية التربية بالإسماعيلية، جامعة قناة السويس", "تقدير امتياز", "WES: Earned doctorate", SCU, "doctoral degree"),
    ("2021", "الدبلوم المتخصص في الإرشاد وعلم النفس الإكلينيكي", "Postgraduate Diploma in Counseling and Clinical Psychology", "كلية الآداب، جامعة طنطا", "تقدير امتياز (90.8%)", "WES: One year of graduate study", TANTA, "postgraduate diploma"),
    ("2018", "ماجستير التربية، تخصص الصحة النفسية", "Master of Education (Mental Health)", "كلية التربية بالإسماعيلية، جامعة قناة السويس", "تقدير امتياز", "WES: Master's degree", SCU, "master's degree"),
    ("2014", "الدبلوم الخاص في التربية", "Special Diploma in Education", "جامعة قناة السويس", "تقدير جيد جداً", "WES: Graduate certificate", SCU, "graduate certificate"),
    ("2013", "الدبلوم العام في التربية", "General Diploma in Education", "جامعة قناة السويس", "تقدير جيد جداً", "WES: One year of graduate study", SCU, "postgraduate diploma"),
]
THESES = [
    {"year": "2022", "kind": "رسالة الدكتوراه",
     "ar": "فعالية الإرشاد بالمعنى في خفض مستوى القلق الوجودي وتحسين مستوى المناعة النفسية لدى طلاب الجامعة",
     "en": "Effectiveness of Logo Counselling on Reducing the Level of Existential Anxiety and Improving Psychological Immunity for University Students",
     "facts": [("الجهة", "قسم الصحة النفسية، كلية التربية بالإسماعيلية، جامعة قناة السويس"), ("المناقشة", "12 سبتمبر 2022"), ("إقرار مجلس الجامعة", "30 نوفمبر 2022")],
     "degree": "Ph.D."},
    {"year": "2018", "kind": "رسالة الماجستير",
     "ar": "فاعلية برنامج إثرائي قائم على البرمجة اللغوية العصبية لتنمية الطلاقة اللفظية لدى الطلاب المعلمين",
     "en": "The Effectiveness of an Enriching Program Based on Neuro-Linguistic Programming to Develop Verbal Fluency for Teacher-Students",
     "facts": [("الجهة", "قسم الصحة النفسية، كلية التربية بالإسماعيلية، جامعة قناة السويس"), ("إقرار مجلس الجامعة", "17 يوليو 2018")],
     "degree": "Master's"},
]
CONFERENCES = [
    ("فعالية الإرشاد بالمعنى في خفض القلق في ظل جائحة كورونا وتحسين مستوى المناعة النفسية لدى طلاب الجامعة", "المؤتمر الثامن لشباب الباحثين، جامعة قناة السويس"),
    ("فاعلية برنامج تدريبي في تنمية الطلاقة اللفظية لدى الطالب المعلم", "المؤتمر الرابع لشباب الباحثين، جامعة قناة السويس"),
]
FAMILY_SLUGS = ["couples-counseling", "emotional-communication-couples", "family-interference-marriage",
                "dealing-with-angry-partner", "dealing-with-lying-partner", "dealing-with-jealous-partner",
                "dealing-with-stingy-partner", "dealing-with-narcissistic-partner", "emotionally-abusive-partner",
                "partner-with-depression", "partner-with-anxiety-ocd", "partner-with-addiction",
                "why-we-choose-the-same-person", "four-attachment-styles", "anxious-avoidant-attraction"]


def esc(s):
    return html.escape(str(s), quote=True)


def crumbs(items):
    """Visible breadcrumb + BreadcrumbList data (items: [(name, path-or-None)])."""
    parts = []
    for name, path in items:
        parts.append(f'<a href="{path}">{esc(name)}</a>' if path else f'<span aria-current="page">{esc(name)}</span>')
    nav = '<nav class="crumbs" aria-label="مسار التصفح">' + ' <span aria-hidden="true">›</span> '.join(parts) + '</nav>'
    ld = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": SITE + p} if p else {})}
        for i, (n, p) in enumerate(items)]}
    return nav, ld


def person_core(extra=None):
    d = {"@type": "Person", "@id": PERSON_ID, "name": "Dr. Millad Mikhail",
         "alternateName": ["د. ميلاد ميخائيل", "Millad Mikhail", "ميلاد منير ميخائيل", "د. ميلاد منير"],
         "url": f"{SITE}/", "image": f"{SITE}/assets/millad.jpg",
         "sameAs": [YOUTUBE, LINKEDIN, ORCID, BLOG, WES]}
    d.update(extra or {})
    return d


def page_ld(kind, url, name, desc, crumbs_ld, extra=None, lang="ar"):
    node = {"@type": kind, "@id": url + "#page", "url": url, "name": name, "description": desc, "inLanguage": lang,
            "isPartOf": {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/"},
            "dateModified": UPDATED, "breadcrumb": crumbs_ld}
    node.update(extra or {})
    return {"@context": "https://schema.org", "@graph": [node]}


def about_page(ba, page, write):
    url = f"{SITE}/about/"
    nav, cld = crumbs([("الرئيسية", "/"), ("عن د. ميلاد ميخائيل", None)])
    desc = ("د. ميلاد ميخائيل (Dr. Millad Mikhail)، استشاري العلاج النفسي والأسري، حاصل على الدكتوراه في الصحة النفسية "
            "من جامعة قناة السويس، عضو الجمعية الأمريكية لعلم النفس (APA)، ومؤلف كتاب «ليه بنحب اللي بيوجعنا؟».")
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      {nav}
      <p class="kicker-g">{TITLE_AR}</p>
      <h1>عن د. ميلاد ميخائيل</h1>
      <p class="lead">بساعد الناس يفهموا نفسهم وعلاقاتهم، ويبدأوا خطوات عملية لحياة أهدى، بالعربي البسيط ومن مراجع علمية.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow id-page">
      <div class="id-card">
        <picture><source srcset="/assets/millad-cut.webp" type="image/webp"><img src="/assets/millad.jpg" width="160" height="160" alt="د. ميلاد ميخائيل" loading="eager"></picture>
        <div>
          <p class="id-name">{NAME_AR} <span lang="en" dir="ltr">· {NAME_EN}</span></p>
          <p>{TITLE_AR}. يُعرف أيضاً باسم «د. ميلاد منير».</p>
          <ul class="id-facts">
            <li>دكتوراه في الصحة النفسية، جامعة قناة السويس (2022)</li>
            <li>عضو الجمعية الأمريكية لعلم النفس (APA)</li>
            <li>مؤهلات مقيّمة أمريكيًا من WES</li>
            <li>مؤلف كتاب «ليه بنحب اللي بيوجعنا؟»</li>
          </ul>
        </div>
      </div>

      <h2>السيرة المهنية</h2>
      <p>د. ميلاد ميخائيل حاصل على الدكتوراه في الصحة النفسية من قسم الصحة النفسية بكلية التربية بالإسماعيلية، جامعة قناة السويس، سنة 2022. رسالته كانت عن «فعالية الإرشاد بالمعنى في خفض مستوى القلق الوجودي وتحسين مستوى المناعة النفسية لدى طلاب الجامعة»، وده اللي خلّى المعنى والمناعة النفسية من أهم المواضيع اللي بيشتغل عليها.</p>
      <p>قبل الدكتوراه حصل على ماجستير التربية تخصص الصحة النفسية من جامعة قناة السويس (2018)، والدبلوم المتخصص في الإرشاد وعلم النفس الإكلينيكي من جامعة طنطا (2021). ومؤهلاته مقيّمة ومعادلة أمريكيًا من <span lang="en" dir="ltr">World Education Services (WES)</span>. وبيدرس حاليًا مقررات دراسات عليا في علم النفس كطالب زائر في <span lang="en" dir="ltr">JFK School of Psychology</span> بجامعة <span lang="en" dir="ltr">National University</span> في أمريكا.</p>
      <p>بيقدّم جلسات نفسية أونلاين بالعربي لأهلنا في مصر والوطن العربي، وبيكتب محتوى توعوي مجاني عن التعلّق والعلاقات والقلق والمعنى: مقالات واختبارات وتمارين على الموقع ده، وفيديوهات على قناة «جلسة شيزلونج».</p>

      <h2>مجالات الاهتمام</h2>
      <ul class="id-list">
        <li>العلاقات وأنماط التعلّق، وليه بنكرر نفس الاختيارات</li>
        <li>التوعية الأسرية والزوجية والتواصل بين الشريكين</li>
        <li>القلق والضغوط والمناعة النفسية</li>
        <li>البحث عن المعنى والإرشاد بالمعنى (Logotherapy)</li>
      </ul>

      <h2>اعرف أكتر</h2>
      <ul class="link-grid">
        <li><a href="/about/qualifications/"><b>المؤهلات العلمية</b><span>الدرجات العلمية والتقييم الأمريكي (WES).</span></a></li>
        <li><a href="/about/publications/"><b>الرسائل العلمية والأبحاث</b><span>رسالة الدكتوراه والماجستير وأبحاث المؤتمرات.</span></a></li>
        <li><a href="/book/"><b>الكتب</b><span>«ليه بنحب اللي بيوجعنا؟» و«بطاريتي 1%» (قريبًا).</span></a></li>
        <li><a href="/articles/"><b>المقالات</b><span>مقالات مبسّطة بمراجع علمية.</span></a></li>
        <li><a href="/family/"><b>التوعية الأسرية والزوجية</b><span>كل محتوى العلاقات والزواج في مكان واحد.</span></a></li>
        <li><a href="/contact/"><b>تواصل</b><span>للجلسات أو التعاون أو الأسئلة.</span></a></li>
      </ul>

      <h2>تابعني</h2>
      <ul class="id-links">
        <li><a href="{YOUTUBE}" rel="me noopener" target="_blank">قناة «جلسة شيزلونج» على يوتيوب</a></li>
        <li><a href="{LINKEDIN}" rel="me noopener" target="_blank">LinkedIn</a></li>
        <li><a href="{ORCID}" rel="me noopener" target="_blank">ORCID (الهوية البحثية)</a></li>
        <li><a href="{BLOG}" rel="me noopener" target="_blank">مدونة «راحة البال»</a></li>
        <li><a href="/en/about/" hreflang="en" lang="en">About Dr. Millad Mikhail (English)</a></li>
      </ul>
      <p class="id-updated">آخر تحديث للصفحة: <time datetime="{UPDATED}">11 نوفمبر 2026</time></p>
    </div>
  </section>'''
    ld = page_ld("ProfilePage", url, "عن د. ميلاد ميخائيل", desc, cld, {
        "mainEntity": person_core({"description": desc, "knowsLanguage": ["ar", "en"],
                                   "alumniOf": [SCU, TANTA],
                                   "memberOf": {"@type": "Organization", "name": "American Psychological Association", "alternateName": "APA"}})})
    html_ = page("about", "نبذة وسيرة مهنية · " + TITLE_AR, desc, body, ld)
    html_ = html_.replace('<link rel="canonical"', f'<link rel="alternate" hreflang="ar" href="{url}">\n<link rel="alternate" hreflang="en" href="{SITE}/en/about/">\n<link rel="canonical"', 1)
    write("about", html_)


def qualifications_page(ba, page, write):
    url = f"{SITE}/about/qualifications/"
    nav, cld = crumbs([("الرئيسية", "/"), ("عن د. ميلاد ميخائيل", "/about/"), ("المؤهلات العلمية", None)])
    desc = "المؤهلات العلمية لـ د. ميلاد ميخائيل: دكتوراه في الصحة النفسية من جامعة قناة السويس (2022)، ماجستير التربية تخصص الصحة النفسية، والدبلوم المتخصص في الإرشاد وعلم النفس الإكلينيكي من جامعة طنطا، مع تقييم WES."
    rows = "\n".join(f'''        <li><span class="q-year">{y}</span><div><b>{esc(t)}</b><span lang="en" dir="ltr">{esc(en)}</span><span>{esc(where)}</span><span>{esc(grade)} · {esc(wes)}</span></div></li>'''
                     for y, t, en, where, grade, wes, _, _ in QUALS)
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      {nav}
      <h1>المؤهلات العلمية</h1>
      <p class="lead">الدرجات العلمية لـ د. ميلاد ميخائيل، زي ما هي مسجلة في الشهادات وفي تقييم <span lang="en" dir="ltr">World Education Services (WES)</span>.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow id-page">
      <ol class="q-timeline">
        <li><span class="q-year">2026</span><div><b>مقررات دراسات عليا في علم النفس (طالب زائر)</b><span lang="en" dir="ltr">JFK School of Psychology, National University (USA)</span><span>جاري الدراسة · اجتاز: نظريات النمو الإنساني (PSY 5104)</span></div></li>
{rows}
      </ol>
      <div class="note-box"><p>المؤهلات مقيّمة ومعادلة أمريكيًا من <span lang="en" dir="ltr">World Education Services (WES)</span>، وتقدر تتحقق منها من <a href="{WES}" target="_blank" rel="noopener">البادج الرسمية على Credly</a>. وهو عضو في الجمعية الأمريكية لعلم النفس (APA).</p></div>
      <p><a href="/about/publications/">الرسائل العلمية والأبحاث ←</a> · <a href="/about/">عن د. ميلاد ←</a></p>
      <p class="id-updated">آخر تحديث للصفحة: <time datetime="{UPDATED}">11 نوفمبر 2026</time></p>
    </div>
  </section>'''
    creds = [{"@type": "EducationalOccupationalCredential", "name": en, "alternateName": t,
              "credentialCategory": cat, "recognizedBy": org, "dateCreated": y}
             for y, t, en, where, grade, wes, org, cat in QUALS]
    ld = page_ld("WebPage", url, "المؤهلات العلمية", desc, cld,
                 {"about": {"@id": PERSON_ID}, "mainEntity": {"@type": "Person", "@id": PERSON_ID, "name": "Dr. Millad Mikhail", "hasCredential": creds}})
    write("about/qualifications", page("about/qualifications", "المؤهلات العلمية", desc, body, ld))


def publications_page(ba, page, write):
    url = f"{SITE}/about/publications/"
    nav, cld = crumbs([("الرئيسية", "/"), ("عن د. ميلاد ميخائيل", "/about/"), ("الرسائل العلمية والأبحاث", None)])
    desc = "الرسائل العلمية والأبحاث لـ د. ميلاد ميخائيل: رسالة الدكتوراه عن الإرشاد بالمعنى والقلق الوجودي والمناعة النفسية (2022)، رسالة الماجستير (2018)، وأبحاث مقدّمة في مؤتمرات شباب الباحثين بجامعة قناة السويس."
    th = "\n".join(f'''      <article class="pub">
        <p class="pub-kind">{esc(t["kind"])}، {t["year"]}</p>
        <h2>{esc(t["ar"])}</h2>
        <p lang="en" dir="ltr">{esc(t["en"])}</p>
        <dl>{"".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in t["facts"])}</dl>
      </article>''' for t in THESES)
    conf = "\n".join(f'<li><b>{esc(t)}</b><span>{esc(w)}</span></li>' for t, w in CONFERENCES)
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      {nav}
      <h1>الرسائل العلمية والأبحاث</h1>
      <p class="lead">الإنتاج العلمي لـ د. ميلاد ميخائيل في الصحة النفسية: الرسائل الجامعية والأبحاث المقدّمة في مؤتمرات علمية.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow id-page">
{th}
      <h2>أبحاث مقدّمة في مؤتمرات علمية</h2>
      <ul class="id-list pub-conf">
        {conf}
      </ul>
      <div class="note-box"><p>الهوية البحثية على <a href="{ORCID}" target="_blank" rel="me noopener">ORCID: 0009-0002-9254-367X</a>. ولو حابب تقرا ملخصات أبحاث نفسية حديثة مترجمة، زور <a href="/research/">مرصد الأبحاث النفسية</a>.</p></div>
      <p><a href="/about/qualifications/">المؤهلات العلمية ←</a> · <a href="/book/">الكتب ←</a></p>
      <p class="id-updated">آخر تحديث للصفحة: <time datetime="{UPDATED}">11 نوفمبر 2026</time></p>
    </div>
  </section>'''
    parts = [{"@type": "Thesis", "name": t["ar"], "alternateName": t["en"], "inLanguage": "ar", "datePublished": t["year"],
              "author": {"@id": PERSON_ID}, "inSupportOf": t["degree"],
              "sourceOrganization": SCU} for t in THESES]
    ld = page_ld("WebPage", url, "الرسائل العلمية والأبحاث", desc, cld, {"about": {"@id": PERSON_ID}, "hasPart": parts})
    write("about/publications", page("about/publications", "الرسائل العلمية والأبحاث", desc, body, ld))


def family_page(ba, page, write):
    url = f"{SITE}/family/"
    nav, cld = crumbs([("الرئيسية", "/"), ("التوعية الأسرية والزوجية", None)])
    desc = "التوعية الأسرية والزوجية مع د. ميلاد ميخائيل: مقالات عن التواصل بين الزوجين، تدخل الأهل، الغيرة والكذب والعصبية، ودعم شريك عنده اكتئاب أو قلق أو إدمان، مع اختبارات وأوراق تمرين مجانية."
    arts = {a["slug"]: a for a in ba.load()}
    chosen = [arts[s] for s in FAMILY_SLUGS if s in arts]
    cards = "\n        ".join(ba.card(a, "h3") for a in chosen)
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      {nav}
      <p class="kicker-g">للأزواج والمخطوبين والأسرة</p>
      <h1>التوعية الأسرية والزوجية</h1>
      <p class="lead">كل محتوى العلاقات والزواج في مكان واحد: إزاي تتواصلوا أحسن، وتحطوا حدود صحية مع الأهل، وتتعاملوا مع الخلافات والمشاعر الصعبة من غير ما العلاقة تتكسر.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <h2>ابدأ من هنا</h2>
      <ul class="link-grid">
        <li><a href="/partner/"><b>سلسلة «شريكي محيّرني»</b><span>حلقات عن الشريك الصعب، مع اختبار يساعدك تحدد تبدأ منين.</span></a></li>
        <li><a href="/relationship-check/"><b>علاقتك صحية؟</b><span>علامات خضرا وحمرا في العلاقة، في دقيقتين.</span></a></li>
        <li><a href="/tests/attachment-style/"><b>اختبار نمط التعلق</b><span>اعرف نمطك وإزاي بيأثر على اختياراتك.</span></a></li>
        <li><a href="/worksheets/"><b>أوراق تمرين مجانية</b><span>تمارين تطبعها وتكتب فيها لوحدك أو مع شريكك.</span></a></li>
      </ul>
      <h2>مقالات العلاقات والزواج</h2>
      <ul class="cards">
        {cards}
      </ul>
      <div class="note-box"><p>المحتوى ده للتوعية، ومش بديل عن جلسات مع متخصص. لو انتو في خلاف كبير أو في أذى، اقرا <a href="/help-now/">محتاج مساعدة دلوقتي</a>، أو شوف <a href="/sessions/">الجلسات النفسية والأسرية</a>.</p></div>
    </div>
  </section>'''
    ld = page_ld("CollectionPage", url, "التوعية الأسرية والزوجية", desc, cld, {
        "about": ["Couples communication", "Family relationships", "Marriage"],
        "author": {"@id": PERSON_ID},
        "hasPart": [{"@type": "Article", "headline": a["title"], "url": f"{SITE}/articles/{a['slug']}/"} for a in chosen]})
    write("family", page("family", "التوعية الأسرية والزوجية", desc, body, ld))


def en_about_page():
    """English profile page, built from the English homepage's own header/footer."""
    src = open(os.path.join(ROOT, "en", "index.html"), encoding="utf-8").read()
    head_links = "\n".join(l for l in re.findall(r'<link [^>]*>', src.split("</head>")[0])
                            if ("stylesheet" in l or "preconnect" in l) and "canonical" not in l and "alternate" not in l)
    header = re.search(r'(<a class="skip-link".*?</header>)', src, re.S)
    header = header.group(1) if header else ""
    footer = re.search(r'(<footer class="footer">.*?</footer>)', src, re.S)
    footer = footer.group(1) if footer else ""
    # in-page links of the English homepage must point back to it from /en/about/
    header = re.sub(r'href="#(?!main")([^"]+)"', r'href="/en/#\1"', header)
    footer = re.sub(r'href="#(?!main")([^"]+)"', r'href="/en/#\1"', footer)
    url = f"{SITE}/en/about/"
    desc = ("Dr. Millad Mikhail, PhD — mental health educator and author. Ph.D. in Mental Health (Suez Canal University, 2022), "
            "member of the American Psychological Association (APA), author of “Why Do We Love What Hurts Us?”.")
    cld = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/en/"},
        {"@type": "ListItem", "position": 2, "name": "About"}]}
    ld = page_ld("ProfilePage", url, "About Dr. Millad Mikhail", desc, cld, {
        "mainEntity": person_core({"jobTitle": "Mental Health Educator and Author", "description": desc,
                                   "alumniOf": [SCU, TANTA], "knowsLanguage": ["ar", "en"],
                                   "memberOf": {"@type": "Organization", "name": "American Psychological Association", "alternateName": "APA"}})}, lang="en")
    rows = "\n".join(f'<li><span class="q-year">{y}</span><div><b>{esc(en)}</b><span>{esc(org["name"])}</span></div></li>'
                     for y, t, en, where, grade, wes, org, cat in QUALS)
    page_ = f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About Dr. Millad Mikhail, PhD | Mental Health Educator and Author</title>
<meta name="description" content="{esc(desc)}">
<link rel="alternate" hreflang="ar" href="{SITE}/about/">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="profile">
<meta property="og:url" content="{url}">
<meta property="og:title" content="About Dr. Millad Mikhail, PhD">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/assets/og/home.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="About Dr. Millad Mikhail, PhD">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og/home.jpg">
<meta name="theme-color" content="#2f6f62">
{head_links}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{header}
<main id="main">
  <section class="page-hero">
    <div class="wrap narrow">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/en/">Home</a> <span aria-hidden="true">›</span> <span aria-current="page">About</span></nav>
      <h1>About Dr. Millad Mikhail, PhD</h1>
      <p class="lead">Mental health educator and author writing in Arabic about attachment, relationships, anxiety and meaning.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow id-page">
      <div class="id-card">
        <picture><source srcset="/assets/millad-cut.webp" type="image/webp"><img src="/assets/millad.jpg" width="160" height="160" alt="Dr. Millad Mikhail" loading="eager"></picture>
        <div>
          <p class="id-name">Dr. Millad Mikhail, PhD <span lang="ar" dir="rtl">· د. ميلاد ميخائيل</span></p>
          <p>Also known in Arabic media as <span lang="ar" dir="rtl">د. ميلاد منير</span> (Dr. Milad Mounir).</p>
        </div>
      </div>
      <h2>Biography</h2>
      <p>Dr. Millad Mikhail holds a Ph.D. in Mental Health from the Department of Mental Health, Faculty of Education in Ismailia, Suez Canal University (Egypt, 2022). His doctoral research studied the effectiveness of logo counselling (meaning-centred counselling) in reducing existential anxiety and improving psychological immunity among university students.</p>
      <p>His qualifications have been evaluated by World Education Services (WES), and he is a member of the American Psychological Association (APA). He is currently taking graduate psychology courses as a visiting student at the JFK School of Psychology, National University (USA).</p>
      <p>He is the author of <a href="{BOOK_EN}" target="_blank" rel="noopener">Why Do We Love What Hurts Us?</a> (also in Arabic), and he hosts the Arabic YouTube channel «جلسة شيزلونج» (Glset Shezlong). On this website he publishes free Arabic articles, self-tests and worksheets.</p>
      <h2>Education</h2>
      <ol class="q-timeline">
{rows}
      </ol>
      <h2>Research</h2>
      <p>Doctoral thesis (2022): <em>Effectiveness of Logo Counselling on Reducing the Level of Existential Anxiety and Improving Psychological Immunity for University Students</em>. More in Arabic on the <a href="/about/publications/" hreflang="ar">research page</a>. ORCID: <a href="{ORCID}" rel="me noopener" target="_blank">0009-0002-9254-367X</a>.</p>
      <h2>Find him online</h2>
      <ul class="id-links">
        <li><a href="{YOUTUBE}" rel="me noopener" target="_blank">YouTube (Arabic)</a></li>
        <li><a href="{LINKEDIN}" rel="me noopener" target="_blank">LinkedIn</a></li>
        <li><a href="{WES}" rel="me noopener" target="_blank">WES credential badge</a></li>
        <li><a href="/about/" hreflang="ar" lang="ar">عن د. ميلاد ميخائيل (العربية)</a></li>
      </ul>
      <p class="id-updated">Last updated: <time datetime="{UPDATED}">November 11, 2026</time></p>
    </div>
  </section>
</main>
{footer}
<script src="/assets/nav.js" defer></script>
</body>
</html>
'''
    os.makedirs(os.path.join(ROOT, "en", "about"), exist_ok=True)
    with open(os.path.join(ROOT, "en", "about", "index.html"), "w", encoding="utf-8") as f:
        f.write(page_)


def build_all(ba, page, write, SITE_=SITE):
    about_page(ba, page, write)
    qualifications_page(ba, page, write)
    publications_page(ba, page, write)
    family_page(ba, page, write)
    en_about_page()
