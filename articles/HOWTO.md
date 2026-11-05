# How to add an article (for the twice-weekly scheduled run)

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
4. Run `python3 tools/build_articles.py` (it validates and rebuilds article pages, `/articles/`, the home-page "latest" block and `sitemap.xml`).
5. Commit and push to `main`; Netlify deploys automatically.

Book illustrations available (book page numbers): love-p09, p10, p11, p12 (ch.1), p16, p17, p18, p19 (ch.2),
p23, p27 (ch.3), p30, p35 (ch.4), p37, p42 (ch.5), p46, p50, p53 (ch.6), p59 (ch.7), p64 (conclusion).
Look at the image before choosing it if you are unsure what it shows.
