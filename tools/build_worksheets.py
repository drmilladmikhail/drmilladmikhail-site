#!/usr/bin/env python3
"""Build the printable worksheets (PDF) for drmilladmikhail.com/worksheets/.

Data:    content/worksheets.json  (one entry per worksheet, see content/WORKSHEETS-HOWTO.md)
Output:  worksheets/<slug>.pdf     A4, Arabic RTL, fonts embedded
         worksheets/<slug>.webp    preview of page 1 for the library page
         worksheets/manifest.json  content hash, pages and size per worksheet

A PDF is only rebuilt when its entry in worksheets.json changed (or the PDF is missing),
so re-running doesn't create noisy git diffs. Force all with --force, one with --only <slug>.
Needs Playwright + Chromium and pdftoppm. Afterwards run tools/build_articles.py
(it rebuilds the /worksheets/ page and the sitemap).
"""
import hashlib
import html
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT = os.path.join(ROOT, "worksheets")
TEMPLATE_VERSION = "4"  # safety contact correction and its official citation

AR_URL, EN_URL = "amazon.com/dp/B0HPNCYWWS", "amazon.com/dp/B0HPRPSPWF"


def esc(s):
    return html.escape(s, quote=True)


CSS = f"""
@font-face {{ font-family: "Naskh"; src: url("file://{FONTS}/naskh-700.ttf"); font-weight: 700; }}
@font-face {{ font-family: "Plex"; src: url("file://{FONTS}/plexar-400.ttf"); font-weight: 400; }}
@font-face {{ font-family: "Plex"; src: url("file://{FONTS}/plexar-600.ttf"); font-weight: 600; }}
@page {{ size: A4; margin: 15mm 16mm 13mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Plex", sans-serif; color: #18233a; font-size: 11.3pt; line-height: 1.7; }}
.top {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 3px solid #2f6f62; padding-bottom: 6px; margin-bottom: 8px; }}
.top .tag {{ color: #b9862a; font-weight: 600; font-size: 10pt; }}
.top .site {{ color: #566274; font-size: 9pt; direction: ltr; }}
h1 {{ font-family: "Naskh", serif; font-size: 25pt; margin: 4px 0 2px; line-height: 1.4; }}
h1 span {{ color: #2f6f62; }}
.intro {{ margin: 0 0 8px; color: #33405a; }}
section {{ break-inside: avoid; }}
h2 {{ font-family: "Naskh", serif; font-size: 13.5pt; color: #2f6f62; margin: 15px 0 3px; display: flex; gap: 8px; align-items: center; line-height: 1.5; }}
h2 .n {{ flex: none; display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 50%; background: #2f6f62; color: #fff; font-family: "Plex"; font-size: 10.5pt; }}
.hint {{ margin: 0 0 3px; color: #566274; font-size: 10pt; }}
.lines div {{ border-bottom: 1px solid #b7c6bf; height: 31px; }}
.examples {{ background: #dfe9e4; border-radius: 10px; padding: 7px 14px; margin: 3px 0 6px; font-size: 10.5pt; }}
.examples p {{ margin: 2px 0; }}
.checks {{ list-style: none; margin: 4px 0 6px; padding: 0; columns: 2; column-gap: 18px; }}
.checks li {{ break-inside: avoid; display: flex; gap: 8px; align-items: flex-start; margin: 0 0 5px; font-size: 10.5pt; }}
.checks li::before {{ content: ""; flex: none; width: 13px; height: 13px; margin-top: 5px; border: 1.5px solid #2f6f62; border-radius: 3px; }}
.words {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 6px; }}
.words span {{ border: 1px solid #b7c6bf; border-radius: 999px; padding: 1px 11px; font-size: 10pt; background: #f4f8f6; }}
table {{ width: 100%; border-collapse: collapse; margin: 4px 0 6px; table-layout: fixed; }}
th {{ background: #2f6f62; color: #fff; font-weight: 600; font-size: 9.5pt; padding: 5px 6px; text-align: right; border: 1px solid #2f6f62; line-height: 1.4; }}
td {{ border: 1px solid #b7c6bf; height: 36px; padding: 3px 6px; font-size: 9.5pt; color: #33405a; vertical-align: top; }}
table.tall td {{ height: 46px; }}
td.lab {{ background: #f4f8f6; font-weight: 600; }}
.box {{ border: 1.5px dashed #b9862a; border-radius: 10px; padding: 6px 14px 4px; margin-top: 10px; }}
.box h2 {{ margin-top: 2px; }}
.circles {{ display: block; margin: 4px auto 0; width: 150mm; height: auto; }}
.note {{ margin-top: 12px; font-size: 9.5pt; color: #566274; border-top: 1px solid #d6dfda; padding-top: 6px; }}
.note b {{ color: #18233a; }}
.foot {{ margin-top: 8px; display: flex; justify-content: space-between; gap: 12px; font-size: 9pt; color: #33405a; }}
.foot .ltr {{ direction: ltr; text-align: left; }}
.pb {{ break-before: page; }}
"""


def lines(n):
    return f'<div class="lines">{"<div></div>" * n}</div>' if n else ""


def circles_svg(labels):
    """Three rings (inner = closest people). Labels sit at the top of each ring."""
    r = [62, 128, 196]
    cx, cy = 210, 205
    fills = ["#dfe9e4", "#eef4f1", "#f8faf9"]
    out = [f'<svg class="circles" viewBox="0 0 420 410" xmlns="http://www.w3.org/2000/svg" role="img">']
    for rad, fill in reversed(list(zip(r, fills))):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{fill}" stroke="#2f6f62" stroke-width="1.6"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#b9862a"/>')
    out.append(f'<text x="{cx}" y="{cy + 26}" text-anchor="middle" font-family="Plex" font-size="11" fill="#566274">أنا</text>')
    for i, lab in enumerate(labels[:3]):
        y = cy - r[i] + 20 if i else cy - 30
        out.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="Naskh" font-weight="700" font-size="14" fill="#2f6f62">{esc(lab)}</text>')
    out.append("</svg>")
    return "".join(out)


def section_html(n, s):
    parts = []
    if s.get("words"):
        parts.append('<div class="words">' + "".join(f"<span>{esc(w)}</span>" for w in s["words"]) + "</div>")
    if s.get("examples"):
        parts.append('<div class="examples">' + "".join(f"<p>• {esc(e)}</p>" for e in s["examples"]) + "</div>")
    if s.get("checks"):
        parts.append('<ul class="checks">' + "".join(f"<li>{esc(c)}</li>" for c in s["checks"]) + "</ul>")
    if s.get("hint"):
        parts.append(f'<p class="hint">{esc(s["hint"])}</p>')
    if s.get("circles"):
        parts.append(circles_svg(s["circles"]))
    if s.get("table"):
        t = s["table"]
        labels = t.get("labels")
        head = "".join(f"<th>{esc(c)}</th>" for c in t["cols"])
        widths = ""
        if labels and max(len(x) for x in labels) <= 2:
            widths = '<colgroup><col style="width:9%">' + "<col>" * (len(t["cols"]) - 1) + "</colgroup>"
        rows = ""
        for i in range(t["rows"]):
            first = f'<td class="lab">{esc(labels[i])}</td>' if labels else "<td></td>"
            rows += "<tr>" + first + "<td></td>" * (len(t["cols"]) - 1) + "</tr>"
        cls = ' class="tall"' if t["rows"] <= 5 else ""
        parts.append(f"<table{cls}>{widths}<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>")
    parts.append(lines(s.get("lines", 0)))
    if s.get("hint2"):
        parts.append(f'<p class="hint" style="margin-top:6px">{esc(s["hint2"])}</p>')
    parts.append(lines(s.get("lines2", 0)))
    h = f'<h2><span class="n">{n}</span> {esc(s["t"])}</h2>'
    inner = h + "".join(parts)
    pb = '<div class="pb"></div>' if s.get("break") == "force" else ""  # normally let sections flow
    if s.get("box"):
        return f'{pb}<section class="box">{inner}</section>'
    return f"{pb}<section>{inner}</section>"


def worksheet_html(w):
    title = w["title"]
    acc = w.get("accent")
    if acc and title.endswith(acc):
        h1 = f'{esc(title[: -len(acc)])}<span>{esc(acc)}</span>'
    else:
        h1 = esc(title)
    secs = "\n".join(section_html(i, s) for i, s in enumerate(w["sections"], 1))
    extra = f' {esc(w["extra_note"])}' if w.get("extra_note") else ""
    return f"""<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{esc(title)} — ورقة تمرين</title><style>{CSS}</style></head>
<body>
<div class="top"><span class="tag">ورقة تمرين مجانية</span><span class="site">drmilladmikhail.com/worksheets</span></div>
<h1>{h1}</h1>
<p class="intro">{esc(w["intro"])}</p>
{secs}
<p class="note"><b>تنبيه:</b> ده تمرين للتأمل وفهم النفس، مش تشخيص ولا بديل عن العلاج النفسي.{extra} لو حاسس بضيق جامد أو خايف على نفسك، كلّم متخصص أو حد بتثق فيه فورًا — مصر: 16328<sup>1</sup> · أمريكا: 988.</p>
<p style="font-size:8pt">1. رقم الأمانة العامة للصحة النفسية: <a href="https://www.100millionseha.eg/happiness">https://www.100millionseha.eg/happiness</a></p>
<div class="foot">
<div>من عالم كتاب <b>«ليه بنحب اللي بيوجعنا؟»</b><br>د. ميلاد ميخائيل — دكتوراه في الصحة النفسية، جامعة قناة السويس</div>
<div class="ltr">Arabic: {AR_URL}<br>English: {EN_URL}<br>drmilladmikhail.com</div>
</div>
</body></html>"""


def digest(w):
    return hashlib.sha256((TEMPLATE_VERSION + json.dumps(w, ensure_ascii=False, sort_keys=True)).encode()).hexdigest()[:16]


def pdf_pages(path):
    out = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 1


def main():
    args = sys.argv[1:]
    force = "--force" in args
    only = args[args.index("--only") + 1] if "--only" in args else None
    with open(os.path.join(ROOT, "content", "worksheets.json"), encoding="utf-8") as f:
        data = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(OUT, "manifest.json")
    manifest = {}
    if os.path.exists(mpath):
        with open(mpath, encoding="utf-8") as f:
            manifest = json.load(f)
    todo = []
    for w in data["items"]:
        pdf = os.path.join(OUT, w["slug"] + ".pdf")
        h = digest(w)
        if force or (only == w["slug"]) or (not only and (manifest.get(w["slug"], {}).get("hash") != h or not os.path.exists(pdf))):
            todo.append((w, h))
    if todo:
        from playwright.sync_api import sync_playwright
        from PIL import Image
        with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
            browser = p.chromium.launch()
            page = browser.new_page()
            for w, h in todo:
                src = os.path.join(tmp, w["slug"] + ".html")
                with open(src, "w", encoding="utf-8") as f:
                    f.write(worksheet_html(w))
                page.goto("file://" + src)
                page.evaluate("document.fonts.ready")
                pdf = os.path.join(OUT, w["slug"] + ".pdf")
                page.pdf(path=pdf, format="A4", print_background=True, prefer_css_page_size=True)
                # Keep metadata explicit while preserving every page and link.
                from pypdf import PdfReader, PdfWriter
                writer = PdfWriter(clone_from=PdfReader(pdf))
                writer.add_metadata({"/Title": w.get("title", w["slug"]),
                                     "/Author": "Perplexity Computer"})
                writer.write(pdf + ".metadata.pdf")
                os.replace(pdf + ".metadata.pdf", pdf)
                png = os.path.join(tmp, "prev")
                subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "70", "-png", "-singlefile", pdf, png], check=True)
                img = Image.open(png + ".png").convert("RGB")
                img.thumbnail((480, 680))
                img.save(os.path.join(OUT, w["slug"] + ".webp"), "WEBP", quality=72)
                manifest[w["slug"]] = {"hash": h, "pages": pdf_pages(pdf), "kb": round(os.path.getsize(pdf) / 1024),
                                       "w": img.width, "h": img.height}
                print("built", w["slug"], manifest[w["slug"]])
            browser.close()
    slugs = {w["slug"] for w in data["items"]}
    manifest = {k: v for k, v in manifest.items() if k in slugs}
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print(f"worksheets: {len(todo)} built, {len(manifest)} total")


if __name__ == "__main__":
    main()
