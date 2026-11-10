/* depth3d.js — light 3D layer for drmilladmikhail.com (pairs with depth3d.css).
   1. Homepage hero stage follows the mouse (desktop), the phone's tilt
      (Android) or the scroll position (iPhone and others).
   2. Link cards tilt in 3D under the mouse and press in under a finger.
   3. Cards below the fold unfold in 3D as they scroll into view.
   Pure decoration: nothing is stored or sent, and it all switches off for
   visitors who ask their device for reduced motion. */
(function () {
  'use strict';
  var root = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;
  root.classList.add('d3-js');
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------- 1. hero stage ---------- */
  var stage = document.querySelector('.h3d-stage');
  if (stage) {
    var hero = stage.closest('section') || document.body;
    var target = { x: 8, y: -10 }, frame = 0;
    var apply = function () {
      frame = 0;
      stage.style.setProperty('--h3d-rx', target.x.toFixed(2) + 'deg');
      stage.style.setProperty('--h3d-ry', target.y.toFixed(2) + 'deg');
    };
    var queue = function () { if (!frame) frame = requestAnimationFrame(apply); };
    if (fine) {
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        target.x = 8 - py * 14; target.y = -10 + px * 22; queue();
      });
      hero.addEventListener('pointerleave', function () { target.x = 8; target.y = -10; queue(); });
    } else {
      var gyro = false;
      window.addEventListener('deviceorientation', function (e) {
        if (e.beta == null || e.gamma == null) return;
        gyro = true;
        var g = Math.max(-25, Math.min(25, e.gamma)), b = Math.max(10, Math.min(70, e.beta));
        target.y = -10 + g * 0.6; target.x = 8 + (b - 40) * 0.25; queue();
      });
      window.addEventListener('scroll', function () {
        if (gyro) return;
        var p = Math.min(1, Math.max(0, window.scrollY / 700));
        target.x = 8 + p * 10; target.y = -10 + p * 18; queue();
      }, { passive: true });
    }
  }

  /* ---------- 2. tilting / pressing cards ---------- */
  var SEL = '.card > a, .concern-card, .weekly, .test-card, .vcard, .g-card, .platform-card, .story-card, ' +
            '.ws-card, .path-card, .xt-card, .fw-card, .c-card, .myth-card';
  var cards = Array.prototype.filter.call(document.querySelectorAll(SEL), function (el) {
    if (el.matches('.df-station, .meta, .df-urgent') || el.closest('.h3d-stage')) return false;
    if (el.matches('a, button')) return true;
    /* only small link cards: big panels, forms and step lists stay flat */
    if (el.querySelector('input, textarea, select, details, ol, form')) return false;
    if (el.getBoundingClientRect().height > 460) return false;
    return !!el.querySelector('a, button');
  });
  cards.forEach(function (el) {
    el.classList.add('d3-tilt');
    var raf = 0, next = '';
    var set = function (t) { next = t; if (!raf) raf = requestAnimationFrame(function () { raf = 0; el.style.transform = next; }); };
    var reset = function () { el.classList.remove('d3-active'); set(''); };
    el.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse' && e.pointerType !== 'pen') return;
      var r = el.getBoundingClientRect();
      if (r.width > 760) return;
      var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
      var max = r.width > 420 ? 4 : 7;
      el.classList.add('d3-active');
      set('perspective(900px) rotateX(' + (-py * max).toFixed(2) + 'deg) rotateY(' + (px * max).toFixed(2) + 'deg) translateZ(14px)');
    });
    el.addEventListener('pointerleave', reset);
    el.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') set('perspective(900px) translateZ(-10px) scale(.985)');
    });
    ['pointerup', 'pointercancel'].forEach(function (t) {
      el.addEventListener(t, function (e) { if (e.pointerType === 'touch') reset(); });
    });
  });

  /* ---------- 3. unfold on scroll ---------- */
  if (!('IntersectionObserver' in window)) return;
  var fold = window.innerHeight;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('d3-in'); io.unobserve(en.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  cards.forEach(function (el) {
    var unit = el.parentElement && el.parentElement.tagName === 'LI' ? el.parentElement : el;
    if (unit.getBoundingClientRect().top < fold) return;
    if (unit.parentElement) unit.parentElement.classList.add('d3-stage');
    unit.classList.add('d3-reveal');
    io.observe(unit);
  });
})();
