// Self-assessment scoring for /tests/ pages. Runs only in the browser; nothing is sent or stored.
(function () {
  var form = document.getElementById('quiz');
  var out = document.getElementById('result');
  var cfgEl = document.getElementById('quiz-config');
  if (!form || !out || !cfgEl) return;
  var cfg = JSON.parse(cfgEl.textContent);
  var err = form.querySelector('.quiz-error');

  function bar(label, value, min, max, note) {
    var pct = Math.round(((value - min) / (max - min)) * 100);
    return '<div class="meter"><div class="meter-top"><span>' + label + '</span><b>' + note + '</b></div>' +
      '<div class="meter-track"><span style="width:' + pct + '%"></span></div></div>';
  }

  function render(html) {
    out.innerHTML = html + '<button type="button" class="btn again">أعد الاختبار</button>';
    out.hidden = false;
    out.querySelector('.again').addEventListener('click', function () {
      form.reset(); out.hidden = true; form.hidden = false;
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    form.hidden = true;
    out.focus({ preventScroll: true });
    out.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  form.addEventListener('change', function (e) {
    var fs = e.target.closest('.q');
    if (fs) fs.classList.add('done');
    if (err) err.hidden = true;
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var qs = form.querySelectorAll('.q');
    var missing = null;
    qs.forEach(function (q) {
      var c = q.querySelector('input:checked');
      q.classList.toggle('missing', !c);
      if (!c && !missing) missing = q;
    });
    if (missing) {
      if (err) err.hidden = false;
      missing.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    if (cfg.kind === 'ecr') {
      var sums = { avoid: 0, anx: 0 }, counts = { avoid: 0, anx: 0 };
      qs.forEach(function (q) {
        var v = parseInt(q.querySelector('input:checked').value, 10);
        if (q.dataset.rev === '1') v = 8 - v;
        sums[q.dataset.sub] += v; counts[q.dataset.sub] += 1;
      });
      var av = sums.avoid / counts.avoid, an = sums.anx / counts.anx;
      var key = an > 4 ? (av > 4 ? 'fearful' : 'anxious') : (av > 4 ? 'avoidant' : 'secure');
      var s = cfg.styles[key];
      render('<p class="result-kicker">نمطك أقرب لـ</p><h2>' + s[0] + '</h2><p>' + s[1] + '</p>' +
        bar('قلق التعلق (الخوف من الرفض والهجر)', an, 1, 7, an.toFixed(1) + ' من 7') +
        bar('تجنب التعلق (البعد عن القرب والاعتماد)', av, 1, 7, av.toFixed(1) + ' من 7') +
        '<p class="result-note">نمط التعلق مش حكم نهائي ولا عيب فيك، وممكن يتغير مع الوعي والعلاقات الآمنة. معظمنا فيه حاجة من أكتر من نمط.</p>');
      return;
    }

    var total = 0;
    qs.forEach(function (q) { total += parseInt(q.querySelector('input:checked').value, 10); });
    total = total * (cfg.multiplier || 1);
    var band = cfg.bands.filter(function (b) { return total >= b[0] && total <= b[1]; })[0] || cfg.bands[cfg.bands.length - 1];
    var high = cfg.safety && band[4] === true;
    render('<p class="result-kicker">نتيجتك</p><h2>' + band[2] + '</h2>' +
      bar('درجتك', total, 0, cfg.max, total + ' من ' + cfg.max) +
      '<p>' + band[3] + '</p>' +
      (high ? '<p class="result-alert">لو حاسس إنك مش قادر تتحمل، أو عندك أفكار إنك تأذي نفسك، اطلب مساعدة دلوقتي: في مصر الخط الساخن للدعم النفسي 105، وفي أمريكا 988، أو أقرب طوارئ.</p>' : '') +
      '<p class="result-note">النتيجة دي مؤشر مش تشخيص. لو قلقان من نتيجتك، أحسن خطوة إنك تتكلم مع متخصص نفسي.</p>');
  });
})();
