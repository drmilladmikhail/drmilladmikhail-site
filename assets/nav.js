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
