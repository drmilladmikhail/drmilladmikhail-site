#!/usr/bin/env python3
"""Build the self-assessment tests section (/tests/) of drmilladmikhail.com.

All scoring happens in the visitor's browser (assets/quiz.js); nothing is sent or stored.
Run:  python3 tools/build_tests.py   (then python3 tools/build_articles.py to refresh sitemap)
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://drmilladmikhail.com"
BOOK_AR = "https://www.amazon.com/dp/B0HPNCYWWS"

FREQ4 = [("خالص", 0), ("كام يوم", 1), ("أكتر من نص الأيام", 2), ("تقريباً كل يوم", 3)]
AGREE4 = [("موافق جداً", 3), ("موافق", 2), ("مش موافق", 1), ("مش موافق خالص", 0)]
AGREE7 = [("مش موافق خالص", 1), ("مش موافق", 2), ("مش موافق شوية", 3), ("محايد", 4),
          ("موافق شوية", 5), ("موافق", 6), ("موافق جداً", 7)]
WHO5 = [("طول الوقت", 5), ("معظم الوقت", 4), ("أكتر من نص الوقت", 3),
        ("أقل من نص الوقت", 2), ("أحياناً", 1), ("ولا مرة", 0)]

SAFETY = ("لو عندك أفكار إنك تأذي نفسك أو إن الحياة مالهاش لازمة، متستناش: كلّم حد بتثق فيه دلوقتي، "
          "أو اتصل بالخط الساخن للدعم النفسي في مصر <strong>105</strong>، أو في أمريكا اتصل أو ابعت رسالة على "
          "<strong>988</strong>، أو روح أقرب طوارئ.")

TESTS = [
    {
        "slug": "attachment-style",
        "title": "اختبار نمط التعلق: انت آمن ولا قلقان ولا متجنب؟",
        "short": "نمط التعلق",
        "description": "اختبار علمي قصير (مقياس ECR-RS) من 9 أسئلة يقيس قلق التعلق وتجنب التعلق، ويقولك نمطك أقرب لأنهي نوع من الأنماط الأربعة.",
        "icon": "attach",
        "minutes": 2,
        "kind": "ecr",
        "intro": "فكّر في علاقاتك القريبة بشكل عام (شريك الحياة، الأهل، الصحاب المقربين)، وقول لنفسك قد إيه كل جملة بتنطبق عليك.",
        "options": AGREE7,
        "items": [
            ("بيريحني إني ألجأ للناس القريبين مني وقت ما أحتاجهم.", "avoid", True),
            ("عادةً بتكلم مع الناس القريبين مني عن مشاكلي وهمومي.", "avoid", True),
            ("بتناقش في أموري مع الناس القريبين مني.", "avoid", True),
            ("سهل عليا أعتمد على الناس القريبين مني.", "avoid", True),
            ("مش بكون مرتاح إني أفتح قلبي للناس القريبين مني.", "avoid", False),
            ("بفضّل مأوريش الناس القريبين مني أنا حاسس بإيه من جوايا.", "avoid", False),
            ("كتير بقلق إن الناس القريبين مني مش مهتمين بيا بجد.", "anx", False),
            ("بخاف إن الناس القريبين مني يسيبوني.", "anx", False),
            ("بقلق إن الناس القريبين مني مش هيهتموا بيا قد ما أنا بهتم بيهم.", "anx", False),
        ],
        "styles": {
            "secure": ["النمط الآمن", "غالباً بتبقى مرتاح في القرب ومش بتخاف من البعد. بتقدر تطلب اللي محتاجه، وتسمع غيرك من غير ما تحس إنك متهاجم."],
            "anxious": ["النمط القلقان", "غالباً بتحتاج طمأنة كتير، وبتخاف إن اللي بتحبه يسيبك، وممكن تقرا أي تأخير في الرد على إنه رفض."],
            "avoidant": ["النمط المتجنب", "غالباً بتحب استقلاليتك جداً، ولما حد يقرب أوي بتحس إنك متخنق وتبعد، ومش سهل عليك تتكلم عن مشاعرك."],
            "fearful": ["النمط الخايف المتجنب", "غالباً عايز القرب جداً وخايف منه في نفس الوقت، فبتقرب وتبعد، وعلاقاتك ممكن يكون فيها تقلبات."],
        },
        "source": "Fraley, R. C., Heffernan, M. E., Vicary, A. M., & Brumbaugh, C. C. (2011). The Experiences in Close Relationships—Relationship Structures questionnaire. <em>Psychological Assessment, 23</em>(3), 615–625. (الصيغة العامة للعلاقات القريبة، 9 بنود، مقياس من 1 لـ 7)",
        "note": "الدرجات بتتحسب زي المقياس الأصلي (متوسط من 1 لـ 7). المقياس مش بيحط حدود رسمية للأنماط؛ إحنا بنستخدم نص المقياس (4) عشان نقولك نمطك <em>أقرب</em> لأنهي نوع، فاعتبرها علامة مش حكم.",
        "related": ("/articles/why-we-choose-the-same-person/", "ليه بتختار نفس الشخص كل مرة؟"),
        "safety": False,
    },
    {
        "slug": "depression-phq8",
        "title": "اختبار الاكتئاب (PHQ-8): مزاجك عامل إيه آخر أسبوعين؟",
        "short": "الاكتئاب",
        "description": "مقياس PHQ-8 العالمي من 8 أسئلة لقياس شدة أعراض الاكتئاب في آخر أسبوعين، والنتيجة بتطلع فوراً.",
        "icon": "cloud",
        "minutes": 2,
        "kind": "sum",
        "intro": "في آخر أسبوعين، قد إيه ضايقتك الحاجات دي؟",
        "options": FREQ4,
        "items": [
            "قلة الاهتمام أو المتعة في عمل الحاجات",
            "الإحساس بالضيق أو الاكتئاب أو اليأس",
            "صعوبة إنك تنام أو تكمّل نومك، أو إنك بتنام أكتر من اللازم",
            "الإحساس بالتعب أو قلة الطاقة",
            "ضعف الشهية أو الأكل أكتر من اللازم",
            "الإحساس إنك وحش في نظر نفسك، أو إنك فاشل، أو إنك خذلت نفسك أو عيلتك",
            "صعوبة في التركيز على حاجات زي القراءة أو مشاهدة التلفزيون",
            "إنك بتتحرك أو بتتكلم ببطء لدرجة إن اللي حواليك لاحظوا، أو العكس: متوتر ومش مستقر وبتتحرك أكتر من العادي",
        ],
        "max": 24,
        "bands": [
            [0, 4, "مفيش أعراض تُذكر", "نتيجتك في المدى الطبيعي. كمّل في الحاجات اللي بتحافظ على مزاجك."],
            [5, 9, "أعراض بسيطة", "فيه أعراض بسيطة. راقب مزاجك الأسابيع الجاية، واهتم بنومك وحركتك وعلاقاتك."],
            [10, 14, "أعراض متوسطة", "الدرجة دي بتستاهل إنك تتكلم مع متخصص نفسي أو دكتور يقيّم حالتك."],
            [15, 19, "أعراض متوسطة لشديدة", "الأعراض واضحة. يُفضّل جداً إنك تتواصل مع متخصص نفسي قريب.", True],
            [20, 24, "أعراض شديدة", "الأعراض شديدة. مهم إنك تطلب مساعدة متخصص في أقرب وقت.", True],
        ],
        "source": "Kroenke, K., Strine, T. W., Spitzer, R. L., Williams, J. B., Berry, J. T., & Mokdad, A. H. (2009). The PHQ-8 as a measure of current depression in the general population. <em>Journal of Affective Disorders, 114</em>, 163–173. (استبيان PHQ من تطوير Spitzer وWilliams وKroenke، ومتاح للاستخدام من غير إذن)",
        "note": "استخدمنا نسخة PHQ-8 (من غير سؤال الأفكار الانتحارية الموجود في PHQ-9) لأنها النسخة المعتمدة للاستخدام العام من غير متابعة مباشرة.",
        "related": None,
        "safety": True,
    },
    {
        "slug": "anxiety-gad7",
        "title": "اختبار القلق (GAD-7): قلقك طبيعي ولا زيادة؟",
        "short": "القلق",
        "description": "مقياس GAD-7 العالمي من 7 أسئلة لقياس شدة أعراض القلق العام في آخر أسبوعين.",
        "icon": "wave",
        "minutes": 2,
        "kind": "sum",
        "intro": "في آخر أسبوعين، قد إيه ضايقتك الحاجات دي؟",
        "options": FREQ4,
        "items": [
            "الإحساس بالعصبية أو القلق أو إنك على أعصابك",
            "إنك مش قادر توقف القلق أو تتحكم فيه",
            "القلق الزيادة على حاجات كتير مختلفة",
            "صعوبة إنك تسترخي",
            "التوتر لدرجة إنه صعب تقعد في مكانك",
            "إنك بتتضايق أو بتتعصب بسهولة",
            "الإحساس بالخوف كأن حاجة وحشة هتحصل",
        ],
        "max": 21,
        "bands": [
            [0, 4, "قلق بسيط جداً", "نتيجتك في المدى الطبيعي."],
            [5, 9, "قلق بسيط", "فيه قلق بسيط. تمارين التنفس والنوم المنتظم والحركة ممكن تساعدك."],
            [10, 14, "قلق متوسط", "الدرجة دي بتستاهل إنك تتكلم مع متخصص نفسي يقيّم حالتك."],
            [15, 21, "قلق شديد", "القلق واضح وشديد. يُفضّل جداً إنك تتواصل مع متخصص نفسي.", True],
        ],
        "source": "Spitzer, R. L., Kroenke, K., Williams, J. B. W., & Löwe, B. (2006). A brief measure for assessing generalized anxiety disorder: The GAD-7. <em>Archives of Internal Medicine, 166</em>(10), 1092–1097. (متاح للاستخدام من غير إذن)",
        "note": "",
        "related": None,
        "safety": True,
    },
    {
        "slug": "self-esteem-rosenberg",
        "title": "اختبار تقدير الذات (روزنبرج): انت شايف نفسك إزاي؟",
        "short": "تقدير الذات",
        "description": "مقياس روزنبرج لتقدير الذات، أشهر مقياس في العالم لتقدير الذات، من 10 جمل.",
        "icon": "mirror",
        "minutes": 2,
        "kind": "sum",
        "intro": "قد إيه انت موافق على كل جملة من دول عن نفسك؟",
        "options": AGREE4,
        "reverse": [2, 5, 6, 8, 9],
        "items": [
            "بشكل عام، أنا راضي عن نفسي.",
            "ساعات بحس إني مش كويس خالص.",
            "بحس إن فيا صفات حلوة كتير.",
            "أقدر أعمل الحاجات كويس زي معظم الناس.",
            "بحس إن مفيش حاجات كتير أفتخر بيها.",
            "أكيد ساعات بحس إني ماليش لازمة.",
            "بحس إني شخص ليه قيمة، على الأقل زي الناس التانية.",
            "نفسي أحترم نفسي أكتر من كده.",
            "في الآخر، بميل إني أحس إني فاشل.",
            "عندي نظرة إيجابية لنفسي.",
        ],
        "max": 30,
        "bands": [
            [0, 14, "تقدير ذات منخفض", "صورتك عن نفسك محتاجة اهتمام. ده مش عيب فيك، ده حاجة اتعلمناها وممكن تتغير، والكلام مع متخصص بيساعد."],
            [15, 25, "تقدير ذات في المدى الطبيعي", "صورتك عن نفسك متوازنة في أغلبها."],
            [26, 30, "تقدير ذات عالي", "عندك نظرة قوية وإيجابية لنفسك."],
        ],
        "source": "Rosenberg, M. (1965). <em>Society and the adolescent self-image</em>. Princeton University Press. (متاح للاستخدام التعليمي والبحثي)",
        "note": "الجمل رقم 2 و5 و6 و8 و9 بتتحسب بالعكس زي المقياس الأصلي. الحد بين المنخفض والطبيعي (15) هو الأكثر استخداماً في الأبحاث، ومش حد تشخيصي.",
        "related": ("/articles/why-we-choose-the-same-person/", "صورتك عن نفسك هي اللي بتختارلك"),
        "safety": False,
    },
    {
        "slug": "wellbeing-who5",
        "title": "مؤشر الرفاهية النفسية (WHO-5) من منظمة الصحة العالمية",
        "short": "الرفاهية النفسية",
        "description": "مؤشر WHO-5 من منظمة الصحة العالمية: 5 أسئلة سريعة تقيس حالتك النفسية العامة في آخر أسبوعين، من 0 لـ 100.",
        "icon": "sun",
        "minutes": 1,
        "kind": "sum",
        "multiplier": 4,
        "intro": "في آخر أسبوعين، قد إيه الجمل دي كانت بتوصف حالك؟",
        "options": WHO5,
        "items": [
            "كنت مبسوط ومزاجي حلو.",
            "كنت هادي ومرتاح.",
            "كنت نشيط وعندي طاقة.",
            "كنت بصحى حاسس إني فايق ومرتاح.",
            "يومي كان مليان بحاجات بتهمني.",
        ],
        "max": 100,
        "bands": [
            [0, 28, "رفاهية نفسية منخفضة جداً", "الدرجة دي بتستاهل جداً إنك تتكلم مع متخصص نفسي يقيّم حالتك، لأنها ممكن تكون علامة على اكتئاب.", True],
            [29, 50, "رفاهية نفسية منخفضة", "حالتك النفسية مش في أحسن أحوالها. ممكن تعمل اختبار الاكتئاب (PHQ-8)، ولو الحال استمر كلّم متخصص."],
            [51, 100, "رفاهية نفسية كويسة", "حالتك النفسية العامة في المدى الكويس."],
        ],
        "source": "Topp, C. W., Østergaard, S. D., Søndergaard, S., & Bech, P. (2015). The WHO-5 Well-Being Index: A systematic review of the literature. <em>Psychotherapy and Psychosomatics, 84</em>(3), 167–176. (WHO Collaborating Centre in Mental Health، 1998)",
        "note": "الدرجة الخام (من 0 لـ 25) بتتضرب في 4 عشان تبقى من 0 لـ 100، زي الطريقة الرسمية.",
        "related": None,
        "safety": True,
    },
]

ICONS = {
    "attach": '<circle cx="15" cy="20" r="8"/><circle cx="25" cy="20" r="8"/>',
    "cloud": '<path d="M12 27h16a6 6 0 0 0 0-12 9 9 0 0 0-17 2 5 5 0 0 0 1 10Z"/><path d="M15 31v3M21 31v3M27 31v3"/>',
    "wave": '<path d="M5 16c4-4 8-4 12 0s8 4 12 0 5-2 6-1M5 25c4-4 8-4 12 0s8 4 12 0 5-2 6-1"/>',
    "mirror": '<ellipse cx="20" cy="17" rx="9" ry="12"/><path d="M20 29v6M14 35h12M16 12c1-2 3-3 5-3"/>',
    "sun": '<circle cx="20" cy="20" r="6"/><path d="M20 5v4M20 31v4M5 20h4M31 20h4M9 9l3 3M28 28l3 3M31 9l-3 3M12 28l-3 3"/>',
}


def esc(s):
    return html.escape(s, quote=True)


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 40 40" aria-hidden="true">{ICONS[name]}</svg>'


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=Noto+Naskh+Arabic:wght@600;700'
         '&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;1,6..72,500&display=swap" rel="stylesheet">\n'
         '<link rel="stylesheet" href="/assets/site.css">')

TOPBAR = '''<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/">د. ميلاد منير ميخائيل</a>
    <nav class="nav" aria-label="أقسام الموقع">
      <a href="/articles/">المقالات</a>
      <a href="/tests/">اختبارات نفسية</a>
      <a href="/#book">الكتب</a>
      <a href="/#about">نبذة</a>
      <a href="/#credentials">المؤهلات</a>
      <a class="lang" href="/en/" hreflang="en" lang="en">English</a>
    </nav>
    <details class="menu">
      <summary aria-label="القائمة"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
      <nav aria-label="القائمة">
        <a href="/articles/">المقالات</a>
        <a href="/tests/">اختبارات نفسية</a>
        <a href="/#book">الكتب</a>
        <a href="/#about">نبذة</a>
        <a href="/#credentials">المؤهلات</a>
        <a href="https://blog.drmilladmikhail.com/">المدونة</a>
        <a href="/en/" hreflang="en" lang="en">English</a>
      </nav>
    </details>
  </div>
</header>'''

FOOTER = '''<footer class="footer">
  <div class="wrap footer-grid">
    <div>
      <p class="names">د. ميلاد منير ميخائيل <span lang="en" dir="ltr">· Dr. Millad Mikhail</span></p>
      <p>حاصل على الدكتوراه في الصحة النفسية من جامعة قناة السويس، وعضو الجمعية الأمريكية لعلم النفس (APA).</p>
      <p class="fine">© 2026. الاختبارات للتوعية وفهم النفس، ومش تشخيص ولا بديل عن تقييم متخصص.</p>
    </div>
    <div>
      <h2>اقرأ وجرّب</h2>
      <ul>
        <li><a href="/articles/">المقالات</a></li>
        <li><a href="/tests/">اختبارات نفسية</a></li>
        <li><a href="/#book">الكتب</a></li>
        <li><a href="https://blog.drmilladmikhail.com/" target="_blank" rel="noopener">المدونة</a></li>
      </ul>
    </div>
    <div>
      <h2>تابعني</h2>
      <ul>
        <li><a href="https://www.youtube.com/@DrMilladMikhail" target="_blank" rel="noopener">يوتيوب</a></li>
        <li><a href="https://www.amazon.com/author/drmilladmikhail" target="_blank" rel="noopener">أمازون</a></li>
        <li><a href="https://www.linkedin.com/in/dr-millad-mikhail-a57b0b215" target="_blank" rel="noopener">LinkedIn</a></li>
        <li><a href="https://orcid.org/0009-0002-9254-367X" target="_blank" rel="me noopener">ORCID</a></li>
        <li><a href="/en/" hreflang="en" lang="en">English</a></li>
      </ul>
    </div>
  </div>
</footer>'''


def head(title, desc, url, ld):
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | د. ميلاد ميخائيل</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:site_name" content="د. ميلاد منير ميخائيل">
<meta property="og:image" content="{SITE}/assets/og/tests.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og/tests.jpg">
<meta property="og:locale" content="ar_EG">
<meta name="theme-color" content="#2f6f62">
{FONTS}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{TOPBAR}
<main>'''


def test_page(t):
    url = f"{SITE}/tests/{t['slug']}/"
    rev = set(t.get("reverse", []))
    qs = []
    for i, item in enumerate(t["items"], start=1):
        if t["kind"] == "ecr":
            text, sub, r = item
            attrs = f' data-sub="{sub}" data-rev="{1 if r else 0}"'
        else:
            text, attrs = item, ""
        opts = []
        n = len(t["options"])
        for label, val in t["options"]:
            v = (n - 1) - val if (i in rev) else val  # reverse-keyed items (Rosenberg)
            opts.append(f'<label class="opt"><input type="radio" name="q{i}" value="{v}" required><span>{esc(label)}</span></label>')
        qs.append(f'''<fieldset class="q"{attrs}>
          <legend><span class="qn">{i}</span> {esc(text)}</legend>
          <div class="opts opts-{n}">{"".join(opts)}</div>
        </fieldset>''')
    cfg = {"kind": t["kind"], "max": t.get("max"), "multiplier": t.get("multiplier", 1),
           "bands": t.get("bands"), "styles": t.get("styles"), "safety": t["safety"]}
    related = ""
    if t.get("related"):
        related = f'<p class="related">اقرأ كمان: <a href="{t["related"][0]}">{esc(t["related"][1])}</a></p>'
    safety_block = f'<p class="safety test-safety">{SAFETY}</p>' if t["safety"] else ""
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": t["title"], "description": t["description"],
          "url": url, "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    return head(t["title"], t["description"], url, ld) + f'''
  <section class="section test">
    <div class="wrap narrow">
      <p class="crumbs"><a href="/tests/">اختبارات نفسية</a> · {t["minutes"]} دقيقة تقريباً</p>
      <h1>{esc(t["title"])}</h1>
      <p class="test-intro">{esc(t["intro"])}</p>
      <p class="privacy">🔒 إجاباتك بتتحسب على جهازك بس، ومش بتتبعت أو تتحفظ في أي مكان.</p>
      <form id="quiz" novalidate>
        {"".join(qs)}
        <p class="quiz-error" hidden>جاوب على كل الأسئلة الأول عشان تطلع النتيجة.</p>
        <button class="btn primary big" type="submit">اعرض النتيجة</button>
      </form>
      <div id="result" class="result" hidden tabindex="-1" aria-live="polite"></div>
      {safety_block}
      <details class="about-test">
        <summary>عن المقياس ده ومصدره العلمي</summary>
        <p>{t["source"]}</p>
        {f"<p>{t['note']}</p>" if t["note"] else ""}
        <p>الترجمة العربية مبسّطة لأغراض التوعية، ومش النسخة العربية المقننة رسمياً، فالنتيجة تقريبية. الاختبار ده أداة تساعدك تفهم نفسك، ومش تشخيص. التشخيص بيكون بس من متخصص بعد تقييم كامل.</p>
      </details>
      {related}
      <aside class="book-box">
        <picture class="cover-img">
          <source srcset="/assets/love-cover-ar.webp" type="image/webp">
          <img src="/assets/love-cover-ar.jpg" width="480" height="768" alt="غلاف كتاب ليه بنحب اللي بيوجعنا؟" loading="lazy">
        </picture>
        <div>
          <p class="book-box-title">عايز تفهم نفسك وعلاقاتك أكتر؟</p>
          <p>كتاب «ليه بنحب اللي بيوجعنا؟» دليل عملي فيه تمارين واختبارات عن نمط التعلق واختيار شريك الحياة.</p>
          <div class="actions"><a class="btn primary" href="{BOOK_AR}" target="_blank" rel="noopener">اقرأ الكتاب على أمازون</a></div>
        </div>
      </aside>
      <p class="more-tests"><a class="btn" href="/tests/">جرّب اختبارات تانية</a></p>
    </div>
  </section>
</main>
{FOOTER}
<script type="application/json" id="quiz-config">{json.dumps(cfg, ensure_ascii=False)}</script>
<script src="/assets/quiz.js" defer></script>
<script src="/assets/helper.js" defer></script>
</body>
</html>
'''


def index_page():
    cards = []
    for t in TESTS:
        cards.append(f'''<li class="test-card">
        <a href="/tests/{t["slug"]}/">
          {icon(t["icon"])}
          <span class="tc-body">
            <h2>{esc(t["short"])}</h2>
            <span class="card-desc">{esc(t["description"])}</span>
            <span class="card-date">{len(t["items"])} أسئلة · {t["minutes"]} دقيقة</span>
          </span>
        </a>
      </li>''')
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "اختبارات نفسية مجانية",
          "url": f"{SITE}/tests/", "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}}
    return head("اختبارات نفسية مجانية بالعربي", "اختبارات نفسية علمية مجانية بالعربي: نمط التعلق، الاكتئاب، القلق، تقدير الذات، والرفاهية النفسية. النتيجة بتطلع فوراً.", f"{SITE}/tests/", ld) + f'''
  <section class="section articles-index">
    <div class="wrap">
      <h1>اختبارات نفسية</h1>
      <p class="section-intro">مقاييس علمية معروفة ومستخدمة في الأبحاث حول العالم، مترجمة بالعربي البسيط. النتيجة بتطلع فوراً، وإجاباتك مش بتتحفظ في أي مكان. الاختبارات دي للتوعية، ومش تشخيص.</p>
      <ul class="cards">
      {"".join(cards)}
      </ul>
    </div>
  </section>
</main>
{FOOTER}
<script src="/assets/helper.js" defer></script>
</body>
</html>
'''


def main():
    os.makedirs(os.path.join(ROOT, "tests"), exist_ok=True)
    for t in TESTS:
        d = os.path.join(ROOT, "tests", t["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(test_page(t))
    with open(os.path.join(ROOT, "tests", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page())
    with open(os.path.join(ROOT, "tests", "tests.json"), "w", encoding="utf-8") as f:
        json.dump([{"slug": t["slug"], "title": t["title"]} for t in TESTS], f, ensure_ascii=False, indent=2)
    print("built tests:", ", ".join(t["slug"] for t in TESTS))


if __name__ == "__main__":
    main()
