/* «مدينة الأفكار» — a small CBT game. Content: assets/game/data.js.
   Nothing the player types is sent anywhere. Only the list of lit neighbourhoods is kept on this device (localStorage, optional). */
(function () {
  "use strict";
  var D = window.FANOOS, root = document.getElementById("fanoos");
  if (!D || !root) return;
  var KEY = "fanoos-lit-v1", lit = load(), cur = null;

  function load() {
    try { var v = JSON.parse(localStorage.getItem(KEY) || "[]"); return Array.isArray(v) ? v : []; } catch (e) { return []; }
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(lit)); } catch (e) { /* private mode */ } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function ar(n) { return String(n).replace(/\d/g, function (d) { return "٠١٢٣٤٥٦٧٨٩"[d]; }); }
  function isLit(id) { return lit.indexOf(id) > -1; }

  /* A fanoos (Ramadan lantern) drawn in SVG; --glow (0..1) sets how bright its flame is. */
  function lantern(hue, glow, size) {
    return '<svg class="fn-lan" style="--hue:' + hue + ';--glow:' + glow + '" width="' + size + '" viewBox="0 0 60 100" aria-hidden="true">' +
      '<circle class="fn-halo" cx="30" cy="58" r="30"/>' +
      '<path class="fn-metal" d="M30 2v8M22 12h16l-3 8H25z"/>' +
      '<path class="fn-body" d="M18 22h24l6 16-4 34H16l-4-34z"/>' +
      '<path class="fn-glass" d="M21 28h18l4 11-3 27H20l-3-27z"/>' +
      '<ellipse class="fn-flame" cx="30" cy="50" rx="6" ry="11"/>' +
      '<path class="fn-metal" d="M30 22v50M14 39h32M16 72h28l-4 8H20zM26 80h8l-1 8h-6z"/>' +
      '</svg>';
  }

  function stars() {
    var s = "";
    for (var i = 0; i < 26; i++) {
      s += '<i style="right:' + ((i * 37) % 100) + '%;top:' + ((i * 53) % 46) + '%;animation-delay:' + (i % 7) * 0.6 + 's"></i>';
    }
    return '<div class="fn-stars" aria-hidden="true">' + s + "</div>";
  }

  function show(html, focusSel) {
    root.innerHTML = '<div class="fn-sky">' + stars() + html + "</div>";
    var f = root.querySelector(focusSel || "h2");
    if (f) { f.setAttribute("tabindex", "-1"); f.focus({ preventScroll: true }); }
    var top = root.getBoundingClientRect().top;
    if (top < 0) root.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }

  /* ---------------- map ---------------- */
  function map() {
    cur = null;
    var done = lit.length, total = D.worlds.length;
    var houses = D.worlds.map(function (w) {
      var on = isLit(w.id);
      return '<li><button type="button" class="fn-house' + (on ? " on" : "") + '" data-w="' + w.id + '">' +
        lantern(w.hue, on ? 1 : 0.12, 54) +
        '<span class="fn-hname">' + esc(w.place) + "</span>" +
        '<span class="fn-hstate">' + (on ? "منوّر ✓" : "مطفي") + "</span></button></li>";
    }).join("");
    var lead = done === 0
      ? "المدينة دي هي عقلك. كل حارة فيها النور مطفي، لأن فيه فكرة قاسية مسيطرة عليها. ادخل أي حارة، ساعد صاحبها يشوف فكرته بوضوح، والحارة هتنوّر."
      : done < total ? "نوّرت " + ar(done) + " من " + ar(total) + " حارات. كمّل، لسه فيه حارات مستنياك."
        : "المدينة كلها نوّرت. تقدر تلعب أي حارة تاني، أو تشوف حقيبة أدواتك.";
    show(
      '<div class="fn-head"><p class="fn-kicker">لعبة العلاج المعرفي السلوكي</p><h2>مدينة الأفكار</h2><p class="fn-lead">' + lead + "</p></div>" +
      '<div class="fn-meter" role="img" aria-label="الحارات المنوّرة: ' + done + " من " + total + '"><span style="width:' + (done / total * 100) + '%"></span></div>' +
      '<ul class="fn-city">' + houses + "</ul>" +
      '<div class="fn-skyline" aria-hidden="true"></div>' +
      '<div class="fn-actions">' +
      (done === total ? '<button type="button" class="fn-btn fn-primary" data-act="finale">حقيبة أدواتك</button>' : "") +
      '<button type="button" class="fn-btn fn-ghost" data-act="how">إزاي ألعب؟</button>' +
      (done ? '<button type="button" class="fn-btn fn-ghost" data-act="reset">ابدأ من الأول</button>' : "") +
      "</div>" +
      '<div class="fn-how" hidden><ol>' +
      "<li><b>امسك الفخ:</b> اعرف «فخ التفكير» اللي وقعت فيه الشخصية.</li>" +
      "<li><b>حقيقة ولا تخمين؟</b> افرز الأدلة: إيه اللي حصل فعلًا، وإيه اللي مجرد توقع.</li>" +
      "<li><b>الفكرة المتوازنة:</b> اختار فكرة واقعية، مش قاسية ومش وردية.</li>" +
      "<li><b>خطوة صغيرة:</b> اختار تصرف يساعد فعلًا.</li>" +
      "</ol><p>مفيش وقت ولا نقط ولا خسارة. لو اخترت حاجة مش مناسبة، هتعرف ليه وتجرب تاني.</p></div>"
    );
  }

  /* ---------------- a world ---------------- */
  var STAGES = ["امسك الفخ", "حقيقة ولا تخمين؟", "الفكرة المتوازنة", "خطوة صغيرة"];

  function level(id) {
    var w = D.worlds.filter(function (x) { return x.id === id; })[0];
    cur = { w: w, stage: 0 };
    stage();
  }

  function intensity() {
    var w = cur.w;
    return Math.round(w.before - (w.before - w.after) * (cur.stage / STAGES.length));
  }

  function frame(inner) {
    var w = cur.w, v = intensity();
    var dots = STAGES.map(function (s, i) {
      return '<li class="' + (i < cur.stage ? "done" : i === cur.stage ? "now" : "") + '"><span>' + ar(i + 1) + "</span>" + s + "</li>";
    }).join("");
    return '<div class="fn-level" style="--hue:' + w.hue + '">' +
      '<div class="fn-topline"><button type="button" class="fn-back" data-act="map">→ المدينة</button><span class="fn-place">' + esc(w.place) + "</span></div>" +
      '<ol class="fn-steps" aria-label="مراحل الحارة">' + dots + "</ol>" +
      '<div class="fn-scene">' +
      '<div class="fn-lanwrap">' + lantern(w.hue, Math.max(0.12, cur.stage / STAGES.length), 70) + "</div>" +
      '<div class="fn-story"><p class="fn-who"><b>' + esc(w.who) + "</b> · " + esc(w.whoLine) + "</p>" +
      '<p class="fn-sit">' + esc(w.situation) + "</p>" +
      '<blockquote class="fn-thought">«' + esc(w.thought) + "»</blockquote>" +
      '<div class="fn-int" role="img" aria-label="قوة ال' + esc(w.feeling) + " دلوقتي " + v + ' من 10"><span>' + esc(w.feeling) + "</span>" +
      '<div class="fn-bar"><i style="width:' + v * 10 + '%"></i></div><b>' + ar(v) + "/١٠</b></div>" +
      "</div></div>" + inner +
      '<p class="fn-fb" role="status" aria-live="polite"></p></div>';
  }

  function stage() {
    var w = cur.w, s = cur.stage, body = "";
    if (s === 0) {
      body = '<h2 class="fn-q">إيه فخ التفكير اللي ' + esc(w.who) + " وقع فيه؟</h2>" +
        '<div class="fn-cards">' + shuffle(w.trap.options).map(function (k) {
          return '<button type="button" class="fn-card" data-trap="' + k + '"><b>' + esc(D.traps[k].name) + "</b><small>" + esc(D.traps[k].def) + "</small></button>";
        }).join("") + "</div>";
    } else if (s === 1) {
      body = '<h2 class="fn-q">افرز الكلام: حقيقة حصلت، ولا تخمين؟</h2><ul class="fn-ev">' +
        shuffle(w.evidence.map(function (e, i) { return i; })).map(function (i) {
          var e = w.evidence[i];
          return '<li data-i="' + i + '"><p>' + esc(e.t) + '</p><div class="fn-two">' +
            '<button type="button" class="fn-chip" data-ev="' + i + '" data-v="1">حقيقة</button>' +
            '<button type="button" class="fn-chip" data-ev="' + i + '" data-v="0">تخمين</button></div></li>';
        }).join("") + "</ul>";
      cur.sorted = {};
    } else if (s === 2 || s === 3) {
      var list = s === 2 ? w.reframe : w.step;
      body = '<h2 class="fn-q">' + (s === 2 ? "أنهي فكرة أكتر توازن وواقعية؟" : "إيه أنفع خطوة صغيرة دلوقتي؟") + "</h2>" +
        '<div class="fn-cards fn-wide">' + shuffle(list.map(function (o, i) { return i; })).map(function (i) {
          return '<button type="button" class="fn-card" data-opt="' + i + '"><span>' + esc(list[i].t) + "</span></button>";
        }).join("") + "</div>";
    } else {
      return win();
    }
    show(frame(body), ".fn-q");
  }

  function feedback(text, good) {
    var fb = root.querySelector(".fn-fb");
    fb.className = "fn-fb " + (good ? "good" : "soft");
    fb.innerHTML = esc(text);
  }

  function nextButton() {
    var fb = root.querySelector(".fn-fb");
    var b = document.createElement("button");
    b.type = "button"; b.className = "fn-btn fn-primary fn-next"; b.dataset.act = "next";
    b.textContent = cur.stage === STAGES.length - 1 ? "نوّر الحارة" : "كمّل";
    fb.insertAdjacentElement("afterend", b);
    b.focus({ preventScroll: true });
  }

  function lockAll(sel) { root.querySelectorAll(sel).forEach(function (b) { b.disabled = true; }); }

  function pickTrap(btn) {
    var w = cur.w, k = btn.dataset.trap;
    if (k === w.trap.answer) {
      btn.classList.add("right"); lockAll(".fn-card");
      feedback("بالظبط: " + w.trap.why, true); nextButton();
    } else {
      btn.classList.add("miss"); btn.disabled = true;
      feedback("مش ده. «" + D.traps[k].name + "» معناه: " + D.traps[k].def + " اقرا الفكرة تاني وجرّب.", false);
    }
  }

  function pickEvidence(btn) {
    var w = cur.w, i = +btn.dataset.ev, e = w.evidence[i], said = btn.dataset.v === "1";
    var li = btn.closest("li");
    if (said === e.fact) {
      li.classList.add(e.fact ? "is-fact" : "is-guess");
      li.querySelectorAll("button").forEach(function (b) { b.disabled = true; });
      cur.sorted[i] = true;
      feedback(e.fact ? "صح، دي حاجة حصلت فعلًا وتقدر تشوفها." : "صح، ده توقع أو تفسير، مش حاجة حصلت.", true);
      if (Object.keys(cur.sorted).length === w.evidence.length) {
        feedback("حلو! خد بالك: التخمينات هي اللي كانت مغذّية الفكرة، والحقايق بتقول حاجة تانية.", true);
        nextButton();
      }
    } else {
      btn.classList.add("miss");
      feedback(e.fact ? "بص تاني: دي حاجة حصلت فعلًا، مش توقع." : "بص تاني: ده محدش يعرفه أكيد. ده تفسير أو توقع.", false);
    }
  }

  function pickOption(btn) {
    var list = cur.stage === 2 ? cur.w.reframe : cur.w.step, o = list[+btn.dataset.opt];
    if (o.ok) {
      btn.classList.add("right"); lockAll(".fn-card");
      feedback(o.fb, true); nextButton();
    } else {
      btn.classList.add("miss"); btn.disabled = true;
      feedback(o.fb + " جرّب اختيار تاني.", false);
    }
  }

  function win() {
    var w = cur.w;
    if (!isLit(w.id)) { lit.push(w.id); save(); }
    var all = lit.length === D.worlds.length;
    show('<div class="fn-win" style="--hue:' + w.hue + '">' +
      '<div class="fn-lanwrap big">' + lantern(w.hue, 1, 120) + "</div>" +
      "<h2>" + esc(w.place) + " نوّرت</h2>" +
      "<p>" + esc(w.who) + " بدأ ب" + esc(w.feeling) + " قوته " + ar(w.before) + " من ١٠، ودلوقتي بقى " + ar(w.after) + ". الإحساس ماختفاش، بس بقى أخف وأوضح.</p>" +
      '<div class="fn-skill"><span>مهارة جديدة في حقيبتك</span><p>' + esc(w.skill) + "</p></div>" +
      '<div class="fn-actions">' +
      (all ? '<button type="button" class="fn-btn fn-primary" data-act="finale">المدينة كلها نوّرت! شوف حقيبتك</button>'
        : '<button type="button" class="fn-btn fn-primary" data-act="map">ارجع للمدينة</button>') +
      "</div></div>", "h2");
  }

  /* ---------------- finale: toolkit + try it on your own thought ---------------- */
  function finale() {
    var skills = D.worlds.map(function (w) {
      return '<li style="--hue:' + w.hue + '">' + lantern(w.hue, 1, 30) + "<div><b>" + esc(w.place) + "</b><p>" + esc(w.skill) + "</p></div></li>";
    }).join("");
    var trapOpts = Object.keys(D.traps).map(function (k) { return '<option value="' + k + '">' + esc(D.traps[k].name) + "</option>"; }).join("");
    show('<div class="fn-head"><p class="fn-kicker">المدينة كلها نوّرت</p><h2>حقيبة أدواتك</h2>' +
      '<p class="fn-lead">دي المهارات اللي استخدمتها في الحارات الخمسة. كلها جاية من العلاج المعرفي السلوكي، وتقدر تستخدمها في يومك.</p></div>' +
      '<ul class="fn-kit">' + skills + "</ul>" +
      '<form class="fn-own" id="fn-own" novalidate><h3>جرّبها على فكرة من عندك</h3>' +
      '<p class="fn-note">اللي هتكتبه بيفضل على الشاشة بس. مش بيتبعت ولا بيتحفظ.</p>' +
      '<label for="fn-sit">الموقف (حصل إيه بالظبط؟)</label><textarea id="fn-sit" rows="2"></textarea>' +
      '<label for="fn-th">الفكرة اللي جت في بالك</label><textarea id="fn-th" rows="2"></textarea>' +
      '<label for="fn-trap">فخ التفكير (لو فيه)</label><select id="fn-trap"><option value="">مش متأكد</option>' + trapOpts + "</select>" +
      '<label for="fn-fact">حقايق حصلت فعلًا</label><textarea id="fn-fact" rows="2"></textarea>' +
      '<label for="fn-bal">فكرة أكتر توازن</label><textarea id="fn-bal" rows="2"></textarea>' +
      '<label for="fn-step">خطوة صغيرة هعملها</label><textarea id="fn-step" rows="2"></textarea>' +
      '<button type="submit" class="fn-btn fn-primary">جمّع الورقة</button>' +
      '<div class="fn-card-out" hidden></div></form>' +
      '<div class="fn-actions"><button type="button" class="fn-btn fn-ghost" data-act="map">ارجع للمدينة</button>' +
      '<button type="button" class="fn-btn fn-ghost" data-act="reset">ابدأ اللعبة من الأول</button></div>', "h2");
  }

  function ownCard(form) {
    var g = function (id) { return form.querySelector("#" + id).value.trim(); };
    var trap = g("fn-trap") ? D.traps[g("fn-trap")].name : "";
    var rows = [["الموقف", g("fn-sit")], ["الفكرة", g("fn-th")], ["فخ التفكير", trap], ["الحقايق", g("fn-fact")],
      ["الفكرة المتوازنة", g("fn-bal")], ["خطوتي الصغيرة", g("fn-step")]].filter(function (r) { return r[1]; });
    var out = form.querySelector(".fn-card-out");
    out.hidden = false;
    if (!rows.length) { out.innerHTML = "<p>اكتب حاجة واحدة على الأقل، وبعدين دوس «جمّع الورقة».</p>"; return; }
    var text = rows.map(function (r) { return r[0] + ": " + r[1]; }).join("\n");
    out.innerHTML = "<h4>ورقتك</h4><dl>" + rows.map(function (r) { return "<dt>" + r[0] + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl>" +
      '<button type="button" class="fn-btn fn-ghost" data-act="copy">انسخ الورقة</button>';
    out.dataset.text = text + "\n\n— من لعبة «مدينة الأفكار»";
    out.querySelector("h4").setAttribute("tabindex", "-1");
    out.querySelector("h4").focus();
  }

  /* ---------------- events ---------------- */
  root.addEventListener("click", function (ev) {
    var b = ev.target.closest("button");
    if (!b || b.disabled) return;
    if (b.dataset.w) return level(b.dataset.w);
    if (b.dataset.trap) return pickTrap(b);
    if (b.dataset.ev !== undefined) return pickEvidence(b);
    if (b.dataset.opt !== undefined) return pickOption(b);
    var a = b.dataset.act;
    if (a === "next") { cur.stage++; stage(); }
    else if (a === "map") map();
    else if (a === "finale") finale();
    else if (a === "how") { var h = root.querySelector(".fn-how"); h.hidden = !h.hidden; b.setAttribute("aria-expanded", String(!h.hidden)); }
    else if (a === "reset") {
      if (b.dataset.sure) { lit = []; save(); map(); }
      else { b.dataset.sure = "1"; b.textContent = "متأكد؟ دوس تاني"; }
    } else if (a === "copy") {
      var t = b.closest(".fn-card-out").dataset.text;
      var ok = function () { b.textContent = "اتنسخت ✓"; };
      try { navigator.clipboard.writeText(t).then(ok, function () { b.textContent = "حدد النص وانسخه بإيدك"; }); }
      catch (e) { b.textContent = "حدد النص وانسخه بإيدك"; }
    }
  });
  root.addEventListener("submit", function (ev) { ev.preventDefault(); ownCard(ev.target); });

  map();
})();
