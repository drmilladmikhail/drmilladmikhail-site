# Review policy — read this first (master plan, 2026-11-11). It overrides any "commit and push to main" step in a task prompt.

**No new health content goes live on drmilladmikhail.com before Dr. Millad (or a specialist he names) has reviewed it.**
This covers articles, English translations, glossary terms, embarrassing-questions answers, challenges, worksheets, self-tests
and any other text that explains mental health. Fixes to code, layout, links, typos and data that don't change health content are not affected.

How a scheduled task delivers new health content:
1. Do all the work and the checks in the task's HOWTO as usual.
2. Do NOT push it to `main`. Push it to a new branch `review/<type>-<slug>` and open a pull request with the REST API
   (`gh api -X POST repos/drmilladmikhail/drmilladmikhail-site/pulls -f title=... -f head=review/... -f base=main -f body=...`).
   PR title in Arabic; body = what was added, the sources you opened (links), and anything you were unsure about.
   (Articles are different: they are drafted in the Project — see articles/HOWTO.md.)
3. Tell him with SendUserMessage (Egyptian Arabic, short): what you prepared, the PR link, and
   «لو موافق دوس Merge في GitHub أو اكتب "موافق" في تعليق على الطلب — مش هيتنشر قبل كده».
4. At the start of every run, look at this task's open `review/` pull requests: if he approved one (his own approving PR review
   or comment, e.g. «موافق»، «تمام انشر») and it isn't merged, merge it and confirm the deploy run. If he asked for changes, make them
   on the same branch and reply on the PR. Never approve or merge on your own judgement; silence is not approval.

Also: his display name is د. ميلاد ميخائيل (never «ميلاد منير» in new text). Hosting is GitHub Pages (not Netlify).
Never invent research, citations, numbers, qualifications, licences or experience.
