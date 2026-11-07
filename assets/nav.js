// Header drop-downs (<details class="dd">): only one open at a time, close on outside click / Esc.
(function () {
  var dds = document.querySelectorAll('.topbar details');
  if (!dds.length) return;
  dds.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      dds.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });
  document.addEventListener('click', function (e) {
    dds.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    dds.forEach(function (d) {
      if (d.open) { d.open = false; var s = d.querySelector('summary'); if (s) s.focus(); }
    });
  });
})();
// Open a folded home-page section (<details class="fold">) when its link (#credentials, #research) is used.
(function () {
  function openHash() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    var d = el && el.querySelector('details.fold');
    if (d && !d.open) { d.open = true; el.scrollIntoView(); }
  }
  window.addEventListener('hashchange', openHash);
  openHash();
})();

/* Persistent, accessible route back to the homepage on every page using the shared navigation script. */
(function () {
  if (document.querySelector(".floating-home")) return;
  var isHome = location.pathname === "/" || location.pathname === "/index.html";
  if (isHome) return;
  var link = document.createElement("a");
  link.className = "floating-home";
  link.href = "/";
  link.setAttribute("aria-label", document.documentElement.lang === "en" ? "Home page" : "الصفحة الرئيسية");
  link.title = link.getAttribute("aria-label");
  link.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg><span>' + (document.documentElement.lang === "en" ? "Home" : "الصفحة الرئيسية") + '</span>';
  var style = document.createElement("style");
  style.textContent = ".floating-home{position:fixed;z-index:999;inset-inline-start:18px;bottom:calc(18px + env(safe-area-inset-bottom,0px));display:inline-flex;align-items:center;gap:9px;min-height:48px;padding:10px 16px;border:1px solid rgba(255,255,255,.2);border-radius:999px;background:#28594f;color:#fff;text-decoration:none;font:600 14px/1.2 inherit;box-shadow:0 8px 24px rgba(22,48,41,.25);transition:transform .18s ease,background .18s ease}.floating-home svg{width:19px;height:19px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.floating-home:hover{background:#1e493f;transform:translateY(-2px)}.floating-home:focus-visible{outline:3px solid #d9ad58;outline-offset:3px}@media(max-width:480px){.floating-home{inset-inline-start:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));min-height:46px;padding:10px 13px;font-size:13px}}@media(prefers-reduced-motion:reduce){.floating-home{transition:none}.floating-home:hover{transform:none}}";
  document.head.appendChild(style);
  document.body.appendChild(link);
})();
