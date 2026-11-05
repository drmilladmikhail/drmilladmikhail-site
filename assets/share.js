/* Share buttons for drmilladmikhail.com (articles, tests, pages).
   The WhatsApp / Facebook / Telegram / X links work without JavaScript.
   This adds: "copy link" and, on phones, the system share sheet (navigator.share). */
(function () {
  document.querySelectorAll(".share[data-url]").forEach(function (box) {
    var url = box.getAttribute("data-url"), title = box.getAttribute("data-title") || document.title;
    var copy = box.querySelector(".sh-copy"), nat = box.querySelector(".sh-native");
    if (copy && navigator.clipboard) {
      copy.hidden = false;
      copy.addEventListener("click", function () {
        navigator.clipboard.writeText(url).then(function () {
          var t = copy.textContent; copy.textContent = "اتنسخ ✓";
          setTimeout(function () { copy.textContent = t; }, 1800);
        });
      });
    }
    if (nat && navigator.share) {
      nat.hidden = false;
      nat.addEventListener("click", function () { navigator.share({ title: title, url: url }).catch(function () {}); });
    }
  });
})();
