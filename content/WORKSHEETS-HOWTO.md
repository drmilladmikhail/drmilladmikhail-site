# How to add a worksheet (monthly scheduled run, and by hand)

Library page: `/worksheets/` («مكتبة أوراق التمرين»). Everything comes from `content/worksheets.json`.

1. Add one object to `items` (keep the others untouched):
```
{"slug": "english-words-a-z", "category": "love|self|<new category slug>",
 "title": "عنوان قصير", "accent": "آخر كلمتين من العنوان (بيتلوّنوا أخضر)",
 "desc": "جملة واحدة للكارت (~120 حرف) فيها الكلام اللي الناس بتدوّر بيه",
 "intro": "2–3 سطور دافية بالعامية: التمرين ده ليه ومحتاج قد إيه",
 "related": ["/tests/<slug>/" or "/articles/<slug>/", "اسم الصفحة"],   // only pages that exist
 "added": "YYYY-MM-DD",
 "sections": [ ... 5–7 sections ... ],
 "extra_note": "optional safety/when-to-get-help sentence"}
```
   Section fields (combine as needed, rendered in this order):
   `t` (title, required) · `words` [chips] · `examples` [shaded example lines] · `checks` [tick-box list] ·
   `hint` (grey help line) · `circles` [3 ring labels, inner→outer] ·
   `table` {"cols": [...], "rows": N, "labels": [...optional first-column labels]} ·
   `lines` (blank writing lines) · `hint2` + `lines2` · `box: true` (dashed amber box — use for the last
   "خطوة صغيرة" section) · `break: "force"` (page break — normally not needed).
2. Content rules: ORIGINAL exercises (don't copy the book's quizzes/tables), warm simple Egyptian Arabic,
   one idea per sheet, practical, no diagnosis, no medical advice, no offering therapy in the US.
   The footer (book + Amazon links + byline) and the general safety note (105 / 988) are added automatically.
   Topics touching abuse/self-harm need an `extra_note` with what to do and the danger numbers (122 / 911).
3. Build: `python3 tools/build_worksheets.py` (PDF + preview, only for changed entries), then
   `python3 tools/build_articles.py` (library page, sitemap, start page, CSP/analytics).
4. Look at it: `pdftoppm -r 70 -png worksheets/<slug>.pdf /tmp/x` and open every page image —
   Arabic letters joined, RTL, nothing cut off, ideally exactly 2 pages (shorten or add lines to fit).
5. Commit `content/worksheets.json`, `worksheets/<slug>.pdf`, `worksheets/<slug>.webp`,
   `worksheets/manifest.json`, `worksheets/index.html`, `sitemap.xml`, `start/index.html`.

Note: `gifts/` holds the e-mail gift PDF (kept out of search). The library is public and free with no sign-up.
