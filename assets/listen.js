// «استمع لهذا المقال»: reads the article aloud with the device's own Arabic voice (Web Speech API).
// Free, no server, nothing is sent anywhere. Hidden on devices that can't speak.
(function () {
  var box = document.querySelector('.listen');
  var body = document.querySelector('.post-body');
  if (!box || !body || !('speechSynthesis' in window) || !window.SpeechSynthesisUtterance) return;
  var synth = window.speechSynthesis;
  var btn = box.querySelector('.listen-btn'), label = box.querySelector('.listen-label');
  var stopBtn = box.querySelector('.listen-stop'), msg = box.querySelector('.listen-msg');
  var rateSel = box.querySelector('select');
  var chunks = [], i = 0, state = 'idle', voice = null, gen = 0;

  function pickVoice() {
    var vs = synth.getVoices() || [];
    var ar = vs.filter(function (v) { return /^ar(-|_|$)/i.test(v.lang); });
    var pref = ['ar-EG', 'ar-SA', 'ar-AE', 'ar-XA'];
    for (var p = 0; p < pref.length; p++) {
      var hit = ar.filter(function (v) { return v.lang.replace('_', '-').toLowerCase() === pref[p].toLowerCase(); })[0];
      if (hit) return hit;
    }
    return ar[0] || null;
  }
  function textChunks() {
    var title = (document.querySelector('.post h1') || {}).textContent || '';
    var parts = [title];
    body.querySelectorAll('h2, p, li, td').forEach(function (el) {
      if (el.closest('figure')) return;
      var t = el.textContent.replace(/\s+/g, ' ').trim();
      if (t) parts.push(t);
    });
    // short pieces: some browsers stop long utterances after ~15 seconds
    var out = [];
    parts.forEach(function (t) {
      t.replace(/([.!؟?،:])\s+/g, '$1\n').split('\n').forEach(function (s) {
        while (s.length > 220) { var cut = s.lastIndexOf(' ', 220); if (cut < 80) cut = 220; out.push(s.slice(0, cut)); s = s.slice(cut); }
        if (s.trim()) out.push(s.trim());
      });
    });
    return out;
  }
  function setState(s) {
    state = s;
    btn.setAttribute('aria-pressed', s === 'playing' ? 'true' : 'false');
    label.textContent = s === 'playing' ? 'إيقاف مؤقت' : (s === 'paused' ? 'كمّل الاستماع' : 'استمع لهذا المقال');
    stopBtn.hidden = s === 'idle';
    box.classList.toggle('is-playing', s === 'playing');
  }
  function speakNext() {
    if (state !== 'playing') return;
    if (i >= chunks.length) { setState('idle'); i = 0; msg.textContent = 'خلص المقال. شكراً إنك سمعت 🌿'; return; }
    var g = gen, u = new SpeechSynthesisUtterance(chunks[i]);
    u.lang = voice ? voice.lang : 'ar-EG';
    if (voice) u.voice = voice;
    u.rate = parseFloat(rateSel.value) || 1;
    u.onend = function () { if (g !== gen) return; i++; speakNext(); };
    u.onerror = function (e) { if (g === gen && e.error !== 'interrupted' && e.error !== 'canceled') { i++; speakNext(); } };
    synth.speak(u);
  }
  function init() {
    voice = pickVoice();
    box.hidden = false;
  }
  btn.addEventListener('click', function () {
    msg.textContent = '';
    if (state === 'playing') { synth.pause(); setState('paused'); return; }
    if (state === 'paused') { setState('playing'); synth.resume(); if (!synth.speaking) speakNext(); return; }
    if (!voice) voice = pickVoice();
    chunks = textChunks(); i = 0;
    gen++; synth.cancel(); setState('playing'); speakNext();
    if (!voice) msg.textContent = 'لو مسمعتش صوت عربي، نزّل صوت عربي من إعدادات الموبايل (إمكانية الوصول ← تحويل النص لكلام).';
  });
  stopBtn.addEventListener('click', function () { gen++; setState('idle'); synth.cancel(); i = 0; });
  rateSel.addEventListener('change', function () {
    if (state === 'playing') { gen++; synth.cancel(); speakNext(); }
  });
  window.addEventListener('pagehide', function () { synth.cancel(); });
  if ((synth.getVoices() || []).length) init();
  else { synth.addEventListener ? synth.addEventListener('voiceschanged', init, { once: true }) : (synth.onvoiceschanged = init); setTimeout(function () { if (box.hidden) init(); }, 1500); }
})();
