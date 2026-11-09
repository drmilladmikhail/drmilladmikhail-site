// Draft: browser only. Nothing is sent, logged or stored.
(function () {
  'use strict';
  var T = [
    { t: '«أكيد المدير هيشوف إن الإيميل كان غلط.»', h: 'سؤال يساعدك: في معلومة فعلية بتقول كده، ولا ده توقع؟ لو توقع، هل في حاجة أقدر أعملها دلوقتي بخصوصه؟' },
    { t: '«لازم أراجع الإيميل تاني الصبح وأصحح لو في غلط.»', h: 'سؤال يساعدك: الفكرة دي بتنتهي بخطوة محددة ووقت. ممكن تبقى تفكير بيحل مشكلة.' },
    { t: '«ليه دايمًا بعمل كده؟ أنا كل مرة بغلط.»', h: 'سؤال يساعدك: «ليه» هنا بترجع بيك للماضي من غير خطوة. هل «دايمًا» و«كل مرة» دقيقة فعلًا؟' },
    { t: '«ماذا لو اتفصلت؟ ماذا لو ما لقيتش شغل؟»', h: 'سؤال يساعدك: كلها احتمالات بعيدة. هل في جزء منها أقدر أستعد له بخطوة صغيرة، ولا بتلف بدون خطوة؟' },
    { t: '«هبعت له رسالة قصيرة بكرة أسأله لو محتاج تعديل.»', h: 'سؤال يساعدك: ده قرار وخطوة. ممكن تكتبه وتسيب الموضوع لبكرة.' }
  ];
  var box = document.getElementById('thoughts'); var st2 = document.getElementById('status2');
  var labels = [['بيوصّل لخطوة', 'step'], ['بيلف في مكانه', 'loop'], ['مش متأكد', 'unsure']];
  T.forEach(function (x, i) {
    var d = document.createElement('div'); d.className = 'tt';
    var p = document.createElement('p'); p.textContent = x.t; d.appendChild(p);
    var seg = document.createElement('div'); seg.className = 'seg'; seg.setAttribute('role', 'group'); seg.setAttribute('aria-label', 'تقييمك للفكرة ' + (i + 1));
    var hint = document.createElement('p'); hint.className = 'fb'; hint.hidden = true; hint.textContent = x.h;
    labels.forEach(function (l) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = l[0]; b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(seg.children, function (c) { c.setAttribute('aria-pressed', c === b ? 'true' : 'false'); });
        hint.hidden = false; st2.textContent = x.h;
      });
      seg.appendChild(b);
    });
    d.appendChild(seg); d.appendChild(hint); box.appendChild(d);
  });
  var form = document.getElementById('tool-form'), status = document.getElementById('status');
  function v(id) { return document.getElementById(id).value.trim(); }
  function build() {
    var body = document.getElementById('print-body'); body.textContent = '';
    function row(h, t) { var a = document.createElement('h3'); a.textContent = h; var p = document.createElement('p'); p.textContent = t || '—'; body.appendChild(a); body.appendChild(p); }
    row('الفكرة اللي بتتكرر', v('thought'));
    var s = form.querySelector('input[name=step]:checked'); row('بتوصّلني لخطوة؟', s ? s.value : '');
    row('الخطوة ومتى', v('act'));
    row('ممكن أجرّب', Array.prototype.map.call(form.querySelectorAll('input[name=alt]:checked'), function (c) { return c.value; }).join('، '));
  }
  window.addEventListener('beforeprint', build);
  document.getElementById('print-btn').addEventListener('click', function () { build(); window.print(); });
  document.getElementById('reset-btn').addEventListener('click', function () {
    form.reset(); document.getElementById('reflect').reset(); document.getElementById('print-body').textContent = '';
    Array.prototype.forEach.call(box.querySelectorAll('button'), function (b) { b.setAttribute('aria-pressed', 'false'); });
    Array.prototype.forEach.call(box.querySelectorAll('.fb'), function (h) { h.hidden = true; });
    status.textContent = 'تم مسح كل اللي كتبته واخترته من الصفحة.'; document.getElementById('thought').focus();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  document.getElementById('reflect').addEventListener('submit', function (e) { e.preventDefault(); });
})();
