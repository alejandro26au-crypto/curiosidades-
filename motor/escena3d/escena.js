// Escenarios 3D low-poly con sombreado toon, sombras suaves, niebla y cielo.
// Unidades: metros. Suelo en y=0. El eje X cruza la pantalla, Z hacia la cámara.
import * as THREE from '/node_modules/three/build/three.module.js';

const W = window.ANCHO || 1080, H = window.ALTO || 1920;
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 900);
let scene, animables = [];

// ---------- utilidades ----------
const rnd = (seed) => () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
const C = (c) => new THREE.Color(c);
const grad = (() => {
  const d = new Uint8Array([90, 160, 215, 255]);
  const t = new THREE.DataTexture(d, 4, 1, THREE.RedFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t;
})();
const mat = (color, extra = {}) => new THREE.MeshToonMaterial({ color: C(color), gradientMap: grad, ...extra });
const flat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color: C(color), flatShading: true, roughness: 0.95, metalness: 0, ...extra });
function malla(geo, m, sombra = true) {
  const o = new THREE.Mesh(geo, m); o.castShadow = sombra; o.receiveShadow = true; return o;
}
function texCanvas(w, h, fn) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; fn(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const texSuave = texCanvas(128, 128, (g, w) => {
  const r = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = r; g.fillRect(0, 0, w, w);
});
const rayas = (c1, c2, n = 6, vertical = false) => texCanvas(256, 256, (g, w, h) => {
  for (let i = 0; i < n; i++) { g.fillStyle = i % 2 ? c2 : c1; vertical ? g.fillRect(i * w / n, 0, w / n + 1, h) : g.fillRect(0, i * h / n, w, h / n + 1); }
});

// ---------- paletas ----------
const HORAS = {
  dia:       { cieloA: '#4f9be6', cieloB: '#cfe9fa', hemiA: '#d9efff', hemiB: '#8f8a5c', hemi: 1.35, sol: '#fff3dc', solI: 2.6, solPos: [-8, 14, 9], niebla: '#cfe2ee', exp: 1.05 },
  atardecer: { cieloA: '#4b4588', cieloB: '#f7a46a', hemiA: '#f6c7a4', hemiB: '#5a4a6a', hemi: 1.0, sol: '#ffb070', solI: 2.4, solPos: [-14, 4, 4], niebla: '#e9a98a', exp: 1.0 },
  amanecer:  { cieloA: '#6d93d4', cieloB: '#fcd4a8', hemiA: '#ffe2c8', hemiB: '#7d7a6a', hemi: 1.1, sol: '#ffd1a0', solI: 2.2, solPos: [12, 5, 6], niebla: '#f0d2b8', exp: 1.0 },
  noche:     { cieloA: '#0b0f2e', cieloB: '#3b3f86', hemiA: '#5a64b8', hemiB: '#1b1830', hemi: 0.75, sol: '#9fb2ff', solI: 0.9, solPos: [8, 12, 4], niebla: '#2a2d63', exp: 1.25 },
  nublado:   { cieloA: '#8794a6', cieloB: '#d6dbe2', hemiA: '#e3e8ee', hemiB: '#77756a', hemi: 1.5, sol: '#ffffff', solI: 1.0, solPos: [-6, 14, 6], niebla: '#c9ced6', exp: 1.0 },
};
const LUGARES = {
  campo:    { suelo: '#92b85a', lejos: '#6f9b5e', pasto: '#5d8d36', densidad: 1 },
  huerto:   { suelo: '#b39565', lejos: '#7aa067', pasto: '#7d9a45', densidad: 0.5 },
  playa:    { suelo: '#ecd49b', lejos: '#86ad7f', pasto: '#a9b55a', densidad: 0.12, mar: true },
  sabana:   { suelo: '#d4b061', lejos: '#b7995d', pasto: '#c69c3f', densidad: 1.1 },
  desierto: { suelo: '#e2bb80', lejos: '#c98f5f', pasto: '#a08a4a', densidad: 0.05 },
  nieve:    { suelo: '#f2f6fb', lejos: '#b5c6dc', pasto: '#dfe8f2', densidad: 0.0 },
  hielo:    { suelo: '#e1eef9', lejos: '#c3d7ec', pasto: '#c9dcee', densidad: 0.0, hielo: true },
  pueblo:   { suelo: '#c6ae86', lejos: '#7f9f78', pasto: '#839a4a', densidad: 0.3, casas: true },
  ciudad:   { suelo: '#9a948b', lejos: '#9a948b', pasto: '#777', densidad: 0, edificios: true },
  mar:      { suelo: '#3a8cc2', lejos: '#94b4c8', pasto: '#3a8cc2', densidad: 0, todoMar: true },
  interior: { suelo: '#a87a4e', lejos: '#a87a4e', pasto: '#a87a4e', densidad: 0, interior: true },
};

// ---------- cielo ----------
function cielo(h, r) {
  const g = new THREE.SphereGeometry(500, 32, 16);
  const m = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { a: { value: C(h.cieloA) }, b: { value: C(h.cieloB) } },
    vertexShader: 'varying vec3 p; void main(){ p = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader: 'uniform vec3 a;\nuniform vec3 b;\nvarying vec3 p;\nvoid main(){\nfloat k = smoothstep(-0.05, 0.55, p.y);\ngl_FragColor = vec4(mix(b, a, k), 1.0);\n#include <colorspace_fragment>\n}',
  });
  scene.add(new THREE.Mesh(g, m));
  const noche = h === HORAS.noche;
  if (noche) {
    const n = 900, pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const th = r() * Math.PI * 2, ph = 0.08 + r() * 1.3;
      pos.set([Math.cos(th) * Math.cos(ph) * 450, Math.sin(ph) * 450, Math.sin(th) * Math.cos(ph) * 450], i * 3);
    }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const pts = new THREE.Points(geo, new THREE.PointsMaterial({ size: 2.2, sizeAttenuation: false, color: 0xfffbe8, fog: false, map: texSuave, transparent: true }));
    scene.add(pts);
  }
  // sol / luna
  const disco = new THREE.Mesh(new THREE.CircleGeometry(noche ? 9 : 14, 32), new THREE.MeshBasicMaterial({ color: noche ? 0xfff6d8 : 0xfff3c8, fog: false }));
  const sp = new THREE.Vector3(...h.solPos).normalize().multiplyScalar(420);
  disco.position.copy(sp); disco.lookAt(0, 0, 0); scene.add(disco);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: texSuave, color: noche ? 0x8fa0ff : 0xffe7b0, transparent: true, opacity: 0.55, fog: false, depthWrite: false }));
  halo.position.copy(sp); halo.scale.set(110, 110, 1); scene.add(halo);
  // nubes infladas low-poly
  if (!noche) {
    for (let i = 0; i < 9; i++) {
      const g = new THREE.Group();
      const n = 4 + Math.floor(r() * 4);
      for (let k = 0; k < n; k++) {
        const s = 4 + r() * 5;
        const b = malla(new THREE.IcosahedronGeometry(s, 1), mat('#ffffff', { emissive: C('#9fb0c8'), emissiveIntensity: 0.25 }), false);
        b.position.set((k - n / 2) * 5 + r() * 2, r() * 3, r() * 3); g.add(b);
      }
      const ang = -0.9 + r() * 1.8;
      g.position.set(Math.sin(ang) * (120 + r() * 60), 30 + r() * 35, -Math.cos(ang) * (120 + r() * 80));
      g.userData.vel = 0.6 + r(); animables.push((t) => { g.position.x += 0; g.rotation.y = 0; g.position.x = g.userData.x0 + t * g.userData.vel; });
      g.userData.x0 = g.position.x; scene.add(g);
    }
  }
}

// ---------- terreno ----------
function ruido(x, z) { return Math.sin(x * 0.11 + Math.sin(z * 0.07)) * Math.cos(z * 0.09 - x * 0.03) + 0.5 * Math.sin(x * 0.27 + z * 0.21); }
function terreno(L, r) {
  const g = new THREE.PlaneGeometry(600, 600, 150, 150); g.rotateX(-Math.PI / 2);
  const p = g.attributes.position, col = [];
  const base = C(L.suelo), lej = C(L.lejos);
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), z = p.getZ(i);
    const d = Math.hypot(x * 0.8, Math.min(0, z + 8));
    let y = 0;
    if (!L.todoMar && !L.interior) {
      y = Math.max(0, d - 22) * 0.06 * (1 + ruido(x, z)) * (L.hielo ? 0.5 : 1);
      y += Math.max(0, d - 70) * 0.18 * (0.6 + 0.4 * ruido(x * 0.5, z * 0.5));
      y += (r() - 0.5) * 0.06;
    }
    p.setY(i, y);
    const k = Math.min(1, Math.max(0, (d - 18) / 50));
    const c = base.clone().lerp(lej, k).offsetHSL(0, 0, (r() - 0.5) * 0.04);
    col.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.computeVertexNormals();
  const m = new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: 1 });
  const suelo = new THREE.Mesh(g, m); suelo.receiveShadow = true; scene.add(suelo);
}
function pasto(L, r) {
  const n = Math.floor(14000 * L.densidad); if (!n) return;
  const blade = new THREE.ConeGeometry(0.022, 0.17, 3); blade.translate(0, 0.085, 0);
  const im = new THREE.InstancedMesh(blade, new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true, roughness: 1 }), n);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), v = new THREE.Vector3(), c = C(L.pasto);
  for (let i = 0; i < n; i++) {
    const cx = (r() - 0.5) * 46, cz = 6 - Math.pow(r(), 0.8) * 40; const x = cx, z = cz;
    e.set((r() - 0.5) * 0.5, r() * 6, (r() - 0.5) * 0.5); q.setFromEuler(e);
    const k = 0.6 + r() * 0.9; s.set(k, k * (0.7 + r() * 0.9), k);
    m4.compose(v.set(x, 0, z), q, s); im.setMatrixAt(i, m4);
    im.setColorAt(i, c.clone().offsetHSL((r() - 0.5) * 0.04, 0, (r() - 0.5) * 0.12));
  }
  im.receiveShadow = true; scene.add(im);
  // piedritas
  for (let i = 0; i < 40 * Math.max(0.3, L.densidad); i++) {
    const p = malla(new THREE.DodecahedronGeometry(0.06 + r() * 0.12, 0), flat('#8f8c86'));
    p.position.set((r() - 0.5) * 30, 0.02, 6 - r() * 30); p.scale.y = 0.6; scene.add(p);
  }
}
function mar(y0, zIni, r) {
  const g = new THREE.PlaneGeometry(800, 400, 80, 40); g.rotateX(-Math.PI / 2);
  const m = new THREE.MeshStandardMaterial({ color: C('#2f8fcf'), flatShading: true, roughness: 0.35, metalness: 0.05 });
  const o = new THREE.Mesh(g, m); o.position.set(0, y0, zIni - 200); o.receiveShadow = true; scene.add(o);
  const p = g.attributes.position, base = p.array.slice();
  animables.push((t) => {
    for (let i = 0; i < p.count; i++) p.setY(i, base[i * 3 + 1] + 0.12 * Math.sin(base[i * 3] * 0.3 + t * 1.6) * Math.cos(base[i * 3 + 2] * 0.25 + t));
    p.needsUpdate = true; g.computeVertexNormals();
  });
  // espuma de orilla
  const esp = malla(new THREE.BoxGeometry(800, 0.04, 0.6), flat('#f4fbff'), false);
  esp.position.set(0, y0 + 0.03, zIni); scene.add(esp);
  animables.push((t) => { esp.position.z = zIni + 0.4 * Math.sin(t * 1.3); });
  return o;
}

// ---------- props ----------
function humo(g, x, y, z, gris = 0.85, n = 8, alto = 6) {
  const sprites = [];
  for (let i = 0; i < n; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: texSuave, color: new THREE.Color(gris, gris, gris + 0.04), transparent: true, depthWrite: false }));
    g.add(s); sprites.push(s);
  }
  animables.push((t) => sprites.forEach((s, i) => {
    const k = (t * 0.18 + i / n) % 1;
    s.position.set(x + Math.sin(i * 1.7 + t * 0.5) * 0.3 + k * 1.2, y + k * alto, z);
    const sc = 0.6 + k * 2.4; s.scale.set(sc, sc, 1); s.material.opacity = 0.75 * (1 - k);
  }));
}
function copa(g, y, r, color, n = 5, radio = 0.9) {
  for (let i = 0; i < n; i++) {
    const s = radio * (0.7 + r() * 0.5);
    const b = malla(new THREE.IcosahedronGeometry(s, 1), mat(color));
    b.position.set((r() - 0.5) * radio * 1.6, y + (r() - 0.3) * radio, (r() - 0.5) * radio * 1.2);
    g.add(b);
  }
}
const PROPS = {
  arbol(g, p, r) {
    const tc = p.pintado ? '#f1f0ea' : (p.color_tronco || '#7a5236');
    const tr = malla(new THREE.CylinderGeometry(0.13, 0.2, 2.0, 7), mat(tc)); tr.position.y = 1.0; g.add(tr);
    if (p.pintado) { const top = malla(new THREE.CylinderGeometry(0.125, 0.13, 0.7, 7), mat('#7a5236')); top.position.y = 1.85; g.add(top); }
    copa(g, 2.6, r, p.color || '#6aa344', 6, 1.0);
  },
  arbol_fruta(g, p, r) {
    PROPS.arbol(g, { ...p, color: p.color || '#5f9a3e' }, r);
    for (let i = 0; i < 22; i++) {
      const a = r() * Math.PI * 2, b = r() * 1.2;
      const f = malla(new THREE.SphereGeometry(0.11, 10, 8), mat(p.fruta || '#f28c28', { emissive: C(p.fruta || '#f28c28'), emissiveIntensity: 0.12 }));
      f.position.set(Math.cos(a) * 1.25 * Math.cos(b - 0.5), 2.6 + Math.sin(b - 0.5) * 1.1, Math.sin(a) * 1.0); g.add(f);
      if (p.hielo) {
        const h = new THREE.Mesh(new THREE.IcosahedronGeometry(0.17, 1), new THREE.MeshStandardMaterial({ color: 0xdff4ff, transparent: true, opacity: 0.55, roughness: 0.1, flatShading: true }));
        h.position.copy(f.position); g.add(h);
      }
    }
  },
  pino(g, p, r) {
    const tr = malla(new THREE.CylinderGeometry(0.12, 0.16, 1, 6), mat('#6b4a30')); tr.position.y = 0.5; g.add(tr);
    for (let k = 0; k < 3; k++) { const c = malla(new THREE.ConeGeometry(1.2 - k * 0.3, 1.6, 7), mat(p.color || '#3f7a4f')); c.position.y = 1.4 + k * 0.9; g.add(c); }
  },
  arbusto(g, p, r) { copa(g, 0.45, r, p.color || '#5e9a45', 4, 0.55); },
  palmera(g, p, r) {
    let y = 0, x = 0;
    for (let k = 0; k < 8; k++) { const s = malla(new THREE.CylinderGeometry(0.13, 0.16, 0.6, 7), mat(k % 2 ? '#9c7a4e' : '#8a6a42')); s.position.set(x, y + 0.3, 0); s.rotation.z = -0.06 * k; g.add(s); y += 0.58; x += 0.05 * k; }
    for (let k = 0; k < 7; k++) {
      const h = malla(new THREE.ConeGeometry(0.28, 2.2, 4), mat('#4f9a52')); h.scale.z = 0.25;
      const a = k / 7 * Math.PI * 2; h.position.set(x + Math.cos(a) * 0.9, y - 0.2, Math.sin(a) * 0.9);
      h.rotation.set(Math.sin(a) * 1.2, 0, -Math.cos(a) * 1.2); g.add(h);
    }
  },
  acacia(g, p, r) {
    const tr = malla(new THREE.CylinderGeometry(0.12, 0.2, 2.6, 6), mat('#6b4a30')); tr.position.y = 1.3; tr.rotation.z = 0.12; g.add(tr);
    const c = malla(new THREE.SphereGeometry(1, 10, 6), mat('#7ba040')); c.scale.set(2.6, 0.45, 1.9); c.position.set(-0.3, 2.8, 0); g.add(c);
  },
  granero(g, p, r) {
    const cc = p.color || '#b5402f';
    const b = malla(new THREE.BoxGeometry(4.2, 3, 3.4), mat(cc)); b.position.y = 1.5; g.add(b);
    const techo = malla(new THREE.CylinderGeometry(2.6, 2.6, 3.6, 3, 1), mat('#5a3a2e')); techo.rotation.set(0, 0, Math.PI / 2); techo.rotation.y = Math.PI / 2;
    techo.scale.set(1, 1, 0.62); techo.position.y = 3.6; g.add(techo);
    const pu = malla(new THREE.BoxGeometry(1.6, 2.0, 0.08), mat('#7b2a20')); pu.position.set(0, 1.0, 1.72); g.add(pu);
    for (const s of [1, -1]) { const x = malla(new THREE.BoxGeometry(0.12, 2.5, 0.05), mat('#f4efe6')); x.position.set(0, 1.0, 1.77); x.rotation.z = s * 0.67; g.add(x); }
    if (p.vapor) humo(g, 0, 4.5, 0, 0.92);
  },
  casa(g, p, r) {
    const b = malla(new THREE.BoxGeometry(3, 2.2, 2.6), mat(p.color || '#e7d3b0')); b.position.y = 1.1; g.add(b);
    const t = malla(new THREE.ConeGeometry(2.4, 1.3, 4), mat('#b05a3c')); t.position.y = 2.85; t.rotation.y = Math.PI / 4; t.scale.set(1.05, 1, 0.9); g.add(t);
    const pu = malla(new THREE.BoxGeometry(0.7, 1.3, 0.06), mat('#7a5236')); pu.position.set(-0.6, 0.65, 1.31); g.add(pu);
    const v = malla(new THREE.BoxGeometry(0.6, 0.6, 0.06), mat('#9cc7e6')); v.position.set(0.7, 1.3, 1.31); g.add(v);
  },
  cerca(g, p, r) {
    const largo = (p.largo || 900) / 120;
    const c = p.color || '#a07850';
    for (let x = -largo / 2; x <= largo / 2; x += 1.4) { const po = malla(new THREE.BoxGeometry(0.12, 1.1, 0.12), mat(c)); po.position.set(x, 0.55, 0); g.add(po); }
    for (const y of [0.45, 0.85]) { const t = malla(new THREE.BoxGeometry(largo, 0.1, 0.06), mat(c)); t.position.set(0, y, 0.07); g.add(t); }
  },
  fogata(g, p, r) {
    for (let k = 0; k < 4; k++) { const l = malla(new THREE.CylinderGeometry(0.09, 0.09, 1.0, 7), mat('#7a4e2e')); l.rotation.set(Math.PI / 2, k * Math.PI / 4, 0.25); l.position.y = 0.12; g.add(l); }
    for (let k = 0; k < 9; k++) { const s = malla(new THREE.DodecahedronGeometry(0.13, 0), flat('#77736c')); const a = k / 9 * Math.PI * 2; s.position.set(Math.cos(a) * 0.6, 0.06, Math.sin(a) * 0.6); g.add(s); }
    if (p.apagada) { humo(g, 0, 0.3, 0, 0.5); return; }
    const llamas = [['#ff5a1a', 0.42, 1.2], ['#ff9a1f', 0.3, 0.9], ['#ffe27a', 0.17, 0.55]].map(([c, rr, h], i) => {
      const f = new THREE.Mesh(new THREE.ConeGeometry(rr, h, 7), new THREE.MeshBasicMaterial({ color: C(c), transparent: true, opacity: 0.95 }));
      f.position.y = 0.2 + h / 2; g.add(f); return f;
    });
    const luz = new THREE.PointLight(0xff8a3c, 9, 14, 1.6); luz.position.y = 0.9; luz.castShadow = false; g.add(luz);
    animables.push((t) => { llamas.forEach((f, i) => { const k = 1 + 0.15 * Math.sin(t * 13 + i * 2); f.scale.set(1 / Math.sqrt(k), k, 1 / Math.sqrt(k)); f.rotation.y = t * (i + 1); }); luz.intensity = 9 * (1 + 0.12 * Math.sin(t * 17)); });
    humo(g, 0, 1.4, 0, 0.6, 7, 7);
  },
  roca(g, p, r) { const o = malla(new THREE.DodecahedronGeometry(0.6, 0), flat(p.color || '#8c8a86')); o.scale.set(1.3, 0.8, 1); o.position.y = 0.35; g.add(o); },
  fardos(g, p, r) {
    const filas = p.filas || 3;
    for (let f = 0; f < filas; f++) for (let c = 0; c < 3 - (f > 1 ? 1 : 0); c++) {
      const b = new THREE.Group();
      const caja = malla(new THREE.BoxGeometry(1.1, 0.55, 0.6), mat('#e6c25a')); b.add(caja);
      for (const s of [-0.25, 0.25]) { const cu = malla(new THREE.BoxGeometry(0.05, 0.57, 0.62), mat('#c0392b'), false); cu.position.x = s; b.add(cu); }
      b.position.set(-1.15 + c * 1.15 + f * 0.3, 0.28 + f * 0.56, 0); g.add(b);
    }
    if (p.humo) humo(g, 0, 1.8, 0, 0.85);
  },
  camioneta(g, p, r) {
    const cc = p.color || '#3e6fb0', hund = (p.hundida || 0) * 0.45;
    const cu = new THREE.Group(); cu.position.y = -hund; g.add(cu);
    const caja = malla(new THREE.BoxGeometry(4.4, 0.9, 1.9), mat(cc)); caja.position.y = 0.95; cu.add(caja);
    const cab = malla(new THREE.BoxGeometry(1.8, 0.9, 1.8), mat(cc)); cab.position.set(0.7, 1.85, 0); cu.add(cab);
    const vid = malla(new THREE.BoxGeometry(1.5, 0.6, 1.84), mat('#bfe0f2')); vid.position.set(0.7, 1.9, 0); cu.add(vid);
    for (const [x, z] of [[-1.4, 0.95], [1.4, 0.95], [-1.4, -0.95], [1.4, -0.95]]) {
      const ru = malla(new THREE.CylinderGeometry(0.48, 0.48, 0.38, 16), mat('#222226')); ru.rotation.x = Math.PI / 2; ru.position.set(x, 0.48, z);
      if (p.llantas_bajas) { ru.scale.set(1.12, 1, 0.82); ru.position.y = 0.4; } cu.add(ru);
      const ri = malla(new THREE.CylinderGeometry(0.2, 0.2, 0.4, 10), mat('#b8b8bc')); ri.rotation.x = Math.PI / 2; ri.position.copy(ru.position); cu.add(ri);
    }
  },
  auto(g, p, r) { PROPS.camioneta(g, p, r); },
  carreta(g, p, r) {
    const b = malla(new THREE.BoxGeometry(2.4, 0.5, 1.3), mat('#9c6b3e')); b.position.y = 0.9; g.add(b);
    for (const z of [0.7, -0.7]) { const w = malla(new THREE.TorusGeometry(0.5, 0.07, 6, 14), mat('#6b4a30')); w.position.set(0, 0.55, z); g.add(w); }
    if (p.carga === 'leña') for (let i = 0; i < 9; i++) { const l = malla(new THREE.CylinderGeometry(0.12, 0.12, 1.2, 7), mat('#b98a5a')); l.rotation.x = Math.PI / 2; l.position.set(-0.9 + (i % 5) * 0.42, 1.25 + Math.floor(i / 5) * 0.22, 0); g.add(l); }
  },
  estanque(g, p, r) {
    const o = new THREE.Mesh(new THREE.CircleGeometry(2.2, 18), new THREE.MeshStandardMaterial({ color: C('#4e8fc0'), roughness: 0.2, flatShading: true }));
    o.rotation.x = -Math.PI / 2; o.position.y = 0.03; o.scale.y = 0.6; o.receiveShadow = true; g.add(o);
  },
  barco(g, p, r) {
    const casco = malla(new THREE.CylinderGeometry(1.2, 1.2, 6, 12, 1, false, 0, Math.PI), mat(p.color || '#6b4a30'));
    casco.rotation.set(0, 0, Math.PI / 2); casco.rotation.x = Math.PI; casco.position.y = 1.1; g.add(casco);
    const m = malla(new THREE.CylinderGeometry(0.08, 0.1, 6, 6), mat('#5a3a22')); m.position.y = 4; g.add(m);
    const v = malla(new THREE.PlaneGeometry(2.4, 3.2), mat('#f4efe2', { side: THREE.DoubleSide })); v.position.set(1.2, 4.2, 0); g.add(v);
    animables.push((t) => { g.rotation.z = 0.03 * Math.sin(t * 1.4); });
  },
  lata_leche(g, p, r) {
    const b = malla(new THREE.CylinderGeometry(0.2, 0.22, 0.55, 16), mat('#c9ced6')); b.position.y = 0.28; g.add(b);
    const c = malla(new THREE.CylinderGeometry(0.12, 0.2, 0.16, 16), mat('#aeb4be')); c.position.y = 0.63; g.add(c);
    const ta = malla(new THREE.CylinderGeometry(0.13, 0.13, 0.08, 16), mat('#9aa1ab')); ta.position.y = 0.75; g.add(ta);
    if (p.vendada) {
      const v = malla(new THREE.CylinderGeometry(0.235, 0.245, 0.52, 16), mat('#efeee6', { map: rayas('#f4f3ec', '#d8d6cc', 10) })); v.position.y = 0.28; g.add(v);
      humo(g, 0, 0.7, 0, 0.98, 5, 1.6);
    }
  },
  torre_agua(g, p, r) {
    for (const [x, z] of [[-0.8, -0.8], [0.8, -0.8], [-0.8, 0.8], [0.8, 0.8]]) { const l = malla(new THREE.CylinderGeometry(0.08, 0.1, 4, 6), mat('#8a6a48')); l.position.set(x * 0.8, 2, z * 0.8); g.add(l); }
    const tk = malla(new THREE.CylinderGeometry(1.2, 1.2, 1.8, 14), mat('#b9a894')); tk.position.y = 4.9; g.add(tk);
    const tc = malla(new THREE.ConeGeometry(1.35, 0.8, 14), mat('#8c7b68')); tc.position.y = 6.2; g.add(tc);
  },
  bomba_agua(g, p, r) {
    const b = malla(new THREE.CylinderGeometry(0.14, 0.18, 1.3, 8), mat('#3c4e5e')); b.position.y = 0.65; g.add(b);
    const s = malla(new THREE.CylinderGeometry(0.06, 0.06, 0.5, 6), mat('#3c4e5e')); s.rotation.z = Math.PI / 2; s.position.set(-0.3, 0.95, 0); g.add(s);
    if (!p.sin_manija) { const m = malla(new THREE.BoxGeometry(0.8, 0.06, 0.06), mat('#222')); m.position.set(0.35, 1.25, 0); m.rotation.z = 0.35; g.add(m); }
  },
  puesto(g, p, r) {
    const m = malla(new THREE.BoxGeometry(2.4, 0.9, 1), mat('#b98a5a')); m.position.y = 0.45; g.add(m);
    for (const x of [-1.15, 1.15]) { const po = malla(new THREE.BoxGeometry(0.08, 2.2, 0.08), mat('#6b4a30')); po.position.set(x, 1.1, 0.45); g.add(po); }
    const tol = malla(new THREE.BoxGeometry(2.6, 0.08, 1.4), mat('#ffffff', { map: rayas('#e74c3c', '#ffffff', 8, true) })); tol.position.set(0, 2.2, 0.3); tol.rotation.x = 0.25; g.add(tol);
  },
  pasto_alto(g, p, r) {
    for (let i = 0; i < 120; i++) { const b = malla(new THREE.ConeGeometry(0.04, 1.2 + r(), 3), flat(p.color || '#c8a24a'), false); b.position.set((r() - 0.5) * 4, 0.6, (r() - 0.5) * 1.5); b.rotation.z = (r() - 0.5) * 0.4; g.add(b); }
  },
  vaca(g, p, r) {
    const cc = p.color || '#8b5a3c'; const s = p.mira || 1;
    const c = malla(new THREE.BoxGeometry(1.8, 0.9, 0.85), mat(cc)); c.position.y = 1.15; g.add(c);
    const ca = malla(new THREE.BoxGeometry(0.55, 0.6, 0.55), mat(cc)); ca.position.set(s * 1.05, 1.5, 0); g.add(ca);
    const ho = malla(new THREE.BoxGeometry(0.2, 0.3, 0.45), mat('#f1b6a6')); ho.position.set(s * 1.35, 1.35, 0); g.add(ho);
    for (const [x, z] of [[-0.7, 0.3], [0.7, 0.3], [-0.7, -0.3], [0.7, -0.3]]) { const l = malla(new THREE.BoxGeometry(0.18, 0.75, 0.18), mat(cc)); l.position.set(x, 0.37, z); g.add(l); }
    const mancha = malla(new THREE.BoxGeometry(0.6, 0.5, 0.87), mat('#f4f1ea')); mancha.position.set(-0.2, 1.25, 0); g.add(mancha);
    if (p.ojos_traseros) for (const z of [0.2, -0.2]) {
      const o = malla(new THREE.CircleGeometry(0.14, 16), new THREE.MeshBasicMaterial({ color: 0xffffff })); o.position.set(-s * 0.91, 1.3, z); o.rotation.y = -s * Math.PI / 2; g.add(o);
      const i2 = malla(new THREE.CircleGeometry(0.07, 16), new THREE.MeshBasicMaterial({ color: 0xe0a01a })); i2.position.set(-s * 0.915, 1.3, z); i2.rotation.y = -s * Math.PI / 2; g.add(i2);
    }
  },
  'cañon'(g, p, r) {
    const t = malla(new THREE.CylinderGeometry(0.18, 0.26, 2, 12), mat('#3a3a3e')); t.rotation.z = Math.PI / 2 - 0.1; t.position.y = 0.9; g.add(t);
    for (const z of [0.4, -0.4]) { const w = malla(new THREE.CylinderGeometry(0.45, 0.45, 0.1, 12), mat('#7a5236')); w.rotation.x = Math.PI / 2; w.position.set(-0.3, 0.45, z); g.add(w); }
  },
  muro(g, p, r) { const m = malla(new THREE.BoxGeometry((p.largo || 700) / 100, 2.2, 1.2), mat(p.color || '#b79a6a', { map: rayas('#b79a6a', '#a6885a', 12) })); m.position.y = 1.1; g.add(m); },
  bandera(g, p, r) {
    const m = malla(new THREE.CylinderGeometry(0.04, 0.05, 4.5, 6), mat('#555')); m.position.y = 2.25; g.add(m);
    const geo = new THREE.PlaneGeometry(1.6, 1, 12, 4); const f = malla(geo, mat(p.color || '#2f5da8', { side: THREE.DoubleSide })); f.position.set(0.8, 4, 0); g.add(f);
    const pa = geo.attributes.position, base = pa.array.slice();
    animables.push((t) => { for (let i = 0; i < pa.count; i++) pa.setZ(i, 0.12 * Math.sin(base[i * 3] * 3 + t * 6) * (base[i * 3] + 0.8)); pa.needsUpdate = true; });
  },
  poste(g, p, r) { const m = malla(new THREE.CylinderGeometry(0.08, 0.1, 5, 6), mat('#6b4a30')); m.position.y = 2.5; g.add(m); },
  humo(g, p, r) { humo(g, 0, 0, 0, p.gris || 0.7); },
};

// ---------- interior / ciudad / pueblo ----------
function interior() {
  const tabla = texCanvas(512, 512, (g, w, h) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#a77a4c' : '#9a6e42'; g.fillRect(i * w / 8, 0, w / 8, h); g.fillStyle = '#6e4a2c'; g.fillRect(i * w / 8, 0, 3, h); } });
  tabla.wrapS = tabla.wrapT = THREE.RepeatWrapping; tabla.repeat.set(6, 2);
  const pared = malla(new THREE.BoxGeometry(30, 8, 0.3), mat('#ffffff', { map: tabla })); pared.position.set(0, 4, -5); scene.add(pared);
  for (const x of [-7, 7]) { const l = malla(new THREE.BoxGeometry(0.3, 8, 14), mat('#ffffff', { map: tabla })); l.position.set(x, 4, 1); scene.add(l); }
  const viga = malla(new THREE.BoxGeometry(30, 0.4, 0.4), mat('#5a3a22')); viga.position.set(0, 5, -2); scene.add(viga);
}
function edificios(r) {
  for (let i = 0; i < 16; i++) {
    const w = 2.5 + r() * 2, h = 4 + r() * 6;
    const b = malla(new THREE.BoxGeometry(w, h, 3), mat(['#b5654a', '#a8836a', '#c29a6b', '#8e6e5c', '#b07b5f'][i % 5]));
    b.position.set(-22 + i * 3.1, h / 2, -12 - r() * 5); scene.add(b);
    for (let k = 0; k < Math.floor(h / 1.8); k++) for (const dx of [-0.6, 0.6]) {
      const v = malla(new THREE.BoxGeometry(0.5, 0.8, 0.05), mat(window.__noche ? '#ffd27a' : '#2b2f3a', window.__noche ? { emissive: C('#ffb84a'), emissiveIntensity: 0.6 } : {}), false);
      v.position.set(b.position.x + dx, 1.2 + k * 1.8, b.position.z + 1.53); scene.add(v);
    }
  }
}

// ---------- API ----------
window.construir = function (fondo) {
  scene = new THREE.Scene(); animables = [];
  const h = HORAS[fondo.hora] || HORAS.dia, L = LUGARES[fondo.lugar] || LUGARES.campo;
  window.__noche = fondo.hora === 'noche';
  const r = rnd((fondo.semilla || 1) * 9973 + 17);
  renderer.toneMappingExposure = h.exp;
  scene.fog = new THREE.Fog(C(h.niebla), L.interior ? 30 : 26, L.interior ? 80 : 150);
  cielo(h, r);
  scene.add(new THREE.HemisphereLight(C(h.hemiA), C(h.hemiB), h.hemi));
  const sol = new THREE.DirectionalLight(C(h.sol), h.solI);
  sol.position.set(...h.solPos); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); sol.shadow.bias = -0.0004; sol.shadow.radius = 4;
  Object.assign(sol.shadow.camera, { left: -18, right: 18, top: 18, bottom: -18, near: 1, far: 60 });
  scene.add(sol);
  if (L.interior) { interior(); }
  terreno(L, r);
  if (L.todoMar) mar(0.05, 30, r);
  pasto(L, r);
  if (L.mar) window.__mar = mar(-0.08, -9 + (fondo.mar_sube ? 0 : 0), r); else window.__mar = null;
  if (L.edificios) edificios(r);
  if (L.casas) for (let i = 0; i < 7; i++) { const g = new THREE.Group(); PROPS.casa(g, { color: ['#e7d3b0', '#d9a779', '#f0e6d2'][i % 3] }, r); g.position.set(-18 + i * 6 + r() * 2, 0, -18 - r() * 6); g.rotation.y = (r() - 0.5) * 0.4; scene.add(g); }
  // ambientación: árboles lejanos para dar profundidad
  if (!L.interior && !L.todoMar && !L.edificios) {
    const tipo = fondo.lugar === 'sabana' ? 'acacia' : fondo.lugar === 'playa' ? 'palmera' : fondo.lugar === 'nieve' ? 'pino' : 'arbol';
    if (L.densidad > 0.04 || fondo.lugar === 'nieve') for (let i = 0; i < 14; i++) {
      const g = new THREE.Group(); PROPS[tipo](g, {}, r);
      const x = (r() - 0.5) * 70; g.position.set(x, 0, -24 - r() * 30); g.scale.setScalar(0.9 + r() * 0.6); scene.add(g);
    }
  }
  for (const p of (fondo.props || [])) {
    const f = PROPS[p.tipo]; if (!f) continue;
    const g = new THREE.Group(); f(g, p, r);
    g.position.set(...p._pos); g.rotation.y = p.rot || 0; g.scale.setScalar(p._escala || 1);
    scene.add(g);
  }
  window.__marSube = fondo.mar_sube || 0;
  return true;
};

window.cuadro = function (cam, t, p) {
  camera.position.set(...cam.pos);
  camera.up.set(Math.sin(cam.roll || 0), Math.cos(cam.roll || 0), 0);
  camera.lookAt(...cam.target);
  camera.fov = cam.fov; camera.updateProjectionMatrix();
  for (const a of animables) a(t);
  if (window.__mar && window.__marSube) window.__mar.position.z = -209 + window.__marSube * 6 * p;
  renderer.render(scene, camera);
  return renderer.domElement.toDataURL('image/jpeg', 0.93);
};
window.listo = true;
