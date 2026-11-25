/* Therapist dashboard: email sign-in link, edit own profile, write posts, moderate comments.
   Every permission is enforced in the database (RLS); this page only offers the controls. */
(function () {
  'use strict';
  var TP = window.TP;
  var el = TP && TP.el;
  var root = document.getElementById('dash');
  if (!root) return;
  if (!TP || !TP.client) {
    root.textContent = 'اللوحة مش قادرة تشتغل دلوقتي. جرّب تفتح الصفحة تاني بعد شوية.';
    return;
  }
  var db = TP.client;
  var me = null;        // therapist row
  var tab = 'profile';
  var COLS = 'id,slug,published,name,title,specialties,bio,experience,languages,credentials,courses,articles,videos,sessions,session_mode,schedule,cancel_policy,whatsapp,photo_path,comments_enabled,book_title,book_author,book_why,note_path,note_text';

  function clear() { root.textContent = ''; }
  function msg(text, kind) { return el('p', { class: 'dash-msg' + (kind ? ' dash-' + kind : ''), role: 'status', text: text || '' }); }
  function field(label, input, hint) {
    return el('div', { class: 'dash-field' }, [el('label', { for: input.id, text: label }), input, hint ? el('small', { text: hint }) : null]);
  }
  function input(id, value, attrs) {
    var a = Object.assign({ id: id, type: 'text', value: value || '' }, attrs || {});
    return el('input', a);
  }
  function area(id, value, attrs) {
    var t = el('textarea', Object.assign({ id: id, rows: 4 }, attrs || {}));
    t.value = value || '';
    return t;
  }

  /* ---------- sign in ---------- */
  function loginView(note) {
    clear();
    var email = input('login-email', '', { type: 'email', autocomplete: 'email', dir: 'ltr', required: true, inputmode: 'email' });
    var status = msg(note || '');
    var btn = el('button', { class: 'tp-btn', type: 'submit', text: 'ابعتلي لينك الدخول' });
    var form = el('form', { class: 'dash-card', novalidate: true }, [
      el('h1', { text: 'لوحة المعالج' }),
      el('p', { class: 'tp-muted', text: 'اكتب الإيميل المسجل بيه، وهيوصلك لينك تدخل بيه من غير باسورد.' }),
      field('الإيميل', email), btn, status
    ]);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = email.value.trim().toLowerCase();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) { status.textContent = 'اكتب إيميل صحيح.'; return; }
      btn.disabled = true; status.textContent = 'لحظة…';
      db.rpc('is_therapist_email', { p_email: v }).then(function (r) {
        if (r.error) { btn.disabled = false; status.textContent = 'حصلت مشكلة. جرّب تاني بعد شوية.'; return; }
        if (!r.data) { btn.disabled = false; status.textContent = 'الإيميل ده مش مسجل كمعالج. كلّم إدارة الموقع عشان يضيفوك.'; return; }
        db.auth.signInWithOtp({ email: v, options: { emailRedirectTo: location.origin + '/therapists/dashboard/', shouldCreateUser: true } })
          .then(function (s) {
            btn.disabled = false;
            if (s.error) {
              status.textContent = /rate|seconds/i.test(s.error.message || '')
                ? 'استنى دقيقة وجرّب تاني (فيه حد أقصى للإيميلات).'
                : 'اللينك ماتبعتش. جرّب تاني بعد شوية.';
              return;
            }
            status.textContent = 'تمام! افتح الإيميل بتاعك ودوس على اللينك. لو مالقيتوش، بص في Spam.';
          });
      });
    });
    root.appendChild(form);
  }

  /* ---------- after sign in ---------- */
  function load() {
    clear(); root.appendChild(msg('بيحمّل…'));
    db.rpc('my_therapist').then(function (r) {
      if (r.error || !r.data) {
        db.auth.signOut().then(function () { loginView('الحساب ده مش مربوط بصفحة معالج. كلّم إدارة الموقع.'); });
        return;
      }
      db.from('therapists').select(COLS).eq('id', r.data).single().then(function (t) {
        if (t.error) { clear(); root.appendChild(msg('مش قادر أحمّل بياناتك. جرّب تحدّث الصفحة.', 'err')); return; }
        me = t.data; shell();
      });
    });
  }

  function shell() {
    clear();
    var tabs = [['profile', 'صفحتي'], ['posts', 'البوستات'], ['comments', 'التعليقات']];
    var nav = el('nav', { class: 'dash-tabs', 'aria-label': 'أقسام اللوحة' });
    tabs.forEach(function (x) {
      nav.appendChild(el('button', { type: 'button', class: 'dash-tab', 'aria-pressed': String(tab === x[0]), text: x[1],
        onclick: function () { tab = x[0]; shell(); } }));
    });
    var top = el('div', { class: 'dash-top' }, [
      el('div', null, [el('b', { text: me.name || 'أهلاً' }), el('div', { class: 'tp-small tp-muted', text: 'لوحة التحكم في صفحتك' })]),
      el('div', { class: 'dash-top-actions' }, [
        el('a', { class: 'tp-btn tp-btn-sm', href: '/therapists/' + me.slug + '/', target: '_blank', rel: 'noopener', text: 'افتح صفحتي' }),
        el('button', { type: 'button', class: 'dash-link', text: 'خروج', onclick: function () { db.auth.signOut().then(function () { loginView('خرجت من حسابك.'); }); } })
      ])
    ]);
    var body = el('div', { id: 'dash-body' });
    root.appendChild(top); root.appendChild(nav); root.appendChild(body);
    if (tab === 'profile') profileView(body);
    else if (tab === 'posts') postsView(body);
    else commentsView(body);
  }

  /* ---------- repeatable rows (certificates, courses, articles, videos, prices) ---------- */
  function rows(id, items, cols, addLabel) {
    var wrap = el('div', { class: 'dash-rows', id: id });
    function addRow(v) {
      v = v || {};
      var r = el('div', { class: 'dash-row' });
      cols.forEach(function (c) {
        var i = el('input', { type: c.type || 'text', placeholder: c.label, 'aria-label': c.label, 'data-k': c.k, dir: c.dir || null });
        i.value = v[c.k] || '';
        r.appendChild(i);
      });
      r.appendChild(el('button', { type: 'button', class: 'dash-x', 'aria-label': 'امسح السطر', text: '×', onclick: function () { r.remove(); } }));
      list.appendChild(r);
    }
    var list = el('div', { class: 'dash-rowlist' });
    (items || []).forEach(addRow);
    if (!(items || []).length) addRow();
    wrap.appendChild(list);
    wrap.appendChild(el('button', { type: 'button', class: 'dash-link', text: '+ ' + addLabel, onclick: function () { addRow(); } }));
    wrap.read = function () {
      var out = [];
      list.querySelectorAll('.dash-row').forEach(function (r) {
        var o = {}, any = false;
        r.querySelectorAll('input').forEach(function (i) { o[i.getAttribute('data-k')] = i.value.trim(); if (i.value.trim()) any = true; });
        if (any) out.push(o);
      });
      return out;
    };
    return wrap;
  }

  function splitList(v) {
    return String(v || '').split(/[،,\n]/).map(function (s) { return s.trim(); }).filter(Boolean);
  }

  /* ---------- profile ---------- */
  function profileView(body) {
    var f = {
      name: input('p-name', me.name, { maxlength: 120 }),
      title: input('p-title', me.title, { maxlength: 120 }),
      specialties: input('p-spec', (me.specialties || []).join('، ')),
      experience: input('p-exp', me.experience, { maxlength: 120 }),
      languages: input('p-lang', (me.languages || []).join('، ')),
      bio: area('p-bio', me.bio, { maxlength: 3000, rows: 6 }),
      session_mode: input('p-mode', me.session_mode, { maxlength: 120 }),
      schedule: area('p-sched', me.schedule, { maxlength: 400, rows: 2 }),
      cancel_policy: input('p-cancel', me.cancel_policy, { maxlength: 300 }),
      whatsapp: input('p-wa', me.whatsapp, { inputmode: 'numeric', dir: 'ltr', maxlength: 15 }),
      book_title: input('p-book', me.book_title, { maxlength: 200 }),
      book_author: input('p-book-author', me.book_author, { maxlength: 120 }),
      book_why: area('p-book-why', me.book_why, { maxlength: 1200, rows: 3 }),
      note_text: area('p-note-text', me.note_text, { maxlength: 600, rows: 3 })
    };
    var creds = rows('p-creds', me.credentials, [{ k: 'name', label: 'الشهادة' }, { k: 'place', label: 'الجامعة / الجهة' }, { k: 'year', label: 'السنة' }], 'شهادة');
    var courses = rows('p-courses', me.courses, [{ k: 'name', label: 'الكورس' }, { k: 'place', label: 'الجهة' }, { k: 'year', label: 'السنة' }], 'كورس');
    var arts = rows('p-arts', me.articles, [{ k: 'title', label: 'عنوان المقال' }, { k: 'place', label: 'اتنشر فين' }, { k: 'url', label: 'الرابط https://', type: 'url', dir: 'ltr' }], 'مقال');
    var vids = rows('p-vids', me.videos, [{ k: 'title', label: 'عنوان الفيديو' }, { k: 'url', label: 'رابط يوتيوب', type: 'url', dir: 'ltr' }], 'فيديو');
    var prices = rows('p-prices', me.sessions, [{ k: 'length', label: 'المدة (مثلاً ٦٠ دقيقة)' }, { k: 'price', label: 'السعر' }], 'مدة وسعر');
    var comments = el('input', { type: 'checkbox', id: 'p-comments' });
    comments.checked = !!me.comments_enabled;

    function uploader(id, key, label, hint, preview) {
      var st = msg('');
      var inp = el('input', { type: 'file', id: id, accept: 'image/jpeg,image/png,image/webp' });
      inp.addEventListener('change', function () {
        var file = inp.files && inp.files[0];
        if (!file) return;
        if (file.size > 3 * 1024 * 1024) { st.textContent = 'الصورة أكبر من ٣ ميجا. اختار صورة أصغر.'; return; }
        var ext = ({ 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp' })[file.type];
        if (!ext) { st.textContent = 'الصورة لازم تكون JPG أو PNG أو WEBP.'; return; }
        var path = me.id + '/' + key + '-' + Date.now() + '.' + ext;
        st.textContent = 'بترفع الصورة…';
        db.storage.from(TP.BUCKET).upload(path, file, { contentType: file.type, upsert: false }).then(function (u) {
          if (u.error) { st.textContent = 'الصورة ماترفعتش. جرّب تاني.'; return; }
          var col = key === 'note' ? 'note_path' : 'photo_path';
          var old = me[col], upd = {};
          upd[col] = path;
          db.from('therapists').update(upd).eq('id', me.id).then(function (r) {
            if (r.error) { st.textContent = 'الصورة اترفعت بس ماتحفظتش. جرّب تاني.'; return; }
            me[col] = path; preview(); st.textContent = 'الصورة اتحفظت.';
            if (old) db.storage.from(TP.BUCKET).remove([old]);
          });
        });
      });
      return [field(label, inp, hint), st];
    }

    var photoStatus = msg('');
    var photoPrev = el('div', { class: 'dash-photo' });
    function showPhoto() {
      photoPrev.textContent = '';
      var u = TP.photoUrl(me.photo_path);
      photoPrev.appendChild(u ? el('img', { src: u, alt: 'صورتك', width: 96, height: 96 }) : el('div', { class: 'tp-photo tp-initial', text: TP.initial(me.name) }));
    }
    showPhoto();
    var photoInput = el('input', { type: 'file', id: 'p-photo', accept: 'image/jpeg,image/png,image/webp' });
    photoInput.addEventListener('change', function () {
      var file = photoInput.files && photoInput.files[0];
      if (!file) return;
      if (file.size > 3 * 1024 * 1024) { photoStatus.textContent = 'الصورة أكبر من ٣ ميجا. اختار صورة أصغر.'; return; }
      var ext = ({ 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp' })[file.type];
      if (!ext) { photoStatus.textContent = 'الصورة لازم تكون JPG أو PNG أو WEBP.'; return; }
      var path = me.id + '/photo-' + Date.now() + '.' + ext;
      photoStatus.textContent = 'بترفع الصورة…';
      db.storage.from(TP.BUCKET).upload(path, file, { contentType: file.type, upsert: false }).then(function (u) {
        if (u.error) { photoStatus.textContent = 'الصورة ماترفعتش. جرّب تاني.'; return; }
        var old = me.photo_path;
        db.from('therapists').update({ photo_path: path }).eq('id', me.id).then(function (r) {
          if (r.error) { photoStatus.textContent = 'الصورة اترفعت بس ماتحفظتش. جرّب تاني.'; return; }
          me.photo_path = path; showPhoto(); photoStatus.textContent = 'الصورة اتحفظت.';
          if (old) db.storage.from(TP.BUCKET).remove([old]);
        });
      });
    });

    var notePrev = el('div', { class: 'dash-note' });
    function showNote() {
      notePrev.textContent = '';
      var u = TP.photoUrl(me.note_path);
      if (u) {
        notePrev.appendChild(el('img', { src: u, alt: 'رسالتك بخط إيدك' }));
        notePrev.appendChild(el('button', { type: 'button', class: 'dash-link dash-danger', text: 'شيل الصورة', onclick: function () {
          var old = me.note_path;
          db.from('therapists').update({ note_path: '' }).eq('id', me.id).then(function (r) {
            if (r.error) return;
            me.note_path = ''; showNote();
            if (old) db.storage.from(TP.BUCKET).remove([old]);
          });
        } }));
      }
    }
    showNote();
    var noteUp = uploader('p-note', 'note', 'صورة الرسالة', 'اكتب رسالة قصيرة للزائر على ورقة بخط إيدك وصوّرها في نور كويس. JPG أو PNG.', showNote);

    var status = msg('');
    var save = el('button', { type: 'submit', class: 'tp-btn', text: 'احفظ التعديلات' });
    var form = el('form', { class: 'dash-card', novalidate: true }, [
      el('h2', { text: 'صورتك' }), photoPrev, field('غيّر الصورة', photoInput, 'صورة واضحة، خلفية هادية، JPG أو PNG.'), photoStatus,
      el('h2', { text: 'البيانات الأساسية' }),
      field('اسمك زي ما يظهر على الصفحة', f.name),
      field('اللقب', f.title, 'مثلاً: معالج نفسي، أخصائي نفسي إكلينيكي'),
      field('التخصصات', f.specialties, 'افصل بينهم بفاصلة، لحد ٨'),
      field('الخبرة', f.experience, 'مثلاً: ١٠ سنين'),
      field('اللغات', f.languages, 'افصل بينهم بفاصلة'),
      field('نبذة عنك', f.bio, 'بتشتغل إزاي، بتساعد مين، وإيه اللي الشخص يتوقعه في أول جلسة. سيب سطر فاضي بين الفقرات.'),
      el('h2', { text: 'كلمة مني' }),
      el('p', { class: 'tp-small tp-muted', text: 'رسالة قصيرة منك للزائر بخط إيدك. بتخلي الصفحة شخصية جداً.' }),
      notePrev, noteUp[0], noteUp[1],
      field('نص الرسالة', f.note_text, 'اكتب نفس الكلام اللي في الصورة، عشان اللي مش قادر يقرا الخط أو بيستخدم قارئ شاشة.'),
      el('h2', { text: 'الشهادات والترخيص' }), el('p', { class: 'tp-small tp-muted', text: 'اكتب بس الحاجات الحقيقية اللي تقدر تثبتها.' }), creds,
      el('h2', { text: 'الكورسات والتدريب' }), courses,
      el('h2', { text: 'مقالاتك' }), arts,
      el('h2', { text: 'فيديوهاتك' }), el('p', { class: 'tp-small tp-muted', text: 'ارفع الفيديو على قناتك على يوتيوب وحط الرابط هنا، وهيشتغل جوه صفحتك.' }), vids,
      el('h2', { text: 'كتاب غيّر في حياتي' }),
      field('اسم الكتاب', f.book_title), field('المؤلف', f.book_author),
      field('ليه الكتاب ده؟', f.book_why, 'سطرين أو تلاتة: غيّر فيك إيه، ومين ممكن يستفيد منه.'),
      el('h2', { text: 'الجلسات والحجز' }), prices,
      field('طريقة الجلسة', f.session_mode, 'مثلاً: فيديو أو صوت'),
      field('المواعيد المتاحة', f.schedule, 'الأيام والساعات، واكتب التوقيت'),
      field('سياسة الإلغاء', f.cancel_policy, 'مثلاً: قبل الميعاد بـ ٢٤ ساعة'),
      field('رقم الواتساب للحجز', f.whatsapp, 'بكود الدولة ومن غير + أو مسافات، مثلاً 2010xxxxxxxx'),
      el('h2', { text: 'التعليقات' }),
      el('label', { class: 'dash-check', for: 'p-comments' }, [comments, ' اسمح للناس يعلّقوا على بوستاتي (التعليق مش هيظهر غير لما أوافق عليه)']),
      save, status
    ]);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var wa = f.whatsapp.value.replace(/[^0-9]/g, '');
      var badUrl = arts.read().concat(vids.read()).some(function (x) { return x.url && !TP.safeUrl(x.url); });
      if (badUrl) { status.textContent = 'فيه رابط مش صحيح. الروابط لازم تبدأ بـ https://'; return; }
      var badVid = vids.read().some(function (x) { return x.url && !TP.youtubeId(x.url); });
      if (badVid) { status.textContent = 'رابط الفيديو لازم يكون من يوتيوب.'; return; }
      var update = {
        name: f.name.value.trim(), title: f.title.value.trim() || 'معالج نفسي',
        specialties: splitList(f.specialties.value).slice(0, 8), experience: f.experience.value.trim(),
        languages: splitList(f.languages.value).slice(0, 6), bio: f.bio.value.trim(),
        credentials: creds.read(), courses: courses.read(), articles: arts.read(), videos: vids.read(), sessions: prices.read(),
        session_mode: f.session_mode.value.trim(), schedule: f.schedule.value.trim(), cancel_policy: f.cancel_policy.value.trim(),
        whatsapp: wa, comments_enabled: comments.checked,
        book_title: f.book_title.value.trim(), book_author: f.book_author.value.trim(), book_why: f.book_why.value.trim(),
        note_text: f.note_text.value.trim()
      };
      save.disabled = true; status.textContent = 'بيحفظ…';
      db.from('therapists').update(update).eq('id', me.id).select(COLS).single().then(function (r) {
        save.disabled = false;
        if (r.error) { status.textContent = 'التعديلات ماتحفظتش. اتأكد إن مفيش خانة طويلة زيادة وجرّب تاني.'; return; }
        me = r.data; status.textContent = 'اتحفظ! التعديلات ظاهرة على صفحتك دلوقتي.';
      });
    });
    body.appendChild(form);
  }

  /* ---------- posts ---------- */
  function postsView(body) {
    var title = input('n-title', '', { maxlength: 200 });
    var text = area('n-body', '', { maxlength: 8000, rows: 6 });
    var video = input('n-video', '', { type: 'url', dir: 'ltr' });
    var status = msg('');
    var btn = el('button', { type: 'submit', class: 'tp-btn', text: 'انشر' });
    var form = el('form', { class: 'dash-card', novalidate: true }, [
      el('h2', { text: 'بوست جديد' }),
      field('العنوان (اختياري)', title), field('الموضوع', text, 'سيب سطر فاضي بين الفقرات.'),
      field('رابط فيديو يوتيوب (اختياري)', video), btn, status
    ]);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var b = text.value.trim(), v = video.value.trim();
      if (!b) { status.textContent = 'اكتب الموضوع الأول.'; return; }
      if (v && !TP.youtubeId(v)) { status.textContent = 'رابط الفيديو لازم يكون من يوتيوب.'; return; }
      btn.disabled = true; status.textContent = 'بينشر…';
      db.from('posts').insert({ therapist_id: me.id, title: title.value.trim(), body: b, video_url: v }).then(function (r) {
        btn.disabled = false;
        if (r.error) { status.textContent = 'البوست ماتنشرش. جرّب تاني.'; return; }
        title.value = ''; text.value = ''; video.value = '';
        status.textContent = 'اتنشر على صفحتك.';
        loadPosts();
      });
    });
    var listWrap = el('div', { class: 'dash-card' }, [el('h2', { text: 'بوستاتك' })]);
    var list = el('div');
    listWrap.appendChild(list);
    function loadPosts() {
      list.textContent = 'بيحمّل…';
      db.from('posts').select('id,title,body,video_url,created_at').eq('therapist_id', me.id).order('created_at', { ascending: false }).then(function (r) {
        list.textContent = '';
        if (r.error) { list.appendChild(msg('مش قادر أحمّل البوستات.', 'err')); return; }
        if (!r.data.length) { list.appendChild(msg('لسه مانزلتش بوستات.')); return; }
        r.data.forEach(function (p) { list.appendChild(postItem(p, loadPosts)); });
      });
    }
    body.appendChild(form); body.appendChild(listWrap);
    loadPosts();
  }

  function postItem(p, reload) {
    var box = el('div', { class: 'dash-post' });
    function view() {
      box.textContent = '';
      box.appendChild(el('b', { text: p.title || '(من غير عنوان)' }));
      box.appendChild(el('div', { class: 'tp-small tp-muted', text: TP.date(p.created_at) }));
      box.appendChild(el('p', { class: 'dash-clip', text: p.body }));
      var confirmDel = el('span', { class: 'dash-confirm', hidden: true }, [
        'متأكد؟ ',
        el('button', { type: 'button', class: 'dash-link dash-danger', text: 'أيوه، امسح', onclick: function () {
          db.from('posts').delete().eq('id', p.id).then(function () { reload(); });
        } }),
        el('button', { type: 'button', class: 'dash-link', text: 'لأ', onclick: function () { confirmDel.hidden = true; } })
      ]);
      box.appendChild(el('div', { class: 'dash-actions' }, [
        el('button', { type: 'button', class: 'dash-link', text: 'عدّل', onclick: edit }),
        el('button', { type: 'button', class: 'dash-link dash-danger', text: 'امسح', onclick: function () { confirmDel.hidden = false; } }),
        confirmDel
      ]));
    }
    function edit() {
      box.textContent = '';
      var t = input('e-t-' + p.id, p.title, { maxlength: 200 });
      var b = area('e-b-' + p.id, p.body, { maxlength: 8000, rows: 6 });
      var v = input('e-v-' + p.id, p.video_url, { type: 'url', dir: 'ltr' });
      var s = msg('');
      box.appendChild(field('العنوان', t)); box.appendChild(field('الموضوع', b)); box.appendChild(field('رابط يوتيوب', v));
      box.appendChild(el('div', { class: 'dash-actions' }, [
        el('button', { type: 'button', class: 'tp-btn tp-btn-sm', text: 'احفظ', onclick: function () {
          if (!b.value.trim()) { s.textContent = 'الموضوع مايبقاش فاضي.'; return; }
          if (v.value.trim() && !TP.youtubeId(v.value)) { s.textContent = 'رابط الفيديو لازم يكون من يوتيوب.'; return; }
          db.from('posts').update({ title: t.value.trim(), body: b.value.trim(), video_url: v.value.trim() }).eq('id', p.id).select().single().then(function (r) {
            if (r.error) { s.textContent = 'ماتحفظش. جرّب تاني.'; return; }
            p = r.data; view();
          });
        } }),
        el('button', { type: 'button', class: 'dash-link', text: 'إلغاء', onclick: view })
      ]));
      box.appendChild(s);
    }
    view();
    return box;
  }

  /* ---------- comments ---------- */
  function commentsView(body) {
    var card = el('div', { class: 'dash-card' }, [
      el('h2', { text: 'التعليقات' }),
      el('p', { class: 'tp-small tp-muted', text: me.comments_enabled
        ? 'التعليقات الجديدة مش بتظهر للناس غير لما توافق عليها.'
        : 'التعليقات مقفولة على صفحتك. تقدر تفتحها من «صفحتي».' }),
      el('p', { class: 'dash-msg dash-warn', text: 'لو حد كتب إنه في خطر أو بيفكر يأذي نفسه، متوافقش على التعليق علناً. تواصل معاه بشكل خاص لو ممكن، ووجّهه لخط الطوارئ.' })
    ]);
    var list = el('div');
    card.appendChild(list);
    body.appendChild(card);
    list.textContent = 'بيحمّل…';
    db.from('posts').select('id,title').eq('therapist_id', me.id).then(function (pr) {
      var posts = (pr && pr.data) || [];
      if (!posts.length) { list.textContent = ''; list.appendChild(msg('مفيش بوستات لسه، فمفيش تعليقات.')); return; }
      var titles = {};
      posts.forEach(function (p) { titles[p.id] = p.title || '(بوست من غير عنوان)'; });
      db.from('comments').select('id,post_id,author_name,body,status,reply,created_at').in('post_id', posts.map(function (p) { return p.id; }))
        .order('created_at', { ascending: false }).limit(200).then(function (r) {
          list.textContent = '';
          if (r.error) { list.appendChild(msg('مش قادر أحمّل التعليقات.', 'err')); return; }
          var groups = { pending: [], approved: [], rejected: [] };
          r.data.forEach(function (c) { (groups[c.status] || groups.pending).push(c); });
          [['pending', 'مستني موافقتك'], ['approved', 'ظاهر للناس'], ['rejected', 'مرفوض']].forEach(function (g) {
            if (!groups[g[0]].length && g[0] !== 'pending') return;
            list.appendChild(el('h3', { text: g[1] + ' (' + groups[g[0]].length + ')' }));
            if (!groups[g[0]].length) list.appendChild(msg('مفيش تعليقات جديدة.'));
            groups[g[0]].forEach(function (c) { list.appendChild(commentItem(c, titles[c.post_id])); });
          });
        });
    });
  }

  function commentItem(c, postTitle) {
    var box = el('div', { class: 'dash-comment dash-' + c.status });
    var reply = area('r-' + c.id, c.reply, { maxlength: 1500, rows: 2, placeholder: 'ردك (اختياري، هيظهر تحت التعليق)' });
    var s = msg('');
    function set(update) {
      db.from('comments').update(update).eq('id', c.id).select().single().then(function (r) {
        if (r.error) { s.textContent = 'ماتحفظش. جرّب تاني.'; return; }
        c = r.data; s.textContent = c.status === 'approved' ? 'ظاهر على صفحتك.' : c.status === 'rejected' ? 'اترفض ومش هيظهر.' : 'اتحفظ.';
        box.className = 'dash-comment dash-' + c.status;
      });
    }
    box.appendChild(el('div', { class: 'tp-small tp-muted', text: 'على: ' + postTitle + ' · ' + TP.date(c.created_at) }));
    box.appendChild(el('b', { text: c.author_name }));
    box.appendChild(el('p', { text: c.body }));
    box.appendChild(field('ردك', reply));
    box.appendChild(el('div', { class: 'dash-actions' }, [
      el('button', { type: 'button', class: 'tp-btn tp-btn-sm', text: 'وافق وانشر', onclick: function () { set({ status: 'approved', reply: reply.value.trim() }); } }),
      el('button', { type: 'button', class: 'dash-link', text: 'احفظ الرد بس', onclick: function () { set({ reply: reply.value.trim() }); } }),
      el('button', { type: 'button', class: 'dash-link dash-danger', text: 'ارفض', onclick: function () { set({ status: 'rejected' }); } })
    ]));
    box.appendChild(s);
    return box;
  }

  /* ---------- start ---------- */
  // A used or expired email link comes back with #error_code=... in the address.
  var linkNote = '';
  var h = location.hash || '';
  if (/error_code=otp_expired|error=access_denied/.test(h)) {
    linkNote = 'اللينك ده اتستخدم قبل كده أو خلص (كل لينك بيشتغل مرة واحدة بس). اطلب لينك جديد من هنا.';
  } else if (/error/.test(h)) {
    linkNote = 'اللينك ماشتغلش. اطلب لينك جديد من هنا.';
  }

  var started = false;
  function route(session) {
    if (session) { if (!started) { started = true; load(); } }
    else { started = false; me = null; loginView(linkNote); linkNote = ''; }
  }
  db.auth.getSession().then(function (r) {
    // Only after the library has read the address: drop a leftover error from it.
    if (/error/.test(location.hash || '')) {
      try { history.replaceState(null, '', location.pathname); } catch (e) {}
    }
    route(r.data && r.data.session);
  });
  db.auth.onAuthStateChange(function (event, session) {
    if (event === 'SIGNED_IN') route(session);
    if (event === 'SIGNED_OUT') { me = null; started = false; }
  });
})();
