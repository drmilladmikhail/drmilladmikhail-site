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
})();