#!/usr/bin/env python3
"""Pull published therapist profiles from Supabase into content/therapists/*.json,
refresh each share image (therapists/<slug>/og.jpg) and rebuild the static pages.

Runs hourly in .github/workflows/therapists-sync.yml. Therapists edit their data
from /therapists/dashboard/; the live page already shows it through profile.js,
and this sync keeps the static fallback and the WhatsApp/Facebook preview current.
Only public columns are read, with the public (publishable) key.
"""
import hashlib
import json
import os
import sys
import tempfile
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import therapists_og  # noqa: E402

URL = "https://putqeswsycwyxxrdcmyh.supabase.co"
KEY = "sb_publishable_Yg7WovbSlye0T9CV8PHbYw_zBuhFR11"
DATA = os.path.join(ROOT, "content", "therapists")
OUT = os.path.join(ROOT, "therapists")
COLS = ("slug,name,title,specialties,bio,experience,languages,credentials,courses,articles,videos,"
        "sessions,session_mode,schedule,cancel_policy,whatsapp,photo_path")


def get(path):
    req = urllib.request.Request(URL + path, headers={"apikey": KEY, "Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def to_json(row, old):
    """Map a database row onto the builder's JSON shape, keeping local-only flags."""
    bio = [p.strip() for p in (row.get("bio") or "").split("\n\n") if p.strip()]
    return {
        "slug": row["slug"],
        "name": row.get("name") or "",
        "title": row.get("title") or "معالج نفسي",
        "photo": "",
        "languages": row.get("languages") or [],
        "experience": row.get("experience") or "",
        "bio": bio,
        "credentials": row.get("credentials") or [],
        "courses": row.get("courses") or [],
        "articles": [{"title": a.get("title", ""), "place": a.get("place", ""), "url": a.get("url", "")}
                     for a in (row.get("articles") or []) if isinstance(a, dict)],
        "videos": row.get("videos") or [],
        "sessions": row.get("sessions") or [],
        "session_mode": row.get("session_mode") or "",
        "schedule": row.get("schedule") or "",
        "cancel_policy": row.get("cancel_policy") or "",
        "contact_whatsapp": row.get("whatsapp") or "",
        "specialties": row.get("specialties") or [],
        "photo_path": row.get("photo_path") or "",
        "preview": old.get("preview", True),
        "og": old.get("og", ""),
    }


def main():
    rows = json.loads(get("/rest/v1/therapists?published=eq.true&select=" + COLS))
    changed = []
    for row in rows:
        slug = row["slug"]
        path = os.path.join(DATA, slug + ".json")
        old = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                old = json.load(f)
        new = to_json(row, old)

        # Share image: rebuild only when what it shows changed.
        sig_src = json.dumps([new["name"], new["title"], new["specialties"][:4], new["photo_path"]], ensure_ascii=False)
        sig = hashlib.sha1(sig_src.encode("utf-8")).hexdigest()[:12]
        og_path = os.path.join(OUT, slug, "og.jpg")
        if new["og"] != sig or not os.path.exists(og_path):
            photo = None
            if new["photo_path"]:
                try:
                    blob = get("/storage/v1/object/public/therapist-photos/" + urllib.parse.quote(new["photo_path"]))
                    fd, photo = tempfile.mkstemp(suffix=".img")
                    with os.fdopen(fd, "wb") as f:
                        f.write(blob)
                except Exception as e:  # keep going with the initial letter
                    print(f"{slug}: photo download failed: {e}")
                    photo = None
            therapists_og.make(new, og_path, photo)
            if photo:
                os.remove(photo)
            new["og"] = sig

        if new != old:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(new, f, ensure_ascii=False, indent=2)
                f.write("\n")
            changed.append(slug)
    print(f"therapists sync: {len(rows)} published, changed: {', '.join(changed) or 'none'}")


if __name__ == "__main__":
    main()
