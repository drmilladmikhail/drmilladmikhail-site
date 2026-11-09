// Draft tool: runs only in the browser. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var form = document.getElementById('tool-form'); if (!form) return;
  var status = document.getElementById('status');
  var lists = { 'in': [], 'influence': [], 'out': [] };
  var names = { 'in': 'في إيدي', 'influence': 'أقدر أأثر فيه', 'out': 'مش في إيدي' };
  function render(k) {
    var ul = document.getElementById('ul-' + k); ul.textContent = '';
    lists[k].forEach(function (t, i) {
      var li = document.createElement('li'); var s = document.createElement('span'); s.textContent = t;
      var b = document.createElement('button'); b.type = 'button'; b.textContent = '✕';
      b.setAttribute('aria-label', 'احذف: ' + t);
      b.addEventListener('click', function () { lists[k].splice(i, 1); render(k); status.textContent = 'اتحذف البند.'; var inp = document.getElementById('in-' + k); inp.focus(); });
      li.appendChild(s); li.appendChild(b); ul.appendChild(li);
    });
    document.getElementById('empty-' + k).hidden = lists[k].length > 0;
  }
  function add(k) {
    var inp = document.getElementById('in-' + k); var v = inp.value.trim(); if (!v) return;
    lists[k].push(v); inp.value = ''; render(k); status.textContent = 'اتضاف البند في «' + names[k] + '».'; inp.focus();
  }
  Object.keys(lists).forEach(function (k) {
    render(k);
    document.querySelector('[data-add="' + k + '"]').addEventListener('click', function () { add(k); });
    document.getElementById('in-' + k).addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); add(k); } });
  });
  function buildPrint() {
    var body = document.getElementById('print-body'); body.textContent = '';
    function row(h, t) { var a = document.createElement('h3'); a.textContent = h; var p = document.createElement('p'); p.textContent = t || '—'; body.appendChild(a); body.appendChild(p); }
    row('اللي شاغلني', document.getElementById('worry').value.trim());
    Object.keys(lists).forEach(function (k) { row(names[k], lists[k].join('\n')); });
    row('خطوتي الصغيرة النهارده', document.getElementById('step').value.trim());
    row('جملة لنفسي', document.getElementById('letgo').value.trim());
  }
  window.addEventListener('beforeprint', buildPrint);
  document.getElementById('print-btn').addEventListener('click', function () { buildPrint(); window.print(); });
  document.getElementById('reset-btn').addEventListener('click', function () {
    form.reset(); Object.keys(lists).forEach(function (k) { lists[k] = []; render(k); });
    document.getElementById('print-body').textContent = '';
    status.textContent = 'تم مسح كل اللي كتبته من الصفحة.'; document.getElementById('worry').focus();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})();
