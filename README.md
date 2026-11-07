
> **Sessions rule (2026-11-05, his request):** Arabic pages say «جلسات نفسية أونلاين لأهلنا في مصر والوطن العربي» (not «إرشاد نفسي»). NEVER mention sessions on English pages (/en/, English translations).

> **Name rule (2026-11-05, his request):** his display name is **د. ميلاد ميخائيل** / Dr. Millad Mikhail — never write «د. ميلاد منير ميخائيل» in new text. Older forms (د. ميلاد منير، د. ميلاد منير ميخائيل) stay ONLY as aliases (JSON-LD alternateName, the home-page FAQ, llms.txt) and in YouTube video titles.

# drmilladmikhail-site
## 2026-11-07 additions
- **Header/menus:** ONE source — `tools/site_header.py` (logo, «د. ميلاد ميخائيل | استشاري العلاج النفسي وتطوير الذات», «الصفحة الرئيسية» first, desktop drop-downs, grouped mobile menu). `tools/add_analytics.py` runs it after every build (and the Site checks Action after every push), so every Arabic page gets the same header. Edit links only there.
- **Tests:** 11 scales; new kind `multi` (sub-scales) in `tools/build_tests.py`: Mini-IPIP, MAAS, SCS-SF, CBI, MLQ. Every test shows its reference (📚). Validated scales keep their original item count — never add or remove items.
- **Home:** hero = name + title + slogan; «تأمل اليوم» (`assets/daily.js`, add lines to the list), «تمرين الأسبوع» card, 4-door site guide; credentials/research are folded.
- **Articles:** «استمع لهذا المقال» (`assets/listen.js`, the device's Arabic voice) + discussion question (optional `"discuss"` field in articles.json) + comments.
- **Comments:** Cusdis (moderated, nickname, no ads). OFF until `content/comments.json` has `app_id`; then rebuild — CSP is opened for cusdis.com automatically.
- **New pages** (`tools/build_extras.py`, called by build_pages.py): `/exercise/` (content/exercises.json, one per week), `/stories/` (content/stories.json — REAL consented stories only, never invent), `/shelf/` (content/shelf.json; "رأيي فيه" texts are for Dr. Millad to review).
