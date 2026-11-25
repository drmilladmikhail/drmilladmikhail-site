/* Live therapist profile: reads the therapist's own data, posts and approved comments
   from Supabase and replaces the static fallback built by tools/build_therapists.py. */
(function () {
  'use strict';
  var TP = window.TP;
  if (!TP || !TP.client) return;
  var el = TP.el, db = TP.client;
  var slug = (location.pathname.match(/\/therapists\/([a-z0-9-]+)\/?$/) || [])[1];
  if (!slug || slug === 'dashboard') return;

  var hero = document.getElementById('tp-hero');
  var main = document.getElementById('tp-main');
  if (!hero || !main) return;

  function list(items, kind) {
    var ul = el('ul', { class: 'tp-list' });
    (items || []).forEach(function (it) {
      if (!it) return;
      var li;
      if (kind === 'cred') {
        var meta = [it.place, it.year].filter(Boolean).join(' · ');
        li = el('li', null, [el('b', { text: it.name || '' }), meta ? el('small', { text: meta }) : null]);
      } else if (kind === 'article') {
        var u = TP.safeUrl(it.url);
        li = el('li', null, [
          el('b', null, [u ? el('a', { href: u, target: '_blank', rel: 'noopener', text: it.title || u }) : (it.title || '')]),
          it.place ? el('small', { text: it.place }) : null
        ]);
      }
      if (li) ul.appendChild(li);
    });
    return ul.childNodes.length ? ul : null;
  }

  function block(title, body, id) {
    if (!body) return null;
    return el('section', { class: 'tp-block', id: id || null }, [el('h2', { text: title }), body]);
  }

  function heroView(t) {
    var photo = TP.photoUrl(t.photo_path);
    var avatar = photo
      ? el('img', { class: 'tp-photo', src: photo, alt: 'صورة ' + (t.name || ''), width: 160, height: 160 })
      : el('div', { class: 'tp-photo tp-initial', 'aria-hidden': 'true', text: TP.initial(t.name) });
    var tags = el('ul', { class: 'tp-tags' });
    (t.specialties || []).forEach(function (s) { tags.appendChild(el('li', { text: s })); });
    return [avatar, el('div', { class: 'tp-id' }, [
      el('h1', { text: t.name || '' }),
      el('p', { class: 'tp-title', text: t.title || 'معالج نفسي' }),
      tags,
      el('a', { class: 'tp-btn', href: '#book', text: 'احجز جلسة' })
    ])];
  }

  function facts(t) {
    var ul = el('ul', { class: 'tp-facts' });
    if (t.experience) ul.appendChild(el('li', null, [el('span', { text: 'الخبرة' }), el('b', { text: t.experience })]));
    if ((t.languages || []).length) ul.appendChild(el('li', null, [el('span', { text: 'اللغات' }), el('b', { text: t.languages.join('، ') })]));
    if (t.session_mode) ul.appendChild(el('li', null, [el('span', { text: 'الجلسة' }), el('b', { text: 'أونلاين · ' + t.session_mode })]));
    return ul;
  }

  function videos(t) {
    var wrap = el('div', { class: 'tp-videos' });
    (t.videos || []).forEach(function (v) {
      var e = v && TP.youtubeEmbed(v.url, v.title);
      if (e) wrap.appendChild(el('figure', null, [e, v.title ? el('figcaption', { text: v.title }) : null]));
    });
    return wrap.childNodes.length ? wrap : null;
  }

  function bio(t) {
    var parts = String(t.bio || '').split(/\n{2,}|\r\n\r\n/).map(function (s) { return s.trim(); }).filter(Boolean);
    if (!parts.length) return null;
    var d = el('div', { class: 'tp-prose' });
    parts.forEach(function (p) { d.appendChild(el('p', { text: p })); });
    return d;
  }

  function booking(t) {
    var prices = el('ul', { class: 'tp-prices' });
    (t.sessions || []).forEach(function (s) {
      if (s && (s.length || s.price)) prices.appendChild(el('li', null, [el('span', { text: s.length || '' }), el('b', { text: s.price || '' })]));
    });
    var wa = String(t.whatsapp || '').replace(/[^0-9]/g, '');
    var cta = wa
      ? el('a', { class: 'tp-btn', target: '_blank', rel: 'noopener',
          href: 'https://wa.me/' + wa + '?text=' + encodeURIComponent('أهلاً ' + (t.name || '') + '، حابب أحجز جلسة. شفت صفحتك: ' + location.href.split('#')[0]),
          text: 'احجز على واتساب' })
      : el('p', { class: 'tp-muted', text: 'الحجز هيتفعل أول ما رقم الحجز يتضاف.' });
    return el('section', { class: 'tp-block tp-book', id: 'book' }, [
      el('h2', { text: 'احجز جلسة مع ' + (t.name || '') }),
      prices.childNodes.length ? prices : null,
      t.schedule ? el('p', { class: 'tp-muted', text: 'المواعيد: ' + t.schedule }) : null,
      t.cancel_policy ? el('p', { class: 'tp-muted', text: 'الإلغاء أو التعديل: ' + t.cancel_policy }) : null,
      cta,
      el('p', { class: 'tp-muted tp-small', text: 'الجلسات سرّية. بياناتك بتتستخدم للحجز والتواصل بس.' })
    ]);
  }

  function commentForm(post, t) {
    var status = el('p', { class: 'tp-small tp-muted', role: 'status' });
    var name = el('input', { type: 'text', maxlength: 60, required: true, id: 'c-name-' + post.id, autocomplete: 'nickname' });
    var body = el('textarea', { maxlength: 1500, required: true, rows: 3, id: 'c-body-' + post.id });
    var btn = el('button', { class: 'tp-btn tp-btn-sm', type: 'submit', text: 'ابعت تعليقك' });
    var form = el('form', { class: 'tp-cform', novalidate: true }, [
      el('label', { for: 'c-name-' + post.id, text: 'اسمك (أو اسم مستعار)' }), name,
      el('label', { for: 'c-body-' + post.id, text: 'تعليقك' }), body,
      el('p', { class: 'tp-small tp-muted', text: 'تعليقك هيظهر للناس بعد ما ' + (t.name || 'المعالج') + ' يوافق عليه. متكتبش رقم تليفون أو تفاصيل شخصية تعرّف بيك. التعليق مش بديل عن جلسة.' }),
      btn, status
    ]);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var n = name.value.trim(), b = body.value.trim();
      if (!n || !b) { status.textContent = 'اكتب اسمك وتعليقك الأول.'; return; }
      btn.disabled = true; status.textContent = 'بيتبعت…';
      db.from('comments').insert({ post_id: post.id, author_name: n, body: b }).then(function (r) {
        btn.disabled = false;
        if (r.error) { status.textContent = 'التعليق ماتبعتش. جرّب تاني بعد شوية.'; return; }
        body.value = '';
        status.textContent = 'وصل تعليقك، وهيظهر بعد المراجعة.';
      });
    });
    return form;
  }

  function postView(p, comments, t) {
    var bodyEl = el('div', { class: 'tp-prose' });
    String(p.body || '').split(/\n{2,}/).forEach(function (para) {
      para = para.trim();
      if (para) bodyEl.appendChild(el('p', { text: para }));
    });
    var cl = el('ul', { class: 'tp-comments' });
    comments.forEach(function (c) {
      cl.appendChild(el('li', null, [
        el('b', { text: c.author_name }), el('p', { text: c.body }),
        c.reply ? el('div', { class: 'tp-reply' }, [el('b', { text: 'رد ' + (t.name || 'المعالج') }), el('p', { text: c.reply })]) : null
      ]));
    });
    return el('article', { class: 'tp-post', id: 'post-' + p.id }, [
      p.title ? el('h3', { text: p.title }) : null,
      el('time', { class: 'tp-small tp-muted', datetime: p.created_at, text: TP.date(p.created_at) }),
      bodyEl,
      TP.youtubeEmbed(p.video_url, p.title),
      cl.childNodes.length ? el('div', null, [el('h4', { text: 'التعليقات' }), cl]) : null,
      t.comments_enabled ? el('details', { class: 'tp-cdetails' }, [el('summary', { text: 'علّق على الموضوع ده' }), commentForm(p, t)]) : null
    ]);
  }

  function render(t, posts, comments) {
    hero.textContent = '';
    heroView(t).forEach(function (n) { hero.appendChild(n); });
    document.title = (t.name || '') + ' | ' + (t.title || 'معالج نفسي');

    var byPost = {};
    comments.forEach(function (c) { (byPost[c.post_id] = byPost[c.post_id] || []).push(c); });
    var postsWrap = el('div', { class: 'tp-posts' });
    posts.forEach(function (p) { postsWrap.appendChild(postView(p, byPost[p.id] || [], t)); });

    var nodes = [
      facts(t),
      block('نبذة', bio(t)),
      block('مواضيع وبوستات', postsWrap.childNodes.length ? postsWrap : null, 'posts'),
      block('فيديوهات', videos(t)),
      block('الشهادات والمؤهلات', list(t.credentials, 'cred')),
      block('الكورسات والتدريب', list(t.courses, 'cred')),
      block('مقالات', list(t.articles, 'article')),
      booking(t),
      el('p', { class: 'tp-urgent', text: 'لو أنت أو حد قريبك في خطر فوري، متستناش جلسة ولا رد على تعليق: اتصل بالطوارئ (في مصر ١٢٣) أو خط الصحة النفسية ١٦٣٢٨، أو اتوجه لأقرب مستشفى.' })
    ];
    main.textContent = '';
    nodes.forEach(function (n) { if (n) main.appendChild(n); });
    if (location.hash) {
      var target = document.getElementById(location.hash.slice(1));
      if (target) target.scrollIntoView();
    }
  }

  db.from('therapists').select('id,slug,name,title,specialties,bio,experience,languages,credentials,courses,articles,videos,sessions,session_mode,schedule,cancel_policy,whatsapp,photo_path,comments_enabled')
    .eq('slug', slug).maybeSingle().then(function (r) {
      if (r.error || !r.data) return; // keep the static page
      var t = r.data;
      db.from('posts').select('id,title,body,video_url,created_at').eq('therapist_id', t.id)
        .order('created_at', { ascending: false }).limit(50).then(function (pr) {
          var posts = (pr && pr.data) || [];
          if (!posts.length) { render(t, [], []); return; }
          db.from('comments').select('id,post_id,author_name,body,reply,created_at').eq('status', 'approved')
            .in('post_id', posts.map(function (p) { return p.id; })).order('created_at', { ascending: true })
            .then(function (cr) { render(t, posts, (cr && cr.data) || []); });
        });
    });
})();
