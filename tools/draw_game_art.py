#!/usr/bin/env python3
"""Caricature pictures for the «بطاريتي 1%» game — one per scene (assets/game/art/<id>.webp).

A small drawing kit: big-head caricature people with exaggerated faces, a few settings that follow the
time of day, and props. Every scene in assets/game/data.js has an "art" id that must exist in ART below.

Run:  python3 tools/draw_game_art.py            # writes assets/game/art/*.webp (800×500)
      python3 tools/draw_game_art.py --sheet F   # also writes a contact sheet PNG to F (for checking)
Needs rsvg-convert and Pillow, and the site fonts installed for rsvg (cp tools/fonts/*.ttf ~/.local/share/fonts && fc-cache -f).
"""
import io, math, os, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "game", "art")
W, H = 800, 500

# palette
INK = "#24304a"; TEAL = "#2f6f62"; TEAL2 = "#4c8f80"; GOLD = "#e2b35a"; GOLD2 = "#b9862a"; RED = "#e0675a"
PINK = "#f2a7a0"; SKY = "#9fd0ee"; WHITE = "#ffffff"; CREAM = "#fbf6ec"; GREY = "#9aa6b5"; BLUSH = "#f39a8c"
SKIN = {"a": "#f0c39e", "b": "#d9a074", "c": "#b97f56"}
SKYCOL = {"dawn": ("#f7b98d", "#fbe3c4"), "morning": ("#8fcbee", "#e3f3fb"), "noon": ("#6fb7e8", "#d6eefa"),
          "afternoon": ("#f0b968", "#f8e2ba"), "evening": ("#a65a44", "#5a4a8a"), "night": ("#25335f", "#121a33"),
          "late": ("#141b33", "#080c18")}
WALL = {"dawn": "#f6e2cf", "morning": "#e8f0ee", "noon": "#eef3ea", "afternoon": "#f5e7d0", "evening": "#e6d6cf",
        "night": "#c9cfe0", "late": "#9aa3bd"}


def P(d, fill, extra=""):
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def S(d, color=INK, w=5, extra=""):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def C(x, y, r, fill, extra=""):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" {extra}/>'


def E(x, y, rx, ry, fill, extra=""):
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" {extra}/>'


def R(x, y, w, h, fill, rx=8, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" {extra}/>'


def T(x, y, txt, size=30, fill=INK, weight=800, anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Arabic, DejaVu Sans, sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" direction="ltr">{txt}</text>')


# ------------------------------------------------------------------ settings
def sky(part, x, y, w, h):
    a, b = SKYCOL[part]
    sid = f"sk{abs(hash((part, x, y))) % 9999}"
    s = (f'<defs><linearGradient id="{sid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/>'
         f'<stop offset="1" stop-color="{b}"/></linearGradient></defs>' + R(x, y, w, h, f"url(#{sid})", 6))
    if part in ("night", "late"):
        s += C(x + w * 0.72, y + h * 0.3, min(w, h) * 0.13, "#f4ecd0") + C(x + w * 0.66, y + h * 0.26, min(w, h) * 0.12, a)
        s += "".join(C(x + w * f, y + h * g, 2, WHITE, 'opacity=".8"') for f, g in ((.2, .2), (.35, .5), (.5, .15), (.85, .6), (.15, .7)))
    elif part == "evening":
        s += C(x + w * 0.3, y + h * 0.85, min(w, h) * 0.2, "#f3a35d")
    else:
        s += C(x + w * 0.75, y + h * 0.32, min(w, h) * 0.15, "#ffe08a" if part != "dawn" else "#ffc27a")
    return s


def window(part, x=560, y=60, w=170, h=150):
    return (R(x - 10, y - 10, w + 20, h + 20, WHITE, 10) + sky(part, x, y, w, h) + S(f"M{x + w / 2},{y} v{h} M{x},{y + h / 2} h{w}", WHITE, 8))


def floor(y=430, col="#d8c3a5"):
    return R(0, y, W, H - y, col, 0) + S(f"M0,{y} H{W}", "#00000018", 3)


def room(part, wall=None, fl="#d8c3a5", win=True, wx=560):
    wall = wall or WALL[part]
    s = R(0, 0, W, H, wall, 0) + floor(430, fl)
    if win:
        s += window(part, wx)
    if part in ("night", "late"):
        s += R(0, 0, W, H, "#0b1430", 0, 'opacity=".28"')
    return s


def bedroom(part):
    s = room(part, wx=80)
    s += R(150, 300, 520, 150, "#b98a6a", 18) + R(130, 250, 40, 200, "#8e6248", 12) + R(650, 300, 30, 150, "#8e6248", 10)
    s += E(250, 300, 80, 34, WHITE)  # pillow
    return s


def blanket(col="#7fb2c9", y=330):
    return P(f"M160,{y} Q410,{y - 40} 660,{y} L660,440 L160,440 Z", col) + S(f"M200,{y + 30} q60,-14 120,0 M400,{y + 26} q60,-14 120,0", "#ffffff55", 5)


def office(part):
    s = room(part, wall="#e9eef0" if part not in ("night", "late") else None, fl="#b9c3cc", wx=40)
    s += R(380, 330, 400, 22, "#a7774f", 6) + R(400, 350, 18, 90, "#8e6248", 4) + R(740, 350, 18, 90, "#8e6248", 4)
    s += plant(760, 330, 0.6)
    return s


def desk_front():
    return R(380, 330, 400, 22, "#a7774f", 6) + R(380, 352, 400, 90, "#b98a62", 4) + R(380, 352, 400, 8, "#00000022", 0)


def at_desk(f="neutral", pose="down", screen="#8fd0e8", inner="", x=500):
    """Protagonist sitting behind the desk, laptop beside him (face stays visible)."""
    return me(x, 400, 0.95, f, pose, sit=True) + desk_front() + laptop(680, 330, 0.8, screen, inner)


def street(part, ground="#c9c3b8"):
    s = sky(part, 0, 0, W, 380)
    for x, w, h, c in ((0, 150, 230, "#b8a58f"), (160, 120, 290, "#c7b39c"), (300, 160, 200, "#a9937c"),
                       (480, 130, 260, "#bfa88f"), (630, 170, 220, "#b19b83")):
        s += R(x, 380 - h, w, h, c, 4)
        for wy in range(int(400 - h), 360, 46):
            for wx in range(x + 18, x + w - 30, 40):
                lit = part in ("evening", "night", "late") and (wx + wy) % 3 == 0
                s += R(wx, wy, 22, 26, "#ffd98a" if lit else "#e9eef2", 3)
    s += R(0, 380, W, 120, ground, 0) + R(0, 430, W, 70, "#8d8a86", 0) + S("M0,465 H800", "#f5f1e6", 6, 'stroke-dasharray="40 30"')
    return s


def bus(part):
    s = R(0, 0, W, H, "#dfe4e8", 0)
    for x in (30, 290, 550):
        s += R(x, 50, 220, 150, WHITE, 16) + sky(part, x + 10, 60, 200, 130)
    s += R(0, 230, W, 200, "#cdd5db", 0) + floor(430, "#8f9aa3")
    s += R(395, 0, 14, 430, "#c3ccd4", 4)
    return s


def stairs(part):
    s = room(part, wall="#efe6d8", fl="#cdb89a", win=False)
    for i in range(6):
        s += R(430 + i * 60, 430 - (i + 1) * 45, 400, 45 + (i + 1) * 45, "#d9c7a8", 0) + S(f"M{430 + i * 60},{430 - (i + 1) * 45} h400", "#b79d7a", 4)
    s += S("M420,300 L760,90", "#8e6248", 10) + "".join(S(f"M{430 + i * 60},{300 - i * 37} v80", "#8e6248", 5) for i in range(6))
    return s


def shop(part):
    s = room(part, wall="#f3efe6", fl="#c9c0b2", win=False)
    for y in (90, 180, 270):
        s += R(30, y, 360, 12, "#b08a63", 3)
        for i, c in enumerate((RED, GOLD, TEAL, SKY, PINK, "#9b7fc2", GOLD2, TEAL2)):
            s += R(40 + i * 43, y - 50, 32, 50, c, 5)
    s += R(470, 300, 330, 130, "#a7774f", 10) + R(600, 250, 90, 50, INK, 6) + R(610, 258, 70, 30, "#7fd0b8", 3)
    return s


def kitchen(part):
    s = room(part, wall="#f2e4cf" if part not in ("night", "late") else "#cbc6d4", wx=40)
    s += S("M400,0 v80", INK, 3) + P("M360,80 h80 l-14,-26 h-52 z", GOLD) + C(400, 92, 12, "#fff3c4")
    s += R(150, 330, 520, 24, "#a7774f", 8) + R(180, 352, 18, 88, "#8e6248", 4) + R(620, 352, 18, 88, "#8e6248", 4)
    return s


def table_front():
    return R(150, 330, 520, 24, "#a7774f", 8) + R(150, 354, 520, 80, "#c08f63", 4) + R(150, 354, 520, 8, "#00000022", 0)


def living(part):
    s = room(part, wx=40)
    s += R(250, 280, 400, 110, "#7fa9a0", 30) + R(225, 340, 450, 90, "#5f8f85", 26) + R(270, 350, 360, 30, "#9cc4ba", 14)
    s += R(700, 220, 10, 210, INK, 3) + P("M670,220 h70 l-16,-50 h-38 z", GOLD)
    return s


def plain(c1="#e7f1ef", c2="#f8f4ea"):
    return (f'<defs><linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{c2}"/></linearGradient></defs>' + R(0, 0, W, H, "url(#pl)", 0))


def dark_room():
    return room("late", wall="#56607a", fl="#3d455a", wx=560)


# ------------------------------------------------------------------ people
def face(cx, cy, r, f, skin):
    """Exaggerated caricature faces."""
    o = []
    ex, ey, er = r * 0.36, cy - r * 0.08, r * 0.2

    def whites(k=1.0, py=0.0, px=0.0, pr=0.45):
        s = ""
        for sx in (-1, 1):
            s += E(cx + sx * ex, ey, er * k, er * 1.15 * k, WHITE, f'stroke="{INK}" stroke-width="{r * 0.035:.1f}"')
            s += C(cx + sx * ex + px * er, ey + py * er, er * pr * k, INK)
        return s

    def brows(inner, outer, lift=0.0):
        s = ""
        for sx in (-1, 1):
            s += S(f"M{cx + sx * (ex - er * 1.1):.1f},{ey - er * (1.5 + outer) - lift:.1f} L{cx + sx * (ex + er * 0.6) * 0.55:.1f},{ey - er * (1.5 + inner) - lift:.1f}", INK, r * 0.07)
        return s

    def mouth(kind):
        my = cy + r * 0.45
        if kind == "smile":
            return P(f"M{cx - r * 0.36:.1f},{my - r * 0.05:.1f} Q{cx:.1f},{my + r * 0.45:.1f} {cx + r * 0.36:.1f},{my - r * 0.05:.1f} Z", "#7a2e2a") + P(f"M{cx - r * 0.22:.1f},{my + r * 0.13:.1f} Q{cx:.1f},{my + r * 0.3:.1f} {cx + r * 0.22:.1f},{my + r * 0.13:.1f} Z", "#e7837a")
        if kind == "soft":
            return S(f"M{cx - r * 0.22:.1f},{my:.1f} Q{cx:.1f},{my + r * 0.18:.1f} {cx + r * 0.22:.1f},{my:.1f}", INK, r * 0.06)
        if kind == "frown":
            return S(f"M{cx - r * 0.24:.1f},{my + r * 0.12:.1f} Q{cx:.1f},{my - r * 0.12:.1f} {cx + r * 0.24:.1f},{my + r * 0.12:.1f}", INK, r * 0.06)
        if kind == "o":
            return E(cx, my + r * 0.05, r * 0.13, r * 0.18, "#7a2e2a")
        if kind == "flat":
            return S(f"M{cx - r * 0.2:.1f},{my + r * 0.04:.1f} H{cx + r * 0.2:.1f}", INK, r * 0.06)
        if kind == "wavy":
            return S(f"M{cx - r * 0.26:.1f},{my + r * 0.05:.1f} q{r * 0.065:.1f},{-r * 0.1:.1f} {r * 0.13:.1f},0 t{r * 0.13:.1f},0 t{r * 0.13:.1f},0 t{r * 0.13:.1f},0", INK, r * 0.05)
        if kind == "teeth":
            return R(cx - r * 0.28, my - r * 0.06, r * 0.56, r * 0.22, WHITE, r * 0.06, f'stroke="{INK}" stroke-width="{r * 0.04:.1f}"') + S(f"M{cx - r * 0.28:.1f},{my + r * 0.05:.1f} H{cx + r * 0.28:.1f} M{cx - r * 0.1:.1f},{my - r * 0.06:.1f} v{r * 0.22:.1f} M{cx + r * 0.1:.1f},{my - r * 0.06:.1f} v{r * 0.22:.1f}", INK, r * 0.03)
        return ""

    closed_happy = "".join(S(f"M{cx + sx * ex - er:.1f},{ey + er * 0.2:.1f} Q{cx + sx * ex:.1f},{ey - er * 1.1:.1f} {cx + sx * ex + er:.1f},{ey + er * 0.2:.1f}", INK, r * 0.07) for sx in (-1, 1))
    closed_calm = "".join(S(f"M{cx + sx * ex - er:.1f},{ey - er * 0.2:.1f} Q{cx + sx * ex:.1f},{ey + er * 0.8:.1f} {cx + sx * ex + er:.1f},{ey - er * 0.2:.1f}", INK, r * 0.07) for sx in (-1, 1))
    lids = "".join(P(f"M{cx + sx * ex - er * 1.05:.1f},{ey:.1f} A{er * 1.05:.1f},{er * 1.2:.1f} 0 0 1 {cx + sx * ex + er * 1.05:.1f},{ey:.1f} Z", skin, f'stroke="{INK}" stroke-width="{r * 0.04:.1f}"') for sx in (-1, 1))
    bags = "".join(S(f"M{cx + sx * ex - er * 0.8:.1f},{ey + er * 1.45:.1f} q{er * 0.8:.1f},{er * 0.5:.1f} {er * 1.6:.1f},0", "#a77b8a", r * 0.04) for sx in (-1, 1))
    cheeks = "".join(E(cx + sx * r * 0.55, cy + r * 0.3, r * 0.15, r * 0.09, BLUSH, 'opacity=".75"') for sx in (-1, 1))
    nose = S(f"M{cx - r * 0.04:.1f},{cy + r * 0.1:.1f} q{r * 0.1:.1f},{r * 0.12:.1f} {-r * 0.02:.1f},{r * 0.2:.1f}", "#00000055", r * 0.045)

    if f == "happy":
        o += [closed_happy, cheeks, mouth("smile")]
    elif f == "calm":
        o += [closed_calm, mouth("soft"), cheeks]
    elif f == "tired":
        o += [whites(py=0.3), lids, bags, mouth("flat"), S(f"M{cx + r * 0.62:.1f},{cy - r * 0.5:.1f} l{r * 0.12:.1f},0 l{-r * 0.12:.1f},{r * 0.14:.1f} l{r * 0.12:.1f},0", GREY, r * 0.04)]
    elif f == "angry":
        o += [whites(pr=0.5), brows(0.25, -0.55, 0), mouth("teeth"), cheeks.replace(BLUSH, "#e8584a")]
    elif f == "sad":
        o += [whites(py=0.35), brows(-0.6, 0.15), mouth("frown"), P(f"M{cx + ex + er * 0.3:.1f},{ey + er * 1.3:.1f} q{r * 0.08:.1f},{r * 0.16:.1f} 0,{r * 0.22:.1f} q{-r * 0.08:.1f},{-r * 0.06:.1f} 0,{-r * 0.22:.1f} Z", "#7cc0e8")]
    elif f == "anxious":
        o += [whites(k=1.1, pr=0.32), brows(-0.5, 0.1, r * 0.05), mouth("wavy"),
              P(f"M{cx + r * 0.85:.1f},{cy - r * 0.45:.1f} q{r * 0.1:.1f},{r * 0.16:.1f} 0,{r * 0.24:.1f} q{-r * 0.1:.1f},{-r * 0.08:.1f} 0,{-r * 0.24:.1f} Z", "#7cc0e8")]
    elif f == "shocked":
        o += [whites(k=1.3, pr=0.25), brows(-0.6, -0.6, r * 0.12), mouth("o")]
    elif f == "annoyed":
        o += [whites(px=0.5), "".join(R(cx + sx * ex - er * 1.1, ey - er * 1.3, er * 2.2, er * 1.15, skin, 0) + S(f"M{cx + sx * ex - er:.1f},{ey - er * 0.15:.1f} h{er * 2:.1f}", INK, r * 0.05) for sx in (-1, 1)), mouth("flat")]
    elif f == "blush":
        o += [closed_happy, cheeks, cheeks, mouth("soft")]
    elif f == "worried":
        o += [whites(py=0.1, pr=0.4), brows(-0.55, 0.05), mouth("frown")]
    else:  # neutral
        o += [whites(), mouth("soft")]
    o.append(nose)
    return "".join(o)


def person(x, base, sc=1.0, f="neutral", pose="down", kind="me", shirt=TEAL, skin="a", sit=False, flip=1, prop=""):
    """Big-head caricature. pose: down, up, head, phone, hold, wave, cross, point, hug, shrug."""
    r = 60 * sc
    sk = SKIN.get(skin, skin)
    if kind == "kid":
        r = 46 * sc
    body_h = r * (1.1 if kind == "kid" else 1.35)
    leg_h = r * (0.75 if kind == "kid" else 1.05)
    if sit:
        hy = base - body_h - r * 0.85
    else:
        hy = base - leg_h - body_h - r * 0.85
    tt = hy + r * 0.85
    tb = tt + body_h
    tw = r * 1.15
    o = []
    pants = "#2a3550" if kind != "kid" else "#3e5a8a"
    if kind == "old":
        pants = "#6b5a4a"
    # legs
    if sit:
        o.append(R(x - tw * 0.45, tb - r * 0.25, tw * 0.38, r * 0.75, pants, r * 0.18) + R(x + tw * 0.07, tb - r * 0.25, tw * 0.38, r * 0.75, pants, r * 0.18))
    elif leg_h > 0:
        o.append(R(x - tw * 0.36, tb - 4, tw * 0.28, leg_h + 4, pants, r * 0.1) + R(x + tw * 0.08, tb - 4, tw * 0.28, leg_h + 4, pants, r * 0.1))
        o.append(E(x - tw * 0.22, tb + leg_h, r * 0.22, r * 0.1, INK) + E(x + tw * 0.22, tb + leg_h, r * 0.22, r * 0.1, INK))
    # torso
    dress = kind in ("woman", "old_w", "mom")
    if dress:
        o.append(P(f"M{x - tw * 0.42:.1f},{tt:.1f} h{tw * 0.84:.1f} l{tw * 0.2:.1f},{body_h + r * 0.35:.1f} h{-tw * 1.24:.1f} Z", shirt))
    else:
        o.append(R(x - tw / 2, tt, tw, body_h, shirt, r * 0.35))
    if kind == "boss":
        o.append(P(f"M{x:.1f},{tt + 4:.1f} l{-r * 0.09:.1f},{r * 0.16:.1f} l{r * 0.09:.1f},{r * 0.7:.1f} l{r * 0.09:.1f},{-r * 0.7:.1f} Z", RED))
    # arms
    aw = r * 0.2
    sh_y = tt + r * 0.22
    L, Rr = (x - tw * 0.46, sh_y), (x + tw * 0.46, sh_y)
    def arm(a, b, c=None):
        pts = [a, b] + ([c] if c else [])
        d = "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        end = pts[-1]
        return S(d, shirt, aw) + C(end[0], end[1], aw * 0.62, sk)
    m = flip
    if pose == "up":
        o += [arm(L, (L[0] - r * 0.5, sh_y - r * 0.5), (L[0] - r * 0.6, sh_y - r * 1.1)), arm(Rr, (Rr[0] + r * 0.5, sh_y - r * 0.5), (Rr[0] + r * 0.6, sh_y - r * 1.1))]
    elif pose == "head":
        o += [arm(L, (L[0] - r * 0.55, sh_y - r * 0.2), (x - r * 0.85, hy - r * 0.35)), arm(Rr, (Rr[0] + r * 0.55, sh_y - r * 0.2), (x + r * 0.85, hy - r * 0.35))]
    elif pose == "phone":
        px = x + m * r * 0.95
        o += [arm(L, (L[0] - r * 0.1, sh_y + r * 0.55), (L[0] + r * 0.05, sh_y + r * 0.95)) if m > 0 else arm(Rr, (Rr[0] + r * 0.1, sh_y + r * 0.55), (Rr[0] - r * 0.05, sh_y + r * 0.95)),
              arm(Rr if m > 0 else L, (x + m * tw * 0.75, sh_y + r * 0.4), (px, hy + r * 0.25)), phone(px, hy + r * 0.05, sc * 0.75, n=0)]
    elif pose == "hold":
        o += [arm(L, (L[0] - r * 0.15, sh_y + r * 0.45), (x - r * 0.3, sh_y + r * 0.6)), arm(Rr, (Rr[0] + r * 0.15, sh_y + r * 0.45), (x + r * 0.3, sh_y + r * 0.6))]
    elif pose == "wave":
        o += [arm(L, (L[0] - r * 0.1, sh_y + r * 0.55), (L[0] + r * 0.02, sh_y + r * 0.95)), arm(Rr, (Rr[0] + r * 0.55, sh_y - r * 0.15), (Rr[0] + r * 0.7, sh_y - r * 0.85))]
    elif pose == "cross":
        o += [S(f"M{L[0]:.1f},{L[1]:.1f} L{x + r * 0.35:.1f},{sh_y + r * 0.5:.1f}", shirt, aw * 1.05), S(f"M{Rr[0]:.1f},{Rr[1]:.1f} L{x - r * 0.35:.1f},{sh_y + r * 0.62:.1f}", shirt, aw * 1.05)]
    elif pose == "point":
        o += [arm(L, (L[0] - r * 0.1, sh_y + r * 0.55), (L[0] + r * 0.02, sh_y + r * 0.95)), arm(Rr, (Rr[0] + r * 0.6, sh_y + r * 0.05), (Rr[0] + r * 1.15, sh_y - r * 0.1))]
    elif pose == "reach":  # one arm out to the side (helping / giving)
        o += [arm(L, (L[0] - r * 0.1, sh_y + r * 0.55), (L[0] + r * 0.02, sh_y + r * 0.95)), arm(Rr, (Rr[0] + r * 0.6, sh_y + r * 0.35), (Rr[0] + r * 1.1, sh_y + r * 0.35))]
    elif pose == "shrug":
        o += [arm(L, (L[0] - r * 0.5, sh_y + r * 0.3), (L[0] - r * 0.75, sh_y - r * 0.2)), arm(Rr, (Rr[0] + r * 0.5, sh_y + r * 0.3), (Rr[0] + r * 0.75, sh_y - r * 0.2))]
    elif pose == "none":
        pass
    else:
        o += [arm(L, (L[0] - r * 0.12, sh_y + r * 0.55), (L[0] - r * 0.02, sh_y + r * 0.98)), arm(Rr, (Rr[0] + r * 0.12, sh_y + r * 0.55), (Rr[0] + r * 0.02, sh_y + r * 0.98))]
    # head + hair
    hair = {"me": "#2b2420", "man2": "#4a3426", "woman": "#3b2a22", "boss": "#6b6f78", "old": "#d9dbe0", "kid": "#5a3a24",
            "hijab": "#7d6a9c", "mom": "#a35d6a", "girl": "#5a3a24"}.get(kind, "#2b2420")
    hx, hyy = x, hy
    if kind in ("hijab", "mom"):
        o.append(E(hx, hyy + r * 0.15, r * 1.12, r * 1.18, hair) + P(f"M{hx - r * 1.05:.1f},{hyy + r * 0.4:.1f} Q{hx:.1f},{hyy + r * 1.7:.1f} {hx + r * 1.05:.1f},{hyy + r * 0.4:.1f} L{hx + r * 0.9:.1f},{tt + r * 0.4:.1f} L{hx - r * 0.9:.1f},{tt + r * 0.4:.1f} Z", hair))
    if kind == "woman" or kind == "girl":
        o.append(P(f"M{hx - r * 1.05:.1f},{hyy:.1f} A{r * 1.05:.1f},{r * 1.05:.1f} 0 0 1 {hx + r * 1.05:.1f},{hyy:.1f} L{hx + r * 1.0:.1f},{hyy + r * 1.25:.1f} Q{hx:.1f},{hyy + r * 1.45:.1f} {hx - r * 1.0:.1f},{hyy + r * 1.25:.1f} Z", hair))
    o.append(C(hx, hyy, r, sk))
    o.append(E(hx - r * 0.98, hyy + r * 0.08, r * 0.14, r * 0.2, sk) + E(hx + r * 0.98, hyy + r * 0.08, r * 0.14, r * 0.2, sk))
    if kind == "me":
        o.append("".join(C(hx + dx * r, hyy + dy * r, r * 0.3, hair) for dx, dy in ((-0.7, -0.55), (-0.38, -0.82), (0, -0.92), (0.38, -0.82), (0.7, -0.55), (-0.88, -0.2), (0.88, -0.2))))
    elif kind in ("man2", "kid"):
        o.append(P(f"M{hx - r * 0.98:.1f},{hyy - r * 0.05:.1f} A{r:.1f},{r:.1f} 0 0 1 {hx + r * 0.98:.1f},{hyy - r * 0.05:.1f} Q{hx + r * 0.3:.1f},{hyy - r * 0.6:.1f} {hx - r * 0.98:.1f},{hyy - r * 0.05:.1f} Z", hair))
    elif kind == "boss":
        o.append(P(f"M{hx - r * 1.0:.1f},{hyy + r * 0.1:.1f} q{r * 0.05:.1f},{-r * 0.5:.1f} {r * 0.3:.1f},{-r * 0.6:.1f} M{hx + r * 1.0:.1f},{hyy + r * 0.1:.1f} q{-r * 0.05:.1f},{-r * 0.5:.1f} {-r * 0.3:.1f},{-r * 0.6:.1f}", "none", f'stroke="{hair}" stroke-width="{r * 0.22:.1f}" stroke-linecap="round"'))
        o.append(S(f"M{hx - r * 0.55:.1f},{hyy - r * 0.35:.1f} h{r * 0.3:.1f} M{hx + r * 0.25:.1f},{hyy - r * 0.35:.1f} h{r * 0.3:.1f}", INK, r * 0.07))
    elif kind == "old":
        o.append(C(hx, hyy - r * 1.0, r * 0.35, hair) + P(f"M{hx - r * 1.0:.1f},{hyy - r * 0.05:.1f} A{r:.1f},{r:.1f} 0 0 1 {hx + r * 1.0:.1f},{hyy - r * 0.05:.1f} Q{hx:.1f},{hyy - r * 0.55:.1f} {hx - r * 1.0:.1f},{hyy - r * 0.05:.1f} Z", hair))
    elif kind in ("woman", "girl"):
        o.append(P(f"M{hx - r * 1.0:.1f},{hyy - r * 0.05:.1f} A{r:.1f},{r:.1f} 0 0 1 {hx + r * 1.0:.1f},{hyy - r * 0.05:.1f} Q{hx - r * 0.2:.1f},{hyy - r * 0.75:.1f} {hx - r * 1.0:.1f},{hyy - r * 0.05:.1f} Z", hair))
    if kind in ("hijab", "mom"):
        o.append(P(f"M{hx - r * 1.0:.1f},{hyy - r * 0.1:.1f} A{r * 1.0:.1f},{r * 1.0:.1f} 0 0 1 {hx + r * 1.0:.1f},{hyy - r * 0.1:.1f} Q{hx:.1f},{hyy - r * 0.62:.1f} {hx - r * 1.0:.1f},{hyy - r * 0.1:.1f} Z", hair))
    o.append(face(hx, hyy, r, f, sk))
    if kind == "old":
        o.append("".join(C(hx + sx * r * 0.36, hyy - r * 0.08, r * 0.24, "none", f'stroke="{INK}" stroke-width="{r * 0.05:.1f}"') for sx in (-1, 1)))
    o.append(prop)
    return "".join(o)


def me(x=400, base=440, sc=1.0, f="neutral", pose="down", sit=False, **k):
    return person(x, base, sc, f, pose, "me", TEAL, "a", sit, **k)


def in_bed(f, pose="down", x=330, col="#7fb2c9"):
    """Protagonist sitting up in bed under the blanket."""
    return person(x, 405, 1.05, f, pose, "me", "#8fb7a9", "a", sit=True) + blanket(col, 345)


# ------------------------------------------------------------------ props
def phone(x, y, sc=1.0, n=0, screen="#8fd0e8", mark=""):
    w, h = 46 * sc, 80 * sc
    s = R(x - w / 2, y - h / 2, w, h, INK, 9 * sc) + R(x - w / 2 + 4 * sc, y - h / 2 + 8 * sc, w - 8 * sc, h - 18 * sc, screen, 4 * sc)
    if n:
        s += C(x + w / 2, y - h / 2, 14 * sc, RED) + T(x + w / 2, y - h / 2 + 6 * sc, str(n), 16 * sc, WHITE)
    if mark:
        s += mark
    return s


def big_phone(x, y, sc=1.0, content=""):
    return phone(x, y, sc) + content


def clock(x, y, s=1.0, ring=True):
    o = (C(x, y, 42 * s, RED) + C(x, y, 32 * s, WHITE) + S(f"M{x},{y} v{-20 * s:.1f} M{x},{y} l{14 * s:.1f},{8 * s:.1f}", INK, 4 * s)
         + C(x - 30 * s, y - 38 * s, 14 * s, GOLD) + C(x + 30 * s, y - 38 * s, 14 * s, GOLD) + S(f"M{x - 26 * s:.1f},{y + 36 * s:.1f} l-8,12 M{x + 26 * s:.1f},{y + 36 * s:.1f} l8,12", INK, 5 * s))
    if ring:
        o += S(f"M{x - 60 * s:.1f},{y - 30 * s:.1f} l-14,-8 M{x - 62 * s:.1f},{y:.1f} h-16 M{x + 60 * s:.1f},{y - 30 * s:.1f} l14,-8 M{x + 62 * s:.1f},{y:.1f} h16", INK, 4)
    return o


def bubble(x, y, w, h, txt="", fill=WHITE, tail=-1, size=34, col=INK):
    tx = x + (w * 0.25 if tail < 0 else w * 0.75)
    return (R(x, y, w, h, fill, h * 0.45, f'stroke="{INK}" stroke-width="3"') + P(f"M{tx - 14},{y + h - 2} L{tx + tail * 26},{y + h + 30} L{tx + 16},{y + h - 2} Z", fill, f'stroke="{INK}" stroke-width="3"')
            + R(tx - 13, y + h - 6, 28, 8, fill, 0) + (T(x + w / 2, y + h / 2 + size * 0.36, txt, size, col) if txt else ""))


def thought(x, y, w, h, inner=""):
    return (E(x + w / 2, y + h / 2, w / 2, h / 2, WHITE, f'stroke="{INK}" stroke-width="3"') + C(x + w * 0.2, y + h + 14, 12, WHITE, f'stroke="{INK}" stroke-width="3"')
            + C(x + w * 0.1, y + h + 38, 7, WHITE, f'stroke="{INK}" stroke-width="3"') + inner)


def heart(x, y, s=1.0, c=RED):
    return P(f"M{x},{y + 12 * s:.1f} C{x - 26 * s:.1f},{y - 8 * s:.1f} {x - 14 * s:.1f},{y - 30 * s:.1f} {x},{y - 14 * s:.1f} C{x + 14 * s:.1f},{y - 30 * s:.1f} {x + 26 * s:.1f},{y - 8 * s:.1f} {x},{y + 12 * s:.1f} Z", c)


def zzz(x, y, c=GREY):
    return T(x, y, "Z", 34, c) + T(x + 28, y - 30, "z", 26, c) + T(x + 50, y - 54, "z", 20, c)


def steam(x, y, c="#e0675a"):
    return S(f"M{x},{y} q-12,-14 0,-28 q12,-14 0,-28 M{x + 26},{y + 6} q-12,-14 0,-28 q12,-14 0,-28", c, 6)


def sparkles(x, y, c=GOLD, n=3):
    o = ""
    for i in range(n):
        cx, cy, s = x + i * 46, y + (i % 2) * 30, 14 - (i % 2) * 4
        o += P(f"M{cx},{cy - s} L{cx + s * 0.3},{cy - s * 0.3} L{cx + s},{cy} L{cx + s * 0.3},{cy + s * 0.3} L{cx},{cy + s} L{cx - s * 0.3},{cy + s * 0.3} L{cx - s},{cy} L{cx - s * 0.3},{cy - s * 0.3} Z", c)
    return o


def rain_lines(x0, x1, y0, y1, c="#6fa8cf"):
    return "".join(S(f"M{x},{y} l-8,22", c, 4) for x in range(x0, x1, 34) for y in range(y0 + (x % 3) * 12, y1, 60))


def cloud(x, y, s=1.0, c="#c3ccd6"):
    return f'<g transform="translate({x},{y}) scale({s})" fill="{c}"><circle cx="-50" cy="8" r="38"/><circle cx="0" cy="-12" r="52"/><circle cx="54" cy="6" r="40"/><rect x="-88" y="6" width="182" height="42" rx="21"/></g>'


def laptop(x, y, sc=1.0, screen="#8fd0e8", inner=""):
    w, h = 170 * sc, 108 * sc
    return R(x - w / 2, y - h, w, h, INK, 10 * sc) + R(x - w / 2 + 8 * sc, y - h + 8 * sc, w - 16 * sc, h - 16 * sc, screen, 4 * sc) + R(x - w / 2 - 18 * sc, y - 2, w + 36 * sc, 12 * sc, "#3a4763", 5) + inner


def papers(x, y, n=4):
    return "".join(R(x + i * 3, y - i * 9, 90, 70, WHITE if i % 2 else "#eef2f4", 4, f'stroke="#c3ccd6" stroke-width="2"') for i in range(n))


def cup(x, y, c=WHITE, hot=True):
    s = R(x - 20, y - 36, 40, 40, c, 9) + S(f"M{x + 20},{y - 26} q16,6 0,22", c, 6)
    if hot:
        s += S(f"M{x - 7},{y - 46} q-8,-12 0,-24 M{x + 7},{y - 46} q-8,-12 0,-24", "#b8c4cc", 4)
    return s


def plant(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M0,0 C-50,-40 -40,-110 0,-130 C40,-110 50,-40 0,0Z" fill="{TEAL}"/>'
            f'<path d="M0,0 C-70,-10 -90,-60 -70,-90 C-30,-80 -5,-40 0,0Z" fill="{TEAL2}"/><path d="M0,0 C70,-10 90,-60 70,-90 C30,-80 5,-40 0,0Z" fill="{TEAL2}"/>'
            f'<path d="M-34,0 h68 l-10,60 h-48 z" fill="{GOLD2}"/></g>')


def cat(x, y, s=1.0, c="#e89a4f"):
    return (f'<g transform="translate({x},{y}) scale({s})">' + E(0, 0, 46, 30, c) + C(-44, -26, 26, c) + P("M-64,-44 l6,-26 l14,18 Z M-34,-46 l8,-24 l10,22 Z", c)
            + C(-52, -28, 4, INK) + C(-36, -28, 4, INK) + S("M-44,-18 q-4,4 -8,0 M-44,-18 q4,4 8,0", INK, 2) + S("M44,-6 q30,-10 22,-40", c, 9) + "</g>")


def car(x, y, c=RED, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})">' + R(0, 0, 230, 66, c, 24) + P("M40,4 l30,-50 h90 l30,50 z", c) + P("M76,-38 h32 v38 h-52 z M118,-38 h30 l22,38 h-52 z", "#dff2fb")
            + C(55, 68, 25, INK) + C(175, 68, 25, INK) + C(55, 68, 9, GREY) + C(175, 68, 9, GREY) + "</g>")


def splash(x, y):
    return "".join(E(x + dx, y + dy, rx, ry, "#7cc0e8", 'opacity=".85"') for dx, dy, rx, ry in ((0, 0, 70, 22), (-50, -40, 14, 20), (10, -60, 12, 18), (60, -36, 14, 20), (-90, -10, 10, 14)))


def wallet(x, y):
    return R(x - 40, y - 28, 80, 56, "#8a5a3c", 10) + R(x - 40, y - 28, 80, 22, "#6f4630", 10) + R(x - 18, y - 46, 50, 24, "#7fc39c", 3) + C(x + 26, y - 6, 6, GOLD)


def cake(x, y):
    return (R(x - 60, y - 50, 120, 50, PINK, 10) + R(x - 60, y - 58, 120, 18, CREAM, 9) + R(x - 4, y - 92, 8, 34, GOLD, 3)
            + P(f"M{x},{y - 110} q10,12 0,20 q-10,-8 0,-20 Z", "#ff9d3b") + R(x - 76, y - 4, 152, 10, WHITE, 5))


def flowers(x, y):
    o = S(f"M{x},{y} L{x - 20},{y - 70} M{x},{y} L{x},{y - 84} M{x},{y} L{x + 22},{y - 66}", TEAL, 5)
    for fx, fy, c in ((x - 20, y - 76, RED), (x, y - 92, PINK), (x + 22, y - 72, GOLD)):
        o += "".join(C(fx + 9 * math.cos(a), fy + 9 * math.sin(a), 8, c) for a in [i * 1.2566 for i in range(5)]) + C(fx, fy, 6, GOLD2)
    return o + P(f"M{x - 26},{y - 30} L{x + 26},{y - 30} L{x + 10},{y + 18} L{x - 10},{y + 18} Z", "#d9c7f0")


def ball(x, y, r=26):
    return C(x, y, r, WHITE, f'stroke="{INK}" stroke-width="3"') + P(f"M{x},{y - r * 0.4} l{r * 0.38},{r * 0.28} l{-r * 0.15},{r * 0.45} h{-r * 0.46} l{-r * 0.15},{-r * 0.45} Z", INK)


def tv(x, y, inner=""):
    return R(x - 120, y - 150, 240, 150, INK, 10) + R(x - 108, y - 138, 216, 126, "#6a8fd8", 4) + inner + R(x - 10, y, 20, 30, INK, 2) + R(x - 50, y + 26, 100, 10, INK, 4)


def candle(x, y):
    return C(x, y - 70, 60, "#ffd98a", 'opacity=".35"') + R(x - 14, y - 60, 28, 60, CREAM, 5) + P(f"M{x},{y - 92} q12,16 0,28 q-12,-12 0,-28 Z", "#ff9d3b")


def calendar(x, y, mark=""):
    return R(x - 50, y - 60, 100, 100, WHITE, 8, f'stroke="{INK}" stroke-width="3"') + R(x - 50, y - 60, 100, 26, RED, 8) + R(x - 50, y - 44, 100, 10, RED, 0) + mark


def bulb(x, y, c=GOLD):
    return C(x, y, 30, c) + R(x - 14, y + 24, 28, 18, GREY, 4) + S(f"M{x - 48},{y - 30} l-14,-12 M{x},{y - 46} v-18 M{x + 48},{y - 30} l14,-12", c, 5)


def star(x, y, r=26, c=GOLD):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}")
    return P("M" + " L".join(pts) + " Z", c)


def confetti(x0, y0, w, h):
    cols = (RED, GOLD, TEAL, SKY, PINK)
    return "".join(R(x0 + (i * 53) % w, y0 + (i * 37) % h, 12, 6, cols[i % 5], 2, f'transform="rotate({(i * 47) % 180} {x0 + (i * 53) % w} {y0 + (i * 37) % h})"') for i in range(26))


def scribble(x, y, c=INK, s=1.0):
    return S(f"M{x - 40 * s:.1f},{y:.1f} c20,-40 50,30 70,-10 s-60,-40 -50,10 s50,40 60,-10 s-40,-30 -50,0", c, 5)


def checklist(x, y, n=5, done=0):
    o = R(x, y, 150, 30 + n * 34, WHITE, 8, f'stroke="{INK}" stroke-width="3"')
    for i in range(n):
        yy = y + 24 + i * 34
        o += R(x + 14, yy - 10, 18, 18, WHITE, 3, f'stroke="{INK}" stroke-width="2.5"') + R(x + 44, yy - 4, 86 - (i % 3) * 14, 8, "#c3ccd6", 4)
        if i < done:
            o += S(f"M{x + 16},{yy} l5,6 l10,-12", TEAL, 4)
    return o


def notes(x, y, c=INK):
    return S(f"M{x},{y} v-40 l24,-8 v40", c, 5) + C(x - 6, y, 9, c) + C(x + 18, y - 8, 9, c) + S(f"M{x + 60},{y + 20} v-34", c, 5) + C(x + 54, y + 20, 9, c)


def food(x, y):
    return E(x, y, 70, 16, WHITE) + E(x, y - 8, 54, 22, "#d9823c") + C(x - 20, y - 18, 8, "#7fae4f") + C(x + 14, y - 22, 7, "#d1453b")


def money(x, y):
    return R(x - 50, y - 26, 100, 52, "#7fc39c", 6) + C(x, y, 15, "#5ea67d") + T(x, y + 9, "$", 26, WHITE)


def grade(x, y):
    return R(x - 50, y - 64, 100, 128, WHITE, 6, f'stroke="{INK}" stroke-width="3"') + "".join(R(x - 36, y - 30 + i * 18, 60, 6, "#c3ccd6", 3) for i in range(4)) + C(x + 26, y - 42, 22, "none", f'stroke="{RED}" stroke-width="4"') + T(x + 26, y - 33, "4", 24, RED)


def drawing(x, y):
    return R(x - 60, y - 46, 120, 92, WHITE, 4, f'stroke="{INK}" stroke-width="3"') + C(x + 30, y - 22, 12, GOLD) + P(f"M{x - 48},{y + 36} l30,-40 l20,22 l16,-14 l24,32 Z", TEAL2) + S(f"M{x - 40},{y - 10} q10,-16 20,0", "#7cc0e8", 4)


def bag(x, y, c=GOLD2):
    return R(x - 30, y - 50, 60, 54, c, 8) + S(f"M{x - 14},{y - 50} q14,-26 28,0", INK, 4)


def guitar(x, y):
    return E(x, y, 40, 46, "#c9853f") + E(x, y - 46, 30, 32, "#c9853f") + C(x, y - 10, 12, INK) + R(x - 6, y - 150, 12, 100, "#6f4630", 3) + R(x - 12, y - 166, 24, 22, "#6f4630", 4)


def book(x, y):
    return P(f"M{x - 60},{y} L{x},{y + 10} L{x + 60},{y} L{x + 60},{y - 60} L{x},{y - 50} L{x - 60},{y - 60} Z", WHITE, f'stroke="{INK}" stroke-width="3"') + S(f"M{x},{y - 50} v60", INK, 3)


def mini_screen_people(x, y):
    return C(x - 10, y, 9, "#f0c39e") + C(x + 10, y + 2, 9, "#d9a074") + R(x - 20, y + 8, 40, 14, TEAL, 6)


def battery_icon(x, y, level=0.15, c=RED):
    return R(x, y, 90, 44, WHITE, 8, f'stroke="{INK}" stroke-width="5"') + R(x + 90, y + 13, 8, 18, INK, 3) + R(x + 7, y + 7, max(6, 76 * level), 30, c, 4)


# ------------------------------------------------------------------ scenes (one per data.js "art" id)
def sv(*parts):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">' + "".join(parts) + "</svg>"


LATE_ROOM = lambda: bedroom("late")
ART = {
 # 7:00 dawn
 "t01-1": lambda: sv(bedroom("dawn"), in_bed("tired", "head"), clock(560, 300), zzz(420, 130)),
 "t01-2": lambda: sv(bedroom("dawn"), in_bed("shocked", "phone"), bubble(470, 70, 120, 64, "30", RED, -1, 34, WHITE), sparkles(620, 160, RED, 3)),
 "t01-3": lambda: sv(bedroom("dawn"), in_bed("tired"), cloud(470, 120, 0.9, "#9aa6b5"), P("M430,240 l-14,30 l16,0 l-10,30", "none", f'stroke="{GOLD2}" stroke-width="6"')),
 "t01-4": lambda: sv(bedroom("dawn"), in_bed("shocked", "head"), clock(560, 300, 1.0, False), T(560, 250, "!!", 56, RED)),
 "t01-5": lambda: sv(bedroom("dawn"), in_bed("annoyed", "head"), bubble(520, 60, 230, 80, "#@!", WHITE, -1, 40, RED), S("M700,170 l20,-10 M700,190 l26,0 M700,210 l20,10", RED, 6)),
 "t01-6": lambda: sv(bedroom("dawn"), in_bed("anxious"), calendar(600, 330, star(600, 300, 22, RED))),
 "t01-7": lambda: sv(bedroom("dawn"), rain_lines(90, 250, 60, 220), cloud(170, 70, 0.7, "#9aa6b5"), in_bed("tired", "hold", col="#d98f6a"), cup(330, 336)),
 "t01-8": lambda: sv(bedroom("dawn"), in_bed("blush", "phone"), heart(500, 140, 1.4), heart(560, 100, 0.9, PINK)),
 # 8:30 morning
 "t02-1": lambda: sv(street("morning"), car(20, 360, SKY, 0.8), car(560, 360, GOLD, 0.8), me(400, 470, 0.95, "angry", "point"), steam(380, 150), T(560, 120, "...", 60, INK)),
 "t02-2": lambda: sv(bus("morning"), me(260, 460, 0.95, "annoyed", "cross"), person(560, 460, 0.95, "happy", "phone", "man2", GOLD, "b"), bubble(600, 40, 170, 70, "!!!", WHITE, -1, 40, RED)),
 "t02-3": lambda: sv(street("morning"), me(330, 470, 0.95, "anxious", "phone"), bubble(470, 70, 230, 80, "", WHITE, -1) + heart(585, 112, 1.2)),
 "t02-4": lambda: sv(street("morning"), car(470, 380, RED, 0.9), splash(380, 420), me(300, 470, 0.95, "shocked", "up")),
 "t02-5": lambda: sv(bus("morning"), me(280, 470, 1.0, "worried", "down", sit=True), person(520, 460, 0.95, "tired", "hold", "old", "#9b7fc2", "a"), R(180, 400, 200, 70, "#5f8f85", 14)),
 "t02-6": lambda: sv(street("morning"), me(380, 470, 1.0, "shocked", "shrug"), thought(520, 60, 170, 120, phone(605, 120, 0.8) + S("M570,90 l70,60 M640,90 l-70,60", RED, 8))),
 "t02-7": lambda: sv(bus("morning"), me(330, 470, 1.0, "annoyed", "head"), notes(520, 140, RED), notes(620, 230, RED)),
 "t02-8": lambda: sv(stairs("morning"), me(300, 440, 0.95, "happy", "wave"), person(560, 440 - 90, 0.85, "happy", "wave", "man2", GOLD2, "c"), bubble(470, 60, 140, 70, "?", WHITE, 1)),
 # 10:00 office
 "t03-1": lambda: sv(office("morning"), at_desk("worried"), person(230, 450, 0.95, "happy", "point", "man2", GOLD, "b"), papers(400, 330, 5)),
 "t03-2": lambda: sv(office("morning"), at_desk("anxious", "phone"), thought(80, 40, 260, 150, person(210, 175, 0.55, "angry", "point", "boss", "#5a6b8c", "b"))),
 "t03-3": lambda: sv(office("morning"), me(400, 470, 1.0, "worried", "phone"), bubble(500, 60, 230, 80, "هههه", WHITE, -1, 34, RED), bubble(80, 80, 200, 70, ":P", WHITE, 1, 34, RED)),
 "t03-4": lambda: sv(office("morning"), me(250, 470, 1.0, "angry", "head"), laptop(560, 330, 1.0, "#f3c1bb", T(560, 290, "!", 60, RED))),
 "t03-5": lambda: sv(office("morning"), person(560, 450, 0.9, "happy", "point", "boss", "#5a6b8c", "b"), person(700, 450, 0.8, "happy", "up", "man2", GOLD, "c"), me(240, 450, 0.95, "sad", "cross"), bulb(240, 80)),
 "t03-6": lambda: sv(office("morning"), at_desk("worried", "head", WHITE, S("M636,262 h88 M636,280 h64 M636,298 h80", "#c3ccd6", 6) + S("M634,258 l30,30 M664,258 l-30,30", RED, 5))),
 "t03-7": lambda: sv(office("morning"), me(300, 460, 0.95, "happy", "wave"), person(560, 460, 0.9, "worried", "down", "man2", "#9b7fc2", "b"), T(560, 110, "?", 70, INK)),
 "t03-8": lambda: sv(office("morning"), me(330, 470, 1.0, "anxious", "head"), checklist(560, 110, 5, 0), sparkles(500, 90, RED, 2)),
 # 12:30 noon
 "t04-1": lambda: sv(office("noon"), at_desk("shocked", "head", WHITE, R(645, 275, 70, 14, RED, 3))),
 "t04-2": lambda: sv(plain(), me(260, 470, 1.0, "sad", "phone"), big_phone(560, 250, 2.4) + mini_screen_people(560, 200) + heart(560, 280, 0.9) + star(530, 140, 14) + star(590, 140, 14)),
 "t04-3": lambda: sv(office("noon"), me(400, 470, 1.0, "happy", "up"), confetti(150, 40, 500, 160), checklist(600, 200, 4, 4)),
 "t04-4": lambda: sv(plain("#eef0f6", "#f7f2ea"), me(280, 470, 1.0, "worried", "shrug"), person(560, 470, 0.95, "annoyed", "point", "man2", GOLD2, "c"), bubble(440, 40, 300, 80, "اتغيرت!", WHITE, -1, 34)),
 "t04-5": lambda: sv(plain(), me(260, 470, 1.0, "anxious", "phone"), big_phone(560, 250, 2.4) + T(560, 260, "-$", 50, RED) + money(560, 330)),
 "t04-6": lambda: sv(plain(), me(260, 470, 1.0, "sad", "phone"), big_phone(560, 250, 2.4) + mini_screen_people(540, 230) + mini_screen_people(580, 230) + mini_screen_people(560, 280)),
 "t04-7": lambda: sv(office("noon"), me(260, 450, 0.95, "blush", "down"), person(540, 450, 0.9, "happy", "point", "boss", "#5a6b8c", "b"), star(400, 90, 34), star(460, 140, 20), bubble(560, 40, 160, 66, "", WHITE, -1) + heart(640, 75, 1.0)),
 "t04-8": lambda: sv(plain(), me(260, 470, 1.0, "angry", "phone"), big_phone(560, 250, 2.4) + R(520, 170, 70, 26, WHITE, 10) + R(530, 210, 70, 26, "#c7f0d0", 10) + R(520, 250, 70, 26, WHITE, 10) + T(560, 300, "!!", 40, RED)),
 # 2:00 noon
 "t05-1": lambda: sv(office("noon"), at_desk("neutral", "hold"), food(480, 326)),
 "t05-2": lambda: sv(office("noon"), at_desk("tired"), clock(170, 120, 0.8, False), S("M380,180 c-20,-30 20,-40 0,-70", GREY, 5)),
 "t05-3": lambda: sv(office("noon"), me(280, 450, 0.95, "worried", "cross"), person(520, 450, 0.95, "angry", "point", "woman", "#9b7fc2", "b"), bubble(560, 40, 200, 70, "بس اسمع...", WHITE, -1, 28)),
 "t05-4": lambda: sv(office("noon"), at_desk("tired", "head", "#ffffff"), S("M470,100 l-12,-24 M500,90 v-26 M530,100 l12,-24", GOLD2, 6)),
 "t05-5": lambda: sv(office("noon"), person(450, 450, 0.95, "happy", "point", "man2", GOLD, "c"), cake(650, 330), me(220, 450, 0.9, "happy", "up"), confetti(100, 30, 600, 120)),
 "t05-6": lambda: sv(shop("noon"), person(560, 450, 0.75, "annoyed", "down", "man2", GOLD, "b"), person(640, 450, 0.75, "neutral", "down", "woman", PINK, "c"), person(720, 450, 0.75, "tired", "down", "man2", "#9b7fc2", "a"), me(300, 470, 1.0, "annoyed", "cross")),
 "t05-7": lambda: sv(plain(), me(260, 470, 1.0, "blush", "phone"), big_phone(560, 250, 2.4) + T(560, 230, "?", 80, RED) + heart(560, 300, 0.9, PINK)),
 "t05-8": lambda: sv(office("noon"), at_desk("sad"), clock(170, 120, 0.8, False), checklist(80, 230, 4, 0)),
 # 4:00 afternoon
 "t06-1": lambda: sv(plain("#fdeacb", "#f7f2ea"), me(260, 470, 1.0, "happy", "phone"), big_phone(560, 250, 2.4) + heart(560, 230, 1.6)),
 "t06-2": lambda: sv(plain("#fdeacb", "#f7f2ea"), me(260, 470, 1.0, "tired", "phone"), battery_icon(470, 70, 0.2), big_phone(600, 280, 2.0) + notes(580, 300, GOLD2)),
 "t06-3": lambda: sv(office("afternoon"), me(280, 450, 0.95, "blush", "down"), person(540, 450, 0.9, "happy", "up", "woman", GOLD, "b"), sparkles(360, 60, GOLD, 3)),
 "t06-4": lambda: sv(living("afternoon"), me(320, 470, 1.0, "neutral", "down", sit=True), person(560, 470, 0.9, "happy", "reach", "kid", RED, "b"), drawing(670, 300)),
 "t06-5": lambda: sv(plain("#fdeacb", "#f7f2ea"), me(260, 470, 1.0, "worried", "cross"), person(540, 470, 0.95, "neutral", "reach", "man2", GOLD2, "c"), money(660, 260), T(400, 120, "?", 60, INK)),
 "t06-6": lambda: sv(living("afternoon"), me(400, 470, 1.0, "neutral", "down", sit=True), sparkles(600, 80, GOLD, 3)),
 "t06-7": lambda: sv(plain("#e8eef6", "#f7f2ea"), me(260, 470, 1.0, "worried", "phone"), big_phone(560, 250, 2.4) + C(560, 220, 30, "#f0c39e") + P("M572,232 q6,12 0,20 q-6,-8 0,-20 Z", "#7cc0e8")),
 "t06-8": lambda: sv(plain("#fdeacb", "#f7f2ea"), me(260, 470, 1.0, "blush", "phone"), big_phone(560, 250, 2.4) + star(560, 230, 34) + book(560, 330)),
 # 5:00 afternoon
 "t07-1": lambda: sv(stairs("afternoon"), person(560, 440 - 120, 0.85, "tired", "hold", "old", "#9b7fc2", "a"), bag(500, 300), bag(620, 300, RED), me(300, 450, 0.95, "worried", "down")),
 "t07-2": lambda: sv(street("afternoon"), me(300, 470, 1.0, "worried", "reach"), cat(560, 440, 1.2), bubble(560, 230, 120, 64, "مياو", WHITE, -1, 28)),
 "t07-3": lambda: sv(living("afternoon"), person(560, 470, 0.95, "sad", "head", "kid", GOLD, "b", True), book(660, 470), me(300, 470, 0.95, "neutral", "down", sit=True), T(560, 120, "?", 70, INK)),
 "t07-4": lambda: sv(street("afternoon"), me(320, 470, 1.0, "shocked", "point"), wallet(600, 450), sparkles(560, 360, GOLD, 3)),
 "t07-5": lambda: sv(shop("afternoon"), person(645, 300, 0.75, "angry", "point", "man2", GOLD, "c"), me(320, 470, 1.0, "sad", "down"), bubble(420, 40, 200, 70, "#@!", WHITE, 1, 36, RED)),
 "t07-6": lambda: sv(street("afternoon"), person(560, 470, 0.95, "happy", "wave", "kid", RED, "b"), ball(480, 450), me(280, 470, 1.0, "neutral", "down")),
 "t07-7": lambda: sv(street("afternoon"), me(300, 470, 1.0, "blush", "down"), flowers(560, 460), heart(380, 110, 1.2)),
 "t07-8": lambda: sv(street("afternoon"), person(560, 470, 0.85, "sad", "head", "kid", GOLD, "a"), person(680, 470, 0.8, "happy", "point", "kid", RED, "c"), me(280, 470, 1.0, "worried", "down"), T(680, 140, "هههه", 34, RED)),
 # 6:00 evening
 "t08-1": lambda: sv(living("evening"), me(450, 470, 1.0, "tired", "down", sit=True), clock(150, 290, 0.7, False), battery_icon(560, 80, 0.3, GOLD)),
 "t08-2": lambda: sv(kitchen("evening"), me(300, 470, 1.0, "tired", "head"), papers(520, 330, 3) + "".join(C(560 + i * 30, 300 - i * 12, 26, WHITE, f'stroke="{INK}" stroke-width="3"') for i in range(4))),
 "t08-3": lambda: sv(living("evening"), me(450, 470, 1.0, "worried", "down", sit=True), cloud(450, 70, 0.75, "#9aa6b5"), T(450, 85, "?", 50, WHITE)),
 "t08-4": lambda: sv(dark_room(), me(400, 470, 1.0, "annoyed", "shrug"), T(600, 120, "!", 70, GOLD)),
 "t08-5": lambda: sv(living("evening"), me(330, 470, 1.0, "happy", "down", sit=True), guitar(600, 420), notes(600, 140, TEAL)),
 "t08-6": lambda: sv(living("evening"), me(330, 470, 1.0, "angry", "head"), papers(520, 420, 3), ball(650, 420, 20), book(560, 440), steam(320, 110)),
 "t08-7": lambda: sv(living("evening"), me(450, 470, 1.0, "sad", "down", sit=True), cloud(620, 90, 0.5, "#9aa6b5")),
 "t08-8": lambda: sv(plain("#efe4f4", "#f7f2ea"), me(260, 470, 1.0, "happy", "up"), big_phone(580, 260, 2.4) + star(580, 240, 40) + confetti(450, 30, 300, 120)),
 # 8:00 night
 "t09-1": lambda: sv(living("night"), me(330, 470, 0.95, "neutral", "down", sit=True), person(560, 470, 0.95, "sad", "down", "woman", "#9b7fc2", "b", True), bubble(560, 60, 180, 70, "...", WHITE, -1, 44)),
 "t09-2": lambda: sv(living("night"), person(560, 470, 0.95, "happy", "point", "man2", GOLD, "c"), me(300, 470, 1.0, "sad", "down"), bubble(500, 40, 200, 70, "هههه", WHITE, -1, 32, RED)),
 "t09-3": lambda: sv(living("night"), me(400, 470, 1.0, "calm", "hold", sit=True), book(400, 478), clock(150, 290, 0.6, False)),
 "t09-4": lambda: sv(kitchen("night"), person(240, 372, 0.85, "happy", "down", "mom", "#a35d6a", "a", True), me(420, 372, 0.9, "worried", "phone", sit=True), person(590, 372, 0.85, "happy", "down", "kid", RED, "b", True), table_front(), food(330, 326), food(505, 326), C(525, 150, 18, RED) + T(525, 158, "9", 22, WHITE)),
 "t09-5": lambda: sv(living("night"), person(560, 470, 0.9, "sad", "down", "kid", GOLD, "b"), grade(400, 250), me(240, 470, 0.95, "worried", "down")),
 "t09-6": lambda: sv(kitchen("night"), person(580, 450, 0.9, "happy", "hold", "mom", "#a35d6a", "a"), me(330, 372, 0.95, "happy", "down", sit=True), table_front(), food(450, 326), heart(580, 70, 1.2)),
 "t09-7": lambda: sv(dark_room(), me(300, 470, 1.0, "sad", "phone", sit=True), thought(470, 40, 300, 170, mini_screen_people(560, 110) + star(660, 110, 18) + heart(620, 160, 0.8))),
 "t09-8": lambda: sv(living("night"), person(560, 470, 0.95, "worried", "down", "man2", GOLD2, "c", True), me(320, 470, 0.95, "calm", "down", sit=True), bulb(560, 90)),
 # 10:00 night (bed)
 "t10-1": lambda: sv(bedroom("night"), in_bed("worried"), thought(470, 40, 260, 160, scribble(600, 120, INK, 1.2))),
 "t10-2": lambda: sv(bedroom("night"), in_bed("anxious", "head"), calendar(600, 320, T(600, 330, "!", 50, RED))),
 "t10-3": lambda: sv(bedroom("night"), in_bed("worried", "head"), thought(470, 40, 260, 160, C(600, 120, 40, "#f0c39e") + E(586, 112, 6, 8, INK) + E(614, 112, 6, 8, INK) + E(600, 140, 10, 7, INK))),
 "t10-4": lambda: sv(bedroom("night"), in_bed("shocked", "head"), cake(600, 360)),
 "t10-5": lambda: sv(bedroom("night"), in_bed("angry"), thought(470, 40, 260, 160, bubble(520, 80, 80, 50, "...", WHITE, -1, 30) + bubble(610, 110, 80, 50, "!!", WHITE, 1, 30, RED))),
 "t10-6": lambda: sv(bedroom("night"), me(560, 440, 0.95, "tired", "up"), S("M520,250 l-20,-10 M520,270 l-26,0", RED, 6), T(470, 230, "آه!", 40, RED)),
 "t10-7": lambda: sv(bedroom("night"), in_bed("anxious", "hold"), checklist(520, 80, 6, 1)),
 "t10-8": lambda: sv(bedroom("night"), in_bed("blush", "phone"), heart(500, 130, 1.3), heart(560, 90, 0.8, PINK), sparkles(600, 160, GOLD, 2)),
 # 11:30 late
 "t11-1": lambda: sv(LATE_ROOM(), in_bed("tired", "phone"), C(420, 230, 80, "#8fd0e8", 'opacity=".25"'), clock(600, 300, 0.7, False)),
 "t11-2": lambda: sv(LATE_ROOM(), in_bed("worried", "phone"), bubble(470, 60, 220, 70, "صاحي؟", WHITE, -1, 32)),
 "t11-3": lambda: sv(LATE_ROOM(), in_bed("anxious"), clock(600, 300, 0.7, False), S("M430,120 c30,-30 60,30 90,0", GREY, 5), S("M440,160 c30,-30 60,30 90,0", GREY, 5)),
 "t11-4": lambda: sv(LATE_ROOM(), in_bed("tired", "hold"), tv(620, 300, P("M600,200 l40,25 l-40,25 Z", WHITE))),
 "t11-5": lambda: sv(LATE_ROOM(), in_bed("annoyed", "head"), notes(560, 140, RED), notes(660, 230, RED), T(620, 100, "!!", 40, RED)),
 "t11-6": lambda: sv(LATE_ROOM(), in_bed("shocked", "phone"), bubble(470, 50, 240, 70, "ضروري!", WHITE, -1, 32, RED), laptop(620, 360, 0.6)),
 "t11-7": lambda: sv(LATE_ROOM(), in_bed("calm"), sparkles(500, 90, GOLD, 4), heart(640, 200, 0.9, GOLD)),
 "t11-8": lambda: sv(LATE_ROOM(), in_bed("sad"), cloud(560, 110, 0.95, "#5a6378"), T(560, 125, "مش كفاية", 30, WHITE)),
}


def render(svg):
    png = subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H)], input=svg.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    ids = sorted(ART)
    imgs = {}
    for k in ids:
        im = render(ART[k]())
        im.save(os.path.join(OUT, k + ".webp"), "WEBP", quality=78, method=6)
        imgs[k] = im
    print(f"drew {len(ids)} pictures → {OUT}")
    if "--sheet" in sys.argv:
        dest = sys.argv[sys.argv.index("--sheet") + 1]
        cols, tw, th = 8, 400, 250
        rows = math.ceil(len(ids) / cols)
        sheet = Image.new("RGB", (cols * tw, rows * (th + 24)), "white")
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet)
        for i, k in enumerate(ids):
            x, y = (i % cols) * tw, (i // cols) * (th + 24)
            sheet.paste(imgs[k].resize((tw, th)), (x, y + 24))
            d.text((x + 6, y + 4), k, fill="black")
        sheet.save(dest)
        print("sheet:", dest)


if __name__ == "__main__":
    main()
