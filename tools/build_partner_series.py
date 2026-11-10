#!/usr/bin/env python3
"""/partner/ — hub of the series «شريكي محيّرني» + the behaviour checklist
«إيه اللي بيتعبك في علاقتك؟» (content/partner-check.json, assets/partner-check.js).

Called by tools/build_pages.py (build_all). The checklist is about BEHAVIOURS and never
labels the partner («نرجسي» / «مريض نفسي») — keep it that way.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERIES = [
    "dealing-with-narcissistic-partner",
    "dealing-with-jealous-partner",
    "dealing-with-stingy-partner",
    "emotionally-abusive-partner",
    "partner-with-depression",
    "partner-with-addiction",
    "dealing-with-angry-partner",
    "dealing-with-lying-partner",
    "family-interference-marriage",
    "partner-with-anxiety-ocd",
]
TOOLS = ["emotional-communication-couples", "couples-counseling"]
ORD = ["١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩", "١٠"]


def build_all(ba, page, write, SITE):
    esc = ba.esc
    with open(os.path.join(ROOT, "content", "partner-check.json"), encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(ROOT, "articles", "articles.json"), encoding="utf-8") as f:
        arts = {a["slug"]: a for a in json.load(f)}

    cats = {k: {"name": v["name"], "msg": v["msg"], "url": f"/articles/{v['slug']}/",
                "title": arts[v["slug"]]["title"]} for k, v in data["cats"].items()}

    qs = ""
    for n, it in enumerate(data["items"], 1):
        opts = "".join(f'<label class="opt"><input type="radio" name="{it["id"]}" value="{v}" required><span>{lab}</span></label>'
                       for v, lab in (("2", "أيوه"), ("1", "ساعات"), ("0", "لأ")))
        qs += f'''<fieldset class="q" data-cat="{it["cat"]}">
          <legend><span class="qn">{n}</span> {esc(it["t"])}</legend>
          <div class="opts opts-3">{opts}</div>
        </fieldset>'''

    def ep_card(slug, label):
        a = arts[slug]
        return f'''<li class="card"><a href="/articles/{slug}/">
          {ba.pic(a["image"], a["image_alt"], sizes="(max-width: 700px) 100vw, 340px")}
          <div class="card-body"><span class="card-date">{label}</span><h3>{esc(a["title"])}</h3><p class="card-desc">{esc(a["description"])}</p></div>
        </a></li>'''

    eps = "".join(ep_card(s, f"الحلقة {ORD[i]}") for i, s in enumerate(SERIES) if s in arts)
    tools = "".join(ep_card(s, "أداة تساعدك") for s in TOOLS if s in arts)

    body = f'''  <a class="quick-exit" href="https://www.google.com/" rel="noreferrer">✕ اخرج بسرعة</a>
  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">سلسلة جديدة</p>
      <h1>شريكي محيّرني</h1>
      <p class="lead">نرجسي؟ شكاك؟ بخيل؟ عصبي؟ بيكدب؟ أهله متدخلين؟ بيأذيك نفسياً؟ ولا تعبان نفسياً ومحتاج دعم؟ سلسلة بالمصري تساعدك تفهم اللي بيحصل في علاقتك، وتعرف تتعامل إزاي من غير ما تضيع منك نفسك.</p>
      <p><a class="btn primary big" href="#check">ابدأ بالاختبار (٣ دقايق)</a></p>
    </div>
  </section>
  <section class="section" id="check">
    <div class="wrap narrow">
      <h2>إيه اللي بيتعبك في علاقتك؟</h2>
      <p>{len(data["items"])} جملة عن شريكك (خطيب، زوج، أو ارتباط). جاوب بصراحة عن آخر كام شهر، وهتعرف أكتر نمط بيتعبك، والحلقة اللي تقراها الأول.</p>
      <p class="privacy">🔒 الإجابات مش بتتبعت لأي حد ومش بتتحفظ. وزرار «اخرج بسرعة» بيقفل الصفحة فوراً لو حد دخل عليك.</p>
      <form id="pc" class="quiz" novalidate>
        {qs}
        <p class="quiz-error" hidden>فاضل جمل ماجاوبتهاش، اتعلّمت باللون الأحمر.</p>
        <button type="submit" class="btn primary big">شوف النتيجة</button>
      </form>
      <noscript><p>الصفحة دي محتاجة JavaScript عشان تحسب النتيجة.</p></noscript>
      <div id="pc-result" class="result" hidden tabindex="-1" aria-live="polite"></div>
      <div class="note-box">
        <h2>ليه الاختبار مش بيقولك «شريكك نرجسي» أو «مريض نفسي»؟</h2>
        <p>لأن التشخيص النفسي محدش يقدر يعمله غير متخصص بعد ما يقابل الشخص نفسه ويقيّمه. الاختبار ده بيسأل عن <strong>السلوك اللي انت عايشه</strong>، وده اللي يهم: السلوك المؤذي يستاهل تحمي نفسك منه، سواء وراه اضطراب ولا لأ. والجمل مكتوبة للتوعية بناءً على كتاب «ليه بنحب اللي بيوجعنا؟» وعلامات الإنذار المعروفة، ومش مقياس علمي مقنن.</p>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <h2>حلقات السلسلة</h2>
      <ul class="cards">{eps}</ul>
      <h2>أدوات تساعدكم تقرّبوا</h2>
      <ul class="cards">{tools}</ul>
      <p>ولو حاسس إنك محتاج حد يسمعك، فيه <a href="/sessions/">جلسات نفسية أونلاين لأهلنا في مصر والوطن العربي</a>. ولو في خطر دلوقتي، شوف <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>
      {ba.share_block(SITE + "/partner/", "شريكي محيّرني: اعرف إيه اللي بيتعبك في علاقتك في ٣ دقايق — د. ميلاد ميخائيل", "شارك السلسلة")}
    </div>
  </section>
  <script type="application/json" id="pc-data">{json.dumps(cats, ensure_ascii=False)}</script>'''

    parts = [{"@type": "Article", "name": arts[s]["title"], "url": f"{SITE}/articles/{s}/"} for s in SERIES if s in arts]
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "شريكي محيّرني",
          "url": f"{SITE}/partner/", "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"},
          "description": "سلسلة عن التعامل مع الشريك النرجسي والشكاك والبخيل والعصبي والكداب والمؤذي نفسياً، وتدخل الأهل، والشريك اللي عنده اكتئاب أو إدمان أو قلق، مع اختبار سلوكيات.",
          "hasPart": parts}
    title = "شريكي محيّرني: التعامل مع الشريك النرجسي والشكاك والبخيل"
    desc = "شريكك نرجسي ولا شكاك ولا بخيل ولا بيأذيك نفسياً؟ اختبار قصير يوضحلك إيه اللي بيتعبك، وسلسلة مقالات بالمصري تقولك تتعامل إزاي."
    html = page("partner", title, desc, body, ld, og=f"{SITE}/assets/og/dealing-with-narcissistic-partner.jpg")
    html = html.replace('<script src="/assets/share.js" defer></script>',
                        '<script src="/assets/partner-check.js" defer></script>\n<script src="/assets/share.js" defer></script>')
    write("partner", html)
