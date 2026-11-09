#!/usr/bin/env python3
"""Apply the reviewed homepage design; preserve the header and other pages."""
from pathlib import Path
import re

HERO = """<section class="hero hero-dark clarity-hero">
  <div class="wrap"><div class="hero-text">
    <p class="quiz-kicker">د. ميلاد ميخائيل</p>
    <h1 class="hero-name">افهم نفسك… وخد خطوة لحياة أهدى</h1>
    <p class="statement">مقالات مبسطة وأدوات توعوية وتمارين عملية لفهم مشاعرك وعلاقاتك، بالعربي البسيط.</p>
    <div class="actions"><a class="btn btn-gold" href="/discover-feelings/">اكتشف مشاعرك</a> <a class="btn btn-ghost" href="#concern-title">اختار اللي شاغل بالك</a></div>
    <p class="hero-sub">مش عارف إحساسك؟ اكتبه بكلماتك، وسمّيه، وجرّب خطوة صغيرة. اللي بتكتبه ما بيتبعتش ولا بيتحفظ.</p>
  </div></div>
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
