// «دقايق هدوء»: nothing typed here is sent or stored. Text lives in the page only until it is closed.
(function () {
  var audios = Array.prototype.slice.call(document.querySelectorAll('.calm-track audio'));
  audios.forEach(function (a) {
    a.addEventListener('play', function () {
      audios.forEach(function (o) { if (o !== a) o.pause(); });
    });
  });
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
