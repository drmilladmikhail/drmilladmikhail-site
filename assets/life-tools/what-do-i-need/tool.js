// Draft tool: runs only in the browser. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var form = document.getElementById('tool-form'); if (!form) return;
  var status = document.getElementById('status');
  var NEEDS = [
    ['body', 'راحة للجسم', 'ممكن تبدأ بحاجة صغيرة: مية، أكل خفيف، تمدد، أو دقايق نوم أو قعدة هادية.'],
    ['quiet', 'هدوء ومساحة', 'ممكن تقلل المنبهات شوية: اقفل الإشعارات أو اقعد في مكان أهدى لدقايق.'],
    ['heard', 'حد يسمعني', 'ممكن تبعت لشخص تثق فيه: «عندك دقايق أحكيلك على حاجة؟»'],
    ['clear', 'أفهم الصورة أوضح', 'ممكن تكتب اللي في دماغك في ورقة وتفرز: إيه الحقيقة وإيه التوقع.'],
    ['help', 'مساعدة عملية', 'ممكن تحدد حاجة واحدة محددة تطلب فيها مساعدة، وتطلبها بجملة واضحة.'],
    ['move', 'حركة أو تغيير جو', 'ممكن تمشي 5 دقايق أو تفتح الشباك أو تغيّر المكان اللي قاعد فيه.'],
    ['fun', 'حاجة تفرّحني أو تسليني', 'ممكن تختار نشاط صغير بتحبه من غير ما تحاسب نفسك عليه.'],
    ['notsure', 'مش عارف', 'عادي جدًا. جرب تبدأ بالجسم: مية، أكل، حركة خفيفة. وبعدها اسأل نفسك تاني.']
  ];
  var box = document.getElementById('needs');
  NEEDS.forEach(function (n) {
    var d = document.createElement('div'); d.className = 'xt-opt';
    var i = document.createElement('input'); i.type = 'radio'; i.name = 'need'; i.id = 'need-' + n[0]; i.value = n[0];
    var l = document.createElement('label'); l.setAttribute('for', i.id); l.textContent = n[1];
    d.appendChild(i); d.appendChild(l); box.appendChild(d);
    i.addEventListener('change', function () {
      document.getElementById('hint-text').textContent = n[2];
      document.getElementById('hint-box').hidden = false;
    });
  });
  function chosen() { var c = form.querySelector('input[name="need"]:checked'); return c ? c.value : ''; }
  function label(v) { for (var k = 0; k < NEEDS.length; k++) if (NEEDS[k][0] === v) return NEEDS[k][1]; return ''; }
  function buildPrint() {
    var body = document.getElementById('print-body'); body.textContent = '';
    function row(h, t) { var a = document.createElement('h3'); a.textContent = h; var p = document.createElement('p'); p.textContent = t || '—'; body.appendChild(a); body.appendChild(p); }
    row('حاسس بإيه', document.getElementById('feel').value.trim());
    row('أنا محتاج', label(chosen()));
    row('خطوتي الصغيرة', document.getElementById('step').value.trim());
  }
  window.addEventListener('beforeprint', buildPrint);
  document.getElementById('print-btn').addEventListener('click', function () { buildPrint(); window.print(); });
  document.getElementById('reset-btn').addEventListener('click', function () {
    form.reset(); document.getElementById('hint-box').hidden = true; document.getElementById('print-body').textContent = '';
    status.textContent = 'تم مسح كل اللي كتبته من الصفحة.'; document.getElementById('feel').focus();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})();
