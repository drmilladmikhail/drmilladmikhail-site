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
<title>{esc(title)} | د. ميلاد منير ميخائيل</title>
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
    for slug, label, note in (("glossary", "القاموس النفسي", "مصطلحات نفسية بشرح بسيط بالمصري."),
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
      <aside class="safety-note">
        <p><b>لو حاسس إنك مش بخير دلوقتي:</b> الموقع ده للتوعية ومش بديل عن متخصص. لو عندك أفكار تأذي بيها نفسك أو حاسس إنك في خطر، كلّم حد فورًا: مصر <a href="tel:105">105</a> (الخط الساخن للدعم النفسي) · أمريكا <a href="tel:988">988</a>.</p>
      </aside>
      {ba.share_block(SITE + "/start/", "مكتبة مجانية بالعربي عن الحب والتعلق والصحة النفسية — د. ميلاد ميخائيل", "شارك الموقع")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "ابدأ من هنا", "url": f"{SITE}/start/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "description": "دليل لكل المحتوى المجاني على موقع د. ميلاد منير ميخائيل: اختبارات ومقالات وفيديوهات."}
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


def main():
    start_page()
    book_page()
    battery_page()
    print("pages: start, book, battery")


if __name__ == "__main__":
    main()
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "add_analytics.py")], check=True)
