/* Public metadata only. Queries never enter URLs, storage, analytics or requests. */
(function () {
  'use strict';
  var root = document.querySelector('.explore-page');
  if (!root) return;
  var query = document.getElementById('explore-query');
  var form = document.getElementById('explore-form');
  var list = document.getElementById('explore-results');
  var counter = document.getElementById('explore-count');
  var empty = document.getElementById('explore-empty');
  var more = document.getElementById('explore-more');
  var clear = document.getElementById('explore-clear');
  var kinds = Array.from(root.querySelectorAll('[data-explore-kind]'));
  var kind = 'all', limit = 12, timer, matches = [];
  function normal(value) {
    return String(value || '').normalize('NFKC').toLowerCase()
      .replace(/[\u064B-\u065F\u0670\u06D6-\u06ED\u0640]/g, '')
      .replace(/[أإآٱ]/g, 'ا').replace(/ؤ/g, 'و').replace(/[ئى]/g, 'ي').replace(/ة/g, 'ه')
      .replace(/[^\p{L}\p{N}\s]/gu, ' ').replace(/\s+/g, ' ').trim();
  }
  var rows = Array.from(list.querySelectorAll('.explore-item')).map(function (el, index) {
    return { el: el, index: index, kind: el.dataset.kind,
      title: normal(el.dataset.title), text: normal(el.dataset.search) };
  });
  function paint() {
    var text = normal(query.value), words = text ? text.split(' ') : [];
    matches = rows.filter(function (r) {
      return (kind === 'all' || r.kind === kind) && words.every(function (w) { return r.text.includes(w); });
    }).map(function (r) {
      var score = !text ? 0 : r.title === text ? 1000 :
        (r.title.includes(text) ? 100 : 0) + words.reduce(function (n, w) {
          return n + (r.title.includes(w) ? 10 : 1);
        }, 0);
      return { row: r, score: score };
    }).sort(function (a, b) { return b.score - a.score || a.row.index - b.row.index; })
      .map(function (v) { return v.row; });
    rows.forEach(function (r) { r.el.hidden = true; });
    matches.forEach(function (r, i) { list.appendChild(r.el); r.el.hidden = i >= limit; });
    var shown = Math.min(limit, matches.length);
    counter.textContent = matches.length.toLocaleString('ar-EG') + ' نتيجة' +
      (shown < matches.length ? ' · ظاهر منها ' + shown.toLocaleString('ar-EG') : '');
    empty.hidden = matches.length > 0;
    more.hidden = shown >= matches.length;
    more.textContent = 'اعرض المزيد (' + Math.min(12, matches.length - shown).toLocaleString('ar-EG') + ')';
    clear.disabled = !query.value;
    kinds.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.exploreKind === kind)); });
  }
  function reset() {
    clearTimeout(timer); query.value = ''; kind = 'all'; limit = 12; paint();
  }
  query.addEventListener('input', function () {
    clearTimeout(timer); timer = setTimeout(function () { limit = 12; paint(); }, 150);
  });
  form.addEventListener('submit', function (event) {
    event.preventDefault(); clearTimeout(timer); limit = 12; paint();
  });
  clear.addEventListener('click', function () {
    clearTimeout(timer); query.value = ''; limit = 12; paint(); query.focus();
  });
  kinds.forEach(function (b) {
    b.addEventListener('click', function () {
      clearTimeout(timer); kind = b.dataset.exploreKind; limit = 12; paint();
    });
  });
  root.querySelectorAll('[data-explore-topic]').forEach(function (b) {
    b.addEventListener('click', function () {
      clearTimeout(timer); query.value = b.dataset.exploreTopic; kind = 'all'; limit = 12; paint();
    });
  });
  document.getElementById('explore-reset').addEventListener('click', function () { reset(); query.focus(); });
  more.addEventListener('click', function () {
    clearTimeout(timer);
    var firstNew = limit; limit += 12; paint();
    if (matches[firstNew]) matches[firstNew].el.querySelector('a').focus();
  });
  // Clear the in-memory query even when the browser restores a cached page.
  window.addEventListener('pagehide', reset);
  window.addEventListener('pageshow', function (event) { if (event.persisted) reset(); });
  reset();
  root.classList.add('explore-enhanced');
  root.querySelector('.explore-controls').hidden = false;
}());
