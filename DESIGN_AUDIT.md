# DESIGN_AUDIT.md — drmilladmikhail.com

**Prepared:** 2026-11-08  
**Repository:** `drmilladmikhail/drmilladmikhail-site`  
**Branch reviewed:** `main`  
**Architecture:** Static multi-page site (HTML, CSS, vanilla JavaScript), published with GitHub Pages and a custom domain.  
**Review scope:** Repository/source inspection, route inventory, sitemap, shared CSS tokens, navigation links, selected page markup and scripts. This is a source-based audit, not a fully instrumented browser/device QA run.

> **Evidence and limitations.** The repository was inspected at the current `main` tree. I could not launch an authenticated browser or run a real device screenshot capture in this environment. Therefore no screenshot is fabricated or represented as a real capture. The screenshot section supplies the exact capture matrix and annotation brief. Visual/mobile findings are source-level risks and recommendations unless explicitly identified as confirmed by source code.

---

## 1. Executive overview

The site has grown beyond a simple personal homepage into a multi-section Arabic-first mental-health education and self-guided learning platform, with an English homepage, articles, tests, exercises, challenges, worksheets, videos, and an early-stage professional directory.

### Strengths observed
- Clear static architecture with no unnecessary framework dependency.
- A substantial content library and dedicated routes for key topics.
- Shared global stylesheet and navigation script.
- Sitemap, robots.txt, canonical/metadata infrastructure, Open Graph images, and an LLM-facing `llms.txt`.
- Dedicated privacy and terms pages.
- Self-guided challenges and personal progress stored locally in the browser rather than requiring accounts.
- Test catalog distinguishes self-exploration from diagnosis in its copy.
- Accessibility foundations include skip links, semantic headings, focus styles, and reduced-motion treatment in shared components.

### Highest-priority risks
1. The global navigation is extensive and repeats many destinations across desktop/mobile or multiple dropdowns; simplify the information architecture.
2. The homepage tries to serve several audiences and many content types; strengthen the primary journey and progressive disclosure.
3. Some important sections are still “coming soon” or empty-state (professional directory/platform); make the state and next action unmistakable.
4. Health-related tools need very clear non-diagnostic boundaries, crisis escalation, privacy expectations, and source transparency.
5. Mobile needs real-device testing for sticky/floating controls, long Arabic labels, menu dropdowns, tables, quiz controls, and safe-area overlap.
6. Search indexing must be verified in Search Console; source files alone cannot confirm Google's accepted property, sitemap processing, or URL indexing.

---

## 2. Screenshot export and capture matrix

### Capture status
**Not captured in this export.** A real browser screenshot engine/session was not available to this review. The repository includes Open Graph preview images under `assets/og/`, but those are social preview artwork, not screenshots of the rendered website. Do not pass them to another AI as page screenshots.

### Required desktop and mobile captures

Capture at minimum:
- Desktop: 1440 × 1000 CSS px (or 1365 × 900).
- Mobile: 390 × 844 CSS px (iPhone-class viewport); repeat at 375 × 812 and 430 × 932 for overflow checks.
- Browser zoom: 100%; record browser and capture date.
- Capture the initial viewport and one full-page capture for long pages.
- Capture menu-open state on homepage and one interior page.
- Capture interactive states for a quiz/test (intro, question, result/disclaimer) where safe and possible.

| Page | Desktop capture | Mobile capture | Suggested label |
|---|---|---|---|
| Home Arabic | Pending | Pending | H01 |
| Home English | Pending | Pending | H02 |
| Start / guide | Pending | Pending | P01 |
| Articles index | Pending | Pending | P02 |
| Article: attachment styles | Pending | Pending | P03 |
| Article: repeated relationship pattern | Pending | Pending | P04 |
| Tests index | Pending | Pending | P05 |
| Each of 11 test pages | Pending | Pending | T01–T11 |
| Videos | Pending | Pending | P06 |
| Exercises | Pending | Pending | P07 |
| Challenges | Pending | Pending | P08 |
| My Space | Pending | Pending | P09 |
| Feelings wheel | Pending | Pending | P10 |
| Relationship check | Pending | Pending | P11 |
| Questions | Pending | Pending | P12 |
| Stories | Pending | Pending | P13 |
| Worksheets | Pending | Pending | P14 |
| Book | Pending | Pending | P15 |
| Shelf | Pending | Pending | P16 |
| Sessions | Pending | Pending | P17 |
| Ask anonymously | Pending | Pending | P18 |
| Contact | Pending | Pending | P19 |
| Platform | Pending | Pending | P20 |
| Learning paths | Pending | Pending | P21 |
| Experts directory | Pending | Pending | P22 |
| Join the directory | Pending | Pending | P23 |
| Help now | Pending | Pending | P24 |
| Privacy | Pending | Pending | P25 |
| Terms | Pending | Pending | P26 |
| Porn-addiction resource | Pending | Pending | P27 |
| Battery / resilience tool | Pending | Pending | P28 |
| Myth or Fact | Pending | Pending | P29 |
| 404 page | Pending | Pending | P30 |

### Screenshot annotation legend for the next AI
Use these callouts on the real captures:
- **RED — REMOVE:** redundant navigation items, duplicate CTAs, nonessential decorative elements, repeated sections.
- **AMBER — MOVE:** content that belongs lower in the page, secondary actions, long credentials, legal/disclaimer copy that can be progressively disclosed without hiding essential warnings.
- **BLUE — REDESIGN:** hierarchy, spacing, card layout, contrast, button priority, typography, mobile menu and overlapping fixed controls.
- **GREEN — KEEP:** strong content, clear primary CTA, useful safety/privacy information.

### High-value annotation targets
- H01: header/name/portrait, hero headline, primary CTA, topic cards, floating question/help control, lower credentials and footer.
- P05/T01–T11: test disclaimer, progress indicator, answer targets, result interpretation, next step, crisis/support link.
- P09: local-only progress explanation, challenge completion display, reset/clear affordance if present.
- P20–P23: distinguish platform information, directory browsing, and joining flow; show empty-state and verification process clearly.
- All mobile captures: test floating home button against bottom browser UI, chat/help bubble, sticky header, and long Arabic button text.

---

## 3. Complete sitemap and page inventory

The repository sitemap is `/sitemap.xml`. It is the canonical route inventory for indexing, but it does not necessarily include every utility or error route. The source tree also contains routes that should be reviewed for intentional sitemap inclusion/exclusion.

### Main pages and purpose / sections / primary actions

| Route | Purpose | Main sections observed from markup/content | Primary CTA / actions |
|---|---|---|---|
| `/` | Arabic homepage and main entry point | Hero; topic finder; start paths; daily quiz; myth/fact; content discovery; latest articles; tests; videos; sessions; bio; credentials; research; FAQ; footer | Start here, free test, topic cards, articles, tests, videos, sessions, contact |
| `/en/` | English-language homepage | English brand introduction and content entry points | Explore / navigate to English content |
| `/start/` | Onboarding and guide to site use | Site map by need/content type; how to use resources | Choose a section or learning route |
| `/articles/` | Article library | Article list/cards and topic discovery | Open article |
| `/articles/four-attachment-styles/` | Long-form educational article | Attachment-style explanations and related resources | Related test/article |
| `/articles/why-we-choose-the-same-person/` | Long-form educational article | Repeated relationship patterns and explanation | Related test/article |
| `/tests/` | Test catalog | 11 self-exploration tools and categories | Start a selected test |
| `/tests/attachment-style/` | Attachment-style self-exploration | Questions, scoring/interpretation and caveats | Complete test / related reading |
| `/tests/anxiety-gad7/` | Anxiety symptom screening | GAD-7 items, score interpretation and safety context | Complete measure / seek support if needed |
| `/tests/depression-phq8/` | Mood symptom screening | PHQ-8 items, score interpretation and safety context | Complete measure / seek support if needed |
| `/tests/self-esteem-rosenberg/` | Self-esteem measure | Items, scoring, interpretation | Complete measure |
| `/tests/wellbeing-who5/` | Wellbeing measure | WHO-5 items and interpretation | Complete measure |
| `/tests/porn-use-bps/` | Brief problematic-use screening | Items, scoring and explanatory caveats | Complete measure / resources |
| `/tests/personality-big-five/` | Personality exploration | Big Five questions and trait feedback | Complete test |
| `/tests/mindfulness-maas/` | Mindfulness measure | MAAS items and interpretation | Complete measure |
| `/tests/self-compassion-scs/` | Self-compassion measure | SCS-SF items and interpretation | Complete measure |
| `/tests/burnout-cbi/` | Burnout measure | CBI items and interpretation | Complete measure |
| `/tests/meaning-in-life-mlq/` | Meaning-in-life measure | MLQ items and interpretation | Complete measure |
| `/videos/` | Video/audio content library | Video collection and embedded/media content | Play/open video |
| `/exercise/` | Weekly practical exercise | Exercise prompt and reflection/practice instructions | Start exercise / save locally if supported |
| `/challenges/` | Short guided challenges | 3–7 day challenge cards and daily steps | Start/continue challenge |
| `/my-space/` | Local progress dashboard | 7-day challenge and other challenge progress; privacy note | Continue challenge / open challenges |
| `/feelings/` | Emotion vocabulary and identification tool | Emotion wheel/categories and explanatory content | Select/identify feeling |
| `/relationship-check/` | Relationship reflection tool | Relationship prompts and feedback | Start reflection |
| `/questions/` | Common questions and educational answers | Question topics and answers | Read/expand answer |
| `/stories/` | Recovery stories | Story listing/content | Read story |
| `/worksheets/` | Printable/downloadable worksheets | Worksheet cards and PDF/preview links | View/download worksheet |
| `/book/` | Author/book information | Book cover, description, sample pages and purchase links | Read sample / purchase |
| `/shelf/` | Curated reading/resources shelf | Books and recommendations | Open recommendation |
| `/sessions/` | Information about online sessions | Service explanation, scope/eligibility and contact route | Contact / enquire |
| `/ask/` | Anonymous question entry point | Question explanation, privacy boundaries, submission interaction | Submit question |
| `/contact/` | Contact destination | Contact options and form/details | Contact |
| `/platform/` | Professional platform overview | Audience categories, platform scope, links to paths/directory/join | Explore platform |
| `/paths/` | Guided learning paths | Anxiety, relationships/attachment, self-relationship, wellbeing/meaning | Start a learning path |
| `/experts/` | Professional directory (early/empty state) | Directory status, practitioner/researcher/trainer/author categories, verification explanation | Read criteria / join |
| `/join-us/` | Interest/entry point for prospective directory profiles | Categories, review standards, information to be reviewed, steps | Express interest / contact |
| `/help-now/` | Urgent support resource | Crisis/support information and directions | Get immediate help |
| `/privacy/` | Privacy policy | Data practices and privacy explanation | Review policy |
| `/terms/` | Terms of use | Use limitations and terms | Review terms |
| `/porn-addiction/` | Topic resource | Educational content and resources | Read / seek appropriate support |
| `/battery/` | Resilience/psychological battery tool | Battery metaphor and resilience-related content | Explore/complete activity |
| `/myth-fact/` | Daily myth-or-fact interaction | Statement, response feedback, explanation and next step | Answer / share |
| `/404.html` | Not-found recovery | Error explanation and navigation back | Return home / browse |

**Inventory note:** The repository has 209 tracked files in 54 directories at the reviewed tree. The page inventory above includes all public-facing page routes found in the source tree and sitemap-level route families. The complete raw file tree is below.

---

## 4. Navigation structure

### Shared primary navigation (as observed in homepage markup)
- Home
- Articles
- Psychological tests
- Videos
- Platform
- Learning paths
- Experts directory
- Exercise of the week
- Short challenges
- Feelings wheel
- Relationship check
- Worksheets
- Questions
- Recovery stories
- Recommendations shelf
- Books
- External blog
- About / credentials
- Sessions
- Anonymous questions
- Contact
- Join the platform
- English

### Navigation behavior
- Shared dropdowns use native `details/summary` patterns.
- `assets/nav.js` closes other dropdowns when one opens, closes menus on outside click, and supports Escape with focus return.
- A persistent floating Home link is injected on non-home pages using the shared navigation script.
- In-page hash links open folded credential/research sections where applicable.

### Navigation recommendations
1. Separate **Learn**, **Practice**, **Explore tools**, and **About/Contact** into four top-level groups.
2. Keep 5–7 primary destinations visible at desktop widths; move lower-frequency routes into a clearly labeled “More” menu.
3. Avoid listing the same test/challenge routes in multiple navigation groups unless the grouping has distinct user value.
4. Make the mobile menu a full-height or large, scrollable panel with a clear close control and visible section labels.
5. Add breadcrumbs on deep routes (articles, tests, worksheets, directory).
6. Add “Back to section” links on long test/article pages; retain Home but avoid making it the only recovery route.
7. Ensure external blog and Amazon links are visually marked as external.
8. Add current-page state with `aria-current="page"`.

---

## 5. Current color palette

The following values are extracted from CSS custom properties and the homepage-specific override. Because styles are layered, page colors vary by page and theme; the values below distinguish global tokens from homepage tokens.

### Global light-theme tokens (`assets/site.css`)
| Role | Token | Value |
|---|---|---|
| Primary page background | `--paper` | `#F5F7F4` |
| Card/surface | `--surface` | `#FFFFFF` |
| Secondary surface / mist | `--mist` | `#DFE9E4` |
| Main text | `--ink` | `#18233A` |
| Muted text | `--muted` | `#566274` |
| Borders/dividers | `--line` | `#D6DFDA` |
| Eucalyptus / primary accent | `--eucalyptus` | `#2F6F62` |
| Eucalyptus foreground | `--eucalyptus-ink` | `#FFFFFF` |
| Amber accent | `--amber` | `#B9862A` |
| Amber text | `--amber-text` | `#8A6214` |
| Focus ring | `--focus` | `#2F6F62` |

### Global dark-theme tokens
| Role | Value |
|---|---|
| Background | `#111A2A` |
| Surface | `#18233A` |
| Mist | `#1F3040` |
| Text | `#E8ECEF` |
| Muted text | `#A3AFBD` |
| Border | `#2A3A4D` |
| Eucalyptus accent | `#7FC1B1` |
| Amber | `#E2B35A` |

### Homepage-specific palette (`assets/home-redesign.css`)
- Initial homepage palette: paper `#F5F1E8`, card `#FFFAF3`, ink `#26313D`, muted `#69727D`, line `#E4D8C6`, blue accent `#426B88`.
- Later homepage overrides: paper `#F2F0E7`, card `#FFFDF7`, ink `#203B34`, muted `#586B62`, line `#D8DFD4`, accent `#37695C`, dark accent `#244D43`.
- Homepage hero has a later gradient treatment using sage/blue/warm-neutral tones. The actual rendered appearance should be confirmed with browser screenshots.

### Topic-card accent families present in CSS
- Blue: `#E3EDF9 / #1D3F6E / #2F6BB3`
- Lavender: `#ECE6F7 / #43306E / #6A4FB0`
- Terracotta: `#FAE4DF / #7A2618 / #C2482F`
- Rose: `#F9E3EE / #74224A / #B2457B`
- Slate: `#E6EAEE / #2F3C4A / #5B6B7C`
- Sand: `#F8EED6 / #5F4410 / #B9862A`

### Recommended design-system palette (recommendation, not current)
- Primary deep evergreen: `#24584D`
- Secondary sage: `#7D9F91`
- Background warm ivory: `#F5F2E9`
- Surface: `#FFFCF6`
- Cool secondary surface: `#E8F0EC`
- Main text: `#20312D`
- Muted text: `#5F6E68`
- Accent gold: `#C69A4B`
- Error: `#A83C3C`
- Success: `#2E7657`
- Focus: `#24584D`

**Recommendation:** Use semantic tokens consistently. Avoid using accent color as body text on pale cards unless contrast is tested; target WCAG 2.2 AA contrast (4.5:1 normal text, 3:1 large text/UI boundaries).

---

## 6. Typography and fonts

### Font families referenced in CSS
- **IBM Plex Sans Arabic** — primary Arabic UI/body family.
- **IBM Plex Sans** — primary English UI/body family.
- **Noto Naskh Arabic** — Arabic display/fallback serif family.
- **Newsreader** — English display serif/fallback family.
- **Amiri** — Arabic display/hero/quotation family in homepage-specific styles.
- System fallbacks: `system-ui`, `Georgia`, `serif`, `sans-serif`.

### Local font files in repository
- `tools/fonts/plexar-400.ttf`
- `tools/fonts/plexar-600.ttf`
- `tools/fonts/naskh-700.ttf`
- `tools/fonts/newsreader-600.woff`
- `tools/fonts/LICENSE-OFL.txt`

### Typography recommendations
1. Define a clear type scale (12, 14, 16, 18, 22, 28, 36, 44/48).
2. Keep Arabic body text at 16–18 px minimum on mobile; long-form reading at 18–20 px.
3. Use one display face for Arabic headings and one UI/body family; avoid mixing Amiri and Naskh arbitrarily.
4. Use `line-height: 1.7–1.9` for Arabic body copy and 1.25–1.4 for headings.
5. Limit paragraph width to roughly 60–75 characters (adjust for Arabic script and RTL).
6. Ensure bold weights are real local font weights rather than synthetic where possible.
7. Load only necessary weights and use `font-display: swap`.

---

## 7. Top 20 UI/UX problems and risks

These are ranked source-based findings and likely user-experience risks. Confirm visual severity with real captures and user testing.

1. **Navigation breadth is high.** Too many destinations compete for attention; new visitors may not know where to start.
2. **Repeated navigation links.** Several destinations are surfaced in multiple dropdowns/sections; this can feel redundant.
3. **Homepage scope is broad.** It acts as personal profile, educational hub, test portal, video library, sessions page, and platform entry point.
4. **Primary conversion is ambiguous.** The homepage offers several plausible next steps without one dominant visitor journey.
5. **Long homepage.** Many content modules and credentials make the page difficult to scan on a phone.
6. **Mixed audiences.** General visitors, people seeking help, researchers, practitioners, and potential directory members need different entry paths.
7. **Directory is an early-stage empty state.** Clearly explain what exists now versus what is planned and avoid implying a functioning populated directory.
8. **Platform and directory hierarchy may be unclear.** Users may not distinguish platform overview, learning paths, experts directory, and join flow.
9. **Test catalog is dense.** Eleven tests need stronger grouping by user need and clear duration/intent labels.
10. **Mental-health assessment expectations.** Every test needs consistent “not a diagnosis” framing before and after completion.
11. **Crisis support discoverability.** “Help now” should be prominent on relevant tests and emotionally sensitive content, not buried only in footer navigation.
12. **Local-only data needs explicit explanation.** Explain exactly what is stored on the device, how to clear it, and what is not sent to a server.
13. **Floating controls compete.** Floating Home, help/chat/question controls, and sticky header can overlap on small screens.
14. **Long-form content needs stronger reading navigation.** Add contents anchors, reading time, sources, and related-resource modules.
15. **CTAs need consistent verbs.** Use action labels such as “ابدأ الاختبار”, “اقرأ المقال”, “جرّب التمرين” rather than generic labels.
16. **External destinations are mixed with internal routes.** Mark external blog, video platforms, and book purchase destinations.
17. **Trust signals need contextual placement.** Credentials and research are valuable but should be concise near the relevant claims and expanded lower on the homepage.
18. **No clear search/discovery layer.** A large content library benefits from site search or filters (with no sensitive query logging).
19. **Content freshness varies.** Sitemap includes at least one videos route with an older lastmod value; audit lastmod generation and update only when content actually changes.
20. **Visual consistency may drift.** Multiple CSS layers and homepage-specific overrides can produce different button, spacing, card, and typography behavior across page families.

---

## 8. Top 20 visual design improvements

1. Establish a single design-token layer for color, spacing, radius, shadows, type scale, and breakpoints.
2. Create a consistent 8 px spacing system (4 px micro spacing).
3. Standardize card radius, border, padding, and hover/focus behavior.
4. Give every page one clear H1 and a concise one-line purpose statement.
5. Use one prominent primary CTA per page and one quieter secondary CTA.
6. Use consistent icon style and stroke weight; avoid mixing emoji and line icons in the same card set.
7. Improve section separation with subtle surface changes rather than heavy borders everywhere.
8. Limit text measure for better Arabic readability.
9. Use a consistent hero pattern with portrait/illustration only where it improves context.
10. Build topic cards with consistent height, title placement, icon area, and action placement.
11. Use a controlled accent palette: evergreen + sage + warm ivory + restrained gold.
12. Use color meaning consistently (blue = information, amber = attention, red = urgent/error, green = progress).
13. Add visual hierarchy to article metadata (topic, reading time, date) without overwhelming title.
14. Create a consistent test UI with progress, question count, answer options, result, and caveat.
15. Design a unified empty-state component for directory, search, and content gaps.
16. Use a consistent image aspect ratio and object-position rules for cards.
17. Create a reusable footer with grouped links and a clear contact destination.
18. Make button heights and tap targets consistent (minimum 44 × 44 CSS px).
19. Improve focus-visible styling with a clear 2–3 px outline and offset.
20. Add subtle motion only for feedback; respect `prefers-reduced-motion`.

---

## 9. Top 20 mobile responsiveness issues to test

These are risk areas inferred from the page structure/shared CSS; they are **not confirmed defects without browser/device testing**.

1. Header brand/name/portrait may become cramped alongside hamburger controls.
2. Arabic brand text can wrap or become low contrast at narrow widths.
3. Large hero typography may wrap awkwardly into short lines.
4. Hero buttons may wrap or become unequal widths.
5. Long topic-card labels may create uneven card heights.
6. Grid layouts may collapse too late or too early at tablet breakpoints.
7. Multiple navigation dropdowns may become too tall for the viewport.
8. Dropdown menus need scroll containment and clear close behavior.
9. Floating Home may overlap chat/help controls.
10. Floating controls may cover test answers or bottom-page CTAs.
11. Sticky header may consume too much vertical space on small screens.
12. Safe-area insets need testing on iPhone bottom and top edges.
13. Long Arabic headings may overflow cards/buttons without `overflow-wrap` and proper min-width handling.
14. Test answer buttons need generous height and vertical spacing.
15. Result tables/score explanations may overflow horizontally.
16. Worksheet cards and PDF previews need mobile-specific aspect ratios.
17. Video embeds may exceed viewport width or create excessive vertical height.
18. Book sample pages and image galleries need responsive sizing and lazy loading.
19. Long article pages need anchor navigation and “back to top” behavior that does not obscure text.
20. Forms/inputs (ask/contact/join) need mobile keyboard, label, validation, and focus testing.

### Required viewport QA
- 320 × 568 (minimum narrow legacy phone)
- 360 × 800
- 375 × 812
- 390 × 844
- 430 × 932
- 768 × 1024
- 1024 × 768
- 1365 × 900
- 1440 × 1000

Check horizontal overflow, text zoom at 200%, landscape, keyboard open, menu open, and safe-area overlap.

---

## 10. SEO audit summary

### Present in source
- `sitemap.xml` exists and contains canonical HTTPS URLs and Arabic/English alternate links for the homepages.
- `robots.txt` exists and points to the sitemap.
- Root verification token file exists: `a70e72adc175449e921c4c096d97787f.txt`.
- JSON-LD Person schema is present on the Arabic homepage (source inspection).
- Canonical/meta description infrastructure is present in page markup.
- Open Graph preview images exist under `assets/og/`.
- `llms.txt` exists.
- GitHub Actions includes an IndexNow notification workflow; this is not the same as Google indexing.
- Sitemap includes content pages and test routes.

### Not verifiable from repository alone
- Whether the correct `drmilladmikhail.com` property is verified in the user's Google Search Console account.
- Whether the sitemap has been submitted and accepted in Search Console.
- Whether the homepage or individual pages are indexed, canonical-selected, or blocked by a Google report.
- Whether manual “Request indexing” was submitted.
- Search performance, impressions, clicks, queries, Core Web Vitals field data, or rich-result eligibility.
- Whether social profiles link back to the canonical domain.

### SEO recommendations
1. Add/validate a single canonical host policy (HTTPS, apex vs www) and redirects.
2. Check every sitemap URL returns 200, canonical points to itself, and is indexable.
3. Remove redirecting, duplicate, thin, or intentionally private routes from the sitemap.
4. Generate `lastmod` from real content changes, not deploy time.
5. Validate Person JSON-LD using Schema.org Validator and Google Rich Results Test; keep facts accurate and verifiable.
6. Add `sameAs` only for official profiles controlled by the subject.
7. Add Article schema to article pages with author, datePublished, dateModified, headline, image, and mainEntityOfPage.
8. Add BreadcrumbList schema to deep pages.
9. Ensure every page has a unique title and meta description.
10. Ensure Arabic and English pages use correct `hreflang` reciprocal links where equivalent translations exist.
11. Add descriptive alt text for meaningful images; empty alt for decorative imagery.
12. Use descriptive internal links and avoid generic “click here”.
13. Review noindex/canonical consistency for ask, directory-interest, and other sensitive or utility pages.
14. Avoid exposing user-submitted sensitive mental-health information in indexable pages.
15. Verify Google Search Console for the exact property `https://drmilladmikhail.com/` or the domain property `drmilladmikhail.com`; submit `https://drmilladmikhail.com/sitemap.xml`.
16. Inspect the homepage and key routes with URL Inspection and request indexing where appropriate.
17. Monitor Page indexing, HTTPS, Core Web Vitals, and Enhancements reports.
18. Keep crisis/help content accurate, region-aware, and easy to find.
19. Add clear author/reviewer and source references for health content.
20. Avoid claims that a self-report test diagnoses a disorder or replaces professional evaluation.

---

## 11. Page hierarchy and navigation redesign plan

### Recommended information architecture

- **Home**
- **Learn**
  - Articles
  - Videos
  - Questions
  - Stories
  - Book / reading shelf
- **Understand yourself**
  - Tests
  - Feelings wheel
  - Relationship check
  - Battery / resilience tool
- **Practice**
  - Weekly exercise
  - Challenges
  - Worksheets
  - My Space
- **Professional platform**
  - Platform overview
  - Learning paths
  - Experts directory
  - Join the directory
- **About**
  - Profile and credentials
  - Research
  - Sessions
  - Contact
- **Help now** (always visible as a safety route where relevant)
- **English**

### Homepage redesign plan
1. Header: clear portrait + name + concise descriptor + simple menu.
2. Hero: one core promise (“افهم نفسك… وخد خطوة لحياة أهدى”), short supporting sentence, one primary CTA, one secondary CTA.
3. “What brings you here?” topic finder with 5–6 calm color-coded cards.
4. A compact “Start here” pathway: Read / Explore a test / Try a practice.
5. One featured interactive item (daily question OR myth/fact; not both at equal visual priority).
6. Curated latest articles and videos in separate, visually consistent rows.
7. Tests preview grouped by topic and with explicit non-diagnostic note.
8. Platform block separated from general visitor resources.
9. Short author trust panel; move full credentials/research into expandable or dedicated About section.
10. Sessions/contact block only if current availability, scope, and eligibility are accurate.
11. FAQ, crisis support link, privacy note, and structured footer.

---

## 12. Conversion optimization ideas

- Choose a primary homepage conversion: “ابدأ من هنا” to a guided route, rather than competing CTAs.
- Create separate paths for: seeking self-understanding, learning, practical exercises, and professional networking.
- Add topic-based landing pages with related article + tool + exercise + next step.
- Show time estimates and what a user will get before starting each test or exercise.
- Provide clear “what happens next” after every result.
- Use one CTA label consistently for each action type.
- Add contextual cross-links: article → related test → exercise → support.
- Add low-friction newsletter only if privacy, consent, and unsubscribe are properly implemented; do not add sensitive mental-health profiling.
- Track aggregate, privacy-conscious conversion events only with transparent disclosure and consent as legally required.
- Do not collect identifiable health answers or personal reflections unless a secure, governed backend and explicit consent are implemented.
- Keep the professional directory “coming soon” until verification, consent, and moderation processes are real.

---

## 13. Accessibility and safety review

- Target WCAG 2.2 AA.
- Confirm text contrast for muted text and accent text on colored cards.
- Ensure all controls have visible focus, accessible names, and keyboard support.
- Confirm RTL semantics and reading order on Arabic pages.
- Use `lang="ar"` and `dir="rtl"` correctly; use `lang="en"` and `dir="ltr"` for English.
- Use buttons for actions and links for navigation.
- Ensure errors are announced to screen readers and tied to fields.
- Avoid color-only meaning for test scores or feedback.
- Include non-diagnostic disclaimers at the start and result of tests.
- Make emergency/help-now guidance visible in relevant contexts.
- Keep directory credentials and scope-of-practice distinctions explicit; academic/trainer status must not be presented as clinical authorization.

---

## 14. Full repository file tree

**Tracked file count:** 209  
**Directory count:** 54  
**Source:** GitHub recursive tree for `main` at review time.

#### `.github/workflows`
- `indexnow.yml`
- `platform-pr-checks.yml`
- `site-checks.yml`
- `stats.yml`
- `videos.yml`

#### `/`
- `.gitignore`
- `.nojekyll`
- `404.html`
- `CNAME`
- `README.md`
- `a70e72adc175449e921c4c096d97787f.txt`
- `index.html`
- `llms.txt`
- `robots.txt`
- `sitemap.xml`

#### `articles`
- `HOWTO.md`
- `articles.json`
- `index.html`

#### `articles/content`
- `four-attachment-styles.html`
- `why-we-choose-the-same-person.html`

#### `articles/four-attachment-styles`
- `index.html`

#### `articles/why-we-choose-the-same-person`
- `index.html`

#### `ask`
- `index.html`

#### `assets`
- `articles-index.json`
- `battery-cover.jpg`
- `battery-cover.webp`
- `challenges.js`
- `daily.js`
- `extras.js`
- `feelings.js`
- `helper.js`
- `home-redesign.css`
- `listen.js`
- `love-cover-ar.jpg`
- `love-cover-ar.webp`
- `love-cover-en.jpg`
- `love-cover-en.webp`
- `millad-cut.webp`
- `millad.jpg`
- `millad.webp`
- `my-space.js`
- `myth-fact.js`
- `nav.js`
- `quick-quiz.js`
- `quiz.js`
- `relcheck.js`
- `share.js`
- `site.css`
- `videos.js`
- `videos.json`

#### `assets/book`
- `love-p09-600.webp`
- `love-p09.jpg`
- `love-p09.webp`
- `love-p10-600.webp`
- `love-p10.jpg`
- `love-p10.webp`
- `love-p11-600.webp`
- `love-p11.jpg`
- `love-p11.webp`
- `love-p12-600.webp`
- `love-p12.jpg`
- `love-p12.webp`
- `love-p16-600.webp`
- `love-p16.jpg`
- `love-p16.webp`
- `love-p17-600.webp`
- `love-p17.jpg`
- `love-p17.webp`
- `love-p18-600.webp`
- `love-p18.jpg`
- `love-p18.webp`
- `love-p19-600.webp`
- `love-p19.jpg`
- `love-p19.webp`
- `love-p23-600.webp`
- `love-p23.jpg`
- `love-p23.webp`
- `love-p27-600.webp`
- `love-p27.jpg`
- `love-p27.webp`
- `love-p30-600.webp`
- `love-p30.jpg`
- `love-p30.webp`
- `love-p35-600.webp`
- `love-p35.jpg`
- `love-p35.webp`
- `love-p37-600.webp`
- `love-p37.jpg`
- `love-p37.webp`
- `love-p42-600.webp`
- `love-p42.jpg`
- `love-p42.webp`
- `love-p46-600.webp`
- `love-p46.jpg`
- `love-p46.webp`
- `love-p50-600.webp`
- `love-p50.jpg`
- `love-p50.webp`
- `love-p53-600.webp`
- `love-p53.jpg`
- `love-p53.webp`
- `love-p59-600.webp`
- `love-p59.jpg`
- `love-p59.webp`
- `love-p64-600.webp`
- `love-p64.jpg`
- `love-p64.webp`
- `robots-note.txt`

#### `assets/illustrations`
- `listen.svg`
- `practice.svg`
- `read.svg`
- `research.svg`
- `session.svg`
- `understand.svg`

#### `assets/og`
- `articles.jpg`
- `four-attachment-styles.jpg`
- `home-en.jpg`
- `home.jpg`
- `tests.jpg`
- `why-we-choose-the-same-person.jpg`

#### `battery`
- `index.html`

#### `book`
- `index.html`

#### `challenges`
- `index.html`

#### `contact`
- `index.html`

#### `content`
- `PRIORITIES.md`
- `QA-HOWTO.md`
- `WORKSHEETS-HOWTO.md`
- `ask.json`
- `challenges.json`
- `comments.json`
- `exercises.json`
- `feelings.json`
- `questions.json`
- `relationship-check.json`
- `shelf.json`
- `stories.json`
- `worksheets.json`

#### `docs`
- `platform-phase-2-architecture.md`

#### `en`
- `index.html`

#### `exercise`
- `index.html`

#### `experts`
- `index.html`

#### `feelings`
- `index.html`

#### `gifts`
- `hodoody-fil-hob-7k2m.pdf`

#### `help-now`
- `index.html`

#### `join-us`
- `index.html`

#### `my-space`
- `index.html`

#### `myth-fact`
- `index.html`

#### `paths`
- `index.html`

#### `platform`
- `index.html`

#### `porn-addiction`
- `index.html`

#### `privacy`
- `index.html`

#### `questions`
- `index.html`

#### `relationship-check`
- `index.html`

#### `sessions`
- `index.html`

#### `shelf`
- `index.html`

#### `start`
- `index.html`

#### `stories`
- `index.html`

#### `terms`
- `index.html`

#### `tests`
- `HOWTO.md`
- `ROADMAP.md`
- `index.html`
- `tests.json`

#### `tests/anxiety-gad7`
- `index.html`

#### `tests/attachment-style`
- `index.html`

#### `tests/burnout-cbi`
- `index.html`

#### `tests/depression-phq8`
- `index.html`

#### `tests/meaning-in-life-mlq`
- `index.html`

#### `tests/mindfulness-maas`
- `index.html`

#### `tests/personality-big-five`
- `index.html`

#### `tests/porn-use-bps`
- `index.html`

#### `tests/self-compassion-scs`
- `index.html`

#### `tests/self-esteem-rosenberg`
- `index.html`

#### `tests/wellbeing-who5`
- `index.html`

#### `tools`
- `add_analytics.py`
- `build_articles.py`
- `build_extras.py`
- `build_images.py`
- `build_pages.py`
- `build_tests.py`
- `build_videos.py`
- `build_worksheets.py`
- `fetch_stats.py`
- `pages_trust.py`
- `site_header.py`

#### `tools/fonts`
- `LICENSE-OFL.txt`
- `naskh-700.ttf`
- `newsreader-600.woff`
- `plexar-400.ttf`
- `plexar-600.ttf`

#### `tools/gifts`
- `boundaries.html`

#### `videos`
- `index.html`

#### `worksheets`
- `before-going-back.pdf`
- `before-going-back.webp`
- `boundaries-in-love.pdf`
- `boundaries-in-love.webp`
- `feelings-diary.pdf`
- `feelings-diary.webp`
- `hard-day-plan.pdf`
- `hard-day-plan.webp`
- `index.html`
- `joy-list.pdf`
- `joy-list.webp`
- `manifest.json`
- `support-circles.pdf`
- `support-circles.webp`
- `triggers-map.pdf`
- `triggers-map.webp`
- `when-they-dont-reply.pdf`
- `when-they-dont-reply.webp`

---

## 15. Review checklist for the next AI / designer

Ask the next reviewer to:
1. Capture every route listed in Section 2 at desktop and mobile sizes.
2. Attach annotated screenshots with RED/AMBER/BLUE/GREEN callouts.
3. Validate all internal links and identify broken routes.
4. Test each interactive test from intro to result, without submitting real personal data.
5. Check every page at 320, 360, 375, 390, 430, 768, 1024, 1365, and 1440 CSS px.
6. Run Lighthouse (mobile and desktop) for performance, accessibility, best practices, and SEO.
7. Run axe or equivalent automated accessibility checks.
8. Validate JSON-LD and sitemap/canonical/hreflang.
9. Test navigation by keyboard and screen reader.
10. Report confirmed defects separately from inferred risks.

**End of source-based audit.**
