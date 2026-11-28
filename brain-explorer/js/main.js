// DMMA Brain Explorer — Main Application Orchestrator (Strict CSP ES Module)
import { createBrainViewer } from './brain-viewer.js';
import { createFallback2D } from './fallback-2d.js';
import { initModes } from './modes-controller.js';
import { initNeuronLab } from './neuron-lab.js';
import { initKnowledgeCenter } from './knowledge-center.js';

async function loadJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path} (${res.status})`);
  return res.json();
}

async function boot() {
  // Mobile menu toggle
  const menuBtn = document.getElementById('be-menu-toggle');
  const mainNav = document.getElementById('be-main-nav');
  if (menuBtn && mainNav) {
    menuBtn.addEventListener('click', () => {
      const open = mainNav.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    mainNav.querySelectorAll('a').forEach((a) => {
      a.addEventListener('click', () => {
        mainNav.classList.remove('is-open');
        menuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Load all scientific datasets in parallel
  const [regions, modes, behavior, glossary, quizzes, references] = await Promise.all([
    loadJson('/brain-explorer/data/regions.json'),
    loadJson('/brain-explorer/data/modes.json'),
    loadJson('/brain-explorer/data/behavior.json'),
    loadJson('/brain-explorer/data/glossary.json'),
    loadJson('/brain-explorer/data/quizzes.json'),
    loadJson('/brain-explorer/data/references.json'),
  ]);

  const regionsById = new Map(regions.map((r) => [r.id, r]));

  // DOM refs
  const loaderEl = document.getElementById('be-loader');
  const loaderProgress = document.getElementById('be-loader-progress');
  const hoverPill = document.getElementById('be-hover-pill');
  const modeBadge = document.getElementById('be-active-mode-badge');
  const canvasMount = document.getElementById('be-canvas-mount');
  const fallbackMount = document.getElementById('be-fallback-2d');
  const btnMode3D = document.getElementById('btn-mode-3d');
  const btnMode2D = document.getElementById('btn-mode-2d');
  const btnXray = document.getElementById('btn-xray');
  const btnExplode = document.getElementById('btn-explode');
  const btnAutoRotate = document.getElementById('btn-autorotate');

  const infoEmpty = document.getElementById('be-info-empty');
  const infoContent = document.getElementById('be-info-content');
  const quickPicks = document.getElementById('be-quick-picks');
  const btnDeselect = document.getElementById('btn-deselect');
  const regionsGrid = document.getElementById('be-regions-grid');

  let viewer3D = null;
  let viewer2D = null;
  let currentRegionId = null;

  function renderInfoPanel(id) {
    currentRegionId = id;
    if (!id || !regionsById.has(id)) {
      infoContent.hidden = true;
      infoEmpty.hidden = false;
      hoverPill.textContent = 'حرّك المؤشر أو انقر على أي منطقة دماغية';
      if (viewer2D) viewer2D.selectRegion(null);
      document.querySelectorAll('.be-region-card').forEach((c) => c.classList.remove('is-selected'));
      return;
    }

    const r = regionsById.get(id);
    document.getElementById('region-group-badge').textContent = r.groupLabel;
    document.getElementById('region-ar-name').textContent = r.arName;
    document.getElementById('region-en-name').textContent = r.enName;
    document.getElementById('region-location').textContent = r.location;
    document.getElementById('region-bio').textContent = r.bioFunctions;
    document.getElementById('region-cognition').textContent = r.cognitionBehavior;
    document.getElementById('region-emotion').textContent = r.emotionalRole;
    document.getElementById('region-example').textContent = r.realLifeExample;
    document.getElementById('region-notes').textContent = r.scientificNotes;

    const relWrap = document.getElementById('region-related');
    relWrap.textContent = '';
    (r.related || []).forEach((relId) => {
      const target = regionsById.get(relId);
      if (!target) return;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'be-quick-pick';
      btn.textContent = target.arName;
      btn.addEventListener('click', () => selectStructure(relId, true));
      relWrap.appendChild(btn);
    });

    infoEmpty.hidden = true;
    infoContent.hidden = false;
    hoverPill.textContent = `${r.arName} · ${r.enName}`;

    document.querySelectorAll('.be-region-card').forEach((c) => {
      c.classList.toggle('is-selected', c.getAttribute('data-region-id') === id);
    });
    if (viewer2D) viewer2D.selectRegion(id);
  }

  function selectStructure(id, focusCam = true) {
    if (viewer3D) {
      viewer3D.clearMode();
      if (modeBadge) modeBadge.hidden = true;
      const xrayNow = viewer3D.selectRegion(id, focusCam);
      if (btnXray) btnXray.setAttribute('aria-pressed', xrayNow ? 'true' : 'false');
    }
    renderInfoPanel(id);
  }

  function show2DFallback(reason) {
    if (loaderEl) loaderEl.hidden = true;
    canvasMount.hidden = true;
    fallbackMount.hidden = false;
    btnMode2D.classList.add('is-active');
    btnMode2D.setAttribute('aria-pressed', 'true');
    btnMode3D.classList.remove('is-active');
    btnMode3D.setAttribute('aria-pressed', 'false');
    if (reason) hoverPill.textContent = 'وضع العرض التفاعلي 2D المبسط (متوافق مع جميع الأجهزة)';
    if (!viewer2D) {
      viewer2D = createFallback2D({
        mount: fallbackMount,
        regionsById,
        onSelect: (id) => selectStructure(id, false),
      });
    }
    if (currentRegionId) viewer2D.selectRegion(currentRegionId);
  }

  function show3DView() {
    if (!viewer3D) return;
    fallbackMount.hidden = true;
    canvasMount.hidden = false;
    btnMode3D.classList.add('is-active');
    btnMode3D.setAttribute('aria-pressed', 'true');
    btnMode2D.classList.remove('is-active');
    btnMode2D.setAttribute('aria-pressed', 'false');
    viewer3D.resize();
  }

  // Initialize 3D Viewer
  viewer3D = createBrainViewer({
    mount: canvasMount,
    regionsById,
    onSelect: (id) => selectStructure(id, true),
    onHover: (id) => {
      if (id && regionsById.has(id)) {
        const r = regionsById.get(id);
        hoverPill.textContent = `${r.arName} · ${r.enName}`;
      } else if (currentRegionId && regionsById.has(currentRegionId)) {
        const r = regionsById.get(currentRegionId);
        hoverPill.textContent = `${r.arName} · ${r.enName}`;
      } else {
        hoverPill.textContent = 'حرّك المؤشر أو انقر على أي منطقة دماغية';
      }
    },
    onProgress: (pct) => {
      if (loaderProgress) loaderProgress.textContent = `تم تحميل ${pct}% من النموذج التشريحي`;
    },
    onReady: () => {
      if (loaderEl) loaderEl.hidden = true;
    },
    onError: () => {
      show2DFallback(true);
    },
  });

  if (!viewer3D) {
    show2DFallback(true);
  }

  // Camera & anatomy control bindings
  document.querySelectorAll('[data-cam]').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (viewer3D) viewer3D.setCameraPreset(btn.getAttribute('data-cam'));
    });
  });

  if (btnXray) {
    btnXray.addEventListener('click', () => {
      const next = btnXray.getAttribute('aria-pressed') !== 'true';
      btnXray.setAttribute('aria-pressed', next ? 'true' : 'false');
      if (viewer3D) viewer3D.setXRay(next);
    });
  }
  if (btnExplode) {
    btnExplode.addEventListener('click', () => {
      const next = btnExplode.getAttribute('aria-pressed') !== 'true';
      btnExplode.setAttribute('aria-pressed', next ? 'true' : 'false');
      if (viewer3D) viewer3D.setExploded(next);
    });
  }
  if (btnAutoRotate) {
    btnAutoRotate.addEventListener('click', () => {
      const next = btnAutoRotate.getAttribute('aria-pressed') !== 'true';
      btnAutoRotate.setAttribute('aria-pressed', next ? 'true' : 'false');
      if (viewer3D) viewer3D.setAutoRotate(next);
    });
  }
  if (btnMode2D) btnMode2D.addEventListener('click', () => show2DFallback(false));
  if (btnMode3D) btnMode3D.addEventListener('click', () => show3DView());

  if (btnDeselect) {
    btnDeselect.addEventListener('click', () => selectStructure(null, false));
  }
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && currentRegionId) selectStructure(null, false);
  });

  // Populate quick picks inside empty info panel
  ['prefrontal_cortex', 'amygdala', 'hippocampus', 'hypothalamus', 'insula', 'cerebellum'].forEach((id) => {
    const r = regionsById.get(id);
    if (!r) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'be-quick-pick';
    btn.textContent = r.arName;
    btn.addEventListener('click', () => selectStructure(id, true));
    quickPicks.appendChild(btn);
  });

  // Populate 15 anatomical structures directory grid + category filters
  function renderRegionsGrid(cat = 'all') {
    regionsGrid.textContent = '';
    regions
      .filter((r) => cat === 'all' || r.category === cat)
      .forEach((r) => {
        const card = document.createElement('button');
        card.type = 'button';
        card.className = 'be-region-card' + (r.id === currentRegionId ? ' is-selected' : '');
        card.setAttribute('data-region-id', r.id);

        const top = document.createElement('span');
        top.className = 'be-en-name';
        top.lang = 'en';
        top.dir = 'ltr';
        const dot = document.createElement('span');
        dot.className = 'be-region-dot';
        dot.style.backgroundColor = r.color;
        top.append(dot, document.createTextNode(r.enName));

        const h3 = document.createElement('h3');
        h3.textContent = r.arName;

        const p = document.createElement('p');
        p.textContent = r.bioFunctions;

        card.append(top, h3, p);
        card.addEventListener('click', () => {
          selectStructure(r.id, true);
          document.getElementById('explorer').scrollIntoView({ behavior: 'smooth' });
        });
        regionsGrid.appendChild(card);
      });
  }
  renderRegionsGrid('all');

  document.querySelectorAll('[data-region-cat]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const cat = btn.getAttribute('data-region-cat');
      document.querySelectorAll('[data-region-cat]').forEach((b) => {
        const on = b === btn;
        b.classList.toggle('is-active', on);
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      renderRegionsGrid(cat);
    });
  });

  // Populate "From Brain to Behavior" section
  const behaviorGrid = document.getElementById('be-behavior-grid');
  if (behaviorGrid) {
    behavior.forEach((item) => {
      const art = document.createElement('article');
      art.className = 'be-behavior-card glass-panel';

      const en = document.createElement('span');
      en.className = 'be-en-name';
      en.lang = 'en';
      en.dir = 'ltr';
      en.textContent = item.enTitle;

      const h3 = document.createElement('h3');
      h3.textContent = item.title;

      const sit = document.createElement('p');
      const sitB = document.createElement('strong');
      sitB.textContent = 'الموقف اليومي: ';
      sit.append(sitB, document.createTextNode(item.situation));

      const sysWrap = document.createElement('div');
      sysWrap.className = 'be-behavior-systems';
      item.systems.forEach((s) => {
        const tag = document.createElement('span');
        tag.className = 'be-concept-tag';
        tag.textContent = s;
        sysWrap.appendChild(tag);
      });

      const exp = document.createElement('p');
      exp.textContent = item.explanation;

      const take = document.createElement('p');
      take.className = 'be-example-box';
      const takeB = document.createElement('strong');
      takeB.textContent = 'خلاصة عملية: ';
      take.append(takeB, document.createTextNode(item.takeaway));

      const links = document.createElement('div');
      links.className = 'be-behavior-links';
      item.links.forEach((lk) => {
        const a = document.createElement('a');
        a.href = lk.href;
        a.textContent = lk.label + ' ←';
        links.appendChild(a);
      });

      art.append(en, h3, sit, sysWrap, exp, take, links);
      behaviorGrid.appendChild(art);
    });
  }

  // Initialize 6 Psychological Modes synced with 3D Viewer
  initModes({
    modes,
    regionsById,
    onHighlightStep: (mode, allIds, activeId) => {
      if (modeBadge) {
        modeBadge.textContent = `الوضع النشط: ${mode.arTitle}`;
        modeBadge.hidden = false;
      }
      if (viewer3D) {
        const xrayNow = viewer3D.highlightMode(allIds, activeId);
        if (btnXray) btnXray.setAttribute('aria-pressed', xrayNow ? 'true' : 'false');
      }
      if (activeId) renderInfoPanel(activeId);
    },
  });

  // Initialize Neuron Communication Lab
  initNeuronLab();

  // Initialize Knowledge Center (Quizzes, Flashcards, Glossary, References)
  initKnowledgeCenter({ quizzesData: quizzes, glossaryData: glossary, referencesData: references });
}

boot().catch((err) => {
  const lp = document.getElementById('be-loader-progress');
  if (lp) lp.textContent = 'حدث خطأ أثناء تحميل البيانات التعليمية: ' + err.message;
});
