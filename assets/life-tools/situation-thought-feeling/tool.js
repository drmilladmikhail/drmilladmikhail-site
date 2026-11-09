// Draft tool: runs only in the browser. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var form = document.getElementById('tool-form');
  if (!form) return;
  var status = document.getElementById('status');
  var pairs = [['intensity-before', 'intensity-before-out'], ['intensity-after', 'intensity-after-out']];
  pairs.forEach(function (p) {
    var input = document.getElementById(p[0]), out = document.getElementById(p[1]);
    input.addEventListener('input', function () { out.textContent = input.value; });
  });

  var rows = [
    ['الموقف', 'situation'], ['الإحساس', 'feeling'], ['شدة الإحساس قبل', 'intensity-before'],
    ['الفكرة', 'thought'], ['نظرة أوسع', 'wider'], ['شدة الإحساس بعد', 'intensity-after']
  ];
  function buildPrintCopy() {
    var body = document.getElementById('print-body');
    body.textContent = '';
    rows.forEach(function (r) {
      var el = document.getElementById(r[1]);
      var h = document.createElement('h3'); h.textContent = r[0];
      var p = document.createElement('p');
      p.textContent = (el.value || '').trim() || '—';
      if (el.type === 'range') p.textContent = el.value + ' من 10';
      body.appendChild(h); body.appendChild(p);
    });
  }
  window.addEventListener('beforeprint', buildPrintCopy);
  document.getElementById('print-btn').addEventListener('click', function () {
    buildPrintCopy();
    window.print();
  });
  document.getElementById('reset-btn').addEventListener('click', function () {
    form.reset();
    pairs.forEach(function (p) { document.getElementById(p[1]).textContent = document.getElementById(p[0]).value; });
    document.getElementById('print-body').textContent = '';
    status.textContent = 'تم مسح كل اللي كتبته من الصفحة.';
    document.getElementById('situation').focus();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})();
