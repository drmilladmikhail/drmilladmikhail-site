#!/usr/bin/env python3
"""Build the dual-audience research page and the bilingual research library."""
from pathlib import Path
import json
import hashlib
import xml.etree.ElementTree as ET
from site_header import header_for, NAV_JS
from add_analytics import SECURITY, SNIPPET, inject_depth3d, ensure_social
import build_news
from breadcrumbs import process as add_breadcrumbs, auto_ld
ROOT = Path(__file__).resolve().parents[1]


def version_shared_assets(page, root):
    """Match the shared asset versioner so rebuilding creates no stale diffs."""
    page = ensure_social(build_news.inject(inject_depth3d(page)))
    for name in ('site.css', 'nav.js', 'depth3d.css', 'depth3d.js', 'nav-layout.css'):
        path = Path(root) / 'assets' / name
        if path.is_file():
            digest = hashlib.md5(path.read_bytes()).hexdigest()[:8]
            page = page.replace('/assets/' + name + '"',
                                '/assets/' + name + '?v=' + digest + '"')
    return page

CSS = '.research-page{max-width:1000px;margin:auto;padding:40px 20px;line-height:1.95;overflow-wrap:anywhere}.research-page h1{font-size:clamp(30px,5vw,46px)}.research-page article{background:#fff;border:1px solid #dbe3dc;border-radius:18px;padding:clamp(18px,4vw,34px);margin-top:28px}.research-page details{border:1px solid #dbe3dc;border-radius:12px;padding:16px;margin-block:20px}.research-page summary{cursor:pointer;font-weight:700;min-height:44px}.research-page .notice{background:#eef3ee;padding:16px;border-radius:10px;color:#304b3e}.research-page dt{font-weight:700}.research-page dd{margin-inline-start:0;margin-bottom:10px}.research-page a{color:#245b49}.research-page .tag{color:#416353}.research-page :focus-visible{outline:3px solid #326356;outline-offset:4px}'
LIB_CSS = '.library-page{max-width:1000px;margin:auto;padding:40px 20px 110px;line-height:1.95;overflow-wrap:anywhere}.library-page h1{font-size:clamp(28px,4.5vw,42px)}.lib-controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-block:22px;padding:14px;background:#eef3ee;border-radius:14px}.lib-controls input[type=search]{flex:1 1 240px;min-width:200px;padding:10px 12px;border:1px solid #c9d6cd;border-radius:10px;font:inherit}.lib-controls select,.lib-controls button{padding:10px 12px;border:1px solid #c9d6cd;border-radius:10px;background:#fff;font:inherit;cursor:pointer;min-height:44px}.lib-controls select{max-width:min(44vw,230px);text-overflow:ellipsis}.lib-controls .lang-btn{background:#2f6f62;color:#fff;border-color:#2f6f62;font-weight:700}#lib-count{font-weight:700;color:#416353}.lib-card{background:#fff;border:1px solid #dbe3dc;border-radius:18px;padding:clamp(16px,3vw,28px);margin-top:22px}.lib-card>h2{font-size:clamp(18px,2.6vw,24px);margin:6px 0 4px}.lib-card .alt-title{color:#5c6f66;font-size:95%}.lib-card .tag{color:#416353}.lib-card .authors{font-size:95%}.lib-card details{border:1px solid #dbe3dc;border-radius:12px;padding:12px 16px;margin-block:14px}.lib-card summary{cursor:pointer;font-weight:700;min-height:44px;display:flex;align-items:center}.abs-block{margin-top:12px;padding-top:10px;border-top:1px dashed #c9d6cd}.abs-block h3{margin:0 0 6px;font-size:100%}.abs-block p{margin:0}.lib-card .src{font-size:95%}.lib-pager{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:center;margin-block:26px}.lib-pager button{padding:8px 14px;border:1px solid #c9d6cd;border-radius:10px;background:#fff;cursor:pointer;min-height:44px;min-width:44px}.lib-pager [aria-current]{background:#2f6f62;color:#fff;border-radius:10px;padding:8px 14px}.library-page .notice{background:#eef3ee;padding:16px;border-radius:10px;color:#304b3e}.library-page a{color:#245b49}.library-page :focus-visible{outline:3px solid #326356;outline-offset:4px}main.library-page + .footer{padding-bottom:100px}.lib-today{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin-block:18px 0;padding:14px 16px;background:#2f6f62;color:#fff;border-radius:14px;font-weight:700}.lib-today[hidden]{display:none}.lib-today .today-text{display:inline-flex;align-items:center;gap:8px}.lib-today .today-dot{width:9px;height:9px;border-radius:50%;background:#ffd66b;display:inline-block}.lib-today button{font:inherit;font-weight:700;min-height:44px;padding:8px 16px;border-radius:10px;border:1px solid rgba(255,255,255,.45);background:rgba(255,255,255,.12);color:#fff;cursor:pointer}.lib-today button:hover{background:rgba(255,255,255,.22)}.lib-card .new-badge{display:inline-block;background:#b9862a;color:#fff;border-radius:8px;padding:1px 9px;font-size:85%;font-weight:700;margin-inline-start:8px}#lib-intro-count{font-weight:700;color:#2f6f62;margin:0}'


CSS += '''
.research-page article,.research-page details{background:var(--surface);border-color:var(--line);color:var(--ink)}
.research-page .notice{background:var(--mist);color:var(--ink)}
.research-page a,.research-page .tag{color:var(--eucalyptus)}
'''
LIB_CSS += '''
.library-page .lib-card{background:var(--surface);border-color:var(--line);color:var(--ink)}
.library-page a,#lib-count,#lib-intro-count{color:var(--eucalyptus)}
.lib-card .alt-title,.lib-card .tag{color:var(--muted)}
.lib-card details,.abs-block{border-color:var(--line)}
.lib-controls,.library-page .notice{background:var(--mist);color:var(--ink)}
.lib-controls input[type=search],.lib-controls select,.lib-controls button,.lib-pager button{
  background:var(--surface);color:var(--ink);border-color:var(--line)}
.lib-controls .lang-btn{background:#2f6f62;color:#fff;border-color:#2f6f62}
.lib-card .new-badge{background:var(--amber);color:#18233a}
'''

def build_library(root=ROOT):
    """Build /research/library/ : APA-journal papers, bilingual abstracts, search UI."""
    root = Path(root)
    data = json.loads((root / 'content/research-library.json').read_text(encoding='utf-8'))
    assert len(data) >= 50, 'library must hold at least the 50 seed papers'
    for r in data:
        for k in ('doi', 'title', 'title_ar', 'abstract', 'abstract_ar', 'authors', 'journal', 'journal_ar', 'volume', 'issue'):
            assert r.get(k), 'missing field ' + k + ' in ' + str(r.get('doi'))
    (root / 'assets/research-library-data.js').write_text(
        'window.RESEARCH_LIBRARY_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n',
        encoding='utf-8')
    head = ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">' + SECURITY +
            '<meta name="viewport" content="width=device-width,initial-scale=1">' +
            '<title>مكتبة الأكاديميين والباحثين | د. ميلاد ميخائيل</title>' +
            '<meta name="description" content="مكتبة أبحاث نفسية محكّمة من دوريات الجمعية الأمريكية لعلم النفس APA وغيرها، مع الملخص الأصلي بالإنجليزية وترجمته العربية الكاملة وروابط المصادر، وبحث يدعم اللغتين، وإضافات يومية.">' +
            '<link rel="canonical" href="https://drmilladmikhail.com/research/library/">' +
            '<link rel="stylesheet" href="/assets/site.css"><style>' + LIB_CSS + '</style></head><body>')
    body = ('<main id="main" class="library-page">' +
            '<p><a href="/">الرئيسية</a> / <a href="/research/">مرصد الأبحاث النفسية</a> / <span data-ar="مكتبة الأكاديميين والباحثين" data-en="Researchers Library">مكتبة الأكاديميين والباحثين</span></p>' +
            '<h1 data-ar="مكتبة الأكاديميين والباحثين" data-en="The Researchers Library">مكتبة الأكاديميين والباحثين</h1>' +
            '<p id="lib-intro-count" aria-live="polite"></p>' +
            '<p data-ar="مجموعة مختارة من الأبحاث المحكّمة في علم النفس والصحة النفسية من دوريات الجمعية الأمريكية لعلم النفس (APA) وغيرها من الدوريات المحكّمة، مع الملخص الأصلي بالإنجليزية وترجمته العربية الكاملة، وروابط المصدر للتحقق من كل بيانات، ويُضاف إليها بحثان جديدان يوميًا." data-en="A curated set of peer-reviewed papers in psychology and mental health from journals of the American Psychological Association (APA) and other refereed journals, each with the original English abstract and its full Arabic translation, plus source links for verification. Two new papers are added daily.">مجموعة مختارة من الأبحاث المحكّمة في علم النفس والصحة النفسية من دوريات الجمعية الأمريكية لعلم النفس (APA) وغيرها من الدوريات المحكّمة، مع الملخص الأصلي بالإنجليزية وترجمته العربية الكاملة، وروابط المصدر للتحقق من كل بيانات، ويُضاف إليها بحثان جديدان يوميًا.</p>' +
            '<p class="notice" data-ar="الترجمات العربية تحريرية كاملة للملخصات الأصلية المتاحة على PubMed أو موقع الناشر، وليست ترجمات معتمدة من الناشر؛ راجع المقال الأصلي قبل أي اقتباس. الترجمة للملخص (abstract) فقط وليست للبحث كاملًا، والملخص وحده لا يكفي للحكم على نتائج الدراسة أو لتغيير قرار صحي أو علاجي. ظهرت بعض الأبحاث إلكترونيًا قبل تاريخ العدد الورقي، والقائمة مختارة تحريريًا وليست حصرًا لأحدث ما نُشر." data-en="The Arabic translations are complete editorial renderings of original abstracts from PubMed or the publisher, not publisher-approved translations; consult the original article before citing. The translation covers the abstract only, not the full paper, and an abstract alone is not enough to judge a study or to change a health or treatment decision. Some papers appeared online before the print issue date, and this list is a curated selection, not an exhaustive index.">الترجمات العربية تحريرية كاملة للملخصات الأصلية المتاحة على PubMed أو موقع الناشر، وليست ترجمات معتمدة من الناشر؛ راجع المقال الأصلي قبل أي اقتباس. الترجمة للملخص (abstract) فقط وليست للبحث كاملًا، والملخص وحده لا يكفي للحكم على نتائج الدراسة أو لتغيير قرار صحي أو علاجي. ظهرت بعض الأبحاث إلكترونيًا قبل تاريخ العدد الورقي، والقائمة مختارة تحريريًا وليست حصرًا لأحدث ما نُشر.</p>' +
            '<div id="lib-today" class="lib-today" hidden></div>' +
            '<section class="lib-controls" aria-label="أدوات البحث والتصفح">' +
            '<input type="search" id="lib-search" placeholder="ابحث بالعربية أو الإنجليزية" aria-label="بحث في المكتبة">' +
            '<select id="lib-journal" aria-label="تصفية حسب الدورية"><option value="all">كل الدوريات</option></select>' +
            '<select id="lib-sort" aria-label="ترتيب النتائج"><option value="journal">حسب الدورية</option><option value="title">حسب العنوان</option></select>' +
            '<button type="button" id="lib-search-btn">مسح البحث والفلاتر</button>' +
            '<button type="button" id="lib-lang" class="lang-btn" lang="en">English</button>' +
            '</section>' +
            '<p id="lib-count" aria-live="polite"></p>' +
            '<div id="lib-results"></div>' +
            '<nav id="lib-pager" aria-label="التنقل بين صفحات النتائج"></nav>' +
            '<noscript><p class="notice">عرض المكتبة والبحث فيها يحتاج تشغيل الجافاسكريبت في المتصفح. يمكنك أيضًا مراجعة ملف البيانات الكامل على /assets/research-library-data.js أو صفحة المصدر لكل بحث عبر PubMed أو موقع الناشر.</p></noscript>' +
            '<p class="notice" data-ar="المحتوى للتثقيف والبحث، وليس تشخيصًا أو توصية علاجية فردية." data-en="Content is for education and research, not diagnosis or individual treatment advice.">المحتوى للتثقيف والبحث، وليس تشخيصًا أو توصية علاجية فردية.</p>' +
            '</main>')
    page = (head + header_for('research/library/index.html') + body +
            '<footer class="footer"><div class="wrap"><a href="/research/">مرصد الأبحاث النفسية</a> · <a href="/articles/">المقالات</a> · <a href="/contact/">تواصل</a></div></footer>' +
            ''.join('<script src="/assets/' + name + '?v=' +
                    hashlib.sha256((root / 'assets' / name).read_bytes()).hexdigest()[:12] +
                    '" defer></script>' for name in ('research-library-data.js', 'research-library.js')) +
            NAV_JS + SNIPPET + '</body></html>')
    out = root / 'research/library/index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    page = version_shared_assets(page, root)
    out.write_text(page, encoding='utf-8')
    add_breadcrumbs(str(out), 'library', str(root))
    page = out.read_text(encoding='utf-8')
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    path = root / 'sitemap.xml'
    tree = ET.parse(path)
    url = 'https://drmilladmikhail.com/research/library/'
    if not any(e.text == url for e in tree.findall('.//{' + ns + '}loc')):
        entry = ET.SubElement(tree.getroot(), '{' + ns + '}url')
        ET.SubElement(entry, '{' + ns + '}loc').text = url
        tree.write(path, encoding='utf-8', xml_declaration=True)
    return page

def build(root=ROOT):
    root = Path(root)
    body = (root / 'content/research-body.html').read_text(encoding='utf-8')
    assert body.count('<h1>') == 1 and 'id="main"' in body
    head = '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">' + SECURITY + '<meta name="viewport" content="width=device-width,initial-scale=1"><title>مرصد الأبحاث النفسية | د. ميلاد ميخائيل</title><meta name="description" content="أبحاث علم النفس بعرض أكاديمي نقدي وشرح مبسط، مع المصدر الإنجليزي والترجمة العربية وحدود الاستنتاج."><link rel="canonical" href="https://drmilladmikhail.com/research/"><link rel="stylesheet" href="/assets/site.css"><style>' + CSS + '</style></head><body>'
    page = head + header_for('research/index.html') + body + '<footer class="footer"><div class="wrap"><a href="/articles/">المقالات</a> · <a href="/contact/">تواصل</a></div></footer>' + NAV_JS + SNIPPET + '</body></html>'
    output = root / 'research/index.html'
    output.parent.mkdir(parents=True, exist_ok=True)
    page = version_shared_assets(page, root)
    output.write_text(page, encoding='utf-8')
    auto_ld(root)  # same BreadcrumbList data add_analytics gives other pages
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    path = root / 'sitemap.xml'
    tree = ET.parse(path)
    url = 'https://drmilladmikhail.com/research/'
    if not any(e.text == url for e in tree.findall('.//{' + ns + '}loc')):
        entry = ET.SubElement(tree.getroot(), '{' + ns + '}url')
        ET.SubElement(entry, '{' + ns + '}loc').text = url
        tree.write(path, encoding='utf-8', xml_declaration=True)
    home = root / 'index.html'
    text = home.read_text(encoding='utf-8')
    marker = '<!-- RESEARCH-LINK -->'
    if marker not in text:
        assert '</main>' in text
        # The observatory is linked from the menu (site_header.py), not the homepage.
        home.write_text(text.replace('</main>', marker + '</main>', 1), encoding='utf-8')
    return page

if __name__ == '__main__':
    build()
    build_library()
