// Draft simulator: browser only. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var S = window.SCENARIOS; if (!S) return;
  var $ = function (id) { return document.getElementById(id); };
  var cur = null, doneIds = [];
  var steps = ['pick', 'play', 'done'];
  function show(id) { steps.forEach(function (s) { $(s).hidden = s !== id; }); }
  function sub(n) { ['s1', 's2', 's3'].forEach(function (s, i) { $(s).hidden = i + 1 !== n; }); }
  function mk(tag, text, cls) { var e = document.createElement(tag); if (text) e.textContent = text; if (cls) e.className = cls; return e; }
  function btn(text, onclick) { var li = mk('li'); var b = mk('button', text, 'choice'); b.type = 'button'; b.setAttribute('aria-pressed', 'false'); b.addEventListener('click', function () { onclick(b); }); li.appendChild(b); return li; }
  function say(m) { $('status').textContent = m; }
  function list() {
    var ul = $('scn-list'); ul.textContent = '';
    S.forEach(function (s) { ul.appendChild(btn(s.title + (doneIds.indexOf(s.id) >= 0 ? ' (جرّبته)' : ''), function () { start(s); })); });
  }
  function start(s) {
    cur = s; show('play'); sub(1); say('');
    $('prog').textContent = 'موقف ' + (S.indexOf(s) + 1) + ' من ' + S.length;
    $('scn-title').textContent = s.title; $('scn-situation').textContent = s.situation;
    var o = $('opts'); o.textContent = '';
    s.options.forEach(function (op) { o.appendChild(btn(op.t, function (b) { choose(op, b); })); });
    $('scn-title').focus();
  }
  function choose(op, b) {
    Array.prototype.forEach.call($('opts').querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    var fb = $('fb'); fb.textContent = '';
    var k = mk('b', 'رأي على الرد ده: ', 'k'); fb.appendChild(k); fb.appendChild(document.createTextNode(op.f));
    var alt = $('alt'); alt.textContent = ''; alt.appendChild(mk('b', 'صياغة بديلة ممكنة: ')); alt.appendChild(document.createTextNode(cur.alt));
    if (cur.note) alt.appendChild(mk('p', cur.note, 'hint'));
    var r = $('retry'); r.textContent = '';
    cur.retry.forEach(function (v) { r.appendChild(btn(v.l + ': ' + v.t, function (bb) { pickRetry(v, bb); })); });
    sub(2); fb.focus();
  }
  function pickRetry(v, b) {
    Array.prototype.forEach.call($('retry').querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    $('final').value = v.t; sub(3); $('final').focus();
    if (doneIds.indexOf(cur.id) < 0) doneIds.push(cur.id);
  }
  $('copy').addEventListener('click', function () {
    var t = $('final').value; if (!t.trim()) { say('اكتب الجملة الأول.'); return; }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { say('اتنسخت الجملة.'); }, function () { say('ما قدرتش أنسخ. حدد الجملة وانسخها بإيدك.'); });
    else say('المتصفح مش بيدعم النسخ هنا. حدد الجملة وانسخها بإيدك.');
  });
  $('another').addEventListener('click', function () {
    $('final').value = '';
    if (doneIds.length >= S.length) { show('done'); $('share').focus(); } else { show('pick'); list(); $('scn-list').querySelector('button').focus(); }
  });
  $('reset').addEventListener('click', function () { doneIds = []; $('final').value = ''; show('pick'); list(); $('scn-list').querySelector('button').focus(); });
  $('again').addEventListener('click', function () { doneIds = []; show('pick'); list(); $('scn-list').querySelector('button').focus(); });
  $('share').addEventListener('click', function () {
    var t = 'جرّبت تمرين «أقول إيه في الموقف ده؟» لتدريب التواصل. مفيش رد صح في كل مكان، بس التدريب بيساعد. drmilladmikhail.com';
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { $('share').textContent = 'اتنسخت الرسالة'; });
  });
  list(); show('pick');
})();
