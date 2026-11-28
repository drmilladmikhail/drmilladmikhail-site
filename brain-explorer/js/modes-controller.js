// DMMA Brain Explorer — Six Interactive Psychological Modes Controller
export function initModes({ modes, regionsById, onHighlightStep }) {
  const tabsEl = document.getElementById('be-mode-tabs');
  const enTitle = document.getElementById('mode-en-title');
  const arTitle = document.getElementById('mode-ar-title');
  const summaryEl = document.getElementById('mode-summary');
  const stepsEl = document.getElementById('mode-steps');
  const diagEl = document.getElementById('mode-diagram');
  const conceptsEl = document.getElementById('mode-concepts-list');
  const exampleEl = document.getElementById('mode-example');
  const quizQ = document.getElementById('mode-quiz-q');
  const quizOpts = document.getElementById('mode-quiz-opts');
  const quizFeedback = document.getElementById('mode-quiz-feedback');
  const playBtn = document.getElementById('btn-mode-play');

  let activeMode = modes[0];
  let activeStepIdx = 0;
  let playTimer = null;

  function stopPlayback() {
    if (playTimer) {
      clearInterval(playTimer);
      playTimer = null;
    }
    if (playBtn) playBtn.textContent = '▶ تشغيل التسلسل التعليمي';
  }

  function highlightStep(idx, notify3D = true) {
    activeStepIdx = idx;
    Array.from(stepsEl.children).forEach((li, i) => {
      li.classList.toggle('is-active', i === idx);
    });
    const diagNodes = diagEl.querySelectorAll('.be-diag-node');
    diagNodes.forEach((el, i) => {
      el.classList.toggle('is-active', i === Math.min(idx, diagNodes.length - 1));
    });
    if (notify3D && onHighlightStep) {
      const step = activeMode.steps[idx];
      const allIds = activeMode.steps.map((s) => s.regionId);
      onHighlightStep(activeMode, allIds, step ? step.regionId : null);
    }
  }

  function renderMode(mode, notify3D = false) {
    stopPlayback();
    activeMode = mode;
    enTitle.textContent = mode.enTitle;
    arTitle.textContent = mode.arTitle;
    summaryEl.textContent = mode.summary;
    exampleEl.textContent = mode.example;

    // Steps
    stepsEl.textContent = '';
    mode.steps.forEach((step, idx) => {
      const li = document.createElement('li');
      li.className = 'be-step-item';
      li.setAttribute('tabindex', '0');

      const reg = regionsById.get(step.regionId);
      const head = document.createElement('div');
      head.className = 'be-step-title';
      const tSpan = document.createElement('span');
      tSpan.textContent = step.title;
      const rSpan = document.createElement('span');
      rSpan.className = 'be-step-region';
      rSpan.textContent = reg ? reg.arName : '';
      head.append(tSpan, rSpan);

      const p = document.createElement('p');
      p.className = 'be-step-desc';
      p.textContent = step.desc;

      li.append(head, p);
      li.addEventListener('click', () => {
        stopPlayback();
        highlightStep(idx, true);
      });
      li.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          stopPlayback();
          highlightStep(idx, true);
        }
      });
      stepsEl.appendChild(li);
    });

    // Simplified diagram
    diagEl.textContent = '';
    mode.diagram.forEach((nodeLabel, idx) => {
      const box = document.createElement('span');
      box.className = 'be-diag-node';
      box.textContent = nodeLabel;
      diagEl.appendChild(box);
      if (idx < mode.diagram.length - 1) {
        const arr = document.createElement('span');
        arr.className = 'be-diag-arrow';
        arr.setAttribute('aria-hidden', 'true');
        arr.textContent = '←';
        diagEl.appendChild(arr);
      }
    });

    // Concepts
    conceptsEl.textContent = '';
    mode.concepts.forEach((c) => {
      const tag = document.createElement('span');
      tag.className = 'be-concept-tag';
      tag.textContent = c;
      conceptsEl.appendChild(tag);
    });

    // Mini quiz
    quizQ.textContent = mode.quiz.question;
    quizFeedback.textContent = '';
    quizOpts.textContent = '';
    mode.quiz.options.forEach((optText, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'be-quiz-opt';
      btn.textContent = optText;
      btn.addEventListener('click', () => {
        Array.from(quizOpts.children).forEach((b, i) => {
          b.classList.remove('is-correct', 'is-wrong');
          if (i === mode.quiz.correct) b.classList.add('is-correct');
          else if (i === idx) b.classList.add('is-wrong');
        });
        const ok = idx === mode.quiz.correct;
        quizFeedback.textContent = (ok ? 'إجابة صحيحة! ' : 'محاولة جيدة — ') + mode.quiz.explanation;
      });
      quizOpts.appendChild(btn);
    });

    highlightStep(0, notify3D);
  }

  // Render tabs
  tabsEl.textContent = '';
  modes.forEach((m, idx) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'be-mode-tab' + (idx === 0 ? ' is-active' : '');
    btn.setAttribute('role', 'tab');
    btn.setAttribute('aria-selected', idx === 0 ? 'true' : 'false');
    btn.textContent = m.arTitle;
    btn.addEventListener('click', () => {
      Array.from(tabsEl.children).forEach((b) => {
        b.classList.remove('is-active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('is-active');
      btn.setAttribute('aria-selected', 'true');
      renderMode(m, true);
    });
    tabsEl.appendChild(btn);
  });

  if (playBtn) {
    playBtn.addEventListener('click', () => {
      if (playTimer) {
        stopPlayback();
        return;
      }
      playBtn.textContent = '⏸ إيقاف مؤقت';
      highlightStep(0, true);
      let next = 1;
      playTimer = setInterval(() => {
        if (next >= activeMode.steps.length) {
          stopPlayback();
          return;
        }
        highlightStep(next, true);
        next++;
      }, 2100);
    });
  }

  const syncLink = document.getElementById('btn-mode-3d-sync');
  if (syncLink) {
    syncLink.addEventListener('click', () => {
      highlightStep(activeStepIdx, true);
    });
  }

  renderMode(modes[0], false);
}
