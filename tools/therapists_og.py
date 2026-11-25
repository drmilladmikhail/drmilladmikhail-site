#!/usr/bin/env python3
"""Share image (1200x630) for a therapist page: photo, name, title, specialties.

Used by tools/sync_therapists.py. This is what WhatsApp/Facebook show when someone
shares /therapists/<slug>/, so it carries the therapist's identity, not the site's.
"""
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
W, H = 1200, 630
DEEP = (28, 58, 58)
GOLD = (201, 162, 39)
CREAM = (243, 239, 226)
WHITE = (255, 255, 255)
SOFT = (205, 220, 216)
RTL = {"direction": "rtl", "language": "ar"}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)


def fit(draw, text, name, sizes, width):
    for s in sizes:
        f = font(name, s)
        if draw.textlength(text, font=f, **RTL) <= width:
            return f
    return font(name, sizes[-1])


def initial(name):
    rest = (name or "").replace("د.", "", 1)
    for ch in rest:
        if ch.isalpha():
            return ch
    return "د"


def make(data, out, photo=None):
    im = Image.new("RGB", (W, H), DEEP)
    d = ImageDraw.Draw(im)
    # soft ring on the right (RTL start) for the photo
    size, cx, cy = 340, W - 90 - 170, H // 2 - 10
    box = (cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2)
    d.ellipse((box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10), fill=GOLD)
    if photo and os.path.exists(photo):
        pic = ImageOps.fit(Image.open(photo).convert("RGB"), (size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        im.paste(pic, box[:2], mask)
    else:
        d.ellipse(box, fill=CREAM)
        d.text((cx, cy), initial(data.get("name")), font=font("naskh-700.ttf", 170), fill=DEEP, anchor="mm", **RTL)

    right = box[0] - 60          # text column ends here (RTL: text is right-aligned to this x)
    width = right - 70
    name = data.get("name") or ""
    nf = fit(d, name, "naskh-700.ttf", (76, 68, 60, 52, 46, 40), width)
    d.text((right, 190), name, font=nf, fill=WHITE, anchor="rs", **RTL)
    title = data.get("title") or "معالج نفسي"
    d.text((right, 262), title, font=fit(d, title, "plexar-600.ttf", (40, 36, 32), width), fill=GOLD, anchor="rs", **RTL)

    specs = [s for s in (data.get("specialties") or []) if s][:4]
    if specs:
        line = " · ".join(specs)
        d.text((right, 340), line, font=fit(d, line, "plexar-400.ttf", (34, 30, 28, 26), width), fill=SOFT, anchor="rs", **RTL)

    d.rounded_rectangle((70, 430, right, 432), radius=1, fill=(60, 96, 96))
    d.text((right, 500), "جلسات نفسية أونلاين · احجز من الصفحة", font=font("plexar-400.ttf", 30), fill=SOFT, anchor="rs", **RTL)
    d.rectangle((0, H - 12, W, H), fill=GOLD)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "JPEG", quality=84, optimize=True, progressive=True)


if __name__ == "__main__":
    import json
    import sys
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    make(data, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
