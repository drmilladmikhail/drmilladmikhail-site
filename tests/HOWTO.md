# How to add a weekly self-test (for the scheduled run)

Rules (non-negotiable):
- Only add **published, validated scales whose authors allow free use** (public domain or "free for non-commercial / educational use"). Before adding, open the scale's official source (author/lab page or the original paper) and confirm (1) the exact items, (2) the response options, (3) reverse-keyed items, (4) scoring and any published cut-offs, (5) the permission statement. If any of these cannot be confirmed from a reliable source, skip that scale and take the next one in ROADMAP.md.
- Never invent items, cut-offs or norms. If the scale has no official cut-offs, show the score and its meaning in plain words without labels like "شديد".
- Arabic: simple, close to the original meaning (not slang that changes meaning). The page already states that the Arabic is a simplified translation, not the officially validated Arabic version.
- Sensitive topics (depression, anxiety, trauma, substance use, self-harm): set `"safety": True` and mark the highest band(s) with a 5th element `True` so the crisis box (Egypt 105 / US 988) appears. Never include items asking directly about suicide or self-harm.
- One test per run. Do not change or remove existing tests.

Steps:
1. Add a new dict to `TESTS` in `tools/build_tests.py` (copy the structure of an existing one: slug, title, short, description, icon, minutes, kind, intro, options, items, max, bands, source (APA citation + permission note), note, related, safety). Reverse-keyed items for `kind: "sum"` go in `"reverse": [item numbers]`.
2. Supported kinds in `assets/quiz.js`: `"sum"` (total score, optional `"multiplier"`, bands) and `"ecr"` (attachment). If a scale needs subscales or mean scores, add a new kind to quiz.js carefully without breaking the existing two, and add any new icon to `ICONS`.
3. Run `python3 tools/build_tests.py` then `python3 tools/build_articles.py` (refreshes sitemap.xml).
4. Test in a real browser with Playwright (chromium is pre-installed): serve the repo with `python3 -m http.server`, open the new test, answer all-first and all-last options, and check that the score, band and alert are correct by hand calculation. Also re-check one existing test still works. No horizontal scroll at 390px.
5. Commit ("Add test: <slug>" + trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>") and push to main.
6. Mark the scale as done in `tests/ROADMAP.md` (date + slug) in the same commit.

## Visitor data → what to make next (added 2026-11-05)
Before choosing a topic (article, English translation, glossary term, worksheet, or self-test), read `content/PRIORITIES.md`. It is rewritten every 15 days from Cloudflare Web Analytics by the scheduled task «تقرير زوار الموقع». If it has data, prefer the topics it ranks higher — but only within this task's own rules and sources (articles from the book, tests only from scales allowed here and in ROADMAP.md). If it says "No data yet", keep the normal order.
