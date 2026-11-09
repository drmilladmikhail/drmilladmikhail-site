# Daily Egyptian Arabic glossary additions

The visible feature name is `القاموس النفسي`. Definition headings read `المعنى`.
Do not add `بالمصري` to any glossary UI label, title, metadata, sharing text, or
homepage/start-page link. Keep the simple Egyptian Arabic writing and everyday
examples, without labeling the dialect. Preserve the calm green, blue, sand and
lavender category palette and its accessible dark-mode variants.

The site owner authorized automatically publishing two new psychology glossary
terms each day, preserving the existing colorful cards, click-to-open definitions,
Egyptian Arabic everyday examples, and scientific references. The daily schedule
is managed by Perplexity Computer, not by a second GitHub cron job.

## Content and daily deduplication

- Read both `content/glossary.json` and `content/glossary-more.json` before choosing
  terms. Append new records only to the latter file's `items` array.
- Compare existing slugs, Arabic and English titles, aliases, and meanings. Do not
  pad the collection with synonyms or duplicate concepts.
- Set `added` on each new record to the current date in `America/New_York`, in
  `YYYY-MM-DD` format. This records the publication batch, not a research date.
- Update the top-level `updated` date in `content/glossary.json` to the same local
  date so standalone pages show the actual latest editorial update. Preserve all
  existing records.
- Count today's records across both source files before editing. If there are
  already two or more, verify the existing deployment and do not add more.
  If there is one, add only one more. Retries must not duplicate a day's batch.
- Use the existing schema: `slug`, `title`, `english`, `category`, `aliases`,
  `summary`, `definition`, `example`, `not`, `comparison`, `question`, `related`,
  `source: {name, url}`, and `added`. `help` and `reading` are optional.
- Use an existing category and valid related slugs. Match the Egyptian Arabic
  style, with a clearly fictional everyday example containing `تخيّل`.
- Search and fetch an authoritative source for every new term, such as APA, NHS,
  WHO, or a recognized academic/clinical institution. Cite its actual public HTTPS
  URL. If a source cannot be verified, choose a different term.
- Explain misconceptions accurately. Do not diagnose readers, invent clinical
  thresholds, promise treatment, or claim a human scientific review. Optional
  clinical guidance needs supporting evidence; otherwise use the builder's
  explicitly labeled general support guidance.
- Never publish lower-quality or unsupported content just to meet a daily quota.
  Report a blocker instead.

## Build, publish, and verify

1. Use the latest `main`; never overwrite unrelated work or force-push.
2. Run:

   ```sh
   python3 -m unittest discover -s tools -p test_glossary.py -v
   python3 tools/build_pages.py
   python3 tools/growth_package.py
   python3 tools/build_articles.py
   python3 tools/home_clarity.py
   python3 tools/build_research.py
   git diff --check
   ```

3. Inspect the diff, including the glossary index, new standalone pages, and
   sitemap. Check mobile/desktop cards, modal examples, sources, search, category
   filters, and direct links; ensure existing site flows still work.
4. Check `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT` before
   committing. Preserve configured identities; follow authenticated CLI
   instructions if an identity is missing.
5. Commit only intended files and push to `main`. On a concurrent update, preserve
   upstream changes and re-check today's records and uniqueness before retrying.
6. Wait for `Build and publish verified site` and `Site checks` to succeed. Check
   the live homepage `site-revision` against the published commit, then verify the
   glossary count, both new cards, their Egyptian examples, sources, and standalone
   pages at `https://drmilladmikhail.com/glossary/`.
7. Report the two titles, their live links, the new total, and publication status
   to the source conversation. Never report success before live verification.

The newsletter/email sending setup remains postponed. This task does not
authorize subscriber messages, new third-party services, or unrelated site changes.
