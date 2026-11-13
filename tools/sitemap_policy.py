#!/usr/bin/env python3
"""Apply the current sitemap policy after site generation."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
SITE = "https://drmilladmikhail.com"
# 2026-11-11 SEO brief
IDENTITY = ("about", "about/qualifications", "about/publications", "family", "en/about")
PRIVATE = {SITE + "/saved/", SITE + "/my-space/", SITE + "/newsletter/thanks/"}
ET.register_namespace("", NS)
ET.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")


def serialize(tree):
    body = ET.tostring(tree.getroot(), encoding="unicode")
    body = re.sub(r">\s+<", "><", body).replace(" />", "/>")
    body = body.replace("<url>", "\n  <url>").replace("</urlset>", "\n</urlset>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"


def apply(root):
    root = Path(root)
    path = root / "sitemap.xml"
    original = path.read_text(encoding="utf-8")
    tree = ET.ElementTree(ET.fromstring(original))
    urls = tree.getroot()
    if urls.tag != f"{{{NS}}}urlset":
        raise ValueError("Unexpected sitemap root")
    # lastmod only where we know the real date of the last content change (articles: "updated"/"date"
    # in articles/articles.json). A date that changes on every build teaches Google to ignore it.
    import json
    real = {}
    try:
        data = json.loads((root / "articles/articles.json").read_text(encoding="utf-8"))
        for a in (data.get("articles", data) if isinstance(data, dict) else data):
            d = a.get("updated") or a.get("date")
            if a.get("slug") and d:
                real[f"{SITE}/articles/{a['slug']}/"] = str(d)[:10]
    except (OSError, ValueError):
        pass
    try:  # English adaptations (en/articles/articles.json)
        for a in json.loads((root / "en/articles/articles.json").read_text(encoding="utf-8")):
            d = a.get("updated") or a.get("date")
            if a.get("slug") and d:
                real[f"{SITE}/en/articles/{a['slug']}/"] = str(d)[:10]
    except (OSError, ValueError):
        pass
    for entry in urls.findall(f"{{{NS}}}url"):
        for date in entry.findall(f"{{{NS}}}lastmod"):
            entry.remove(date)
        loc = entry.find(f"{{{NS}}}loc")
        if loc is not None and loc.text in real:
            ET.SubElement(entry, f"{{{NS}}}lastmod").text = real[loc.text]
    for entry in list(urls.findall(f"{{{NS}}}url")):
        loc = entry.find(f"{{{NS}}}loc")
        if loc is not None and loc.text in PRIVATE:
            urls.remove(entry)
    locations = {node.text for node in urls.findall(f"{{{NS}}}url/{{{NS}}}loc")}
    for slug in IDENTITY:
        target = SITE + "/" + slug + "/"
        if (root / slug / "index.html").is_file() and target not in locations:
            entry = ET.SubElement(urls, f"{{{NS}}}url")
            ET.SubElement(entry, f"{{{NS}}}loc").text = target
            locations.add(target)
    target = SITE + "/myth-fact/"
    if (root / "myth-fact" / "index.html").is_file() and target not in locations:
        entry = ET.SubElement(urls, f"{{{NS}}}url")
        ET.SubElement(entry, f"{{{NS}}}loc").text = target
    output = serialize(tree)
    if output == original:
        return False
    temporary = path.with_suffix(".xml.tmp")
    try:
        temporary.write_text(output, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return True


if __name__ == "__main__":
    apply(Path(__file__).resolve().parents[1])
