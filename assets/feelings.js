/* «عجلة المشاعر» (/feelings/). Without JavaScript all the cards show as a list.
   With it: pick a colour (family) -> pick a word -> see one card. Nothing is stored or sent.
   A link like /feelings/#f-lonely opens that card directly (used by the WhatsApp button). */
(function () {
  var root = document.getElementById("fw");
  if (!root) return;
  var pick = root.querySelector(".fw-pick"), sub = root.querySelector(".fw-sub"), chips = root.querySelector(".fw-chips");
  var after = root.querySelector(".fw-after"), wa = root.querySelector(".fw-wa");
  var fams = root.querySelectorAll(".fw-fam"), cards = root.querySelectorAll(".fw-card");
  root.classList.add("js");
  pick.hidden = false;

  function hideCards() {
    cards.forEach(function (c) { c.classList.remove("on"); });
    after.hidden = true;
  }

  function chooseFam(id, focusChips) {
    fams.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-fam") === id ? "true" : "false"); });
    root.setAttribute("data-fam", id);
    chips.innerHTML = "";
    root.querySelectorAll('.fw-card[data-fam="' + id + '"]').forEach(function (c) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "fw-chip";
      b.textContent = c.getAttribute("data-name");
      b.setAttribute("aria-pressed", "false");
      b.setAttribute("data-card", c.id);
      b.addEventListener("click", function () { showCard(c.id, true); });
      chips.appendChild(b);
    });
    sub.hidden = false;
    hideCards();
    if (focusChips) {
      sub.scrollIntoView({ behavior: "smooth", block: "nearest" });
      var first = chips.querySelector("button");
      if (first) first.focus({ preventScroll: true });
    }
  }

  function showCard(id, move) {
    var c = document.getElementById(id);
    if (!c) return;
    if (root.getAttribute("data-fam") !== c.getAttribute("data-fam")) chooseFam(c.getAttribute("data-fam"), false);
    hideCards();
    c.classList.add("on");
    chips.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-card") === id ? "true" : "false"); });
    var url = location.origin + "/feelings/#" + id;
    wa.href = "https://wa.me/?text=" + encodeURIComponent("النهارده أنا حاسس إني " + c.getAttribute("data-name") + ". لقيت الشرح ده وحسيته بيوصف إحساسي: " + url);
    after.hidden = false;
    if (move) {
      c.focus({ preventScroll: true });
      c.scrollIntoView({ behavior: "smooth", block: "start" });
      try { history.replaceState(null, "", "#" + id); } catch (e) {}
    }
  }

  fams.forEach(function (b) {
    b.addEventListener("click", function () { chooseFam(b.getAttribute("data-fam"), true); });
  });
  root.querySelector(".fw-again").addEventListener("click", function () {
    hideCards();
    sub.hidden = true;
    root.removeAttribute("data-fam");
    fams.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
    try { history.replaceState(null, "", location.pathname); } catch (e) {}
    pick.scrollIntoView({ behavior: "smooth", block: "start" });
    fams[0].focus({ preventScroll: true });
  });

  var h = location.hash.slice(1);
  if (h && /^f-[a-z-]+$/.test(h) && document.getElementById(h)) showCard(h, true);
})();
