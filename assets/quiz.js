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
  function rrect(ctx, x, y, w, h, r) {
    if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); return; }
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }
  // spec: {title, line, bars:[{label, pct (0..1), val}]}
  function makeCard(title, line, bars) {
    var W = 1080, H = 1350, cv = document.createElement("canvas");
    cv.width = W; cv.height = H;
    var ctx = cv.getContext("2d");
    var g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "#141f33"); g.addColorStop(1, "#2f6f62");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // decorative shapes
    ctx.fillStyle = "rgba(226,179,90,.10)";
    ctx.beginPath(); ctx.arc(W + 40, 120, 300, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,.05)";
    ctx.beginPath(); ctx.arc(-60, H - 380, 240, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "rgba(226,179,90,.35)"; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(90, H - 330); ctx.lineTo(W - 90, H - 330); ctx.stroke();
    ctx.direction = "rtl"; ctx.textAlign = "center";
    var F = '"IBM Plex Sans Arabic", system-ui, sans-serif';
    var testName = (document.querySelector("h1") || {}).textContent || "";
    testName = testName.split(/[:(：]/)[0].trim();
    // header
    ctx.fillStyle = "rgba(255,255,255,.75)"; ctx.font = "500 44px " + F;
    ctx.fillText("نتيجتي في", W / 2, 250);
    ctx.fillStyle = "#e2b35a"; ctx.font = "600 58px " + F;
    ctx.fillText(testName, W / 2, 335);
    // title (up to 2 lines)
    var y = 500;
    ctx.fillStyle = "#ffffff"; ctx.font = "700 96px " + F;
    var tl = wrap(ctx, title, W - 180).slice(0, 2);
    tl.forEach(function (l) { ctx.fillText(l, W / 2, y); y += 120; });
    // bars
    if (bars && bars.length) {
      y += 40;
      bars.slice(0, 2).forEach(function (b) {
        ctx.textAlign = "right"; ctx.fillStyle = "rgba(255,255,255,.88)"; ctx.font = "500 40px " + F;
        ctx.fillText(b.label, W - 90, y);
        ctx.textAlign = "left"; ctx.fillStyle = "#e2b35a"; ctx.font = "600 40px " + F;
        ctx.fillText(b.val, 90, y);
        ctx.textAlign = "center";
        var bx = 90, bw = W - 180, by = y + 26, bh = 30;
        ctx.fillStyle = "rgba(255,255,255,.16)";
        rrect(ctx, bx, by, bw, bh, 15); ctx.fill();
        var fg = ctx.createLinearGradient(bx, 0, bx + bw, 0);
        fg.addColorStop(0, "#c9973f"); fg.addColorStop(1, "#e2b35a");
        ctx.fillStyle = fg;
        var fw = Math.max(bh, Math.round(bw * Math.min(1, Math.max(0, b.pct))));
        rrect(ctx, bx + bw - fw, by, fw, bh, 15); ctx.fill(); // fills from the right (RTL)
        y += 150;
      });
    }
    // line
    if (line) {
      ctx.fillStyle = "rgba(255,255,255,.85)"; ctx.font = "400 42px " + F;
      y = Math.max(y + 10, 900);
      wrap(ctx, line, W - 220).slice(0, 3).forEach(function (l) { ctx.fillText(l, W / 2, y); y += 64; });
    }
    // footer
    ctx.fillStyle = "#e2b35a"; ctx.font = "600 48px " + F;
    ctx.fillText("وانت؟ اعرف نتيجتك مجانًا", W / 2, H - 235);
    ctx.fillStyle = "#ffffff"; ctx.font = "500 40px " + F;
    ctx.direction = "ltr";
    ctx.fillText("drmilladmikhail.com" + location.pathname.replace(/\/$/, ""), W / 2, H - 165);
    ctx.direction = "rtl"; ctx.fillStyle = "rgba(255,255,255,.7)"; ctx.font = "400 36px " + F;
    ctx.fillText("د. ميلاد ميخائيل", W / 2, H - 100);
    return cv;
  }
  function addCardButton(title, line, bars) {
    if ((cfg.safety && cfg.kind !== 'multi') || cfg.private || !document.createElement("canvas").getContext) return;
    var box = document.createElement("div");
    box.className = "rcard";
    box.innerHTML = '<button type="button" class="btn primary rcard-make">📸 اعمل كارت نتيجتي للستوري</button>';
    var again = out.querySelector(".again");
    out.insertBefore(box, again);
    box.querySelector(".rcard-make").addEventListener("click", function () {
      var ready = document.fonts && document.fonts.load ? document.fonts.load('700 40px "IBM Plex Sans Arabic"') : Promise.resolve();
      ready.catch(function () {}).then(function () {
        var cv = makeCard(title, line, bars), url = cv.toDataURL("image/png");
        box.innerHTML = '<img class="rcard-img" alt="كارت نتيجتك: ' + title.replace(/"/g, "") + '" width="1080" height="1350" src="' + url + '">' +
          '<div class="actions"><a class="btn primary rcard-dl" download="natiga-drmilladmikhail.png" href="' + url + '">نزّل الكارت</a>' +
          '<button type="button" class="btn rcard-link">انسخ رابط الاختبار</button></div>' +
          '<p class="result-note">نزّله وحطه ستوري أو ابعته لصاحبك. الكارت بيتعمل على جهازك ومش بيتبعت لأي حد.</p>';
        var linkBtn = box.querySelector(".rcard-link");
        if (linkBtn && navigator.clipboard) linkBtn.addEventListener("click", function () {
          navigator.clipboard.writeText("اعمل الاختبار انت كمان: " + location.origin + location.pathname).then(function () {
            linkBtn.textContent = "اتنسخ ✓";
            setTimeout(function () { linkBtn.textContent = "انسخ رابط الاختبار"; }, 1800);
          }).catch(function () {});
        });
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

  var qpN = document.querySelector('.qp-n'), qpBar = document.querySelector('.qp-bar');
  function progress() {
    var all = form.querySelectorAll('.q').length, done = form.querySelectorAll('.q.done').length;
    if (qpN) qpN.textContent = done;
    if (qpBar) qpBar.style.width = Math.round(done / all * 100) + '%';
  }
  form.addEventListener('change', function (e) {
    var fs = e.target.closest('.q');
    if (fs) {
      fs.classList.add('done'); fs.classList.remove('missing');
      // gently move to the next unanswered question
      var next = fs.nextElementSibling;
      if (next && next.classList.contains('q') && !next.classList.contains('done') && window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
        setTimeout(function () { next.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 180);
      }
    }
    if (err) err.hidden = true;
    progress();
  });
  form.addEventListener('reset', function () {
    setTimeout(function () { form.querySelectorAll('.q').forEach(function (q) { q.classList.remove('done', 'missing'); }); progress(); }, 0);
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
      addCardButton(s[0], (s[1].split(/[.،!؟]/)[0] || '').trim(), [
        { label: 'قلق التعلق', pct: (an - 1) / 6, val: an.toFixed(1) + ' من 7' },
        { label: 'تجنب التعلق', pct: (av - 1) / 6, val: av.toFixed(1) + ' من 7' }
      ]);
      return;
    }

    if (cfg.kind === 'multi') {
      var acc = {};
      qs.forEach(function (q) {
        var k = q.dataset.sub, v = parseFloat(q.querySelector('input:checked').value);
        acc[k] = acc[k] || { s: 0, n: 0 }; acc[k].s += v; acc[k].n += 1;
      });
      var res = cfg.scales.map(function (sc) {
        var a = acc[sc.key], v = sc.agg === 'sum' ? a.s : a.s / a.n;
        var band = sc.bands.filter(function (b) { return v >= b[0] - 1e-9; }).pop();
        return { sc: sc, v: v, band: band, rel: (v - sc.min) / (sc.max - sc.min) };
      });
      var anyHigh = res.some(function (r) { return r.band[3] === true; });
      var html;
      if (res.length === 1) {
        var r0 = res[0];
        html = '<p class="result-kicker">نتيجتك</p><h2>' + r0.band[1] + '</h2>' +
          bar(r0.sc.name, r0.v, r0.sc.min, r0.sc.max, r0.v.toFixed(r0.sc.dec) + ' من ' + r0.sc.max) +
          '<p>' + r0.band[2] + '</p>';
      } else {
        html = '<p class="result-kicker">نتيجتك</p><h2>' + (cfg.result_title || 'نتيجتك') + '</h2>' +
          res.map(function (r) {
            return '<div class="scale-res">' + bar(r.sc.name, r.v, r.sc.min, r.sc.max, r.band[1] + ' · ' + r.v.toFixed(r.sc.dec) + ' من ' + r.sc.max) +
              '<p>' + r.band[2] + '</p></div>';
          }).join('');
      }
      if (anyHigh && cfg.safety) html += '<p class="result-alert">لو حاسس إنك مش قادر تتحمل، أو عندك أفكار إنك تأذي نفسك، اطلب مساعدة دلوقتي: في مصر الخط الساخن للدعم النفسي 105، وفي أمريكا 988، أو أقرب طوارئ.</p>';
      html += '<p class="result-note">النتيجة دي مؤشر يساعدك تفهم نفسك، مش تشخيص. لو قلقان من نتيجتك، أحسن خطوة إنك تتكلم مع متخصص نفسي.</p>';
      render(html);
      if (cfg.card === 'first') addCardButton(res[0].band[1], (res[0].band[2].split(/[.،!؟]/)[0] || '').trim(), [
        { label: res[0].sc.name, pct: res[0].rel, val: res[0].v.toFixed(res[0].sc.dec) + ' من ' + res[0].sc.max }
      ]);
      else if (cfg.card === 'top') {
        var top = res.slice().sort(function (a, b) { return b.rel - a.rel; })[0];
        addCardButton('أعلى سمة عندي: ' + top.sc.name, (top.band[2].split(/[.،!؟]/)[0] || '').trim(), [
          { label: top.sc.name, pct: top.rel, val: top.v.toFixed(top.sc.dec) + ' من ' + top.sc.max }
        ]);
      }
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
    addCardButton(band[2], '', [{ label: 'درجتك', pct: total / cfg.max, val: total + ' من ' + cfg.max }]);
  });
})();
