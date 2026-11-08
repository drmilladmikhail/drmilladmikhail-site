#!/usr/bin/env python3
"""Build the first dual-audience research page using the unchanged shared header."""
from pathlib import Path
import xml.etree.ElementTree as ET
from site_header import header_for, NAV_JS
from add_analytics import SECURITY, SNIPPET
ROOT = Path(__file__).resolve().parents[1]
CSS = '.research-page{max-width:1000px;margin:auto;padding:40px 20px;line-height:1.95;overflow-wrap:anywhere}.research-page h1{font-size:clamp(30px,5vw,46px)}.research-page article{background:#fff;border:1px solid #dbe3dc;border-radius:18px;padding:clamp(18px,4vw,34px);margin-top:28px}.research-page details{border:1px solid #dbe3dc;border-radius:12px;padding:16px;margin-block:20px}.research-page summary{cursor:pointer;font-weight:700;min-height:44px}.research-page .notice{background:#eef3ee;padding:16px;border-radius:10px;color:#304b3e}.research-page dt{font-weight:700}.research-page dd{margin-inline-start:0;margin-bottom:10px}.research-page a{color:#245b49}.research-page .tag{color:#416353}.research-page :focus-visible{outline:3px solid #326356;outline-offset:4px}'

def build(root=ROOT):
    root = Path(root)
    body = (root / 'content/research-body.html').read_text(encoding='utf-8')
    assert body.count('<h1>') == 1 and 'id="main"' in body
    head = '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">' + SECURITY + '<meta name="viewport" content="width=device-width,initial-scale=1"><title>مرصد الأبحاث النفسية | د. ميلاد ميخائيل</title><meta name="description" content="أبحاث علم النفس بعرض أكاديمي نقدي وشرح مبسط، مع المصدر الإنجليزي والترجمة العربية وحدود الاستنتاج."><link rel="canonical" href="https://drmilladmikhail.com/research/"><link rel="stylesheet" href="/assets/site.css"><style>' + CSS + '</style></head><body>'
    page = head + header_for('research/index.html') + body + '<footer class="footer"><div class="wrap"><a href="/articles/">المقالات</a> · <a href="/contact/">تواصل</a></div></footer>' + NAV_JS + SNIPPET + '</body></html>'
    output = root / 'research/index.html'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding='utf-8')
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
        link = marker + '<div class="wrap"><p><a href="/research/">مرصد الأبحاث النفسية: عرض علمي وشرح مبسط</a></p></div>'
        home.write_text(text.replace('</main>', link + '</main>', 1), encoding='utf-8')
    return page

if __name__ == '__main__':
    build()
