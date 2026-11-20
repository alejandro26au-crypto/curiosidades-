// ===== story.js: LOS PLANOS DE ESTE VÍDEO (se reescribe en cada vídeo) =====
// Todo va atado a la voz: tiempos.js (lo escribe tiempos_es.py) da cada FRASE y cada PALABRA con su fotograma (30 fps).
// Usa en('palabra') para el fotograma exacto de una palabra; así, si cambia la voz, los golpes se mueven solos.
// Técnicas que trae (vienen del vídeo del submarino):
//   · luces por plano (LIGHTS + lightFor: día, tarde, noche, interior, alarma roja, oscuro, gas) y cambios a mitad de plano
//   · cámaras con camFromKeys (deslizan y nunca se congelan) + KICKS (golpe de cámara en palabras fuertes)
//   · ZOOMS: zoom de golpe en cifras y remates (entra en 3 fotogramas y vuelve suave)
//   · barrido rápido entre planos (sale hacia un lado y el plano nuevo entra desde el otro); corte seco con barrido: false
//   · SACUDIDAS: temblor continuo (alarmas, explosiones) · FLASHES: destello blanco
//   · personajes con idle() siempre, caras fijas que cambian en la palabra clave, impulso (pop), asentir (nod),
//     negar (shake) y 4-5 cambios de brazos con brazosEn (impulso y asiento)
//   · efectos 2D (FX): vapor, burbujas, chorro, onda, explosión aditiva, palabra que salta, objeto en el suelo + los del kit
// ENCUADRE (regla del usuario): personajes pequeños o lejos para que se vea el entorno (plano medio-general: el personaje
// ocupa ~1/3-1/2 de la altura). Caras a pantalla completa solo 1-2 veces y breves. Nada en pantalla que no diga el guion.
import { M, clamp, lerp, lerp3, ramp, camFromKeys, idle, blinkAt, q } from './motion.js';
import { brazosEn } from './gestos.js';
import { FRASES, PAL, DURACION } from './tiempos.js';
export const FPS = 30, TOTAL = DURACION;

// ---------- palabras → fotogramas ----------
const norm = (w) => w.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ]/g, '');
/** fotograma en que empieza la palabra (n = 1ª, 2ª… vez que aparece) */
export const en = (w, n = 1) => { let k = 0; for (const [p, f0] of PAL) if (norm(p) === norm(w) && ++k === n) return f0; throw new Error('palabra no está en tiempos.js: ' + w); };

// ---------- planos ----------
// id, a-b (fotogramas), light (preset de LIGHTS), barrido (false = corte seco)
export const SHOTS = [
  { id: 'plaza', a: 0, b: 84, light: 'dia' },        // plano general: el pueblo entero y los tres pequeños junto al pozo
  { id: 'apuesta', a: 85, b: 159, light: 'dia' },    // plano medio-general: la apuesta
  { id: 'tarde', a: 160, b: TOTAL - 1, light: 'tarde' }, // luz de atardecer
];
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];

// ---------- luces (una por plano; lightFor puede cambiarlas a mitad) ----------
const DIA = { az: 140, el: 46, sky: '#c4d6f2', ground: '#8a8262', hemi: 1.15, sun: '#fff1dc', sunI: 2.5, fog: '#cadcf0', fogNear: 70, fogFar: 900,
  skyTop: '#3f80d4', skyHor: '#c3daf2', sat: 1.1, vig: 0.2, shadowExt: 18, tint: '#ffffff', lampI: 0 };
const IN = { az: 80, el: 72, sky: '#fff0d8', ground: '#6a5848', hemi: 1.0, sun: '#ffe6c0', sunI: 1.5, fog: '#3a3028', fogNear: 30, fogFar: 90,
  skyTop: '#000', skyHor: '#000', sat: 1.12, lampC: '#ffcf8a', lampI: 7, bulb: '#fff0c0', vig: 0.3, shadowExt: 9, tint: '#ffffff' };
export const LIGHTS = {
  dia: DIA,
  tarde: { ...DIA, az: 8, el: 9, sky: '#9a90c8', ground: '#6a4c40', hemi: 1.0, sun: '#ffb46c', sunI: 2.9, fog: '#f0b88c', fogNear: 60, fogFar: 760,
    skyTop: '#6f6eb0', skyHor: '#ffc27e', sunDisc: '#fff0c8', sunSize: 0.0035, sat: 1.12, gain: '#fff2e2', vig: 0.26, tint: '#ffe2c8' },
  noche: { ...DIA, az: 200, el: 35, sky: '#4a5a9a', ground: '#141826', hemi: 0.75, sun: '#9fb4ff', sunI: 0.9, fog: '#141a30', fogNear: 30, fogFar: 400,
    skyTop: '#0a1030', skyHor: '#26305a', sat: 1.0, gain: '#d8e0ff', lift: '#04060e', vig: 0.45, tint: '#b8c4ee', lampC: '#ffcf8a', lampI: 9 },
  interior: IN,
  alarma: { ...IN, sky: '#ff9a8a', ground: '#3a1418', hemi: 0.95, sun: '#ff6a52', sunI: 1.5, lampC: '#ff4a38', lampI: 8, bulb: '#ff7a64', gain: '#ffe4dc', vig: 0.45, tint: '#ffd2c8', fog: '#2a0a0e' },
  oscuro: { ...IN, sky: '#5a6cc8', ground: '#160a1c', hemi: 0.62, sun: '#ff3a2e', sunI: 0.9, lampC: '#ff2a1a', lampI: 2.6, bulb: '#2a2022', gain: '#d8dcff', lift: '#06040e', vig: 0.6, tint: '#aeb0e6', fog: '#06040e' },
  gas: { ...IN, sky: '#d6f2a8', ground: '#3a4a20', sun: '#e2ff9a', sunI: 1.3, lampC: '#d8f080', fog: '#9fc46a', fogNear: 1.5, fogFar: 14, gain: '#f0ffe0', vig: 0.42, tint: '#eaffd4' },
};
export const lightFor = (S, f) => {
  const L = { ...LIGHTS[S.light] };
  // ejemplos de cambio a mitad de plano: «silencio» → el farol se enciende y baja el sol
  if (S.id === 'tarde' && f >= en('silencio')) { const t = M.smooth(ramp(f, en('silencio'), en('silencio') + 10)); L.lampI = 6 * t; L.sunI = lerp(2.9, 2.2, t); }
  // parpadeo de alarma: if (S.light === 'alarma') L.lampI *= 0.75 + 0.25 * Math.abs(Math.sin(f * 0.3));
  return L;
};

// ---------- posiciones ----------
const POZO = [1.6, 0, -3.2];
const S_ = 0.85; // escala de los personajes (≈ 1,7 m)

// ---------- cámaras ----------
// { f, pos, look, fov, roll?, ease? ('smooth' | 'easeOut' | 'easeIn' | 'back'), path? } — entre claves desliza; parada = se acerca despacio
const CAMS = {
  plaza: [{ f: 0, pos: [-1.2, 1.75, 6.6], look: [0.5, 1.45, -3.0], fov: 46 }, { f: 84, pos: [-0.8, 1.7, 5.9], look: [0.5, 1.4, -3.0], fov: 45 }],
  apuesta: [{ f: 85, pos: [2.2, 1.35, 4.4], look: [0.0, 1.2, -1.7], fov: 44 }, { f: 159, pos: [1.9, 1.33, 3.9], look: [0.0, 1.2, -1.7], fov: 42 }],
  tarde: [{ f: 160, pos: [-1.8, 1.4, 4.4], look: [0.2, 1.3, -2.0], fov: 44 }, { f: TOTAL - 1, pos: [-1.5, 1.38, 3.9], look: [0.2, 1.3, -2.0], fov: 42 }],
};
const KICKS = [{ f: en('diez'), a: 0.03 }, { f: en('cien'), a: 0.05 }, { f: en('rio'), a: 0.02 }];          // golpes de cámara
const ZOOMS = [[en('diez'), 0.14], [en('cien'), 0.18]];                                                       // zoom de golpe [fotograma, fuerza]
const SACUDIDAS = [];                     // temblor continuo: { a, b, amp } (alarma 0.06 → 0.012; explosión 0.12)
const FLASHES = [];                       // destello blanco: { f, a, d } (fotograma, fuerza 0-1, duración)
export const camAt = (f) => {
  const S = shotAt(f);
  const c = camFromKeys(CAMS[S.id], f, { creep: 0.0008, kicks: KICKS });
  // zoom de golpe: entra en 3 fotogramas y vuelve suave en 13
  for (const [z, k] of ZOOMS) { const d = f - (z - 2); if (d >= 0 && d < 16) c.fov *= 1 - k * (d < 3 ? M.easeOut(d / 3) : 1 - M.smooth((d - 3) / 13)); }
  // barrido rápido entre planos (4 fotogramas a cada lado del corte)
  { const i = SHOTS.indexOf(S), next = SHOTS[i + 1], de = S.b - f, ds = f - S.a, A = 0.5; let w = 0;
    if (de < 4 && next && next.barrido !== false && S.barrido !== false) w = Math.pow((4 - de) / 4, 2) * A;
    else if (ds < 4 && i > 0 && S.barrido !== false) w = -Math.pow((4 - ds) / 4, 2) * A;
    if (w) { const dx = c.look[0] - c.pos[0], dz = c.look[2] - c.pos[2], L = Math.hypot(dx, dz) || 1, D = Math.hypot(dx, c.look[1] - c.pos[1], dz);
      c.look = [c.look[0] - dz / L * w * D, c.look[1], c.look[2] + dx / L * w * D]; c.roll = (c.roll || 0) + w * 10; } }
  // temblor continuo
  for (const s of SACUDIDAS) if (f >= s.a && f <= s.b) { const k = s.amp; c.look = [c.look[0] + k * Math.sin(f * 2.1), c.look[1] + k * Math.sin(f * 2.7 + 1), c.look[2]]; c.roll = (c.roll || 0) + k * 30 * Math.sin(f * 1.9); }
  c.flash = 0; for (const x of FLASHES) if (f >= x.f && f < x.f + (x.d || 4)) c.flash = x.a * (1 - (f - x.f) / (x.d || 4));
  return c;
};

// ---------- lente (desenfoque) ----------
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
export const dofAt = (f) => {
  const S = shotAt(f), C = camAt(f);
  if (S.id === 'plaza') return { focus: dist(C.pos, [0, 1.2, -2]), cinf: 4 };     // plano general: casi todo nítido
  return { focus: dist(C.pos, C.look), cinf: 9 };                                  // plano medio: fondo suave como los romanos
};

// ---------- estado del decorado (lo lee worldState de _world.js) ----------
export const worldAt = (f) => {
  const S = shotAt(f), W = { bucket: 0 };
  if (S.id === 'plaza') W.bucket = M.back(ramp(f, en('diez'), en('diez') + 14)) * 0.6;  // el cubo baja en «¡Diez metros!»
  return W;
};

// ---------- personajes ----------
const R = (T, who, o, pos, extra = {}) => ({ key: who + JSON.stringify(o), draw: (p) => T.romanFront(p, who, o), x: pos[0], y: pos[1], z: pos[2], s: S_, ...extra });
/** vida: respira, se mece y parpadea (en TODOS los personajes en pantalla) */
const life = (f, seed, o = {}) => { const i = idle(f, seed); return { bob: q(i.bob, 3), tilt: q(i.tilt, 1), headTilt: q(i.headTilt + (o.headTilt || 0), 1), seed, blink: blinkAt(f, seed), ...o }; };
/** salto con impulso en un momento clave */
const pop = (f, f0, a = 0.04) => (f >= f0 && f < f0 + 8 ? q(a * Math.sin((f - f0) / 8 * Math.PI), 3) : 0);
/** asentir en palabras fuertes */
const nod = (f, fs) => { let t = 0; for (const g of fs) { const d = f - g; if (d >= -2 && d < 10) t += -6 * Math.sin(((d + 2) / 12) * Math.PI); } return t; };
/** negar con la cabeza */
const shake = (f, f0, f1) => (f >= f0 && f <= f1 ? q(7 * Math.sin((f - f0) / (f1 - f0) * Math.PI * 4), 1) : 0);
// Poses de brazos: hang, point, up, wave, hip, belly, temple, lift, reach, cheek, cross, thumb, open, beat,
//   hold (sujeta algo; con match: 1 = cerilla encendida, -1 = humo), shh (silencio, dedo en la boca), mouth (tapa la boca), cheer (celebra).
// Extras de cara: sweat (gotas, n) + sweatT, puff (mejillas hinchadas), look (-1..1), expr (neutral, smile, grin, laugh, shock, nervous,
//   pained, stern, stubborn, squint, snore, cejas, hold, relief, dazed…).

export const actorsAt = (f, T) => {
  const S = shotAt(f), out = [], tint = LIGHTS[S.light].tint;
  const A = (who, o, pos, extra = {}) => out.push(R(T, who, o, pos, { tint, ...extra }));
  switch (S.id) {
    case 'plaza': {
      const arms = brazosEn(f, [{ f: en('pozo'), R: 'point' }, { f: en('diez'), L: 'up' }]);
      A('vecino', life(f, 3, { expr: f < en('diez') ? 'cejas' : 'shock', look: 0.4, ...arms, bob: pop(f, en('diez')) }), [-0.9, 0, -1.4]);
      A('chico', life(f, 7, { expr: f < en('diez') ? 'smile' : 'shock', look: 0.6 }), [0.1, 0, -0.6]);
      A('jefe', life(f, 9, { expr: 'stern', L: 'hip', R: 'hip', look: -0.3, headTilt: nod(f, [en('metros')]) }), [-0.25, 0, -4.4]);
      break;
    }
    case 'apuesta': {
      const arms = brazosEn(f, [{ f: en('vecino'), R: 'thumb' }, { f: en('apostó'), R: 'beat' }, { f: en('cien'), L: 'cheer', R: 'cheer' }]);
      A('vecino', life(f, 3, { expr: f < en('cien') ? 'grin' : 'laugh', look: 0.5, ...arms, bob: pop(f, en('cien'), 0.05) }), [-0.9, 0, -1.6]);
      A('chico', life(f, 7, { expr: f < en('cien') ? 'cejas' : 'shock', L: f < en('cien') ? 'hang' : 'mouth', sweat: f < en('cien') ? 0 : 2, sweatT: q((f % 60) / 60, 2), look: -0.6 }), [0.3, 0, -1.1]);
      A('jefe', life(f, 9, { expr: 'stubborn', L: 'cross', R: 'cross', look: -0.5, headTilt: shake(f, en('monedas'), en('monedas') + 20) }), [-1.6, 0, -4.3]);
      break;
    }
    case 'tarde': {
      const laugh = f < en('silencio');
      const lb = q(Math.abs(Math.sin(f * 0.55)) * 0.025, 3);
      A('chico', life(f, 7, laugh ? { expr: 'laugh', L: 'belly', R: 'belly', look: 0.3, bob: lb, tilt: q(5 * Math.sin(f * 0.55), 1) } : { expr: 'squint', look: 0.4 }), [-0.7, 0, -1.0]);
      const arms = brazosEn(f, [{ f: en('silencio'), R: 'shh' }]);
      A('abuela', life(f, 13, { expr: laugh ? 'stern' : 'squint', look: -0.5, ...arms, puff: !laugh }), [0.5, 0, -1.3]);
      break;
    }
  }
  return out;
};

// ---------- efectos 2D ----------
// FX(clave, dibujo, centro [x,y,z], tamaño en m, extras). Extras útiles: noInk, add (aditivo), alpha, tint, roll, order.
const FX = (key, draw, c, size, extra = {}) => { const s = size / 2.25; return { key, draw, x: c[0], y: c[1] - 1.069 * s, z: c[2], s, blob: false, shadow: false, order: 5, ...extra }; };
// biblioteca (lienzo 600x1000, centro 300,500). Del kit además: T.fxPuff, T.fxBurst, T.fxDust, T.fxLeaf, T.fxZ, T.fxCreak, T.fxSplash, T.fxDrip, T.fxCloud
const steam = (p, t) => { for (let i = 0; i < 4; i++) { const pts = []; const x0 = 140 + i * 100, k = (t + i * 0.25) % 1; for (let j = 0; j < 12; j++) pts.push([x0 + Math.sin(j * 0.8 + k * 6) * 18, 760 - j * 34 - k * 120]); const g = p.g; g.save(); g.globalAlpha = Math.sin(k * Math.PI); p.stroke(pts, 10, '#ffffff'); g.restore(); } };
const bubbles = (p, t, n = 14, seed = 1) => { for (let i = 0; i < n; i++) { const k = (t + i / n) % 1, x = 300 + Math.sin(i * 2.3 + seed) * 200 + Math.sin(k * 8 + i) * 20, y = 950 - k * 900, r = 8 + (i % 4) * 7; p.ell(x, y, r, r, 'rgba(220,245,255,.55)', 3); p.dot(x - r * 0.35, y - r * 0.35, r * 0.25, '#ffffff'); } };
const spray = (p, t) => { for (let i = 0; i < 22; i++) { const k = ((t + i / 22) % 1), sx = (i % 2 ? 1 : -1) * (40 + (i * 37) % 140), x = 300 + sx * k * 1.6, y = 800 - Math.sin(k * Math.PI) * 520 + k * 120, r = 12 + (i % 3) * 5; p.ell(x, y, r, r * 1.4, '#9fd8ff', 4); } p.poly([[270, 800], [330, 800], [360, 420], [240, 420]], 'rgba(160,220,255,.75)', 5); };
const ping = (p, t, col = '140,255,200') => { const g = p.g; for (let k = 0; k < 3; k++) { const u = t - k * 0.18; if (u <= 0 || u >= 1) continue; g.beginPath(); g.arc(300, 500, 40 + 260 * u, 0, Math.PI * 2); g.strokeStyle = `rgba(${col},${(1 - u).toFixed(2)})`; g.lineWidth = 16 * (1 - u) + 3; g.stroke(); } };
const blast = (p, t) => { const g = p.g, r = 80 + 220 * M.easeOut(t), gr = g.createRadialGradient(300, 500, 0, 300, 500, r); gr.addColorStop(0, `rgba(255,255,240,${(1 - t).toFixed(2)})`); gr.addColorStop(0.6, `rgba(255,220,150,${(0.7 * (1 - t)).toFixed(2)})`); gr.addColorStop(1, 'rgba(255,180,90,0)'); g.fillStyle = gr; g.beginPath(); g.arc(300, 500, r, 0, 7); g.fill(); };
const word = (p, txt, col, t) => { const g = p.g; g.save(); g.translate(300, 500); const s = 0.6 + 0.4 * M.back(clamp(t * 3)); g.scale(s, s); g.rotate(-0.12); g.font = '900 150px Arial Black, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round'; g.lineWidth = 34; g.strokeStyle = '#241726'; g.strokeText(txt, 0, 0); g.fillStyle = col; g.fillText(txt, 0, 0); g.restore(); };
const coin = (p) => { p.ell(300, 500, 110, 110, '#e8c45a', 8); p.ell(300, 500, 80, 80, '#f2d27a', 4); p.ell(270, 470, 22, 14, '#fff6d0', 0); }; // objeto suelto (como el gorro en el suelo del submarino)

export const fxAt = (f, T) => {
  const S = shotAt(f), out = [];
  if (S.id === 'apuesta' && f >= en('cien')) { // «¡cien monedas!»: la cifra salta, estallido y monedas
    const t = clamp((f - en('cien')) / 10);
    out.push(FX('w' + q(t, 2), (p) => word(p, '¡100!', '#ffd23a', t), [-0.5, 2.25, -1.0], 1.5, { order: 6 }));
    if (f < en('cien') + 14) { const k = q((f - en('cien')) / 14, 2); out.push(FX('burst' + k, (p) => { p.g.translate(50, 250); T.fxBurst(p, k, '#fff6c8', 12, 40, 200); }, [-0.5, 2.25, -1.05], 1.8)); }
    for (let i = 0; i < 5; i++) { const k = clamp((f - en('cien') - i * 3) / 20); if (k > 0) out.push(FX('coin', coin, [-1.3 + i * 0.35, Math.max(0.08, 2.2 - 4 * k * k + 1.2 * k), -1.3 + (i % 2) * 0.3], 0.16, { roll: q(k * 9 + i, 1) })); }
  }
  if (S.id === 'tarde') { // hojas que cruzan con la brisa de la tarde
    for (let i = 0; i < 7; i++) { const t = ((f - 160) * 0.012 + i / 7) % 1, cols = ['#d9822b', '#c4452c', '#e6b13a'];
      out.push(FX('leaf' + i % 3, (p) => T.fxLeaf(p, cols[i % 3]), [-2.6 + t * 5 + Math.sin(i * 3.1) * 0.4, 2.6 - t * 2.4 + Math.sin(t * 9 + i) * 0.2, -1.0 + i * 0.25], 0.12, { roll: q(t * 8 + i, 1) })); }
  }
  // ejemplos listos para copiar:
  //   vapor: out.push(FX('steam' + t, (p) => steam(p, t), [x, y, z], 1.0, { alpha: 0.85 }));
  //   burbujas: FX('bub' + t, (p) => bubbles(p, t, 10, i), [x, y, z], 14, { noInk: true })
  //   chorro: FX('spray' + t, (p) => spray(p, t), [x, y, z], 1.6) · onda: FX('ping' + t, (p) => ping(p, t), c, 1.2, { noInk: true, add: true })
  //   explosión aditiva: FX('blast' + t, (p) => blast(p, t), c, 36, { noInk: true, add: true })
  //   gas/polvo: FX('gas' + k, (p) => T.fxDust(p, k, '#9ee06a'), c, 1.4, { alpha: 0.8, tint: '#c8ff9a' })
  return out;
};
export { steam, bubbles, spray, ping, blast, word, coin, POZO, FRASES };
