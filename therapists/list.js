/* «اختار المعالج»: every published therapist as a card (site owner first).
   Used on /sessions/ and /therapists/. Replaces the static fallback card inside #tp-list. */
(function () {
  'use strict';
  var TP = window.TP;
  var box = document.getElementById('tp-list');
  if (!TP || !TP.client || !box) return;
  var el = TP.el, db = TP.client;
  var FIRST = 'millad-mikhail';

  function card(t) {
    var photo = TP.photoUrl(t.photo_path);
    var profile = '/therapists/' + t.slug + '/';
    var wa = String(t.whatsapp || '').replace(/[^0-9]/g, '');
    var price = (t.sessions || []).filter(function (s) { return s && s.price; })[0];
    var tags = el('ul', { class: 'tl-tags' });
    (t.specialties || []).slice(0, 4).forEach(function (s) { tags.appendChild(el('li', { text: s })); });
    var msg = 'أهلًا ' + (t.name || '') + '، أنا جاي من الموقع وعايز أحجز جلسة نفسية أونلاين. أنا مقيم في: ';
    return el('article', { class: 'tl-card' }, [
      el('a', { class: 'tl-head', href: profile }, [
        photo ? el('img', { class: 'tl-photo', src: photo, alt: '', width: 72, height: 72, loading: 'lazy' })
              : el('span', { class: 'tl-photo tl-initial', 'aria-hidden': 'true', text: TP.initial(t.name) }),
        el('span', { class: 'tl-id' }, [el('b', { class: 'tl-name', text: t.name || '' }), el('span', { class: 'tl-title', text: t.title || 'معالج نفسي' })])
      ]),
      tags.childNodes.length ? tags : null,
      price ? el('p', { class: 'tl-price' }, [el('span', { text: 'الجلسة' }), el('b', { text: (price.length ? price.length + ' · ' : '') + price.price })]) : null,
      el('div', { class: 'tl-actions' }, [
        wa ? el('a', { class: 'tl-btn tl-primary', href: 'https://wa.me/' + wa + '?text=' + encodeURIComponent(msg), target: '_blank', rel: 'noopener', text: 'احجز على واتساب' }) : null,
        el('a', { class: 'tl-btn', href: profile, text: 'البروفايل' })
      ])
    ]);
  }

  db.from('therapists').select('slug,name,title,specialties,photo_path,sessions,whatsapp,created_at')
    .eq('published', true).order('created_at', { ascending: true }).then(function (r) {
      if (r.error || !r.data || !r.data.length) return; // keep the static card
      var rows = r.data.slice().sort(function (a, b) { return (b.slug === FIRST) - (a.slug === FIRST); });
      box.textContent = '';
      rows.forEach(function (t) { box.appendChild(card(t)); });
    });
})();
