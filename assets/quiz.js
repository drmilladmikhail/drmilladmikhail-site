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


  // ---- shareable result card (only for tests without a safety flag: attachment style, self-esteem)
  function wrap(ctx, text, maxW) {
    var words = text.split(/\s+/), lines = [], line = "";
    words.forEach(function (w) {
      var t = line ? line + " " + w : w;
      if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t;
    });
    if (line) lines.push(line);
    return lines;
  }
  function makeCard(title, line) {
    var W = 1080, H = 1350, cv = document.createElement("canvas");
    cv.width = W; cv.height = H;
    var ctx = cv.getContext("2d");
    var g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "#18233a"); g.addColorStop(1, "#2f6f62");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "rgba(226,179,90,.14)";
    ctx.beginPath(); ctx.arc(W - 120, 170, 260, 0, Math.PI * 2); ctx.fill();
    ctx.direction = "rtl"; ctx.textAlign = "center";
    var F = '"IBM Plex Sans Arabic", system-ui, sans-serif';
    var testName = (document.querySelector("h1") || {}).textContent || "";
    testName = testName.split(/[:(：]/)[0].trim();
    ctx.fillStyle = "rgba(255,255,255,.75)"; ctx.font = "500 46px " + F;
    ctx.fillText("نتيجتي في", W / 2, 300);
    ctx.fillStyle = "#e2b35a"; ctx.font = "600 56px " + F;
    ctx.fillText(testName, W / 2, 380);
    ctx.fillStyle = "#ffffff"; ctx.font = "700 104px " + F;
    var y = 600;
    wrap(ctx, title, W - 160).forEach(function (l) { ctx.fillText(l, W / 2, y); y += 130; });
    if (line) {
      ctx.fillStyle = "rgba(255,255,255,.85)"; ctx.font = "400 44px " + F;
      y += 10;
      wrap(ctx, line, W - 200).slice(0, 3).forEach(function (l) { ctx.fillText(l, W / 2, y); y += 66; });
    }
    ctx.fillStyle = "#e2b35a"; ctx.font = "600 50px " + F;
    ctx.fillText("وانت؟ اعرف نتيجتك مجانًا", W / 2, H - 230);
    ctx.fillStyle = "#ffffff"; ctx.font = "500 40px " + F;
    ctx.direction = "ltr";
    ctx.fillText("drmilladmikhail.com" + location.pathname.replace(/\/$/, ""), W / 2, H - 160);
    ctx.direction = "rtl"; ctx.fillStyle = "rgba(255,255,255,.7)"; ctx.font = "400 36px " + F;
    ctx.fillText("د. ميلاد ميخائيل", W / 2, H - 95);
    return cv;
  }
  function addCardButton(title, line) {
    if (cfg.safety || !document.createElement("canvas").getContext) return;
    var box = document.createElement("div");
    box.className = "rcard";
    box.innerHTML = '<button type="button" class="btn primary rcard-make">📸 اعمل كارت نتيجتي للستوري</button>';
    var again = out.querySelector(".again");
    out.insertBefore(box, again);
    box.querySelector(".rcard-make").addEventListener("click", function () {
      var ready = document.fonts && document.fonts.load ? document.fonts.load('700 40px "IBM Plex Sans Arabic"') : Promise.resolve();
      ready.catch(function () {}).then(function () {
        var cv = makeCard(title, line), url = cv.toDataURL("image/png");
        box.innerHTML = '<img class="rcard-img" alt="كارت نتيجتك: ' + title.replace(/"/g, "") + '" width="1080" height="1350" src="' + url + '">' +
          '<div class="actions"><a class="btn primary rcard-dl" download="natiga-drmilladmikhail.png" href="' + url + '">نزّل الكارت</a></div>' +
          '<p class="result-note">نزّله وحطه ستوري أو ابعته لصاحبك. الكارت بيتعمل على جهازك ومش بيتبعت لأي حد.</p>';
        cv.toBlob(function (blob) {
          if (!blob || !navigator.canShare) return;
          var file = new File([blob], "natiga.png", { type: "image/png" });
          if (!navigator.canShare({ files: [file] })) return;
          var b = document.createElement("button");
          b.type = "button"; b.className = "btn"; b.textContent = "شارك الكارت";
          b.addEventListener("click", function () {
            navigator.share({ files: [file], text: "اعمل الاختبار انت كمان: " + location.origin + location.pathname }).catch(function () {});
          });
          box.querySelector(".actions").appendChild(b);
        });
      });
    });
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
      addCardButton(s[0], (s[1].split(/[.،!؟]/)[0] || '').trim());
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
    addCardButton(band[2], '');
  });
})();
