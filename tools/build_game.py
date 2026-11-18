#!/usr/bin/env python3
"""Build /game/ «فوانيس العقل» — a small CBT game (called by build_pages.main).

Content: assets/game/data.js · engine: assets/game/game.js · style: assets/game/game.css.
Nothing a player types is sent or stored; only the list of lit lanterns is kept on the device.
Health content: goes live only after Dr. Millad's review (content/REVIEW-POLICY.md).
"""
SLUG = "game"
TITLE = "فوانيس العقل"
DESC = ("لعبة مجانية بالمصري من العلاج المعرفي السلوكي: نوّر فوانيس ٥ حارات في مدينة العقل "
        "(القلق، الحزن، العلاقات، الثقة بالنفس، الغضب) واتعلّم تمسك فخاخ التفكير.")
REFS = [
    ("NHS: Cognitive behavioural therapy (CBT)",
     "https://www.nhs.uk/mental-health/talking-therapies-medicine-treatments/talking-therapies-and-counselling/cognitive-behavioural-therapy-cbt/overview/"),
    ("APA: Cognitive behavioral therapy", "https://www.apa.org/topics/psychotherapy/cognitive-behavioral"),
]


def build(ba, page, write, SITE):
    esc = ba.esc
    refs = "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a></li>' for t, u in REFS)
    body = f'''  <section class="page-hero">
    <div class="wrap narrow">
      <p class="kicker-g">لعبة مجانية، حوالي ١٠ دقايق</p>
      <h1>{TITLE}</h1>
      <p class="lead">مدينة العقل ضلمة، وفي كل حارة فكرة قاسية مطفية الفانوس. ساعد أهل الحارات يمسكوا «فخاخ التفكير» ويفرّقوا بين الحقيقة والتخمين، ونوّر المدينة كلها. واللي هتتعلمه هنا، تقدر تستخدمه على أفكارك إنت.</p>
      <p class="privacy">🔒 مفيش تسجيل، واللي بتكتبه مش بيتبعت لأي حد.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div id="fanoos" class="fanoos">
        <noscript><p style="padding:24px">اللعبة محتاجة JavaScript. لو مش شغال عندك، جرّب <a href="/life-tools/situation-thought-feeling/">أداة الموقف والفكرة والإحساس</a>.</p></noscript>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap narrow">
      <div class="note-box">
        <h2>اللعبة دي مبنية على إيه؟</h2>
        <p>على فكرة أساسية في العلاج المعرفي السلوكي (CBT): الموقف نفسه مش هو بس اللي بيحدد إحساسنا، الطريقة اللي بنفسّره بيها كمان. لما نلاحظ الفكرة، ونفرّق بين اللي حصل فعلًا واللي إحنا متوقعينه، ونختار فكرة أوقع وخطوة صغيرة، الإحساس غالبًا بيخف.</p>
        <p>الشخصيات والمواقف خيالية. اللعبة للتوعية والتدريب، ومش اختبار ولا تشخيص ولا بديل عن العلاج. لو الأفكار التقيلة مأثرة على نومك أو شغلك أو علاقاتك من أسابيع، كلّم متخصص.</p>
        <p>لو بتمر بأزمة دلوقتي أو عندك أفكار إنك تأذي نفسك: في مصر الخط الساخن للدعم النفسي <b>16328</b>، وفي أمريكا <b>988</b> (اتصال أو رسالة). وكل الأرقام في صفحة <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>
        <h3>مراجع للاستزادة</h3>
        <ul>{refs}</ul>
      </div>
      <ul class="link-grid">
        <li><a href="/life-tools/situation-thought-feeling/"><b>الموقف والفكرة والإحساس</b><span>طبّق نفس الخطوات على موقف حصلّك.</span></a></li>
        <li><a href="/worksheets/"><b>أوراق تمرين</b><span>تمارين تطبعها وتكتب فيها.</span></a></li>
        <li><a href="/tests/"><b>اختبارات نفسية</b><span>اختبارات علمية مجانية، ونتيجتها مش بتتحفظ.</span></a></li>
      </ul>
      {ba.share_block(f"{SITE}/{SLUG}/", f"{TITLE}: لعبة مجانية تتعلم فيها تمسك فخاخ التفكير — د. ميلاد ميخائيل", "شارك اللعبة")}
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": ["WebPage", "Game"], "name": TITLE, "url": f"{SITE}/{SLUG}/",
          "inLanguage": "ar", "author": {"@id": f"{SITE}/#person"}, "isAccessibleForFree": True,
          "educationalUse": "psychoeducation", "about": "Cognitive behavioral therapy (CBT)", "description": DESC}
    html = page(SLUG, f"{TITLE}: لعبة العلاج المعرفي السلوكي", DESC, body, ld)
    html = html.replace("</head>", '<link rel="stylesheet" href="/assets/game/game.css">\n</head>', 1)
    html = html.replace('<script src="/assets/share.js" defer></script>',
                        '<script src="/assets/game/data.js" defer></script>\n<script src="/assets/game/game.js" defer></script>\n'
                        '<script src="/assets/share.js" defer></script>')
    write(SLUG, html)
