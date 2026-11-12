/* Bilingual research library: search, filter, sort, paginate, AR/EN toggle. */
(function () {
  'use strict';
  var DATA = window.RESEARCH_LIBRARY_DATA || [];
  var PER_PAGE = 10;
  var state = { lang: 'ar', q: '', journal: 'all', sort: 'journal', page: 1, todayOnly: false };

  function todayStr() {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function isNewToday(r) { return r.added && r.added === todayStr(); }

  var LABELS = {
    ar: {
      search: 'ابحث بالعربية أو الإنجليزية',
      journal: 'كل الدوريات',
      sortJournal: 'حسب الدورية',
      sortTitle: 'حسب العنوان',
      results: 'نتيجة',
      noResults: 'لا توجد نتائج مطابقة. جرّب كلمة أعم أو أزل الفلاتر.',
      page: 'صفحة',
      prev: 'السابق',
      next: 'التالي',
      authors: 'المؤلفون',
      vol: 'المجلد',
      issue: 'العدد',
      abstracts: 'الملخصات (عربي + English)',
      abstractAr: 'الملخص العربي',
      abstractEn: 'Original abstract (English)',
      translationNotice: 'النص العربي ترجمة من إعداد الموقع؛ النص الإنجليزي هو الملخص الأصلي.',
      source: 'المصدر',
      pmid: 'PMID',
      toggle: 'English',
      count: function (n, t) { return 'عرض ' + n + ' من ' + t + ' بحثًا'; },
      reset: 'مسح البحث والفلاتر',
      todayNotice: function (n) {
        if (n === 1) return 'بحث جديد واحد أُضيف اليوم';
        if (n === 2) return 'بحثان جديدان أُضيفا اليوم';
        if (n <= 10) return n + ' أبحاث جديدة أُضيفت اليوم';
        return n + ' بحثًا جديدًا أُضيف اليوم';
      },
      showToday: 'عرض الجديد',
      showAll: 'عرض المكتبة كلها',
      newBadge: 'جديد اليوم',
      totalCount: function (n) { return 'المكتبة تضم الآن ' + n + ' بحثًا محكّمًا'; }
    },
    en: {
      search: 'Search in Arabic or English',
      journal: 'All journals',
      sortJournal: 'By journal',
      sortTitle: 'By title',
      results: 'results',
      noResults: 'No matching results. Try a broader term or clear the filters.',
      page: 'Page',
      prev: 'Previous',
      next: 'Next',
      authors: 'Authors',
      vol: 'Vol.',
      issue: 'Issue',
      abstracts: 'Abstracts (English + العربية)',
      abstractAr: 'الملخص العربي',
      abstractEn: 'Original abstract (English)',
      translationNotice: 'Arabic translation by this website; the English text is the original abstract.',
      source: 'Source',
      pmid: 'PMID',
      toggle: 'العربية',
      count: function (n, t) { return 'Showing ' + n + ' of ' + t + ' papers'; },
      reset: 'Clear search and filters',
      todayNotice: function (n) { return n + ' new ' + (n === 1 ? 'study' : 'studies') + ' added today'; },
      showToday: 'Show new',
      showAll: 'Show all papers',
      newBadge: 'New today',
      totalCount: function (n) { return 'The library now holds ' + n + ' peer-reviewed papers'; }
    }
  };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function norm(s) {
    return String(s || '').toLowerCase().replace(/[\u064B-\u0652]/g, '').replace(/\u0640/g, '');
  }

  function matches(r) {
    if (state.todayOnly && !isNewToday(r)) return false;
    if (state.journal !== 'all' && r.journal !== state.journal) return false;
    if (!state.q) return true;
    var q = norm(state.q);
    var hay = norm(r.title + ' ' + r.title_ar + ' ' + r.abstract + ' ' + r.abstract_ar + ' ' + r.journal + ' ' + r.journal_ar + ' ' + r.authors.join(' ') + ' ' + r.doi + ' ' + r.pmid);
    return hay.indexOf(q) !== -1;
  }

  function sorted(list) {
    var out = list.slice();
    if (state.sort === 'title') {
      out.sort(function (a, b) {
        var x = state.lang === 'ar' ? a.title_ar : a.title;
        var y = state.lang === 'ar' ? b.title_ar : b.title;
        return x.localeCompare(y, state.lang === 'ar' ? 'ar' : 'en');
      });
    } else {
      var order = {};
      DATA.forEach(function (r) { if (!(r.journal in order)) order[r.journal] = Object.keys(order).length; });
      out.sort(function (a, b) {
        return order[a.journal] - order[b.journal] || (state.lang === 'ar' ? a.title_ar : a.title).localeCompare(state.lang === 'ar' ? b.title_ar : b.title);
      });
    }
    return out;
  }

  function authorsLine(r) {
    var a = r.authors;
    if (r.license) return a.join(', ');
    var shown = a.slice(0, 3).join(', ');
    if (a.length > 3) shown += ' et al.';
    return shown;
  }

  function card(r) {
    var L = LABELS[state.lang];
    var ar = state.lang === 'ar';
    var mainTitle = ar ? r.title_ar : r.title;
    var secondTitle = ar ? r.title : r.title_ar;
    var journalName = ar ? r.journal_ar : r.journal;
    var issueTxt = ar ? r.issue_ar : r.issue_en;
    var absArFirst = ar;
    var absAr = '<div class="abs-block" dir="rtl" lang="ar"><h3>' + esc(LABELS.ar.abstractAr) + '</h3><p>' + esc(r.abstract_ar) + '</p></div>';
    var absEn = '<div class="abs-block" dir="ltr" lang="en"><h3>' + esc(LABELS.en.abstractEn) + '</h3><p>' + esc(r.abstract) + '</p></div>';
    return '<article class="lib-card" id="p' + esc(r.pmid || r.doi) + '">' +
      '<p class="tag">' + esc(journalName) + ' · ' + esc(L.vol) + ' ' + esc(r.volume) + ' · ' + esc(L.issue) + ' ' + esc(r.issue) + ' · ' + esc(issueTxt) +
      (isNewToday(r) ? '<span class="new-badge">' + esc(L.newBadge) + '</span>' : '') + '</p>' +
      '<h2>' + esc(mainTitle) + '</h2>' +
      '<p class="alt-title" dir="' + (ar ? 'ltr' : 'rtl') + '" lang="' + (ar ? 'en' : 'ar') + '">' + esc(secondTitle) + '</p>' +
      '<p class="authors"><b>' + esc(L.authors) + ':</b> <span dir="ltr" lang="en">' + esc(authorsLine(r)) + '</span></p>' +
      '<details class="abs"><summary>' + esc(L.abstracts) + '</summary>' + (absArFirst ? absAr + absEn : absEn + absAr) + '</details>' +
      '<p class="src"><b>' + esc(L.source) + ':</b> ' +
      (r.pmid ? '<a href="https://pubmed.ncbi.nlm.nih.gov/' + esc(r.pmid) + '/">' + esc(L.pmid) + ' ' + esc(r.pmid) + '</a> · ' : '') +
      '<a href="https://doi.org/' + esc(r.doi) + '" dir="ltr">DOI: ' + esc(r.doi) + '</a>' +
      (r.copyright ? ' · <span dir="ltr" lang="en">' + esc(r.copyright) + '</span>' : '') +
      (r.license && r.license_url ? ' · <a rel="license" href="' + esc(r.license_url) + '" dir="ltr">' + esc(r.license) + '</a>' : '') + '</p>' +
      (r.license ? '<p class="src translation-notice">' + esc(L.translationNotice) + '</p>' : '') +
      '</article>';
  }

  function render() {
    var L = LABELS[state.lang];
    var el = function (id) { return document.getElementById(id); };
    var list = sorted(DATA.filter(matches));
    var pages = Math.max(1, Math.ceil(list.length / PER_PAGE));
    if (state.page > pages) state.page = pages;
    var start = (state.page - 1) * PER_PAGE;
    var slice = list.slice(start, start + PER_PAGE);

    document.documentElement.lang = state.lang;
    document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';
    var swaps = document.querySelectorAll('[data-ar][data-en]');
    for (var si = 0; si < swaps.length; si++) {
      swaps[si].textContent = state.lang === 'ar' ? swaps[si].getAttribute('data-ar') : swaps[si].getAttribute('data-en');
    }
    el('lib-search').placeholder = L.search;
    el('lib-search-btn').textContent = L.reset;
    el('lib-journal').options[0].textContent = L.journal;
    var jOpts = el('lib-journal').options;
    for (var oi = 1; oi < jOpts.length; oi++) {
      jOpts[oi].textContent = state.lang === 'ar' ? jOpts[oi].getAttribute('data-ar') : jOpts[oi].getAttribute('data-en');
    }
    el('lib-sort').options[0].textContent = L.sortJournal;
    el('lib-sort').options[1].textContent = L.sortTitle;
    el('lib-lang').textContent = L.toggle;
    el('lib-count').textContent = L.count(slice.length, list.length);

    var intro = el('lib-intro-count');
    if (intro) intro.textContent = L.totalCount(DATA.length);

    var todayBox = el('lib-today');
    if (todayBox) {
      var fresh = DATA.filter(isNewToday);
      if (fresh.length) {
        todayBox.hidden = false;
        todayBox.innerHTML = '<span class="today-text"><span class="today-dot" aria-hidden="true"></span>' +
          esc(L.todayNotice(fresh.length)) + '</span>' +
          '<button type="button" id="lib-today-btn">' + esc(state.todayOnly ? L.showAll : L.showToday) + '</button>';
        var tb = document.getElementById('lib-today-btn');
        if (tb) tb.addEventListener('click', function () {
          state.todayOnly = !state.todayOnly;
          state.page = 1;
          render();
          var top = document.getElementById('lib-results');
          if (top) window.scrollTo({ top: top.offsetTop - 90, behavior: 'smooth' });
        });
      } else {
        todayBox.hidden = true;
        todayBox.innerHTML = '';
        state.todayOnly = false;
      }
    }
    el('lib-results').innerHTML = slice.length
      ? slice.map(card).join('')
      : '<p class="notice">' + esc(L.noResults) + '</p>';

    var nav = '<div class="lib-pager" role="navigation" aria-label="' + esc(L.page) + '">';
    nav += state.page > 1 ? '<button type="button" data-go="' + (state.page - 1) + '">' + esc(L.prev) + '</button> ' : '';
    for (var i = 1; i <= pages; i++) {
      nav += i === state.page
        ? '<span aria-current="page"><b>' + i + '</b></span> '
        : '<button type="button" data-go="' + i + '">' + i + '</button> ';
    }
    nav += state.page < pages ? '<button type="button" data-go="' + (state.page + 1) + '">' + esc(L.next) + '</button>' : '';
    nav += '</div>';
    el('lib-pager').innerHTML = nav;
  }

  function go(p) {
    state.page = p;
    render();
    var top = document.getElementById('lib-results');
    if (top) window.scrollTo({ top: top.offsetTop - 90, behavior: 'smooth' });
  }

  // Public study fragments identify a paper, never the visitor's search query.
  function openLinkedStudy(preserveFilters) {
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    var paper = DATA.find(function (r) { return 'p' + (r.pmid || r.doi) === id; });
    if (!paper) return;
    if (preserveFilters !== true) {
      state.q = ''; state.journal = 'all'; state.todayOnly = false;
      document.getElementById('lib-search').value = '';
      document.getElementById('lib-journal').value = 'all';
    }
    var ordered = sorted(DATA.filter(matches)), index = ordered.indexOf(paper);
    if (index < 0) return false;
    state.page = Math.floor(index / PER_PAGE) + 1;
    render();
    var target = document.getElementById(id);
    if (target) {
      target.querySelector('details.abs').open = true;
      target.style.scrollMarginTop = '110px';
      target.tabIndex = -1;
      target.focus({ preventScroll: true });
      target.scrollIntoView({ block: 'start' });
    }
    return true;
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!DATA.length) return;
    var el = function (id) { return document.getElementById(id); };

    var jSel = el('lib-journal');
    var seen = {};
    DATA.forEach(function (r) {
      if (!seen[r.journal]) {
        seen[r.journal] = 1;
        var o = document.createElement('option');
        o.value = r.journal;
        o.textContent = r.journal;
        o.setAttribute('data-ar', r.journal_ar);
        o.setAttribute('data-en', r.journal);
        jSel.appendChild(o);
      }
    });

    el('lib-search').addEventListener('input', function (e) { state.q = e.target.value.trim(); state.page = 1; render(); });
    el('lib-journal').addEventListener('change', function (e) { state.journal = e.target.value; state.page = 1; render(); });
    el('lib-sort').addEventListener('change', function (e) { state.sort = e.target.value; state.page = 1; render(); });
    el('lib-search-btn').addEventListener('click', function () {
      state.q = ''; state.journal = 'all'; state.sort = 'journal'; state.page = 1; state.todayOnly = false;
      el('lib-search').value = ''; el('lib-journal').value = 'all'; el('lib-sort').value = 'journal';
      render();
    });
    el('lib-lang').addEventListener('click', function () {
      var linked;
      try { linked = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (_) {}
      state.lang = state.lang === 'ar' ? 'en' : 'ar';
      if (!linked || !openLinkedStudy(true)) render();
    });
    el('lib-pager').addEventListener('click', function (e) {
      var b = e.target.closest('button[data-go]');
      if (b) go(parseInt(b.getAttribute('data-go'), 10));
    });
    render();
    openLinkedStudy();
    window.addEventListener('hashchange', openLinkedStudy);
  });
})();
