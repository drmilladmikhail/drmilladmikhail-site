#!/usr/bin/env python3
"""Apply the current sitemap policy after site generation."""
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
SITE = "https://drmilladmikhail.com"
ET.register_namespace("", NS)
ET.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")


def apply(root):
    root = Path(root)
    path = root / "sitemap.xml"
    tree = ET.parse(path)
    urls = tree.getroot()
    if urls.tag != f"{{{NS}}}urlset":
        raise ValueError("Unexpected sitemap root")
    changed = False
    for entry in urls.findall(f"{{{NS}}}url"):
        for date in entry.findall(f"{{{NS}}}lastmod"):
            entry.remove(date)
            changed = True
    locations = {node.text for node in urls.findall(f"{{{NS}}}url/{{{NS}}}loc")}
    target = SITE + "/myth-fact/"
    if (root / "myth-fact" / "index.html").is_file() and target not in locations:
        entry = ET.SubElement(urls, f"{{{NS}}}url")
        ET.SubElement(entry, f"{{{NS}}}loc").text = target
        changed = True
    if changed:
        ET.indent(tree, space="  ")
        temporary = path.with_suffix(".xml.tmp")
        try:
            tree.write(temporary, encoding="UTF-8", xml_declaration=True)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    return changed


if __name__ == "__main__":
    apply(Path(__file__).resolve().parents[1])
