(function () {
  'use strict';
  var controls = document.querySelector('.g-controls');
  if (controls) {
    var input = document.querySelector('#glossary-search');
    var entries = Array.from(document.querySelectorAll('.g-entry'));
    var filters = Array.from(document.querySelectorAll('[data-category-filter]'));
    var category = '';
    var normalize = function (value) {
      return value.toLowerCase().normalize('NFKC')
        .replace(/[\u064b-\u065f\u0670\u0640]/g, '')
        .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
        .replace(/\s+/g, ' ').trim();
    };
    var apply = function () {
      var words = normalize(input.value).split(' ').filter(Boolean);
      var count = 0;
      entries.forEach(function (entry) {
        var haystack = normalize(entry.dataset.search);
        var matches = (!category || entry.dataset.category === category) &&
          words.every(function (word) { return haystack.indexOf(word) !== -1; });
        entry.hidden = !matches;
        if (matches) count += 1;
      });
      document.querySelector('.g-count').textContent = count + ' من ' + entries.length + ' مصطلح';
      document.querySelector('.g-empty').hidden = count !== 0;
      filters.forEach(function (button) {
        button.setAttribute('aria-pressed', String(button.dataset.categoryFilter === category));
      });
    };
    controls.hidden = false;
    input.addEventListener('input', apply);
    filters.forEach(function (button) {
      button.addEventListener('click', function () {
        category = button.dataset.categoryFilter;
        apply();
      });
    });
    document.querySelectorAll('.g-reset').forEach(function (button) {
      button.addEventListener('click', function () {
        input.value = '';
        category = '';
        apply();
        input.focus();
      });
    });
    apply();
  }
  var dialog = document.querySelector('#glossary-preview');
  if (dialog && typeof dialog.showModal === 'function') {
    document.querySelectorAll('.g-card[data-term]').forEach(function (link) {
      link.setAttribute('aria-haspopup', 'dialog');
      link.addEventListener('click', function (event) {
        // Preserve new-tab, modifier-key and no-JS navigation.
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        var template = document.getElementById('g-preview-' + link.dataset.term);
        if (!template) return;
        event.preventDefault();
        dialog.replaceChildren(template.content.cloneNode(true));
        dialog.showModal();
        dialog.scrollTop = 0;
      });
    });
    dialog.addEventListener('click', function (event) {
      if (event.target.closest('.g-close')) {
        dialog.close();
      } else if (event.target === dialog) {
        var bounds = dialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right ||
            event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
      }
    });
  }
  var copy = document.querySelector('.g-copy');
  if (copy && navigator.clipboard && window.isSecureContext) {
    copy.hidden = false;
    copy.addEventListener('click', function () {
      var status = document.querySelector('.g-copy-status');
      navigator.clipboard.writeText(copy.dataset.url).then(function () {
        status.textContent = 'اتنسخ رابط المصطلح.';
      }).catch(function () {
        status.textContent = 'تعذّر النسخ. تقدر تنسخ رابط الصفحة من شريط العنوان.';
      });
    });
  }
}());
