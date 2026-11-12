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
// Open a folded home-page section (<details class="fold">) when its link (#about, #credentials, #research) is used.
(function () {
  function openHash() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (!el) return;
    var changed = false;
    for (var p = el.parentElement; p; p = p.parentElement) {
      if (p.tagName === 'DETAILS' && !p.open) { p.open = true; changed = true; }
    }
    var d = el.querySelector('details.fold');
    if (d && !d.open) { d.open = true; changed = true; }
    if (changed) el.scrollIntoView();
  }
  window.addEventListener('hashchange', openHash);
  openHash();
})();

/* Site-wide «جديد» ticker: the newest content on the site, written into each
   page by tools/build_news.py as <script type="application/json" id="site-news">.
   Nothing new → the previous items keep showing. Dismissing hides it for this
   visit until something newer goes up. */
(function () {
  var built = document.querySelector('.site-announcement[data-k]');
  if (built) {
    var k = built.getAttribute('data-k');
    try { if (sessionStorage.getItem('siteAnnouncementDismissed') === k) { built.remove(); return; } } catch (e) {}
    var btn = built.querySelector('.site-announcement-close');
    if (btn) btn.addEventListener('click', function () {
      built.remove();
      try { sessionStorage.setItem('siteAnnouncementDismissed', k); } catch (e) {}
    });
    return;
  }
  var header = document.querySelector('.topbar');
  if (!header || document.querySelector('.site-announcement')) return;
  var src = document.getElementById('site-news');
  var news = [];
  try { news = JSON.parse(src ? src.textContent : '[]') || []; } catch (e) { news = []; }
  if (!news.length) return;
  var key = news[0].k;
  try {
    if (sessionStorage.getItem('siteAnnouncementDismissed') === key) return;
  } catch (e) {}

  var isEnglish = document.documentElement.lang === 'en';
  var bar = document.createElement('aside');
  bar.className = 'site-announcement';
  bar.setAttribute('aria-label', 'الجديد على الموقع');

  var label = document.createElement('span');
  label.className = 'site-announcement-label';
  label.textContent = 'جديد';

  var viewport = document.createElement('div');
  viewport.className = 'site-announcement-viewport';

  var track = document.createElement('div');
  track.className = 'site-announcement-track';
  var chars = 0;
  for (var i = 0; i < 2; i++) {
    news.forEach(function (n) {
      var link = document.createElement('a');
      link.className = 'site-announcement-link';
      link.href = n.u;
      link.textContent = n.t;
      if (i === 1) { link.setAttribute('aria-hidden', 'true'); link.tabIndex = -1; } else { chars += n.t.length; }
      track.appendChild(link);
    });
  }
  track.style.animationDuration = Math.max(24, Math.round(chars * 0.22)) + 's';
  viewport.appendChild(track);

  var close = document.createElement('button');
  close.className = 'site-announcement-close';
  close.type = 'button';
  close.setAttribute('aria-label', isEnglish ? 'Dismiss announcement' : 'إخفاء الإعلان');
  close.textContent = '×';
  close.addEventListener('click', function () {
    bar.remove();
    try { sessionStorage.setItem('siteAnnouncementDismissed', key); } catch (e) {}
  });

  bar.appendChild(label);
  bar.appendChild(viewport);
  bar.appendChild(close);
  header.insertAdjacentElement('afterend', bar);

  if (!document.getElementById('nav-layout-fix')) {
    var style = document.createElement('style');
    style.textContent = [
      '.site-announcement{position:relative;z-index:20;display:flex;align-items:center;gap:12px;min-height:46px;padding:7px max(16px,calc((100% - 1080px)/2));background:#173f38;color:#fff;border-bottom:1px solid rgba(255,255,255,.14);overflow:hidden;font:600 14px/1.5 inherit}',
      '.site-announcement-label{flex:none;padding:3px 10px;border-radius:999px;background:#e2b35a;color:#20352f;font-size:12px;font-weight:700}',
      '.site-announcement-viewport{flex:1;min-width:0;overflow:hidden}',
      '.site-announcement-track{display:flex;width:max-content;direction:rtl;animation:site-announcement-scroll 24s linear infinite}',
      '.site-announcement-link{display:block;flex:none;padding-inline:32px;color:#fff;text-decoration:none;white-space:nowrap}',
      '.site-announcement-link+.site-announcement-link{border-inline-start:1px solid rgba(226,179,90,.55)}',
      '.site-announcement-link:hover{text-decoration:underline}',
      '.site-announcement-close{position:relative;z-index:2;flex:none;width:30px;height:30px;border:0;border-radius:50%;background:rgba(255,255,255,.12);color:#fff;font:400 22px/1 Arial,sans-serif;cursor:pointer}',
      '.site-announcement-close:hover{background:rgba(255,255,255,.22)}',
      '@keyframes site-announcement-scroll{from{transform:translateX(0)}to{transform:translateX(50%)}}',
      'html[lang="en"] .site-announcement-track{direction:ltr;animation-name:site-announcement-scroll-en}',
      '@keyframes site-announcement-scroll-en{from{transform:translateX(-50%)}to{transform:translateX(0)}}',
      '@media(hover:hover){.site-announcement-viewport:hover .site-announcement-track{animation-play-state:paused}}',
      '@media(max-width:480px){.site-announcement{gap:8px;min-height:44px;padding-inline:10px;font-size:12px}.site-announcement-link{padding-inline:22px}}',
      '@media(prefers-reduced-motion:reduce){.site-announcement-track{animation:none!important;width:100%}.site-announcement-link[aria-hidden="true"]{display:none}.site-announcement-link{white-space:normal;padding:2px 8px}}'
    ].join('');
    document.head.appendChild(style);
  }
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
  style.textContent = ".floating-home{position:fixed;z-index:999;inset-inline-start:18px;bottom:calc(18px + env(safe-area-inset-bottom,0px));display:inline-flex;align-items:center;gap:9px;min-height:48px;padding:10px 16px;border:1px solid rgba(255,255,255,.2);border-radius:999px;background:#28594f;color:#fff;text-decoration:none;font-family:inherit;font-size:14px;font-weight:600;line-height:1.2;box-shadow:0 8px 24px rgba(22,48,41,.25);transition:transform .18s ease,background .18s ease}.floating-home svg{width:19px;height:19px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.floating-home:hover{background:#1e493f;transform:translateY(-2px)}.floating-home:focus-visible{outline:3px solid #d9ad58;outline-offset:3px}@media(max-width:480px){.floating-home{inset-inline-start:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));min-height:46px;padding:10px 13px;font-size:13px}}@media(prefers-reduced-motion:reduce){.floating-home{transition:none}.floating-home:hover{transform:none}}";
  document.head.appendChild(style);
  var wrap = document.createElement("nav");
  wrap.setAttribute("aria-label", document.documentElement.lang === "en" ? "Back to home" : "العودة للرئيسية");
  wrap.appendChild(link);
  document.body.appendChild(wrap);
})();

/* Bound the Arabic navigation without removing links or clipping the page. */
(function () {
  if (document.documentElement.lang !== 'ar' || document.getElementById('nav-layout-fix')) return;
  var style = document.createElement('style');
  style.id = 'nav-layout-fix';
  style.textContent = [
    'html[lang] body .topbar .wrap{flex-wrap:wrap;min-width:0;row-gap:8px;padding-block:10px}',
    'html[lang] body .topbar .brand{max-width:100%;min-width:0}',
    'html[lang] body .topbar .brand-text{min-width:0;white-space:normal;overflow-wrap:anywhere}',
    'html[lang] body .topbar .nav{flex:1 1 680px;min-width:0;max-width:100%;flex-wrap:wrap;justify-content:flex-end;gap:8px 14px}',
    'html[lang] body .topbar .nav>*,html[lang] body .topbar .dd{min-width:0;max-width:100%}',
    'html[lang] body .topbar .dd:not([open])>.dd-panel{display:none}',
    'html[lang] body .topbar .dd[open]>.dd-panel{position:fixed;left:20px;right:20px;inset-inline:20px;top:auto;width:auto;min-width:0;max-width:none;max-height:70vh;overflow-y:auto;white-space:normal;transform:none;margin-inline:0}',
    'html[lang] body .topbar .dd-panel a{white-space:normal;overflow-wrap:anywhere}',
    'html[lang] body .topbar .menu nav{position:fixed;left:16px;right:16px;inset-inline:16px;top:auto;width:auto;min-width:0;max-width:none;max-height:75vh;overflow-y:auto}',
    '@media(max-width:1100px){html[lang] body .topbar .nav{display:none}html[lang] body .topbar .menu{display:block}}'
  ].join('');
  document.head.appendChild(style);
})();

/* Floating buttons step aside while the visitor reads down, and come back on scroll up (2026-11-11). */
(function () {
  var root = document.documentElement, last = window.pageYOffset, ticking = false;
  function update() {
    var y = window.pageYOffset, d = y - last;
    if (Math.abs(d) > 6) {
      if (d > 0 && y > 240) root.classList.add('fab-away'); else root.classList.remove('fab-away');
      last = y;
    }
    if (window.innerHeight + y >= document.documentElement.scrollHeight - 80) root.classList.remove('fab-away');
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  document.addEventListener('focusin', function (e) { if (e.target.closest && e.target.closest('.floating-home, .helper')) root.classList.remove('fab-away'); });
})();
