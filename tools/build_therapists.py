#!/usr/bin/env python3
"""Build one profile page per therapist: therapists/<slug>/index.html.

Data: content/therapists/<slug>.json (see content/therapists/HOWTO.md).
His request (2026-11-25): every therapist gets a page with their own name in the
link, that feels like their own profile, while it lives on this site. So the page
carries no site header and no personal branding of the site owner; the site shows
only as a small link in the footer. No scripts: booking is a WhatsApp link.
"""
import html
import json
import os
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "content", "therapists")
OUT = os.path.join(ROOT, "therapists")
SITE = "https://drmilladmikhail.com"


def e(s):
    return html.escape(str(s or ""), quote=True)


def is_placeholder(s):
    s = str(s or "").strip()
    return s.startswith("[") and s.endswith("]")


def item_list(items, kind):
    out = []
    for it in items:
        if kind == "cred":
            main, meta = it.get("name"), " · ".join(x for x in (it.get("place"), it.get("year")) if x)
            out.append(f'<li><b>{e(main)}</b><small>{e(meta)}</small></li>')
        elif kind == "article":
            title, place, url = it.get("title"), it.get("place"), it.get("url")
            head = (f'<a href="{e(url)}" target="_blank" rel="noopener">{e(title)}</a>' if url else e(title))
            out.append(f'<li><b>{head}</b><small>{e(place)}</small></li>')
        elif kind == "video":
            title, url = it.get("title"), it.get("url")
            head = (f'<a href="{e(url)}" target="_blank" rel="noopener">▶ {e(title)}</a>' if url else f'▶ {e(title)}')
            out.append(f'<li><b>{head}</b></li>')
    return "\n".join(out)


def initial(name):
    """First letter of the name after the title, skipping brackets and punctuation."""
    rest = name.replace("د.", "", 1)
    for ch in rest:
        if ch.isalpha():
            return ch
    return "د"


def section(title, body, sid=None):
    if not body:
        return ""
    idattr = f' id="{sid}"' if sid else ""
    return f'<section class="tp-block"{idattr}>\n<h2>{e(title)}</h2>\n{body}\n</section>'


def page(d):
    name = d["name"]
    slug = d["slug"]
    url = f"{SITE}/therapists/{slug}/"
    specs = d.get("specialties") or []
    desc = f'{name} · {d.get("title", "معالج نفسي")}' + (f' · {"، ".join(specs)}' if specs else "") + " · جلسات نفسية أونلاين."
    photo = d.get("photo") or ""
    avatar = (f'<img class="tp-photo" src="/{e(photo.lstrip("/"))}" alt="صورة {e(name)}" width="160" height="160">'
              if photo else f'<div class="tp-photo tp-initial" aria-hidden="true">{e(initial(name))}</div>')
    og_img = f'<meta property="og:image" content="{SITE}/{e(photo.lstrip("/"))}">\n' if photo else ""
    robots = '<meta name="robots" content="noindex, nofollow">\n' if d.get("preview", True) else ""
    preview = ('<p class="tp-preview">صفحة تجريبية: البيانات اللي بين الأقواس هتتملى من استمارة المعالج.</p>'
               if d.get("preview", True) else "")

    facts = []
    if d.get("experience"):
        facts.append(f'<li><span>الخبرة</span><b>{e(d["experience"])}</b></li>')
    if d.get("languages"):
        facts.append(f'<li><span>اللغات</span><b>{e("، ".join(d["languages"]))}</b></li>')
    if d.get("session_mode"):
        facts.append(f'<li><span>الجلسة</span><b>أونلاين · {e(d["session_mode"])}</b></li>')

    bio = "\n".join(f"<p>{e(p)}</p>" for p in d.get("bio") or [])
    creds = d.get("credentials") or []
    courses = d.get("courses") or []
    arts = d.get("articles") or []
    vids = d.get("videos") or []

    rows = "\n".join(f'<li><span>{e(s.get("length"))}</span><b>{e(s.get("price"))}</b></li>' for s in d.get("sessions") or [])
    wa = (d.get("contact_whatsapp") or "").strip()
    if wa:
        msg = urllib.parse.quote(f"أهلاً {name}، حابب أحجز جلسة. شفت صفحتك: {url}")
        cta = f'<a class="tp-btn" href="https://wa.me/{e(wa)}?text={msg}" target="_blank" rel="noopener">احجز على واتساب</a>'
        cta_top = f'<a class="tp-btn" href="#book">احجز جلسة</a>'
    else:
        cta = '<p class="tp-muted">الحجز هيتفعل أول ما رقم الحجز يتضاف.</p>'
        cta_top = '<a class="tp-btn" href="#book">احجز جلسة</a>'

    book = f'''<section class="tp-block tp-book" id="book">
<h2>احجز جلسة مع {e(name)}</h2>
<ul class="tp-prices">{rows}</ul>
<p class="tp-muted">المواعيد: {e(d.get("schedule"))}</p>
<p class="tp-muted">الإلغاء أو التعديل: {e(d.get("cancel_policy"))}</p>
{cta}
<p class="tp-muted tp-small">الجلسات سرّية. بياناتك بتتستخدم للحجز والتواصل بس.</p>
</section>'''

    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{robots}<title>{e(name)} | {e(d.get("title", "معالج نفسي"))}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(name)} | {e(d.get("title", "معالج نفسي"))}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
{og_img}<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="/assets/fonts.css">
<link rel="stylesheet" href="/therapists/profile.css">
</head>
<body class="tp">
{preview}
<header class="tp-hero">
<div class="tp-wrap tp-hero-in">
{avatar}
<div class="tp-id">
<h1>{e(name)}</h1>
<p class="tp-title">{e(d.get("title", "معالج نفسي"))}</p>
<ul class="tp-tags">{"".join(f"<li>{e(s)}</li>" for s in specs)}</ul>
{cta_top}
</div>
</div>
</header>
<main class="tp-wrap">
<ul class="tp-facts">{"".join(facts)}</ul>
{section("نبذة", bio)}
{section("الشهادات والمؤهلات", f'<ul class="tp-list">{item_list(creds, "cred")}</ul>' if creds else "")}
{section("الكورسات والتدريب", f'<ul class="tp-list">{item_list(courses, "cred")}</ul>' if courses else "")}
{section("مقالات", f'<ul class="tp-list">{item_list(arts, "article")}</ul>' if arts else "")}
{section("فيديوهات", f'<ul class="tp-list">{item_list(vids, "video")}</ul>' if vids else "")}
{book}
<p class="tp-urgent">لو أنت أو حد قريبك في خطر فوري، متستناش جلسة: اتصل بالطوارئ (في مصر ١٢٣) أو خط الصحة النفسية ١٦٣٢٨، أو اتوجه لأقرب مستشفى.</p>
</main>
<footer class="tp-foot tp-wrap">
<a href="/">مقالات واختبارات نفسية مجانية بالعربي ←</a>
</footer>
</body>
</html>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    built = []
    for fn in sorted(os.listdir(DATA)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(DATA, fn), encoding="utf-8") as f:
            d = json.load(f)
        assert d.get("slug") == fn[:-5], f"{fn}: slug must match the file name"
        target = os.path.join(OUT, d["slug"])
        os.makedirs(target, exist_ok=True)
        path = os.path.join(target, "index.html")
        new = page(d)
        # keep what add_analytics.py injected later (CSP, analytics) by rebuilding from scratch each time;
        # run tools/add_analytics.py after this script.
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        built.append(d["slug"])
    print(f"therapists: built {len(built)} profile page(s): {', '.join(built)}")


if __name__ == "__main__":
    main()
