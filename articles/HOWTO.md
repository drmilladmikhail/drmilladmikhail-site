# How to add an article (knowledge platform, updated 2026-11-11)

> **Name rule (2026-11-05, his request):** his display name is **د. ميلاد ميخائيل** / Dr. Millad Mikhail — never write «د. ميلاد منير ميخائيل» in new text. Older forms stay ONLY as aliases (JSON-LD alternateName, the home-page FAQ, llms.txt) and in YouTube video titles.

## 0. Review rule — nothing health-related goes live without a person's review (master plan, 2026-11-11)
See also `content/REVIEW-POLICY.md` (applies to glossary terms, English translations and every other kind of health content: deliver as a pull request).
- A new article is first written as a **draft for review**, NOT pushed to `main`. Drafts never live in this repo (it is public):
  put the full draft in a Claude Doc (or the Project doc `claude/drafts/<slug>.md`) and send him the link.
- It is published only after **he** (or a specialist he names) has read it and said it can go out.
  Then add it to `articles/articles.json` with `"reviewed_on": "YYYY-MM-DD"` (the day of his approval) and push.
- `tools/build_articles.py` refuses (build fails, nothing deploys) any article dated on/after 2026-11-12 that has no
  `reviewed_on`, no `summary`, fewer than 2 `refs`, or no valid `category`. Never fill `reviewed_on` yourself without his approval.
- Never invent research, citations, statistics, qualifications, licences or experience. Every fact must come from a source you opened.

## 1. Categories (field `category`)
| slug | name |
| --- | --- |
| `anxiety-mental-health` | القلق والصحة النفسية |
| `relationships-family` | العلاقات والأسرة |
| `personality-behavior` | الشخصية والسلوك |
| `resilience-recovery` | المرونة النفسية والتعافي |
| `research-education` | الأبحاث والتعليم النفسي |

Each category has its own page `/articles/category/<slug>/` (built automatically; an empty one is `noindex` and hidden until its first article).

## 2. Files
1. Body: `articles/content/<slug>.html` (HTML fragment; slug = short English words, a-z 0-9 `-`).
   - Allowed markup: `<p>`, `<h2>`, `<h3>`, `<strong>`, `<em>`, `<ul>/<ol>/<li>`, `<table>` (simple),
     `<figure><img src="/assets/book/love-pNN.jpg" width="1200" height="800" alt="..." loading="lazy"></figure>`,
     `<div class="exercise"><p class="exercise-title">...</p><p>...</p></div>`,
     `<p class="safety"><strong>وقفة أمان:</strong> ...</p>`
   - Don't add the title, «باختصار», the contents list, the references, the book box, the author box or the date — the template adds them.
   - If the body has no «وقفة أمان», the template adds a standard educational/medical disclaimer.
2. Entry in `articles/articles.json`:
   ```json
   {"slug": "…", "title": "…", "description": "…", "date": "YYYY-MM-DD", "updated": "YYYY-MM-DD (only for a real revision)",
    "category": "anxiety-mental-health", "summary": "2–3 sentences: the direct answer",
    "refs": [{"title": "…", "url": "https://…"}, {"title": "…", "url": "https://…"}],
    "reviewed_on": "YYYY-MM-DD", "minutes": 6,
    "image": "love-p16 (optional)", "image_alt": "…", "chapter": "من الفصل التاني (only for book-based articles)"}
   ```
   - No `image` → the category's picture is used for the card and the share card, and the article opens with «باختصار» (no hero).
   - `updated` only when the content really changed (it is shown as «آخر تحديث» and used in the sitemap).
3. Run `python3 tools/build_articles.py` — it validates, rebuilds every article, `/articles/`, the five category pages, the home
   "latest" block, `sitemap.xml`, `llms.txt`, the share card `assets/og/<slug>.jpg` (open it and check the Arabic), then `add_analytics.py`.
4. Commit and push to `main` (GitHub Pages deploys; IndexNow pings Bing automatically).

## 3. Editorial quality checklist (every article)
- Title = the reader's real question, the way people type it (2–3 web searches first). 45–65 characters.
- `summary` = the direct answer in 2–3 sentences (shown first as «باختصار» and as `Article.abstract`).
- `description` 130–155 characters with the main phrase.
- Original Egyptian Arabic, 600–1200 words (the length the answer needs, no padding), clear `<h2>` questions, a practical Egyptian example, steps the reader can take.
- ≥ 2 reliable sources you actually opened (WHO, NIMH, NHS, APA, Mayo Clinic, Cleveland Clinic, peer-reviewed papers with DOI).
- 2–3 internal links (related article, test, glossary term or tool) — only where they really fit.
- «امتى تكلم متخصص» + safety note; crisis topics follow safe-messaging (no methods; Egypt 105/122/123, US 988/911).
- No diagnosis, no medication names or doses, no therapy offers to people in the US.
- Don't duplicate: check `articles/articles.json`, `/questions/`, `/glossary/`, `/stories/` and the blog log first.

## 4. Titles and descriptions people actually search for (SEO)
- Write the title the way people type the question into Google: «إزاي أفرّق بين الحزن والاكتئاب؟», «نوبة الهلع أعمل إيه وقتها؟».
- Keep the main phrase near the start; use it once in the first paragraph and in one `<h2>`; never stuff keywords.

Book illustrations (book-based articles only): love-p09, p10, p11, p12 (ch.1), p16, p17, p18, p19 (ch.2),
p23, p27 (ch.3), p30, p35 (ch.4), p37, p42 (ch.5), p46, p50, p53 (ch.6), p59 (ch.7), p64 (conclusion).

## Visitor data → what to make next
Read `content/PRIORITIES.md` (rewritten every 15 days from Cloudflare Web Analytics) and the 90-day editorial calendar
(Project doc `claude/editorial-calendar.md`) before choosing a topic.
