#!/usr/bin/env python3
"""Apply a needs-first introduction to the generated start page."""
from pathlib import Path
import re

START = "<!-- START-JOURNEY:BEGIN -->"
END = "<!-- START-JOURNEY:END -->"
BLOCK = START + """
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
""" + END


def transform(text):
    marker = '<ol class="path">'
    if START in text:
        if END not in text:
            raise ValueError("Incomplete start journey block")
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: BLOCK, text, count=1, flags=re.S)
    elif marker in text:
        text = text.replace(marker, BLOCK + "\n      " + marker, 1)
    else:
        raise ValueError("Start page structure changed; review the template")
    text = text.replace("اعرف نفسك في دقيقتين", "استكشف الاختبارات لو حابب")
    text = text.replace("اختبارات علمية مجانية، النتيجة بتطلع على طول، ومش بتتحفظ في أي مكان. لو مش عارف تبدأ منين، ابدأ باختبار نمط التعلّق.", "اختار الاختبار المرتبط بالموضوع اللي يهمك. النتيجة للتوعية، ومش تشخيص ولا حكم ثابت عليك.")
    if 'class="journey-tests"' not in text:
        before, after = text.split(marker, 1)
        after = re.sub(r'(<ul class="plain-list">.*?</ul>)', r'<details class="journey-tests"><summary>عرض قائمة الاختبارات</summary>\1</details>', after, count=1, flags=re.S)
        text = before + marker + after
    return text


def apply(root):
    path = Path(root) / "start" / "index.html"
    if not path.is_file():
        return False
    original = path.read_text(encoding="utf-8")
    updated = transform(original)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


if __name__ == "__main__":
    apply(Path(__file__).resolve().parents[1])
