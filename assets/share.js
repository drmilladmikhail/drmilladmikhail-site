/* Share buttons for drmilladmikhail.com (articles, tests, pages).
   The WhatsApp / Facebook / Telegram / X links work without JavaScript.
   This adds: "copy link" and, on phones, the system share sheet (navigator.share).
   Copy works even where the Clipboard API is missing or blocked (e.g. in-app
   browsers inside Facebook or WhatsApp): it falls back to a hidden text field,
   and if that fails too it tells the visitor to copy the address manually. */
(function () {
  function legacyCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-1000px";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () {
        if (!legacyCopy(text)) throw new Error("copy failed");
      });
    }
    return legacyCopy(text) ? Promise.resolve() : Promise.reject(new Error("copy failed"));
  }

  document.querySelectorAll(".share[data-url]").forEach(function (box) {
    var url = box.getAttribute("data-url"), title = box.getAttribute("data-title") || document.title;
    var copy = box.querySelector(".sh-copy"), nat = box.querySelector(".sh-native");
    if (copy) {
      var label = copy.textContent;
      copy.hidden = false;
      copy.addEventListener("click", function () {
        copyText(url).then(function () {
          copy.textContent = "اتنسخ ✓";
        }, function () {
          copy.textContent = "انسخ الرابط من شريط العنوان";
        }).then(function () {
          setTimeout(function () { copy.textContent = label; }, 2200);
        });
      });
    }
    if (nat && navigator.share) {
      nat.hidden = false;
      nat.addEventListener("click", function () { navigator.share({ title: title, url: url }).catch(function () {}); });
    }
  });
})();
