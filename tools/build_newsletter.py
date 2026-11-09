#!/usr/bin/env python3
"""Build the weekly newsletter pages: /newsletter/ (landing + archive),
/newsletter/thanks/ (post-subscribe) and /newsletter/issues/<date>/ from
content/newsletter-issues.json. Called from tools/build_pages.py main().

Subscriptions are received through FormSubmit (https://formsubmit.co) which
forwards them to the owner's inbox — no emails are stored on the site itself.
Update /privacy/ (tools/pages_trust.py) if this ever changes.
"""
import json
import os

import build_articles as ba

SITE = "https://drmilladmikhail.com"
EMAIL = "millad.mounir@gmail.com"
FORM_ACTION = f"https://formsubmit.co/{EMAIL}"
NEXT_URL = f"{SITE}/newsletter/thanks/"

CSS = '''
<style>
.nl-hero{padding:56px 0 36px;background:linear-gradient(135deg,var(--mist),var(--paper) 75%)}
.nl-hero .kicker{color:var(--amber-text);font-weight:700;margin:0 0 6px}
.nl-hero h1{font-family:var(--display-ar);font-size:clamp(32px,5vw,48px);margin:0 0 10px}
.nl-hero p{color:var(--muted);font-size:18px;max-width:720px;margin:0}
.nl-meta{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:16px;color:var(--muted);font-size:15px}
.nl-meta span{display:inline-flex;align-items:center;gap:6px}
.nl-body{padding:8px 0 54px}
.nl-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));margin:26px 0}
.nl-benefit{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:20px}
.nl-benefit .ico{font-size:26px}
.nl-benefit h2{font-size:19px;margin:8px 0 6px}
.nl-benefit p{color:var(--muted);margin:0;font-size:15px}
.nl-panel{max-width:640px;background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:clamp(20px,4vw,32px)}
.nl-form{display:grid;gap:12px;margin-top:6px;grid-template-columns:minmax(0,1fr)}
.nl-form label{display:grid;gap:6px;font-weight:600;min-width:0}
.nl-form input{font:inherit;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--paper);color:var(--ink);width:100%;box-sizing:border-box;min-width:0}
.nl-form input:focus{outline:3px solid var(--focus);outline-offset:1px}
.nl-form button{justify-self:start}
.nl-trust{color:var(--muted);font-size:14px;margin:14px 0 0}
.nl-archive{margin-top:40px}
.nl-archive h2{font-family:var(--display-ar);font-size:24px}
.nl-issue{display:block;border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0;text-decoration:none;background:var(--surface)}
.nl-issue:hover{border-color:var(--eucalyptus)}
.nl-issue b{color:var(--ink)}
.nl-issue span{display:block;color:var(--muted);font-size:15px;margin-top:4px}
.nl-empty{color:var(--muted);background:var(--mist);border-radius:14px;padding:18px}
.nl-issue-page{max-width:760px}
.nl-issue-page .kicker{color:var(--amber-text);font-weight:700;margin:0 0 6px}
.nl-issue-page h1{font-family:var(--display-ar);font-size:clamp(30px,4.5vw,42px);margin:0 0 6px}
.nl-issue-page .date{color:var(--muted);margin:0 0 18px}
.nl-block{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:18px 20px;margin:16px 0}
.nl-block h2{font-size:20px;margin:0 0 8px}
.nl-block p{margin:0}
.nl-block .go{display:inline-block;margin-top:10px;font-weight:600}
.nl-issue-page blockquote{border-inline-start:4px solid var(--amber);margin:18px 0;padding:4px 18px;font-size:18px}
._honey{display:none}
</style>
'''


def form(inline=False, btn="اشترك مجانًا"):
    name_field = "" if inline else (
        '<label>الاسم (اختياري)<input type="text" name="name" autocomplete="name" placeholder="اسمك"></label>')
    return f'''<form class="nl-form" action="{FORM_ACTION}" method="POST">
  <input type="hidden" name="_subject" value="اشتراك جديد في نشرة راحة البال">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="_next" value="{NEXT_URL}">
  <input type="text" name="_honey" class="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
  <label>الإيميل بتاعك<input type="email" name="email" required dir="ltr" autocomplete="email" placeholder="you@example.com"></label>
  {name_field}
  <button class="btn primary" type="submit">{btn}</button>
</form>'''


def load_issues():
    p = os.path.join(ba.ROOT, "content", "newsletter-issues.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f).get("issues", [])
    return []


def landing_page(page, write):
    issues = load_issues()
    archive = ""
    if issues:
        archive = '<div class="nl-archive"><h2>أعداد سابقة</h2>' + "".join(
            f'<a class="nl-issue" href="/newsletter/issues/{i["date"]}/"><b>{ba.esc(i["title"])}</b>'
            f'<span>{ba.esc(i["date"])}</span></a>' for i in reversed(issues)) + "</div>"
    else:
        archive = ('<div class="nl-archive"><h2>أعداد سابقة</h2>'
                   '<p class="nl-empty">أول عدد لسه نازل — اشترك عشان يوصلك أول واحد، وتقدر تقرأه بعدين هنا.</p></div>')
    body = f'''{CSS}
<section class="nl-hero">
  <div class="wrap">
    <p class="kicker">نشرة أسبوعية مجانية</p>
    <h1>نشرة راحة البال</h1>
    <p>رسالة واحدة كل أسبوع من د. ميلاد ميخائيل: مقال مختار بعناية، وأحدث الأبحاث النفسية بملخص عربي بسيط، وتأمل قصير يفتح أسبوعك.</p>
    <div class="nl-meta">
      <span>✉️ رسالة واحدة في الأسبوع</span>
      <span>🚫 من غير إعلانات</span>
      <span>↩️ إلغاء الاشتراك في أي وقت</span>
    </div>
  </div>
</section>
<section class="nl-body">
  <div class="wrap">
    <div class="nl-grid">
      <div class="nl-benefit"><span class="ico" aria-hidden="true">📖</span><h2>مقال مختار</h2><p>أفضل مقال في الأسبوع من الموقع في فهم الذات والعلاقات والمشاعر.</p></div>
      <div class="nl-benefit"><span class="ico" aria-hidden="true">🔬</span><h2>أحدث الأبحاث</h2><p>بحثان جديدان أسبوعيًا من مكتبة الأكاديميين، مترجمين للعربية بأسلوب مبسط.</p></div>
      <div class="nl-benefit"><span class="ico" aria-hidden="true">🌿</span><h2>تأمل الأسبوع</h2><p>فكرة قصيرة وعملية تبدأ بيها أسبوعك بهدوء.</p></div>
    </div>
    <div class="nl-panel">
      <h2>اشترك مجانًا</h2>
      {form()}
      <p class="nl-trust">إيميلك بيُستخدم للنشرة بس ومش بيتباع ولا بيتبادل مع أي حد. التفاصيل في <a href="/privacy/">صفحة الخصوصية</a>.</p>
    </div>
    {archive}
  </div>
</section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "url": f"{SITE}/newsletter/",
          "inLanguage": "ar", "name": "نشرة راحة البال الأسبوعية",
          "description": "نشرة أسبوعية مجانية: مقال مختار وأحدث الأبحاث النفسية مترجمة وتأمل قصير."}
    write("newsletter", page("newsletter", "نشرة راحة البال الأسبوعية",
                             "اشترك في نشرة د. ميلاد ميخائيل الأسبوعية: مقال مختار، أحدث الأبحاث النفسية مترجمة للعربية، وتأمل قصير. مجانًا ومن غير إعلانات.",
                             body, ld))


def thanks_page(page, write):
    body = f'''{CSS}
<section class="nl-hero">
  <div class="wrap">
    <p class="kicker">تمام</p>
    <h1>اشتراكك اتبعت</h1>
    <p>أول عدد من نشرة راحة البال هيتوصلك في أول إصدار. لو مش وصلك خلال أسبوع، بص على مجلد البريد المزعج (Spam) وعلّم الرسالة إنها مش مزعجة.</p>
    <p>في انتظارك كمان: <a href="/articles/">المقالات</a> · <a href="/tests/">اختبارات نفسية</a> · <a href="/research/library/">مكتبة الأبحاث</a></p>
  </div>
</section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "url": f"{SITE}/newsletter/thanks/",
          "inLanguage": "ar", "name": "تم الاشتراك في النشرة"}
    write("newsletter/thanks", page("newsletter/thanks", "تم الاشتراك", "تم استلام اشتراكك في نشرة راحة البال.", body, ld))


def issue_pages(page, write):
    for i in load_issues():
        art = i.get("article") or {}
        art_html = ""
        if art:
            art_html = (f'<div class="nl-block"><h2>📖 مقال الأسبوع</h2><p>{ba.esc(art.get("blurb", ""))}</p>'
                        f'<a class="go" href="{ba.esc(art.get("url", "#"))}">اقرأ المقال ←</a></div>')
        papers = "".join(
            f'<div class="nl-block"><h2>🔬 {ba.esc(p.get("title", ""))}</h2><p>{ba.esc(p.get("blurb", ""))}</p>'
            f'<a class="go" href="{ba.esc(p.get("url", "#"))}">الملخص الكامل في مكتبة الأبحاث ←</a></div>'
            for p in i.get("papers", []))
        refl = f'<blockquote>{ba.esc(i.get("reflection", ""))}</blockquote>' if i.get("reflection") else ""
        body = f'''{CSS}
<section class="nl-body">
  <div class="wrap nl-issue-page">
    <p class="kicker">نشرة راحة البال · عدد {ba.esc(i["date"])}</p>
    <h1>{ba.esc(i["title"])}</h1>
    <p class="date">من د. ميلاد ميخائيل</p>
    <p>{ba.esc(i.get("intro", ""))}</p>
    {art_html}
    {papers}
    {refl}
    <div class="nl-block"><h2>✉️ النشرة دي بتوصلك بالبريد كل أسبوع</h2>
    <p>لو وصلتك من صاحبك، <a href="/newsletter/">اشترك مجانًا من هنا</a>.</p></div>
    <p><a href="/newsletter/">← كل الأعداد</a></p>
  </div>
</section>'''
        ld = {"@context": "https://schema.org", "@type": "WebPage", "url": f"{SITE}/newsletter/issues/{i['date']}/",
              "inLanguage": "ar", "name": i["title"]}
        write(f"newsletter/issues/{i['date']}", page(f"newsletter/issues/{i['date']}", i["title"],
                                                     i.get("intro", "عدد من نشرة راحة البال الأسبوعية.")[:150], body, ld))


def build_all(ba_, page, write, SITE_):
    landing_page(page, write)
    thanks_page(page, write)
    issue_pages(page, write)
