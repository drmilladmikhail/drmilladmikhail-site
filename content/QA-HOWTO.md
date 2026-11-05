# How to add questions and challenges (weekly scheduled run)

Pages: `/questions/` («أسئلة محرجة… وإجابات علمية») and `/challenges/` («تحديات قصيرة»).
Both are built by `tools/build_pages.py` from `content/questions.json` and `content/challenges.json`.
Run `python3 tools/build_articles.py` (it runs build_pages, the sitemap and analytics/CSP).

## Questions — `content/questions.json`
`sections`: `{"slug", "name"}` (+ `"adult": true, "note"` for 18+). `items`: one object per question:
```
{"id": "short-english-slug", "section": "feelings|relationships|sexual|<new>",
 "q": "السؤال زي ما الناس بتقوله بالظبط، بالعامية",
 "a": ["فقرة 1", "فقرة 2", "فقرة 3 (خطوات عملية)"],
 "when": "امتى يكلّم متخصص — جملة واحدة واضحة",
 "safety": true,              // only when there is risk (self-harm, violence, abuse)
 "link": ["/articles/<slug>/", "عنوان المقال"],   // optional, only to a page that exists
 "sources": ["WHO ...", "NHS ..."],               // not shown; for checking
 "added": "YYYY-MM-DD"}
```
Rules:
- The question is the kind people are too shy to ask in public. Phrase it the way people say it / search it
  (run 2–3 web searches to see real phrasing). Never repeat or near-repeat an existing question.
- Answer: warm simple Egyptian Arabic, 2–4 short paragraphs, 90–180 words, no judgement, no shaming.
  Start by normalising ("ده شائع…") when that is true, then the science, then 2–3 practical steps.
- Only mainstream, well-established information. Before writing, check it on reliable sources
  (WHO, NHS, Mayo Clinic, APA, NIMH, Cleveland Clinic, peer-reviewed reviews) and list them in `sources`.
  No invented numbers. No diagnosis. No medication names or doses. No offering sessions/therapy in the US.
- Sexual section (18+, adults only): educational and clinical wording only — no explicit or arousing
  description, no techniques, nothing about minors' sexuality, nothing about sexual history/fantasies of
  real people. Typical topics: myths, anxiety, performance worries, desire differences, pain, guilt,
  talking with a spouse, when to see a urologist/gynaecologist/sex therapist.
  Questions with a religious side: say that for the religious ruling «اسأل رجل دين بتثق فيه» and answer
  only the medical/psychological side.
- Suicide / self-harm / abuse: follow safe-messaging (no methods, no details, hope + reaching out),
  set `"safety": true`, and include Egypt 105 and US 988 (and 122 / 911 for danger).
- When a section has 8+ questions you may add a new non-adult section (e.g. «الأهل والبيت»،
  «الجسم والنوم»، «الشغل والدراسة»، «الصحاب والوحدة») — slug in English, add it to `sections`.

## Challenges — `content/challenges.json`
`{"id", "title" («N أيام …»), "days", "why" (one sentence, research-based, no invented numbers),
"tasks": [one task per day, ≤ 10 minutes, concrete, safe for anyone]}`. 3–7 days. Never change the
`id` or the order of tasks of an existing challenge (visitors' saved progress uses `id-N`).
No fasting/diet/exercise targets, no cold exposure, nothing risky.

## Check before pushing
- `python3 -m json.tool` both files; build; open `/questions/` and `/challenges/` with Playwright
  (bypass_csp=True only for injecting axe): no console/CSP errors, axe 0 violations, the 18+ gate still
  closed by default, new items visible, checkboxes still save.
