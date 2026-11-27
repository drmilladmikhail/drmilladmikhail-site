// «دقايق هدوء»: nothing typed here is sent or stored. Text lives in the page only until it is closed.
(function () {
  var audios = Array.prototype.slice.call(document.querySelectorAll('.calm-track audio'));
  audios.forEach(function (a) {
    a.addEventListener('play', function () {
      audios.forEach(function (o) { if (o !== a) o.pause(); });
    });
  });

  // Category & search filter for «دقيقة لنفسك» (50 emotion tracks)
  var filterBtns = Array.prototype.slice.call(document.querySelectorAll('.calm-filter'));
  var searchInput = document.getElementById('calm-search');
  var statusEl = document.getElementById('calm-filter-status');
  var moodTracks = Array.prototype.slice.call(document.querySelectorAll('#calm-minute-list .calm-track'));
  var activeCat = 'anxiety_stress_fear';

  function norm(s) {
    return (s || '').toLowerCase()
      .replace(/[أإآ]/g, 'ا')
      .replace(/ة/g, 'ه')
      .replace(/ى/g, 'ي')
      .replace(/[\u064B-\u0652]/g, '')
      .trim();
  }

  function applyFilter() {
    if (!moodTracks.length) return;
    var q = searchInput ? norm(searchInput.value) : '';
    var shown = 0;
    moodTracks.forEach(function (li) {
      var cat = li.getAttribute('data-cat') || '';
      var hay = norm(li.getAttribute('data-search') || li.textContent);
      var matchCat = q ? true : (activeCat === 'all' || cat === activeCat);
      var matchQ = !q || hay.indexOf(q) !== -1;
      var visible = matchCat && matchQ;
      li.hidden = !visible;
      if (visible) shown++;
    });
    if (statusEl) {
      if (q) {
        statusEl.textContent = shown ? ('عدد المقطوعات المطابقة: ' + shown) : 'ما لقيناش شعور بالاسم ده — جرّب كلمة تانية أو اختار تصنيف من فوق.';
      } else {
        statusEl.textContent = 'يعرض ' + shown + ' مقطوعة هادية (مدة كل مقطوعة دقيقتين).';
      }
    }
  }

  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      activeCat = btn.getAttribute('data-cat') || 'all';
      if (searchInput && searchInput.value) searchInput.value = '';
      filterBtns.forEach(function (b) {
        var on = b === btn;
        b.classList.toggle('is-active', on);
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      applyFilter();
    });
  });

  if (searchInput) searchInput.addEventListener('input', applyFilter);
  applyFilter();

  var box = document.getElementById('calm-text');
  var count = document.getElementById('calm-count');
  function update() { if (count) count.textContent = box.value.length ? box.value.length + ' حرف' : ''; }
  if (box) box.addEventListener('input', update);
  document.querySelectorAll('.calm-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      if (!box) return;
      var add = chip.getAttribute('data-insert') || '';
      box.value = box.value ? box.value.replace(/\s*$/, ' ') + add : add;
      box.focus();
      box.setSelectionRange(box.value.length, box.value.length);
      update();
    });
  });
  var clear = document.getElementById('calm-clear');
  if (clear) clear.addEventListener('click', function () {
    if (box && box.value && window.confirm('تمسح الكلام اللي كتبته؟')) { box.value = ''; update(); box.focus(); }
  });
})();
