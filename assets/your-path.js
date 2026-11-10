/* Curated paths: state stays in memory. No storage, network, analytics events or personal inputs. */
(function () {
  'use strict';
  var root = document.querySelector('.your-path');
  if (!root) return;
  var routes = Array.from(root.querySelectorAll('.yp-route'));
  var topics = Array.from(root.querySelectorAll('[data-topic]'));
  var starts = Array.from(root.querySelectorAll('[data-start]'));
  var preferences = root.querySelector('#yp-preferences');
  var restart = root.querySelector('#yp-restart');
  var progress = root.querySelector('#yp-progress');
  var sessionNote = root.querySelector('#yp-session-note');
  var finish = root.querySelector('#yp-finish');
  var status = root.querySelector('#yp-status');
  var active = null;
  var preferred = 'story';
  var complete = new Set();
  var digits = ['٠', '١', '٢', '٣'];
  function defaultButton(button) {
    var title = button.closest('.yp-step').querySelector('h3').textContent;
    button.textContent = 'خلصت الخطوة';
    var name = document.createElement('span');
    name.className = 'sr-only';
    name.textContent = ': ' + title;
    button.appendChild(name);
  }
  function paint() {
    starts.forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.start === preferred));
    });
    if (!active) return;
    var list = active.querySelector('.yp-steps');
    var order = [preferred].concat(['story', 'concept', 'exercise'].filter(function (kind) {
      return kind !== preferred;
    }));
    order.forEach(function (kind, index) {
      var step = active.querySelector('[data-kind="' + kind + '"]');
      if (list.children[index] !== step) list.insertBefore(step, list.children[index] || null);
    });
    active.querySelectorAll('[data-complete]').forEach(function (button) {
      var step = button.closest('.yp-step');
      var done = complete.has(step.dataset.kind);
      step.classList.toggle('yp-done', done);
      button.setAttribute('aria-pressed', String(done));
      if (done) {
        button.textContent = 'تراجع عن إكمال الخطوة';
        var name = document.createElement('span');
        name.className = 'sr-only';
        name.textContent = ': ' + step.querySelector('h3').textContent;
        button.appendChild(name);
      } else defaultButton(button);
    });
    progress.textContent = 'خلصت ' + digits[complete.size] + ' من ٣ خطوات';
    finish.hidden = complete.size !== 3;
  }
  function choose(id, moveFocus) {
    var chosen = routes.find(function (route) { return route.id === id; });
    if (!chosen) return false;
    active = chosen;
    preferred = 'story';
    complete.clear();
    routes.forEach(function (route) { route.hidden = route !== chosen; });
    topics.forEach(function (topic) {
      if (topic.dataset.topic === id) topic.setAttribute('aria-current', 'true');
      else topic.removeAttribute('aria-current');
    });
    preferences.hidden = restart.hidden = progress.hidden = sessionNote.hidden = false;
    paint();
    status.textContent = 'جهّزنا اقتراحات عن «' + chosen.querySelector('h2').textContent + '». اختار تحب تبدأ بإيه.';
    if (moveFocus) root.querySelector('#yp-preference-title').focus();
    return true;
  }
  topics.forEach(function (topic) {
    topic.addEventListener('click', function (event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      choose(topic.dataset.topic, true);
    });
  });
  starts.forEach(function (button) {
    button.addEventListener('click', function () {
      preferred = button.dataset.start;
      paint();
      status.textContent = 'المحطة الأولى بقت: ' + button.textContent + '. تقدر تفتح أي محطة.';
    });
  });
  root.querySelectorAll('[data-complete]').forEach(function (button) {
    button.hidden = false;
    button.addEventListener('click', function () {
      if (!active || !active.contains(button)) return;
      var kind = button.closest('.yp-step').dataset.kind;
      if (complete.has(kind)) complete.delete(kind);
      else complete.add(kind);
      paint();
      status.textContent = progress.textContent + '. تقدر تغيّر العلامات أو تكتفي لحد هنا.';
    });
  });
  function reset() {
    active = null;
    preferred = 'story';
    complete.clear();
    routes.forEach(function (route) { route.hidden = true; });
    topics.forEach(function (topic) { topic.removeAttribute('aria-current'); });
    preferences.hidden = restart.hidden = progress.hidden = sessionNote.hidden = finish.hidden = true;
    status.textContent = 'ابدأ من الموضوع الأقرب ليك، من غير استعجال.';
    paint();
  }
  restart.addEventListener('click', function () {
    reset();
    root.querySelector('#yp-topic-title').focus();
  });
  reset();
  var initial = location.hash.slice(1);
  if (initial && routes.some(function (route) { return route.id === initial; })) {
    try { history.replaceState(null, '', location.pathname + location.search); } catch (ignore) {}
    choose(initial, true);
  }
})();
