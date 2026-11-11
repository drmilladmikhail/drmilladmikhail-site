/* depth3d.js — light 3D layer for drmilladmikhail.com (pairs with depth3d.css).
   1. Homepage hero stage follows the mouse (desktop), the phone's tilt
      (Android) or the scroll position (iPhone and others).
   2. Link cards tilt in 3D under the mouse and press in under a finger.
   3. Cards below the fold unfold in 3D as they scroll into view.
   4. On computers and strong phones, a real WebGL sphere replaces the CSS one.
   Pure decoration: nothing is stored or sent, and it all switches off for
   visitors who ask their device for reduced motion. */
(function () {
  'use strict';
  var root = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;
  root.classList.add('d3-js');
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------- 1. hero stage ---------- */
  var stage = document.querySelector('.h3d-stage');
  if (stage) {
    var hero = stage.closest('section') || document.body;
    var target = { x: 8, y: -10 }, frame = 0;
    var apply = function () {
      frame = 0;
      stage.style.setProperty('--h3d-rx', target.x.toFixed(2) + 'deg');
      stage.style.setProperty('--h3d-ry', target.y.toFixed(2) + 'deg');
    };
    var queue = function () { if (!frame) frame = requestAnimationFrame(apply); };
    window.__h3dTarget = target;
    if (fine) {
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        target.x = 8 - py * 14; target.y = -10 + px * 22; queue();
      });
      hero.addEventListener('pointerleave', function () { target.x = 8; target.y = -10; queue(); });
    } else {
      var gyro = false;
      window.addEventListener('deviceorientation', function (e) {
        if (e.beta == null || e.gamma == null) return;
        gyro = true;
        var g = Math.max(-25, Math.min(25, e.gamma)), b = Math.max(10, Math.min(70, e.beta));
        target.y = -10 + g * 0.6; target.x = 8 + (b - 40) * 0.25; queue();
      });
      window.addEventListener('scroll', function () {
        if (gyro) return;
        var p = Math.min(1, Math.max(0, window.scrollY / 700));
        target.x = 8 + p * 10; target.y = -10 + p * 18; queue();
      }, { passive: true });
    }
  }

  /* ---------- 4. real 3D sphere (WebGL) on capable devices ---------- */
  /* A tiny hand-written shader (no library): a glossy, slowly "breathing"
     sphere with a gold orbit ring and moving glints. Only on computers and
     strong phones, never on Data Saver / slow connections; otherwise the
     CSS sphere stays. It pauses when off screen or in a background tab. */
  function whenIdle(fn) {
    /* start only after the page has loaded and the main thread is free,
       so the 3D never delays the first view (LCP) or taps (TBT/INP) */
    function go() { (window.requestIdleCallback || function (f) { setTimeout(f, 300); })(fn, { timeout: 2500 }); }
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go, { once: true });
  }
  whenIdle(function () {
    var core = document.querySelector('.h3d-core');
    if (!core) return;
    var conn = navigator.connection || {};
    if (conn.saveData || /(^|-)2g|3g/.test(conn.effectiveType || '')) return;
    var cores = navigator.hardwareConcurrency || 2, mem = navigator.deviceMemory || 4;
    if (!fine && (cores < 6 || mem < 4)) return;
    var canvas = document.createElement('canvas');
    canvas.className = 'h3d-gl';
    canvas.setAttribute('aria-hidden', 'true');
    var gl = canvas.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: false, powerPreference: 'low-power' });
    if (!gl) return;
    /* no graphics chip (software rendering: SwiftShader, llvmpipe…) → each frame would block the
       main thread for 100 ms+, so keep the CSS sphere */
    var dbg = gl.getExtension('WEBGL_debug_renderer_info');
    var renderer = String(dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER) || '');
    if (/swiftshader|llvmpipe|softpipe|software|basic render|microsoft basic/i.test(renderer)) {
      var lose = gl.getExtension('WEBGL_lose_context'); if (lose) lose.loseContext();
      return;
    }
    var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
    var FS = [
      'precision mediump float;',
      'uniform vec2 res;uniform float t;uniform vec2 rot;',
      'mat3 rY(float a){float c=cos(a),s=sin(a);return mat3(c,0.,-s,0.,1.,0.,s,0.,c);}',
      'mat3 rX(float a){float c=cos(a),s=sin(a);return mat3(1.,0.,0.,0.,c,s,0.,-s,c);}',
      'void main(){',
      ' vec2 uv=(gl_FragCoord.xy-.5*res)/res.y;',
      ' float px=1.5/res.y;',
      ' mat3 m=rY(rot.y)*rX(rot.x);',
      ' vec3 ro=m*vec3(0.,0.,3.2), rd=m*normalize(vec3(uv,-1.75));',
      ' float R=.5*(1.+.012*sin(t*.9));',
      ' vec3 col=vec3(0.);float a=0.;',
      ' float b=dot(-ro,rd); vec3 cpt=ro+rd*b; float dm=length(cpt);',
      ' float ts=1e9;',
      ' if(dm<R+px){',
      '  float h=sqrt(max(R*R-dm*dm,0.)); ts=b-h; vec3 p=ro+rd*ts; vec3 n=normalize(p);',
      '  vec3 q=p*3.;',
      '  n=normalize(n+.07*vec3(sin(q.y*2.+t*.7),sin(q.z*2.3+t*.6),sin(q.x*2.1+t*.5)));',
      '  float sw=.5+.5*sin(p.x*4.+p.y*3.+t*.45+2.*sin(p.z*5.+t*.35));',
      '  vec3 deep=vec3(.12,.30,.26), mid=vec3(.18,.44,.38), mint=vec3(.80,.90,.86);',
      '  vec3 l=normalize(m*vec3(-.55,.7,.65));',
      '  float d=max(dot(n,l),0.);',
      '  vec3 base=mix(deep,mid,d); base=mix(base,mint,pow(d,3.)*.85); base+=sw*.06*vec3(.6,.9,.8);',
      '  float sp=pow(max(dot(reflect(-l,n),-rd),0.),64.);',
      '  float fr=pow(1.-max(dot(n,-rd),0.),3.);',
      '  vec3 rf=reflect(rd,n); float sky=smoothstep(-.3,.9,rf.y);',
      '  float sheen=pow(max(dot(reflect(-l,n),-rd),0.),8.);',
      '  col=base*(.55+.6*d)+mix(vec3(.04,.12,.10),vec3(.78,.92,.88),sky)*(.18+.5*fr)+sp*1.1+sheen*.12+fr*vec3(.89,.70,.35)*.45;',
      '  a=smoothstep(R+px,R-px,dm);',
      ' }',
      ' vec3 pm=col*a;',
      ' float glow=exp(-max(dm-R,0.)*9.)*.22*(1.-a);',
      ' pm+=vec3(.55,.80,.72)*glow; a+=glow;',
      ' vec3 nr=normalize(vec3(.05,.96,.27));',
      ' float dn=dot(rd,nr);',
      ' if(abs(dn)>1e-4){',
      '  float tr=-dot(ro,nr)/dn;',
      '  if(tr>0.&&tr<ts){',
      '   vec3 q=ro+rd*tr; float rr=length(q); float dd=abs(rr-.92);',
      '   vec3 e1=normalize(cross(nr,vec3(0.,0.,1.))), e2=cross(nr,e1);',
      '   float ang=atan(dot(q,e2),dot(q,e1));',
      '   float gl=pow(.5+.5*cos(ang-t*.55),60.)+.6*pow(.5+.5*cos(ang+2.4-t*.55),90.);',
      '   float line=smoothstep(.011,.0,dd);',
      '   float halo=exp(-dd*55.)*.35;',
      '   float ra=clamp(line*.85+halo+gl*exp(-dd*40.)*1.2,0.,1.);',
      '   vec3 gold=vec3(.89,.70,.35);',
      '   pm=pm*(1.-ra)+(gold+gl*vec3(.35,.3,.2))*ra; a=a*(1.-ra)+ra;',
      '  }',
      ' }',
      ' for(int i=0;i<10;i++){',
      '  float fi=float(i); float sp2=.25*(1.+fi*.08);',
      '  vec3 P=vec3(cos(fi*2.4+t*sp2),sin(fi*1.7+t*.2)*.5,sin(fi*2.4+t*sp2))*(.72+.1*sin(fi*1.3));',
      '  vec3 v=P-ro; float tp=dot(v,rd);',
      '  if(tp<ts){ float dd2=length(v-rd*tp); float s=exp(-dd2*dd2*7000.)*(.55+.45*sin(t*1.7+fi*2.1));',
      '   pm+=vec3(1.,.86,.56)*s; a=a+s*(1.-a);}',
      ' }',
      ' gl_FragColor=vec4(pm,a);',
      '}'].join('\n');
    function sh(type, src) { var o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o); return gl.getShaderParameter(o, gl.COMPILE_STATUS) ? o : null; }
    var vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
    if (!vs || !fs) return;
    var prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
    gl.useProgram(prog);
    var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var uRes = gl.getUniformLocation(prog, 'res'), uT = gl.getUniformLocation(prog, 't'), uRot = gl.getUniformLocation(prog, 'rot');
    core.appendChild(canvas);
    core.classList.add('h3d-has-gl');
    var dpr = Math.min(window.devicePixelRatio || 1, fine ? 2 : 1.5);
    function size() {
      var w = canvas.clientWidth, h = canvas.clientHeight;
      canvas.width = Math.max(1, Math.round(w * dpr)); canvas.height = Math.max(1, Math.round(h * dpr));
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
    size(); window.addEventListener('resize', size);
    var visible = true, running = false, start = performance.now(), cur = { x: 0, y: 0 };
    var n = 0, t10 = 0, last = 0, slow = false, slowFrames = 0;
    function stop() { slow = true; visible = false; core.classList.remove('h3d-has-gl'); canvas.remove(); }
    function frame(now) {
      if (slow || !visible || document.hidden) { running = false; last = 0; return; }
      /* performance guard: if the first ~60 visible frames average over 34 ms,
         this device can't draw it smoothly, so fall back to the CSS sphere */
      if (last && now - last < 250) { n++; if (n === 10) t10 = now; if (n === 70 && (now - t10) / 60 > 34) { stop(); return; } }
      /* and a quick exit: two very slow frames (>80 ms) among the first 15 → stop at once */
      if (last && n < 15 && now - last > 80 && ++slowFrames >= 2) { stop(); return; }
      last = now;
      var tg = window.__h3dTarget || { x: 8, y: -10 };
      cur.x += ((tg.x - 8) * 0.035 - cur.x) * 0.06; cur.y += ((tg.y + 10) * 0.035 - cur.y) * 0.06;
      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uT, (now - start) / 1000);
      gl.uniform2f(uRot, cur.x - 0.12, cur.y + 0.25);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      requestAnimationFrame(frame);
    }
    function run() { if (!running && visible && !document.hidden) { running = true; requestAnimationFrame(frame); } }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; run(); }).observe(core);
    }
    document.addEventListener('visibilitychange', run);
    canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); stop(); });
    run();
  });

  /* ---------- 2. tilting / pressing cards ---------- */
  var SEL = '[data-d3="card"], .card > a, .concern-card, .weekly, .test-card, .vcard, .g-card, .platform-card, .story-card, ' +
            '.ws-card, .path-card, .xt-card, .fw-card, .c-card, .myth-card';
  var cards = Array.prototype.filter.call(document.querySelectorAll(SEL), function (el) {
    if (el.matches('.df-station, .meta, .df-urgent') || el.closest('.h3d-stage')) return false;
    if (el.matches('a, button, [data-d3="card"]')) return true;
    /* only small link cards: big panels, forms and step lists stay flat */
    if (el.querySelector('input, textarea, select, details, ol, form')) return false;
    if (el.getBoundingClientRect().height > 460) return false;
    return !!el.querySelector('a, button');
  });
  cards.forEach(function (el) {
    el.classList.add('d3-tilt');
    var raf = 0, next = '';
    var set = function (t) { next = t; if (!raf) raf = requestAnimationFrame(function () { raf = 0; el.style.transform = next; }); };
    var reset = function () { el.classList.remove('d3-active'); set(''); };
    el.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse' && e.pointerType !== 'pen') return;
      var r = el.getBoundingClientRect();
      if (r.width > 760) return;
      var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
      var max = r.width > 420 ? 4 : 7;
      el.classList.add('d3-active');
      set('perspective(900px) rotateX(' + (-py * max).toFixed(2) + 'deg) rotateY(' + (px * max).toFixed(2) + 'deg) translateZ(14px)');
    });
    el.addEventListener('pointerleave', reset);
    el.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') set('perspective(900px) translateZ(-10px) scale(.985)');
    });
    ['pointerup', 'pointercancel'].forEach(function (t) {
      el.addEventListener(t, function (e) { if (e.pointerType === 'touch') reset(); });
    });
  });

  /* ---------- 3. unfold on scroll ---------- */
  if (!('IntersectionObserver' in window)) return;
  var fold = window.innerHeight;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('d3-in'); io.unobserve(en.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  cards.forEach(function (el) {
    var unit = el.parentElement && el.parentElement.tagName === 'LI' ? el.parentElement : el;
    if (unit.getBoundingClientRect().top < fold) return;
    if (unit.parentElement) unit.parentElement.classList.add('d3-stage');
    unit.classList.add('d3-reveal');
    io.observe(unit);
  });
})();
