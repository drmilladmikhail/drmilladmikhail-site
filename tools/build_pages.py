#!/usr/bin/env python3
"""Build the standalone Arabic pages of drmilladmikhail.com:

  start/index.html    «ابدأ من هنا» — a guide to everything free on the site
  book/index.html     «الكتب» — a calm library page for both books (not a sales page)
  battery/index.html  «بطاريتي 1%» — coming-soon page for the next book

Run:  python3 tools/build_pages.py   (build_articles.py also calls it)
Lists (latest articles, tests, video topics) are read from the site's data files,
so the pages stay current when the scheduled tasks add content.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_articles as ba  # noqa: E402

SITE, esc = ba.SITE, ba.esc


def load(path, default):
    p = os.path.join(ROOT, path)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return default


def page(slug, title, desc, body, ld, og=f"{SITE}/assets/og/home.jpg"):
    url = f"{SITE}/{slug}/"
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | د. ميلاد ميخائيل</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{ba.social(url, title, desc, og, title, "website")}
<meta name="theme-color" content="#2f6f62">
{ba.FONTS}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{ba.TOPBAR}
<main id="main">
{body}
</main>
{ba.FOOTER}
<script src="/assets/share.js" defer></script>
<script src="/assets/helper.js" defer></script>
</body>
</html>
'''


def write(slug, html):
    d = os.path.join(ROOT, slug)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


# ------------------------------------------------------------------ start
def start_page():
    tests = load("tests/tests.json", [])
    arts = ba.load()
    vids = load("assets/videos.json", {})
    cats = [c for c in vids.get("categories", []) if c["slug"] != "other"]
    test_li = "\n".join(f'<li><a href="/tests/{t["slug"]}/">{esc(t["title"])}</a></li>' for t in tests)
    art_cards = "\n        ".join(ba.card(a, "h3") for a in arts[:3])
    vid_chips = "\n".join(f'<a href="/videos/#{c["slug"]}">{esc(c["name"])}</a>' for c in cats)
    extra = []
    for slug, label, note in (("questions", "أسئلة محرجة وإجابات علمية", "اللي بتتكسف تسأله، من غير حكم."),
                              ("ask", "اسأل من غير اسمك", "ابعت سؤالك المحرج، ومحدش هيعرف مين بعت."),
                              ("feelings", "عجلة المشاعر", "مش عارف تسمّي إحساسك؟ اختار لونه."),
                              ("relationship-check", "علاقتك صحية؟", "علامات خضرا وحمرا في العلاقة، في دقيقتين."),
                              ("challenges", "تحديات قصيرة", "مهمة صغيرة كل يوم من 3 لـ 7 أيام."),("glossary", "القاموس النفسي", "معاني المصطلحات النفسية وأمثلة من الحياة اليومية."),
                              ("worksheets", "أوراق تمرين مجانية", "تمارين تطبعها وتكتب فيها."),
                              ("roundup", "خلاصة كل شهر", "كل اللي نزل في الشهر في صفحة واحدة.")):
        if os.path.exists(os.path.join(ROOT, slug, "index.html")):
            extra.append(f'<li><a href="/{slug}/"><b>{label}</b><span>{note}</span></a></li>')
    extra_html = (f'<ul class="link-grid">{"".join(extra)}</ul>' if extra else "")
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">أهلاً بيك</p>
      <h1>ابدأ من هنا</h1>
      <p class="lead">الموقع ده مكتبة مجانية بالعربي البسيط عن الحب والتعلّق والقلق والصحة النفسية. مش لازم تقرا كل حاجة. اختار الطريق اللي يناسبك دلوقتي.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <ol class="path">
        <li>
          <h2><span class="step">1</span> اعرف نفسك في دقيقتين</h2>
          <p>اختبارات علمية مجانية، النتيجة بتطلع على طول، ومش بتتحفظ في أي مكان. لو مش عارف تبدأ منين، ابدأ باختبار نمط التعلّق.</p>
          <ul class="plain-list">{test_li}</ul>
          <div class="actions"><a class="btn primary" href="/tests/attachment-style/">ابدأ باختبار نمط التعلّق</a></div>
        </li>
        <li>
          <h2><span class="step">2</span> اقرا مقال يفسّر اللي بتحس بيه</h2>
          <p>مقالات قصيرة بالعامية، فيها أمثلة من الحياة وتمرين صغير تعمله بنفسك. مقال جديد كل اتنين وخميس.</p>
          <ul class="cards">
        {art_cards}
          </ul>
          <div class="actions"><a class="btn" href="/articles/">كل المقالات</a></div>
        </li>
        <li>
          <h2><span class="step">3</span> اتفرّج واسمع</h2>
          <p>فيديوهات «جلسة شيزلونج» متقسمة حسب الموضوع. اختار اللي يهمك:</p>
          <div class="vchips">{vid_chips}</div>
        </li>
        <li>
          <h2><span class="step">4</span> روح أعمق</h2>
          <p>لو حابب تكمّل بخطوات عملية، فيه كتاب «ليه بنحب اللي بيوجعنا؟»، وفيه تمارين وخطة 21 يوم. وده اختياري تمامًا، والموقع كله مجاني.</p>
          {extra_html}
          <div class="actions"><a class="btn" href="/book/">عن الكتب</a></div>
        </li>
      </ol>
      <div class="safety-note" role="note">
        <p><b>لو حاسس إنك مش بخير دلوقتي:</b> الموقع ده للتوعية ومش بديل عن متخصص. لو عندك أفكار تأذي بيها نفسك أو حاسس إنك في خطر، كلّم حد فورًا: مصر <a href="tel:16328">16328</a> (الخط الساخن للدعم النفسي) · أمريكا <a href="tel:988">988</a>.</p>
      </div>
      {ba.share_block(SITE + "/start/", "مكتبة مجانية بالعربي عن الحب والتعلق والصحة النفسية — د. ميلاد ميخائيل", "شارك الموقع")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "ابدأ من هنا", "url": f"{SITE}/start/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "description": "دليل لكل المحتوى المجاني على موقع د. ميلاد ميخائيل: اختبارات ومقالات وفيديوهات."}
    write("start", page("start", "ابدأ من هنا", "دليل لكل المحتوى المجاني: اختبارات نفسية، مقالات بالعامية، وفيديوهات عن الحب والتعلق والقلق.", body, ld))


# ------------------------------------------------------------------ books
CHAPTERS = [
    ("الفصل الأول", "ليه بنكرر نفس الغلطة؟", "ليه بنتشد لنفس النوع من العلاقات تاني وتالت."),
    ("الفصل التاني", "أنماط التعلق الأربعة", "الآمن والقلقان والمتجنب والخايف المتجنب، وإزاي تعرف نمطك."),
    ("الفصل التالت", "جذورك", "إزاي البيت وأول حب بيرسموا طريقتنا في الحب."),
    ("الفصل الرابع", "العلامات الحمرا", "إزاي تشوف الإشارات بدري قبل ما تتعلّق."),
    ("الفصل الخامس", "ليه صعب أمشي؟", "الحبال اللي بتشدنا للعلاقة المؤذية، ووقفة أمان."),
    ("الفصل السادس", "خطة الشفاء 21 يوم", "مهمة صغيرة كل يوم ترجّعك لنفسك."),
    ("الفصل السابع", "اختيار صح", "الفرق بين الكيميا والتوافق، والهدوء اللي هو أمان مش ملل."),
    ("الخاتمة", "عهد مع نفسي", ""),
]
FAQ = [
    ("هل الكتاب بديل عن العلاج النفسي؟",
     "لأ. الكتاب للتوعية وفهم النفس، والاختبارات اللي فيه أدوات للتأمل مش مقاييس طبية. لو بتعاني بشكل كبير، كلّم متخصص."),
    ("محتاج جهاز Kindle عشان أقراه؟",
     "لأ. تقدر تقراه على تطبيق Kindle المجاني على الموبايل أو الكمبيوتر. والنسخة الإنجليزي متاحة كمان ككتاب ورقي."),
    ("الشخصيات اللي في الكتاب حقيقية؟",
     "لأ. سارة وأمير وباقي الشخصيات خيالية، ومتجمعة من قصص كتير، عشان محدش يتعرف عليه."),
    ("لازم أشتري الكتاب عشان أستفيد من الموقع؟",
     "خالص. المقالات والاختبارات والفيديوهات على الموقع كلها مجانية. الكتاب لمن يحب يكمّل بتمارين وخطة منظمة."),
]


def book_page():
    ch = "\n".join(f'<li><span class="ch-n">{esc(n)}</span><b>{esc(t)}</b>{f"<span>{esc(d)}</span>" if d else ""}</li>'
                   for n, t, d in CHAPTERS)
    faq = "\n".join(f'<details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in FAQ)
    pics = [("love-p09", "بنت قاعدة قدامها تلات شباب ليهم نفس الضل"),
            ("love-p18", "طفلة بتجري ناحية مامتها اللي فاتحة إيديها"),
            ("love-p46", "رسمة من فصل خطة الشفاء")]
    gallery = "\n".join(f'<figure>{ba.pic(n, a, sizes="(max-width: 700px) 100vw, 33vw")}</figure>' for n, a in pics)
    body = f'''  <section class="page-hero">
    <div class="wrap">
      <p class="kicker-g">الكتب</p>
      <h1>كتب د. ميلاد ميخائيل</h1>
      <p class="lead">كتب عملية بالعامية المصرية، فيها قصص ورسومات وتمارين، عن الحب والتعلّق والبحث عن المعنى.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <article class="book-row">
        <picture class="book-cover">
          <source srcset="/assets/love-cover-ar.webp" type="image/webp">
          <img src="/assets/love-cover-ar.jpg" width="480" height="768" alt="غلاف كتاب ليه بنحب اللي بيوجعنا؟">
        </picture>
        <div>
          <h2>ليه بنحب اللي بيوجعنا؟</h2>
          <p class="sub">دليل عملي تفهم بيه نمط تعلقك وتختار شريك حياتك صح</p>
          <p>الكتاب بدأ كمحاضرة للشباب، وبيجاوب على أسئلة زي: «ليه بختار نفس النوع كل مرة؟» و«ليه مش قادر أنساه مع إنه أذاني؟». فيه 7 فصول قصيرة، واختبارات، وتحديات 7 أيام، وخطة شفاء 21 يوم.</p>
          <ul class="ticks">
            <li>بالعامية المصرية، ومعاه نسخة إنجليزي</li>
            <li>رسومات في كل فصل</li>
            <li>صفحات تمارين تقدر تطبعها لنفسك</li>
          </ul>
          <div class="actions">
            <a class="btn primary" href="{ba.BOOK_AR}" target="_blank" rel="noopener">النسخة العربي (Kindle)</a>
            <a class="btn" href="{ba.BOOK_EN}" target="_blank" rel="noopener" lang="en">English edition</a>
          </div>
        </div>
      </article>
      <h3 class="sec-h">جوه الكتاب</h3>
      <ol class="chapters">{ch}</ol>
      <div class="gallery">{gallery}</div>
      <p class="note-free">عايز تجرّب قبل ما تقرر؟ مقالات كتير على الموقع مأخوذة من الكتاب، <a href="/articles/">اقراها مجانًا</a>.</p>
      <h3 class="sec-h">أسئلة شائعة</h3>
      {faq}
      <article class="book-row soon" id="battery">
        <picture class="book-cover">
          <source srcset="/assets/battery-cover.webp" type="image/webp">
          <img src="/assets/battery-cover.jpg" width="480" height="720" alt="غلاف كتاب بطاريتي 1%" loading="lazy">
        </picture>
        <div>
          <p class="badge-soon">قريبًا</p>
          <h2>بطاريتي 1%</h2>
          <p class="sub">إزاي تشحن روحك من جديد وتلاقي معنى لحياتك</p>
          <p>تمارين وقصص ورسومات، للأيام اللي بتحس فيها إن طاقتك خلصت.</p>
          <div class="actions"><a class="btn" href="/battery/">اعرف أكتر</a></div>
        </div>
      </article>
      {ba.share_block(SITE + "/book/", "كتب د. ميلاد ميخائيل: ليه بنحب اللي بيوجعنا؟ وبطاريتي 1%", "شارك الصفحة")}
    </div>
  </section>'''
    ld = [{"@context": "https://schema.org", "@type": "Book", "name": "ليه بنحب اللي بيوجعنا؟",
           "alternateName": "Why Do We Love What Hurts Us?", "inLanguage": ["ar", "en"],
           "author": {"@id": f"{SITE}/#person", "@type": "Person", "name": "Dr. Millad Mikhail"},
           "image": f"{SITE}/assets/love-cover-ar.jpg", "url": f"{SITE}/book/",
           "sameAs": [ba.BOOK_AR, ba.BOOK_EN], "datePublished": "2026"},
          {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    write("book", page("book", "الكتب", "كتب د. ميلاد ميخائيل بالعامية: «ليه بنحب اللي بيوجعنا؟» عن نمط التعلق واختيار شريك الحياة، و«بطاريتي 1%» قريبًا.", body, ld))


# ------------------------------------------------------------------ battery
def battery_page():
    body = f'''  <section class="section">
    <div class="wrap">
      <article class="book-row soon">
        <picture class="book-cover">
          <source srcset="/assets/battery-cover.webp" type="image/webp">
          <img src="/assets/battery-cover.jpg" width="480" height="720" alt="غلاف كتاب بطاريتي 1% لـ د. ميلاد ميخائيل">
        </picture>
        <div>
          <p class="badge-soon">قريبًا</p>
          <h1>بطاريتي 1%</h1>
          <p class="sub">إزاي تشحن روحك من جديد وتلاقي معنى لحياتك</p>
          <p>كتاب جديد بالعامية المصرية، فيه تمارين وقصص ورسومات، للأيام اللي بتحس فيها إن طاقتك خلصت ومش لاقي سبب تكمّل بيه.</p>
          <p>الكتاب قريب من موضوع رسالة الدكتوراه بتاعتي: الإرشاد بالمعنى (العلاج بالمعنى عند فيكتور فرانكل) والمناعة النفسية، بس مكتوب للناس العادية، مش للمتخصصين.</p>
          <p><b>عايز تعرف أول ما ينزل؟</b> تابع قناة «جلسة شيزلونج» أو المدونة.</p>
          <div class="actions">
            <a class="btn primary" href="https://www.youtube.com/@DrMilladMikhail?sub_confirmation=1" target="_blank" rel="noopener">اشترك في القناة</a>
            <a class="btn" href="https://blog.drmilladmikhail.com/" target="_blank" rel="noopener">المدونة</a>
          </div>
        </div>
      </article>
      <h2 class="sec-h">لحد ما ينزل، جرّب دول</h2>
      <ul class="link-grid">
        <li><a href="/tests/wellbeing-who5/"><b>مؤشر الرفاهية النفسية (WHO-5)</b><span>طاقتك ومزاجك عاملين إيه آخر أسبوعين؟</span></a></li>
        <li><a href="/videos/#immunity"><b>فيديوهات المناعة النفسية</b><span>إزاي تقف تاني بعد الضغوط.</span></a></li>
        <li><a href="/articles/"><b>المقالات</b><span>مقال جديد كل اتنين وخميس.</span></a></li>
      </ul>
      {ba.share_block(SITE + "/battery/", "بطاريتي 1% — كتاب جديد قريبًا لـ د. ميلاد ميخائيل", "شارك الصفحة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "Book", "name": "بطاريتي 1%",
          "alternateName": "My Battery Is at 1%", "inLanguage": "ar", "url": f"{SITE}/battery/",
          "author": {"@id": f"{SITE}/#person", "@type": "Person", "name": "Dr. Millad Mikhail"},
          "image": f"{SITE}/assets/battery-cover.jpg", "description": "إزاي تشحن روحك من جديد وتلاقي معنى لحياتك — قريبًا."}
    write("battery", page("battery", "بطاريتي 1% (قريبًا)", "«بطاريتي 1%»: كتاب جديد قريبًا لـ د. ميلاد ميخائيل عن إزاي تشحن روحك وتلاقي معنى لحياتك.", body, ld))


# ------------------------------------------------------------------ questions
def questions_page():
    data = load("content/questions.json", {"sections": [], "items": []})
    secs, items = data["sections"], data["items"]

    def qa(it):
        paras = "".join(f"<p>{esc(x)}</p>" for x in it["a"])
        link = (f'<p class="qa-link">اقرا كمان: <a href="{it["link"][0]}">{esc(it["link"][1])}</a></p>' if it.get("link") else "")
        when = (f'<p class="qa-when{" qa-urgent" if it.get("safety") else ""}"><b>امتى تكلّم متخصص؟</b> {esc(it["when"])}</p>' if it.get("when") else "")
        return f'<details class="faq qa" id="{it["id"]}"><summary>{esc(it["q"])}</summary><div class="qa-body">{paras}{when}{link}</div></details>'

    chips = "\n".join(f'<a href="#sec-{c["slug"]}">{esc(c["name"])}{' (<bdi dir="ltr">18+</bdi>)' if c.get("adult") else ""} <span>{sum(1 for i in items if i["section"] == c["slug"])}</span></a>' for c in secs)
    blocks = ""
    for c in secs:
        qs = "\n".join(qa(i) for i in items if i["section"] == c["slug"])
        if c.get("adult"):
            inner = f'''<details class="adult-gate"><summary>القسم ده للكبار فوق 18 سنة. دوس هنا عشان تفتحه</summary>
          <p class="vnote">{esc(c.get("note", ""))}</p>
          {qs}
        </details>'''
        else:
            inner = qs
        blocks += f'''
      <section class="vcat" id="sec-{c["slug"]}" aria-labelledby="h-{c["slug"]}">
        <h2 id="h-{c["slug"]}">{esc(c["name"])}{' <span class="vcount" dir="ltr">18+</span>' if c.get("adult") else ""}</h2>
        {inner}
      </section>'''
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">من غير كسوف</p>
      <h1>أسئلة محرجة… وإجابات علمية</h1>
      <p class="lead">أسئلة ناس كتير بتتكسف تسألها قدام حد، عن المشاعر والعلاقات والجنس. الإجابات مبسّطة ومبنية على العلم، ومن غير حكم على حد.</p>
      <p class="privacy">🔒 محدش بيعرف انت فتحت أنهي سؤال. الصفحة مش بتسجل أي حاجة.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <nav class="vchips" aria-label="أقسام الأسئلة">{chips}</nav>
      {blocks}
      <div class="note-box ask-cta"><h2>سؤالك مش موجود؟</h2><p>ابعته من غير اسمك، وممكن نجاوبه هنا في الأسابيع الجاية.</p><div class="actions"><a class="btn primary" href="/ask/">اسأل من غير اسمك</a></div></div>
      <div class="safety-note" role="note">
        <p><b>تنبيه:</b> الإجابات دي للتوعية، ومش تشخيص ولا بديل عن دكتور أو معالج. لو عندك أفكار تأذي بيها نفسك أو حاسس إنك في خطر، كلّم حد فورًا: مصر <a href="tel:16328">16328</a> · أمريكا <a href="tel:988">988</a>.</p>
      </div>
      {ba.share_block(SITE + "/questions/", "أسئلة محرجة وإجابات علمية بالمصري — د. ميلاد ميخائيل", "شارك الصفحة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "ar", "url": f"{SITE}/questions/",
          "author": {"@id": f"{SITE}/#person"},
          "mainEntity": [{"@type": "Question", "name": i["q"],
                          "acceptedAnswer": {"@type": "Answer", "text": " ".join(i["a"]) + (" " + i["when"] if i.get("when") else "")}}
                         for i in items]}
    write("questions", page("questions", "أسئلة محرجة وإجابات علمية",
                            "أسئلة ناس كتير بتتكسف تسألها عن المشاعر والعلاقات والجنس، وإجاباتها العلمية بالعامية المصرية من غير حكم.", body, ld))


# ------------------------------------------------------------------ challenges
def challenges_page():
    chs = load("content/challenges.json", [])
    cards = ""
    for c in chs:
        tasks = "\n".join(f'<li><label><input type="checkbox" data-key="{c["id"]}-{n}"> <span><b>يوم {n}:</b> {esc(t)}</span></label></li>'
                          for n, t in enumerate(c["tasks"], 1))
        journey = c["id"] == "seven-day-journey"
        extra = '''<div class="journey-progress" role="group" aria-label="تقدمك في الرحلة">
          <div class="journey-track"><span data-journey-bar></span></div>
          <p class="journey-badge" data-journey-badge hidden>شارة «خطوة لنفسي»: أنهيت الرحلة!</p>
        </div>
        <p class="journey-private">تقدمك بيتحفظ على جهازك فقط. مفيش حساب، ومفيش إجابات شخصية بتتبعت للموقع.</p>
        <div data-journey-share-wrap hidden>
          <button type="button" class="sh" data-journey-share>صمّم بطاقة إنجازك وشاركها</button>
          <p data-journey-share-hint role="status" aria-live="polite">الصورة بتتجهز على جهازك فقط؛ مفيش بيانات بتتبعت للموقع.</p>
        </div>
        <button type="button" class="sh journey-reset" data-journey-reset>ابدأ الرحلة من جديد</button>''' if journey else ""
        cards += f'''
      <article class="challenge{" featured-journey" if journey else ""}" id="{c["id"]}">
        <h2>{esc(c["title"])}</h2>
        <p class="ch-why">{esc(c["why"])}</p>
        <ol class="ch-tasks">{tasks}</ol>
        <p class="ch-progress" aria-live="polite" data-for="{c["id"]}" data-total="{len(c["tasks"])}"></p>{extra}
      </article>'''
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">خطوة صغيرة كل يوم</p>
      <h1>تحديات قصيرة</h1>
      <p class="lead">تحديات من 3 لـ 7 أيام، مهمة صغيرة كل يوم مش بتاخد أكتر من 10 دقايق. علّم ✓ على اليوم اللي خلّصته، والموقع هيفتكره على جهازك انت بس.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      {cards}
      <p class="fine" data-ch-storage-hint role="status" aria-live="polite"></p>
      <div class="safety-note" role="note"><p>التحديات دي للتجربة وتحسين المزاج، ومش علاج. لو حاسس إنك مش بخير لفترة طويلة، كلّم متخصص. مصر <a href="tel:16328">16328</a> · أمريكا <a href="tel:988">988</a>.</p></div>
      {ba.share_block(SITE + "/challenges/", "تحديات نفسية قصيرة: 7 أيام من غير جلد للذات، نوم منتظم، امتنان… — د. ميلاد ميخائيل", "اتحدّى صاحبك")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "تحديات قصيرة", "url": f"{SITE}/challenges/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    html = page("challenges", "تحديات قصيرة", "تحديات نفسية قصيرة من 3 لـ 7 أيام: من غير جلد للذات، امتنان، نوم منتظم، «لأ» صغيرة، وسوشيال ميديا أقل.", body, ld)
    html = html.replace('<script src="/assets/share.js" defer></script>', '<script src="/assets/challenges.js" defer></script>\n<script src="/assets/share.js" defer></script>')
    write("challenges", html)


# ------------------------------------------------------------------ feelings wheel
def feelings_page():
    data = load("content/feelings.json", {"families": []})
    fams = data["families"]
    wheel = "\n".join(f'<button type="button" class="fw-fam hue-{f["hue"]}" style="--i:{n}" data-fam="{f["id"]}" aria-pressed="false">'
                      f'<span class="fw-emo" aria-hidden="true">{f["emoji"]}</span><span>{esc(f["name"])}</span></button>'
                      for n, f in enumerate(fams))
    groups = ""
    for f in fams:
        cards = ""
        for it in f["items"]:
            sos = ('<p class="fw-sos">لو عندك أفكار تأذي بيها نفسك أو حاسس إنك في خطر، كلّم حد فورًا: مصر <a href="tel:16328">16328</a>'
                   ' أو الطوارئ <a href="tel:122">122</a> · أمريكا <a href="tel:988">988</a> أو <a href="tel:911">911</a>.</p>') if it.get("safety") else ""
            cards += f'''
          <article class="fw-card hue-{f["hue"]}" id="f-{it["id"]}" data-fam="{f["id"]}" data-name="{esc(it["name"])}" tabindex="-1">
            <p class="fw-kicker"><span aria-hidden="true">{f["emoji"]}</span> {esc(f["name"])}</p>
            <h2 class="fw-title">حاسس إني {esc(it["name"])}</h2>
            <dl>
              <dt>يعني إيه؟</dt><dd>{esc(it["means"])}</dd>
              <dt>بيبان في جسمك إزاي؟</dt><dd>{esc(it["body"])}</dd>
              <dt>الإحساس ده بيقولك إيه؟</dt><dd>{esc(it["says"])}</dd>
              <dt>جرّب دلوقتي</dt><dd class="fw-try">{esc(it["try"])}</dd>
            </dl>{sos}
          </article>'''
        groups += f'''
        <section class="fw-group" data-fam="{f["id"]}" aria-labelledby="g-{f["id"]}">
          <h2 id="g-{f["id"]}"><span aria-hidden="true">{f["emoji"]}</span> {esc(f["name"])}</h2>{cards}
        </section>'''
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">سمّيه… يهدى</p>
      <h1>عجلة المشاعر</h1>
      <p class="lead">ساعات بنقول «أنا مش كويس» وبس. لما تعرف تسمّي إحساسك بالظبط، بتفهم نفسك أكتر وبتعرف تتصرف. اختار أقرب لون لإحساسك دلوقتي.</p>
      <p class="privacy">🔒 مفيش حاجة بتتسجل أو بتتبعت لحد.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <div class="fw" id="fw">
        <div class="fw-pick" hidden>
          <p class="fw-step" id="fw-q1"><span class="step">1</span> حاسس بإيه دلوقتي؟</p>
          <div class="fw-wheel" role="group" aria-labelledby="fw-q1">
            {wheel}
            <span class="fw-hub" aria-hidden="true">إحساسك<br>إيه؟</span>
          </div>
          <div class="fw-sub" hidden>
            <p class="fw-step" id="fw-q2"><span class="step">2</span> أقرب كلمة لإحساسك؟</p>
            <div class="fw-chips" role="group" aria-labelledby="fw-q2"></div>
          </div>
        </div>
        <div class="fw-groups">{groups}
        </div>
        <div class="fw-after" hidden>
          <div class="actions">
            <button type="button" class="btn fw-again">اختار إحساس تاني</button>
            <a class="btn primary fw-wa" href="#" target="_blank" rel="noopener">ابعته لحد بتثق فيه</a>
          </div>
        </div>
      </div>
      <div class="note-box">
        <h2>ليه تسمية الإحساس بتفرق؟</h2>
        <p>دراسة مشهورة من جامعة UCLA (ليبرمان وزملاؤه، 2007) لقت إن لما الناس بيسمّوا إحساسهم بكلمة، نشاط اللوزة الدماغية (جرس الإنذار في المخ) بيقل. وأبحاث «دقة المشاعر» بتقول إن اللي بيعرف يفرّق بين «زعلان» و«مخذول» و«وحيد» بيعرف يتعامل مع مشاعره أحسن.</p>
        <p>المشاعر مش حلوة ووحشة، كلها رسايل. الفكرة إنك تسمع الرسالة، مش إنك تكتمها أو تمشي وراها من غير تفكير.</p>
      </div>
      <div class="safety-note" role="note"><p>العجلة دي للتوعية وفهم النفس، ومش تشخيص. لو إحساس صعب مكمّل معاك أكتر من أسبوعين أو مأثر على حياتك، كلّم متخصص. ولو حاسس إنك في خطر: مصر <a href="tel:16328">16328</a> · أمريكا <a href="tel:988">988</a>.</p></div>
      {ba.share_block(SITE + "/feelings/", "عجلة المشاعر: مش عارف تسمّي إحساسك؟ اختار لونه — د. ميلاد ميخائيل", "شارك العجلة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "عجلة المشاعر", "url": f"{SITE}/feelings/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "description": "أداة تفاعلية بالعامية المصرية تساعدك تسمّي إحساسك بالظبط وتعرف رسالته وتعمل خطوة صغيرة."}
    html = page("feelings", "عجلة المشاعر: سمّي إحساسك", "مش عارف تسمّي إحساسك؟ عجلة المشاعر بالمصري: اختار اللون، وبعدين الكلمة، واعرف الإحساس ده بيقولك إيه وتعمل إيه دلوقتي.", body, ld)
    html = html.replace('<script src="/assets/share.js" defer></script>', '<script src="/assets/feelings.js" defer></script>\n<script src="/assets/share.js" defer></script>')
    write("feelings", html)


# ------------------------------------------------------------------ relationship check
def relationship_check_page():
    data = load("content/relationship-check.json", {"items": []})
    qs = ""
    for n, it in enumerate(data["items"], 1):
        opts = "".join(f'<label class="opt"><input type="radio" name="{it["id"]}" value="{v}" required><span>{lab}</span></label>'
                       for v, lab in (("2", "أيوه"), ("1", "ساعات"), ("0", "لأ")))
        qs += f'''<fieldset class="q" data-type="{it["type"]}" data-text="{esc(it["t"])}">
          <legend><span class="qn">{n}</span> {esc(it["t"])}</legend>
          <div class="opts opts-3">{opts}</div>
        </fieldset>'''
    body = f'''  <a class="quick-exit" href="https://www.google.com/" rel="noreferrer">✕ اخرج بسرعة</a>
  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">في دقيقتين</p>
      <h1>علاقتك صحية؟</h1>
      <p class="lead">{len(data["items"])} جملة عن علاقتك (خطوبة، جواز، أو ارتباط). جاوب بصراحة عن آخر كام شهر، وهتشوف العلامات الخضرا اللي عندك، والعلامات اللي محتاجة تقف عندها.</p>
      <p class="privacy">🔒 الإجابات مش بتتبعت لأي حد ومش بتتحفظ. وزرار «اخرج بسرعة» بيقفل الصفحة فورًا لو حد دخل عليك.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <form id="rc" class="quiz" novalidate>
        {qs}
        <p class="quiz-error" hidden>فاضل جمل ماجاوبتهاش، اتعلّمت باللون الأحمر.</p>
        <button type="submit" class="btn primary big">شوف النتيجة</button>
      </form>
      <noscript><p>الصفحة دي محتاجة JavaScript عشان تحسب النتيجة.</p></noscript>
      <div id="rc-result" class="result" hidden tabindex="-1" aria-live="polite"></div>
      <div class="note-box">
        <h2>يعني إيه علاقة صحية؟</h2>
        <p>مفيش علاقة مثالية، وكل الناس بتختلف وبتتخانق. الفرق إن العلاقة الصحية فيها احترام وأمان وكلام مفتوح، والاختلاف فيها مش بيتحول لخوف أو تحكم أو إهانة. القايمة دي مبنية على علامات الإنذار اللي بتنشرها جهات زي loveisrespect ومراكز السيطرة على الأمراض الأمريكية (CDC) ومنظمة الصحة العالمية، وهي للتوعية ومش مقياس تشخيصي.</p>
      </div>
      {ba.share_block(SITE + "/relationship-check/", "علاقتك صحية؟ علامات خضرا وحمرا في دقيقتين — د. ميلاد ميخائيل", "شارك الصفحة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "علاقتك صحية؟", "url": f"{SITE}/relationship-check/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "description": "قايمة توعية بالعامية المصرية عن علامات العلاقة الصحية وعلامات الإنذار."}
    html = page("relationship-check", "علاقتك صحية؟ علامات خضرا وحمرا", "علاقتك صحية ولا لأ؟ جمل بسيطة بالمصري تعرف منها العلامات الخضرا والحمرا في علاقتك، من غير ما حاجة تتسجل.", body, ld)
    html = html.replace('<script src="/assets/share.js" defer></script>', '<script src="/assets/relcheck.js" defer></script>\n<script src="/assets/share.js" defer></script>')
    write("relationship-check", html)


# ------------------------------------------------------------------ worksheets
def worksheets_page():
    """Library of printable worksheets. PDFs are made by tools/build_worksheets.py."""
    data = load("content/worksheets.json", {"categories": [], "items": []})
    man = load("worksheets/manifest.json", {})
    items = [w for w in data["items"] if w["slug"] in man and os.path.exists(os.path.join(ROOT, "worksheets", w["slug"] + ".pdf"))]
    if not items:
        return
    items.sort(key=lambda w: w.get("added", ""), reverse=True)
    pages_ar = {1: "صفحة واحدة", 2: "صفحتين"}

    def card(w):
        m = man[w["slug"]]
        pdf = f'/worksheets/{w["slug"]}.pdf'
        rel = (f'<p class="ws-rel">مرتبط بـ: <a href="{w["related"][0]}">{esc(w["related"][1])}</a></p>' if w.get("related") else "")
        return f'''<li class="ws-card" id="{w["slug"]}">
          <a class="ws-thumb" href="{pdf}" tabindex="-1" aria-hidden="true"><img src="/worksheets/{w["slug"]}.webp" width="{m["w"]}" height="{m["h"]}" alt="" loading="lazy" decoding="async"></a>
          <div class="ws-body">
            <h3>{esc(w["title"])}</h3>
            <p>{esc(w["desc"])}</p>
            <p class="ws-meta">PDF · {pages_ar.get(m["pages"], str(m["pages"]) + " صفحات")} · <bdi dir="ltr">{m["kb"]} KB</bdi></p>
            {rel}
            <div class="ws-actions"><a class="btn primary" href="{pdf}" download>حمّل واطبع</a><a class="btn" href="{pdf}" target="_blank" rel="noopener">افتحه<span class="sr-only"> ({esc(w["title"])})</span></a></div>
          </div>
        </li>'''

    cats = [c for c in data["categories"] if any(w["category"] == c["slug"] for w in items)]
    chips = "\n".join(f'<a href="#sec-{c["slug"]}">{esc(c["name"])} <span>{sum(1 for w in items if w["category"] == c["slug"])}</span></a>' for c in cats)
    blocks = ""
    for c in cats:
        cards = "\n".join(card(w) for w in items if w["category"] == c["slug"])
        blocks += f'''
      <section class="vcat" id="sec-{c["slug"]}" aria-labelledby="h-{c["slug"]}">
        <h2 id="h-{c["slug"]}">{esc(c["name"])}</h2>
        <ul class="ws-cards">{cards}</ul>
      </section>'''
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">اطبع واكتب بإيدك</p>
      <h1>مكتبة أوراق التمرين</h1>
      <p class="lead">تمارين نفسية مجانية تطبعها وتكتب فيها، عن الحب والعلاقات والمشاعر والعناية بالنفس. كل ورقة صفحتين، بالعامية، ومن غير تسجيل ولا إيميل.</p>
      <p class="privacy">✍️ الكتابة بالإيد بتخليك تبطّأ وتفكر. اطبعها، أو افتحها على التابلت واكتب عليها.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <nav class="vchips" aria-label="أقسام الأوراق">{chips}</nav>
      {blocks}
      <div class="safety-note" role="note">
        <p><b>تنبيه:</b> الأوراق دي للتأمل وفهم النفس، ومش تشخيص ولا بديل عن العلاج. لو حاسس بضيق جامد أو خايف على نفسك، كلّم حد فورًا: مصر <a href="tel:16328">16328</a> · أمريكا <a href="tel:988">988</a>.</p>
      </div>
      {ba.share_block(SITE + "/worksheets/", "أوراق تمرين نفسية مجانية تطبعها وتكتب فيها — د. ميلاد ميخائيل", "شارك المكتبة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "مكتبة أوراق التمرين", "url": f"{SITE}/worksheets/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "hasPart": [{"@type": "DigitalDocument", "name": w["title"], "description": w["desc"], "encodingFormat": "application/pdf",
                       "url": f'{SITE}/worksheets/{w["slug"]}.pdf', "inLanguage": "ar", "isAccessibleForFree": True,
                       "author": {"@id": f"{SITE}/#person"}, "dateCreated": w.get("added")} for w in items]}
    write("worksheets", page("worksheets", "مكتبة أوراق التمرين (PDF مجاني)",
                             "أوراق تمرين نفسية مجانية بالعامية تطبعها وتكتب فيها: حدودك في الحب، القلق لما محدش يرد، يوميات المشاعر، خطة اليوم الصعب، وأكتر.",
                             body, ld))


# ------------------------------------------------------------------ ask anonymously
def ask_page():
    """«اسأل من غير اسمك». Built only when content/ask.json has a form_url (a Google Form he owns)."""
    cfg = load("content/ask.json", {})
    url = cfg.get("form_url", "").strip()
    if not url.startswith("https://"):
        return False
    wa = "".join(ch for ch in cfg.get("whatsapp", "") if ch.isdigit())
    sessions = ""
    if wa:
        from urllib.parse import quote
        msg = quote("أهلًا د. ميلاد، أنا جاي من الموقع وعايز أحجز جلسة نفسية أونلاين. أنا مقيم في: ")
        sessions = f'''<div class="note-box sessions-box">
        <h2>عايز جلسة مع د. ميلاد؟</h2>
        <p>متاح جلسات نفسية أونلاين لأهلنا في مصر والوطن العربي، لو محتاج حد يسمعك ويتابع معاك بشكل شخصي. ابعت رسالة على واتساب ونتفق على التفاصيل.</p>
        <div class="actions"><a class="btn primary" href="https://wa.me/{wa}?text={msg}" target="_blank" rel="noopener">كلّمني على واتساب</a></div>
      </div>'''
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">من غير كسوف ومن غير اسم</p>
      <h1>اسأل من غير اسمك</h1>
      <p class="lead">فيه سؤال محرج مش قادر تسأله لحد؟ ابعته هنا. مش هنطلب اسمك ولا إيميلك ولا رقمك، ومحدش هيعرف مين بعت.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <ol class="ask-steps">
        <li><b>اكتب سؤالك</b><span>زي ما بتقوله لنفسك، بالعامية. ماتكتبش اسمك أو أي حاجة تعرّف بيك.</span></li>
        <li><b>اختار إذا كنت موافق ننشره</b><span>لو وافقت، ممكن نجاوبه في صفحة «أسئلة محرجة» من غير أي بيانات عنك.</span></li>
        <li><b>عايز رد ليك انت؟ (اختياري)</b><span>اكتب إيميلك في آخر خانة في الفورم. لو سيبتها فاضية، سؤالك يفضل من غير أي بيانات عنك خالص.</span></li>
        <li><b>تابع صفحة الأسئلة</b><span>بنضيف إجابات جديدة كل أسبوع، مبنية على العلم ومن غير حكم.</span></li>
      </ol>
      <div class="actions"><a class="btn primary big" href="{esc(url)}" target="_blank" rel="noopener">اكتب سؤالك دلوقتي</a>
        <a class="btn" href="/questions/">شوف الأسئلة اللي اتجاوبت</a></div>
      <p class="privacy">🔒 الفورم على Google Forms. مش بيطلب تسجيل دخول، واسمك مش بيوصلنا. الإيميل بيوصل بس لو انت كتبته بنفسك.</p>
      <div class="note-box">
        <h2>الرد الشخصي بيبقى إزاي؟</h2>
        <p>لو كتبت إيميلك، بنحاول نبعتلك رد قصير بإيميل. الرد ده توعوي وعام، ومش استشارة ولا تشخيص، وممكن ياخد وقت.</p>
      </div>
      {sessions}
      <div class="safety-note" role="note"><p><b>الصندوق ده مش للطوارئ</b>، والرد ممكن ياخد أسابيع، ومش كل سؤال هيتنشر. ولا هو بديل عن استشارة شخصية. لو حاسس إنك في خطر أو بتفكر تأذي نفسك، كلّم حد دلوقتي: مصر <a href="tel:16328">16328</a> أو <a href="tel:122">122</a> · أمريكا <a href="tel:988">988</a> أو <a href="tel:911">911</a>.</p></div>
      {ba.share_block(SITE + "/ask/", "اسأل د. ميلاد من غير اسمك: سؤالك المحرج ليه إجابة علمية", "شارك الصفحة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "اسأل من غير اسمك", "url": f"{SITE}/ask/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    write("ask", page("ask", "اسأل من غير اسمك", "ابعت سؤالك المحرج عن المشاعر أو العلاقات أو الجنس من غير اسمك، وممكن نجاوبه علميًا في صفحة «أسئلة محرجة».", body, ld))
    return True



# ------------------------------------------------------------------ porn addiction / CSBD (special page, 2026-11-05)
def csbd_page():
    toc = [("what", "يعني إيه؟"), ("signs", "العلامات"), ("not", "إمتى مش مشكلة؟"), ("why", "ليه بيحصل؟"),
           ("cycle", "الدايرة"), ("steps", "خطوات التعافي"), ("relapse", "لو وقعت"), ("partner", "لشريك الحياة"),
           ("help", "إمتى تكلّم متخصص؟")]
    chips = "".join(f'<a href="#{i}">{t}</a>' for i, t in toc)
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">صفحة خاصة · للكبار <bdi dir="ltr">18+</bdi></p>
      <h1>التعافي من إدمان الإباحية والسلوك الجنسي القهري</h1>
      <p class="lead">لو حاسس إنك مش قادر تتحكم في مشاهدة الإباحية أو في سلوك جنسي معيّن، ونفسك تبطّل ومش عارف، الصفحة دي ليك. كلام علمي، بالمصري، ومن غير حكم عليك.</p>
      <p class="privacy">🔒 الصفحة مش بتسجل أي حاجة عنك، ومحدش يعرف إنك فتحتها.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <nav class="vchips" aria-label="محتوى الصفحة">{chips}</nav>
      <div class="post-body csbd">

<p>أول حاجة عايز أقولهالك: <strong>انت مش وحش، ومش ضعيف، ومش لوحدك.</strong> ناس كتير جداً، رجالة وستات، من كل الأعمار والخلفيات، بيعانوا من نفس الحاجة وساكتين من الكسوف. والكسوف ده نفسه، زي ما هتشوف تحت، من أكتر الحاجات اللي بتخلي السلوك يكمّل.</p>

<h2 id="what">يعني إيه «إدمان الإباحية» أو «إدمان الجنس»؟</h2>
<p>الكلمة اللي الناس بتستخدمها هي «إدمان». بس الاسم العلمي في التصنيف الدولي للأمراض بتاع منظمة الصحة العالمية (<bdi dir="ltr">ICD-11</bdi>) هو <strong>«اضطراب السلوك الجنسي القهري»</strong>. التصنيف حاطه مع اضطرابات التحكم في الاندفاع، والعلماء لسه بيتناقشوا هل هو «إدمان» بالمعنى الحرفي ولا لأ.</p>
<p>ببساطة: هو <strong>نمط مستمر من عدم القدرة على التحكم في رغبات ودوافع جنسية قوية ومتكررة</strong>، فالشخص يلاقي نفسه بيكرر سلوك جنسي معيّن (زي مشاهدة الإباحية لساعات) لمدة طويلة، غالباً 6 شهور أو أكتر، والموضوع ده بيسبب له ضيق شديد أو بيأثر بشكل واضح على حياته: شغله أو دراسته أو علاقاته أو صحته.</p>

<h2 id="signs">علامات إن الموضوع بقى مشكلة</h2>
<ul>
<li>السلوك بقى <strong>مركز حياتك</strong>، لدرجة إنك بتهمل نومك أو صحتك أو شغلك أو الناس اللي بتحبهم.</li>
<li>حاولت <strong>كذا مرة</strong> تقلل أو تبطّل، ومقدرتش.</li>
<li>بتكمّل <strong>رغم إنك شايف الضرر</strong>: مشاكل في العلاقة، فلوس، كذب، خوف من الفضيحة.</li>
<li>بتكمّل <strong>حتى لما مبقتش بتستمتع</strong>، وبقى أقرب لحاجة لازم تعملها عشان تهدى.</li>
<li>بتحتاج <strong>وقت أطول أو حاجة أكتر</strong> عشان توصل لنفس الإحساس.</li>
<li>بتحس بعدها بـ<strong>ندم وخجل</strong> كبير، وبتخبي الموضوع عن كل الناس.</li>
</ul>
<p class="test-cta">📝 عايز تقيس نفسك؟ جرّب <a href="/tests/porn-use-bps/">اختبار مشاهدة الإباحية (BPS)</a>: 5 أسئلة علمية، والنتيجة بتطلع على جهازك بس.</p>
<p>لو كذا علامة من دول بتنطبق عليك من شهور، ده مش معناه إنك «مريض» بالضرورة. ده معناه إن الموضوع يستاهل تاخده بجد، وإن فيه طرق حقيقية بتساعد.</p>

<h2 id="not">إمتى ميبقاش ده اضطراب؟</h2>
<ul>
<li><strong>الرغبة الجنسية العالية</strong> لوحدها مش مرض، طول ما انت متحكم فيها ومش بتأذيك.</li>
<li><strong>الممارسة الفردية</strong> لوحدها مش مرض من الناحية الطبية. اللي بيفرق هو فقدان التحكم والضرر.</li>
<li><strong>الإحساس بالذنب بسبب قيمك أو دينك</strong> لوحده مش كفاية عشان نسميه اضطراب، والتصنيف الدولي بيقول كده صراحة. ده إحساس حقيقي ومحترم، بس ليه كلام تاني: الحكم الديني تسأل فيه رجل دين تثق فيه، والمعالج يساعدك تتصالح مع قيمك من غير جلد للذات.</li>
</ul>

<h2 id="why">ليه بيحصل؟</h2>
<p>مفيش سبب واحد، بس فيه حاجات بتتكرر كتير:</p>
<ul>
<li><strong>هروب من مشاعر صعبة:</strong> عند ناس كتير، السلوك ده مش عن الجنس أصلاً، هو طريقة سريعة يهربوا بيها من الوحدة أو القلق أو الضغط أو الملل أو الحزن. بيدّي راحة مؤقتة، وبعدها المشاعر بترجع أتقل.</li>
<li><strong>دماغ بيتعلم بسرعة:</strong> المخ بيحب أي حاجة بتدّي مكافأة فورية. ومع التكرار، السلوك بيبقى عادة أوتوماتيك بتشتغل لوحدها في مواقف معيّنة (زي الموبايل في السرير بالليل).</li>
<li><strong>سهولة الوصول:</strong> المحتوى موجود 24 ساعة، ببلاش، ومن غير ما حد يعرف. ده بيخلي الوقوع أسهل كتير من أي وقت فات.</li>
<li><strong>حاجات تانية ممكن تكون معاه:</strong> ساعات بيبقى فيه اكتئاب أو قلق أو تشتت انتباه، أو تجارب صعبة في الطفولة. ولما الحاجات دي تتعالج، السلوك بيبقى أسهل في التحكم.</li>
</ul>

<h2 id="cycle">الدايرة اللي بتتكرر</h2>
<ol class="cycle">
<li><b>محفّز</b><span>زهق، وحدة، خناقة، تعب، موبايل في السرير</span></li>
<li><b>رغبة قوية</b><span>«مرة واحدة بس»</span></li>
<li><b>السلوك</b><span>غالباً أطول من اللي كنت ناويه</span></li>
<li><b>راحة مؤقتة</b><span>دقايق</span></li>
<li><b>ندم وخجل</b><span>«أنا وحش، مفيش فايدة»</span></li>
<li><b>ضغط ومشاعر أصعب</b><span>وده نفسه بيبقى محفّز جديد ←</span></li>
</ol>
<p>عشان كده <strong>جلد الذات مش بيساعد</strong>، بالعكس، بيقفل الدايرة. التعافي بيبدأ لما تفهم الدايرة بتاعتك وتكسرها من أكتر من نقطة.</p>

<h2 id="steps">خطوات عملية للتعافي</h2>
<p><strong>١. اعرف محفّزاتك.</strong> لمدة أسبوع، كل ما تحس بالرغبة، اكتب: الساعة كام؟ كنت فين؟ حاسس بإيه؟ هتلاقي نمط. فيه اختصار مشهور بيساعد: لما الرغبة تيجي، اسأل نفسك هل أنا <strong>جعان، متضايق، وحيد، ولا تعبان؟</strong> غالباً الإجابة واحدة من دول، والحل يبقى للاحتياج ده، مش للسلوك.</p>
<p><strong>٢. صعّب الوصول.</strong> مش عشان انت ضعيف، عشان كل خطوة زيادة بتدّي دماغك فرصة يفكر. استخدم برامج حجب المحتوى، وطلّع الموبايل من أوضة النوم بالليل، وقلل الوقت لوحدك مع الأجهزة في الأوقات اللي بتقع فيها.</p>
<p><strong>٣. «اركب الموجة».</strong> الرغبة زي الموجة: بتعلى، وبتوصل لقمتها، وبعدين بتهدى لوحدها لو مسبتهاش تتحكم فيك. لما تيجي، أجّل 15 دقيقة، وقوم من مكانك، واعمل حاجة بجسمك: مشي، دش، تمرين، كوباية مية. ولاحظ الإحساس من غير ما تنفذه.</p>
<p><strong>٤. اتعامل مع الشعور الحقيقي.</strong> لو وحيد، كلّم صاحب. لو مضغوط، اتنفس ببطء أو اكتب اللي مضايقك. لو زهقان، خلّي عندك قايمة حاجات بتحبها تعملها. السلوك كان بيحل مشكلة غلط، فلازم تلاقي حل صح للمشكلة الأصلية.</p>
<p><strong>٥. متبقاش لوحدك.</strong> السر بيقوّي الدايرة. قول لشخص واحد تثق فيه، أو لمعالج، أو انضم لمجموعة دعم. مجرد إنك تتكلم بيقلل الخجل كتير.</p>
<p><strong>٦. ابني حياة تستاهل.</strong> نوم كفاية، رياضة، علاقات حقيقية، هدف بتشتغل عليه. كل ما حياتك يبقى فيها معنى ومصادر راحة تانية، السلوك ده بيقل احتياجك ليه.</p>

<div class="exercise"><p class="exercise-title">تمرين النهارده: خريطة صغيرة</p>
<p>هات ورقة واكتب 3 أعمدة: <strong>المحفّز</strong> (إيه اللي حصل قبلها؟)، <strong>الإحساس</strong> (كنت حاسس بإيه؟)، <strong>البديل</strong> (إيه الحاجة اللي ممكن تعملها المرة الجاية بدل السلوك؟). املاها لآخر 3 مرات تفتكرها. الهدف مش إنك تحاسب نفسك، الهدف إنك تشوف الخريطة.</p>
<p>وعايز النسخة الكاملة؟ حمّل <a href="/worksheets/#triggers-map">ورقة «خريطة المحفّزات»</a> واطبعها، وابدأ معاها <a href="/challenges/#urge-awareness">تحدّي «7 أيام وعي»</a>.</p></div>

<h2 id="relapse">لو وقعت تاني</h2>
<p>ده بيحصل لناس كتير في رحلة التعافي، ومش معناه إنك فشلت. أخطر حاجة بعد الوقوع هي فكرة <strong>«خلاص باظت، يبقى أكمّل»</strong>. الفكرة دي بتحوّل مرة واحدة لأسبوع.</p>
<p>بدل كده: وقّف، واسأل نفسك بهدوء إيه اللي حصل قبلها؟ وإيه اللي هتغيّره المرة الجاية؟ وبعدين ارجع لخطتك. التعافي مش خط مستقيم، هو اتجاه عام للأحسن.</p>

<h2 id="partner">لو انت شريك أو شريكة حياة حد بيعاني من ده</h2>
<p>إحساسك بالخيانة أو الجرح أو إنك «مش كفاية» إحساس حقيقي ومفهوم. بس اعرف إن السلوك ده <strong>مش بسببك</strong>، ومش مقياس لقيمتك أو جمالك. انت كمان محتاج دعم، مش بس هو. العلاج الزوجي مع متخصص ممكن يساعدكم تتكلموا بأمان وتبنوا الثقة من جديد، لو الاتنين عايزين كده.</p>

<h2 id="help">إمتى تكلّم متخصص؟</h2>
<ul>
<li>لو حاولت كذا مرة بجد ومقدرتش تبطّل لوحدك.</li>
<li>لو الموضوع بيأثر على شغلك أو علاقتك أو فلوسك، أو بتكذب عشان تخبيه.</li>
<li>لو فيه اكتئاب أو قلق شديد أو إحساس دايم بالفراغ.</li>
<li>لو السلوك فيه مخاطرة على صحتك، زي علاقات مش آمنة. هنا كمان اعمل الكشف والتحاليل اللازمة عند دكتور.</li>
</ul>
<p><strong>العلاج المعرفي السلوكي</strong> و<strong>علاج القبول والالتزام</strong> من أكتر الطرق اللي بتساعد. وفيه حالات دكتور نفسي بيقرر فيها علاج دوائي، وده <strong>بيتاخد بس تحت إشراف دكتور</strong>، ومتاخدش أي دوا من نفسك.</p>
<p>ولو حابب تتكلم مع متخصص، أنا بقدّم <a href="/sessions/">جلسات نفسية أونلاين لأهلنا في مصر والوطن العربي</a>، وكل اللي بيتقال فيها سري.</p>
<p class="safety"><strong>وقفة أمان:</strong> لو عندك أفكار تأذي بيها نفسك، كلّم حد فوراً: مصر <a href="tel:16328">16328</a> · أمريكا <a href="tel:988">988</a>. ولو عندك أي أفكار أو رغبات ناحية أطفال، حتى لو عمرك ما عملت حاجة، اطلب مساعدة متخصصة سرية فوراً. فيه جهات متخصصة في ده زي <a href="https://www.stopitnow.org/" target="_blank" rel="noopener">Stop It Now</a>.</p>
      </div>

      <h2 class="sec-h">ممكن يفيدك كمان</h2>
      <ul class="link-grid">
        <li><a href="/tests/porn-use-bps/"><b>اختبار مشاهدة الإباحية (BPS)</b><span>5 أسئلة علمية، والنتيجة فوراً.</span></a></li>
        <li><a href="/worksheets/#triggers-map"><b>ورقة تمرين: خريطة المحفّزات</b><span>PDF مجاني تطبعه وتملاه أسبوع.</span></a></li>
        <li><a href="/challenges/#urge-awareness"><b>تحدّي: 7 أيام وعي</b><span>مهمة صغيرة كل يوم، وتقدّمك بيتحفظ على جهازك.</span></a></li>
        <li><a href="/questions/#porn"><b>«مش قادر أبطّل أتفرج… ده إدمان؟»</b><span>من قسم أسئلة محرجة وإجابات علمية.</span></a></li>
        <li><a href="/tests/anxiety-gad7/"><b>اختبار القلق (GAD-7)</b><span>القلق من أكتر المحفّزات اللي ورا السلوك ده.</span></a></li>
        <li><a href="/tests/depression-phq8/"><b>اختبار الاكتئاب (PHQ-8)</b><span>لو حاسس بفراغ أو حزن مستمر.</span></a></li>
        <li><a href="/challenges/"><b>تحديات قصيرة</b><span>عادات صغيرة بتبني حياة أهدى.</span></a></li>
      </ul>
      <div class="safety-note" role="note">
        <p><b>تنبيه:</b> الصفحة دي للتوعية وفهم النفس، ومش تشخيص ولا بديل عن العلاج النفسي مع متخصص.</p>
      </div>
      {ba.share_block(SITE + "/porn-addiction/", "التعافي من إدمان الإباحية والسلوك الجنسي القهري — د. ميلاد ميخائيل", "ابعتها لحد ممكن يحتاجها")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "MedicalWebPage", "inLanguage": "ar", "url": f"{SITE}/porn-addiction/",
          "name": "التعافي من إدمان الإباحية والسلوك الجنسي القهري",
          "author": {"@id": f"{SITE}/#person", "@type": "Person", "name": "Dr. Millad Mikhail"},
          "audience": {"@type": "PeopleAudience", "suggestedMinAge": 18},
          "about": {"@type": "MedicalCondition", "name": "Compulsive sexual behaviour disorder",
                    "alternateName": ["اضطراب السلوك الجنسي القهري", "إدمان الإباحية", "إدمان الجنس"],
                    "code": {"@type": "MedicalCode", "code": "6C72", "codingSystem": "ICD-11"}},
          "datePublished": "2026-11-05"}
    write("porn-addiction", page("porn-addiction", "التعافي من إدمان الإباحية والسلوك الجنسي القهري",
                                  "إدمان الإباحية والسلوك الجنسي القهري: يعني إيه، علاماته، ليه بيحصل، وخطوات عملية للتعافي ولو وقعت تاني، بالمصري ومن غير حكم.", body, ld))


def main():
    import pages_trust
    pages_trust.build_all(ba, page, write, SITE)
    import build_extras
    build_extras.build_all(ba, page, write, SITE)
    import build_partner_series
    build_partner_series.build_all(ba, page, write, SITE)
    import build_newsletter
    build_newsletter.build_all(ba, page, write, SITE)
    ask_page()
    feelings_page()
    relationship_check_page()
    worksheets_page()
    questions_page()
    csbd_page()
    challenges_page()
    import build_glossary
    build_glossary.build()
    start_page()
    book_page()
    battery_page()
    print("pages: exercise, stories, shelf, sessions, contact, help-now, privacy, terms, feelings, relationship-check, worksheets, questions, porn-addiction, challenges, start, book, battery")


if __name__ == "__main__":
    main()
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "add_analytics.py")], check=True)
