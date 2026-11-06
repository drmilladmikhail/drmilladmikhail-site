# How to add an article (for the twice-weekly scheduled run)

> **Name rule (2026-11-05, his request):** his display name is **د. ميلاد ميخائيل** / Dr. Millad Mikhail — never write «د. ميلاد منير ميخائيل» in new text. Older forms (د. ميلاد منير، د. ميلاد منير ميخائيل) stay ONLY as aliases (JSON-LD alternateName, the home-page FAQ, llms.txt) and in YouTube video titles.


1. Read `articles/articles.json` to see what is already published. Never repeat a topic.
2. Write the body as an HTML fragment in `articles/content/<slug>.html`
   - slug: short English words, a-z 0-9 and `-` only (e.g. `four-attachment-styles`)
   - Egyptian Arabic, 700–1000 words, one idea from the book «ليه بنحب اللي بيوجعنا؟»
   - Allowed markup: `<p>`, `<h2>`, `<strong>`, `<em>`, `<ul>/<ol>/<li>`,
     `<figure><img src="/assets/book/love-pNN.jpg" width="1200" height="800" alt="..." loading="lazy"></figure>`,
     `<div class="exercise"><p class="exercise-title">...</p><p>...</p></div>`,
     `<p class="safety"><strong>وقفة أمان:</strong> ...</p>`
   - Do NOT add the title, the book box, the author box or the date — the template adds them.
   - 1–2 `<figure>` images inside the body (different from the hero image).
3. Append an entry to `articles/articles.json`:
   `{"slug", "title", "description" (one sentence, ~150 chars, with the words people search for), "date" (YYYY-MM-DD), "image" (hero, e.g. "love-p16"), "image_alt", "chapter" (e.g. "من الفصل التاني"), "minutes"}`
4. Run `python3 tools/build_articles.py` (it validates and rebuilds article pages, `/articles/`, the home-page "latest" block and `sitemap.xml`;
   it also runs `tools/build_images.py`, which makes the WebP versions of book images and the 1200x630 share card
   `assets/og/<slug>.jpg` with the article title — open that card and check the Arabic text looks right).
   Commit the new files in `assets/og/` and `assets/book/*.webp` too.
5. Commit and push to `main`; Netlify deploys automatically. A GitHub Action (`.github/workflows/indexnow.yml`)
   then pings IndexNow (Bing etc.) with the sitemap URLs — nothing to do by hand.

## Titles and descriptions people actually search for (SEO)
- Write the title the way people type the question into Google, in Egyptian Arabic or simple Arabic:
  e.g. «إزاي أنسى حد بحبه وهو أذاني؟»، «ليه برجع لحد عارف إنه مش مناسب ليا؟»، «علامات إن العلاقة مؤذية».
  Before choosing, run 2–3 web searches on the topic to see the phrasing people and other sites use; prefer
  the common phrasing over a clever one. Keep the main phrase near the start; 45–65 characters is ideal.
- `description`: one sentence (130–155 characters) that repeats the main phrase naturally and says what the reader gets.
- Use the main phrase once in the first paragraph and in one `<h2>`; never stuff keywords.
- Link to one related article (if any exists) and, when the topic fits, to a test in `/tests/` inside the body.

Book illustrations available (book page numbers): love-p09, p10, p11, p12 (ch.1), p16, p17, p18, p19 (ch.2),
p23, p27 (ch.3), p30, p35 (ch.4), p37, p42 (ch.5), p46, p50, p53 (ch.6), p59 (ch.7), p64 (conclusion).
Look at the image before choosing it if you are unsure what it shows.

## Visitor data → what to make next (added 2026-11-05)
Before choosing a topic (article, English translation, glossary term, worksheet, or self-test), read `content/PRIORITIES.md`. It is rewritten every 15 days from Cloudflare Web Analytics by the scheduled task «تقرير زوار الموقع». If it has data, prefer the topics it ranks higher — but only within this task's own rules and sources (articles from the book, tests only from scales allowed here and in ROADMAP.md). If it says "No data yet", keep the normal order.
