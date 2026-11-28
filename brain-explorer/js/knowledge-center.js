// DMMA Brain Explorer — Quizzes, Flashcards, Searchable Glossary & References
function normalizeAr(str) {
  return String(str || '')
    .toLowerCase()
    .replace(/[\u064B-\u065F\u0670\u06D6-\u06ED\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/ؤ/g, 'و')
    .replace(/[ئى]/g, 'ي')
    .replace(/ة/g, 'ه')
    .trim();
}

export function initKnowledgeCenter({ quizzesData, glossaryData, referencesData }) {
  // ---------------- 1. Multi-level Quiz ----------------
  const levelBtns = Array.from(document.querySelectorAll('[data-level]'));
  const progressFill = document.getElementById('quiz-progress-fill');
  const progressLabel = document.getElementById('quiz-progress-label');
  const quizBody = document.getElementById('quiz-body');
  const quizResult = document.getElementById('quiz-result');
  const scoreHeading = document.getElementById('quiz-score-heading');
  const scoreNote = document.getElementById('quiz-score-note');
  const reviewEl = document.getElementById('quiz-review');
  const retryBtn = document.getElementById('btn-quiz-retry');

  let currentLevel = 'beginner';
  let qIdx = 0;
  let answers = [];

  function startQuiz(level) {
    currentLevel = level;
    qIdx = 0;
    answers = [];
    levelBtns.forEach((b) => {
      const on = b.getAttribute('data-level') === level;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    quizResult.hidden = true;
    quizBody.hidden = false;
    renderQuestion();
  }

  function renderQuestion() {
    const list = quizzesData.levels[currentLevel] || [];
    const item = list[qIdx];
    if (!item) return showQuizResult();

    progressLabel.textContent = `سؤال ${qIdx + 1} من ${list.length}`;
    progressFill.style.width = `${Math.round(((qIdx + 1) / list.length) * 100)}%`;

    quizBody.textContent = '';
    const qP = document.createElement('p');
    qP.className = 'be-quiz-q';
    qP.textContent = item.q;
    const opts = document.createElement('div');
    opts.className = 'be-quiz-opts';

    item.options.forEach((txt, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'be-quiz-opt';
      btn.textContent = txt;
      btn.addEventListener('click', () => {
        answers.push({ item, chosen: idx, ok: idx === item.correct });
        qIdx++;
        renderQuestion();
      });
      opts.appendChild(btn);
    });

    quizBody.append(qP, opts);
  }

  function showQuizResult() {
    const total = answers.length;
    const score = answers.filter((a) => a.ok).length;
    quizBody.hidden = true;
    quizResult.hidden = false;
    progressFill.style.width = '100%';
    progressLabel.textContent = 'اكتمل الاختبار';

    scoreHeading.textContent = `نتيجتك المعرفية: ${score} من ${total}`;
    scoreNote.textContent =
      'هذه النتيجة مقياس تعليمي لمعلوماتك حول علم الأعصاب فقط، وليست تقييماً نفسياً أو تشخيصاً إكلينيكياً.';

    reviewEl.textContent = '';
    answers.forEach((a, i) => {
      const div = document.createElement('div');
      div.className = 'be-review-item';
      const strong = document.createElement('strong');
      strong.textContent = `${i + 1}. ${a.ok ? '✓' : '✕'} ${a.item.q}`;
      const p = document.createElement('p');
      p.textContent = a.item.explanation;
      const link = document.createElement('a');
      link.href = a.item.lesson;
      link.textContent = 'راجع الدرس المرتبط ←';
      div.append(strong, p, link);
      reviewEl.appendChild(div);
    });
  }

  levelBtns.forEach((b) => {
    b.addEventListener('click', () => startQuiz(b.getAttribute('data-level')));
  });
  if (retryBtn) retryBtn.addEventListener('click', () => startQuiz(currentLevel));
  startQuiz('beginner');

  // ---------------- 2. Flashcards ----------------
  const cards = quizzesData.flashcards || [];
  let cardIdx = 0;
  let flipped = false;
  const flashBtn = document.getElementById('flashcard-btn');
  const flashCounter = document.getElementById('flash-counter');
  const flashLabel = document.getElementById('flash-label');
  const flashFront = document.getElementById('flash-front');
  const flashEn = document.getElementById('flash-en');
  const flashBack = document.getElementById('flash-back');
  const prevBtn = document.getElementById('btn-flash-prev');
  const flipBtn = document.getElementById('btn-flash-flip');
  const nextBtn = document.getElementById('btn-flash-next');

  function renderFlashcard() {
    if (!cards.length) return;
    const c = cards[cardIdx];
    flashCounter.textContent = `${cardIdx + 1} / ${cards.length}`;
    flashFront.textContent = c.ar;
    flashEn.textContent = c.en;
    flashBack.textContent = c.back;
    flashBack.hidden = !flipped;
    flashLabel.textContent = flipped ? 'الشرح العلمي' : 'المصطلح';
    flashBtn.setAttribute('aria-pressed', flipped ? 'true' : 'false');
  }

  function toggleFlip() {
    flipped = !flipped;
    renderFlashcard();
  }

  if (flashBtn) flashBtn.addEventListener('click', toggleFlip);
  if (flipBtn) flipBtn.addEventListener('click', toggleFlip);
  if (prevBtn) prevBtn.addEventListener('click', () => { cardIdx = (cardIdx - 1 + cards.length) % cards.length; flipped = false; renderFlashcard(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { cardIdx = (cardIdx + 1) % cards.length; flipped = false; renderFlashcard(); });
  renderFlashcard();

  // ---------------- 3. Searchable Glossary ----------------
  const glossInput = document.getElementById('glossary-input');
  const glossList = document.getElementById('be-glossary-list');

  function renderGlossary(query = '') {
    const q = normalizeAr(query);
    glossList.textContent = '';
    const hits = glossaryData.filter((g) => {
      if (!q) return true;
      return normalizeAr(`${g.ar} ${g.en} ${g.def}`).includes(q);
    });
    if (!hits.length) {
      const empty = document.createElement('p');
      empty.textContent = 'لا توجد مصطلحات مطابقة لهذا البحث حالياً.';
      glossList.appendChild(empty);
      return;
    }
    hits.forEach((g) => {
      const card = document.createElement('article');
      card.className = 'be-gloss-item';
      const h3 = document.createElement('h3');
      h3.textContent = g.ar;
      const en = document.createElement('span');
      en.className = 'be-en-name';
      en.lang = 'en';
      en.dir = 'ltr';
      en.textContent = g.en;
      const p = document.createElement('p');
      p.textContent = g.def;
      card.append(h3, en, p);
      glossList.appendChild(card);
    });
  }

  if (glossInput) {
    glossInput.addEventListener('input', () => renderGlossary(glossInput.value));
  }
  renderGlossary('');

  // ---------------- 4. Verified References ----------------
  const refsList = document.getElementById('be-refs-list');
  if (refsList) {
    refsList.textContent = '';
    referencesData.forEach((ref) => {
      const li = document.createElement('li');
      const strong = document.createElement('strong');
      strong.textContent = ref.org + ': ';
      const a = document.createElement('a');
      a.href = ref.url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = ref.title;
      const note = document.createTextNode(` — ${ref.note}`);
      li.append(strong, a, note);
      refsList.appendChild(li);
    });
  }
}
