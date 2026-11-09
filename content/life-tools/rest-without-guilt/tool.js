// Draft tool: runs only in the browser. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var form = document.getElementById('tool-form'); if (!form) return;
  var status = document.getElementById('status');
  var RESTS = [
    ['detach', 'أبعد بدماغي عن الشغل أو الضغط', 'ممكن تعمل حاجة تشغلك عن الموضوع: مشي، مكالمة مع صاحب، أو هواية من غير ما تفتح الشغل.'],
    ['relax', 'أهدّي جسمي', 'ممكن تجرب تمدد، دش دافي، موسيقى هادية، أو تنفس بطيء لدقايق.'],
    ['master', 'أعمل حاجة بحبها وأتحسن فيها', 'ممكن تختار حاجة صغيرة فيها تعلم أو إنجاز بسيط خارج الشغل، زي طبخ أو رسم أو قراءة.'],
    ['control', 'أقرر أنا أعمل إيه في وقتي', 'ممكن تحجز 20 دقيقة تختار فيها أي حاجة من غير ما حد يطلب منك حاجة.'],
    ['sleep', 'نوم', 'لو التعب جسدي، النوم بدري أو قيلولة قصيرة ممكن يفرق. لو قلة النوم مستمرة، اتكلم مع دكتور.'],
    ['company', 'قعدة مع ناس بحبهم', 'ممكن تتصل أو تقعد مع شخص مريح، من غير ما تكون مضطر تشرح أو تحل حاجة.']
  ];
  var box = document.getElementById('rests');
  RESTS.forEach(function (n) {
    var d = document.createElement('div'); d.className = 'opt';
    var i = document.createElement('input'); i.type = 'radio'; i.name = 'rest'; i.id = 'rest-' + n[0]; i.value = n[0];
    var l = document.createElement('label'); l.setAttribute('for', i.id); l.textContent = n[1];
    d.appendChild(i); d.appendChild(l); box.appendChild(d);
    i.addEventListener('change', function () {
      document.getElementById('hint-text').textContent = n[2];
      document.getElementById('hint-box').hidden = false;
    });
  });
  function label() { var c = form.querySelector('input[name="rest"]:checked'); if (!c) return ''; for (var k = 0; k < RESTS.length; k++) if (RESTS[k][0] === c.value) return RESTS[k][1]; return ''; }
  function buildPrint() {
    var body = document.getElementById('print-body'); body.textContent = '';
    function row(h, t) { var a = document.createElement('h3'); a.textContent = h; var p = document.createElement('p'); p.textContent = t || '—'; body.appendChild(a); body.appendChild(p); }
    row('نوع الراحة', label());
    row('صوت الذنب بيقول', document.getElementById('guilt').value.trim());
    row('جملة أهدى لنفسي', document.getElementById('kind').value.trim());
    row('خطة الراحة', document.getElementById('plan').value.trim());
  }
  window.addEventListener('beforeprint', buildPrint);
  document.getElementById('print-btn').addEventListener('click', function () { buildPrint(); window.print(); });
  document.getElementById('reset-btn').addEventListener('click', function () {
    form.reset(); document.getElementById('hint-box').hidden = true; document.getElementById('print-body').textContent = '';
    status.textContent = 'تم مسح كل اللي كتبته من الصفحة.'; document.getElementById('guilt').focus();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})();
