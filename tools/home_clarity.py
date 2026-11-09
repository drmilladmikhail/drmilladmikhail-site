#!/usr/bin/env python3
"""Apply the reviewed homepage design; preserve the header and other pages."""
from pathlib import Path
import re

HERO = """<section class="hero hero-dark clarity-hero">
  <div class="wrap"><div class="hero-text">
    <p class="quiz-kicker">د. ميلاد ميخائيل</p>
    <h1 class="hero-name">افهم نفسك… وخد خطوة لحياة أهدى</h1>
    <p class="statement">مقالات مبسطة وأدوات توعوية وتمارين عملية لفهم مشاعرك وعلاقاتك، بالعربي البسيط.</p>
    <div class="actions"><a class="btn btn-gold" href="#concern-title">اختار اللي شاغل بالك</a></div>
  </div></div>
</section>"""
REMOVED = ('discovery-hub', 'guide', 'quick-quiz', 'myth-promo', 'tests-band', 'quote-band')


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
    text = before + '<main id="main">' + main + '</main>' + after
    stylesheet = '<link rel="stylesheet" href="/assets/home-clarity.css">'
    if stylesheet not in text:
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
