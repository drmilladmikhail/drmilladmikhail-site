// DMMA Brain Explorer — Accessible 2D Interactive SVG Brain Fallback (All 15 Structures)
const SVG_NS = 'http://www.w3.org/2000/svg';

const SHAPES = [
  { id: 'prefrontal_cortex', d: 'M125,180 C118,125 152,88 198,80 L212,188 L152,216 C135,212 128,198 125,180 Z', lx: 162, ly: 148 },
  { id: 'frontal_lobe',      d: 'M198,80 C248,68 296,68 332,84 L318,186 L212,188 Z', lx: 262, ly: 125 },
  { id: 'parietal_lobe',     d: 'M332,84 C394,88 446,118 468,168 L372,196 L318,186 Z', lx: 386, ly: 138 },
  { id: 'occipital_lobe',    d: 'M468,168 C488,205 480,256 442,276 L378,242 L372,196 Z', lx: 438, ly: 222 },
  { id: 'temporal_lobe',     d: 'M208,205 L368,198 L382,254 C340,282 252,286 206,256 Z', lx: 294, ly: 244 },
  { id: 'corpus_callosum',   d: 'M234,174 C264,142 332,140 364,174 C350,186 336,184 320,174 C294,166 268,168 248,184 Z', lx: 298, ly: 160 },
  { id: 'anterior_cingulate_cortex', d: 'M220,162 C250,126 312,122 344,144 L334,154 C306,136 258,138 232,170 Z', lx: 280, ly: 138 },
  { id: 'insula',            d: 'M238,192 C258,180 286,184 294,204 C284,222 252,224 238,210 Z', lx: 266, ly: 204 },
  { id: 'basal_ganglia',     d: 'M268,176 C296,170 318,182 320,204 C304,214 278,212 268,196 Z', lx: 294, ly: 194 },
  { id: 'thalamus',          d: 'M298,192 C322,186 346,198 344,216 C332,228 304,226 296,210 Z', lx: 320, ly: 210 },
  { id: 'hypothalamus',      d: 'M272,222 C286,216 300,222 298,238 L282,250 L270,236 Z', lx: 284, ly: 234 },
  { id: 'amygdala',          d: 'M246,238 C258,232 270,240 266,252 C256,258 244,252 246,238 Z', lx: 256, ly: 248 },
  { id: 'hippocampus',       d: 'M268,248 C294,252 324,242 338,224 C346,232 332,256 302,262 C282,266 270,260 268,248 Z', lx: 310, ly: 254 },
  { id: 'cerebellum',        d: 'M366,262 C412,256 446,282 436,318 C416,342 370,338 354,310 Z', lx: 398, ly: 300 },
  { id: 'brainstem',         d: 'M304,248 L338,248 L352,306 L346,368 L314,368 L312,306 Z', lx: 328, ly: 318 },
];

export function createFallback2D({ mount, regionsById, onSelect }) {
  mount.textContent = '';
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('viewBox', '0 0 600 400');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', 'خريطة الدماغ البشري التفاعلية ثنائية الأبعاد — 15 بنية تشريحية');

  const pathMap = new Map();

  SHAPES.forEach((s) => {
    const reg = regionsById.get(s.id);
    if (!reg) return;
    const g = document.createElementNS(SVG_NS, 'g');
    g.setAttribute('class', 'be-svg-region');
    g.setAttribute('tabindex', '0');
    g.setAttribute('role', 'button');
    g.setAttribute('aria-label', `${reg.arName} (${reg.enName})`);

    const path = document.createElementNS(SVG_NS, 'path');
    path.setAttribute('d', s.d);
    path.setAttribute('fill', reg.color);
    path.setAttribute('fill-opacity', reg.isDeep ? '0.88' : '0.42');
    path.setAttribute('stroke', '#e5b964');
    path.setAttribute('stroke-width', '1.4');

    const title = document.createElementNS(SVG_NS, 'title');
    title.textContent = `${reg.arName} — ${reg.enName}`;

    const label = document.createElementNS(SVG_NS, 'text');
    label.setAttribute('x', String(s.lx));
    label.setAttribute('y', String(s.ly));
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('fill', '#ffffff');
    label.setAttribute('font-size', reg.isDeep ? '9.5' : '11');
    label.setAttribute('font-weight', '700');
    label.textContent = reg.arName.split(' ')[0] + (reg.arName.split(' ')[1] ? ' ' + reg.arName.split(' ')[1] : '');

    g.appendChild(title);
    g.appendChild(path);
    g.appendChild(label);

    const activate = () => onSelect(s.id);
    g.addEventListener('click', activate);
    g.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activate();
      }
    });

    svg.appendChild(g);
    pathMap.set(s.id, { g, path, reg });
  });

  mount.appendChild(svg);

  return {
    selectRegion(id) {
      pathMap.forEach(({ g, path, reg }, key) => {
        const on = key === id;
        g.classList.toggle('is-selected', on);
        path.setAttribute('fill-opacity', on ? '0.96' : (reg.isDeep ? '0.82' : '0.38'));
        path.setAttribute('stroke-width', on ? '2.6' : '1.3');
      });
    },
  };
}
