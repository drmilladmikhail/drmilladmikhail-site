/* Click-to-play YouTube for drmilladmikhail.com.
   Each video starts as a link with a small WebP thumbnail (fast page).
   On click it becomes the real player from youtube-nocookie.com (privacy-enhanced:
   no YouTube cookies until the visitor plays). Without JavaScript the link
   simply opens the video on YouTube. Built by tools/build_videos.py. */
(function () {
  // WebP thumbnail missing (rare, old uploads) -> use the JPG one. Kept here instead of an
  // inline onerror="" so the page's Content-Security-Policy can forbid inline scripts.
  function fix(img) {
    if (img.src.indexOf("/vi_webp/") > -1) img.src = img.src.replace("/vi_webp/", "/vi/").replace(".webp", ".jpg");
  }
  document.addEventListener("error", function (e) { if (e.target && e.target.tagName === "IMG") fix(e.target); }, true);
  Array.prototype.forEach.call(document.querySelectorAll(".yt img"), function (img) {
    if (img.complete && img.naturalWidth === 0) fix(img);
  });

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a.yt[data-id]");
    if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.button > 0) return;
    e.preventDefault();
    var id = a.getAttribute("data-id");
    if (!/^[\w-]{11}$/.test(id)) return;
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&playsinline=1&hl=ar";
    f.title = (a.getAttribute("aria-label") || "YouTube").replace(/^[^:]*:\s*/, "");
    f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    f.allowFullscreen = true;
    f.referrerPolicy = "strict-origin-when-cross-origin";
    var box = document.createElement("div");
    box.className = a.className;
    box.appendChild(f);
    a.replaceWith(box);
    f.focus();
  });
})();
