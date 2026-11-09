// Draft tool: runs only in the browser. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var form = document.getElementById('tool-form'); if (!form) return;
  var status = document.getElementById('status');
  function val(id) { return document.getElementById(id).value.trim(); }
  function buildPrint() {
    var body = document.getElementById('print-body'); body.textContent = '';
    function row(h, t) { var a = document.createElement('h3'); a.textContent = h; var p = document.createElement('p'); p.textContent = t || '—'; body.appendChild(a); body.appendChild(p); }
    row('الطلب', val('ask')); row('رد فعلي الأول', val('first'));
    var costs = Array.prototype.map.call(form.querySelectorAll('input[name=cost]:checked'), function (c) { return c.value; });
    row('هتكلفني', costs.join('، '));
    row('ليه ممكن أقول أيوه', val('why'));
    var ch = form.querySelector('input[name=choice]:checked'); row('اختياري', ch ? ch.value : '');
    row('جملتي', val('sentence'));
  }
  window.addEventListener('beforeprint', buildPrint);
  document.getElementById('print-btn').addEventListener('click', function () { buildPrint(); window.print(); });
  document.getElementById('reset-btn').addEventListener('click', function () {
    form.reset(); document.getElementById('print-body').textContent = '';
    status.textContent = 'تم مسح كل اللي كتبته من الصفحة.'; document.getElementById('ask').focus();
  });
  document.getElementById('copy-btn').addEventListener('click', function () {
    var t = document.getElementById('sentence').value;
    if (!t.trim()) { status.textContent = 'اكتب الجملة الأول.'; return; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () { status.textContent = 'اتنسخت الجملة.'; }, function () { status.textContent = 'ما قدرتش أنسخ. حدد الجملة وانسخها بإيدك.'; });
    } else { status.textContent = 'المتصفح مش بيدعم النسخ هنا. حدد الجملة وانسخها بإيدك.'; }
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})();
