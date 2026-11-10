#!/usr/bin/env python3
"""ONE shared header (logo + name + title + menus) for every Arabic page.

Why one file: the header used to be copied by hand into 5 builders and several
static pages, so a new link had to be added in many places and some pages forgot it.
Now every builder imports TOPBAR from here, and sync() (called by
tools/add_analytics.py after every build and by the "Site checks" GitHub Action
after every push) rewrites the header of every Arabic page to this exact version
and marks the current section with aria-current="page".

To add/rename a menu link: edit GROUPS / DESKTOP below, then run
    python3 tools/add_analytics.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAME = "د. ميلاد ميخائيل"
TITLE = "استشاري العلاج النفسي وتطوير الذات"
SLOGAN = "راحة بال، وتعديل حال… معاك في الرحلة لحياة أحلى"

# Logo mark: a sunrise arc (حياة أحلى) over the letter م, in the site colours.
MARK = ('<svg class="brand-mark" viewBox="0 0 44 44" aria-hidden="true" focusable="false">'
        '<rect width="44" height="44" rx="13" fill="#2f6f62"/>'
        '<path d="M9 31a13 13 0 0 1 26 0" fill="none" stroke="#e2b35a" stroke-width="2.6" stroke-linecap="round"/>'
        '<circle cx="22" cy="12.5" r="2.4" fill="#e2b35a"/>'
        '<text x="22" y="31" text-anchor="middle" font-family="Noto Naskh Arabic, serif" font-weight="700" '
        'font-size="19" fill="#fff">م</text></svg>')

# Mobile menu (☰) and the desktop drop-downs use the same groups.
GROUPS = [
    ("اقرأ واتفرّج", [
        ("/articles/", "المقالات"),
        ("/partner/", "سلسلة: شريكي محيّرني"),
        ("/videos/", "فيديوهات"),
        ("/questions/", "أسئلة محرجة"),
        ("/stories/", "حكايات التعافي"),
        ("/shelf/", "رفّ الترشيحات"),
        ("/book/", "كتبي"),
        ("https://blog.drmilladmikhail.com/", "المدونة"),
    ]),
    ("اختبر نفسك واتمرّن", [
        ("/discover-feelings/", "اكتشاف مشاعرك"),
        ("/paths/", "مسارات التعلّم"),
        ("/experts/", "دليل المتخصصين"),
        ("/tests/", "اختبارات نفسية"),
        ("/life-tools/", "أدوات لحياتك"),
        ("/exercise/", "تمرين الأسبوع"),
        ("/challenges/", "تحديات قصيرة"),
        ("/feelings/", "عجلة المشاعر"),
        ("/relationship-check/", "علاقتك صحية؟"),
        ("/worksheets/", "أوراق تمرين"),
    ]),
    ("عن د. ميلاد", [
        ("/#about", "نبذة"),
        ("/#credentials", "المؤهلات"),
        ("/sessions/", "الجلسات"),
        ("/ask/", "اسأل من غير اسمك"),
        ("/contact/", "تواصل"),
        ("/join-us/", "انضم للمنصة"),
    ]),
]


def _links(items):
    return "\n".join(f'          <a href="{h}">{t}</a>' for h, t in items)

RESEARCH_LIBRARY = ("/research/library/", "مكتبة الأكاديميين والباحثين")
SAVED = ("/saved/", "محفوظاتي")


def _menu():
    parts = ['        <a class="m-home" href="/">الصفحة الرئيسية</a>',
             '        <a class="m-start" href="/start/">ابدأ من هنا</a>',
             f'        <a href="{SAVED[0]}">{SAVED[1]}</a>',
             f'        <a href="{RESEARCH_LIBRARY[0]}">{RESEARCH_LIBRARY[1]}</a>']
    for title, items in GROUPS:
        parts.append(f'        <p class="m-group">{title}</p>')
        parts.append(_links(items).replace("          ", "        "))
    parts.append('        <a class="m-lang" href="/en/" hreflang="en" lang="en">English</a>')
    return "\n".join(parts)


def _dropdown(label, items):
    return f'''      <details class="dd">
        <summary>{label}</summary>
        <div class="dd-panel">
{_links(items)}
        </div>
      </details>'''


TOPBAR = f'''<a class="skip-link" href="#main">تخطّى للمحتوى</a>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/" aria-label="{NAME}، {TITLE}، الصفحة الرئيسية">
      {MARK}
      <span class="brand-text"><b>{NAME}</b><small>{TITLE}</small></span>
    </a>
    <nav class="nav" aria-label="أقسام الموقع">
      <a href="/">الصفحة الرئيسية</a>
      <a href="/articles/">المقالات</a>
      <a href="/tests/">اختبارات نفسية</a>
      <a href="/videos/">فيديوهات</a>
      <a href="/platform/">المنصة</a>
      <a href="/paths/">مسارات التعلّم</a>
{_dropdown("تمارين وأدوات", GROUPS[1][1][1:])}
{_dropdown("مكتبتي", [SAVED, RESEARCH_LIBRARY] + [GROUPS[0][1][i] for i in (2, 3, 4, 5, 6)])}
{_dropdown("عن د. ميلاد", GROUPS[2][1])}
      <a class="lang" href="/en/" hreflang="en" lang="en">English</a>
    </nav>
    <details class="menu">
      <summary aria-label="القائمة"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
      <nav aria-label="القائمة">
{_menu()}
      </nav>
    </details>
  </div>
</header>'''

HEADER_RE = re.compile(r'<a class="skip-link"[^>]*>[^<]*</a>\s*<header class="topbar( topbar-dark)?">.*?</header>', re.S)
NAV_JS = '<script src="/assets/nav.js" defer></script>'
SKIP_DIRS = {".git", ".github", "tools", "node_modules", "content", "en", "gifts"}


def header_for(rel_path, dark=False):
    """Header with aria-current on the link of the section this page belongs to."""
    url = "/" + rel_path.replace(os.sep, "/")
    url = url[: -len("index.html")] if url.endswith("index.html") else url
    h = TOPBAR
    if dark:
        h = h.replace('<header class="topbar">', '<header class="topbar topbar-dark">', 1)
    if url == "/":
        targets = ["/"]
    else:
        sect = "/" + url.strip("/").split("/")[0] + "/"
        targets = [sect]
    for t in targets:
        h = h.replace(f'<a href="{t}">', f'<a href="{t}" aria-current="page">')
        h = h.replace(f'<a class="m-home" href="{t}">', f'<a class="m-home" href="{t}" aria-current="page">')
    return h


def sync():
    changed = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not (rel_dir == "articles" and d == "content")]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                t = f.read()
            if 'lang="ar"' not in t[:300] or "</body>" not in t:
                continue
            m = HEADER_RE.search(t)
            if not m:
                continue
            new = header_for(os.path.relpath(path, ROOT), dark=bool(m.group(1)))
            t2 = t[:m.start()] + new + t[m.end():]
            if "/assets/nav.js" not in t2:
                i = t2.rfind("</body>")
                t2 = t2[:i] + NAV_JS + "\n" + t2[i:]
            if t2 != t:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(t2)
                changed.append(os.path.relpath(path, ROOT))
    print(f"header: updated {len(changed)} page(s)")


if __name__ == "__main__":
    sync()
