#!/usr/bin/env python3
"""Build optimized images and social-share cards for drmilladmikhail.com.

Run:  python3 tools/build_images.py
(build_articles.py calls it automatically.)

It writes, only when missing or older than the source:
  assets/book/<name>.webp        1000px WebP of every book illustration (source JPG is also capped at 1000px)
  assets/book/<name>-600.webp    600px WebP (cards, phones)
  assets/og/<slug>.jpg           1200x630 share card for every article (title + book image)
  assets/og/home.jpg, home-en.jpg, articles.jpg, tests.jpg   share cards for main pages

Needs Pillow with libraqm (Arabic shaping). Fonts live in tools/fonts/ (SIL OFL).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont, features

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
BOOK = os.path.join(ROOT, "assets", "book")
OG = os.path.join(ROOT, "assets", "og")

PAPER = (245, 247, 244)
INK = (24, 35, 58)
MUTED = (86, 98, 116)
GREEN = (47, 111, 98)
AMBER = (185, 134, 42)
W, H = 1200, 630
PANEL = 560  # image width on the left
PAD = 64
MAX_W = 1000  # largest book-image width; article column is ~700px


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)


def stale(out, *srcs):
    if not os.path.exists(out):
        return True
    t = os.path.getmtime(out)
    return any(os.path.getmtime(s) > t for s in srcs if os.path.exists(s))


def shrink_sources():
    """Cap new book JPGs at MAX_W px and recompress them (they are fallbacks and share-card sources)."""
    for fn in sorted(os.listdir(BOOK)):
        if not fn.endswith(".jpg"):
            continue
        src = os.path.join(BOOK, fn)
        im = Image.open(src)
        if im.width > MAX_W:
            im = im.convert("RGB").resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
            im.save(src, "JPEG", quality=76, optimize=True, progressive=True)


def webp_variants():
    shrink_sources()
    n = 0
    for fn in sorted(os.listdir(BOOK)):
        if not fn.endswith(".jpg"):
            continue
        src = os.path.join(BOOK, fn)
        base = src[:-4]
        for suffix, width in (("", None), ("-600", 600)):
            out = f"{base}{suffix}.webp"
            if not stale(out, src):
                continue
            im = Image.open(src).convert("RGB")
            w = width or min(im.width, MAX_W)
            if im.width > w:
                im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            im.save(out, "WEBP", quality=65, method=6)
            n += 1
    return n


def cover(im, w, h):
    """Crop-to-fill like CSS object-fit: cover."""
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def wrap(draw, text, fnt, width, rtl=True):
    kw = {"direction": "rtl", "language": "ar"} if rtl else {}
    words, lines, cur = text.split(), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=fnt, **kw) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def card(out, image_path, kicker, title, foot, rtl=True, title_font="naskh-700.ttf"):
    im = Image.new("RGB", (W, H), PAPER)
    pic = cover(Image.open(image_path).convert("RGB"), PANEL, H)
    im.paste(pic, (0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, H - 14, W, H), fill=GREEN)
    d.rectangle((PANEL, 0, PANEL + 6, H - 14), fill=AMBER)
    kw = {"direction": "rtl", "language": "ar"} if rtl else {}
    x_text = W - PAD if rtl else PANEL + PAD
    anchor = "ra" if rtl else "la"
    width = W - PANEL - 2 * PAD
    # kicker
    kf = font("plexar-600.ttf", 26)
    d.text((x_text, 70), kicker, font=kf, fill=GREEN, anchor=anchor, **kw)
    # title: shrink until it fits in 5 lines
    for size in (60, 54, 48, 44, 40, 36):
        tf = font(title_font, size)
        lines = wrap(d, title, tf, width, rtl)
        lh = round(size * 1.55)
        if len(lines) <= 5 and 130 + lh * len(lines) <= H - 150:
            break
    y = 130
    for ln in lines:
        d.text((x_text, y), ln, font=tf, fill=INK, anchor=anchor, **kw)
        y += lh
    # footer: name (Arabic or English) + domain
    ff = font("plexar-600.ttf", 28)
    d.text((x_text, H - 118), foot, font=ff, fill=INK, anchor=anchor, **kw)
    lf = font("plexar-400.ttf", 26)
    d.text((x_text, H - 74), "drmilladmikhail.com", font=lf, fill=MUTED, anchor=anchor)
    im.save(out, "JPEG", quality=80, optimize=True, progressive=True)


def main():
    if not features.check("raqm"):
        sys.exit("Pillow was built without libraqm: Arabic text would render broken. Install a Pillow wheel with raqm.")
    os.makedirs(OG, exist_ok=True)
    n_webp = webp_variants()
    with open(os.path.join(ROOT, "articles", "articles.json"), encoding="utf-8") as f:
        items = json.load(f)
    me = "د. ميلاد منير ميخائيل"
    jobs = []
    for a in items:
        src = os.path.join(BOOK, a["image"] + ".jpg")
        jobs.append((os.path.join(OG, a["slug"] + ".jpg"), src,
                     "من كتاب «ليه بنحب اللي بيوجعنا؟»", a["title"], me, True))
    portrait = os.path.join(ROOT, "assets", "millad.jpg")
    jobs += [
        (os.path.join(OG, "home.jpg"), portrait, "حاصل على الدكتوراه في الصحة النفسية",
         "د. ميلاد منير ميخائيل: مقالات واختبارات وكتب عن الحب والعلاقات والصحة النفسية", "جامعة قناة السويس · عضو APA", True),
        (os.path.join(OG, "articles.jpg"), os.path.join(BOOK, "love-p09.jpg"), "المقالات",
         "مقالات بالعامية عن الحب والتعلق والعلاقات المؤذية واختيار شريك الحياة", me, True),
        (os.path.join(OG, "tests.jpg"), os.path.join(BOOK, "love-p16.jpg"), "اختبارات مجانية",
         "اختبارات نفسية علمية بالعربي: نمط التعلق، القلق، الاكتئاب، تقدير الذات", me, True),
        (os.path.join(OG, "home-en.jpg"), portrait, "Ph.D. in Mental Health · Suez Canal University",
         "Dr. Millad Mikhail — Mental Health Educator and Author", "APA member · Author", False),
    ]
    n_og = 0
    script = os.path.abspath(__file__)
    for out, src, kicker, title, foot, rtl in jobs:
        if stale(out, src, script, os.path.join(ROOT, "articles", "articles.json")):
            card(out, src, kicker, title, foot, rtl, "naskh-700.ttf" if rtl else "newsreader-600.woff")
            n_og += 1
    print(f"images: {n_webp} webp written, {n_og} share card(s) written")


if __name__ == "__main__":
    main()
