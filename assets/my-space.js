/* Personal progress dashboard. Reads the challenges page's local-only state. */
(function () {
  var status = document.getElementById("journey-status");
  var count = document.getElementById("journey-count");
  var all = document.getElementById("all-count");
  var bar = document.getElementById("journey-bar");
  var track = document.querySelector('[role="progressbar"]');
  var hint = document.getElementById("space-hint");
  var state = {};
  try { state = JSON.parse(localStorage.getItem("dm-challenges") || "{}") || {}; } catch (e) {
    status.textContent = "المتصفح لا يسمح بقراءة التقدم المحفوظ. تقدر تستخدم التحديات بشكل عادي.";
    hint.textContent = "لو التخزين المحلي مقفول، مش هنقدر نعرض تقدمك هنا.";
    return;
  }
  var done = 0;
  for (var n = 1; n <= 7; n++) if (state["seven-day-journey-" + n]) done++;
  var total = Object.keys(state).filter(function (key) { return !!state[key]; }).length;
  count.textContent = done + "/7";
  all.textContent = String(total);
  bar.style.width = Math.round(done / 7 * 100) + "%";
  track.setAttribute("aria-valuenow", String(done));
  status.textContent = done === 7 ? "أحسنت! أنهيت رحلة الأيام السبعة. اختار عادة واحدة تحب تكمل عليها." : done === 0 ? "لسه ما بدأتش الرحلة. أول خطوة صغيرة كفاية." : "أنجزت " + done + " من 7 أيام. كمل على مهلك ومن غير ضغط.";
  hint.textContent = done === 7 ? "الإنجاز مش نهاية الطريق؛ خليك مع الخطوات اللي كانت مفيدة ليك." : "تقدر تكمل من آخر نقطة وقفت عندها من صفحة التحديات.";

  var challenges = [
    { id: "seven-day-journey", title: "7 أيام أقرب لنفسك", total: 7 },
    { id: "kind-voice", title: "من غير جلد للذات", total: 7 },
    { id: "gratitude", title: "5 أيام امتنان", total: 5 },
    { id: "sleep", title: "نوم منتظم", total: 7 },
    { id: "small-no", title: "حدود صحية", total: 3 },
    { id: "less-scrolling", title: "سوشيال ميديا أقل", total: 7 },
    { id: "reach-out", title: "التواصل مع الآخرين", total: 5 },
    { id: "urge-awareness", title: "وعي بالعادات", total: 7 }
  ];
  var list = document.getElementById("space-challenge-list");
  if (list) {
    list.textContent = "";
    var started = 0;
    challenges.forEach(function (item) {
      var completed = 0;
      for (var i = 1; i <= item.total; i++) if (state[item.id + "-" + i]) completed++;
      if (!completed) return;
      started++;
      var card = document.createElement("article");
      card.className = "space-challenge-item";
      var heading = document.createElement("div");
      heading.className = "space-challenge-heading";
      var title = document.createElement("b");
      title.textContent = item.title;
      var number = document.createElement("span");
      number.textContent = completed + " / " + item.total;
      heading.appendChild(title); heading.appendChild(number);
      var progress = document.createElement("div");
      progress.className = "space-mini-track";
      progress.setAttribute("role", "progressbar");
      progress.setAttribute("aria-label", "تقدم " + item.title);
      progress.setAttribute("aria-valuemin", "0");
      progress.setAttribute("aria-valuemax", String(item.total));
      progress.setAttribute("aria-valuenow", String(completed));
      var fill = document.createElement("span");
      fill.style.width = Math.round(completed / item.total * 100) + "%";
      progress.appendChild(fill);
      card.appendChild(heading); card.appendChild(progress);
      list.appendChild(card);
    });
    if (!started) {
      var empty = document.createElement("p");
      empty.className = "space-empty";
      empty.textContent = "لسه مفيش تحديات بدأت فيها. اختار تحديًا بسيطًا وابدأ وقت ما تكون جاهز.";
      list.appendChild(empty);
    }
  }
})();