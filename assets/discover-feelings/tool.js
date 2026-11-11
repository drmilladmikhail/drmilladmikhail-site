// «اكتشاف مشاعرك»: a five-step guided flow. Runs only in the browser.
// Nothing a visitor types or picks is sent, logged, stored or put in the URL: answers live in memory until the page closes.
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var FE = window.DF_FEELINGS || [], GROUPS = window.DF_GROUPS || [], BODY = window.DF_BODY || [], PATHS = window.DF_PATHS || {};
  var CHIPS = window.DF_CHIPS || [], NEEDS = window.DF_NEEDS || {}, GDEF = window.DF_GROUP_DEFAULT || {}, OVR = window.DF_OVERRIDE || {};
  var QS = window.DF_QUESTIONS || [], MORE_NEED = window.DF_MORE_NEED || {}, AFFECT = window.DF_AFFECT || {}, BREATH = window.DF_BREATH || {};
  if (!$('jr') || !FE.length) return;
  var MAX = 3;
  var LABEL = {}; CHIPS.forEach(function (c) { LABEL[c[1]] = c[0]; });
  var state;
  function fresh() { return { screen: 'welcome', sel: [], ans: {}, qi: 0, near: {}, step: '', from: 'feel' }; }

  function ar(n) { return Number(n).toLocaleString('ar-EG'); }
  function el(tag, text, cls) { var e = document.createElement(tag); if (text) e.textContent = text; if (cls) e.className = cls; return e; }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function byId(id) { for (var i = 0; i < FE.length; i++) if (FE[i].id === id) return FE[i]; }
  function nameOf(f) { return LABEL[f.id] || f.n; }
  function say(t) { var s = $('jr-status'); s.textContent = ''; setTimeout(function () { s.textContent = t; }, 30); }
  function joinAr(list) { return list.length < 2 ? list.join('') : list.slice(0, -1).join('، ') + ' و' + list[list.length - 1]; }

  // ---------- text normalising and safety ----------
  function norm(s) {
    return String(s).toLowerCase()
      .replace(/[ً-ْـ]/g, '')
      .replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
      .replace(/[؟?!.,،:؛"'«»()…]/g, ' ').replace(/\s+/g, ' ').trim();
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

  // ---------- screens and progress ----------
  var STAGE = { welcome: 1, feel: 2, body: 2, ask: 3, needs: 4, result: 5, helpscreen: 0 };
  var screens = document.querySelectorAll('.jr-screen');
  function show(name, focus) {
    state.screen = name;
    for (var i = 0; i < screens.length; i++) screens[i].hidden = screens[i].id !== 'jr-' + name;
    var st = STAGE[name];
    $('jr-top').hidden = name === 'welcome';
    $('jr-progress').hidden = $('jr-count').hidden = !st;
    if (st) {
      $('jr-count').textContent = 'الخطوة ' + ar(st) + ' من ٥';
      $('jr-fill').style.width = ((st - 1) / 4 * 100) + '%';
      Array.prototype.forEach.call($('jr-progress').children, function (li) {
        var n = Number(li.getAttribute('data-s'));
        li.className = n < st ? 'is-done' : n === st ? 'is-now' : '';
        if (n === st) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
      });
    }
    if (focus !== false) {
      var h = $('jr-' + name).querySelector('h2');
      if (h) h.focus({ preventScroll: true });
      var hd = document.querySelector('header.topbar'), off = (hd && hd.offsetHeight ? hd.offsetHeight : 0) + 16;
      var top = $('jr').getBoundingClientRect().top + window.pageYOffset - off;
      if (window.pageYOffset > top) window.scrollTo(0, Math.max(0, top));
    }
  }
  function back() {
    var s = state.screen;
    if (s === 'feel') show('welcome');
    else if (s === 'body') show('feel');
    else if (s === 'ask') { if (state.qi > 0) { state.qi--; renderAsk(); show('ask'); } else show('feel'); }
    else if (s === 'needs') { state.qi = QS.length - 1; renderAsk(); show('ask'); }
    else if (s === 'result') show('needs');
    else if (s === 'helpscreen') show(state.from);
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-back]'), function (b) { b.addEventListener('click', back); });
  $('jr-start').addEventListener('click', function () { show('feel'); });

  // ---------- step 2: pick feelings ----------
  var toggles = [];           // every toggle button for a feeling, so all copies stay in sync
  function isSel(id) { return state.sel.indexOf(id) > -1; }
  function sync() {
    toggles = toggles.filter(function (t) { return document.body.contains(t.b); });
    toggles.forEach(function (t) { t.b.setAttribute('aria-pressed', isSel(t.id) ? 'true' : 'false'); });
    var tray = $('jr-tray'); clear(tray);
    if (!state.sel.length) { tray.appendChild(el('p', 'لسه ما اخترتش شعور.', 'jr-hint')); return; }
    tray.appendChild(el('span', 'اخترت (' + ar(state.sel.length) + ' من ' + ar(MAX) + '):', 'jr-tray-l'));
    state.sel.forEach(function (id) {
      var f = byId(id), b = el('button', '', 'jr-picked'); b.type = 'button';
      b.appendChild(el('span', nameOf(f))); var x = el('span', '×', 'jr-x'); x.setAttribute('aria-hidden', 'true'); b.appendChild(x);
      b.setAttribute('aria-label', 'شيل ' + nameOf(f) + ' من اختياراتك');
      b.addEventListener('click', function () { toggle(id); $('jr-q').focus(); });
      tray.appendChild(b);
    });
  }
  function toggle(id) {
    var i = state.sel.indexOf(id), err = $('jr-feel-err');
    err.hidden = true;
    if (i > -1) state.sel.splice(i, 1);
    else if (state.sel.length >= MAX) { err.textContent = 'تقدر تختار لحد ' + ar(MAX) + ' مشاعر. شيل واحد من اختياراتك الأول.'; err.hidden = false; }
    else state.sel.push(id);
    sync();
  }
  function chip(f, cls, withDesc) {
    var b = el('button', '', cls || 'jr-chip'); b.type = 'button'; b.setAttribute('aria-pressed', 'false');
    if (withDesc) { b.appendChild(el('strong', nameOf(f))); b.appendChild(el('span', f.d)); } else b.textContent = nameOf(f);
    b.addEventListener('click', function () { toggle(f.id); });
    toggles.push({ b: b, id: f.id }); return b;
  }
  CHIPS.forEach(function (c) { var f = byId(c[1]); if (f) $('jr-chips').appendChild(chip(f)); });
  (function () {
    var all = $('jr-all');
    $('jr-all-sum').textContent = 'استكشف كل المشاعر (' + ar(FE.length) + ')';
    GROUPS.forEach(function (g) {
      all.appendChild(el('h3', g[1]));
      var wrap = el('div', '', 'jr-chips jr-chips-small');
      FE.filter(function (f) { return f.g === g[0]; }).forEach(function (f) { wrap.appendChild(chip(f)); });
      all.appendChild(wrap);
    });
  })();

  var idx = FE.map(function (f) { return { f: f, words: [f.n, LABEL[f.id] || ''].concat(f.w).filter(Boolean).map(norm) }; });
  function search(q) {
    var nq = norm(q); if (nq.length < 2) return null;
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
  function renderPicks(box, list, emptyMsg) {
    clear(box);
    if (!list) return;
    if (!list.length) { box.appendChild(el('p', emptyMsg, 'jr-empty')); return; }
    box.appendChild(el('p', 'إيه الأقرب ليك؟ دوس عليه عشان تختاره.', 'jr-label'));
    var ul = el('ul', '', 'jr-picks');
    list.forEach(function (f) { var li = el('li'); li.appendChild(chip(f, 'jr-pick', true)); ul.appendChild(li); });
    box.appendChild(ul); sync();
  }
  function toHelp(from) { state.from = from; $('jr-q').value = ''; clear($('jr-results')); show('helpscreen'); }
  function runSearch(announce) {
    var q = $('jr-q').value;
    if (dangerous(q)) { toHelp('feel'); return; }
    var list = search(q);
    renderPicks($('jr-results'), list, 'مش لاقي وصف قريب. جرّب كلمة تانية، أو اختار من تحت، أو دوس «مش عارف أحدد شعوري».');
    if (announce && list) say(list.length ? 'ظهرت ' + ar(list.length) + ' اقتراحات تحت خانة الكتابة.' : 'مفيش اقتراحات قريبة.');
  }
  var timer;
  $('jr-q').addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(function () { runSearch(false); }, 220); });
  $('jr-search').addEventListener('submit', function (e) { e.preventDefault(); clearTimeout(timer); runSearch(true); });
  $('jr-feel-next').addEventListener('click', function () {
    var err = $('jr-feel-err');
    if (!state.sel.length) {
      err.textContent = 'اختار شعور واحد على الأقل عشان نكمّل. ولو مش عارف تسمّيه، دوس «مش عارف أحدد شعوري».'; err.hidden = false; return;
    }
    err.hidden = true; state.qi = 0; renderAsk(); show('ask');
  });

  // "مش عارف أحدد شعوري"
  BODY.forEach(function (b) { $('jr-body-opts').appendChild(optionRow('checkbox', 'jr-bd', 'jr-bd-' + b[0], b[0], b[1])); });
  $('jr-unknown').addEventListener('click', function () { show('body'); });
  $('jr-body-go').addEventListener('click', function () {
    var tally = {}, n = 0;
    BODY.forEach(function (b) { if ($('jr-bd-' + b[0]).checked) { n++; b[2].forEach(function (id) { tally[id] = (tally[id] || 0) + 1; }); } });
    var ids = Object.keys(tally).sort(function (a, b) { return tally[b] - tally[a]; }).slice(0, 4);
    renderPicks($('jr-body-results'), ids.map(byId), 'اختار حاجة أو اتنين من اللي فوق الأول.');
    if (n) {
      var done = el('p'); var b = el('button', 'تمام، رجّعني أكمّل', 'jr-btn jr-btn-main'); b.type = 'button';
      b.addEventListener('click', function () { show('feel'); }); done.appendChild(b); $('jr-body-results').appendChild(done);
    }
    say(n ? 'ظهرت مشاعر قريبة. اختار منها وبعدين ارجع كمّل.' : 'اختار حاجة من اللي فوق الأول.');
  });

  // ---------- step 3: one question per screen ----------
  function optionRow(type, name, id, value, label, onchange) {
    var d = el('div', '', 'jr-option'); var i = el('input'); i.type = type; i.name = name; i.id = id; i.value = value;
    var l = el('label', label); l.setAttribute('for', id); d.appendChild(i); d.appendChild(l);
    if (onchange) i.addEventListener('change', function () { onchange(value, i); });
    return d;
  }
  function renderAsk() {
    var Q = QS[state.qi], box = $('jr-ask-opts'); clear(box);
    $('jr-ask-n').textContent = 'سؤال ' + ar(state.qi + 1) + ' من ' + ar(QS.length);
    $('jr-h-ask').textContent = Q.q; $('jr-ask-err').hidden = true;
    Q.o.forEach(function (o) {
      var row = optionRow('radio', 'jr-a-' + Q.k, 'jr-a-' + Q.k + '-' + o[0], o[0], o[1], function (v) { state.ans[Q.k] = v; $('jr-ask-err').hidden = true; });
      if (state.ans[Q.k] === o[0]) row.firstChild.checked = true;
      box.appendChild(row);
    });
    $('jr-ask-next').textContent = state.qi === QS.length - 1 ? 'اكتشف احتياجك' : 'متابعة';
  }
  $('jr-ask-next').addEventListener('click', function () {
    var Q = QS[state.qi], err = $('jr-ask-err');
    if (!state.ans[Q.k]) { err.textContent = 'اختار إجابة واحدة عشان نكمّل. لو مش متأكد، في اختيار لكده.'; err.hidden = false; return; }
    if (state.qi < QS.length - 1) { state.qi++; renderAsk(); show('ask'); } else { renderNeeds(); show('needs'); }
  });

  // ---------- step 4: possible needs ----------
  function conf(f) { var g = GDEF[f.g] || { nd: ['understand'], x: '' }, o = OVR[f.id] || {}; return { nd: o.nd || g.nd, x: o.x !== undefined ? o.x : (f.p || g.x), a: o.a || [] }; }
  function phrase(k) { var Q = QS.filter(function (q) { return q.k === k; })[0], v = state.ans[k], out = ''; if (Q) Q.o.forEach(function (o) { if (o[0] === v) out = o[2]; }); return out; }
  function needKeys() {
    var keys = [], add = function (k) { if (k && NEEDS[k] && keys.indexOf(k) < 0) keys.push(k); };
    state.sel.forEach(function (id) { add(conf(byId(id)).nd[0]); });
    add(MORE_NEED[state.ans.more]);
    state.sel.forEach(function (id) { conf(byId(id)).nd.slice(1).forEach(add); });
    return keys.slice(0, 3);
  }
  function contextLine() {
    var parts = [], w = phrase('when'), m = phrase('more'), a = phrase('affect');
    if (w) parts.push('بيظهر غالبًا ' + w);
    if (m) parts.push('وأكتر حاجة بتزوّده ' + m);
    if (a) parts.push('وبيأثر على ' + a);
    return parts.length ? parts.join('، ').replace(/^و/, '') + '.' : '';
  }
  function renderNeeds() {
    var names = state.sel.map(function (id) { return nameOf(byId(id)); });
    $('jr-needs-intro').textContent = 'اخترت: ' + joinAr(names) + '. ' + contextLine() + ' من ده، ممكن تكون محتاج:';
    var ul = $('jr-needs-list'); clear(ul);
    needKeys().forEach(function (k) {
      var n = NEEDS[k], li = el('li', '', 'jr-need');
      li.appendChild(el('h3', n.t)); li.appendChild(el('p', n.d));
      var b = el('button', 'ده قريب مني', 'jr-near'); b.type = 'button'; b.setAttribute('aria-pressed', state.near[k] ? 'true' : 'false');
      b.addEventListener('click', function () { state.near[k] = !state.near[k]; b.setAttribute('aria-pressed', state.near[k] ? 'true' : 'false'); });
      li.appendChild(b); ul.appendChild(li);
    });
  }
  $('jr-needs-next').addEventListener('click', function () { renderResult(); show('result'); });

  // ---------- step 5: results ----------
  function exercise() {
    for (var i = 0; i < state.sel.length; i++) {
      var p = PATHS[conf(byId(state.sel[i])).x];
      if (p) return { title: p.trainMainName, intro: p.trainIntro, steps: p.trainSteps, alt: p.trainAlt, next: p.steps, path: p };
    }
    return { title: BREATH.title, intro: BREATH.intro, steps: BREATH.steps, alt: '', next: BREATH.next, path: null };
  }
  function chosenNeeds() { var all = needKeys(), near = all.filter(function (k) { return state.near[k]; }); return near.length ? near : all; }
  function resultData() {
    var feelings = state.sel.map(byId), first = feelings[0], ex = exercise(), needs = chosenNeeds();
    var pattern = [];
    var fp = PATHS[first.p];
    if (fp) pattern = fp.learn.slice(0, 3); else pattern.push(nameOf(first) + ': ' + first.d);
    feelings.slice(1).forEach(function (f) { pattern.push(nameOf(f) + ': ' + f.d); });
    var questions = needs.map(function (k) { return NEEDS[k].q; });
    var af = AFFECT[state.ans.affect]; if (af) questions.push(af.q);
    var links = [], seen = {}, addL = function (x) { if (x && !seen[x[0]]) { seen[x[0]] = 1; links.push(x); } };
    feelings.forEach(function (f) { conf(f).a.forEach(addL); });
    needs.forEach(function (k) { addL(NEEDS[k].l); });
    if (af) addL(af.l);
    feelings.forEach(function (f) { (f.l || []).forEach(addL); var p = PATHS[f.p]; if (p) p.tryLinks.forEach(addL); });
    feelings.forEach(function (f) { if (f.gl) addL(['/glossary/' + f.gl + '/', nameOf(f) + ' في قاموس المصطلحات']); });
    feelings.forEach(function (f) { var p = PATHS[f.p]; if (p && p.scale) addL(p.scale); });
    return { feelings: feelings, ex: ex, needs: needs, pattern: pattern, questions: questions, links: links.slice(0, 7), cta: links.filter(function (x) { return x[0].indexOf('/life-tools/') === 0; })[0] || ['/life-tools/', 'أدوات لحياتك'] };
  }
  function fillList(id, items) { var ul = $(id); clear(ul); items.forEach(function (t) { ul.appendChild(el('li', t)); }); }
  function renderResult() {
    var r = resultData();
    var box = $('jr-r-feel'); clear(box); r.feelings.forEach(function (f) { box.appendChild(el('span', nameOf(f), 'jr-chip is-static')); });
    $('jr-r-context').textContent = contextLine() || 'لسه مش واضح إمتى بيظهر أو إيه اللي بيزوّده، وده طبيعي. الملاحظة مع الوقت بتوضّح.';
    var needsP = el('p', 'اللي ممكن تكون محتاجه: ' + joinAr(r.needs.map(function (k) { return NEEDS[k].t.replace(/^تحتاج (إلى )?/, ''); })) + '.');
    $('jr-r-context').appendChild(document.createElement('br')); $('jr-r-context').appendChild(needsP.firstChild);
    fillList('jr-r-pattern', r.pattern); fillList('jr-r-questions', r.questions);
    $('jr-r-ex-title').textContent = r.ex.title; $('jr-r-ex-intro').textContent = r.ex.intro; fillList('jr-r-ex-steps', r.ex.steps);
    $('jr-r-ex-altbox').hidden = !r.ex.alt; $('jr-r-ex-alt').textContent = r.ex.alt;
    var ul = $('jr-r-links'); clear(ul);
    r.links.forEach(function (x) { var li = el('li'); var a = el('a', x[1]); a.href = x[0]; li.appendChild(a); ul.appendChild(li); });
    var so = $('jr-r-steps'); clear(so);
    r.ex.next.forEach(function (t, i) {
      var row = optionRow('radio', 'jr-step', 'jr-step-' + i, t, t, function (v) { state.step = v; var c = $('jr-r-chosen'); c.hidden = false; c.textContent = 'خطوتي النهارده: ' + v + '. خطوة صغيرة كفاية.'; });
      if (state.step === t) row.firstChild.checked = true;
      so.appendChild(row);
    });
    var ch = $('jr-r-chosen'); ch.hidden = !state.step; if (state.step) ch.textContent = 'خطوتي النهارده: ' + state.step + '. خطوة صغيرة كفاية.';
    $('jr-r-cta').href = r.cta[0];
    var flagged = r.feelings.filter(function (f) { return f.s; }), sf = $('jr-safety'); clear(sf); sf.hidden = !flagged.length;
    if (flagged.length) {
      sf.appendChild(el('b', 'لو الشعور ده تقيل عليك أو مستمر: '));
      sf.appendChild(document.createTextNode('كلّم حد تثق فيه أو متخصص. ولو في خطر عليك دلوقتي افتح '));
      var a = el('a', 'محتاج مساعدة دلوقتي'); a.href = '/help-now/'; sf.appendChild(a); sf.appendChild(document.createTextNode('.'));
    }
  }
  function buildPrint() {
    var body = $('print-body'); clear(body);
    if (!state.sel.length) return;
    var r = resultData();
    function sec(h, lines) { body.appendChild(el('h3', h)); lines.forEach(function (t) { body.appendChild(el('p', t)); }); }
    sec('مشاعري دلوقتي', [joinAr(r.feelings.map(nameOf)), contextLine()]);
    sec('اللي ممكن أكون محتاجه', r.needs.map(function (k) { return NEEDS[k].t; }));
    sec('أسئلة للتأمل', r.questions);
    sec('تمرين: ' + r.ex.title, r.ex.steps.map(function (t, i) { return ar(i + 1) + '. ' + t; }));
    sec('خطوتي النهارده', [state.step || '—']);
    sec('تنبيه', ['ملخص للتأمل الذاتي من drmilladmikhail.com. ليس تشخيصًا ولا بديلًا عن تقييم متخصص.']);
  }
  window.addEventListener('beforeprint', buildPrint);
  $('jr-print').addEventListener('click', function () { buildPrint(); window.print(); });

  // ---------- restart ----------
  function restart() {
    state = fresh();
    $('jr-q').value = '';
    Array.prototype.forEach.call($('jr').querySelectorAll('input[type=radio], input[type=checkbox]'), function (c) { c.checked = false; });
    ['jr-results', 'jr-body-results', 'print-body'].forEach(function (id) { clear($(id)); });
    ['jr-feel-err', 'jr-ask-err'].forEach(function (id) { $(id).hidden = true; });
    sync(); show('welcome'); say('اتمسحت كل إجاباتك من الصفحة. تقدر تبدأ من جديد.');
  }
  $('jr-restart').addEventListener('click', restart);
  $('jr-restart2').addEventListener('click', restart);

  state = fresh(); sync(); show('welcome', false);
  $('jr').className += ' is-ready';
})();
