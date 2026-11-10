// /exercise/, /stories/, /shelf/ — runs only in the browser. Notes and ratings stay on this device (localStorage).
(function () {
  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); return true; } catch (e) { return v === undefined ? null : false; }
  }
  var WA = 'https://wa.me/12012758490?text=';

  // ---------- weekly exercise ----------
  var ex = document.querySelector('[data-start][data-count]');
  if (ex) {
    var arts = document.querySelectorAll('.ex');
    var start = new Date(ex.dataset.start + 'T00:00:00');
    var week = Math.max(0, Math.floor((Date.now() - start.getTime()) / (7 * 864e5)));
    var current = week % arts.length;
    function show(n, scroll) {
      arts.forEach(function (a) {
        var on = +a.dataset.n === n;
        a.hidden = !on;
        var w = a.querySelector('.ex-when');
        if (w) w.textContent = +a.dataset.n === current ? 'تمرين الأسبوع ده' : 'تمرين من الأرشيف';
      });
      document.dispatchEvent(new Event('exercisechange'));
      if (scroll) arts[n].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    var fromHash = -1;
    arts.forEach(function (a) { if ('#' + a.id === location.hash) fromHash = +a.dataset.n; });
    show(fromHash >= 0 ? fromHash : current, false);
    window.addEventListener('hashchange', function () {
      arts.forEach(function (a) { if ('#' + a.id === location.hash) show(+a.dataset.n, true); });
    });
    document.querySelectorAll('.ex-archive a').forEach(function (l) {
      l.addEventListener('click', function (e) {
        if (e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        e.preventDefault(); history.replaceState(null, '', l.getAttribute('href')); show(+l.dataset.n, true);
      });
    });

    document.querySelectorAll('.journal').forEach(function (f) {
      var key = 'journal:' + f.dataset.slug, saved = f.querySelector('.jr-saved');
      var areas = f.querySelectorAll('textarea');
      try {
        var data = JSON.parse(store(key) || '{}');
        if (data && typeof data === 'object' && !Array.isArray(data)) {
          areas.forEach(function (t) { if (typeof data[t.dataset.k] === 'string') t.value = data[t.dataset.k]; });
        }
      } catch (e) {}
      var timer = null;
      function persist() {
        clearTimeout(timer); timer = null;
        var d = {}; areas.forEach(function (t) { d[t.dataset.k] = t.value; });
        saved.textContent = store(key, JSON.stringify(d))
          ? 'اتحفظ على جهازك ✓'
          : 'تعذّر حفظ التغييرات. نزّل اللي كتبته كملف قبل ما تقفل الصفحة.';
      }
      f.addEventListener('input', function () {
        clearTimeout(timer);
        saved.textContent = 'جاري الحفظ…';
        timer = setTimeout(persist, 400);
      });
      window.addEventListener('pagehide', function () { if (timer !== null) persist(); });
      document.addEventListener('visibilitychange', function () { if (document.hidden && timer !== null) persist(); });
      f.querySelector('.jr-dl').addEventListener('click', function () {
        var art = f.closest('.ex'), title = art.querySelector('h2').textContent;
        var txt = title + '\n' + new Date().toLocaleDateString('ar-EG') + '\n\n';
        f.querySelectorAll('.jr-field').forEach(function (l) { txt += l.querySelector('span').textContent + '\n' + l.querySelector('textarea').value + '\n\n'; });
        txt += '— تمرين الأسبوع من drmilladmikhail.com';
        var a = document.createElement('a');
        var url = URL.createObjectURL(new Blob(['﻿' + txt], { type: 'text/plain;charset=utf-8' }));
        a.href = url;
        a.download = 'tamreen-' + f.dataset.slug + '.txt';
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      });
      f.querySelector('.jr-clear').addEventListener('click', function () {
        clearTimeout(timer); timer = null;
        if (!store(key, null)) {
          saved.textContent = 'تعذّر حذف النسخة المحفوظة. كتابتك لسه موجودة؛ جرّب تاني أو راجع إعدادات المتصفح.';
          return;
        }
        areas.forEach(function (t) { t.value = ''; });
        saved.textContent = 'اتمسح.';
      });
    });

    document.querySelectorAll('.breath').forEach(function (b) {
      var go = b.querySelector('.breath-go'), word = b.querySelector('.breath-word'), circle = b.querySelector('.breath-circle');
      var t = null, rounds = 0;
      function stop() { clearTimeout(t); t = null; b.classList.remove('in', 'out'); word.textContent = rounds >= 10 ? 'برافو 🌿' : 'جاهز؟'; go.textContent = 'ابدأ التنفس معايا'; }
      function cycle() {
        if (rounds >= 10) return stop();
        b.classList.remove('out'); b.classList.add('in'); word.textContent = 'شهيق… 4';
        t = setTimeout(function () {
          b.classList.remove('in'); b.classList.add('out'); word.textContent = 'زفير… 6';
          t = setTimeout(function () { rounds++; cycle(); }, 6000);
        }, 4000);
      }
      go.addEventListener('click', function () {
        if (t) { rounds = 0; return stop(); }
        rounds = 0; go.textContent = 'وقّف'; cycle();
      });
      document.addEventListener('exercisechange', function () { if (b.closest('.ex').hidden) { rounds = 0; stop(); } });
      window.addEventListener('pagehide', function () { rounds = 0; stop(); });
      document.addEventListener('visibilitychange', function () { if (document.hidden) { rounds = 0; stop(); } });
      circle.setAttribute('aria-hidden', 'true');
    });
    ex.classList.add('exercise-enhanced');
  }

  // ---------- stories / suggestions → WhatsApp ----------
  function waForm(sel, build) {
    var f = document.querySelector(sel);
    if (!f) return;
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = build(f), err = f.querySelector('.form-err');
      if (!msg) { if (err) err.hidden = false; return; }
      if (err) err.hidden = true;
      window.open(WA + encodeURIComponent(msg), '_blank', 'noopener');
    });
  }
  waForm('.story-form', function (f) {
    var v = function (n) { return (f.elements[n].value || '').trim(); };
    if (!v('before') || !v('helped') || !f.elements.ok.checked) return '';
    return 'حكاية تعافي للموقع (موافق على النشر من غير اسمي)\nالاسم المستعار: ' + (v('alias') || 'من غير اسم') +
      '\nالموضوع: ' + v('cat') + '\n\nكنت فين وإيه اللي كان صعب:\n' + v('before') + '\n\nإيه اللي ساعدني:\n' + v('helped') +
      (v('msg') ? '\n\nرسالتي لحد في أول الطريق:\n' + v('msg') : '');
  });
  waForm('.suggest-form', function (f) {
    var v = function (n) { return (f.elements[n].value || '').trim(); };
    if (!v('title')) return '';
    return 'اقتراح لرفّ الترشيحات\nالاسم: ' + v('title') + (v('author') ? '\nالكاتب: ' + v('author') : '') + '\nتقييمي: ' + v('rate') + ' من 5' + (v('why') ? '\nفرق معايا في: ' + v('why') : '');
  });

  // ---------- shelf: topic filter + personal star rating ----------
  var chips = document.querySelectorAll('.chips .chip');
  chips.forEach(function (c) {
    c.setAttribute('aria-pressed', c.classList.contains('on') ? 'true' : 'false');
    c.addEventListener('click', function () {
      chips.forEach(function (o) { o.classList.toggle('on', o === c); o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); });
      document.querySelectorAll('.shelf .bk').forEach(function (b) { b.hidden = !!c.dataset.t && b.dataset.t !== c.dataset.t; });
    });
  });
  document.querySelectorAll('.shelf .bk').forEach(function (b) {
    var key = 'rate:' + b.dataset.id, btns = b.querySelectorAll('.star'), msg = b.querySelector('.rate-msg');
    function paint(n) { btns.forEach(function (s) { var on = +s.dataset.v <= n; s.classList.toggle('on', on); s.setAttribute('aria-pressed', on ? 'true' : 'false'); }); }
    paint(+(store(key) || 0));
    btns.forEach(function (s) {
      s.addEventListener('click', function () {
        var saved = store(key, s.dataset.v);
        paint(+s.dataset.v);
        msg.textContent = ' شكراً! تقييمك ' + s.dataset.v + ' من 5' +
          (saved ? '' : ' · للزيارة دي بس؛ تعذّر حفظه على الجهاز.');
      });
    });
  });
})();
