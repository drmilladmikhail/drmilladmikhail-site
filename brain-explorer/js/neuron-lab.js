// DMMA Brain Explorer — Interactive Educational Neural Signal Simulation Lab
const PARTS = {
  dendrites: {
    title: 'الزوائد الشجرية (Dendrites)',
    desc: 'تفرعات دقيقة تستقبل الإشارات الكيميائية والكهربائية من الخلايا العصبية المجاورة وتنقلها نحو جسم الخلية.',
    x: 115, y: 170,
  },
  soma: {
    title: 'جسم الخلية العصبية (Cell Body / Soma)',
    desc: 'يحتوي على النواة ويجمع الإشارات الواردة من الزوائد الشجرية؛ وإذا تجاوزت عتبة الاستثارة، يُطلق سيالاً عصبياً عبر المحور.',
    x: 225, y: 170,
  },
  axon: {
    title: 'المحور العصبي (Axon)',
    desc: 'ليف عصبي طويل ينقل النبضة الكهربائية (جهد الفعل) بعيداً عن جسم الخلية باتجاه النهايات المشبكية.',
    x: 470, y: 170,
  },
  myelin: {
    title: 'غمد المايلين (Myelin Sheath)',
    desc: 'طبقات عازلة متقطعة تلفّ المحور العصبي وتسمح للإشارة بالقفز السريع بين عقد رانفييه (النقل القفزي) لزيادة السرعة والكفاءة.',
    x: 470, y: 132,
  },
  synapse: {
    title: 'الشق المشبكي (Synaptic Cleft)',
    desc: 'فجوة مجهرية تفصل بين نهاية محور الخلية المرسِلة والزوائد الشجرية للخلية المستقبِلة، حيث تتحول الإشارة الكهربائية إلى رسالة كيميائية.',
    x: 735, y: 170,
  },
  neurotransmitters: {
    title: 'النواقل العصبية (Neurotransmitters)',
    desc: 'جزيئات كيميائية (مثل الجلوتامات وGABA والدوبامين والسيروتونين) تُطلق من الحويصلات لترتبط بمستقبلات الخلية التالية وتنقل الرسالة.',
    x: 760, y: 170,
  },
};

export function initNeuronLab() {
  const canvas = document.getElementById('neuron-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const fireBtn = document.getElementById('btn-fire-signal');
  const autoBtn = document.getElementById('btn-neuron-auto');
  const partBtns = Array.from(document.querySelectorAll('[data-npart]'));
  const titleEl = document.getElementById('neuron-part-title');
  const descEl = document.getElementById('neuron-part-desc');

  const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let activePart = 'dendrites';
  let autoFire = false;
  let pulses = [];
  let transmitters = [];
  let lastAuto = 0;

  function selectPart(key) {
    activePart = key;
    const p = PARTS[key];
    if (p) {
      titleEl.textContent = p.title;
      descEl.textContent = p.desc;
    }
    partBtns.forEach((b) => {
      const on = b.getAttribute('data-npart') === key;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function fireSignal() {
    pulses.push({ progress: 0 });
  }

  partBtns.forEach((b) => {
    b.addEventListener('click', () => selectPart(b.getAttribute('data-npart')));
  });
  if (fireBtn) fireBtn.addEventListener('click', fireSignal);
  if (autoBtn) {
    autoBtn.addEventListener('click', () => {
      autoFire = !autoFire;
      autoBtn.setAttribute('aria-pressed', autoFire ? 'true' : 'false');
      if (autoFire) fireSignal();
    });
  }

  selectPart('dendrites');

  function drawScene(now) {
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Background subtle grid
    ctx.fillStyle = '#060d1c';
    ctx.fillRect(0, 0, w, h);

    if (autoFire && !reducedMotion && now - lastAuto > 2200) {
      fireSignal();
      lastAuto = now;
    }

    // 1. Dendrites (left branching fibers)
    const dendBranches = [
      [[225, 170], [150, 118], [92, 86]],
      [[150, 118], [108, 130]],
      [[225, 170], [138, 170], [72, 168]],
      [[225, 170], [150, 224], [92, 256]],
      [[150, 224], [110, 212]],
    ];
    ctx.lineCap = 'round';
    dendBranches.forEach((pts) => {
      ctx.beginPath();
      ctx.moveTo(pts[0][0], pts[0][1]);
      for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
      ctx.strokeStyle = activePart === 'dendrites' ? '#f7d68c' : '#5cc2f8';
      ctx.lineWidth = activePart === 'dendrites' ? 4.2 : 2.8;
      ctx.stroke();
    });

    // 2. Axon shaft
    ctx.beginPath();
    ctx.moveTo(260, 170);
    ctx.lineTo(695, 170);
    ctx.strokeStyle = activePart === 'axon' ? '#f7d68c' : '#4a8ec2';
    ctx.lineWidth = activePart === 'axon' ? 7 : 5;
    ctx.stroke();

    // 3. Myelin sheath segments (with Nodes of Ranvier gaps)
    const segments = [295, 392, 489, 586];
    segments.forEach((sx) => {
      ctx.fillStyle = activePart === 'myelin' ? 'rgba(247, 214, 140, 0.42)' : 'rgba(92, 194, 248, 0.24)';
      ctx.strokeStyle = activePart === 'myelin' ? '#f7d68c' : '#5cc2f8';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(sx, 150, 78, 40, 16);
      ctx.fill();
      ctx.stroke();
    });

    // 4. Soma (Cell Body + Nucleus)
    ctx.beginPath();
    ctx.arc(225, 170, 40, 0, Math.PI * 2);
    ctx.fillStyle = activePart === 'soma' ? 'rgba(229, 185, 100, 0.34)' : 'rgba(35, 72, 128, 0.85)';
    ctx.fill();
    ctx.strokeStyle = activePart === 'soma' ? '#f7d68c' : '#5cc2f8';
    ctx.lineWidth = 2.6;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(225, 170, 14, 0, Math.PI * 2);
    ctx.fillStyle = '#e5b964';
    ctx.fill();

    // 5. Axon terminal bulb (presynaptic)
    ctx.beginPath();
    ctx.moveTo(685, 166);
    ctx.quadraticCurveTo(722, 134, 730, 170);
    ctx.quadraticCurveTo(722, 206, 685, 174);
    ctx.closePath();
    ctx.fillStyle = activePart === 'synapse' ? 'rgba(229, 185, 100, 0.38)' : 'rgba(65, 130, 186, 0.72)';
    ctx.fill();
    ctx.strokeStyle = activePart === 'synapse' ? '#f7d68c' : '#5cc2f8';
    ctx.lineWidth = 2.2;
    ctx.stroke();

    // 6. Postsynaptic receiving neuron dendrite (right)
    ctx.beginPath();
    ctx.arc(845, 170, 56, Math.PI * 0.65, Math.PI * 1.35, false);
    ctx.strokeStyle = '#57d6be';
    ctx.lineWidth = 8;
    ctx.stroke();

    // Synaptic cleft subtle highlight
    if (activePart === 'synapse' || activePart === 'neurotransmitters') {
      ctx.fillStyle = 'rgba(229, 185, 100, 0.12)';
      ctx.fillRect(732, 118, 56, 104);
    }

    // 7. Update & draw traveling action potential pulses
    for (let i = pulses.length - 1; i >= 0; i--) {
      const p = pulses[i];
      p.progress += reducedMotion ? 0.03 : 0.014;
      let px, py = 170;
      if (p.progress < 0.22) {
        const u = p.progress / 0.22;
        px = 92 + (225 - 92) * u;
        py = 86 + (170 - 86) * u;
      } else if (p.progress < 0.85) {
        const u = (p.progress - 0.22) / 0.63;
        px = 225 + (726 - 225) * u;
      } else {
        // Spawn neurotransmitter burst across synaptic cleft
        for (let k = 0; k < 10; k++) {
          transmitters.push({
            x: 734,
            y: 150 + k * 4.2,
            vx: 1.1 + (k % 3) * 0.35,
            vy: ((k % 5) - 2) * 0.25,
            life: 1.0,
          });
        }
        pulses.splice(i, 1);
        continue;
      }

      const grad = ctx.createRadialGradient(px, py, 2, px, py, 22);
      grad.addColorStop(0, '#fff7dc');
      grad.addColorStop(0.35, '#f7d68c');
      grad.addColorStop(1, 'rgba(247, 214, 140, 0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(px, py, 22, 0, Math.PI * 2);
      ctx.fill();
    }

    // 8. Update & draw neurotransmitters crossing synaptic cleft
    for (let j = transmitters.length - 1; j >= 0; j--) {
      const nt = transmitters[j];
      nt.x += nt.vx;
      nt.y += nt.vy;
      nt.life -= 0.022;
      if (nt.life <= 0 || nt.x > 792) {
        transmitters.splice(j, 1);
        continue;
      }
      ctx.beginPath();
      ctx.arc(nt.x, nt.y, 3.6, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(87, 214, 190, ${nt.life.toFixed(2)})`;
      ctx.fill();
    }

    // 9. Crisp labels
    ctx.font = '600 13px "IBM Plex Sans Arabic", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = '#dbe7f5';
    ctx.fillText('الزوائد الشجرية', 120, 295);
    ctx.fillText('جسم الخلية', 225, 295);
    ctx.fillText('غمد المايلين والمحور العصبي', 475, 295);
    ctx.fillText('الشق المشبكي والنواقل', 755, 295);
    ctx.fillText('الخلية المستقبِلة', 878, 295);

    requestAnimationFrame(drawScene);
  }

  requestAnimationFrame(drawScene);
}
