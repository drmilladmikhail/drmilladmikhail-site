/* Article library search (progressive): the cards and category links work without JavaScript;
   this only adds a live filter box on /articles/ and the category pages. */
(function () {
  var box = document.querySelector('.lib-search');
  var list = document.getElementById('lib-cards');
  if (!box || !list) return;
  var input = box.querySelector('input');
  var out = box.querySelector('.lib-count');
  var cards = Array.prototype.slice.call(list.querySelectorAll('li.card'));
  if (!cards.length) return;
  box.hidden = false;
  /* Arabic-friendly matching: ignore tashkeel and unify alef/yaa/taa marbuta forms */
  function norm(s) {
    return (s || '').toLowerCase()
      .replace(/[ً-ْـ]/g, '')
      .replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه');
  }
  var texts = cards.map(function (li) { return norm(li.textContent); });
  function run() {
    var words = norm(input.value).split(/\s+/).filter(Boolean);
    var shown = 0;
    cards.forEach(function (li, i) {
      var ok = words.every(function (w) { return texts[i].indexOf(w) !== -1; });
      li.hidden = !ok;
      if (ok) shown++;
    });
    out.textContent = words.length ? (shown ? shown + ' مقال مطابق' : 'مفيش مقال مطابق. جرّب كلمة تانية.') : '';
  }
  input.addEventListener('input', run);
})();
