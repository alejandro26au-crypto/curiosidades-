// ===== _world.js: EL DECORADO DE ESTE VÍDEO (se construye A MEDIDA en cada vídeo) =====
// La plantilla trae un decorado de EJEMPLO hecho solo con piezas del kit (una plaza de pueblo de día): suelo de hierba,
// camino de tierra, casas de yeso con tejado, pozo de piedra, valla, barriles, cipreses, pinos, colinas, montañas y nubes.
// En un vídeo nuevo: BORRA lo que el guion no pida y CONSTRUYE lo que sí, con estas piezas y en su mismo estilo
// (texturas pintadas de paint.js, colores planos con toon(), contorno de tinta automático).
// Lo que este archivo debe dejar definido para _frame.js:
//   DECK (altura del suelo donde pisan los personajes), worldState(W, f) (lo que cambia en cada fotograma),
//   worldLight(L, f) (luces propias del decorado: bombillas, lámparas…), clouds (nubes que miran a la cámara).

// ---------- materiales (texturas pintadas del kit + las nuevas) ----------
const M = {
  plank: texM(P.planks(1), 1, 6), beam: texM(P.beam(2), 1, 2), beamDark: texM(P.beam(3, [28, 36, 30]), 1, 2),
  stone: texM(P.stone(4), 1, 1), stoneMoss: texM(P.mossy(P.stone(4), 5, 1.2), 1, 1),
  grass: texM(P.grass(6), 60, 60), dirt: texM(P.dirt(7), 4, 4), plaster: texM(P.plaster(8), 1, 1), plaster2: texM(P.plaster(18, 28), 1, 1),
  roof: texM(P.roof(9), 2, 2), marbleTop: toon({ color: '#ece2cf' }),
  trunk: toon({ color: '#6a4a32' }), cypress: toon({ color: '#3f6b36' }), pine: toon({ color: '#5c8a3c' }), bush: toon({ color: '#6c9a42' }),
  hill: toon({ color: '#7aa64c' }), hillFar: toon({ color: '#86ad60' }), mount: toon({ color: '#8fa7b8' }), snow: toon({ color: '#f4f6fa' }),
  iron: toon({ color: '#5c5a57' }), bronze: toon({ color: '#b08a4a' }), wood: toon({ color: '#7a5434' }), door: toon({ color: '#5a3a24' }),
  window: toon({ color: '#2b2430' }), red: toon({ color: '#b8282b' }), water: toon({ color: '#3f86a8' }),
};

// ---------- el decorado ----------
const DECK = 0;                                   // los personajes pisan en y = 0
const world = new THREE.Group(); scene.add(world);
const plights = [], bulbs = [];                    // luces del decorado (las enciende/apaga worldLight)

// suelo de hierba y plaza de tierra con camino
const ground = add(new THREE.PlaneGeometry(2400, 2400), M.grass, 0, 0, 0, world, { cast: false }); ground.rotation.x = -Math.PI / 2;
const plaza = add(new THREE.CircleGeometry(9, 40), M.dirt, 0, 0.01, 0, world, { cast: false }); plaza.rotation.x = -Math.PI / 2;
const road = add(uvScale(new THREE.PlaneGeometry(4.2, 80), 1, 12), M.dirt, 0, 0.012, 46, world, { cast: false }); road.rotation.x = -Math.PI / 2;
const road2 = add(uvScale(new THREE.PlaneGeometry(4.2, 70), 1, 10), M.dirt, -42, 0.011, -2, world, { cast: false }); road2.rotation.set(-Math.PI / 2, 0, Math.PI / 2);

// pozo de piedra en el centro de la plaza (prop de ejemplo: piedra + madera + cubo)
const well = new THREE.Group(); well.position.set(1.6, 0, -3.2); world.add(well);
add(new THREE.CylinderGeometry(1.0, 1.08, 0.9, 20, 1, true), M.stone, 0, 0.45, 0, well);
add(new THREE.TorusGeometry(1.02, 0.12, 8, 24), M.stone, 0, 0.9, 0, well).rotation.x = Math.PI / 2;
add(new THREE.CircleGeometry(0.95, 20), M.water, 0, 0.55, 0, well, { cast: false }).rotation.x = -Math.PI / 2;
for (const s of [-1, 1]) add(tbox(0.16, 2.0, 0.16, 1), M.beam, s * 0.95, 1.4, 0, well);
add(new THREE.CylinderGeometry(0.09, 0.09, 2.2, 8), M.wood, 0, 2.15, 0, well).rotation.z = Math.PI / 2;
const wellRoof = add(new THREE.ConeGeometry(1.5, 0.9, 4), M.roof, 0, 2.75, 0, well); wellRoof.rotation.y = Math.PI / 4; wellRoof.scale.set(1, 1, 0.7);
const bucket = add(new THREE.CylinderGeometry(0.18, 0.14, 0.3, 12), M.wood, 0, 1.5, 0, well);

// valla de madera (como la barandilla del puente de los romanos)
const fence = (x0, z0, x1, z1) => {
  const L = Math.hypot(x1 - x0, z1 - z0), a = Math.atan2(z1 - z0, x1 - x0), n = Math.max(2, Math.round(L / 2.2));
  for (let i = 0; i <= n; i++) add(tbox(0.16, 1.1, 0.16, 1), M.beam, x0 + (x1 - x0) * i / n, 0.55, z0 + (z1 - z0) * i / n, world);
  for (const y of [0.55, 1.02]) { const r = add(tbox(L, 0.12, 0.1, 2), M.beam, (x0 + x1) / 2, y, (z0 + z1) / 2, world); r.rotation.y = -a; }
};
fence(-9, 6, -3, 9); fence(3, 9, 10, 5.5);

// barriles y cajas junto a una casa
const barrel = (x, z, s = 1) => { const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s); world.add(g);
  add(new THREE.CylinderGeometry(0.36, 0.36, 0.95, 14), M.beam, 0, 0.475, 0, g);
  for (const y of [0.18, 0.77]) add(new THREE.TorusGeometry(0.37, 0.03, 6, 20), M.iron, 0, y, 0, g).rotation.x = Math.PI / 2; return g; };
barrel(-5.4, -6.6); barrel(-4.7, -6.9, 0.9); barrel(-5.0, -6.0, 0.85);
add(tbox(0.8, 0.8, 0.8, 1), M.plank, -3.6, 0.4, -7.0, world).rotation.y = 0.3;

// casas del pueblo alrededor de la plaza (+ unas cuantas lejos)
const houses = [];
const house = (x, z, w, d, h, rot, mat = M.plaster) => {
  const g = new THREE.Group(); g.position.set(x, DECK, z); g.rotation.y = rot; world.add(g);
  add(tbox(w, h, d, 2), mat, 0, h / 2, 0, g);
  const rf = add(new THREE.ConeGeometry(Math.hypot(w, d) / 2 + 0.5, 1.8, 4), M.roof, 0, h + 0.9, 0, g); rf.rotation.y = Math.PI / 4; rf.scale.set(w / Math.hypot(w, d) * 1.414, 1, d / Math.hypot(w, d) * 1.414);
  add(box(0.9, 1.8, 0.1), M.door, 0, 0.9, d / 2 + 0.03, g, { cast: false });
  for (const s of [-1, 1]) add(box(0.6, 0.7, 0.1), M.window, s * w * 0.3, h * 0.62, d / 2 + 0.03, g, { cast: false });
  houses.push(g); return g;
};
// alrededor de la plaza, con la puerta mirando al centro
const rh = P.rng(12);
[[-8, -11], [0.5, -14], [9, -11.5], [-14, -2.5], [14.5, -1.5], [-12.5, 9.5], [13, 11]].forEach(([x, z], i) =>
  house(x, z, 4.5 + rh() * 2.5, 4 + rh() * 2, 3.4 + rh() * 2.2, Math.atan2(-x, -z) + (rh() - 0.5) * 0.3, i % 2 ? M.plaster2 : M.plaster));
[[-30, -26], [26, -34], [-40, 18], [38, 22], [8, -42], [-18, -40]].forEach(([x, z], i) => house(x, z, 4 + rh() * 3, 4 + rh() * 2, 3 + rh() * 2, rh() * 3, i % 2 ? M.plaster2 : M.plaster));

// árboles (cipreses y pinos del kit), arbustos
const cypress = (x, z, h = 7, y = DECK) => { const g = new THREE.Group(); g.position.set(x, y, z); world.add(g); add(new THREE.CylinderGeometry(0.15, 0.2, 1, 6), M.trunk, 0, 0.5, 0, g); const c = add(new THREE.SphereGeometry(1, 10, 10), M.cypress, 0, 0.9 + h / 2, 0, g); c.scale.set(0.95, h / 2, 0.95); return g; };
const pine = (x, z, h = 6, y = DECK) => { const g = new THREE.Group(); g.position.set(x, y, z); world.add(g); const t = add(new THREE.CylinderGeometry(0.2, 0.3, h, 6), M.trunk, 0, h / 2, 0, g); t.rotation.z = 0.08; const c = add(new THREE.SphereGeometry(1, 12, 8), M.pine, 0.3, h + 0.3, 0, g); c.scale.set(3.2, 1.1, 3.2); return g; };
const rt = P.rng(44);
for (let i = 0; i < 70; i++) { const a = rt() * Math.PI * 2, d = 20 + rt() * 90, x = Math.cos(a) * d, z = Math.sin(a) * d; if (Math.abs(x) < 4 && z > 0) continue; (i % 3 ? cypress : pine)(x, z, 5 + rt() * 4); }
for (const [x, z] of [[-17, -12], [17.5, -9], [-3.5, -17], [5, -17.5]]) cypress(x, z, 7 + rt() * 2);
for (let i = 0; i < 24; i++) { const a = rt() * Math.PI * 2, d = 11 + rt() * 8; add(new THREE.SphereGeometry(0.7 + rt() * 0.7, 10, 8), M.bush, Math.cos(a) * d, 0.3, Math.sin(a) * d, world).scale.y = 0.7; }

// colinas y montañas lejanas (con nieve)
for (let i = 0; i < 16; i++) { const a = rt() * Math.PI * 2, d = 160 + rt() * 160; const h = add(new THREE.SphereGeometry(40 + rt() * 40, 20, 10), i % 2 ? M.hill : M.hillFar, Math.cos(a) * d, -12, Math.sin(a) * d, world, { cast: false }); h.scale.y = 0.5 + rt() * 0.3; }
for (let i = 0; i < 14; i++) { const a = rt() * Math.PI * 2, d = 520 + rt() * 200, hh = 120 + rt() * 120, r_ = 110 + rt() * 70; const g = new THREE.Group(); g.position.set(Math.cos(a) * d, -5, Math.sin(a) * d); world.add(g); add(new THREE.ConeGeometry(r_, hh, 7), M.mount, 0, hh / 2, 0, g, { cast: false }); add(new THREE.ConeGeometry(r_ * 0.3, hh * 0.3, 7), M.snow, 0, hh * 0.86, 0, g, { cast: false }); }

// nubes: carteles pintados muy lejos (sin niebla ni tinta)
const clouds = [];
{ const r = P.rng(90);
  for (let i = 0; i < 14; i++) {
    const c = document.createElement('canvas'); c.width = 600; c.height = 400; const pen = new T.Pen(c.getContext('2d')); pen.ol = 0;
    pen.g.translate(300, 200); pen.g.scale(1.4, 1.2); pen.g.translate(-300, -200); T.fxCloud(pen, i + 1);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 0.667), new THREE.MeshBasicMaterial({ map: P.tex(c), transparent: true, fog: false, depthWrite: false }));
    const a = r() * Math.PI * 2, d = 650 + r() * 250; m.position.set(Math.cos(a) * d, 120 + r() * 160, Math.sin(a) * d); m.scale.setScalar(160 + r() * 140);
    m.userData.ndSkip = true; m.renderOrder = -1; scene.add(m); clouds.push(m);
  } }

// farol con bombilla (ejemplo de luz del decorado: worldLight la enciende de noche)
const lamp = new THREE.Group(); lamp.position.set(-5.2, 0, -3.0); world.add(lamp);
add(new THREE.CylinderGeometry(0.06, 0.08, 3.2, 8), M.iron, 0, 1.6, 0, lamp);
const bulb = add(new THREE.SphereGeometry(0.16, 12, 8), new THREE.MeshBasicMaterial({ color: '#ffe9b0' }), 0, 3.3, 0, lamp, { cast: false }); bulb.userData.ndSkip = true; bulbs.push(bulb);
add(new THREE.ConeGeometry(0.3, 0.25, 6), M.iron, 0, 3.5, 0, lamp);
const pl = new THREE.PointLight('#ffd49a', 0, 9, 1.6); pl.position.set(0, 3.2, 0); lamp.add(pl); plights.push(pl);

// ---------- lo que cambia en cada fotograma (W viene de worldAt() de story.js) ----------
function worldState(W, f) {
  bucket.position.y = 1.5 - (W.bucket || 0) * 0.9;   // ejemplo: el cubo baja al pozo
  for (const c of clouds) c.quaternion.copy(camera.quaternion);
  sky.visible = W.sky !== false;
}
// luces propias del decorado (L viene de lightFor() de story.js)
function worldLight(L, f) {
  for (const l of plights) { l.color.set(L.lampC || '#ffd49a'); l.intensity = L.lampI ?? 0; }
  for (const b of bulbs) b.material.color.set(L.lampI ? (L.bulb || '#ffe9b0') : '#6a6050');
}
