#!/usr/bin/env python3
"""Build /game/ «بطاريتي 1%» — a one-day energy game linked to the book (called by build_pages.main).

Content: assets/game/data.js · engine: assets/game/game.js · style: assets/game/game.css.
Nothing a player chooses is sent or stored (page memory only). The share image is drawn on the device.
Health content: goes live only after Dr. Millad's review (content/REVIEW-POLICY.md).
"""
SLUG = "game"
TITLE = "بطاريتي 1%"
DESC = ("لعبة مجانية بالمصري: عيش يوم كامل في ١١ موقف، وشوف كل اختيار بيشحن بطاريتك ولا بيسحب منها، "
        "واعرف إيه اللي بيستنزفك وإيه اللي بيشحنك بجد.")


def build(ba, page, write, SITE):
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">لعبة مجانية، حوالي ٥ دقايق</p>
      <h1>لعبة «بطاريتي <span dir="ltr">1%</span>»</h1>
      <p class="lead">ساعات بنخلّص اليوم وإحنا حاسين إن بطاريتنا <span dir="ltr">1%</span>، ومش عارفين إيه اللي سحبها. في اللعبة دي هتعيش يوم كامل، وكل اختيار هتشوف أثره على بطاريتك على طول. وفي الآخر هتعرف شواحنك الحقيقية.</p>
      <p class="privacy">🔒 مفيش تسجيل، واختياراتك مش بتتبعت لأي حد.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div id="battery-game" class="bgame">
        <noscript><p style="padding:24px">اللعبة محتاجة JavaScript. لحد ما تشتغل عندك، جرّب <a href="/tests/burnout-cbi/">مقياس الاحتراق النفسي</a>.</p></noscript>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <div class="note-box">
        <h2>اللعبة دي مبنية على إيه؟</h2>
        <p>على فكرة بسيطة: طاقتنا النفسية مش بتخلص مرة واحدة، بتخلص من حاجات صغيرة بتتكرر كل يوم، زي النوم المتقطع، والـ«آه» اللي على حسابنا، والكلام القاسي مع نفسنا، والتقليب في الموبايل. وبرضه بتتشحن بحاجات صغيرة: حركة، وفاصل راحة، وكلمة مع حد بنحبه، وحاجة بنعملها ليها معنى.</p>
        <p>الأرقام في اللعبة للتوضيح، مش قياس علمي لطاقتك. واللعبة للتوعية، ومش اختبار ولا تشخيص. لو حاسس إن بطاريتك <span dir="ltr">1%</span> من أسابيع، وده مأثر على نومك أو شغلك أو علاقاتك، كلّم متخصص.</p>
        <p>لو بتمر بأزمة دلوقتي أو عندك أفكار إنك تأذي نفسك: في مصر الخط الساخن للدعم النفسي <b>16328</b>، وفي أمريكا <b>988</b> (اتصال أو رسالة). وكل الأرقام في صفحة <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>
      </div>
      <ul class="link-grid">
        <li><a href="/battery/"><b>كتاب «بطاريتي <span dir="ltr">1%</span>»</b><span>إزاي تشحن روحك من جديد وتلاقي معنى لحياتك.</span></a></li>
        <li><a href="/tests/burnout-cbi/"><b>مقياس الاحتراق النفسي</b><span>تعبك ده إرهاق عادي ولا احتراق؟</span></a></li>
        <li><a href="/tests/meaning-in-life-mlq/"><b>مقياس المعنى في الحياة</b><span>حاسس إن حياتك ليها معنى؟</span></a></li>
      </ul>
      {ba.share_block(f"{SITE}/{SLUG}/", f"لعبة «{TITLE}»: عيش يوم كامل وشوف إيه اللي بيشحن بطاريتك وإيه اللي بيسحبها — د. ميلاد ميخائيل", "شارك اللعبة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": ["WebPage", "Game"], "name": f"لعبة {TITLE}", "url": f"{SITE}/{SLUG}/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}, "isAccessibleForFree": True,
          "educationalUse": "psychoeducation", "description": DESC,
          "isRelatedTo": {"@type": "Book", "name": "بطاريتي 1%", "url": f"{SITE}/battery/"}}
    html = page(SLUG, f"لعبة {TITLE}: إيه اللي بيشحنك وإيه اللي بيسحب منك؟", DESC, body, ld)
    html = html.replace("</head>", '<link rel="stylesheet" href="/assets/game/game.css">\n</head>', 1)
    html = html.replace('<script src="/assets/share.js" defer></script>',
                        '<script src="/assets/game/data.js" defer></script>\n<script src="/assets/game/game.js" defer></script>\n'
                        '<script src="/assets/share.js" defer></script>')
    write(SLUG, html)
