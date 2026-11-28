// DMMA Brain Explorer — Three.js 3D Segmented Human Brain Viewer (Strict CSP ES Module)
import * as THREE from '../vendor/three/three.module.min.js';
import { OrbitControls } from '../vendor/three/OrbitControls.js';
import { GLTFLoader } from '../vendor/three/GLTFLoader.js';

const CORTEX_IDS = new Set([
  'frontal_lobe',
  'prefrontal_cortex',
  'parietal_lobe',
  'temporal_lobe',
  'occipital_lobe',
]);

const CAMERA_PRESETS = {
  front: { pos: [0.0, 0.25, 2.85], target: [0, 0, 0] },
  side:  { pos: [2.85, 0.22, 0.08], target: [0, 0, 0] },
  top:   { pos: [0.0, 2.95, 0.15], target: [0, 0, 0] },
  rear:  { pos: [0.0, 0.25, -2.85], target: [0, 0, 0] },
  reset: { pos: [1.95, 0.72, 2.05], target: [0, -0.04, 0] },
};

export function createBrainViewer({ mount, regionsById, onSelect, onHover, onProgress, onReady, onError }) {
  const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let renderer, scene, camera, controls;
  const meshes = new Map();
  const baseColors = new Map();
  const explodeVecs = new Map();
  const meshCenters = new Map();

  let selectedId = null;
  let hoveredId = null;
  let xrayEnabled = false;
  let explodedEnabled = false;
  let autoRotate = !reducedMotion;
  let modeHighlightIds = new Set();
  let modeActiveId = null;
  let pathwayLine = null;
  let rafId = null;
  let disposed = false;

  const camAnim = {
    active: false,
    targetPos: new THREE.Vector3(),
    targetLook: new THREE.Vector3(),
  };

  // Detect WebGL support cleanly
  try {
    const testCanvas = document.createElement('canvas');
    const gl = testCanvas.getContext('webgl2') || testCanvas.getContext('webgl');
    if (!gl) throw new Error('WebGL not supported');
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (err) {
    if (onError) onError(err);
    return null;
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(mount.clientWidth || 640, mount.clientHeight || 460);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  mount.appendChild(renderer.domElement);

  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(
    38,
    (mount.clientWidth || 640) / (mount.clientHeight || 460),
    0.1,
    50
  );
  camera.position.set(...CAMERA_PRESETS.reset.pos);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.minDistance = 1.35;
  controls.maxDistance = 5.4;
  controls.enablePan = true;
  controls.autoRotate = autoRotate;
  controls.autoRotateSpeed = 0.65;
  controls.target.set(...CAMERA_PRESETS.reset.target);

  // Scientific Museum Lighting Rig (Navy / Gold / Neural Blue)
  const hemiLight = new THREE.HemisphereLight(0x9bd0ff, 0x101c34, 1.05);
  scene.add(hemiLight);

  const keyLight = new THREE.DirectionalLight(0xffe7bd, 1.55);
  keyLight.position.set(3.2, 4.0, 3.6);
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0x5cc2f8, 1.15);
  rimLight.position.set(-3.4, 1.8, -2.8);
  scene.add(rimLight);

  const underLight = new THREE.PointLight(0xe5b964, 0.55, 8);
  underLight.position.set(0, -2.2, 1.4);
  scene.add(underLight);

  // Subtle ambient neural starfield
  const starGeo = new THREE.BufferGeometry();
  const starCount = 140;
  const starPos = new Float32Array(starCount * 3);
  for (let i = 0; i < starCount; i++) {
    const r = 2.6 + (i % 7) * 0.48;
    const th = i * 2.39996;
    const ph = Math.acos(1 - 2 * ((i + 0.5) / starCount));
    starPos[i * 3] = r * Math.sin(ph) * Math.cos(th);
    starPos[i * 3 + 1] = r * Math.cos(ph);
    starPos[i * 3 + 2] = r * Math.sin(ph) * Math.sin(th);
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  const starMat = new THREE.PointsMaterial({ color: 0x7bc8f8, size: 0.025, transparent: true, opacity: 0.45 });
  const stars = new THREE.Points(starGeo, starMat);
  scene.add(stars);

  const brainGroup = new THREE.Group();
  scene.add(brainGroup);

  // Load segmented GLB
  const loader = new GLTFLoader();
  loader.load(
    '/brain-explorer/models/human-brain-segmented.glb',
    (gltf) => {
      if (disposed) return;
      gltf.scene.traverse((obj) => {
        if (!obj.isMesh) return;
        const id = obj.name;
        const reg = regionsById.get(id);
        const col = new THREE.Color(reg ? reg.color : '#738fb8');
        obj.material = new THREE.MeshPhysicalMaterial({
          color: col.clone(),
          roughness: CORTEX_IDS.has(id) ? 0.54 : 0.36,
          metalness: 0.06,
          clearcoat: CORTEX_IDS.has(id) ? 0.18 : 0.42,
          clearcoatRoughness: 0.38,
          transparent: true,
          opacity: 1.0,
          emissive: new THREE.Color(0x000000),
          emissiveIntensity: 0.0,
        });
        obj.userData.regionId = id;
        obj.geometry.computeBoundingBox();
        const center = new THREE.Vector3();
        obj.geometry.boundingBox.getCenter(center);

        meshes.set(id, obj);
        baseColors.set(id, col);
        meshCenters.set(id, center);
        explodeVecs.set(id, new THREE.Vector3(...(reg && reg.explodeVec ? reg.explodeVec : [0, 0, 0])));
      });
      brainGroup.add(gltf.scene);
      updateMaterials();
      if (onReady) onReady();
    },
    (xhr) => {
      if (onProgress && xhr.total) {
        onProgress(Math.round((xhr.loaded / xhr.total) * 100));
      }
    },
    (err) => {
      if (onError) onError(err);
    }
  );

  // Raycasting for hover & click/tap
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let downX = 0, downY = 0;

  function getHitRegion(clientX, clientY) {
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);

    // When X-Ray is on, prioritize deep structures so users can click right through translucent cortex!
    const targets = [];
    if (xrayEnabled) {
      meshes.forEach((m, id) => { if (!CORTEX_IDS.has(id)) targets.push(m); });
      const deepHits = raycaster.intersectObjects(targets, false);
      if (deepHits.length) return deepHits[0].object.userData.regionId;
    }
    const allTargets = Array.from(meshes.values());
    const hits = raycaster.intersectObjects(allTargets, false);
    return hits.length ? hits[0].object.userData.regionId : null;
  }

  renderer.domElement.addEventListener('pointerdown', (e) => {
    downX = e.clientX;
    downY = e.clientY;
    camAnim.active = false;
  });

  renderer.domElement.addEventListener('pointermove', (e) => {
    if (e.pointerType !== 'mouse') return;
    const hit = getHitRegion(e.clientX, e.clientY);
    if (hit !== hoveredId) {
      hoveredId = hit;
      renderer.domElement.style.cursor = hit ? 'pointer' : 'grab';
      updateMaterials();
      if (onHover) onHover(hit);
    }
  });

  renderer.domElement.addEventListener('pointerup', (e) => {
    const dist = Math.hypot(e.clientX - downX, e.clientY - downY);
    if (dist > 6) return;
    const hit = getHitRegion(e.clientX, e.clientY);
    if (hit && onSelect) {
      onSelect(hit);
    }
  });

  function updateMaterials() {
    const hasFocus = Boolean(selectedId || modeHighlightIds.size);
    meshes.forEach((mesh, id) => {
      const mat = mesh.material;
      const isCortex = CORTEX_IDS.has(id);
      const isSel = id === selectedId;
      const isHov = id === hoveredId;
      const isModeActive = id === modeActiveId;
      const isModeMember = modeHighlightIds.has(id);

      let opacity = 1.0;
      if (xrayEnabled && isCortex && !isSel && !isModeActive) {
        opacity = 0.22;
      } else if (hasFocus && !isSel && !isHov && !isModeMember && !isModeActive) {
        opacity = isCortex ? (xrayEnabled ? 0.16 : 0.58) : 0.42;
      }

      mat.opacity = opacity;
      mat.depthWrite = opacity > 0.72;

      if (isSel || isModeActive) {
        mat.emissive.setHex(0xe5b964);
        mat.emissiveIntensity = 0.62;
      } else if (isModeMember) {
        mat.emissive.setHex(0x5cc2f8);
        mat.emissiveIntensity = 0.42;
      } else if (isHov) {
        mat.emissive.setHex(0x88d2ff);
        mat.emissiveIntensity = 0.32;
      } else {
        mat.emissive.setHex(0x000000);
        mat.emissiveIntensity = 0.0;
      }
    });
  }

  function updatePathwayCurve(regionIds) {
    if (pathwayLine) {
      brainGroup.remove(pathwayLine);
      pathwayLine.geometry.dispose();
      pathwayLine.material.dispose();
      pathwayLine = null;
    }
    const pts = [];
    for (const id of regionIds) {
      const c = meshCenters.get(id);
      if (c) pts.push(c.clone());
    }
    if (pts.length < 2) return;
    const curve = new THREE.CatmullRomCurve3(pts);
    const tubeGeo = new THREE.TubeGeometry(curve, 48, 0.014, 8, false);
    const tubeMat = new THREE.MeshBasicMaterial({ color: 0xf7d68c, transparent: true, opacity: 0.85 });
    pathwayLine = new THREE.Mesh(tubeGeo, tubeMat);
    brainGroup.add(pathwayLine);
  }

  function moveCameraTo(posArr, lookArr = [0, 0, 0]) {
    camAnim.targetPos.set(...posArr);
    camAnim.targetLook.set(...lookArr);
    camAnim.active = true;
  }

  function resize() {
    if (disposed) return;
    const w = mount.clientWidth || 640;
    const h = mount.clientHeight || 460;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }
  window.addEventListener('resize', resize);

  const clock = new THREE.Clock();
  function animate() {
    if (disposed) return;
    rafId = requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    // Smooth exploded view interpolation
    meshes.forEach((mesh, id) => {
      const vec = explodeVecs.get(id);
      if (!vec) return;
      const mult = explodedEnabled ? 0.55 : 0.0;
      mesh.position.x += (vec.x * mult - mesh.position.x) * 0.1;
      mesh.position.y += (vec.y * mult - mesh.position.y) * 0.1;
      mesh.position.z += (vec.z * mult - mesh.position.z) * 0.1;
    });

    // Subtle emissive pulse on selected / active mode structure
    if (!reducedMotion) {
      const pulseId = modeActiveId || selectedId;
      if (pulseId && meshes.has(pulseId)) {
        meshes.get(pulseId).material.emissiveIntensity = 0.52 + 0.18 * Math.sin(t * 3.2);
      }
      stars.rotation.y = t * 0.025;
    }

    if (camAnim.active) {
      camera.position.lerp(camAnim.targetPos, 0.08);
      controls.target.lerp(camAnim.targetLook, 0.08);
      if (camera.position.distanceTo(camAnim.targetPos) < 0.02) {
        camAnim.active = false;
      }
    }

    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  return {
    selectRegion(id, focusCam = true) {
      selectedId = id;
      const reg = id ? regionsById.get(id) : null;
      if (reg && reg.isDeep && !xrayEnabled) {
        xrayEnabled = true;
      }
      updateMaterials();
      if (focusCam && reg && reg.camPos) {
        const center = meshCenters.get(id);
        moveCameraTo(reg.camPos, center ? [center.x * 0.4, center.y * 0.4, center.z * 0.4] : [0, 0, 0]);
      }
      return xrayEnabled;
    },
    setCameraPreset(name) {
      const p = CAMERA_PRESETS[name] || CAMERA_PRESETS.reset;
      moveCameraTo(p.pos, p.target);
    },
    setXRay(enabled) {
      xrayEnabled = Boolean(enabled);
      updateMaterials();
    },
    setExploded(enabled) {
      explodedEnabled = Boolean(enabled);
    },
    setAutoRotate(enabled) {
      autoRotate = Boolean(enabled);
      controls.autoRotate = autoRotate;
    },
    highlightMode(regionIds, activeId) {
      modeHighlightIds = new Set(regionIds || []);
      modeActiveId = activeId || null;
      if (activeId) {
        const reg = regionsById.get(activeId);
        if (reg && reg.isDeep) xrayEnabled = true;
        if (reg && reg.camPos) moveCameraTo(reg.camPos, [0, 0, 0]);
      }
      updateMaterials();
      updatePathwayCurve(regionIds || []);
      return xrayEnabled;
    },
    clearMode() {
      modeHighlightIds.clear();
      modeActiveId = null;
      updatePathwayCurve([]);
      updateMaterials();
    },
    resize,
    dispose() {
      disposed = true;
      if (rafId) cancelAnimationFrame(rafId);
      window.removeEventListener('resize', resize);
      controls.dispose();
      renderer.dispose();
    },
  };
}
