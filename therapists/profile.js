/* Live therapist profile: reads the therapist's own data, posts and approved comments
   from Supabase and replaces the static fallback built by tools/build_therapists.py. */
(function () {
  'use strict';
  var TP = window.TP;
  if (!TP || !TP.client) return;
  var el = TP.el, db = TP.client;
  var slug = (location.pathname.match(/\/therapists\/([a-z0-9-]+)\/?$/) || [])[1];
  var isView = slug === 'view';
  if (isView) {
    try { slug = new URLSearchParams(location.search).get('d') || ''; } catch (e) { slug = ''; }
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) slug = '';
  }
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
      el('div', { class: 'tp-related-slot' }),
      t.comments_enabled ? el('details', { class: 'tp-cdetails' }, [el('summary', { text: 'علّق على الموضوع ده' }), commentForm(p, t)]) : null
    ]);
  }

  function noteBlock(t) {
    var img = TP.photoUrl(t.note_path);
    if (!img && !t.note_text) return null;
    return el('section', { class: 'tp-block tp-note' }, [
      el('h2', { text: 'كلمة مني' }),
      img ? el('img', { class: 'tp-note-img', src: img, alt: t.note_text ? ('رسالة بخط ' + (t.name || 'المعالج') + ': ' + t.note_text) : ('رسالة بخط ' + (t.name || 'المعالج')), loading: 'lazy' }) : null,
      !img && t.note_text ? el('p', { class: 'tp-note-text', text: t.note_text }) : null,
      el('p', { class: 'tp-small tp-muted tp-sign', text: '— ' + (t.name || '') })
    ]);
  }

  function bookBlock(t) {
    if (!t.book_title) return null;
    return el('section', { class: 'tp-block tp-book-pick' }, [
      el('h2', { text: 'كتاب غيّر في حياتي' }),
      el('div', { class: 'tp-bookcard' }, [
        el('div', { class: 'tp-bookspine', 'aria-hidden': 'true' }),
        el('div', null, [
          el('b', { class: 'tp-booktitle', text: t.book_title }),
          t.book_author ? el('div', { class: 'tp-small tp-muted', text: t.book_author }) : null
        ])
      ]),
      t.book_why ? el('p', { text: t.book_why }) : null
    ]);
  }

  function shareBlock(t) {
    var url = location.origin + '/therapists/' + t.slug + '/';
    var msg = (t.name || '') + (t.title ? ' · ' + t.title : '') + '\n' + url;
    var status = el('span', { class: 'tp-small tp-muted', role: 'status' });
    var copy = el('button', { type: 'button', class: 'tp-share-btn', text: 'انسخ اللينك', onclick: function () {
      var done = function () { status.textContent = 'اتنسخ.'; };
      try {
        navigator.clipboard.writeText(url).then(done, function () { status.textContent = url; });
      } catch (e) { status.textContent = url; }
    } });
    var native = (navigator.share ? el('button', { type: 'button', class: 'tp-share-btn', text: 'مشاركة', onclick: function () {
      navigator.share({ title: t.name || '', text: t.title || '', url: url }).catch(function () {});
    } }) : null);
    return el('section', { class: 'tp-block tp-share' }, [
      el('h2', { text: 'شارك الصفحة' }),
      el('p', { class: 'tp-small tp-muted', text: 'لو تعرف حد ممكن يستفيد، ابعتله الصفحة.' }),
      el('div', { class: 'tp-share-row' }, [
        el('a', { class: 'tp-share-btn tp-wa', target: '_blank', rel: 'noopener', href: 'https://wa.me/?text=' + encodeURIComponent(msg), text: 'واتساب' }),
        el('a', { class: 'tp-share-btn tp-fb', target: '_blank', rel: 'noopener', href: 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url), text: 'فيسبوك' }),
        native, copy
      ]),
      status
    ]);
  }

  // «مقالات ممكن تفيدك»: match a post's words against the site's articles.
  var articlesPromise = null;
  function loadArticles() {
    if (!articlesPromise) {
      articlesPromise = fetch('/therapists/related-articles.json', { credentials: 'omit' })
        .then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; });
    }
    return articlesPromise;
  }
  function norm(w) {
    return w.replace(/[ً-ْـ]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
      .replace(/^(وال|بال|فال|كال|لل|ال)/, '');
  }
  var STOP = { 'اللي': 1, 'علشان': 1, 'عشان': 1, 'ازاي': 1, 'ليه': 1, 'لما': 1, 'كمان': 1, 'بس': 1, 'حاجه': 1, 'كده': 1, 'هو': 1, 'هي': 1, 'انت': 1, 'انا': 1, 'مش': 1, 'على': 1, 'علي': 1, 'من': 1, 'في': 1, 'عن': 1, 'مع': 1, 'او': 1, 'ولا': 1, 'كل': 1, 'بين': 1, 'لو': 1, 'دي': 1, 'ده': 1, 'هل': 1, 'ايه': 1, 'يعني': 1 };
  function words(text) {
    var out = {};
    String(text || '').split(/[^؀-ۿA-Za-z]+/).forEach(function (w) {
      w = norm(w);
      if (w.length >= 3 && !STOP[w]) out[w] = 1;
    });
    return out;
  }
  function related(post, t, arts) {
    var mine = words((post.title || '') + ' ' + (post.body || '') + ' ' + (t.specialties || []).join(' '));
    var scored = arts.map(function (a) {
      var aw = words(a.t + ' ' + a.k), score = 0;
      Object.keys(aw).forEach(function (w) { if (mine[w]) score += 1; });
      Object.keys(words(a.t)).forEach(function (w) { if (mine[w]) score += 2; });
      return { a: a, s: score };
    }).filter(function (x) { return x.s >= 3; }).sort(function (x, y) { return y.s - x.s; }).slice(0, 3);
    if (!scored.length) return null;
    var ul = el('ul', { class: 'tp-related' });
    scored.forEach(function (x) {
      if (/^\/articles\/[a-z0-9-]+\/$/.test(x.a.u)) ul.appendChild(el('li', null, [el('a', { href: x.a.u, text: x.a.t })]));
    });
    return ul.childNodes.length ? el('div', { class: 'tp-related-wrap' }, [el('h4', { text: 'مقالات ممكن تفيدك' }), ul]) : null;
  }

  /* ---------- tabs: عني / مقالات / فيديوهات / بوستات / احجز ---------- */
  var TABS = [['about', 'عني'], ['articles', 'مقالات'], ['videos', 'فيديوهات'], ['posts', 'بوستات'], ['book', 'احجز']];
  var params = (function () { try { return new URLSearchParams(location.search); } catch (e) { return null; } })();
  var articleId = params && params.get('a');
  if (articleId && !/^[0-9a-f-]{36}$/.test(articleId)) articleId = null;

  function pageUrl(t) { return location.origin + '/therapists/' + t.slug + '/'; }
  function articleUrl(t, a) { return pageUrl(t) + '?a=' + a.id; }

  function excerpt(body, n) {
    var txt = String(body || '').replace(/^##\s+/gm, '').replace(/\s+/g, ' ').trim();
    return txt.length > n ? txt.slice(0, n).replace(/\s+\S*$/, '') + '…' : txt;
  }

  // Article body: blank line = new paragraph, a line starting with "## " = sub-heading.
  function articleBody(body) {
    var d = el('div', { class: 'tp-prose tp-article-body' });
    String(body || '').split(/\n\s*\n/).forEach(function (chunk) {
      chunk = chunk.trim();
      if (!chunk) return;
      chunk.split('\n').forEach(function (line, i, all) {
        if (/^##\s+/.test(line)) { d.appendChild(el('h2', { text: line.replace(/^##\s+/, '') })); }
      });
      var text = chunk.split('\n').filter(function (l) { return !/^##\s+/.test(l); }).join(' ').trim();
      if (text) d.appendChild(el('p', { text: text }));
    });
    return d;
  }

  function articleCard(t, a) {
    var cover = TP.photoUrl(a.cover_path);
    return el('a', { class: 'tp-acard', href: (isView ? '?d=' + slug + '&a=' : '?a=') + a.id }, [
      cover ? el('img', { class: 'tp-acover', src: cover, alt: '', loading: 'lazy' }) : el('div', { class: 'tp-acover tp-acover-empty', 'aria-hidden': 'true' }),
      el('div', { class: 'tp-abody' }, [
        el('h3', { text: a.title }),
        el('time', { class: 'tp-small tp-muted', datetime: a.created_at, text: TP.date(a.created_at) }),
        el('p', { class: 'tp-muted', text: excerpt(a.body, 140) })
      ])
    ]);
  }

  function videoCard(v) {
    var id = TP.youtubeId(v.url);
    if (!id) return null;
    var thumb = el('button', { type: 'button', class: 'tp-vthumb', 'aria-label': 'شغّل الفيديو: ' + (v.title || '') }, [
      el('img', { src: 'https://i.ytimg.com/vi/' + id + '/hqdefault.jpg', alt: '', loading: 'lazy' }),
      el('span', { class: 'tp-vplay', 'aria-hidden': 'true', text: '▶' })
    ]);
    var fig = el('figure', { class: 'tp-vcard' }, [thumb, v.title ? el('figcaption', { text: v.title }) : null]);
    thumb.addEventListener('click', function () {
      var emb = TP.youtubeEmbed(v.url, v.title);
      if (emb) { fig.replaceChild(emb, thumb); var f = emb.querySelector('iframe'); if (f) f.src += '?autoplay=1'; }
    });
    return fig;
  }

  function allVideos(t, posts) {
    var seen = {}, out = [];
    (t.videos || []).concat(posts.filter(function (p) { return p.video_url; }).map(function (p) { return { title: p.title, url: p.video_url }; }))
      .forEach(function (v) { var id = v && TP.youtubeId(v.url); if (id && !seen[id]) { seen[id] = 1; out.push(v); } });
    return out;
  }

  function trackOnce(key, articleKey) {
    // One count per page per browser per day; a bad network never breaks the page.
    var k = 'tpv:' + key + ':' + new Date().toISOString().slice(0, 10);
    try { if (localStorage.getItem(k)) return; localStorage.setItem(k, '1'); } catch (e) { /* still count */ }
    db.rpc('track_view', { p_slug: slug, p_article: articleKey || null }).then(function () {}, function () {});
  }

  function render(t, posts, comments, arts) {
    hero.textContent = '';
    heroView(t).forEach(function (n) { hero.appendChild(n); });
    document.title = (t.name || '') + ' | ' + (t.title || 'معالج نفسي');
    main.textContent = '';
    if (t.published === false) main.appendChild(el('p', { class: 'tp-preview-note', text: 'معاينة: الصفحة دي لسه مش ظاهرة للناس. بتظهر بعد مراجعة إدارة الموقع.' }));

    // One article on its own
    if (articleId) {
      var a = arts.filter(function (x) { return x.id === articleId; })[0];
      if (a) { renderArticle(t, a); trackOnce('a' + a.id, a.id); return; }
    }

    var byPost = {};
    comments.forEach(function (c) { (byPost[c.post_id] = byPost[c.post_id] || []).push(c); });
    var vids = allVideos(t, posts);

    var panes = {};
    panes.about = [facts(t), noteBlock(t), block('نبذة', bio(t)), bookBlock(t),
      block('الشهادات والمؤهلات', list(t.credentials, 'cred')), block('الكورسات والتدريب', list(t.courses, 'cred')),
      block('مقالات في أماكن تانية', list(t.articles, 'article'))];
    var agrid = el('div', { class: 'tp-agrid' });
    arts.forEach(function (x) { agrid.appendChild(articleCard(t, x)); });
    panes.articles = [agrid.childNodes.length ? agrid : el('p', { class: 'tp-block tp-muted', text: 'لسه مفيش مقالات.' })];
    var vgrid = el('div', { class: 'tp-vgrid' });
    vids.forEach(function (v) { var c = videoCard(v); if (c) vgrid.appendChild(c); });
    panes.videos = [vgrid.childNodes.length ? vgrid : el('p', { class: 'tp-block tp-muted', text: 'لسه مفيش فيديوهات.' })];
    var postsWrap = el('div', { class: 'tp-posts tp-block' });
    posts.forEach(function (p) { postsWrap.appendChild(postView(p, byPost[p.id] || [], t)); });
    panes.posts = [posts.length ? postsWrap : el('p', { class: 'tp-block tp-muted', text: 'لسه مفيش بوستات.' })];
    panes.book = [booking(t), shareBlock(t)];

    var counts = { articles: arts.length, videos: vids.length, posts: posts.length };
    var nav = el('nav', { class: 'tp-tabs', 'aria-label': 'أقسام الصفحة' });
    var paneEls = {};
    TABS.forEach(function (x) {
      var key = x[0];
      if (counts[key] === 0 && key !== 'articles') return; // hide empty videos/posts tabs
      if (key === 'articles' && !counts.articles) return;
      nav.appendChild(el('a', { class: 'tp-tab', href: '#' + key, 'data-tab': key }, [x[1], counts[key] ? el('span', { class: 'tp-count', text: String(counts[key]) }) : null]));
      var pane = el('section', { class: 'tp-pane', id: key, 'data-pane': key });
      panes[key].forEach(function (n) { if (n) pane.appendChild(n); });
      paneEls[key] = pane;
    });
    main.appendChild(nav);
    Object.keys(paneEls).forEach(function (k) { main.appendChild(paneEls[k]); });
    main.appendChild(el('p', { class: 'tp-urgent', text: 'لو أنت أو حد قريبك في خطر فوري، متستناش جلسة ولا رد على تعليق: اتصل بالطوارئ (في مصر ١٢٣) أو خط الصحة النفسية ١٦٣٢٨، أو اتوجه لأقرب مستشفى.' }));

    function show(key, scroll) {
      if (!paneEls[key]) key = 'about';
      Object.keys(paneEls).forEach(function (k) { paneEls[k].hidden = k !== key; });
      nav.querySelectorAll('.tp-tab').forEach(function (a) {
        var on = a.getAttribute('data-tab') === key;
        a.classList.toggle('is-on', on);
        if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
      });
      if (scroll) nav.scrollIntoView({ block: 'start' });
    }
    var first = (location.hash || '').slice(1);
    show(first, !!paneEls[first] && first !== 'about');
    window.addEventListener('hashchange', function () { show((location.hash || '').slice(1), true); });

    if (posts.length) {
      loadArticles().then(function (sa) {
        if (!sa || !sa.length) return;
        posts.forEach(function (p) {
          var slot = document.querySelector('#post-' + p.id + ' .tp-related-slot');
          var r = slot && related(p, t, sa);
          if (r) slot.appendChild(r);
        });
      });
    }
    trackOnce('p', null);
  }

  function renderArticle(t, a) {
    var url = articleUrl(t, a);
    var cover = TP.photoUrl(a.cover_path);
    document.title = a.title + ' | ' + (t.name || '');
    var status = el('span', { class: 'tp-small tp-muted', role: 'status' });
    var art = el('article', { class: 'tp-block tp-article' }, [
      el('a', { class: 'tp-back', href: location.pathname + (isView ? location.search.replace(/[?&]a=[^&]*/, '') : '') + '#articles', text: '← كل مقالات ' + (t.name || '') }),
      el('h1', { class: 'tp-atitle', text: a.title }),
      el('p', { class: 'tp-small tp-muted' }, [(t.name || '') + ' · ', el('time', { datetime: a.created_at, text: TP.date(a.created_at) })]),
      cover ? el('img', { class: 'tp-acover-big', src: cover, alt: '' }) : null,
      articleBody(a.body),
      el('div', { class: 'tp-related-slot' }),
      el('div', { class: 'tp-share-row' }, [
        el('a', { class: 'tp-share-btn tp-wa', target: '_blank', rel: 'noopener', href: 'https://wa.me/?text=' + encodeURIComponent(a.title + '\n' + url), text: 'شارك على واتساب' }),
        el('a', { class: 'tp-share-btn tp-fb', target: '_blank', rel: 'noopener', href: 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url), text: 'فيسبوك' }),
        el('button', { type: 'button', class: 'tp-share-btn', text: 'انسخ اللينك', onclick: function () {
          try { navigator.clipboard.writeText(url).then(function () { status.textContent = 'اتنسخ.'; }, function () { status.textContent = url; }); } catch (e) { status.textContent = url; }
        } }),
        status
      ]),
      el('a', { class: 'tp-btn', href: location.pathname + (isView ? location.search.replace(/[?&]a=[^&]*/, '') : '') + '#book', text: 'احجز جلسة مع ' + (t.name || '') })
    ]);
    main.appendChild(art);
    main.appendChild(el('p', { class: 'tp-urgent', text: 'المقال للتوعية ومش بديل عن جلسة. لو أنت أو حد قريبك في خطر فوري، اتصل بالطوارئ (في مصر ١٢٣) أو خط الصحة النفسية ١٦٣٢٨.' }));
    loadArticles().then(function (sa) {
      var r = sa && sa.length && related({ title: a.title, body: a.body }, t, sa);
      var slot = art.querySelector('.tp-related-slot');
      if (r && slot) slot.appendChild(r);
    });
    window.scrollTo(0, 0);
  }

  db.from('therapists').select('id,slug,published,name,title,specialties,bio,experience,languages,credentials,courses,articles,videos,sessions,session_mode,schedule,cancel_policy,whatsapp,photo_path,comments_enabled,book_title,book_author,book_why,note_path,note_text')
    .eq('slug', slug).maybeSingle().then(function (r) {
      if (r.error || !r.data) {
        if (isView) {
          main.textContent = '';
          main.appendChild(el('p', { class: 'tp-block', text: 'الصفحة دي مش موجودة أو لسه مش منشورة. لو انت صاحبها، ادخل من لوحة المعالج وافتحها من هناك.' }));
        }
        return; // keep the static page
      }
      var t = r.data;
      Promise.all([
        db.from('posts').select('id,title,body,video_url,created_at').eq('therapist_id', t.id).order('created_at', { ascending: false }).limit(50),
        db.from('articles').select('id,title,cover_path,body,created_at').eq('therapist_id', t.id).order('created_at', { ascending: false }).limit(100)
      ]).then(function (res) {
        var posts = (res[0] && res[0].data) || [], arts = (res[1] && res[1].data) || [];
        if (!posts.length) { render(t, [], [], arts); return; }
        db.from('comments').select('id,post_id,author_name,body,reply,created_at').eq('status', 'approved')
          .in('post_id', posts.map(function (p) { return p.id; })).order('created_at', { ascending: true })
          .then(function (cr) { render(t, posts, (cr && cr.data) || [], arts); });
      });
    });
})();
