/* Challenges page: remembers ticked days on this device only (localStorage).
   Nothing is sent anywhere. If storage is blocked, ticking still works for the visit. */
(function () {
  var KEY = "dm-challenges";
  var state = {};
  try { state = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { state = {}; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function progress(id) {
    var p = document.querySelector('.ch-progress[data-for="' + id + '"]');
    if (!p) return;
    var total = +p.getAttribute("data-total"), done = 0;
    for (var n = 1; n <= total; n++) if (state[id + "-" + n]) done++;
    p.textContent = done === 0 ? "" : done === total ? "🎉 خلّصت التحدي! شاركه مع حد يحتاجه." : "خلّصت " + done + " من " + total;
    if (id === "seven-day-journey") {
      var bar = document.querySelector("[data-journey-bar]");
      var badge = document.querySelector("[data-journey-badge]");
      if (bar) bar.style.width = Math.round((done / total) * 100) + "%";
      if (badge) badge.hidden = done !== total;
      p.textContent = done === 0 ? "لسه ما بدأتش — اختار أول خطوة." : done === total ? "🎉 7 من 7 — أحسنت، كملت الرحلة!" : "أنجزت " + done + " من 7 أيام · كمل على مهلك.";
    }
  }
  document.querySelectorAll(".challenge input[type=checkbox]").forEach(function (box) {
    var k = box.getAttribute("data-key");
    box.checked = !!state[k];
    box.addEventListener("change", function () {
      if (box.checked) state[k] = 1; else delete state[k];
      save(); progress(k.replace(/-\d+$/, ""));
    });
  });
  document.querySelectorAll(".challenge").forEach(function (c) { progress(c.id); });
  var reset = document.querySelector("[data-journey-reset]");
  if (reset) reset.addEventListener("click", function () {
    for (var n = 1; n <= 7; n++) delete state["seven-day-journey-" + n];
    save();
    document.querySelectorAll('#seven-day-journey input[type="checkbox"]').forEach(function (box) { box.checked = false; });
    progress("seven-day-journey");
  });
})();
