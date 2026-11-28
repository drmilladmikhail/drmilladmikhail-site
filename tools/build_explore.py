#!/usr/bin/env python3
"""Build the unified knowledge graph (explore/graph-data.json) and interactive /explore/ page.

Reads:
  - articles/articles.json
  - content/feelings.json
  - content/glossary.json (+ content/glossary-more.json if present)
  - content/exercises.json & content/worksheets.json
  - music-library.json (if present) and calm/index.html ("دقيقة لنفسك" audio library)

Outputs:
  - explore/graph-data.json  (Nodes classified by type + Links between shared keywords/themes)
  - explore/index.html       (RTL cozy dark interactive knowledge graph page, strict CSP)
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://drmilladmikhail.com"

CSP = (
    "default-src 'self'; "
    "script-src 'self' https://www.googletagmanager.com https://static.cloudflareinsights.com; "
    "style-src 'self' 'unsafe-inline'; "
    "font-src 'self'; "
    "img-src 'self' data: https://*.google-analytics.com https://www.googletagmanager.com "
    "https://images.unsplash.com https://i.ytimg.com https://putqeswsycwyxxrdcmyh.supabase.co; "
    "frame-src https://www.youtube-nocookie.com; "
    "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com "
    "https://www.googletagmanager.com https://cloudflareinsights.com https://putqeswsycwyxxrdcmyh.supabase.co; "
    "object-src 'none'; base-uri 'self'; form-action 'self' https://formsubmit.co"
)

LABELS = {
    "article": "مقال",
    "feeling": "مشاعر",
    "exercise": "تمارين",
    "audio": "دقيقة لنفسك",
    "glossary": "مصطلح نفسي",
}

CTAS = {
    "article": "اقرأ المقال",
    "feeling": "افهم الشعور",
    "exercise": "ابدأ التمرين",
    "audio": "استمع الآن",
    "glossary": "اقرأ المصطلح",
}

# Canonical psychological themes used for tagging, clustering, and semantic linking.
THEMES = [
    (
        "نمط التعلّق",
        ("تعلق", "التعلق", "متجنب", "هجر", "قصف بالحب", "attachment", "امان عاطفي", "القرب"),
        (0.41, 0.39),
    ),
    (
        "العلاقات",
        ("علاقه", "علاقات", "شريك", "زواج", "زوج", "زوجين", "حب", "ثقه", "تواصل", "خلاف", "خرس", "انفصال", "طلاق", "اهل", "نرجسي", "تلاعب", "جاسلايتنج", "غيره", "غيران"),
        (0.31, 0.27),
    ),
    (
        "القلق",
        ("قلق", "قلقان", "توتر", "متوتر", "خوف", "خايف", "هلع", "وسواس", "ارق", "تهويل", "اقتحاميه", "تنفس", "تاريض", "امان"),
        (0.22, 0.37),
    ),
    (
        "الحدود",
        ("حدود", "حدودي", "حزم", "ارضاء", "قول لا", "استنزاف", "مضغوط", "تحكم", "مخنوق", "مستغل"),
        (0.55, 0.33),
    ),
    (
        "التّشافي",
        ("تعافي", "تشافي", "شفاء", "صدمه", "مرونه", "امل", "تقبل", "حنيه", "تعاطف مع الذات", "تقدير الذات", "طمانينه", "معني", "امتنان", "رضا", "مرتاح", "سلام"),
        (0.54, 0.54),
    ),
    (
        "المشاعر والحزن",
        ("حزن", "زعلان", "اكتئاب", "وحده", "وحيد", "فقد", "وفاه", "حداد", "مخذول", "ياس", "فراغ", "تبلد", "مشاعر"),
        (0.39, 0.22),
    ),
    (
        "الضغط والطاقة",
        ("ارهاق", "مرهق", "احتراق", "طاقه", "بطاريتي", "تسويف", "كماليه", "تشتت", "مشتت", "جلد الذات", "ذنب", "خزي", "مقارنه", "غضب", "متعصب", "احباط"),
        (0.51, 0.23),
    ),
]

CURATED_GLOSSARY_SLUGS = {
    "attachment",
    "anxious-attachment",
    "avoidant-attachment",
    "secure-attachment",
    "boundaries",
    "anxiety",
    "depression",
    "sadness",
    "stress",
    "self-compassion",
    "self-esteem",
    "burnout",
    "gaslighting",
    "mindfulness",
    "emotional-regulation",
    "resilience",
    "self-criticism",
    "procrastination",
    "grief",
    "panic-attack",
    "stonewalling",
    "assertiveness",
}

CURATED_CALM_SLUGS = {
    "calm-the-worry",
    "release-tension",
    "night-lullaby",
    "soft-comfort",
    "warm-companionship",
    "tender-farewell",
    "steady-anchor",
    "deep-rest",
    "forgive-yourself",
    "painful-attachment",
    "gentle-letting-go",
    "healthy-boundaries",
    "clear-mind",
    "quiet-spark",
    "open-sky",
    "still-water",
    "morning-thankfulness",
    "01",
    "05",
}


def normalize_ar(text: str) -> str:
    t = str(text or "").lower()
    t = re.sub(r"[\u064B-\u065F\u0670\u06D6-\u06ED\u0640]", "", t)
    t = re.sub(r"[أإآٱ]", "ا", t)
    t = t.replace("ؤ", "و").replace("ئ", "ي").replace("ى", "ي").replace("ة", "ه")
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def short_label(title: str, max_words: int = 3) -> str:
    head = re.split(r"[:؟?—–\-،]", title)[0].strip()
    head = re.sub(r"^[٠-٩0-9]+\s*·\s*", "", head)
    for prefix in ("كيفية التعامل مع ", "التعامل مع ", "إزاي أتعامل مع ", "إزاي تتعامل مع ", "الفرق بين "):
        if head.startswith(prefix):
            head = head[len(prefix):].strip()
    words = head.split()
    if len(words) > max_words:
        head = " ".join(words[:max_words])
    return head


def trim_summary(text: str, limit: int = 98) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(clean) <= limit:
        return clean
    cut = clean.rfind(" ", 50, limit)
    if cut == -1:
        cut = limit
    return clean[:cut].rstrip("،.,؛:") + "…"


def _load_json(rel_path: str, default):
    path = ROOT / rel_path
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def extract_tags_and_tokens(raw_text: str, category_hint: str = "") -> tuple[list[str], set[str]]:
    norm = normalize_ar(raw_text + " " + category_hint)
    matched_themes: list[str] = []
    for theme_name, stems, _pos in THEMES:
        if any(stem in norm for stem in stems):
            matched_themes.append(theme_name)
    if not matched_themes:
        if "rel" in category_hint or "love" in category_hint:
            matched_themes.append("العلاقات")
        elif "anx" in category_hint or "fear" in category_hint:
            matched_themes.append("القلق")
        else:
            matched_themes.append("التّشافي")

    stop = {
        "في", "من", "علي", "على", "الي", "الى", "عن", "مع", "ده", "دي", "او", "لو", "ولا",
        "مش", "كل", "اي", "ايه", "ازاي", "امتي", "ليه", "بس", "ان", "انك", "انه", "انها",
        "بين", "بعد", "قبل", "وقت", "جدا", "اكتر", "حاجة", "حاجه", "حد", "نفسك", "حياتك",
        "خطوات", "عمليه", "بسيطه", "مقال", "تمرين", "دقيقه", "لنفسك", "شعور", "احساس",
    }
    tokens = {
        w for w in norm.split()
        if len(w) >= 3 and w not in stop and not w.isdigit()
    }
    return matched_themes[:3], tokens


def load_audio_nodes() -> list[dict]:
    """Read music-library.json if present; otherwise extract curated tracks from calm/index.html."""
    for candidate in ("music-library.json", "content/music-library.json", "assets/calm/music-library.json"):
        data = _load_json(candidate, None)
        if isinstance(data, list) and data:
            items = data
            break
        if isinstance(data, dict) and data.get("tracks"):
            items = data["tracks"]
            break
    else:
        items = []
        calm_html_path = ROOT / "calm" / "index.html"
        if calm_html_path.is_file():
            calm_html = calm_html_path.read_text(encoding="utf-8")
            pattern = re.compile(
                r'<li class="calm-track"(?:\s+data-cat="([^"]*)")?(?:\s+data-search="([^"]*)")?[^>]*>'
                r'.*?<b>([^<]+)</b>(?:<span class="calm-track-cat">([^<]+)</span>)?.*?'
                r'<span lang="en" dir="ltr">([^<]+)</span>.*?src="([^"]+)"',
                re.S,
            )
            for cat, search_attr, ar_name, cat_ar, en_name, src in pattern.findall(calm_html):
                slug = Path(src).stem
                if slug not in CURATED_CALM_SLUGS:
                    continue
                clean_title = re.sub(r"^[٠-٩0-9]+\s*·\s*", "", html.unescape(ar_name)).strip()
                items.append({
                    "slug": slug,
                    "title": f"دقيقة لنفسك: {clean_title}",
                    "label": clean_title,
                    "category": cat or "calm",
                    "summary": (
                        f"مقطوعة صوتية هادئة ({html.unescape(en_name)}) مصممة لمرافقتك وقت الشعور بـ«{clean_title}» "
                        f"واستعادة هدوئك في دقيقتين."
                    ),
                    "search": f"{clean_title} {en_name} {cat_ar} {search_attr} دقيقة لنفسك موسيقى استماع هدوء",
                    "href": "/calm/#calm-minute-h" if "/calm/music/" in src else "/calm/#calm-music-h",
                })

    nodes = []
    for item in items:
        slug = item.get("slug") or item.get("id")
        if not slug:
            continue
        title = item["title"]
        summary = trim_summary(item.get("summary") or item.get("description") or title)
        raw = f"{title} {summary} {item.get('search', '')}"
        tags, tokens = extract_tags_and_tokens(raw, item.get("category", ""))
        nodes.append({
            "id": f"audio:{slug}",
            "title": title,
            "label": item.get("label") or short_label(title.replace("دقيقة لنفسك:", "").strip(), 2),
            "type": "audio",
            "typeLabel": LABELS["audio"],
            "summary": summary,
            "href": item.get("href", "/calm/#calm-minute-h"),
            "cta": CTAS["audio"],
            "tags": tags,
            "hub": slug in {"calm-the-worry", "gentle-letting-go", "still-water"},
            "_tokens": tokens,
            "_refs": set(),
        })
    return nodes


def collect_nodes() -> list[dict]:
    nodes: list[dict] = []

    # 1. Articles (articles/articles.json)
    articles = _load_json("articles/articles.json", [])
    featured_article_labels = {
        "four-attachment-styles": "نمط التعلّق",
        "anxious-avoidant-attraction": "القلق والمتجنب",
        "people-pleasing-saying-no": "إرضاء الناس",
        "burnout-signs-recovery": "الاحتراق النفسي",
        "panic-attack-what-to-do": "نوبة الهلع",
        "why-is-it-hard-to-leave": "العلاقة المؤذية",
        "early-red-flags-love-bombing": "القصف بالحب",
        "first-days-after-breakup": "التعافي بعد الانفصال",
        "marital-silence": "الخرس الزوجي",
        "procrastination-not-laziness": "التسويف",
        "perfectionism-never-good-enough": "الكمالية",
        "trauma-after-hard-event": "الصدمة النفسية",
        "sadness-vs-depression": "الحزن والاكتئاب",
        "grief-after-losing-loved-one": "ألم الفقد",
        "cbt-explained": "العلاج المعرفي",
        "life-satisfaction": "الرضا عن الحياة",
    }
    hub_articles = {
        "four-attachment-styles",
        "people-pleasing-saying-no",
        "burnout-signs-recovery",
        "why-is-it-hard-to-leave",
        "first-days-after-breakup",
        "sadness-vs-depression",
    }
    for art in articles:
        slug = art["slug"]
        title = art["title"]
        summary = trim_summary(art.get("summary") or art.get("description") or "")
        cat = art.get("category", "")
        raw = f"{title} {art.get('description', '')} {art.get('summary', '')} {slug.replace('-', ' ')}"
        tags, tokens = extract_tags_and_tokens(raw, cat)
        nodes.append({
            "id": f"article:{slug}",
            "title": title,
            "label": featured_article_labels.get(slug) or short_label(title, 3),
            "type": "article",
            "typeLabel": LABELS["article"],
            "summary": summary,
            "href": f"/articles/{slug}/",
            "cta": CTAS["article"],
            "tags": tags,
            "hub": slug in hub_articles,
            "_tokens": tokens,
            "_refs": set(),
        })

    # 2. Feelings (content/feelings.json)
    feelings_data = _load_json("content/feelings.json", {"families": []})
    hub_feelings = {"worried", "lonely", "exhausted", "suffocated", "guilty", "calm"}
    for fam in feelings_data.get("families", []):
        fam_name = fam.get("name", "")
        for item in fam.get("items", []):
            fid = item["id"]
            name = item["name"]
            summary = trim_summary(f"{item.get('means', '')} {item.get('says', '')}")
            raw = f"{name} {fam_name} {item.get('means', '')} {item.get('says', '')} {item.get('try', '')}"
            tags, tokens = extract_tags_and_tokens(raw, fam.get("id", ""))
            if "المشاعر والحزن" not in tags and fam.get("id") == "sad":
                tags = (["المشاعر والحزن"] + tags)[:3]
            nodes.append({
                "id": f"feeling:{fid}",
                "title": f"شعور: {name}",
                "label": name,
                "type": "feeling",
                "typeLabel": LABELS["feeling"],
                "summary": summary,
                "href": f"/feelings/#f-{fid}",
                "cta": CTAS["feeling"],
                "tags": tags,
                "hub": fid in hub_feelings,
                "_tokens": tokens,
                "_refs": set(),
            })

    # 3. Glossary / Psychological Concepts (content/glossary.json + content/glossary-more.json)
    glossary_items = list(_load_json("content/glossary.json", {"items": []}).get("items", []))
    glossary_items.extend(_load_json("content/glossary-more.json", {"items": []}).get("items", []))
    hub_glossary = {"attachment", "boundaries", "anxiety", "self-compassion", "resilience", "depression"}
    seen_glossary = set()
    for term in glossary_items:
        slug = term.get("slug", "")
        if not slug or slug in seen_glossary or slug not in CURATED_GLOSSARY_SLUGS:
            continue
        seen_glossary.add(slug)
        title = term["title"]
        aliases = " ".join(term.get("aliases", []))
        summary = trim_summary(term.get("summary") or term.get("definition") or "")
        raw = f"{title} {term.get('english', '')} {aliases} {summary} {term.get('category', '')}"
        tags, tokens = extract_tags_and_tokens(raw, term.get("category", ""))
        refs = {f"glossary:{r}" for r in term.get("related", [])}
        nodes.append({
            "id": f"glossary:{slug}",
            "title": title,
            "label": "الحدود" if slug == "boundaries" else short_label(title, 2),
            "type": "glossary",
            "typeLabel": LABELS["glossary"],
            "summary": summary,
            "href": f"/glossary/{slug}/",
            "cta": CTAS["glossary"],
            "tags": tags,
            "hub": slug in hub_glossary,
            "searchExtra": f"{term.get('english', '')} {aliases}".strip(),
            "_tokens": tokens,
            "_refs": refs,
        })

    # 4. Exercises & Printable Worksheets (content/exercises.json + content/worksheets.json)
    for ex in _load_json("content/exercises.json", {"items": []}).get("items", []):
        slug = ex["slug"]
        title = ex["title"]
        summary = trim_summary(ex.get("goal", ""))
        raw = f"{title} {summary} {' '.join(ex.get('steps', []))}"
        tags, tokens = extract_tags_and_tokens(raw, "exercise")
        refs = set()
        rel = ex.get("related")
        if isinstance(rel, list) and rel:
            if rel[0].startswith("/articles/"):
                refs.add("article:" + rel[0].strip("/").split("/")[-1])
        nodes.append({
            "id": f"exercise:{slug}",
            "title": title,
            "label": short_label(title, 2),
            "type": "exercise",
            "typeLabel": "تمرين عملي",
            "summary": summary,
            "href": f"/exercise/#" + slug,
            "cta": CTAS["exercise"],
            "tags": tags,
            "hub": slug in {"mindful-breathing", "small-no", "energy-map"},
            "_tokens": tokens,
            "_refs": refs,
        })

    for ws in _load_json("content/worksheets.json", {"items": []}).get("items", []):
        slug = ws["slug"]
        title = ws["title"]
        summary = trim_summary(ws.get("desc") or ws.get("intro") or "")
        raw = f"{title} {summary} {ws.get('intro', '')}"
        tags, tokens = extract_tags_and_tokens(raw, ws.get("category", ""))
        refs = set()
        rel = ws.get("related")
        if isinstance(rel, list) and rel and rel[0].startswith("/articles/"):
            refs.add("article:" + rel[0].strip("/").split("/")[-1])
        nodes.append({
            "id": f"worksheet:{slug}",
            "title": f"ورقة تمرين: {title}",
            "label": short_label(title, 3),
            "type": "exercise",
            "typeLabel": "ورقة تمرين",
            "summary": summary,
            "href": f"/worksheets/#{slug}",
            "cta": CTAS["exercise"],
            "tags": tags,
            "hub": slug in {"boundaries-in-love", "when-they-dont-reply"},
            "_tokens": tokens,
            "_refs": refs,
        })

    # 5. Audio / "دقيقة لنفسك"
    nodes.extend(load_audio_nodes())
    return nodes


def build_links(nodes: list[dict]) -> list[dict]:
    by_id = {n["id"]: n for n in nodes}
    scored_pairs: dict[tuple[str, str], float] = {}
    per_node_candidates: dict[str, list[tuple[float, str]]] = {n["id"]: [] for n in nodes}

    for i, a in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            b = nodes[j]
            score = 0.0
            if b["id"] in a["_refs"] or a["id"] in b["_refs"]:
                score += 4.5
            shared_tags = set(a["tags"]) & set(b["tags"])
            if shared_tags:
                score += 1.45 * len(shared_tags)
                if a["tags"][0] == b["tags"][0]:
                    score += 0.85
            shared_tokens = a["_tokens"] & b["_tokens"]
            if shared_tokens:
                score += min(3.2, 0.72 * len(shared_tokens))
            # Reward cross-type bridges (e.g. Feeling <-> Article <-> Exercise <-> Audio)
            if score >= 2.1 and a["type"] != b["type"]:
                score += 0.55
            if score >= 2.35:
                pair = (a["id"], b["id"])
                scored_pairs[pair] = score
                per_node_candidates[a["id"]].append((score, b["id"]))
                per_node_candidates[b["id"]].append((score, a["id"]))

    # Keep top strongest edges per node so the graph stays airy, connected, and 60fps-friendly.
    selected_edges: dict[tuple[str, str], float] = {}
    degree: dict[str, int] = {n["id"]: 0 for n in nodes}

    for n in nodes:
        nid = n["id"]
        max_deg = 6 if n.get("hub") else 3
        cands = sorted(per_node_candidates[nid], reverse=True)
        # Prefer diverse target types first
        seen_types = set()
        ordered = []
        rest = []
        for sc, tid in cands:
            ttype = by_id[tid]["type"]
            if ttype not in seen_types:
                seen_types.add(ttype)
                ordered.append((sc, tid))
            else:
                rest.append((sc, tid))
        for sc, tid in ordered + rest:
            if degree[nid] >= max_deg:
                break
            tid_cap = 8 if by_id[tid].get("hub") else 4
            if degree[tid] >= tid_cap:
                continue
            key = (nid, tid) if nid < tid else (tid, nid)
            if key not in selected_edges:
                selected_edges[key] = round(min(1.0, sc / 6.0), 2)
                degree[nid] += 1
                degree[tid] += 1

    # Guarantee every node has at least 1 connection to its primary theme hub
    theme_hubs: dict[str, str] = {}
    for n in nodes:
        if n.get("hub") and n["tags"]:
            theme_hubs.setdefault(n["tags"][0], n["id"])
    for n in nodes:
        nid = n["id"]
        if degree[nid] == 0 and n["tags"]:
            hub_id = theme_hubs.get(n["tags"][0], "article:four-attachment-styles")
            if hub_id != nid and hub_id in by_id:
                key = (nid, hub_id) if nid < hub_id else (hub_id, nid)
                selected_edges[key] = 0.45
                degree[nid] += 1
                degree[hub_id] += 1

    return [
        {"source": src, "target": dst, "weight": weight}
        for (src, dst), weight in sorted(selected_edges.items())
    ]


def compute_constellation_layout(nodes: list[dict], links: list[dict]) -> None:
    """Deterministic organic nebula layout floating cleanly above the bottom-left reading corner."""
    anchor_map = {name: pos for name, _stems, pos in THEMES}
    pos: dict[str, list[float]] = {}

    for idx, n in enumerate(nodes):
        primary = n["tags"][0] if n["tags"] else "التّشافي"
        ax, ay = anchor_map.get(primary, (0.42, 0.38))
        angle = idx * 2.39996323
        radius = 0.025 if n.get("hub") else (0.045 + math.sqrt((idx % 11) / 11.0) * 0.115)
        pos[n["id"]] = [
            ax + math.cos(angle) * radius * 1.18,
            ay + math.sin(angle) * radius * 0.88,
        ]

    # Pin central constellation hub like reference artwork
    if "article:four-attachment-styles" in pos:
        pos["article:four-attachment-styles"] = [0.40, 0.39]

    ids = [n["id"] for n in nodes]
    hub_set = {n["id"] for n in nodes if n.get("hub")}

    for step in range(110):
        temp = 0.015 * (1.0 - step / 115.0)
        disp = {nid: [0.0, 0.0] for nid in ids}

        # Short-range soft repulsion (no hard box clamping -> organic star cluster!)
        for i in range(len(ids)):
            u = ids[i]
            ux, uy = pos[u]
            for j in range(i + 1, len(ids)):
                v = ids[j]
                dx = ux - pos[v][0]
                dy = uy - pos[v][1]
                dist2 = dx * dx + dy * dy + 1e-5
                if dist2 < 0.016:
                    dist = math.sqrt(dist2)
                    force = 0.00016 / dist2
                    fx = (dx / dist) * force
                    fy = (dy / dist) * force
                    disp[u][0] += fx
                    disp[u][1] += fy
                    disp[v][0] -= fx
                    disp[v][1] -= fy

        # Spring attraction along links
        for link in links:
            u, v = link["source"], link["target"]
            dx = pos[v][0] - pos[u][0]
            dy = pos[v][1] - pos[u][1]
            dist = math.sqrt(dx * dx + dy * dy + 1e-6)
            ideal = 0.095
            diff = (dist - ideal) * 0.055 * (0.6 + link["weight"])
            fx = (dx / dist) * diff
            fy = (dy / dist) * diff
            disp[u][0] += fx
            disp[u][1] += fy
            disp[v][0] -= fx
            disp[v][1] -= fy

        # Smooth elliptical containment + curved exclusion cushion around bottom-left reading nook
        for n in nodes:
            nid = n["id"]
            ax, ay = anchor_map.get(n["tags"][0], (0.42, 0.38))
            pull = 0.065 if nid in hub_set else 0.036
            disp[nid][0] += (ax - pos[nid][0]) * pull
            disp[nid][1] += (ay - pos[nid][1]) * pull

            # Elliptical soft outer boundary centered at (0.42, 0.38) with radii (0.31, 0.25)
            ex = (pos[nid][0] - 0.42) / 0.31
            ey = (pos[nid][1] - 0.38) / 0.25
            er = math.sqrt(ex * ex + ey * ey)
            if er > 1.0:
                push = (er - 1.0) * 0.045
                disp[nid][0] -= (ex / er) * push * 0.31
                disp[nid][1] -= (ey / er) * push * 0.25

            # Smooth elliptical cushion keeping bottom-left reading corner (bookshelves/lamp/chair) clear
            rx = (pos[nid][0] - 0.21) / 0.26
            ry = (pos[nid][1] - 0.77) / 0.31
            rr = math.sqrt(rx * rx + ry * ry + 1e-6)
            if rr < 1.0:
                lift = (1.0 - rr) * 0.038
                disp[nid][0] += (rx / rr) * lift * 0.22
                disp[nid][1] -= abs(ry / rr) * lift * 0.34 + 0.008

        for nid in ids:
            if nid == "article:four-attachment-styles":
                continue
            dx, dy = disp[nid]
            mag = math.sqrt(dx * dx + dy * dy + 1e-9)
            scale = min(temp, mag) / mag
            pos[nid][0] += dx * scale
            pos[nid][1] += dy * scale

    for n in nodes:
        x, y = pos[n["id"]]
        n["x"] = round(x, 3)
        n["y"] = round(y, 3)


def generate_graph_data() -> dict:
    nodes = collect_nodes()
    links = build_links(nodes)
    compute_constellation_layout(nodes, links)

    by_type: dict[str, int] = {}
    clean_nodes = []
    for n in nodes:
        by_type[n["type"]] = by_type.get(n["type"], 0) + 1
        entry = {
            "id": n["id"],
            "title": n["title"],
            "label": n["label"],
            "type": n["type"],
            "summary": n["summary"],
            "href": n["href"],
            "tags": n["tags"],
            "x": n["x"],
            "y": n["y"],
        }
        if n["typeLabel"] != LABELS.get(n["type"]):
            entry["typeLabel"] = n["typeLabel"]
        if n.get("hub"):
            entry["hub"] = True
        if n.get("searchExtra"):
            entry["search"] = n["searchExtra"]
        clean_nodes.append(entry)

    return {
        "meta": {
            "counts": {
                "nodes": len(clean_nodes),
                "links": len(links),
                "byType": by_type,
            },
            "defaultNode": "article:four-attachment-styles",
        },
        "nodes": clean_nodes,
        "links": links,
    }


def _asset_version(path: Path) -> str:
    if not path.is_file():
        return "1"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def render_explore_html(graph: dict) -> str:
    explore_dir = ROOT / "explore"
    css_v = _asset_version(explore_dir / "explore.css")
    js_v = _asset_version(explore_dir / "explore.js")
    svg_v = _asset_version(explore_dir / "reading-corner.svg")
    total_nodes = graph["meta"]["counts"]["nodes"]

    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "تصفّح شبكة المعرفة النفسية | د. ميلاد ميخائيل",
        "url": f"{SITE}/explore/",
        "inLanguage": "ar",
        "description": "مساحة ليلية هادئة لتصفّح المقالات والمشاعر والتمارين ومقطوعات دقيقة لنفسك في شبكة معرفة مترابطة.",
    }
    ld_json = json.dumps(ld, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>تصفّح شبكة المعرفة | د. ميلاد ميخائيل</title>
<meta name="description" content="مساحة تفاعلية هادئة لتصفّح المقالات والمشاعر والتمارين والمصطلحات ومقطوعات دقيقة لنفسك في شبكة معرفة نفسية مترابطة.">
<link rel="canonical" href="{SITE}/explore/">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/explore/">
<meta property="og:title" content="تصفّح شبكة المعرفة | د. ميلاد ميخائيل">
<meta property="og:description" content="استكشف الروابط بين مشاعرك، أنماط التعلّق، الحدود الصحية، التمارين العملية، ومقطوعات الهدوء.">
<meta property="og:image" content="{SITE}/assets/og/home.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0d1526">
<link rel="preload" href="/assets/fonts/ibm-plex-sans-arabic-arabic-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/noto-naskh-arabic-arabic-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/explore/explore.css?v={css_v}">
<script type="application/ld+json">{ld_json}</script>
</head>
<body class="explore-night">
<a class="skip-link" href="#explore-main">تخطّى إلى الشبكة التفاعلية</a>

<header class="ex-header topbar">
  <div class="ex-header-inner">
    <a class="ex-brand" href="/" aria-label="د. ميلاد ميخائيل — الصفحة الرئيسية">
      <svg class="ex-brand-icon" viewBox="0 0 36 36" aria-hidden="true" focusable="false">
        <circle cx="18" cy="18" r="16.5" fill="rgba(226,179,90,0.1)" stroke="#e2b35a" stroke-width="1.4"/>
        <path d="M18 7v22M13 12c2.5-2 7.5-2 10 0-2.5 2.5-7.5 2.5-10 5 2.5 2.5 7.5 2.5 10 5" fill="none" stroke="#e2b35a" stroke-width="1.6" stroke-linecap="round"/>
        <circle cx="18" cy="6.5" r="1.8" fill="#f5d08a"/>
      </svg>
      <span class="ex-brand-name">د. ميلاد ميخائيل</span>
    </a>

    <nav class="ex-nav" aria-label="التنقل الرئيسي">
      <a href="/">الرئيسية</a>
      <a href="/articles/">المكتبة</a>
      <a href="/explore/" aria-current="page" class="is-active">تصفّح</a>
      <a href="/about/">عنّي</a>
      <a href="/contact/">اتصل بنا</a>
    </nav>

    <div class="ex-search-box" role="search">
      <svg class="ex-search-icon" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/>
        <path d="M20 20l-4.2-4.2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      </svg>
      <label class="sr-only" for="explore-search">ابحث عن أي موضوع أو شعور</label>
      <input id="explore-search" type="search" maxlength="100" autocomplete="off" spellcheck="false" placeholder="ابحث عن أي موضوع أو شعور...">
      <button type="button" id="search-clear" class="ex-search-clear" aria-label="مسح البحث" hidden>×</button>
    </div>
  </div>

  <div class="ex-filter-bar" role="toolbar" aria-label="فلترة حسب نوع المحتوى">
    <div class="ex-filters">
      <button type="button" class="ex-filter is-active" data-filter="all" aria-pressed="true">الكل</button>
      <button type="button" class="ex-filter" data-filter="feeling" aria-pressed="false">مشاعر</button>
      <button type="button" class="ex-filter" data-filter="article" aria-pressed="false">مقالات</button>
      <button type="button" class="ex-filter" data-filter="exercise" aria-pressed="false">تمارين</button>
      <button type="button" class="ex-filter" data-filter="audio" aria-pressed="false">دقيقة لنفسك</button>
    </div>
    <p id="explore-status" class="ex-status" role="status" aria-live="polite">{total_nodes} موضوع مترابط</p>
  </div>
</header>

<main id="explore-main" class="ex-stage">
  <h1 class="sr-only">تصفّح شبكة المعرفة النفسية المترابطة</h1>

  <div class="ex-ambient" aria-hidden="true">
    <div class="ex-glow ex-glow-gold"></div>
    <div class="ex-glow ex-glow-blue"></div>
  </div>

  <div id="parallax-corner" class="ex-corner" aria-hidden="true">
    <img src="/explore/reading-corner.svg?v={svg_v}" width="460" height="390" alt="" decoding="async">
  </div>

  <canvas id="explore-canvas" class="ex-canvas" aria-label="شبكة المعرفة التفاعلية — اضغط على أي عقدة لعرض التفاصيل"></canvas>

  <div class="ex-zoom-controls" aria-label="التحكم في عرض الشبكة">
    <button type="button" id="zoom-in" class="ex-ctrl-btn" aria-label="تكبير" title="تكبير">+</button>
    <button type="button" id="zoom-out" class="ex-ctrl-btn" aria-label="تصغير" title="تصغير">−</button>
    <button type="button" id="zoom-reset" class="ex-ctrl-btn" aria-label="إعادة ضبط المشهد" title="إعادة ضبط المشهد">⟲</button>
  </div>

  <p id="mobile-hint" class="ex-hint">اضغط على أي نجمة مضيئة لاستكشاف روابطها</p>

  <div id="empty-toast" class="ex-empty-toast" hidden>
    <p>لا توجد عقد مطابقة لهذا البحث حالياً.</p>
    <button type="button" id="reset-all" class="ex-reset-btn">إظهار كل الشبكة</button>
  </div>

  <aside id="node-card" class="ex-card" aria-live="polite" aria-labelledby="card-title" hidden>
    <button type="button" id="card-close" class="ex-card-close" aria-label="إغلاق البطاقة">×</button>
    <div class="ex-card-head">
      <span id="card-type" class="ex-card-badge">مقال</span>
    </div>
    <h2 id="card-title" class="ex-card-title">أنماط التعلّق الأربعة</h2>
    <p id="card-summary" class="ex-card-summary"></p>

    <div class="ex-card-section">
      <span class="ex-card-sublabel">مواضيع مترابطة:</span>
      <div id="card-related" class="ex-card-pills"></div>
    </div>

    <a id="card-cta" class="ex-card-cta" href="/articles/">
      <span id="card-cta-label">اقرأ المقال</span>
      <span class="ex-cta-arrow" aria-hidden="true">←</span>
    </a>
  </aside>
</main>

<script src="/explore/explore.js?v={js_v}" defer></script>
</body>
</html>
"""


def write_outputs() -> dict:
    explore_dir = ROOT / "explore"
    explore_dir.mkdir(parents=True, exist_ok=True)

    graph = generate_graph_data()
    graph_path = explore_dir / "graph-data.json"
    graph_path.write_text(
        json.dumps(graph, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    index_path = explore_dir / "index.html"
    index_path.write_text(render_explore_html(graph), encoding="utf-8")
    return graph


def build(ba=None, page=None, write=None, SITE_URL=SITE):
    """Compatibility entry point for tools/build_extras.py and tools/build_pages.py."""
    return write_outputs()


def main() -> None:
    graph = write_outputs()
    counts = graph["meta"]["counts"]
    graph_kb = (ROOT / "explore" / "graph-data.json").stat().st_size / 1024.0
    html_kb = (ROOT / "explore" / "index.html").stat().st_size / 1024.0
    print(
        f"explore: wrote {counts['nodes']} nodes and {counts['links']} links "
        f"({counts['byType']}) -> graph-data.json ({graph_kb:.1f} KB), index.html ({html_kb:.1f} KB)"
    )


if __name__ == "__main__":
    main()
