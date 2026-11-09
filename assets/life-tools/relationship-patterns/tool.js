// Draft tool: runs only in the browser. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var form = document.getElementById('tool-form'); if (!form) return;
  var status = document.getElementById('status');
  var SIT = [
    ['reply', 'لما حد بيتأخر في الرد عليا'],
    ['conflict', 'لما بيحصل خلاف أو انتقاد'],
    ['close', 'لما حد يقرب مني أوي'],
    ['distance', 'لما حد يبعد أو يطلب مساحة'],
    ['nosay', 'لما أحتاج أقول «لأ» أو أحط حد'],
    ['other', 'موقف تاني (هكتبه تحت)']
  ];
  var box = document.getElementById('situations');
  SIT.forEach(function (n) {
    var d = document.createElement('div'); d.className = 'xt-opt';
    var i = document.createElement('input'); i.type = 'radio'; i.name = 'sit'; i.id = 'sit-' + n[0]; i.value = n[0];
    var l = document.createElement('label'); l.setAttribute('for', i.id); l.textContent = n[1];
    d.appendChild(i); d.appendChild(l); box.appendChild(d);
  });
  function label() { var c = form.querySelector('input[name="sit"]:checked'); if (!c) return ''; for (var k = 0; k < SIT.length; k++) if (SIT[k][0] === c.value) return SIT[k][1]; return ''; }
  function buildPrint() {
    var body = document.getElementById('print-body'); body.textContent = '';
    function row(h, t) { var a = document.createElement('h3'); a.textContent = h; var p = document.createElement('p'); p.textContent = t || '—'; body.appendChild(a); body.appendChild(p); }
    row('الموقف المتكرر', label());
    row('بعمل عادةً', document.getElementById('usual').value.trim());
    row('اللي جوايا', document.getElementById('inside').value.trim());
    row('اللي كنت محتاجه', document.getElementById('need').value.trim());
    row('خطوة مختلفة أجربها', document.getElementById('step').value.trim());
  }
  window.addEventListener('beforeprint', buildPrint);
  document.getElementById('print-btn').addEventListener('click', function () { buildPrint(); window.print(); });
  document.getElementById('reset-btn').addEventListener('click', function () {
    form.reset(); document.getElementById('print-body').textContent = '';
    status.textContent = 'تم مسح كل اللي كتبته من الصفحة.'; document.getElementById('usual').focus();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})();
