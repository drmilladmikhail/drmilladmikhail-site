# صفحات المعالجين

كل معالج = ملف JSON هنا باسمه (مثلاً `ahmed-ali.json`)، والـ slug هو اللي بيبقى في الرابط:
`https://drmilladmikhail.com/therapists/ahmed-ali/`

بعد أي تعديل: `python3 tools/build_therapists.py && python3 tools/add_analytics.py`

- `preview: true` → الصفحة فيها سطر "صفحة تجريبية" ومستخبية من جوجل. لما البيانات تبقى حقيقية ومتراجعة خليه `false`.
- `photo`: مسار صورة جوه `assets/therapists/` (مربعة، ٨٠٠ بكسل على الأقل). فاضي = أول حرف من الاسم.
- `contact_whatsapp`: رقم بالصيغة الدولية من غير + (مثلاً `201xxxxxxxxx`). لو موجود، زرار الحجز يفتح واتساب برسالة جاهزة.
- ماينفعش نكتب أي شهادة أو ترخيص أو تقييم مش من استمارة المعالج نفسه.
