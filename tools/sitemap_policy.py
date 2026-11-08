#!/usr/bin/env python3
"""Apply the current sitemap policy after site generation."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
SITE = "https://drmilladmikhail.com"
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
    for entry in urls.findall(f"{{{NS}}}url"):
        for date in entry.findall(f"{{{NS}}}lastmod"):
            entry.remove(date)
    locations = {node.text for node in urls.findall(f"{{{NS}}}url/{{{NS}}}loc")}
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
