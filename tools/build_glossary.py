#!/usr/bin/env python3
"""Build a source-backed, static Egyptian Arabic glossary. No visitor input stored."""
import json
from pathlib import Path
import re

import build_articles as ba
from site_header import header_for

ROOT = Path(__file__).resolve().parents[1]
SITE = ba.SITE
esc = ba.esc
CATEGORIES = ["المشاعر", "التفكير", "علاقتك بنفسك", "العلاقات"]


def load(root=ROOT):
    data = json.loads((Path(root) / "content/glossary.json").read_text(encoding="utf-8"))
    expansion = Path(root) / "content/glossary-more.json"
    if expansion.exists():
        data["items"].extend(json.loads(expansion.read_text(encoding="utf-8"))["items"])
    seen = set()
    for term in data["items"]:
        # Many everyday concepts have no clinical threshold. Do not invent one.
        if "help" not in term:
            term["help"] = "لو الموضوع بقى متكرر وبيتعبك أو مأثر على حياتك وعلاقاتك، تقدر تتكلم مع مختص. طلب الدعم مش محتاج إنك تشخّص نفسك الأول."
            term["general_help"] = True
        term.setdefault("reading", ["/exercise/", "جرّب تمرينًا عمليًا للعناية بنفسك"])
        slug = term["slug"]
        if not re.fullmatch(r"[a-z]+(?:-[a-z]+)*", slug) or slug in seen:
            raise ValueError("Invalid or duplicate glossary slug")
        seen.add(slug)
        if term["category"] not in CATEGORIES:
            raise ValueError("Unknown glossary category")
        if not term["source"]["url"].startswith("https://"):
            raise ValueError("A public HTTPS source is required")
        for field in ("definition", "example", "not", "comparison", "help", "question"):
            if not term[field].strip():
                raise ValueError("Missing glossary content: " + field)
    for term in data["items"]:
        if any(s not in seen or s == term["slug"] for s in term["related"]):
            raise ValueError("Invalid related term")
    return data


def shell(slug, title, description, body, ld):
    url = SITE + "/" + slug + "/"
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | د. ميلاد ميخائيل</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
{ba.social(url, title, description, SITE + "/assets/og/home.jpg", title, "website")}
<meta name="theme-color" content="#2f6f62">
{ba.FONTS}
<link rel="stylesheet" href="/assets/glossary.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("<", chr(92) + "u003c")}</script>
</head>
<body class="glossary-page">
{header_for(slug + "/index.html")}
<main id="main">{body}</main>
{ba.FOOTER}
<script src="/assets/nav.js" defer></script>
<script src="/assets/glossary.js" defer></script>
</body>
</html>
'''


def index_page(data):
    buckets = [[t for t in data["items"] if t["category"] == c] for c in CATEGORIES]
    terms = [bucket[i] for i in range(max(map(len, buckets), default=0))
             for bucket in buckets if i < len(bucket)]
    cards = []
    previews = []
    for term in terms:
        keywords = " ".join([term["title"], term["english"], *term["aliases"]])
        tone = CATEGORIES.index(term["category"])
        cards.append(f'''<li class="g-entry" data-category="{esc(term["category"])}" data-search="{esc(keywords)}">
<a class="g-card g-tone-{tone}" data-term="{term["slug"]}" href="/glossary/{term["slug"]}/"><div class="g-entry-meta"><span>{esc(term["category"])}</span>
<span lang="en" dir="ltr">{esc(term["english"])}</span></div>
<h2>{esc(term["title"])}</h2><p>{esc(term["summary"])}</p>
<span class="g-read">اعرض التعريف <span aria-hidden="true">←</span></span></a></li>''')
        previews.append(f'''<template id="g-preview-{term["slug"]}"><div class="g-preview-toolbar">
<button type="button" class="g-close" autofocus>اقفل التعريف <span aria-hidden="true">×</span></button></div>
<div class="g-preview-head g-tone-{tone}">
<p class="g-eyebrow">{esc(term["category"])}</p><h2 id="glossary-preview-title">{esc(term["title"])}</h2>
<p class="g-preview-english" lang="en" dir="ltr">{esc(term["english"])}</p></div>
<div class="g-preview-body"><h3>يعني إيه بالمصري؟</h3><p>{esc(term["definition"])}</p>
<a class="g-reference" href="{esc(term["source"]["url"])}" target="_blank" rel="noopener">المرجع الأصلي</a>
<h3>مثال من يومك</h3><p class="g-caption">موقف تخيّلي بالمصري للتوضيح، مش تشخيص</p><p>{esc(term["example"])}</p>
<h3>إيه اللي مش معناه؟</h3><p>{esc(term["not"])}</p>
<a class="g-reference" href="{esc(term["source"]["url"])}" target="_blank" rel="noopener">اقرأ المرجع</a>
<p class="g-preview-note">للتوعية، مش تشخيصًا ولا بديلًا عن تقييم متخصص.</p>
<a class="g-full-link" href="/glossary/{term["slug"]}/">التفاصيل والمقارنة والمراجع <span aria-hidden="true">←</span></a></div></template>''')
    buttons = "".join(f'<button type="button" data-category-filter="{c}" aria-pressed="false">{c}</button>' for c in CATEGORIES)
    body = f'''
<section class="g-hero"><div class="wrap">
<nav class="g-crumbs" aria-label="مسار الصفحة"><a href="/">الرئيسية</a><span aria-hidden="true">/</span><span>القاموس النفسي</span></nav>
<p class="g-eyebrow">كلمات بنسمعها كتير. نفهمها بهدوء.</p>
<h1>القاموس النفسي بالمصري</h1>
<p class="g-lead">اختار كارت وافهم الكلمة: شرح بسيط، مثال من الحياة، والفرق بين المعنى العلمي والكلام اللي بنستخدمه كل يوم.</p>
<p class="g-caption">{len(terms)} مصطلحًا · مصادر تقدر ترجع لها · من غير تسجيل</p>
</div></section>
<section class="g-directory"><div class="wrap">
<div class="g-controls" hidden>
<label for="glossary-search">بتدور على كلمة إيه؟</label>
<div class="g-search-row"><input id="glossary-search" type="search" maxlength="160" placeholder="زي: اكتئاب، حب النفس، بفكر كتير" autocomplete="off" aria-controls="glossary-entries">
<button type="button" class="g-reset">امسح البحث</button></div>
<div class="g-filters" role="group" aria-label="تصفية حسب الموضوع"><button type="button" data-category-filter="" aria-pressed="true">الكل</button>{buttons}</div>
<p class="g-count" role="status" aria-live="polite">{len(terms)} مصطلحًا</p>
</div>
<ul id="glossary-entries" class="g-entries">{"".join(cards)}</ul>
<div class="g-empty" hidden><h2>مفيش مصطلح مطابق للبحث ده</h2><p>جرّب كلمة أقصر أو موضوع تاني.</p><button type="button" class="g-reset">اعرض كل المصطلحات</button></div>
<dialog id="glossary-preview" aria-labelledby="glossary-preview-title"></dialog>
{"".join(previews)}
<aside class="g-editorial" aria-label="عن محتوى القاموس"><h2>نفهم المصطلح، مش نشخّص نفسنا</h2>
<p>الشرح مبسّط بالمصري ومبني على المراجع المرفقة بكل صفحة، مش ترجمة حرفية ولا تقييمًا لحالتك. الأمثلة تخيّلية للتوضيح، مش قصص أشخاص حقيقيين.</p>
<p>لو محتاج دعمًا، ابدأ بصفحة <a href="/help-now/">محتاج مساعدة دلوقتي</a> أو استكشف <a href="/articles/">المقالات</a>.</p></aside>
</div></section>'''
    ld = {"@context": "https://schema.org", "@type": "DefinedTermSet",
          "name": "القاموس النفسي بالمصري", "inLanguage": "ar-EG", "url": SITE + "/glossary/",
          "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t["title"], "url": SITE + "/glossary/" + t["slug"] + "/"} for t in terms]}
    return shell("glossary", "القاموس النفسي بالمصري", "مصطلحات نفسية بالمصري: الحزن والاكتئاب والقلق والحدود الصحية. شرح بسيط وأمثلة توضيحية ومفاهيم شائعة ومراجع للقراءة.", body, ld)


def term_page(term, data):
    slug = "glossary/" + term["slug"]
    url = SITE + "/" + slug + "/"
    ref = f'<a class="g-reference" href="{esc(term["source"]["url"])}" target="_blank" rel="noopener">اقرأ المرجع الأصلي <span class="g-sr-only">في نافذة جديدة</span></a>'
    help_ref = '<p class="g-caption">إرشاد عام لطلب الدعم، مش معيارًا لتشخيص المصطلح.</p>' if term.get("general_help") else ref
    by_slug = {t["slug"]: t for t in data["items"]}
    related = "".join(f'<li><a href="/glossary/{s}/">{esc(by_slug[s]["title"])} <span aria-hidden="true">←</span></a></li>' for s in term["related"])
    from urllib.parse import quote
    share_text = quote(f'{term["title"]}: {term["summary"]}\nالقاموس النفسي بالمصري\n{url}', safe="")
    body = f'''
<article class="g-term"><div class="wrap">
<nav class="g-crumbs" aria-label="مسار الصفحة"><a href="/">الرئيسية</a><span aria-hidden="true">/</span><a href="/glossary/">القاموس النفسي</a><span aria-hidden="true">/</span><span>{esc(term["title"])}</span></nav>
<header class="g-term-header"><p class="g-eyebrow">{esc(term["category"])}</p><h1>{esc(term["title"])}</h1>
<p class="g-english" lang="en" dir="ltr">{esc(term["english"])}</p>
<p class="g-lead">{esc(term["summary"])}</p></header>
<div class="g-term-layout"><div class="g-prose">
<section class="g-definition" aria-labelledby="definition"><h2 id="definition">يعني إيه بالمصري؟</h2><p>{esc(term["definition"])}</p>{ref}</section>
<section><h2>مثال من يومك</h2><p class="g-example-label">موقف تخيّلي بالمصري للتوضيح، مش تشخيص</p><p>{esc(term["example"])}</p></section>
<section><h2>إيه اللي مش معناه؟</h2><p>{esc(term["not"])}</p>{ref}</section>
<section><h2>الفرق اللي يستاهل نعرفه</h2><p>{esc(term["comparison"])}</p>{ref}</section>
<section><h2>إمتى أطلب مساعدة؟</h2><p>{esc(term["help"])}</p>{help_ref}
<p class="g-safety">لو فيه خطر فوري أو أفكار لإيذاء نفسك، اطلب مساعدة عاجلة من الطوارئ المحلية، وشوف <a href="/help-now/">خيارات المساعدة دلوقتي</a>. ما تستناش مدة معينة أو نتيجة اختبار.</p></section>
<section class="g-reflection"><h2>سؤال تاخده معاك</h2><p>{esc(term["question"])}</p><p class="g-caption">سؤال للتأمل، ومش مطلوب تكتب إجابتك على الموقع.</p></section>
</div><aside class="g-side">
<div><h2>كمّل فهمك</h2><ul class="g-related">{related}</ul><a class="g-deeper" href="{esc(term["reading"][0])}">{esc(term["reading"][1])}</a></div>
<div class="g-share"><h2>شارك المعنى، مش بياناتك</h2><p>المشاركة فيها ملخص المصطلح ورابطه بس.</p>
<button type="button" class="g-copy" data-url="{url}" hidden>انسخ رابط المصطلح</button>
<a class="g-whatsapp" href="https://wa.me/?text={share_text}" target="_blank" rel="noopener">شارك على واتساب</a>
<p class="g-copy-status" role="status" aria-live="polite"></p></div>
<div class="g-source"><h2>مصدر الشرح</h2><a href="{esc(term["source"]["url"])}" target="_blank" rel="noopener">{esc(term["source"]["name"])}</a>
<p>الصياغة مبسّطة وليست ترجمة حرفية. الأمثلة وأسئلة التأمل توضيحية من إعداد الموقع.</p><p>آخر تحديث تحريري: <time datetime="{data["updated"]}">{data["updated"]}</time></p>
<p>المحتوى للتوعية، مش تشخيصًا ولا بديلًا عن التقييم والعلاج مع متخصص.</p></div>
<a class="g-back" href="/glossary/">ارجع لكل المصطلحات</a>
</aside></div></div></article>'''
    ld = {"@context": "https://schema.org", "@type": "DefinedTerm",
          "name": term["title"], "alternateName": term["english"], "description": term["summary"],
          "url": url, "inDefinedTermSet": SITE + "/glossary/"}
    return shell(slug, term["title"] + " بالمصري: المعنى والفرق والمثال", term["summary"] + " افهم المعنى بمثال توضيحي، واعرف المفاهيم الشائعة وإمتى تطلب مساعدة، مع مرجع أصلي.", body, ld)


def build(root=ROOT):
    root = Path(root)
    data = load(root)
    pages = {"glossary": index_page(data)}
    pages.update({"glossary/" + t["slug"]: term_page(t, data) for t in data["items"]})
    for slug, html in pages.items():
        path = root / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != html:
            path.write_text(html, encoding="utf-8")
    return list(pages)


if __name__ == "__main__":
    print("Built glossary:", ", ".join(build()))
