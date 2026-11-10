#!/usr/bin/env python3
"""Apply the reviewed homepage design; preserve the header and other pages."""
from pathlib import Path
import re

HERO = """<section class="hero hero-dark clarity-hero">
  <div class="wrap h3d-wrap"><div class="hero-text">
    <p class="quiz-kicker">د. ميلاد ميخائيل</p>
    <h1 class="hero-name">افهم نفسك… وخد خطوة لحياة أهدى</h1>
    <p class="statement">مقالات مبسطة وأدوات توعوية وتمارين عملية لفهم مشاعرك وعلاقاتك، بالعربي البسيط.</p>
    <div class="actions"><a class="btn btn-gold" href="/discover-feelings/">اكتشف مشاعرك</a> <a class="btn btn-ghost" href="#concern-title">اختار اللي شاغل بالك</a></div>
    <p class="hero-sub">مش عارف إحساسك؟ اكتبه بكلماتك، وسمّيه، وجرّب خطوة صغيرة. اللي بتكتبه ما بيتبعتش ولا بيتحفظ.</p>
  </div>
  <div class="hero3d"><div class="h3d-stage">
    <span class="h3d-core" aria-hidden="true"><span class="h3d-ring"></span><span class="h3d-orb"></span><span class="h3d-ring h3d-ring-front"></span></span>
    <span class="h3d-dot d1" aria-hidden="true"></span><span class="h3d-dot d2" aria-hidden="true"></span><span class="h3d-dot d3" aria-hidden="true"></span>
    <ul class="h3d-cards" aria-label="أدوات مجانية في الموقع">
      <li><a class="h3d-card" href="/tests/"><span class="h3d-ico" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M9 11l2 2 4-4"/><rect x="4" y="3" width="16" height="18" rx="3"/></svg></span><span><b>اختبارات نفسية</b><small>مقاييس علمية، والنتيجة فورًا</small></span></a></li>
      <li><a class="h3d-card" href="/exercise/"><span class="h3d-ico" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m4 16 11-11 4 4L8 20H4zM13 7l4 4"/></svg></span><span><b>تمرين الأسبوع</b><small>خطوة عملية صغيرة كل أسبوع</small></span></a></li>
      <li><a class="h3d-card" href="/glossary/"><span class="h3d-ico" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5M9 8h6"/></svg></span><span><b>القاموس النفسي</b><small>افهم المصطلح بمثال بسيط</small></span></a></li>
    </ul>
  </div></div>
  </div>
</section>"""
REMOVED = ('discovery-hub', 'guide', 'quick-quiz', 'myth-promo', 'tests-band', 'quote-band')
GLOSSARY = """<section class="section glossary-home" aria-labelledby="glossary-home-title">
  <div class="wrap">
    <h2 id="glossary-home-title">القاموس النفسي</h2>
    <p>إيه الفرق بين الحزن والاكتئاب؟ وهل الحنية على نفسك أنانية؟ افهم المصطلحات بمثال بسيط ومرجع تقدر ترجع له.</p>
    <a class="btn" href="/glossary/">افتح القاموس النفسي</a>
  </div>
</section>"""


def section_pattern(name):
    return (r'<section\b(?=[^>]*\bclass="(?:[^"]*\s)?'
            + re.escape(name) + r'(?=\s|")[^"]*")[^>]*>.*?</section>')


def transform(text):
    if (text.count('<main id="main">') != 1 or '</head>' not in text
            or 'id="concern-title"' not in text):
        raise ValueError('Homepage structure changed; review before applying')
    before, tail = text.split('<main id="main">', 1)
    if tail.count('</main>') != 1:
        raise ValueError('Expected one closing main tag')
    main, after = tail.split('</main>', 1)
    main = re.sub(r'<!-- GROWTH-GUIDE:BEGIN -->.*?<!-- GROWTH-GUIDE:END -->', '', main, flags=re.S)
    for name in REMOVED:
        for match in re.finditer(section_pattern(name), main, flags=re.S):
            if len(re.findall(r'<section\b', match.group(0))) != 1:
                raise ValueError('Nested section requires manual review: ' + name)
        main = re.sub(section_pattern(name), '', main, flags=re.S)
    heroes = list(re.finditer(section_pattern('hero'), main, flags=re.S))
    if len(heroes) != 1 or len(re.findall(r'<section\b', heroes[0].group(0))) != 1:
        raise ValueError('Expected one non-nested homepage hero')
    main = re.sub(section_pattern('hero'), lambda _: HERO, main, count=1, flags=re.S)
    import build_your_path
    concerns = list(re.finditer(section_pattern('concern-finder'), main, flags=re.S))
    if len(concerns) != 1 or len(re.findall(r'<section\b', concerns[0].group(0))) != 1:
        raise ValueError('Expected one non-nested concern finder')
    main = re.sub(section_pattern('concern-finder'), lambda _: build_your_path.home_section(),
                  main, count=1, flags=re.S)
    if 'class="section glossary-home"' not in main:
        # Keep existing homepage sections and their relative ordering intact.
        main = main.rstrip() + '\n' + GLOSSARY + '\n'
    else:
        matches = list(re.finditer(section_pattern('glossary-home'), main, flags=re.S))
        if len(matches) != 1 or len(re.findall(r'<section\b', matches[0].group(0))) != 1:
            raise ValueError('Expected one non-nested glossary homepage section')
        main = re.sub(section_pattern('glossary-home'), lambda _: GLOSSARY, main, count=1, flags=re.S)
    text = before + '<main id="main">' + main + '</main>' + after
    stylesheet = '<link rel="stylesheet" href="/assets/home-clarity.css">'
    if not re.search(r'href="/assets/home-clarity\.css(\?v=[0-9a-f]+)?"', text):
        text = text.replace('</head>', stylesheet + '\n</head>', 1)
    return text


def apply(root):
    path = Path(root) / 'index.html'
    original = path.read_text(encoding='utf-8')
    updated = transform(original)
    if updated == original:
        return False
    path.write_text(updated, encoding='utf-8')
    return True


if __name__ == '__main__':
    apply(Path(__file__).resolve().parents[1])
