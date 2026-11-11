/* Explicitly requested public-content bookmarks. Never reads journals or answers. */
(function () {
  'use strict';
  var KEY = 'dm-saved-items:v1';
  var catalog = window.DMBookmarkCatalog || {};
  var state = { items: [], error: '' }, filter = 'all';
  var list = document.getElementById('bookmark-list');
  var clear = document.getElementById('bookmark-clear');
  var dialog = document.getElementById('bookmark-confirm');
  var heading = document.getElementById('bookmark-heading');
  var statuses = document.querySelectorAll('.bookmark-status');
  var buttons = document.querySelectorAll('[data-save-id]');
  var labels = { story: 'حكاية', exercise: 'تمرين' };
  function known(id) {
    if (!Object.prototype.hasOwnProperty.call(catalog, id)) return false;
    var c = catalog[id];
    return typeof c.title === 'string' &&
      ((c.kind === 'story' && /^\/stories\/#story-\d+$/.test(c.url)) ||
       (c.kind === 'exercise' && /^\/exercise\/#[a-z0-9-]+$/.test(c.url)));
  }
  function say(text) { statuses.forEach(function (s) { s.textContent = text; }); }
  function read() {
    var raw;
    try { raw = localStorage.getItem(KEY); }
    catch (_) { return { items: [], error: 'blocked' }; }
    if (raw === null) return { items: [], error: '' };
    try {
      var data = JSON.parse(raw);
      if (!data || data.version !== 1 || !Array.isArray(data.items) ||
          data.items.length > 500 || data.items.some(function (id) {
            return typeof id !== 'string' || id.length > 150 ||
              !/^(story|exercise):[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id);
          })) throw new Error('Invalid bookmark data');
      return { items: Array.from(new Set(data.items)), error: '' };
    } catch (_) { return { items: [], error: 'corrupt' }; }
  }
  function problem() {
    if (state.error === 'blocked') return 'المتصفح مش سامح بقراءة المحفوظات. الحفظ غير متاح هنا؛ محتوى الموقع لسه متاح عادي.';
    if (state.error === 'corrupt') return 'تعذر قراءة بيانات المحفوظات. افتح «محفوظاتي» وامسح المحفوظات فقط لو عايز تبدأ من جديد؛ ملاحظاتك مش هتتمسح.';
    return '';
  }
  function paint() {
    buttons.forEach(function (b) {
      var saved = state.items.indexOf(b.dataset.saveId) !== -1;
      b.hidden = false;
      b.disabled = !!state.error || !known(b.dataset.saveId);
      b.setAttribute('aria-pressed', String(saved));
      b.textContent = saved ? 'إلغاء الحفظ' : 'احفظ على جهازي';
      b.setAttribute('aria-label', b.textContent + ': ' + b.dataset.saveTitle);
    });
    if (!list) return;
    document.querySelector('.bookmark-toolbar').hidden = false;
    clear.disabled = state.error === 'blocked' || (!state.items.length && state.error !== 'corrupt');
    document.querySelectorAll('[data-saved-filter]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.savedFilter === filter));
    });
    var available = state.items.filter(known);
    var shown = available.filter(function (id) { return filter === 'all' || catalog[id].kind === filter; });
    document.getElementById('bookmark-count').textContent = state.error ? '' :
      'العناوين المحفوظة: ' + available.length.toLocaleString('ar-EG') +
      (filter === 'all' ? '' : ' · الظاهر: ' + shown.length.toLocaleString('ar-EG'));
    list.replaceChildren();
    shown.forEach(function (id) {
      var item = catalog[id], li = document.createElement('li');
      var type = document.createElement('p'), h = document.createElement('h3');
      var link = document.createElement('a'), remove = document.createElement('button');
      type.className = 'bookmark-type'; type.textContent = labels[item.kind];
      link.href = item.url; link.textContent = item.title; h.appendChild(link);
      remove.type = 'button'; remove.dataset.removeSaved = id;
      remove.textContent = 'إزالة من المحفوظات';
      remove.setAttribute('aria-label', 'إزالة من المحفوظات: ' + item.title);
      li.append(type, h, remove); list.appendChild(li);
    });
    var empty = document.getElementById('bookmark-empty');
    empty.hidden = !!state.error || shown.length > 0;
    empty.querySelector('h3').textContent = available.length ?
      'مفيش عناوين محفوظة من النوع ده' : 'لسه مفيش عناوين محفوظة هنا';
    if (!state.error && available.length < state.items.length) {
      say('بعض العناوين القديمة مش متاحة حاليًا، لكن معرّفاتها لسه محفوظة على جهازك.');
    }
  }
  function change(id, removeOnly) {
    state = read();
    if (state.error) { paint(); say(problem()); return false; }
    var old = state.items.indexOf(id) !== -1;
    var next = state.items.filter(function (v) { return v !== id; });
    if (!old && !removeOnly) next.unshift(id);
    try {
      localStorage.setItem(KEY, JSON.stringify({ version: 1, items: next }));
    } catch (_) {
      say('الحفظ ما تمش لأن المتصفح مش سامح بالكتابة. المحفوظات الحالية ما اتغيّرتش.');
      return false;
    }
    state.items = next; paint();
    say((old || removeOnly ? 'اتشال من المحفوظات: ' : 'اتحفظ على المتصفح ده: ') + catalog[id].title);
    return true;
  }
  buttons.forEach(function (b) {
    b.addEventListener('click', function () { if (known(b.dataset.saveId)) change(b.dataset.saveId, false); });
  });
  if (list) {
    document.querySelectorAll('[data-saved-filter]').forEach(function (b) {
      b.addEventListener('click', function () { filter = b.dataset.savedFilter; paint(); });
    });
    list.addEventListener('click', function (event) {
      var button = event.target.closest('[data-remove-saved]');
      if (!button || !known(button.dataset.removeSaved)) return;
      var index = Array.from(list.querySelectorAll('button')).indexOf(button);
      if (change(button.dataset.removeSaved, true)) {
        var remaining = list.querySelectorAll('button');
        (remaining.length ? remaining[Math.min(index, remaining.length - 1)] : heading).focus();
      }
    });
    clear.addEventListener('click', function () { dialog.showModal(); });
    document.getElementById('bookmark-cancel').addEventListener('click', function () { dialog.close(); });
    document.getElementById('bookmark-confirm-clear').addEventListener('click', function () {
      try { localStorage.removeItem(KEY); }
      catch (_) { say('مسح المحفوظات ما تمش لأن المتصفح مانع الوصول ليها.'); dialog.close(); return; }
      state = read(); dialog.close(); paint(); heading.focus();
      say('اتمسحت المحفوظات فقط. ملاحظات التمارين وتقدم التحديات زي ما هم.');
    });
  }
  window.addEventListener('storage', function (event) {
    if (event.key !== KEY && event.key !== null) return;
    state = read(); say(problem()); paint();
  });
  // A restored back/forward-cache page must reflect saves made on another page.
  window.addEventListener('pageshow', function () {
    state = read(); say(problem()); paint();
  });
  function openStory() {
    if (location.pathname !== '/stories/' || !/^#story-\d+$/.test(location.hash)) return;
    var card = document.getElementById(location.hash.slice(1));
    var details = card && card.querySelector('.story-details');
    if (details) details.open = true;
  }
  state = read(); say(problem()); paint(); openStory();
  window.addEventListener('hashchange', openStory);
}());
