/* «عندك سؤال؟» — guided helper for drmilladmikhail.com (Arabic pages).
   No AI, no tracking, nothing is stored or sent anywhere. It only points visitors to
   the right article, self-test and book chapter. Articles are matched by chapter from
   /assets/articles-index.json (written by tools/build_articles.py). */
(function () {
  "use strict";
  if (document.documentElement.lang !== "ar" || document.getElementById("helper")) return;

  var BOOK = "https://www.amazon.com/dp/B0HPNCYWWS";
  var CH = {
    1: "الفصل الأول: ليه بنكرر نفس الغلطة؟",
    2: "الفصل التاني: أنماط التعلق الأربعة",
    3: "الفصل التالت: جذورك",
    4: "الفصل الرابع: العلامات الحمرا",
    5: "الفصل الخامس: ليه صعب أمشي؟",
    6: "الفصل السادس: خطة الشفاء 21 يوم",
    7: "الفصل السابع: اختيار صح"
  };
  var TESTS = {
    attach: ["/tests/attachment-style/", "اختبار نمط التعلق"],
    esteem: ["/tests/self-esteem-rosenberg/", "اختبار تقدير الذات"],
    anxiety: ["/tests/anxiety-gad7/", "اختبار القلق (GAD-7)"],
    mood: ["/tests/depression-phq8/", "اختبار المزاج (PHQ-8)"],
    wellbeing: ["/tests/wellbeing-who5/", "مؤشر الرفاهية النفسية (WHO-5)"]
  };

  // Each answer only repeats ideas that are in the book or on the site.
  var Q = [
    { q: "بختار نفس النوع كل مرة", ch: 1, tests: ["attach"],
      a: "ده غالباً نمط اتعلمته، مش غباء ولا ضعف ولا «حظ وحش». فيه أسباب نفسية بتخلي الشخص اللي بيوجعنا يبان مألوف وجذاب، وأول خطوة إنك تشوف النمط بوضوح." },
    { q: "عايز أعرف نمط تعلّقي", ch: 2, tests: ["attach"],
      a: "فيه أربع أنماط تعلق: الآمن، والقلقان، والمتجنب، والخايف المتجنب. ومعظمنا عنده خليط، بس فيه نمط بيظهر أكتر وقت الضغط. ابدأ بالاختبار المجاني، والنتيجة بتطلعلك على طول." },
    { q: "إزاي أعرف إن العلاقة مؤذية؟", ch: 4, tests: [], also: 1,
      a: "العلامات الحمرا غالباً بتظهر بدري. علامة حمرا واحدة، زي التحكم أو الإهانة أو التهديد، كفاية إنك توقف وتراجع العلاقة بجد. وفي الكتاب اختبار كامل يوضحلك إذا كانت علاقتك مؤذية.", safety: true },
    { q: "أنا في علاقة بتوجعني ومش قادر أمشي", ch: 5, tests: [],
      a: "صعوبة إنك تمشي مش ضعف. فيه حاجات بتشدك للعلاقة، زي رابطة الصدمة، والأمل إن الشخص يرجع زي الأول، والخوف من الوحدة. الفصل الخامس بيشرحها وبيساعدك توزن قرارك على الورق.", safety: true },
    { q: "لسه خارج من علاقة ومحتاج أتعافى", ch: 6, tests: ["esteem", "wellbeing"],
      a: "العلاقة المؤذية بتاخد حتة من نفسك، والشفاء إنك ترجّعها خطوة صغيرة كل يوم. في الكتاب خطة 21 يوم بمهمة صغيرة كل يوم. ولو بعدها لسه حاسس بحزن تقيل، ده معناه إنك تستاهل مساعدة من متخصص." },
    { q: "طفولتي ليها علاقة باختياراتي؟", ch: 3, tests: ["attach"],
      a: "البيت بيعلّمنا من بدري الحب بييجي إزاي، وإزاي بنتعامل مع الزعل والخلاف. والرسايل اللي سمعناها وإحنا صغيرين ممكن تفضل تأثر على اختياراتنا. الهدف إنك تفهم، مش إنك تلوم حد." },
    { q: "إزاي أختار شريك حياتي صح؟", ch: 7, tests: ["attach"],
      a: "فيه فرق بين الكيميا والتوافق. الهدوء مش ملل، الهدوء أمان. والطبع الحقيقي بيبان مع الوقت والمواقف، فخد وقتك تراقب بهدوء قبل ما تتعلق." },
    { q: "حاسس بقلق أو ضيق كتير", ch: 0, tests: ["anxiety", "mood", "wellbeing"],
      a: "الاختبارات دي مقاييس علمية معروفة، بتساعدك تفهم حالتك في آخر أسبوعين. هي مش تشخيص، ولو النتيجة عالية أو الضيق مأثر على نومك أو شغلك، كلّم متخصص نفسي." }
  ];

  var articles = [];
  fetch("/assets/articles-index.json").then(function (r) { return r.ok ? r.json() : []; })
    .then(function (d) { articles = Array.isArray(d) ? d : []; }).catch(function () {});

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  var root = el("div", "helper"); root.id = "helper";
  var btn = el("button", "helper-btn", '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/><path d="M9 9h6M9 12h4"/></svg><span>عندك سؤال؟</span>');
  btn.type = "button"; btn.setAttribute("aria-expanded", "false"); btn.setAttribute("aria-controls", "helper-panel");
  var panel = el("div", "helper-panel"); panel.id = "helper-panel"; panel.hidden = true;
  panel.setAttribute("role", "dialog"); panel.setAttribute("aria-modal", "false"); panel.setAttribute("aria-labelledby", "helper-title");
  panel.innerHTML =
    '<div class="hp-head"><p id="helper-title">عندك سؤال؟</p><button type="button" class="hp-close" aria-label="إغلاق">×</button></div>' +
    '<p class="hp-note">ده دليل بيوجّهك للمقال والاختبار والفصل المناسب من الكتاب. مش استشارة ولا تشخيص، ومفيش أي حاجة بتتحفظ.</p>' +
    '<div class="hp-log" aria-live="polite"></div>' +
    '<button type="button" class="hp-sos">محتاج مساعدة دلوقتي أو حاسس إنك في خطر؟</button>';
  root.appendChild(panel); root.appendChild(btn);
  document.body.appendChild(root);

  var log = panel.querySelector(".hp-log");

  function bubble(html, who) { var b = el("div", "hp-msg " + (who || "bot"), html); log.appendChild(b); return b; }
  function showFrom(b) { log.scrollTop = Math.max(0, b.offsetTop - 8); }

  function menu() {
    var wrap = el("div", "hp-choices");
    Q.forEach(function (item, i) {
      var c = el("button", "hp-choice", esc(item.q)); c.type = "button";
      c.addEventListener("click", function () { answer(i); });
      wrap.appendChild(c);
    });
    log.appendChild(wrap);
  }

  function articleFor(ch) {
    var list = articles.filter(function (a) { return a.ch === ch; });
    return list.length ? list[0] : null;
  }

  function answer(i) {
    var item = Q[i];
    var old = log.querySelector(".hp-choices"); if (old) old.remove();
    var asked = bubble(esc(item.q), "me");
    var html = "<p>" + esc(item.a) + "</p>";
    var links = [];
    [item.ch, item.also].forEach(function (ch) {
      var art = ch ? articleFor(ch) : null;
      if (art) links.push('<a href="/articles/' + art.slug + '/">اقرا: ' + esc(art.title) + "</a>");
    });
    (item.tests || []).forEach(function (t) { links.push('<a href="' + TESTS[t][0] + '">جرّب ' + TESTS[t][1] + "</a>"); });
    if (item.ch) links.push('<a href="' + BOOK + '" target="_blank" rel="noopener">بالتفصيل في الكتاب، ' + esc(CH[item.ch]) + "</a>");
    if (!links.some(function (l) { return l.indexOf("/articles/") > -1; })) links.push('<a href="/articles/">كل المقالات</a>');
    html += '<ul class="hp-links"><li>' + links.join("</li><li>") + "</li></ul>";
    if (item.safety) html += '<p class="hp-safe">لو انت خايف على نفسك في العلاقة، أو بتتعرض لأذى أو تهديد، متستناش: اتكلم مع حد بتثق فيه أو متخصص، واضغط على زرار المساعدة تحت عشان تشوف أرقام الطوارئ.</p>';
    bubble(html);
    bubble("عندك سؤال تاني؟");
    menu();
    showFrom(asked);
  }

  function sos() {
    var old = log.querySelector(".hp-choices"); if (old) old.remove();
    var asked = bubble("محتاج مساعدة دلوقتي", "me");
    bubble(
      "<p><b>سلامتك أهم حاجة.</b> لو انت في خطر دلوقتي، أو بتفكر تأذي نفسك، كلّم حد على طول:</p>" +
      '<ul class="hp-links hp-numbers">' +
      '<li>مصر: الخط الساخن للدعم النفسي (وزارة الصحة) <a href="tel:105">105</a></li>' +
      '<li>مصر: الإسعاف <a href="tel:123">123</a>، النجدة <a href="tel:122">122</a></li>' +
      '<li>أمريكا: خط الأزمات النفسية <a href="tel:988">988</a> (اتصال أو رسالة)، الطوارئ <a href="tel:911">911</a></li>' +
      "</ul><p>لو انت في بلد تاني، اتصل برقم الطوارئ عندك. وكمان كلّم حد بتثق فيه وقوله إنك محتاجه جنبك دلوقتي. انت مش لوحدك.</p>"
    );
    bubble("لما تحس إنك أحسن، تقدر تختار أي سؤال:");
    menu();
    showFrom(asked);
  }

  var started = false;
  function open() {
    panel.hidden = false; btn.setAttribute("aria-expanded", "true"); root.classList.add("open");
    if (!started) { started = true; bubble("أهلاً بيك 👋 اختار السؤال اللي أقرب للي في بالك، وأنا أوديك للمكان المناسب في الموقع."); menu(); }
    var first = panel.querySelector(".hp-choice"); if (first) first.focus();
  }
  function close() { panel.hidden = true; btn.setAttribute("aria-expanded", "false"); root.classList.remove("open"); btn.focus(); }

  btn.addEventListener("click", function () { panel.hidden ? open() : close(); });
  panel.querySelector(".hp-close").addEventListener("click", close);
  panel.querySelector(".hp-sos").addEventListener("click", sos);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) close(); });
})();
