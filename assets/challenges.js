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

  // Build a shareable achievement card locally. No image or progress is uploaded.
  var shareButton = document.querySelector("[data-journey-share]");
  var shareHint = document.querySelector("[data-journey-share-hint]");
  if (shareButton) shareButton.addEventListener("click", function () {
    var done = 0;
    for (var n = 1; n <= 7; n++) if (state["seven-day-journey-" + n]) done++;
    if (!done) return;
    shareButton.disabled = true;
    shareButton.textContent = "بنجهّز بطاقتك...";
    var canvas = document.createElement("canvas");
    canvas.width = 1200; canvas.height = 630;
    var ctx = canvas.getContext("2d");
    if (!ctx) { shareButton.disabled = false; shareButton.textContent = "حاول تاني"; return; }
    var gradient = ctx.createLinearGradient(0, 0, 1200, 630);
    gradient.addColorStop(0, "#173f3b"); gradient.addColorStop(1, "#315f58");
    ctx.fillStyle = gradient; ctx.fillRect(0, 0, 1200, 630);
    ctx.strokeStyle = "rgba(239,218,174,.35)"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(1030, 120, 210, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.arc(110, 560, 150, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = "#e8c987"; ctx.font = "600 30px 'IBM Plex Sans Arabic', sans-serif"; ctx.textAlign = "center";
    ctx.fillText("رحلتي مع نفسي", 600, 145);
    ctx.fillStyle = "#fffaf0"; ctx.font = "700 58px 'Noto Naskh Arabic', serif";
    ctx.fillText("7 أيام أقرب لنفسي", 600, 245);
    ctx.fillStyle = "#f3dfb8"; ctx.font = "600 42px 'IBM Plex Sans Arabic', sans-serif";
    ctx.fillText(done + " من 7 خطوات", 600, 345);
    ctx.fillStyle = "#fffaf0"; ctx.font = "400 27px 'IBM Plex Sans Arabic', sans-serif";
    ctx.fillText(done === 7 ? "أنهيت الرحلة.. وكل خطوة تستحق التقدير" : "كل خطوة صغيرة بتفرق.. وأنا مكمل", 600, 425);
    ctx.fillStyle = "rgba(255,250,240,.82)"; ctx.font = "500 24px 'IBM Plex Sans Arabic', sans-serif";
    ctx.fillText("د. ميلاد ميخائيل  ·  drmilladmikhail.com", 600, 545);
    canvas.toBlob(async function (blob) {
      shareButton.disabled = false; shareButton.textContent = "صمّم بطاقة إنجازك وشاركها";
      if (!blob) { if (shareHint) shareHint.textContent = "المتصفح مش قادر ينشئ الصورة. جرّب متصفحًا أحدث."; return; }
      var file = new File([blob], "my-seven-day-journey.png", { type: "image/png" });
      var canShareFile = navigator.canShare && navigator.canShare({ files: [file] });
      if (canShareFile && navigator.share) {
        try { await navigator.share({ files: [file], title: "رحلتي مع نفسي", text: "خطوة صغيرة كل يوم. drmilladmikhail.com/challenges/" }); if (shareHint) shareHint.textContent = "اختار واتساب أو فيسبوك من قائمة المشاركة."; }
        catch (error) { if (error && error.name !== "AbortError" && shareHint) shareHint.textContent = "ممكن تحفظ الصورة وتضيفها للمنشور بنفسك."; }
      } else {
        var url = URL.createObjectURL(blob);
        var link = document.createElement("a"); link.href = url; link.download = "my-seven-day-journey.png"; link.click();
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        if (shareHint) shareHint.textContent = "الصورة اتحفظت على جهازك. افتح واتساب أو فيسبوك وأرفقها في المنشور.";
      }
    }, "image/png");
  });
})();
