/* /explore/explore.js — 60fps HTML5 Canvas Knowledge Graph + Search + Filter + Glass Card (Strict CSP) */
(function () {
  'use strict';

  var canvas = document.getElementById('explore-canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d', { alpha: true });

  var searchInput = document.getElementById('explore-search');
  var searchClear = document.getElementById('search-clear');
  var filterBtns = Array.prototype.slice.call(document.querySelectorAll('.ex-filter'));
  var statusEl = document.getElementById('explore-status');
  var cornerEl = document.getElementById('parallax-corner');
  var hintEl = document.getElementById('mobile-hint');
  var emptyToast = document.getElementById('empty-toast');
  var resetAllBtn = document.getElementById('reset-all');

  var cardEl = document.getElementById('node-card');
  var cardClose = document.getElementById('card-close');
  var cardType = document.getElementById('card-type');
  var cardTitle = document.getElementById('card-title');
  var cardSummary = document.getElementById('card-summary');
  var cardRelated = document.getElementById('card-related');
  var cardCta = document.getElementById('card-cta');
  var cardCtaLabel = document.getElementById('card-cta-label');

  var zoomInBtn = document.getElementById('zoom-in');
  var zoomOutBtn = document.getElementById('zoom-out');
  var zoomResetBtn = document.getElementById('zoom-reset');

  var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Color palette matching warm nocturnal theme
  var PALETTE = {
    article:  { glow: '#f0be65', core: '#fff7e2', label: 'مقال', cta: 'اقرأ المقال' },
    glossary: { glow: '#e8b358', core: '#fff5dc', label: 'مصطلح نفسي', cta: 'اقرأ المصطلح' },
    feeling:  { glow: '#f0a568', core: '#fff0e4', label: 'مشاعر', cta: 'افهم الشعور' },
    exercise: { glow: '#6ec4f7', core: '#eaf7ff', label: 'تمرين عملي', cta: 'ابدأ التمرين' },
    audio:    { glow: '#70dfc6', core: '#eafff9', label: 'دقيقة لنفسك', cta: 'استمع الآن' }
  };

  // Pre-render offscreen radial glow sprites once for 60fps mobile rendering
  var SPRITES = {};
  function makeGlowSprite(hexColor) {
    var s = document.createElement('canvas');
    s.width = 64;
    s.height = 64;
    var sc = s.getContext('2d');
    var g = sc.createRadialGradient(32, 32, 1.5, 32, 32, 30);
    g.addColorStop(0, '#ffffff');
    g.addColorStop(0.18, hexColor);
    g.addColorStop(0.50, hexColor + '55');
    g.addColorStop(1, hexColor + '00');
    sc.fillStyle = g;
    sc.fillRect(0, 0, 64, 64);
    return s;
  }
  Object.keys(PALETTE).forEach(function (k) {
    SPRITES[k] = makeGlowSprite(PALETTE[k].glow);
  });

  // Normalize Arabic text for instant search
  function normalizeAr(str) {
    return String(str || '')
      .toLowerCase()
      .replace(/[\u064B-\u065F\u0670\u06D6-\u06ED\u0640]/g, '')
      .replace(/[أإآٱ]/g, 'ا')
      .replace(/ؤ/g, 'و')
      .replace(/[ئى]/g, 'ي')
      .replace(/ة/g, 'ه')
      .replace(/[^\p{L}\p{N}\s]/gu, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  var width = 1, height = 1, dpr = 1;
  var nodes = [], links = [], nodeMap = {}, adjacency = {};
  var stars = [];
  var activeFilter = 'all';
  var searchQuery = '';
  var selectedNode = null;
  var hoveredNode = null;

  // Camera in normalized world space (center cx, cy, zoom scale)
  var cam = { x: 0.42, y: 0.44, zoom: 1.0, tx: 0.42, ty: 0.44, tzoom: 1.0 };
  var parallax = { x: 0, y: 0, tx: 0, ty: 0 };

  function isMobile() {
    return width <= 880;
  }

  function defaultCamera() {
    if (isMobile()) {
      return { x: 0.41, y: 0.43, zoom: 1.02 };
    }
    // Offset right in world space so constellation sits center-left above the reading corner
    return { x: 0.48, y: 0.41, zoom: 1.04 };
  }

  function resetCamera() {
    var d = defaultCamera();
    cam.tx = d.x;
    cam.ty = d.y;
    cam.tzoom = d.zoom;
  }

  function resize() {
    var rect = canvas.getBoundingClientRect();
    width = Math.max(1, rect.width);
    height = Math.max(1, rect.height);
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function initStars() {
    stars = [];
    var count = isMobile() ? 38 : 62;
    for (var i = 0; i < count; i++) {
      stars.push({
        x: (Math.sin(i * 12.9898) * 43758.5453) % 1,
        y: (Math.sin(i * 78.233 + 1.7) * 24634.6345) % 1,
        r: 0.7 + (i % 4) * 0.45,
        phase: i * 0.9,
        speed: 0.6 + (i % 5) * 0.22,
        gold: i % 3 !== 0,
        depth: 0.25 + (i % 5) * 0.15
      });
    }
    stars.forEach(function (s) {
      if (s.x < 0) s.x += 1;
      if (s.y < 0) s.y += 1;
    });
  }

  function worldToScreen(wx, wy) {
    var span = Math.min(width, height) * 1.08 * cam.zoom;
    var sx = width * 0.5 + (wx - cam.x) * span;
    var sy = height * 0.5 + (wy - cam.y) * span;
    return { x: sx, y: sy };
  }

  function screenToWorld(sx, sy) {
    var span = Math.min(width, height) * 1.08 * cam.zoom;
    return {
      x: cam.x + (sx - width * 0.5) / span,
      y: cam.y + (sy - height * 0.5) / span
    };
  }

  function focusOnNode(node, zoomBoost) {
    if (!node) return;
    var targetZ = zoomBoost || (isMobile() ? 1.32 : 1.24);
    var span = Math.min(width, height) * 1.08 * targetZ;
    // Shift camera center so node isn't covered by right desktop card or bottom mobile sheet
    var offsetX = isMobile() ? 0 : (155 / span);
    var offsetY = isMobile() ? (height * 0.17 / span) : 0;
    cam.tx = node.x + offsetX;
    cam.ty = node.y + offsetY;
    cam.tzoom = targetZ;
  }

  function applyFilterAndSearch(focusCamera) {
    var q = normalizeAr(searchQuery);
    var words = q ? q.split(' ') : [];
    var directHits = [];

    nodes.forEach(function (n) {
      var typeOk = activeFilter === 'all' || n.type === activeFilter;
      var searchOk = !words.length || words.every(function (w) { return n._norm.indexOf(w) !== -1; });
      n.matched = typeOk && searchOk;
      if (n.matched) directHits.push(n);
    });

    // When searching, also softly show direct neighbors of matched nodes for context
    var neighborSet = {};
    if (words.length && directHits.length > 0 && directHits.length <= 12) {
      directHits.forEach(function (n) {
        (adjacency[n.id] || []).forEach(function (nb) {
          if (activeFilter === 'all' || nb.type === activeFilter) {
            neighborSet[nb.id] = true;
          }
        });
      });
    }

    nodes.forEach(function (n) {
      if (n.matched) {
        n.targetAlpha = 1.0;
      } else if (neighborSet[n.id]) {
        n.targetAlpha = 0.42;
      } else {
        n.targetAlpha = words.length ? 0.06 : 0.0;
      }
      n.interactive = n.matched || Boolean(neighborSet[n.id]);
    });

    // Update status counter & empty state
    if (statusEl) {
      statusEl.textContent = directHits.length.toLocaleString('ar-EG') +
        (words.length ? ' نتيجة مطابقة' : ' موضوع مترابط');
    }
    if (emptyToast) {
      emptyToast.hidden = directHits.length > 0;
    }

    if (selectedNode && !selectedNode.interactive) {
      closeCard();
    }

    if (focusCamera && directHits.length > 0) {
      if (words.length) {
        // Rank best title match
        directHits.sort(function (a, b) {
          var aTitle = a._normTitle.indexOf(q) !== -1 ? 1 : 0;
          var bTitle = b._normTitle.indexOf(q) !== -1 ? 1 : 0;
          return bTitle - aTitle || (b.hub ? 1 : 0) - (a.hub ? 1 : 0);
        });
        var best = directHits[0];
        if (directHits.length === 1) {
          selectNode(best, true);
        } else {
          focusOnNode(best, isMobile() ? 1.25 : 1.18);
        }
      } else if (activeFilter !== 'all') {
        // Center on centroid of filtered group
        var sx = 0, sy = 0;
        directHits.forEach(function (n) { sx += n.x; sy += n.y; });
        sx /= directHits.length;
        sy /= directHits.length;
        cam.tx = sx + (isMobile() ? 0 : 0.07);
        cam.ty = sy;
        cam.tzoom = isMobile() ? 1.08 : 1.06;
      } else {
        resetCamera();
      }
    }
  }

  function openCard(node) {
    if (!node || !cardEl) return;
    var meta = PALETTE[node.type] || PALETTE.article;
    cardType.textContent = node.typeLabel || meta.label;
    cardType.setAttribute('data-type', node.type);
    cardTitle.textContent = node.title;
    cardSummary.textContent = node.summary;
    cardCta.setAttribute('href', node.href);
    cardCtaLabel.textContent = node.cta || meta.cta;

    while (cardRelated.firstChild) {
      cardRelated.removeChild(cardRelated.firstChild);
    }

    var neighbors = (adjacency[node.id] || []).slice(0, 5);
    if (neighbors.length === 0 && node.tags) {
      node.tags.forEach(function (tag) {
        var span = document.createElement('span');
        span.className = 'ex-pill';
        span.textContent = tag;
        cardRelated.appendChild(span);
      });
    } else {
      neighbors.forEach(function (nb) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'ex-pill';
        btn.textContent = nb.label;
        btn.addEventListener('click', function () {
          if (activeFilter !== 'all' && nb.type !== activeFilter) {
            setFilter('all', false);
          }
          selectNode(nb, true);
        });
        cardRelated.appendChild(btn);
      });
    }

    cardEl.hidden = false;
    if (hintEl && isMobile()) {
      hintEl.hidden = true;
    }
  }

  function closeCard() {
    selectedNode = null;
    if (cardEl) cardEl.hidden = true;
    if (hintEl && isMobile()) hintEl.hidden = false;
  }

  function selectNode(node, moveCamera) {
    selectedNode = node;
    openCard(node);
    if (moveCamera) {
      focusOnNode(node);
    }
  }

  function setFilter(filterVal, moveCam) {
    activeFilter = filterVal;
    filterBtns.forEach(function (btn) {
      var on = btn.getAttribute('data-filter') === filterVal;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    applyFilterAndSearch(moveCam !== false);
  }

  // Hit-test nodes in screen space
  function pickNodeAt(sx, sy) {
    var best = null;
    var bestDist = 28; // generous touch/click radius
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      if (!n.interactive || n.alpha < 0.2) continue;
      var dx = sx - n.sx;
      var dy = sy - n.sy;
      var d = Math.sqrt(dx * dx + dy * dy);
      var hitR = (n.hub ? 22 : 17) * Math.min(1.3, cam.zoom);
      if (d < Math.max(hitR, 16) && d < bestDist) {
        bestDist = d;
        best = n;
      }
    }
    return best;
  }

  // Pointer & Touch handling (pan, tap, hover, pinch-zoom, parallax)
  var drag = { active: false, moved: false, startX: 0, startY: 0, camX: 0, camY: 0 };
  var pointers = {};
  var pinchDist = 0;

  canvas.addEventListener('pointerdown', function (e) {
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    var keys = Object.keys(pointers);
    if (keys.length === 2) {
      var p1 = pointers[keys[0]], p2 = pointers[keys[1]];
      pinchDist = Math.hypot(p2.x - p1.x, p2.y - p1.y);
      drag.moved = true;
      return;
    }
    drag.active = true;
    drag.moved = false;
    drag.startX = e.clientX;
    drag.startY = e.clientY;
    drag.camX = cam.tx;
    drag.camY = cam.ty;
    canvas.classList.add('is-dragging');
  });

  window.addEventListener('pointermove', function (e) {
    var rect = canvas.getBoundingClientRect();
    var lx = e.clientX - rect.left;
    var ly = e.clientY - rect.top;

    if (!reducedMotion && width > 0 && height > 0) {
      parallax.tx = ((lx / width) - 0.5) * -16;
      parallax.ty = ((ly / height) - 0.5) * -12;
    }

    if (pointers[e.pointerId]) {
      pointers[e.pointerId].x = e.clientX;
      pointers[e.pointerId].y = e.clientY;
    }

    var keys = Object.keys(pointers);
    if (keys.length === 2) {
      var p1 = pointers[keys[0]], p2 = pointers[keys[1]];
      var dist = Math.hypot(p2.x - p1.x, p2.y - p1.y);
      if (pinchDist > 10) {
        var ratio = dist / pinchDist;
        cam.tzoom = Math.max(0.68, Math.min(2.4, cam.tzoom * ratio));
      }
      pinchDist = dist;
      return;
    }

    if (drag.active) {
      var dx = e.clientX - drag.startX;
      var dy = e.clientY - drag.startY;
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
        drag.moved = true;
      }
      if (drag.moved) {
        var span = Math.min(width, height) * 1.08 * cam.zoom;
        cam.tx = Math.max(0.05, Math.min(0.95, drag.camX - dx / span));
        cam.ty = Math.max(0.08, Math.min(0.92, drag.camY - dy / span));
      }
      return;
    }

    if (e.pointerType === 'mouse' && ly >= 0 && ly <= height) {
      hoveredNode = pickNodeAt(lx, ly);
      canvas.classList.toggle('is-pointer', Boolean(hoveredNode));
    }
  });

  function endPointer(e) {
    delete pointers[e.pointerId];
    if (Object.keys(pointers).length < 2) pinchDist = 0;

    if (!drag.active) return;
    canvas.classList.remove('is-dragging');
    var wasMoved = drag.moved;
    drag.active = false;

    if (!wasMoved) {
      var rect = canvas.getBoundingClientRect();
      var hit = pickNodeAt(e.clientX - rect.left, e.clientY - rect.top);
      if (hit) {
        selectNode(hit, true);
      } else if (isMobile() && selectedNode) {
        closeCard();
      }
    }
  }
  window.addEventListener('pointerup', endPointer);
  window.addEventListener('pointercancel', endPointer);

  canvas.addEventListener('wheel', function (e) {
    e.preventDefault();
    var rect = canvas.getBoundingClientRect();
    var mx = e.clientX - rect.left;
    var my = e.clientY - rect.top;
    var before = screenToWorld(mx, my);
    var factor = e.deltaY < 0 ? 1.12 : 0.89;
    var nextZ = Math.max(0.68, Math.min(2.4, cam.tzoom * factor));
    cam.tzoom = nextZ;
    var span = Math.min(width, height) * 1.08 * nextZ;
    cam.tx = Math.max(0.05, Math.min(0.95, before.x - (mx - width * 0.5) / span));
    cam.ty = Math.max(0.08, Math.min(0.92, before.y - (my - height * 0.5) / span));
  }, { passive: false });

  // Controls & Search bindings
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      setFilter(btn.getAttribute('data-filter'), true);
    });
  });

  var searchTimer = null;
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      searchQuery = searchInput.value;
      if (searchClear) searchClear.hidden = !searchQuery;
      clearTimeout(searchTimer);
      searchTimer = setTimeout(function () {
        applyFilterAndSearch(true);
      }, 120);
    });
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        clearTimeout(searchTimer);
        applyFilterAndSearch(true);
      }
    });
  }

  if (searchClear) {
    searchClear.addEventListener('click', function () {
      searchInput.value = '';
      searchQuery = '';
      searchClear.hidden = true;
      applyFilterAndSearch(true);
      searchInput.focus();
    });
  }

  if (resetAllBtn) {
    resetAllBtn.addEventListener('click', function () {
      if (searchInput) searchInput.value = '';
      searchQuery = '';
      if (searchClear) searchClear.hidden = true;
      setFilter('all', true);
    });
  }

  if (cardClose) {
    cardClose.addEventListener('click', function () {
      closeCard();
    });
  }

  if (zoomInBtn) {
    zoomInBtn.addEventListener('click', function () {
      cam.tzoom = Math.min(2.4, cam.tzoom * 1.22);
    });
  }
  if (zoomOutBtn) {
    zoomOutBtn.addEventListener('click', function () {
      cam.tzoom = Math.max(0.68, cam.tzoom * 0.82);
    });
  }
  if (zoomResetBtn) {
    zoomResetBtn.addEventListener('click', function () {
      resetCamera();
    });
  }

  window.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && selectedNode) {
      closeCard();
    }
  });

  window.addEventListener('resize', function () {
    resize();
  });

  // Main 60fps Render Loop
  var startTime = performance.now();
  function render(now) {
    var t = (now - startTime) * 0.001;

    // Smooth camera & parallax interpolation
    cam.x += (cam.tx - cam.x) * 0.11;
    cam.y += (cam.ty - cam.y) * 0.11;
    cam.zoom += (cam.tzoom - cam.zoom) * 0.11;

    if (!reducedMotion && cornerEl) {
      var camDriftX = (0.45 - cam.x) * 28;
      var camDriftY = (0.45 - cam.y) * 20;
      parallax.x += (parallax.tx + camDriftX - parallax.x) * 0.08;
      parallax.y += (parallax.ty + camDriftY - parallax.y) * 0.08;
      cornerEl.style.transform = 'translate3d(' + parallax.x.toFixed(1) + 'px,' + parallax.y.toFixed(1) + 'px,0)';
    }

    ctx.clearRect(0, 0, width, height);

    // 1. Ambient twinkling starlight motes
    for (var s = 0; s < stars.length; s++) {
      var st = stars[s];
      var twinkle = reducedMotion ? 0.45 : (0.22 + 0.48 * (0.5 + 0.5 * Math.sin(t * st.speed + st.phase)));
      var sx = (st.x * width + parallax.x * st.depth + width) % width;
      var sy = (st.y * height + parallax.y * st.depth + height) % height;
      ctx.beginPath();
      ctx.arc(sx, sy, st.r, 0, Math.PI * 2);
      ctx.fillStyle = st.gold
        ? 'rgba(245, 206, 130, ' + twinkle.toFixed(2) + ')'
        : 'rgba(130, 205, 248, ' + (twinkle * 0.85).toFixed(2) + ')';
      ctx.fill();
    }

    if (!nodes.length) {
      requestAnimationFrame(render);
      return;
    }

    // 2. Update node screen positions + subtle organic breathing motion
    var focusNode = hoveredNode || selectedNode;
    var connectedToFocus = {};
    if (focusNode) {
      connectedToFocus[focusNode.id] = true;
      (adjacency[focusNode.id] || []).forEach(function (nb) {
        connectedToFocus[nb.id] = true;
      });
    }

    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      n.alpha += (n.targetAlpha - n.alpha) * 0.14;
      var floatX = reducedMotion ? 0 : Math.sin(t * 0.75 + n.phase) * 0.0028;
      var floatY = reducedMotion ? 0 : Math.cos(t * 0.65 + n.phase * 1.3) * 0.0028;
      var sp = worldToScreen(n.x + floatX, n.y + floatY);
      n.sx = sp.x;
      n.sy = sp.y;
    }

    // 3. Draw smooth curved constellation links (quadratic bezier)
    ctx.lineCap = 'round';
    for (var l = 0; l < links.length; l++) {
      var lk = links[l];
      var a = lk.a, b = lk.b;
      var linkAlpha = Math.min(a.alpha, b.alpha);
      if (linkAlpha < 0.03) continue;

      var isHighlighted = focusNode && (a.id === focusNode.id || b.id === focusNode.id);
      var mx = (a.sx + b.sx) * 0.5;
      var my = (a.sy + b.sy) * 0.5;
      var dx = b.sx - a.sx;
      var dy = b.sy - a.sy;
      var len = Math.hypot(dx, dy) || 1;
      var bend = lk.bend * Math.min(34, len * 0.16);
      var cx = mx + (-dy / len) * bend;
      var cy = my + (dx / len) * bend;

      ctx.beginPath();
      ctx.moveTo(a.sx, a.sy);
      ctx.quadraticCurveTo(cx, cy, b.sx, b.sy);

      if (isHighlighted) {
        var grad = ctx.createLinearGradient(a.sx, a.sy, b.sx, b.sy);
        grad.addColorStop(0, PALETTE[a.type].glow);
        grad.addColorStop(1, PALETTE[b.type].glow);
        ctx.strokeStyle = grad;
        ctx.globalAlpha = 0.82 * linkAlpha;
        ctx.lineWidth = 1.9;
        ctx.stroke();

        // Traveling luminous pulse along active connection
        if (!reducedMotion) {
          var u = (t * 0.36 + l * 0.19) % 1;
          var iu = 1 - u;
          var px = iu * iu * a.sx + 2 * iu * u * cx + u * u * b.sx;
          var py = iu * iu * a.sy + 2 * iu * u * cy + u * u * b.sy;
          ctx.beginPath();
          ctx.arc(px, py, 2.2, 0, Math.PI * 2);
          ctx.fillStyle = '#fff8e6';
          ctx.fill();
        }
      } else {
        var dimFactor = focusNode ? 0.08 : 0.16;
        ctx.strokeStyle = (l % 4 === 0) ? '#78c6f7' : '#e6b865';
        ctx.globalAlpha = dimFactor * linkAlpha;
        ctx.lineWidth = 1.0;
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;

    // 4. Draw glowing nodes & collision-free RTL Arabic labels
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';

    var showExtraLabels = cam.zoom >= 1.65 || activeFilter !== 'all' || Boolean(searchQuery.trim());

    // First pass: draw all glowing orbs so labels always sit cleanly on top
    for (var k = 0; k < nodes.length; k++) {
      var nd = nodes[k];
      if (nd.alpha < 0.03) continue;
      if (nd.sx < -60 || nd.sx > width + 60 || nd.sy < -60 || nd.sy > height + 60) continue;

      var isSel = selectedNode && nd.id === selectedNode.id;
      var isHov = hoveredNode && nd.id === hoveredNode.id;
      var isConn = Boolean(connectedToFocus[nd.id]);
      var emphasis = isSel ? 1.45 : isHov ? 1.35 : isConn ? 1.15 : (focusNode ? 0.55 : 0.90);

      var baseR = nd.hub ? 5.6 : 3.4;
      var pulse = (!reducedMotion && (nd.hub || isSel)) ? (1 + 0.08 * Math.sin(t * 2.1 + nd.phase)) : 1;
      var r = baseR * pulse * Math.min(1.25, 0.85 + cam.zoom * 0.18) * (isSel || isHov ? 1.25 : 1);
      nd._drawR = r;
      var glowSize = r * (isSel || isHov ? 8.4 : nd.hub ? 6.6 : 4.8);

      ctx.globalAlpha = Math.min(1, nd.alpha * emphasis);

      var sprite = SPRITES[nd.type] || SPRITES.article;
      ctx.drawImage(sprite, nd.sx - glowSize * 0.5, nd.sy - glowSize * 0.5, glowSize, glowSize);

      if (isSel || isHov) {
        ctx.beginPath();
        ctx.arc(nd.sx, nd.sy, r + 5.5, 0, Math.PI * 2);
        ctx.strokeStyle = PALETTE[nd.type].glow;
        ctx.lineWidth = 1.4;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(nd.sx, nd.sy, r, 0, Math.PI * 2);
      ctx.fillStyle = PALETTE[nd.type].core;
      ctx.fill();
    }

    // Second pass: priority-ordered label placement with bounding-box collision culling
    var labelCandidates = [];
    for (var m = 0; m < nodes.length; m++) {
      var cand = nodes[m];
      if (cand.alpha <= 0.32) continue;
      if (cand.sx < 40 || cand.sx > width - 40 || cand.sy < 30 || cand.sy > height - 20) continue;

      var cSel = selectedNode && cand.id === selectedNode.id;
      var cHov = hoveredNode && cand.id === hoveredNode.id;
      var cConn = Boolean(connectedToFocus[cand.id]);
      var wantLabel = cSel || cHov || cConn || cand.hub || showExtraLabels;
      if (!wantLabel) continue;

      var prio = cSel ? 100 : cHov ? 90 : (cand.matched && searchQuery.trim() ? 80 : cConn ? 70 : cand.hub ? 50 : 20);
      labelCandidates.push({ node: cand, prio: prio, isSel: cSel, isHov: cHov, isConn: cConn });
    }

    labelCandidates.sort(function (a, b) { return b.prio - a.prio; });

    var placedBoxes = [];
    if (!isMobile()) {
      // Keep bottom-left reading corner bookshelves & right card zone free of overlapping labels
      placedBoxes.push({ x1: 10, y1: height - 245, x2: 350, y2: height });
      if (selectedNode) {
        placedBoxes.push({ x1: width - 415, y1: height * 0.14, x2: width, y2: height * 0.86 });
      }
    } else if (selectedNode) {
      placedBoxes.push({ x1: 0, y1: height - 350, x2: width, y2: height });
    }

    for (var p = 0; p < labelCandidates.length; p++) {
      var item = labelCandidates[p];
      var ln = item.node;
      var fSize = item.isSel || item.isHov ? 14.5 : ln.hub ? 13.5 : 12;
      ctx.font = (ln.hub || item.isSel ? '700 ' : '600 ') + fSize + 'px "IBM Plex Sans Arabic", sans-serif';

      var estW = Math.max(48, ctx.measureText(ln.label).width) + 18;
      var estH = fSize + 10;
      var ly = ln.sy - (ln._drawR || 4) - 6;
      var box = {
        x1: ln.sx - estW * 0.5,
        y1: ly - estH,
        x2: ln.sx + estW * 0.5,
        y2: ly + 6
      };

      var collides = false;
      if (!item.isSel && !item.isHov) {
        for (var bIdx = 0; bIdx < placedBoxes.length; bIdx++) {
          var ob = placedBoxes[bIdx];
          if (box.x1 < ob.x2 && box.x2 > ob.x1 && box.y1 < ob.y2 && box.y2 > ob.y1) {
            collides = true;
            break;
          }
        }
      }
      if (collides) continue;

      placedBoxes.push(box);
      ctx.globalAlpha = Math.min(1, ln.alpha * (item.isSel || item.isHov || item.isConn ? 1 : 0.92));
      ctx.lineWidth = 3.8;
      ctx.strokeStyle = 'rgba(10, 16, 29, 0.92)';
      ctx.strokeText(ln.label, ln.sx, ly);

      ctx.fillStyle = item.isSel || item.isHov ? '#fff6dc' : (ln.hub ? '#f5efe2' : '#cfdbe9');
      ctx.fillText(ln.label, ln.sx, ly);
    }
    ctx.globalAlpha = 1;

    requestAnimationFrame(render);
  }

  // Load unified graph JSON
  resize();
  initStars();
  var initCam = defaultCamera();
  cam.x = cam.tx = initCam.x;
  cam.y = cam.ty = initCam.y;
  cam.zoom = cam.tzoom = initCam.zoom;
  requestAnimationFrame(render);

  fetch('/explore/graph-data.json')
    .then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(function (data) {
      nodes = (data.nodes || []).map(function (n, idx) {
        n.alpha = 0;
        n.targetAlpha = 1;
        n.interactive = true;
        n.phase = idx * 0.73;
        n.sx = width * 0.5;
        n.sy = height * 0.5;
        var meta = PALETTE[n.type] || PALETTE.article;
        n._normTitle = normalizeAr(n.title + ' ' + n.label);
        n._norm = normalizeAr([n.title, n.label, n.summary, n.typeLabel || meta.label, (n.tags || []).join(' '), n.search || ''].join(' '));
        nodeMap[n.id] = n;
        adjacency[n.id] = [];
        return n;
      });

      links = [];
      (data.links || []).forEach(function (lk, idx) {
        var a = nodeMap[lk.source];
        var b = nodeMap[lk.target];
        if (!a || !b) return;
        adjacency[a.id].push(b);
        adjacency[b.id].push(a);
        links.push({
          a: a,
          b: b,
          weight: lk.weight || 0.5,
          bend: (idx % 2 === 0 ? 1 : -1) * (0.55 + (idx % 3) * 0.25)
        });
      });

      applyFilterAndSearch(false);

      // Select iconic default node on desktop to match warm library showcase; keep mobile unobstructed until tap
      var defId = (data.meta && data.meta.defaultNode) || 'article:four-attachment-styles';
      var defNode = nodeMap[defId] || nodes[0];
      if (!isMobile() && defNode) {
        selectNode(defNode, false);
      }
    })
    .catch(function () {
      if (statusEl) statusEl.textContent = 'تعذّر تحميل بيانات الشبكة';
    });
})();
