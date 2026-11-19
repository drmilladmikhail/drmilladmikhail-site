/* «بطاريتي 1%» — a one-day energy game. Content: assets/game/data.js.
   Nothing is sent or stored: choices live in page memory only. */
(function () {
  "use strict";
  var G = window.BATTERY_GAME, root = document.getElementById("battery-game");
  if (!G || !root) return;
  var SITE = "drmilladmikhail.com/game";
  var st;

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  /* keep «1%» / «+10%» the right way round inside Arabic text */
  function num(html) {  // text only: tags (style="width:60%", aria-label) are skipped
    return String(html).replace(/(<[^>]*>)|([+\-\u2212]?\d+%)/g, function (m, tag, n) { return tag || '<span dir="ltr" class="bg-n">' + n + "</span>"; });
  }
  function iso(t) { return String(t).replace(/([+\-\u2212]?\d+%)/g, "\u2066$1\u2069"); }
  function clamp(v) { return Math.max(1, Math.min(100, v)); }
  function level(p) { return p <= 20 ? "low" : p <= 45 ? "mid" : "ok"; }
  function ampm(s) { return s.part === "dawn" || s.part === "morning" ? "ص" : "م"; }
  function reduced() { return window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches; }

  function battery(p, big) {
    return '<span class="bg-bat' + (big ? " big" : "") + " " + level(p) + '" role="img" aria-label="البطارية ' + p + '%">' +
      '<span class="bg-bat-body"><span class="bg-bat-fill" style="width:' + p + '%"></span></span><span class="bg-bat-cap"></span></span>';
  }

  function statusBar(time, p) {
    return '<div class="bg-status"><span class="bg-clock">' + esc(time) + '</span>' +
      '<span class="bg-pct"><b>' + p + "%</b>" + battery(p) + "</span></div>";
  }

  function render(part, html, focusSel) {
    root.className = "bgame sky-" + part;
    root.innerHTML = num(html);
    var f = root.querySelector(focusSel || "h2");
    if (f) { f.setAttribute("tabindex", "-1"); f.focus({ preventScroll: true }); }
    if (root.getBoundingClientRect().top < 0) root.scrollIntoView({ behavior: reduced() ? "auto" : "smooth" });
  }

  /* ---------- start ---------- */
  function shuffle(a) {
    a = a.slice();
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }

  /* Build a day: one random variant per time slot (never the same one as last time), choices shuffled. */
  var lastPick = null, days = 0;
  function newDay() {
    var pick = G.slots.map(function (slot, n) {
      var ids = slot.variants.map(function (v, k) { return k; });
      if (lastPick && ids.length > 1) ids = ids.filter(function (k) { return k !== lastPick[n]; });
      return ids[Math.floor(Math.random() * ids.length)];
    });
    lastPick = pick;
    return G.slots.map(function (slot, n) {
      var v = slot.variants[pick[n]];
      return { time: slot.time, part: slot.part, text: v.text, choices: shuffle(v.choices) };
    });
  }

  function intro() {
    days++;
    st = { p: G.start, i: 0, log: [], trail: [G.start], warned: false, day: newDay() };
    render("dawn",
      statusBar("6:55 ص", G.start) +
      '<div class="bg-intro">' + battery(G.start, true) +
      '<p class="bg-kicker">' + (days > 1 ? "يوم جديد، بمواقف جديدة" : "لعبة من كتاب «بطاريتي 1%»") + "</p><h2>يومك بيبدأ والبطارية " + G.start + "%</h2>" +
      "<p>هتعيش يوم كامل في " + st.day.length + " موقف. كل اختيار يا بيشحن بطاريتك، يا بيسحب منها. وفي آخر اليوم هتعرف إيه اللي بيستنزفك، وإيه اللي بيشحنك بجد.</p>" +
      '<button type="button" class="bg-btn bg-go" data-act="go">ابدأ يومك</button>' +
      '<p class="bg-small">مفيش تسجيل، واختياراتك مش بتتبعت لأي حد.</p></div>');
  }

  /* ---------- a scene ---------- */
  function scene() {
    var s = st.day[st.i];
    var opts = s.choices.map(function (c, k) {
      return '<button type="button" class="bg-choice" data-k="' + k + '">' + esc(c.t) + "</button>";
    }).join("");
    render(s.part,
      statusBar(s.time + " " + ampm(s), st.p) +
      '<div class="bg-progress" aria-hidden="true"><span style="width:' + (st.i / st.day.length * 100) + '%"></span></div>' +
      '<div class="bg-note"><span class="bg-note-head"><i></i>يومك · ' + esc(s.time) + " " + ampm(s) + '</span><h2>' + esc(s.text) + "</h2></div>" +
      '<p class="bg-ask">هتعمل إيه؟</p><div class="bg-choices">' + opts + "</div>" +
      '<div class="bg-out" role="status" aria-live="polite"></div>');
  }

  function choose(k) {
    var s = st.day[st.i], c = s.choices[k], before = st.p;
    st.p = clamp(st.p + c.d);
    st.trail.push(st.p);
    st.log.push({ scene: st.i, k: k, d: st.p - before, raw: c.d, c: c.c });
    root.querySelectorAll(".bg-choice").forEach(function (b, n) {
      b.disabled = true;
      if (n === k) b.classList.add("picked");
    });
    var sign = c.d > 0 ? "plus" : c.d < 0 ? "minus" : "zero";
    var chip = c.d > 0 ? "+" + c.d + "% شحن" : c.d < 0 ? "−" + Math.abs(c.d) + "% سحب" : "مفيش تغيير";
    var low = "";
    if (st.p <= 20 && !st.warned) {
      st.warned = true;
      low = '<div class="bg-low"><b>البطارية ضعيفة: ' + st.p + "%</b><span>مش لازم تخلّص اليوم وإنت فاضي. شوف في المواقف الجاية فين ممكن تشحن.</span></div>";
    }
    var out = root.querySelector(".bg-out");
    out.innerHTML = num('<p class="bg-chip ' + sign + '">' + chip + "</p><p class=\"bg-why\">" + esc(c.why) + "</p>" + low +
      '<button type="button" class="bg-btn" data-act="next">' + (st.i === st.day.length - 1 ? "خلّص اليوم" : "كمّل اليوم") + "</button>");
    // update the status bar battery
    var pct = root.querySelector(".bg-pct");
    pct.innerHTML = num("<b>" + st.p + "%</b>") + battery(st.p);
    pct.classList.remove("pulse"); void pct.offsetWidth; pct.classList.add("pulse");
    out.querySelector("button").focus({ preventScroll: true });
  }

  /* ---------- end of the day ---------- */
  function sums() {
    var t = {};
    st.log.forEach(function (e) { t[e.c] = (t[e.c] || 0) + e.raw; });
    var arr = Object.keys(t).map(function (k) { return { c: k, v: t[k] }; });
    return {
      drains: arr.filter(function (x) { return x.v < 0; }).sort(function (a, b) { return a.v - b.v; }).slice(0, 3),
      charges: arr.filter(function (x) { return x.v > 0; }).sort(function (a, b) { return b.v - a.v; }).slice(0, 3)
    };
  }

  function tips() {
    // the 3 scenes where the picked choice cost the most → show that scene's best charger
    return st.log.filter(function (e) {
      var best = Math.max.apply(null, st.day[e.scene].choices.map(function (c) { return c.d; }));
      return e.raw < best;
    }).sort(function (a, b) { return a.raw - b.raw; }).slice(0, 3).map(function (e) {
      var s = st.day[e.scene], best = s.choices.slice().sort(function (a, b) { return b.d - a.d; })[0];
      return { when: s.time + " " + ampm(s), text: best.t, gain: best.d };
    });
  }

  function chart() {
    var w = 320, h = 110, pad = 8, n = st.trail.length - 1;
    var pts = st.trail.map(function (v, i) {
      return [pad + (w - 2 * pad) * (1 - i / n), h - pad - (h - 2 * pad) * (v / 100)];
    });
    var line = pts.map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" ");
    var area = "M" + pts[0][0] + "," + (h - pad) + " L" + line.replace(/ /g, " L") + " L" + pts[n][0] + "," + (h - pad) + " Z";
    var last = pts[n];
    return '<svg class="bg-chart" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="البطارية خلال اليوم: بدأت ' + st.trail[0] + "% وخلصت " + st.p + '%">' +
      '<line x1="' + pad + '" x2="' + (w - pad) + '" y1="' + (h - pad - (h - 2 * pad) * 0.2) + '" y2="' + (h - pad - (h - 2 * pad) * 0.2) + '" class="bg-chart-low"/>' +
      '<path d="' + area + '" class="bg-chart-area"/><polyline points="' + line + '" class="bg-chart-line"/>' +
      '<circle cx="' + last[0] + '" cy="' + last[1] + '" r="5" class="bg-chart-dot"/></svg>' +
      '<div class="bg-chart-axis"><span>الصبح</span><span>بالليل</span></div>';
  }

  function ending() {
    var e = G.endings.filter(function (x) { return st.p >= x.min; })[0];
    st.ending = e;
    var s = sums(), t = tips();
    var list = function (arr, cls) {
      return arr.length ? "<ul class=\"bg-tags " + cls + "\">" + arr.map(function (x) { return "<li>" + esc(G.cats[x.c]) + " <b>" + (x.v > 0 ? "+" : "−") + Math.abs(x.v) + "%</b></li>"; }).join("") + "</ul>"
        : '<p class="bg-small">ولا حاجة النهارده.</p>';
    };
    render("late",
      statusBar("11:59 م", st.p) +
      '<div class="bg-end">' + battery(st.p, true) +
      '<p class="bg-kicker">آخر اليوم · بطاريتك ' + st.p + "%</p><h2>" + esc(e.title) + "</h2><p>" + esc(e.text) + "</p>" +
      '<div class="bg-card"><h3>بطاريتك خلال اليوم</h3>' + chart() + "</div>" +
      '<div class="bg-two"><div class="bg-card"><h3>أكتر حاجات سحبت منك</h3>' + list(s.drains, "drain") + "</div>" +
      '<div class="bg-card"><h3>أكتر حاجات شحنتك</h3>' + list(s.charges, "charge") + "</div></div>" +
      (t.length ? '<div class="bg-card bg-tips"><h3>جرّب بكرة بدلهم</h3><ol>' + t.map(function (x) {
        return "<li><span>" + esc(x.when) + "</span>" + esc(x.text) + " <b>+" + x.gain + "%</b></li>";
      }).join("") + "</ol></div>" : "") +
      '<div class="bg-actions"><button type="button" class="bg-btn" data-act="share">صورة لنتيجتك</button>' +
      '<button type="button" class="bg-btn bg-ghost" data-act="again">عيش يوم جديد</button></div>' +
      '<div class="bg-share" hidden></div>' +
      '<div class="bg-card bg-book"><h3>الحكاية مكمّلة في الكتاب</h3><p>«بطاريتي 1%: إزاي تشحن روحك من جديد وتلاقي معنى لحياتك». تمارين وقصص ورسومات بالعامية المصرية.</p>' +
      '<a class="bg-link" href="/battery/">اعرف أكتر عن الكتاب</a></div>' +
      "</div>");
  }

  /* ---------- share image (canvas, made on the device) ---------- */
  function shareImage() {
    var box = root.querySelector(".bg-share");
    box.hidden = false;
    box.innerHTML = '<p class="bg-small">بجهّز الصورة…</p>';
    var ready = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    ready.then(function () {
      var W = 1080, H = 1350, cv = document.createElement("canvas");
      cv.width = W; cv.height = H;
      var x = cv.getContext("2d");
      var g = x.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, "#1b2a4a"); g.addColorStop(1, "#0b1322");
      x.fillStyle = g; x.fillRect(0, 0, W, H);
      x.direction = "rtl"; x.textAlign = "center";
      var font = function (wt, px, fam) { x.font = wt + " " + px + "px " + (fam || '"IBM Plex Sans Arabic", Tahoma, sans-serif'); };
      x.fillStyle = "#e8b85a"; font(600, 40); x.fillText(iso("لعبة «بطاريتي 1%»"), W / 2, 150);
      // battery
      var p = st.p, col = p <= 20 ? "#ef6b5b" : p <= 45 ? "#e8b85a" : "#4cc38a";
      var bw = 560, bh = 250, bx = (W - bw) / 2 - 20, by = 260;
      x.lineWidth = 16; x.strokeStyle = "#e9eef5";
      roundRect(x, bx, by, bw, bh, 44); x.stroke();
      x.fillStyle = "#e9eef5"; roundRect(x, bx + bw + 14, by + 80, 34, 90, 12); x.fill();
      x.fillStyle = col; roundRect(x, bx + 22, by + 22, Math.max(30, (bw - 44) * p / 100), bh - 44, 14); x.fill();
      x.fillStyle = "#ffffff"; font(700, 150); x.fillText(p + "%", W / 2, 720);
      x.fillStyle = "#ffffff"; font(700, 96, '"Noto Naskh Arabic", serif'); x.fillText(iso(st.ending.title), W / 2, 880);
      x.fillStyle = "#b9c4d3"; font(400, 40); x.fillText("عشت يوم كامل، وده اللي فضل في بطاريتي.", W / 2, 980);
      x.fillText("جرّب إنت وشوف بطاريتك هتخلص على كام؟", W / 2, 1040);
      x.fillStyle = "#e8b85a"; font(600, 44); x.fillText(SITE, W / 2, 1210);
      cv.toBlob(function (blob) {
        var url = cv.toDataURL("image/png"); // data: URL (the site CSP allows data: images, not blob:)
        var file = null;
        try { file = new File([blob], "battery-" + p + ".png", { type: "image/png" }); } catch (e) { /* old browser */ }
        var canShare = file && navigator.canShare && navigator.canShare({ files: [file] });
        box.innerHTML = '<img src="' + url + '" alt="صورة نتيجتك: البطارية ' + p + "% — " + esc(st.ending.title) + '" width="540" height="675">' +
          '<div class="bg-actions">' + (canShare ? '<button type="button" class="bg-btn" data-act="native">شارك الصورة</button>' : "") +
          '<a class="bg-btn bg-ghost" href="' + url + '" download="battery-' + p + '.png">نزّل الصورة</a></div>' +
          '<p class="bg-small">لو الزرار مش شغال، دوس على الصورة مطوّل واحفظها.</p>';
        box._file = file;
      }, "image/png");
    });
  }
  function roundRect(x, a, b, w, h, r) {
    x.beginPath(); x.moveTo(a + r, b); x.arcTo(a + w, b, a + w, b + h, r); x.arcTo(a + w, b + h, a, b + h, r);
    x.arcTo(a, b + h, a, b, r); x.arcTo(a, b, a + w, b, r); x.closePath();
  }

  /* ---------- events ---------- */
  root.addEventListener("click", function (ev) {
    var b = ev.target.closest("button");
    if (!b || b.disabled) return;
    if (b.dataset.k !== undefined) return choose(+b.dataset.k);
    var a = b.dataset.act;
    if (a === "go") scene();
    else if (a === "next") { st.i++; st.i < st.day.length ? scene() : ending(); }
    else if (a === "again") intro();
    else if (a === "share") shareImage();
    else if (a === "native") {
      var f = root.querySelector(".bg-share")._file;
      navigator.share({ files: [f], title: "بطاريتي 1%", text: "بطاريتي خلصت اليوم على " + st.p + "%. جرّب إنت: https://" + SITE + "/" })
        .catch(function () { /* cancelled */ });
    }
  });

  intro();
})();
