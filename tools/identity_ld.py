#!/usr/bin/env python3
"""One identity for the whole site (2026-11-11, phase 2).

Every Person in the site's structured data is the same person, with the fixed id
https://drmilladmikhail.com/#person. This module makes sure all copies of that Person
agree with each other, so search engines and AI search merge them into one entity:

  * url        -> the profile page /about/ (Google's advice for author.url)
  * sameAs     -> the same verified list of official profiles everywhere
  * full descriptions also get the same alternateName list (his old names),
    givenName/familyName, honorificPrefix, identifier (ORCID) and knowsAbout.

Only facts already published on the site are used. Called from add_analytics.py
(and build_research.py) on every page.
"""
import json
import re

SITE = "https://drmilladmikhail.com"
PERSON_ID = SITE + "/#person"
PERSON_URL = SITE + "/about/"

SAME_AS = [
    "https://www.youtube.com/@DrMilladMikhail",
    "https://www.youtube.com/channel/UCTR2Y82KQ3743gUk6GgsIgA",
    "https://www.amazon.com/stores/author/B0HQ931MJP",
    "https://www.linkedin.com/in/dr-millad-mikhail-a57b0b215",
    "https://blog.drmilladmikhail.com/",
    "https://orcid.org/0009-0002-9254-367X",
    "https://www.credly.com/badges/5a6796c0-5e1a-4ad5-b1af-fb64254e81cf/public_url",
]
ALT_NAMES = [
    "د. ميلاد ميخائيل", "دكتور ميلاد ميخائيل", "Millad Mikhail", "Milad Mikhail", "DR. Millad Mikhail",
    "Millad Mounir Mikhail", "Milad Mounir Mikhail", "Dr. Milad Mounir", "Milad Mounir",
    "د. ميلاد منير ميخائيل", "ميلاد منير ميخائيل", "دكتور ميلاد منير", "د. ميلاد منير", "ميلاد منير",
]
COMMON = {
    "givenName": "Millad",
    "familyName": "Mikhail",
    "honorificPrefix": "Dr.",
    "identifier": {"@type": "PropertyValue", "propertyID": "ORCID", "value": "0009-0002-9254-367X"},
    "knowsAbout": ["Mental health", "Logotherapy", "Logo counselling", "Existential anxiety",
                   "Psychological immunity", "Attachment", "Relationships", "Family counselling"],
}
SHORT_KEYS = {"@id", "@type", "name", "alternateName", "url"}
LD_RE = re.compile(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)', re.S)


def _is_person(o):
    t = o.get("@type")
    return o.get("@id") == PERSON_ID and (t == "Person" or (isinstance(t, list) and "Person" in t))


def _merge_alt(cur):
    cur = [cur] if isinstance(cur, str) else list(cur or [])
    out = []
    for n in cur + ALT_NAMES:
        if n not in out:
            out.append(n)
    return out


def _fix(o):
    if isinstance(o, list):
        return [_fix(x) for x in o]
    if not isinstance(o, dict):
        return o
    o = {k: _fix(v) for k, v in o.items()}
    if _is_person(o):
        o["url"] = PERSON_URL
        if set(o) - SHORT_KEYS:  # a full description, not just a reference
            o["sameAs"] = list(SAME_AS)
            o["alternateName"] = _merge_alt(o.get("alternateName"))
            for k, v in COMMON.items():
                o.setdefault(k, v)
    return o


def apply_page(t):
    def repl(m):
        raw = m.group(2)
        if PERSON_ID not in raw:
            return m.group(0)
        try:
            data = json.loads(raw)
        except ValueError:
            return m.group(0)
        new = _fix(data)
        if new == data:
            return m.group(0)
        body = json.dumps(new, ensure_ascii=False, indent=2).replace("</", "<\\/")
        return m.group(1) + "\n" + body + "\n" + m.group(3)
    return LD_RE.sub(repl, t)


# ---- Links between the profile pages, books and articles ("who wrote this?" in one click) ----
HUB_PAGES = {"about": "/about/", "about/qualifications": "/about/qualifications/",
             "about/publications": "/about/publications/", "book": "/book/", "battery": "/book/",
             "articles": "/articles/", "family": "/family/"}
HUB_LINKS = [("/about/", "النبذة والسيرة المهنية"), ("/about/qualifications/", "المؤهلات العلمية"),
             ("/about/publications/", "الرسائل والأبحاث"), ("/book/", "الكتب"),
             ("/articles/", "المقالات"), ("/family/", "التوعية الأسرية والزوجية")]
HUB_RE = re.compile(r'<nav class="profile-hub".*?</nav>\n?', re.S)


def hub(current):
    cur = ' aria-current="page"'
    items = "".join(f'<li><a href="{u}"{cur if u == current else ""}>{label}</a></li>' for u, label in HUB_LINKS)
    return ('<nav class="profile-hub" aria-label="تعرّف على د. ميلاد ميخائيل"><div class="wrap">'
            '<p class="profile-hub-title">تعرّف على د. ميلاد ميخائيل · استشاري العلاج النفسي والأسري</p>'
            f'<ul>{items}</ul></div></nav>\n')


def apply_hub(t, rel):
    """rel = the page folder ("about", "book", …). Adds the same profile navigation at the end of <main>."""
    cur = HUB_PAGES.get(rel.strip("/"))
    if cur is None or "</main>" not in t:
        return t
    t = HUB_RE.sub("", t)
    i = t.rfind("</main>")
    return t[:i] + hub(cur) + t[i:]
