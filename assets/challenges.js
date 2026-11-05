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
})();
