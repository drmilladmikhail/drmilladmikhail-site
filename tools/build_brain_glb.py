#!/usr/bin/env python3
"""Generate an anatomically proportioned, 15-mesh segmented binary glTF 2.0 (.glb) human brain.

Produces: brain-explorer/models/human-brain-segmented.glb
Coordinate convention (Three.js right-handed Y-up, meters scaled to ~1.8 units length):
  +X = right hemisphere, -X = left hemisphere
  +Y = superior (dorsal/top), -Y = inferior (ventral/bottom)
  +Z = anterior (frontal/rostral), -Z = posterior (occipital/caudal)

All 15 anatomical structures are exported as distinct, individually named, watertight
3D meshes with smooth vertex normals and PBR materials (zero blob: textures for strict CSP):
  Cortical lobes: frontal_lobe, parietal_lobe, temporal_lobe, occipital_lobe, prefrontal_cortex
  Deep & posterior structures: amygdala, hippocampus, hypothalamus, thalamus, basal_ganglia,
    corpus_callosum, insula, anterior_cingulate_cortex, cerebellum, brainstem
"""
from __future__ import annotations

import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_GLB = ROOT / "brain-explorer" / "models" / "human-brain-segmented.glb"


# ---------------------------------------------------------------------------
# Procedural 3D noise for realistic cortical gyri/sulci & cerebellar folia
# ---------------------------------------------------------------------------
def _hash3(ix: int, iy: int, iz: int) -> float:
    n = (ix * 374761393 + iy * 668265263 + iz * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0x7FFFFFFF) / 2147483647.0


def _fade(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def value_noise(x: float, y: float, z: float) -> float:
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = _fade(x - ix), _fade(y - iy), _fade(z - iz)
    c000 = _hash3(ix, iy, iz)
    c100 = _hash3(ix + 1, iy, iz)
    c010 = _hash3(ix, iy + 1, iz)
    c110 = _hash3(ix + 1, iy + 1, iz)
    c001 = _hash3(ix, iy, iz + 1)
    c101 = _hash3(ix + 1, iy, iz + 1)
    c011 = _hash3(ix, iy + 1, iz + 1)
    c111 = _hash3(ix + 1, iy + 1, iz + 1)
    x00 = c000 + (c100 - c000) * fx
    x10 = c010 + (c110 - c010) * fx
    x01 = c001 + (c101 - c001) * fx
    x11 = c011 + (c111 - c011) * fx
    y0 = x00 + (x10 - x00) * fy
    y1 = x01 + (x11 - x01) * fy
    return y0 + (y1 - y0) * fz


def gyri_folding(x: float, y: float, z: float) -> float:
    """Multi-octave ridged gyri/sulci cortical folding pattern."""
    n1 = value_noise(x * 7.2 + 1.3, y * 7.2 - 2.1, z * 6.8 + 0.7)
    n2 = value_noise(x * 13.5 - 4.2, y * 13.5 + 1.8, z * 12.8 - 3.1)
    r1 = 1.0 - abs(2.0 * n1 - 1.0)
    r2 = 1.0 - abs(2.0 * n2 - 1.0)
    # Sharpened sulci grooves + rounded gyri crowns
    return (r1 * r1 * 0.72 + r2 * r2 * 0.28) - 0.52


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------
class MeshBuilder:
    def __init__(self) -> None:
        self.positions: list[tuple[float, float, float]] = []
        self.indices: list[int] = []

    def add_grid(self, grid: list[list[tuple[float, float, float]]], wrap_u: bool = False) -> None:
        rows = len(grid)
        cols = len(grid[0])
        base = len(self.positions)
        for r in range(rows):
            for c in range(cols):
                self.positions.append(grid[r][c])
        max_c = cols if wrap_u else cols - 1
        for r in range(rows - 1):
            for c in range(max_c):
                cn = (c + 1) % cols
                i00 = base + r * cols + c
                i10 = base + (r + 1) * cols + c
                i11 = base + (r + 1) * cols + cn
                i01 = base + r * cols + cn
                self.indices.extend((i00, i10, i11, i00, i11, i01))

    def add_sphere(
        self,
        center: tuple[float, float, float],
        radii: tuple[float, float, float],
        rings: int = 16,
        segs: int = 24,
        deform=None,
    ) -> None:
        cx, cy, cz = center
        rx, ry, rz = radii
        grid = []
        for i in range(rings + 1):
            phi = math.pi * i / rings
            sp, cp = math.sin(phi), math.cos(phi)
            row = []
            for j in range(segs):
                theta = 2.0 * math.pi * j / segs
                ux, uy, uz = sp * math.cos(theta), cp, sp * math.sin(theta)
                px, py, pz = cx + ux * rx, cy + uy * ry, cz + uz * rz
                if deform is not None:
                    px, py, pz = deform(px, py, pz, ux, uy, uz)
                row.append((px, py, pz))
            grid.append(row)
        self.add_grid(grid, wrap_u=True)

    def add_tube(
        self,
        spine: list[tuple[float, float, float, float]],
        segs: int = 16,
        oval_y: float = 1.0,
        cap_ends: bool = True,
    ) -> None:
        """Build a smooth closed anatomical tube along a 3D spine [(x,y,z,radius), ...]."""
        n = len(spine)
        rings: list[list[tuple[float, float, float]]] = []
        for idx, (x, y, z, rad) in enumerate(spine):
            if idx == 0:
                tx, ty, tz = spine[1][0] - x, spine[1][1] - y, spine[1][2] - z
            elif idx == n - 1:
                tx, ty, tz = x - spine[idx - 1][0], y - spine[idx - 1][1], z - spine[idx - 1][2]
            else:
                tx = spine[idx + 1][0] - spine[idx - 1][0]
                ty = spine[idx + 1][1] - spine[idx - 1][1]
                tz = spine[idx + 1][2] - spine[idx - 1][2]
            tl = math.sqrt(tx * tx + ty * ty + tz * tz) or 1.0
            tx, ty, tz = tx / tl, ty / tl, tz / tl

            # Pick stable reference up vector
            upx, upy, upz = (0.0, 1.0, 0.0) if abs(ty) < 0.88 else (1.0, 0.0, 0.0)
            # side = normalize(cross(tangent, up))
            sx = ty * upz - tz * upy
            sy = tz * upx - tx * upz
            sz = tx * upy - ty * upx
            sl = math.sqrt(sx * sx + sy * sy + sz * sz) or 1.0
            sx, sy, sz = sx / sl, sy / sl, sz / sl
            # normal = cross(side, tangent)
            nx = sy * tz - sz * ty
            ny = sz * tx - sx * tz
            nz = sx * ty - sy * tx

            row = []
            for s in range(segs):
                a = 2.0 * math.pi * s / segs
                ca, sa = math.cos(a) * rad, math.sin(a) * rad * oval_y
                row.append((
                    x + sx * ca + nx * sa,
                    y + sy * ca + ny * sa,
                    z + sz * ca + nz * sa,
                ))
            rings.append(row)

        if cap_ends:
            x0, y0, z0, _ = spine[0]
            xn, yn, zn, _ = spine[-1]
            rings.insert(0, [(x0, y0, z0)] * segs)
            rings.append([(xn, yn, zn)] * segs)
        self.add_grid(rings, wrap_u=True)

    def compute_normals(self) -> list[tuple[float, float, float]]:
        nx = [0.0] * len(self.positions)
        ny = [0.0] * len(self.positions)
        nz = [0.0] * len(self.positions)
        pos = self.positions
        idx = self.indices
        for k in range(0, len(idx), 3):
            i0, i1, i2 = idx[k], idx[k + 1], idx[k + 2]
            p0, p1, p2 = pos[i0], pos[i1], pos[i2]
            ax, ay, az = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
            bx, by, bz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
            cx = ay * bz - az * by
            cy = az * bx - ax * bz
            cz = ax * by - ay * bx
            for vi in (i0, i1, i2):
                nx[vi] += cx
                ny[vi] += cy
                nz[vi] += cz
        out = []
        for i in range(len(pos)):
            l = math.sqrt(nx[i] * nx[i] + ny[i] * ny[i] + nz[i] * nz[i]) or 1.0
            out.append((nx[i] / l, ny[i] / l, nz[i] / l))
        return out


# ---------------------------------------------------------------------------
# Cortical hemisphere surface + lobe classifier
# ---------------------------------------------------------------------------
def cortex_point(side: float, ux: float, uy: float, uz: float) -> tuple[float, float, float]:
    """Map unit sphere direction (ux, uy, uz) to one anatomically shaped cerebral hemisphere."""
    # Base hemisphere ellipsoid (anterior +Z, superior +Y, lateral +X*side)
    # Flatten the medial wall cleanly along the longitudinal fissure
    lx = ux
    if side > 0 and lx < 0:
        lx *= 0.24
    elif side < 0 and lx > 0:
        lx *= 0.24

    x = side * 0.285 + lx * 0.415
    y = 0.14 + uy * 0.505
    z = uz * 0.785

    # Frontal pole tapers slightly & curves gently downward
    if z > 0.25:
        t = (z - 0.25) / 0.55
        x *= (1.0 - 0.11 * t * t)
        y -= 0.06 * t * t

    # Occipital pole tapers smoothly backward above cerebellum
    if z < -0.25:
        t = (-0.25 - z) / 0.55
        x *= (1.0 - 0.16 * t * t)
        if y < 0.05:
            y += 0.17 * t * t  # cerebellar tentorium arch

    # Temporal lobe lateral-inferior bulge
    if -0.25 < z < 0.35 and uy < 0.05 and abs(lx) > 0.35:
        tb = math.exp(-((z - 0.05) / 0.30) ** 2) * math.exp(-((uy + 0.35) / 0.35) ** 2)
        x += side * 0.085 * tb
        y -= 0.085 * tb

    # Inferior orbital flattening
    if uy < -0.55:
        y = max(y, -0.24 + 0.12 * (z + 0.3))

    # Keep medial gap (interhemispheric fissure) cleanly separated
    if side > 0:
        x = max(0.022, x)
    else:
        x = min(-0.022, x)

    # Add realistic cortical gyri/sulci folding (stronger on lateral/dorsal cortex)
    medial_fade = min(1.0, (abs(x) - 0.02) / 0.14)
    fold = gyri_folding(x, y, z) * 0.036 * max(0.25, medial_fade)
    # Central sulcus & Sylvian fissure subtle anatomical indentations
    central = math.exp(-((z - 0.04 + 0.18 * uy) / 0.055) ** 2) * max(0.0, uy) * 0.022
    sylvian = math.exp(-((y - (0.02 - 0.14 * z)) / 0.05) ** 2) * (1.0 if -0.15 < z < 0.38 else 0.0) * medial_fade * 0.026

    nl = math.sqrt(ux * ux + uy * uy + uz * uz) or 1.0
    disp = fold - central - sylvian
    return (x + (ux / nl) * disp, y + (uy / nl) * disp, z + (uz / nl) * disp)


def classify_cortex_lobe(p: tuple[float, float, float]) -> str:
    x, y, z = p
    # Prefrontal cortex: anterior frontal pole region
    if z > 0.42:
        return "prefrontal_cortex"
    # Temporal lobe: inferior-lateral middle region below Sylvian fissure
    if -0.34 < z <= 0.34 and y < (0.06 - 0.14 * z) and abs(x) > 0.24:
        return "temporal_lobe"
    # Frontal lobe: anterior to central sulcus
    if z >= (0.02 - 0.14 * y):
        return "frontal_lobe"
    # Occipital lobe: posterior pole
    if z < -0.42:
        return "occipital_lobe"
    # Parietal lobe: superior-posterior between central sulcus and parieto-occipital sulcus
    return "parietal_lobe"


def build_cortical_meshes() -> dict[str, MeshBuilder]:
    lobes = {
        "frontal_lobe": MeshBuilder(),
        "prefrontal_cortex": MeshBuilder(),
        "parietal_lobe": MeshBuilder(),
        "temporal_lobe": MeshBuilder(),
        "occipital_lobe": MeshBuilder(),
    }
    rings, segs = 40, 56
    for side in (-1.0, 1.0):
        verts = []
        for i in range(rings + 1):
            phi = math.pi * i / rings
            sp, cp = math.sin(phi), math.cos(phi)
            row = []
            for j in range(segs):
                theta = 2.0 * math.pi * j / segs
                ux, uy, uz = sp * math.cos(theta), cp, sp * math.sin(theta)
                row.append(cortex_point(side, ux, uy, uz))
            verts.append(row)

        # Assign each triangle to its anatomically classified lobe mesh
        vmaps: dict[str, dict[tuple[int, int], int]] = {k: {} for k in lobes}

        def emit_tri(lobe_key: str, a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> None:
            mb = lobes[lobe_key]
            vm = vmaps[lobe_key]
            tri_idx = []
            for rc in (a, b, c):
                if rc not in vm:
                    vm[rc] = len(mb.positions)
                    mb.positions.append(verts[rc[0]][rc[1]])
                tri_idx.append(vm[rc])
            mb.indices.extend(tri_idx)

        for r in range(rings):
            for c in range(segs):
                cn = (c + 1) % segs
                p00 = verts[r][c]
                p10 = verts[r + 1][c]
                p11 = verts[r + 1][cn]
                p01 = verts[r][cn]
                mid1 = ((p00[0] + p10[0] + p11[0]) / 3, (p00[1] + p10[1] + p11[1]) / 3, (p00[2] + p10[2] + p11[2]) / 3)
                mid2 = ((p00[0] + p11[0] + p01[0]) / 3, (p00[1] + p11[1] + p01[1]) / 3, (p00[2] + p11[2] + p01[2]) / 3)
                emit_tri(classify_cortex_lobe(mid1), (r, c), (r + 1, c), (r + 1, cn))
                emit_tri(classify_cortex_lobe(mid2), (r, c), (r + 1, cn), (r, cn))

    return lobes


# ---------------------------------------------------------------------------
# Subcortical, limbic, cerebellar, and brainstem structures
# ---------------------------------------------------------------------------
def build_all_structures() -> dict[str, MeshBuilder]:
    meshes = build_cortical_meshes()

    # 6. Amygdala (paired almond-shaped nuclei at anterior medial temporal lobe)
    amyg = MeshBuilder()
    for side in (-1.0, 1.0):
        amyg.add_sphere((side * 0.165, -0.105, 0.085), (0.062, 0.055, 0.070), rings=14, segs=20)
    meshes["amygdala"] = amyg

    # 7. Hippocampus (paired C-shaped seahorse arches curving posteriorly behind amygdala)
    hippo = MeshBuilder()
    for side in (-1.0, 1.0):
        spine = [
            (side * 0.175, -0.115,  0.030, 0.044),
            (side * 0.195, -0.105, -0.055, 0.040),
            (side * 0.180, -0.065, -0.145, 0.036),
            (side * 0.140,  0.005, -0.205, 0.030),
            (side * 0.085,  0.075, -0.175, 0.024),
            (side * 0.055,  0.115, -0.095, 0.020),
        ]
        hippo.add_tube(spine, segs=14, oval_y=0.85)
    meshes["hippocampus"] = hippo

    # 8. Thalamus (paired ovoid central relay nuclei flanking the 3rd ventricle)
    thal = MeshBuilder()
    for side in (-1.0, 1.0):
        thal.add_sphere((side * 0.088, 0.045, -0.045), (0.078, 0.088, 0.148), rings=16, segs=24)
    meshes["thalamus"] = thal

    # 9. Hypothalamus (ventral-anterior cone/funnel beneath thalamus)
    hypo = MeshBuilder()
    hypo.add_sphere((0.0, -0.065, 0.065), (0.068, 0.058, 0.075), rings=14, segs=20)
    hypo.add_tube([(0.0, -0.095, 0.085, 0.028), (0.0, -0.165, 0.105, 0.018)], segs=12)
    meshes["hypothalamus"] = hypo

    # 10. Basal Ganglia (paired caudate C-arch + lateral lentiform putamen/globus pallidus)
    bg = MeshBuilder()
    for side in (-1.0, 1.0):
        # Putamen / Globus pallidus lens
        bg.add_sphere((side * 0.215, 0.045, 0.035), (0.068, 0.095, 0.145), rings=14, segs=20)
        # Caudate nucleus C-arch
        caudate = [
            (side * 0.115, 0.125,  0.220, 0.044),
            (side * 0.125, 0.185,  0.110, 0.035),
            (side * 0.130, 0.185, -0.040, 0.028),
            (side * 0.145, 0.125, -0.180, 0.022),
            (side * 0.175, 0.025, -0.210, 0.018),
        ]
        bg.add_tube(caudate, segs=12)
    meshes["basal_ganglia"] = bg

    # 11. Corpus Callosum (midsagittal arched commissural bridge: genu, body, splenium)
    cc = MeshBuilder()
    cc_spine = [
        (0.0, 0.105,  0.295, 0.052),
        (0.0, 0.215,  0.255, 0.060),
        (0.0, 0.265,  0.110, 0.055),
        (0.0, 0.260, -0.065, 0.055),
        (0.0, 0.215, -0.225, 0.062),
        (0.0, 0.145, -0.275, 0.056),
    ]
    # Widen horizontally across the midline (X axis)
    cc_mb = MeshBuilder()
    cc_mb.add_tube(cc_spine, segs=16, oval_y=0.65)
    cc.positions = [(x * 2.35, y, z) for (x, y, z) in cc_mb.positions]
    cc.indices = cc_mb.indices
    meshes["corpus_callosum"] = cc

    # 12. Insula (paired folded triangular cortex deep inside Sylvian fissure)
    ins = MeshBuilder()
    for side in (-1.0, 1.0):
        def ins_deform(px, py, pz, ux, uy, uz):
            ripple = math.sin((pz + py) * 32.0) * 0.008
            return (px + side * ripple, py, pz)
        ins.add_sphere((side * 0.315, 0.045, 0.065), (0.048, 0.115, 0.165), rings=14, segs=20, deform=ins_deform)
    meshes["insula"] = ins

    # 13. Anterior Cingulate Cortex (paired arched belt curving over anterior corpus callosum)
    acc = MeshBuilder()
    for side in (-1.0, 1.0):
        acc_spine = [
            (side * 0.058, 0.085, 0.375, 0.036),
            (side * 0.062, 0.225, 0.355, 0.042),
            (side * 0.062, 0.335, 0.235, 0.042),
            (side * 0.060, 0.355, 0.065, 0.038),
        ]
        acc.add_tube(acc_spine, segs=14, oval_y=0.9)
    meshes["anterior_cingulate_cortex"] = acc

    # 14. Cerebellum (bilateral hemispheres + vermis with horizontal folia ridges)
    cereb = MeshBuilder()
    for side in (-1.0, 1.0):
        def folia_deform(px, py, pz, ux, uy, uz):
            folia = math.sin(py * 78.0) * 0.011
            return (px + ux * folia, py + uy * folia * 0.4, pz + uz * folia)
        cereb.add_sphere((side * 0.215, -0.295, -0.405), (0.215, 0.175, 0.205), rings=20, segs=28, deform=folia_deform)
    cereb.add_sphere((0.0, -0.295, -0.415), (0.095, 0.155, 0.175), rings=14, segs=18)
    meshes["cerebellum"] = cereb

    # 15. Brainstem (midbrain, rounded pons bulge, tapering medulla oblongata)
    stem = MeshBuilder()
    stem_spine = [
        (0.0, -0.060, -0.055, 0.095),
        (0.0, -0.175, -0.095, 0.125),  # Pons anterior bulge
        (0.0, -0.295, -0.140, 0.105),
        (0.0, -0.445, -0.175, 0.078),  # Medulla
        (0.0, -0.600, -0.200, 0.064),  # Spinal junction
    ]
    stem.add_tube(stem_spine, segs=18, oval_y=1.08)
    # Anterior pons rounded belly
    stem.add_sphere((0.0, -0.205, -0.060), (0.115, 0.095, 0.088), rings=14, segs=20)
    meshes["brainstem"] = stem

    return meshes


# ---------------------------------------------------------------------------
# Binary glTF 2.0 (.glb) writer (pure Python stdlib, zero external deps!)
# ---------------------------------------------------------------------------
MATERIALS_RGBA = {
    "frontal_lobe":              (0.45, 0.56, 0.72, 1.0),
    "prefrontal_cortex":         (0.86, 0.69, 0.36, 1.0),
    "parietal_lobe":             (0.38, 0.54, 0.68, 1.0),
    "temporal_lobe":             (0.34, 0.60, 0.66, 1.0),
    "occipital_lobe":            (0.43, 0.50, 0.72, 1.0),
    "amygdala":                  (0.92, 0.44, 0.38, 1.0),
    "hippocampus":               (0.32, 0.78, 0.72, 1.0),
    "hypothalamus":              (0.93, 0.62, 0.30, 1.0),
    "thalamus":                  (0.55, 0.68, 0.92, 1.0),
    "basal_ganglia":             (0.70, 0.55, 0.88, 1.0),
    "corpus_callosum":           (0.88, 0.84, 0.72, 1.0),
    "insula":                    (0.42, 0.74, 0.86, 1.0),
    "anterior_cingulate_cortex": (0.90, 0.74, 0.42, 1.0),
    "cerebellum":                (0.52, 0.60, 0.74, 1.0),
    "brainstem":                 (0.62, 0.67, 0.76, 1.0),
}


def write_glb(meshes: dict[str, MeshBuilder], out_path: Path) -> None:
    bin_chunks = bytearray()
    buffer_views = []
    accessors = []
    gltf_materials = []
    gltf_meshes = []
    gltf_nodes = []

    def append_bytes(data: bytes, target: int) -> int:
        # Align to 4-byte boundary per glTF 2.0 spec
        while len(bin_chunks) % 4 != 0:
            bin_chunks.append(0)
        offset = len(bin_chunks)
        bin_chunks.extend(data)
        bv_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": offset,
            "byteLength": len(data),
            "target": target,
        })
        return bv_idx

    for idx, (name, mb) in enumerate(meshes.items()):
        normals = mb.compute_normals()
        pos_bytes = bytearray()
        norm_bytes = bytearray()
        min_p = [1e9, 1e9, 1e9]
        max_p = [-1e9, -1e9, -1e9]

        for (x, y, z), (nx, ny, nz) in zip(mb.positions, normals):
            pos_bytes.extend(struct.pack("<fff", x, y, z))
            norm_bytes.extend(struct.pack("<fff", nx, ny, nz))
            min_p[0], min_p[1], min_p[2] = min(min_p[0], x), min(min_p[1], y), min(min_p[2], z)
            max_p[0], max_p[1], max_p[2] = max(max_p[0], x), max(max_p[1], y), max(max_p[2], z)

        idx_bytes = bytearray()
        for vi in mb.indices:
            idx_bytes.extend(struct.pack("<I", vi))

        bv_pos = append_bytes(bytes(pos_bytes), 34962)   # ARRAY_BUFFER
        bv_norm = append_bytes(bytes(norm_bytes), 34962) # ARRAY_BUFFER
        bv_idx = append_bytes(bytes(idx_bytes), 34963)   # ELEMENT_ARRAY_BUFFER

        acc_pos = len(accessors)
        accessors.append({
            "bufferView": bv_pos,
            "componentType": 5126,  # FLOAT
            "count": len(mb.positions),
            "type": "VEC3",
            "min": [round(v, 5) for v in min_p],
            "max": [round(v, 5) for v in max_p],
        })
        acc_norm = len(accessors)
        accessors.append({
            "bufferView": bv_norm,
            "componentType": 5126,
            "count": len(normals),
            "type": "VEC3",
        })
        acc_idx = len(accessors)
        accessors.append({
            "bufferView": bv_idx,
            "componentType": 5125,  # UNSIGNED_INT
            "count": len(mb.indices),
            "type": "SCALAR",
        })

        rgba = list(MATERIALS_RGBA.get(name, (0.55, 0.65, 0.78, 1.0)))
        gltf_materials.append({
            "name": f"mat_{name}",
            "pbrMetallicRoughness": {
                "baseColorFactor": rgba,
                "metallicFactor": 0.08,
                "roughnessFactor": 0.52,
            },
        })
        gltf_meshes.append({
            "name": name,
            "primitives": [{
                "attributes": {"POSITION": acc_pos, "NORMAL": acc_norm},
                "indices": acc_idx,
                "material": idx,
            }],
        })
        gltf_nodes.append({"name": name, "mesh": idx})

    while len(bin_chunks) % 4 != 0:
        bin_chunks.append(0)

    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "DMMA Brain Explorer Anatomical GLB Builder (CC0 Educational Model)",
        },
        "scene": 0,
        "scenes": [{"name": "HumanBrainSegmented", "nodes": list(range(len(gltf_nodes)))}],
        "nodes": gltf_nodes,
        "meshes": gltf_meshes,
        "materials": gltf_materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(bin_chunks)}],
    }

    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    while len(json_bytes) % 4 != 0:
        json_bytes += b" "

    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_chunks)
    header = struct.pack("<III", 0x46546C67, 2, total_length)  # magic 'glTF', version 2
    chunk0 = struct.pack("<II", len(json_bytes), 0x4E4F534A) + json_bytes  # 'JSON'
    chunk1 = struct.pack("<II", len(bin_chunks), 0x004E4942) + bin_chunks  # 'BIN\0'

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(header + chunk0 + chunk1)
    print(f"brain-glb: wrote {len(meshes)} meshes -> {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)")


def main() -> None:
    meshes = build_all_structures()
    write_glb(meshes, OUT_GLB)


if __name__ == "__main__":
    main()
