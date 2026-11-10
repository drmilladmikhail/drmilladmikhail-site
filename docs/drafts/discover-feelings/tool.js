// Draft: runs only in the browser. Nothing a visitor types is sent, logged, stored or put in the URL.
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var PATHS = window.DF_PATHS || {};
  var FE = window.DF_FEELINGS || [], GROUPS = window.DF_GROUPS || [], BODY = window.DF_BODY || [];
  var statusEl = $('status');
  var state = {};
  function say(t) { statusEl.textContent = ''; setTimeout(function () { statusEl.textContent = t; }, 30); }
  function ar(n) { return Number(n).toLocaleString('ar-EG'); }
  function el(tag, text, cls) { var e = document.createElement(tag); if (text) e.textContent = text; if (cls) e.className = cls; return e; }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }

  // ---------- text normalising and safety ----------
  function norm(s) {
    return String(s).toLowerCase()
      .replace(/[ً-ْـ]/g, '')
      .replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
      .replace(/[؟?!.,،:؛"'«»()]/g, ' ').replace(/\s+/g, ' ').trim();
  }
  var DANGER = [
    /انتحر/, /(عايز|عاوز|عايزه|عاوزه|نفسي|ناوي|ناويه|حابب|حابه)\s+(اموت|اخلص)/, /مش\s+(عايز|عاوز|عايزه|عاوزه)\s+اعيش/,
    /اقتل\s+نفس/, /(اذي|ايذاء|اوذي|اؤذي)\s+نفس/, /انهي\s+حيات/, /اخلص\s+(من\s+حيات|على\s+نفس)/,
    /(تعبت|زهقت|زهقان|تعبان)\s+من\s+الحياه/, /(مفيش|مش\s+شايف)\s+(فايده|لازمه)\s+من\s+الحياه/, /الحياه\s+مالهاش\s+(لازمه|معني)/,
    /(بيضربني|بتضربني|ضربني|ضربتني|بيعتدي\s+علي|بيهددني|بتهددني|تحرش|اتحرش|اغتصب|بيجبرني|بيضرب\s+(ابني|بنتي|اولادي))/,
    /(هقتل|اقتله|اقتلها|هموته|هموتها|عايز\s+اقتل|عاوز\s+اقتل)/,
    /suicid|kill\s+myself|self.?harm|want\s+to\s+die/i
  ];
  function dangerous(q) { var n = norm(q); for (var i = 0; i < DANGER.length; i++) if (DANGER[i].test(n)) return true; return false; }

  // ---------- screens ----------
  var screens = document.querySelectorAll('.df-screen');
  function show(id, focus) {
    for (var i = 0; i < screens.length; i++) screens[i].hidden = screens[i].id !== id;
    $('bar').hidden = (id === 's-home');
    if (focus !== false) { var h = $(id).querySelector('h2'); if (h) h.focus(); }
    window.scrollTo(0, 0);
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-go]'), function (b) {
    b.addEventListener('click', function () { show('s-' + b.getAttribute('data-go')); });
  });

  // ---------- search ----------
  var idx = FE.map(function (f) { return { f: f, words: [f.n].concat(f.w).map(norm) }; });
  function search(q) {
    var nq = norm(q); if (nq.length < 2) return [];
    var toks = nq.split(' ').filter(function (t) { return t.length >= 2; });
    var out = [];
    idx.forEach(function (it) {
      var s = 0;
      it.words.forEach(function (w) {
        if (w === nq) s += 20; else if (w.indexOf(nq) > -1 || nq.indexOf(w) > -1) s += 10;
        toks.forEach(function (t) { if (w.indexOf(t) > -1) s += 3; });
      });
      if (s > 0) out.push({ f: it.f, s: s });
    });
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, 4).map(function (x) { return x.f; });
  }
  function pickButton(f) {
    var li = el('li'); var b = el('button', '', 'df-pick'); b.type = 'button';
    b.appendChild(el('strong', f.n)); b.appendChild(el('span', f.d));
    b.addEventListener('click', function () { choose(f); }); li.appendChild(b); return li;
  }
  function renderResults(box, list, emptyMsg) {
    clear(box);
    if (!list.length) { box.appendChild(el('p', emptyMsg, 'hint')); return; }
    box.appendChild(el('p', 'ممكن يكون جواك أكتر من إحساس. إيه الأقرب ليك؟', 'df-q'));
    var ul = el('ul', '', 'df-picks'); list.forEach(function (f) { ul.appendChild(pickButton(f)); }); box.appendChild(ul);
  }
  $('search-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var q = $('q').value;
    if (dangerous(q)) { $('q').value = ''; clear($('results')); show('s-help'); return; }
    renderResults($('results'), search(q), 'مش لاقي وصف قريب. جرّب كلمة تانية، أو دوس «مش عارف أنا حاسس بإيه».');
    say('ظهرت الاقتراحات تحت.');
  });
  function byId(id) { for (var i = 0; i < FE.length; i++) if (FE[i].id === id) return FE[i]; }
  var doors = $('doors');
  ['anxiety', 'sadness', 'anger', 'loneliness'].forEach(function (id) {
    var f = byId(id); var b = el('button', f.n, 'btn btn-quiet'); b.type = 'button';
    b.addEventListener('click', function () { choose(f); }); doors.appendChild(b);
  });
  var all = $('all');
  GROUPS.forEach(function (g) {
    all.appendChild(el('h3', g[1]));
    var wrap = el('div', '', 'df-doors');
    FE.filter(function (f) { return f.g === g[0]; }).forEach(function (f) {
      var b = el('button', f.n, 'btn btn-quiet'); b.type = 'button'; b.addEventListener('click', function () { choose(f); }); wrap.appendChild(b);
    });
    all.appendChild(wrap);
  });

  // ---------- "مش عارف" ----------
  var bodyOpts = $('body-opts');
  BODY.forEach(function (b) {
    var d = el('div', '', 'df-opt'); var i = el('input'); i.type = 'checkbox'; i.id = 'bd-' + b[0]; i.value = b[0];
    var l = el('label', b[1]); l.setAttribute('for', i.id); d.appendChild(i); d.appendChild(l); bodyOpts.appendChild(d);
  });
  $('unknown').addEventListener('click', function () { show('s-body'); });
  $('body-go').addEventListener('click', function () {
    var tally = {}, n = 0;
    BODY.forEach(function (b) { if ($('bd-' + b[0]).checked) { n++; b[2].forEach(function (id) { tally[id] = (tally[id] || 0) + 1; }); } });
    var ids = Object.keys(tally).sort(function (a, b) { return tally[b] - tally[a]; }).slice(0, 4);
    renderResults($('body-results'), ids.map(byId), 'اختار حاجة أو اتنين من اللي فوق الأول.');
    say(n ? 'ظهرت اقتراحات قريبة.' : 'اختار حاجة من اللي فوق الأول.');
  });

  // ---------- choosing a feeling ----------
  function choose(f) {
    state.feeling = f;
    if (f.p && PATHS[f.p]) { state.path = PATHS[f.p]; applyPath(state.path); show('s-agree'); return; }
    $('soon-name').textContent = f.n; $('soon-desc').textContent = f.d;
    var ul = $('soon-links'); clear(ul);
    function add(h, t) { var li = el('li'); var a = el('a', t); a.href = h; li.appendChild(a); ul.appendChild(li); }
    (f.l || []).forEach(function (x) { add(x[0], x[1]); });
    if (f.gl) add('/glossary/' + f.gl + '/', 'عن الإحساس ده في قاموس المصطلحات');
    add('/feelings/', 'عجلة المشاعر: سمّي إحساسك');
    add('/life-tools/', 'أدوات لحياتك');
    add('/help-now/', 'محتاج مساعدة دلوقتي؟');
    show('s-soon');
  }

  // ---------- path ----------
  var LABEL = { name: 'التسمية', rate: 'خط البداية', understand: 'الفهم', train: 'التدريب', learn: 'تعلّم', progress: 'إيه اللي اتغيّر؟', kit: 'حقيبتي' };
  var ORDER = {
    understand: ['name', 'rate', 'understand', 'train', 'learn', 'progress', 'kit'],
    calm: ['name', 'rate', 'train', 'understand', 'learn', 'progress', 'kit']
  };
  function firstUndone() { for (var i = 0; i < state.order.length; i++) if (!state.done[state.order[i]]) return i; return state.order.length - 1; }
  function renderStepper() {
    var ol = $('stepper'); clear(ol); var open = firstUndone();
    state.order.forEach(function (k, i) {
      var li = el('li'); var b = el('button', (i + 1) + '. ' + LABEL[k], 'df-step'); b.type = 'button';
      if (state.done[k]) b.className += ' is-done';
      if (i === state.idx) b.setAttribute('aria-current', 'step');
      if (i > open) { b.setAttribute('aria-disabled', 'true'); b.title = 'بتفتح بعد ما تخلّص اللي قبلها'; }
      b.addEventListener('click', function () { if (i <= firstUndone()) showStation(i); else say('المحطة دي بتفتح بعد ما تخلّص اللي قبلها.'); });
      li.appendChild(b); ol.appendChild(li);
    });
  }
  function updateNav() {
    var k = state.order[state.idx], last = state.idx === state.order.length - 1;
    $('prev').disabled = state.idx === 0;
    $('next').hidden = last; $('next-hint').hidden = last;
    $('next').disabled = !state.done[k];
  }
  function showStation(i) {
    state.idx = i; var k = state.order[i];
    Array.prototype.forEach.call(document.querySelectorAll('.df-station'), function (s) { s.hidden = s.id !== 'st-' + k; });
    if (k === 'kit') buildSummary();
    renderStepper(); updateNav();
    var h = $('st-' + k).querySelector('h2'); if (h) h.focus();
    window.scrollTo(0, 0);
  }
  function complete(k) {
    var was = state.done[k]; state.done[k] = true; renderStepper(); updateNav();
    if (!was && state.idx < state.order.length - 1) say('تمام. المحطة اللي بعدها اتفتحت.');
  }
  $('next').addEventListener('click', function () { if (state.done[state.order[state.idx]]) showStation(state.idx + 1); });
  $('prev').addEventListener('click', function () { if (state.idx > 0) showStation(state.idx - 1); });
  Array.prototype.forEach.call(document.querySelectorAll('[data-start]'), function (b) {
    b.addEventListener('click', function () {
      state.mode = b.getAttribute('data-start'); state.order = ORDER[state.mode]; state.done = {}; state.idx = 0;
      show('s-path', false); showStation(0);
    });
  });

  // station: name (options built per path)
  function onNameChange(v) { state.named = v; $('nm-ok').hidden = false; complete('name'); }
  // station: rate
    function fillChecks(id, prefix, list) {
    var box = $(id); clear(box); list.forEach(function (t, i) {
      var d = el('div', '', 'df-opt'); var c = el('input'); c.type = 'checkbox'; c.id = prefix + i; c.value = t;
      var l = el('label', t); l.setAttribute('for', c.id); d.appendChild(c); d.appendChild(l); box.appendChild(d);
    });
  }
  $('r1').addEventListener('input', function () { $('r1o').textContent = ar($('r1').value); });
  $('r2').addEventListener('input', function () { $('r2o').textContent = ar($('r2').value); });
  $('r1-save').addEventListener('click', function () {
    state.r1 = Number($('r1').value);
    var p = $('r1-saved'); p.hidden = false; p.textContent = 'اتسجّل تقديرك: ' + ar(state.r1) + ' من ١٠.';
    complete('rate');
  });
  function radioRow(name, id, value, label, onchange) {
    var d = el('div', '', 'df-opt'); var i = el('input'); i.type = 'radio'; i.name = name; i.id = id; i.value = value;
    var l = el('label', label); l.setAttribute('for', id); d.appendChild(i); d.appendChild(l);
    i.addEventListener('change', function () { onchange(value); }); return d;
  }
  function applyPath(p) {
    $('h-agree').textContent = p.title; $('nm-ok').textContent = p.ack;
    var no = $('nm-opts'); clear(no);
    p.names.forEach(function (n, i) { no.appendChild(radioRow('nm', 'nm' + (i + 1), n[0], n[1], onNameChange)); });
    $('r1-l').textContent = p.word + ' شدته كام عندك دلوقتي؟ (٠ = مش موجود، ١٠ = أقصى شدة تتخيلها)';
    $('r2-l').textContent = p.word + ' شدته كام دلوقتي؟ (٠ = مش موجود، ١٠ = أقصى شدة)';
    $('urge-l').textContent = '(اختياري) ' + p.word + ' بيخليك عايز تعمل إيه؟';
    fillChecks('rate-body', 'rb', p.bodies); fillChecks('rate-urge', 'ru', p.urges);
    $('h-train').textContent = p.trainTitle; $('train-intro').textContent = p.trainIntro;
    var ts = $('train-steps'); clear(ts); p.trainSteps.forEach(function (t) { ts.appendChild(el('li', t)); });
    var ap = $('train-altp'); clear(ap); ap.appendChild(el('b', 'بديل: ')); ap.appendChild(document.createTextNode(p.trainAlt));
    $('h-learn').textContent = p.learnTitle;
    var ll = $('learn-list'); clear(ll); p.learn.forEach(function (t) { ll.appendChild(el('li', t)); });
    var so = $('ns-opts'); clear(so);
    p.steps.forEach(function (t, i) { so.appendChild(radioRow('ns', 'ns' + (i + 1), t, t, function (v) { own.hidden = true; state.step = v; complete('learn'); })); });
    var kl = $('kit-links'); clear(kl);
    function kadd(h, t) { var li = el('li'); var a = el('a', t); a.href = h; li.appendChild(a); kl.appendChild(li); }
    kadd('/glossary/' + p.gl + '/', p.word + ' في قاموس المصطلحات');
    p.tryLinks.forEach(function (x) { kadd(x[0], x[1]); });
    kadd('/worksheets/', 'أوراق تمرين للطباعة'); if (p.scale) kadd(p.scale[0], p.scale[1]);
  }
  // station: understand
  function doneUnderstand(alt) {
    state.sit = $('u-sit').value.trim(); state.th = $('u-th').value.trim(); state.ev = $('u-ev').value.trim(); state.bal = $('u-bal').value.trim();
    state.uAlt = !!alt; complete('understand');
  }
  $('u-done').addEventListener('click', function () { doneUnderstand(false); });
  $('u-alt').addEventListener('click', function () { doneUnderstand(true); });
  // station: train
  var TRAIN = {};
  Array.prototype.forEach.call(document.querySelectorAll('[data-train]'), function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-train'); state.train = v === 'done' ? state.path.trainMainName : v === 'alt' ? state.path.trainAltName : 'جرّبت ومكملتش (مش مرتاح)';
      var m = $('train-msg'); m.hidden = false;
      $('train-alt').hidden = v !== 'alt';
      m.textContent = v === 'done' ? 'تمام. لاحظ إن مش لازم القلق يختفي، المهم إنك جرّبت.'
        : v === 'alt' ? 'جرّب البديل اللي ظهر فوق، وبعدها كمّل.' : 'تمام، وقّف. ده اختيارك، وممكن ترجع له بعدين.';
      complete('train');
    });
  });
  // station: learn
  var lr = $('learn-res');
  function link(box, h, t) { var p = el('p'); var a = el('a', t); a.href = h; p.appendChild(a); box.appendChild(p); }
  Array.prototype.forEach.call(document.querySelectorAll('input[name="lm"]'), function (r) {
    r.addEventListener('change', function () {
      clear(lr); lr.hidden = false;
      if (r.value === 'read') { link(lr, '/glossary/' + state.path.gl + '/', 'اقرأ عن ' + state.path.word + ' في قاموس المصطلحات'); link(lr, '/articles/', 'المقالات'); }
      else if (r.value === 'try') { state.path.tryLinks.forEach(function (x) { link(lr, x[0], x[1]); }); }
      else lr.appendChild(el('p', 'التسجيل الصوتي لسه مش متاح. لحد ما ينزل، جرّب القراءة أو التمرين.'));
    });
  });
  var own = $('ns-own');
  $('ns4').addEventListener('change', function () { own.hidden = false; own.focus(); state.step = own.value.trim(); if (state.step) complete('learn'); });
  own.addEventListener('input', function () { state.step = own.value.trim(); if (state.step) complete('learn'); });
  $('learn-skip').addEventListener('click', function () { state.step = state.step || ''; complete('learn'); });
  // station: progress
  function meter(label, v) {
    var row = el('div', '', 'df-meter'); row.setAttribute('role', 'img'); row.setAttribute('aria-label', label + ': ' + ar(v) + ' من ١٠');
    row.appendChild(el('span', label, 'df-meter-l')); var bar = el('span', '', 'df-meter-b'); var fill = el('span', '', 'df-meter-f'); fill.style.width = (v * 10) + '%';
    bar.appendChild(fill); row.appendChild(bar); row.appendChild(el('span', ar(v), 'df-meter-n')); return row;
  }
  $('r2-save').addEventListener('click', function () {
    state.r2 = Number($('r2').value); var c = $('compare'); clear(c); c.hidden = false;
    c.appendChild(meter('قبل', state.r1)); c.appendChild(meter('دلوقتي', state.r2));
    c.appendChild(el('p', 'تقديرك لشدة ' + state.path.word + ' كان ' + ar(state.r1) + ' من ١٠، وبقى ' + ar(state.r2) + ' من ١٠ حسب تقديرك دلوقتي. ده وصف للتغيّر اللي لاحظته، مش نسبة تعافٍ ولا ضمان إن الإحساس مش هيرجع.'));
    if (state.r2 >= state.r1) c.appendChild(el('p', 'مش لازم الإحساس يقل في كل مرة. تقدر توقف، تجرّب بديلًا، أو تطلب دعمًا.', 'df-ok'));
    c.appendChild(el('p', 'سؤال أخير لنفسك: هل بقيت فاهم إحساسك أكتر؟ وهل طلعت بخطوة تقدر تعملها؟', 'hint'));
    complete('progress');
  });
  // kit
  function summaryRows() {
    var rows = [['الإحساس اللي سمّيته', state.named || (state.feeling ? state.feeling.n : '')]];
    if (state.r1 !== undefined) rows.push(['شدة الإحساس في البداية (تقدير شخصي)', ar(state.r1) + ' من ١٠']);
    if (state.r2 !== undefined) rows.push(['شدته بعد المحطات (تقدير شخصي)', ar(state.r2) + ' من ١٠']);
    rows.push(['الموقف', state.sit || '—'], ['الفكرة اللي لاحظتها', state.th || '—'], ['تفسير أكتر اتزانًا', state.bal || '—']);
    rows.push(['المهارة اللي جرّبتها', state.train || '—'], ['خطوتي الجاية', state.step || '—']);
    rows.push(['متابعة', state.path.scaleName ? 'لو حبيت تتابع بمقياس ' + state.path.scaleName + '، الأحسن تعيده بعد أسبوعين.' : 'ممكن تعيد التقدير بعد كام يوم وتقارن بنفسك.']);
    return rows;
  }
  function buildSummary() {
    var dl = $('kit-sum'); clear(dl);
    summaryRows().forEach(function (r) { dl.appendChild(el('dt', r[0])); dl.appendChild(el('dd', r[1])); });
  }
  function buildPrint() {
    var body = $('print-body'); clear(body);
    if (!state.order) return;
    summaryRows().forEach(function (r) { body.appendChild(el('h3', r[0])); body.appendChild(el('p', r[1])); });
  }
  window.addEventListener('beforeprint', buildPrint);
  $('kit-print').addEventListener('click', function () { buildPrint(); window.print(); });

  // ---------- restart ----------
  $('restart').addEventListener('click', function () {
    state = {};
    Array.prototype.forEach.call(document.querySelectorAll('textarea, input[type=text]'), function (t) { t.value = ''; });
    Array.prototype.forEach.call(document.querySelectorAll('input[type=radio], input[type=checkbox]'), function (c) { c.checked = false; });
    ['r1', 'r2'].forEach(function (id) { $(id).value = 5; $(id + 'o').textContent = ar(5); });
    ['nm-ok', 'r1-saved', 'train-alt', 'train-msg', 'learn-res', 'compare', 'ns-own'].forEach(function (id) { $(id).hidden = true; });
    clear($('results')); clear($('body-results')); clear($('print-body')); clear($('kit-sum'));
    show('s-home'); say('تم مسح كل اللي كتبته من الصفحة.');
  });

  show('s-home', false);
})();
