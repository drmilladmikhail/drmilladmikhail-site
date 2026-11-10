"""Reviewed static resource connections, never a personal recommendation engine."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LABELS = {"story": "حكاية مرتبطة", "concept": "معنى من القاموس", "exercise": "تمرين اختياري"}
ACTIONS = {"story": "افتح الحكاية", "concept": "افتح المعنى", "exercise": "افتح التمرين"}


def resolve(raw, stories, exercises, terms, all_story_ids):
    """Resolve stable IDs to current titles and consent-gated story anchors."""
    output = {"story": {}, "exercise": {}}
    for group, kind, sources in (("stories", "story", all_story_ids),
                                 ("exercises", "exercise", exercises)):
        seen = set()
        for item in raw[group]:
            sid = item.get("id", "")
            if not isinstance(sid, str) or not SLUG.fullmatch(sid) or sid in seen or sid not in sources:
                raise ValueError("Invalid or duplicate next-step source: " + repr(sid))
            seen.add(sid)
            concept = item.get("concept")
            if concept not in terms:
                raise ValueError("Missing next-step concept: " + repr(concept))
            resource_kind = "exercise" if kind == "story" else "story"
            target = item.get(resource_kind)
            valid_targets = exercises if resource_kind == "exercise" else all_story_ids
            if target not in valid_targets:
                raise ValueError("Missing next-step resource: " + repr(target))
            note = item.get("note", "")
            if not isinstance(note, str):
                raise ValueError("Invalid next-step note")
            # A withdrawn story must not appear as either source or destination.
            if kind == "story" and sid not in stories:
                continue
            links = [{"kind": "concept", "title": terms[concept]["title"],
                      "href": "/glossary/" + concept + "/"}]
            if resource_kind == "exercise":
                links.append({"kind": "exercise", "title": exercises[target]["title"],
                              "href": "/exercise/#" + target})
            elif target in stories:
                n, story = stories[target]
                links.append({"kind": "story", "title": story["title"], "href": f"/stories/#story-{n}"})
            output[kind][sid] = {"links": links, "note": note}
    return output


def load():
    import build_extras
    import build_glossary
    raw = json.loads((ROOT / "content/next-steps.json").read_text(encoding="utf-8"))
    all_stories = build_extras._load("stories.json", {"stories": []})["stories"]
    stories = {s["id"]: (n, s) for n, s in enumerate(build_extras.eligible_stories(), 1) if s.get("id")}
    exercises = {e["slug"]: e for e in build_extras._load("exercises.json", {"items": []})["items"]}
    terms = {t["slug"]: t for t in build_glossary.load(ROOT)["items"]}
    return resolve(raw, stories, exercises, terms, {s["id"] for s in all_stories if s.get("id")})


def render(esc, kind, sid, entry):
    if not entry:
        return ""
    heading = "next-" + kind + "-" + sid
    links = "".join(
        f'<li><a href="{esc(link["href"])}" target="_blank" rel="noopener">'
        f'<span class="next-kind">{LABELS[link["kind"]]}</span>'
        f'<span class="next-title">{esc(link["title"])}</span>'
        f'<span class="next-action">{ACTIONS[link["kind"]]}'
        '<span class="sr-only">، في لسان جديد</span></span></a></li>'
        for link in entry["links"])
    note = f'<p class="next-note">{esc(entry["note"])}</p>' if entry["note"] else ""
    return f'''<section class="next-steps" aria-labelledby="{esc(heading)}">
<h3 id="{esc(heading)}">لو حابب تكمّل</h3>
<p class="next-intro">موارد مرتبطة بالموضوع للقراءة والتأمل، مش تشخيص أو خطة علاج. اختار اللي يريحك؛ الروابط بتفتح في لسان جديد.</p>
<ul class="next-list">{links}</ul>{note}</section>'''


def attach(html):
    digest = hashlib.sha256((ROOT / "assets/next-steps.css").read_bytes()).hexdigest()[:12]
    return html.replace("</head>", f'<link rel="stylesheet" href="/assets/next-steps.css?v={digest}">\n</head>', 1)
