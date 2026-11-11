#!/usr/bin/env python3
"""Prepare and finalize the reviewed visitor-growth package."""
from pathlib import Path
import json
import re

INTRO = '<!-- GROWTH-INTRO:BEGIN --><p>أنماط التعلّق بتوصف اختلافات في إحساسنا بالأمان والقرب داخل العلاقات. التصنيفات الشائعة بتشمل الآمن والقلق والمتجنب والخائف المتجنب. دي أوصاف تساعد على الفهم، مش تشخيصات ولا هويات ثابتة، وماينفعش نحكم بيها على شخص من موقف واحد.</p><!-- GROWTH-INTRO:END -->'
NOTES = """<!-- GROWTH-NOTES:BEGIN -->
<h2>إزاي تستخدم الفكرة من غير ما تحكم على نفسك؟</h2>
<p>لاحظ السلوك المتكرر والسياق، بدل ما تعتبر كل تأخير في الرد رفضًا أو كل طلب لمساحة علامة على التجنّب. تجربة واحدة مش كفاية لتحديد نمط شخص، والتجارب اللاحقة والعلاقات ممكن تأثر على طريقتنا في القرب.</p>
<h2>هل اختبار التعلّق بيشخّص مشكلة نفسية؟</h2>
<p>لأ. الاختبار الذاتي أداة للتأمل في إجاباتك، مش تشخيصًا ولا إثباتًا إنك أو شريكك نمط ثابت. لو العلاقات بتسبب ضيقًا مستمرًا أو بتأثر على حياتك، التقييم مع متخصص مؤهل يساعدك تفهم السياق بدل الاعتماد على نتيجة اختبار وحدها.</p>
<h2>هل التعلّق المتجنب معناه إن الشخص مش بيحب؟</h2>
<p>مش بالضرورة. عدم الارتياح للقرب العاطفي ممكن يتواجد مع الرغبة في الحب والعلاقة. وفي نفس الوقت، وصف نمط التعلّق مش مبرر للإهانة أو التحكم أو الأذى.</p>
<h2>المصادر والقراءة الإضافية</h2>
<ul>
<li><a href="https://health.clevelandclinic.org/attachment-theory" target="_blank" rel="noopener">Cleveland Clinic: نظرية التعلّق وتأثير الخبرات اللاحقة</a></li>
<li><a href="https://health.clevelandclinic.org/anxious-attachment-style" target="_blank" rel="noopener">Cleveland Clinic: فهم التعلّق القلق</a></li>
<li><a href="https://health.clevelandclinic.org/avoidant-attachment-style" target="_blank" rel="noopener">Cleveland Clinic: فهم التعلّق المتجنب</a></li>
</ul>
<p>المصادر دي للشرح العام، ومش إثباتًا لصلاحية النسخة العربية من أي اختبار على الموقع.</p>
<!-- GROWTH-NOTES:END -->"""
JOURNEY = """<!-- START-JOURNEY:BEGIN -->
<section aria-labelledby="journey-title">
<h2 id="journey-title">إيه اللي شاغل بالك النهارده؟</h2>
<p>مش لازم تبدأ باختبار. اختار الموضوع الأقرب ليك، وابدأ بخطوة بسيطة تناسبك.</p>
<ul class="link-grid">
<li><a href="/articles/four-attachment-styles/"><b>العلاقات والتعلّق</b><span>اقرأ عن أنماط التعلّق وإزاي بتظهر في العلاقات.</span></a></li>
<li><a href="/feelings/"><b>فهم المشاعر</b><span>مش عارف تسمّي إحساسك؟ جرّب عجلة المشاعر.</span></a></li>
<li><a href="/challenges/"><b>خطوات عملية صغيرة</b><span>اختار تحديًا قصيرًا يناسب يومك.</span></a></li>
<li><a href="/articles/"><b>القراءة والاستكشاف</b><span>ابدأ بمقال، وكمل على مهلك.</span></a></li>
</ul>
<p>الاختبارات أدوات للتوعية وليست تشخيصًا، واستخدامها اختياري.</p>
</section>
<!-- START-JOURNEY:END -->"""


def start_html(text):
    marker = '<ol class="path">'
    if '<!-- START-JOURNEY:BEGIN -->' in text:
        text, count = re.subn(r'<!-- START-JOURNEY:BEGIN -->.*?<!-- START-JOURNEY:END -->', lambda _: JOURNEY, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError('Incomplete journey block')
    elif marker in text:
        text = text.replace(marker, JOURNEY + '\n' + marker, 1)
    else:
        raise ValueError('Start template changed')
    text = text.replace('اعرف نفسك في دقيقتين', 'استكشف الاختبارات لو حابب')
    text = text.replace('اختبارات علمية مجانية، النتيجة بتطلع على طول، ومش بتتحفظ في أي مكان. لو مش عارف تبدأ منين، ابدأ باختبار نمط التعلّق.', 'اختار الاختبار المرتبط بالموضوع اللي يهمك. النتيجة للتوعية، ومش تشخيص ولا حكم ثابت عليك.')
    if 'class="journey-tests"' not in text:
        before, after = text.split(marker, 1)
        after, count = re.subn(r'(<ul class="plain-list">.*?</ul>)', r'<details class="journey-tests"><summary>عرض قائمة الاختبارات</summary>\1</details>', after, count=1, flags=re.S)
        if count != 1:
            raise ValueError('Test list not found')
        text = before + marker + after
    return text


def home_html(text):
    # 2026-11-11: name + professional title first — his stated format, and the strongest
    # signal for people searching his name («دكتور ميلاد ميخائيل») on Google.
    title = 'د. ميلاد ميخائيل | استشاري العلاج النفسي والأسري'
    text = re.sub(r'<title>.*?</title>', lambda _: '<title>' + title + '</title>', text, count=1, flags=re.S)
    for key in ('og:title', 'twitter:title'):
        text = re.sub(r'(<meta (?:property|name)="' + key + r'" content=")[^"]*(")', lambda m: m[1] + title + m[2], text, count=1)
    desc = ('دكتور ميلاد ميخائيل (د. ميلاد ميخائيل، Dr. Millad Mikhail)، استشاري العلاج النفسي والأسري، '
            'حاصل على الدكتوراه في الصحة النفسية من جامعة قناة السويس، عضو الجمعية الأمريكية لعلم النفس (APA)، '
            'مؤلف كتاب «ليه بنحب اللي بيوجعنا؟» وصاحب قناة «جلسة شيزلونج». يُعرف أيضاً باسم د. ميلاد منير.')
    text = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m[1] + desc + m[2], text, count=1)
    text = text.replace('11 اختبار نفسي علمي', 'استكشف الاختبارات النفسية')
    text = re.sub(r'<section class="section myth-promo"[^>]*>.*?</section>', '', text, count=1, flags=re.S)
    if '<!-- GROWTH-GUIDE:BEGIN -->' not in text:
        text = re.sub(r'(<section class="section guide"[^>]*>.*?</section>)', lambda m: '<!-- GROWTH-GUIDE:BEGIN --><details class="wrap"><summary>دليل كل أقسام الموقع</summary>' + m[1] + '</details><!-- GROWTH-GUIDE:END -->', text, count=1, flags=re.S)
    return text


def write_changed(path, text):
    if path.read_text(encoding='utf-8') != text:
        path.write_text(text, encoding='utf-8')


def prepare_sources(root):
    root = Path(root)
    path = root / 'articles/content/four-attachment-styles.html'
    text = path.read_text(encoding='utf-8')
    if '<!-- GROWTH-INTRO:BEGIN -->' not in text:
        text = INTRO + '\n' + text
    if '<!-- GROWTH-NOTES:BEGIN -->' not in text:
        text += '\n' + NOTES + '\n'
    text = text.replace('أمير عنده نمط تعلق.', 'السلوك ده ممكن يتفهم من منظور أنماط التعلّق، لكنه مش كفاية لوحده لتحديد نمط أمير.')
    text = text.replace('وعشان تعرف نمطك بدقة أكتر، جرّب', 'ولو حابب تتأمل إجاباتك عن العلاقات، ممكن تجرّب')
    text = text.replace('(مقياس علمي من 9 أسئلة، والنتيجة بتطلع فوراً).', '(أداة توعوية من 9 أسئلة، والنتيجة مش تشخيصًا).')
    write_changed(path, text)
    path = root / 'articles/articles.json'
    items = json.loads(path.read_text(encoding='utf-8'))
    item = next(a for a in items if a['slug'] == 'four-attachment-styles')
    item['title'] = 'أنماط التعلّق الأربعة: الفرق بينها وتأثيرها على العلاقات'
    item['description'] = 'شرح أنماط التعلّق الآمن والقلق والمتجنب والخائف المتجنب، مع مقارنة وأمثلة وتمرين ومصادر وتوضيح حدود الاختبار الذاتي.'
    item['updated'] = '2026-11-08'
    write_changed(path, json.dumps(items, ensure_ascii=False, indent=2) + '\n')


def apply_pages(root):
    root = Path(root)
    path = root / 'index.html'
    write_changed(path, home_html(path.read_text(encoding='utf-8')))
    path = root / 'start/index.html'
    text = start_html(path.read_text(encoding='utf-8'))
    text = text.replace('مقال جديد كل اتنين وخميس.', 'مقالات قصيرة تقدر تستكشفها على مهلك.')
    write_changed(path, text)
    path = root / 'articles/index.html'
    if path.is_file():
        write_changed(path, path.read_text(encoding='utf-8').replace('مقال جديد كل اثنين وخميس.', 'استكشف المقالات المتاحة.'))


if __name__ == '__main__':
    prepare_sources(Path(__file__).resolve().parents[1])
