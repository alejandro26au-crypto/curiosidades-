// ===== «¿Cuánto tardará GTA 6 Online?» — vídeo SIN presentador: gráficos 2D + imágenes del usuario (tal cual). =====
// renderFrame(f) dibuja el fotograma f (30 fps, 1080x1920). Todo va atado a la voz: tiempos.js (FRASES y PAL).
// Planos: uno por frase o golpe (2-3 s), entrada con barrido o golpe, Ken Burns siempre (nada quieto), cifras con insertos.
// Paleta (guiones/recursos/gta6-online/LEEME.md): 2013 = verde/negro · caos = rojo · GTA 6 y 2027 = degradado atardecer.
import { FRASES, PAL as PAL0, DURACION } from './tiempos.js';
// palabras que la voz dice pero el reconocedor escribió en cifras (catorce → 14…) llegan con f0 = 0: toman el final de la anterior
const PAL = PAL0.map((x, i) => (i > 0 && x[1] === 0 ? [x[0], PAL0[i - 1][2] ?? PAL0[i - 1][1] + 6, ...x.slice(2)] : x));

const W = 1080, H = 1920, C = document.getElementById('c'), G = C.getContext('2d');
const BUF = new OffscreenCanvas(W, H), B = BUF.getContext('2d');
const TMP = new OffscreenCanvas(W, H), T = TMP.getContext('2d');
const INK = '#1b0a26', VERDE = '#6fc24a', ROJO = '#ff2d2d', ORO = '#ffd34a', BLANCO = '#ffffff';
const ATARDECER = ['#3b5bd6', '#8e4fd0', '#e64fb4', '#ff9a5a'];

// ---------- utilidades ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ramp = (f, a, b) => clamp((f - a) / (b - a));
const easeOut = (t) => 1 - Math.pow(1 - t, 3), easeIn = (t) => t * t * t, smooth = (t) => t * t * (3 - 2 * t);
const back = (t) => { const s = 1.9; t = clamp(t); return 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); };
const lerp = (a, b, t) => a + (b - a) * t;
const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const norm = (w) => w.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ]/g, '');
const fr = (i) => FRASES[i][0];
/** fotograma de la palabra w a partir de la frase i (así no se confunden los «GTA» repetidos) */
const en = (w, i = 0) => { const a = fr(i); for (const [p, f0] of PAL) if (f0 >= a - 1 && norm(p) === norm(w)) return f0; throw new Error('palabra no está en tiempos.js: ' + w + ' (frase ' + i + ')'); };
const pop = (f, f0, d = 9) => (f < f0 ? 0 : back(ramp(f, f0, f0 + d)));   // entrada con rebote 0→1

// ---------- carga ----------
const IMG = {}, BLUR = {};
const NOMBRES = ['moto-persecucion', 'pareja-muelle', 'poster-vinetas', 'portada-collage', 'gta6-palmeras-coche', 'gta6-dos-chicos',
  'gta5-portada', 'gta-online-portada', 'logo-gta6', 'logo-gta5'];
async function cargar() {
  for (const [n, file] of [['Anton', 'anton-latin-400-normal.woff2'], ['Bebas', 'bebas-neue-latin-400-normal.woff2']]) {
    const ff = new FontFace(n, await (await fetch('fuentes/' + file)).arrayBuffer()); await ff.load(); document.fonts.add(ff);
  }
  for (const n of NOMBRES) {
    const ext = n.startsWith('logo') ? '.png' : '.jpg';
    IMG[n] = await createImageBitmap(await (await fetch('img/' + n + ext)).blob());
  }
  // fondos desenfocados y oscuros (se calculan una vez: el desenfoque por fotograma es lento)
  for (const n of ['gta5-portada', 'gta-online-portada', 'portada-collage', 'gta6-palmeras-coche']) {
    const c = new OffscreenCanvas(540, 960), g = c.getContext('2d'); g.filter = 'blur(14px) saturate(1.2)'; coverOn(g, IMG[n], 540, 960, null, 1.15, 0, 0); BLUR[n] = c;
  }
  const gn = new OffscreenCanvas(256, 256), gg = gn.getContext('2d'), d = gg.createImageData(256, 256);
  for (let i = 0; i < d.data.length; i += 4) { const v = 128 + (rnd(i) - 0.5) * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
  gg.putImageData(d, 0, 0); IMG.grano = gn;
}

// ---------- dibujo básico ----------
/** imagen (o recorte [x,y,w,h]) que cubre w x h, con zoom y desplazamiento ax, ay (-1..1) */
function coverOn(g, img, w, h, crop, zoom = 1, ax = 0, ay = 0) {
  const [sx, sy, sw, sh] = crop || [0, 0, img.width, img.height];
  const s = Math.max(w / sw, h / sh) * zoom, dw = sw * s, dh = sh * s;
  g.drawImage(img, sx, sy, sw, sh, (w - dw) / 2 + ax * (dw - w) / 2, (h - dh) / 2 + ay * (dh - h) / 2, dw, dh);
}
const cover = (img, crop, zoom, ax, ay) => coverOn(B, img, W, H, crop, zoom, ax, ay);
const fondo = (n, zoom = 1, dark = 0.45) => { B.drawImage(BLUR[n], (W - W * zoom) / 2, (H - H * zoom) / 2, W * zoom, H * zoom); velo(dark); };
const velo = (a, col = '0,0,0') => { B.fillStyle = `rgba(${col},${a})`; B.fillRect(0, 0, W, H); };
function degradado(y0, y1, a0, a1, col = '10,4,20') { const gr = B.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, `rgba(${col},${a0})`); gr.addColorStop(1, `rgba(${col},${a1})`); B.fillStyle = gr; B.fillRect(0, Math.min(y0, y1), W, Math.abs(y1 - y0)); }
function atardecer(f) { // fondo propio con los colores de GTA 6
  const gr = B.createLinearGradient(0, 0, 0, H); ATARDECER.forEach((c, i) => gr.addColorStop(i / 3, c)); B.fillStyle = gr; B.fillRect(0, 0, W, H);
  B.fillStyle = 'rgba(255,240,200,.55)'; B.beginPath(); B.arc(W / 2, H * 0.72, 230, 0, 7); B.fill();
}
/** palmeras en silueta (estilo GTA 6) que se mecen */
function palmeras(f, l) {
  B.save(); B.fillStyle = 'rgba(60,14,80,.85)'; B.strokeStyle = 'rgba(60,14,80,.85)'; B.lineCap = 'round';
  for (const [x, h, lado] of [[120, 1250, 1], [300, 1000, -1], [880, 1150, -1], [1010, 1400, 1]]) {
    const sw = Math.sin(l * 0.05 + x) * 14, tx = x + lado * 120 + sw, ty = H - h;
    B.lineWidth = 34; B.beginPath(); B.moveTo(x, H); B.quadraticCurveTo(x + lado * 20, H - h / 2, tx, ty); B.stroke();
    for (let i = 0; i < 7; i++) { const a = -Math.PI / 2 + (i - 3) * 0.55 + Math.sin(l * 0.06 + i) * 0.04, L = 230;
      B.beginPath(); B.moveTo(tx, ty); B.quadraticCurveTo(tx + Math.cos(a) * L * 0.6, ty + Math.sin(a) * L * 0.6 - 60, tx + Math.cos(a) * L, ty + Math.sin(a) * L + 70);
      B.quadraticCurveTo(tx + Math.cos(a) * L * 0.5, ty + Math.sin(a) * L * 0.5 - 10, tx, ty); B.fill(); } }
  B.restore();
}
/** viñeta de cómic (como las portadas de GTA): recorte de imagen con borde negro grueso y sombra */
function vineta(img, crop, cx, cy, w, h, rot = 0, k = 1, zoom = 1.05) {
  if (k <= 0) return; B.save(); B.translate(cx, cy); B.rotate(rot); B.scale(k, k);
  B.fillStyle = 'rgba(0,0,0,.45)'; B.fillRect(-w / 2 + 16, -h / 2 + 22, w, h);
  B.fillStyle = '#0b0710'; B.fillRect(-w / 2 - 12, -h / 2 - 12, w + 24, h + 24);
  B.beginPath(); B.rect(-w / 2, -h / 2, w, h); B.clip(); B.translate(-w / 2, -h / 2); coverOn(B, img, w, h, crop, zoom, 0, 0); B.restore();
}
/** texto grande estilo GTA (Anton, contorno oscuro grueso, sombra). fill puede ser color o 'atardecer' */
function titulo(txt, x, y, size, fill = BLANCO, k = 1, rot = 0, font = 'Anton') {
  if (k <= 0) return; B.save(); B.translate(x, y); B.rotate(rot); B.scale(k, k);
  B.font = `${size}px ${font}`; B.textAlign = 'center'; B.textBaseline = 'middle'; B.lineJoin = 'round';
  const m = B.measureText(txt), maxW = W - 90; if (m.width > maxW) { const s = maxW / m.width; B.scale(s, s); }
  B.fillStyle = 'rgba(0,0,0,.55)'; B.fillText(txt, 10, 14);
  B.lineWidth = size * 0.17; B.strokeStyle = INK; B.strokeText(txt, 0, 0);
  if (fill === 'atardecer') { const gr = B.createLinearGradient(0, -size / 2, 0, size / 2); ATARDECER.forEach((c, i) => gr.addColorStop(i / 3, c)); B.fillStyle = gr; } else B.fillStyle = fill;
  B.fillText(txt, 0, 0); B.restore();
}
/** etiqueta en caja (tipo rótulo de noticia) */
function rotulo(txt, x, y, size, bg = BLANCO, col = INK, k = 1, rot = 0) {
  if (k <= 0) return; B.save(); B.translate(x, y); B.rotate(rot); B.scale(k, k); B.font = `${size}px Anton`;
  const w = B.measureText(txt).width + size * 0.9, h = size * 1.45;
  B.fillStyle = 'rgba(0,0,0,.45)'; B.fillRect(-w / 2 + 10, -h / 2 + 12, w, h);
  B.fillStyle = bg; B.fillRect(-w / 2, -h / 2, w, h); B.lineWidth = 8; B.strokeStyle = INK; B.strokeRect(-w / 2, -h / 2, w, h);
  B.fillStyle = col; B.textAlign = 'center'; B.textBaseline = 'middle'; B.fillText(txt, 0, size * 0.04); B.restore();
}
function logo(n, cx, cy, w, k = 1, rot = 0) { if (k <= 0) return; const im = IMG[n], h = w * im.height / im.width; B.save(); B.translate(cx, cy); B.rotate(rot); B.scale(k, k); B.shadowColor = 'rgba(0,0,0,.55)'; B.shadowBlur = 30; B.shadowOffsetY = 14; B.drawImage(im, -w / 2, -h / 2, w, h); B.restore(); }
/** hoja de calendario: mes, día, año */
function calendario(mes, dia, anio, cx, cy, s, k, top = ROJO, sacude = 0) {
  if (k <= 0) return; B.save(); B.translate(cx + sacude * Math.sin(cy + dia.length * 9 + performance.now() * 0), cy); B.scale(k * s, k * s); B.rotate(-0.05);
  const w = 380, h = 420; B.fillStyle = 'rgba(0,0,0,.45)'; B.fillRect(-w / 2 + 14, -h / 2 + 18, w, h);
  B.fillStyle = '#fffaf0'; B.fillRect(-w / 2, -h / 2, w, h); B.fillStyle = top; B.fillRect(-w / 2, -h / 2, w, 120);
  B.lineWidth = 10; B.strokeStyle = INK; B.strokeRect(-w / 2, -h / 2, w, h); B.beginPath(); B.moveTo(-w / 2, -h / 2 + 120); B.lineTo(w / 2, -h / 2 + 120); B.stroke();
  for (const x of [-110, 110]) { B.fillStyle = INK; B.fillRect(x - 12, -h / 2 - 34, 24, 64); }
  B.textAlign = 'center'; B.textBaseline = 'middle'; B.fillStyle = BLANCO; B.font = '86px Anton'; B.fillText(mes, 0, -h / 2 + 64);
  B.fillStyle = INK; B.font = '200px Anton'; B.fillText(dia, 0, 40); B.font = '64px Anton'; B.fillStyle = '#5a4a60'; B.fillText(anio, 0, 160); B.restore();
}
/** cruz roja que se tacha de golpe */
function cruz(cx, cy, s, t) { if (t <= 0) return; B.save(); B.translate(cx, cy); B.lineCap = 'round';
  for (const [d, tt] of [[1, clamp(t * 2)], [-1, clamp(t * 2 - 1)]]) { if (tt <= 0) continue; const a = [-s * d, -s], b = [-s * d + 2 * s * d * tt, -s + 2 * s * tt];
    B.lineWidth = 56; B.strokeStyle = INK; B.beginPath(); B.moveTo(...a); B.lineTo(...b); B.stroke(); B.lineWidth = 34; B.strokeStyle = ROJO; B.stroke(); }
  B.restore(); }
function contador(v, f) { return Math.round(v).toLocaleString('es-ES').replace(/,/g, '.'); }
function billetes(f, f0, n = 18) { // billetes verdes que caen (dinero del juego)
  for (let i = 0; i < n; i++) { const t = (f - f0) / 45 - rnd(i) * 0.9; if (t <= 0) continue; const y = -120 + ((t * 1500 + rnd(i + 5) * 300) % 2200), x = rnd(i + 2) * W;
    B.save(); B.translate(x, y); B.rotate(Math.sin(t * 6 + i) * 0.8); B.fillStyle = '#2f9e4a'; B.fillRect(-70, -34, 140, 68); B.lineWidth = 6; B.strokeStyle = '#0d3a1a'; B.strokeRect(-70, -34, 140, 68);
    B.fillStyle = '#bff0b0'; B.font = '54px Anton'; B.textAlign = 'center'; B.textBaseline = 'middle'; B.fillText('$', 0, 2); B.restore(); }
}
/** sala de servidores dibujada: armarios con luces que pasan a rojo */
function servidores(f, f0, caos) {
  const gr = B.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#120812'); gr.addColorStop(1, '#2a0a10'); B.fillStyle = gr; B.fillRect(0, 0, W, H);
  for (let r = 0; r < 3; r++) { const x = 70 + r * 330, w = 280, y0 = 380, h = 1180;
    B.fillStyle = '#1d1a24'; B.fillRect(x, y0, w, h); B.lineWidth = 10; B.strokeStyle = '#000'; B.strokeRect(x, y0, w, h);
    for (let i = 0; i < 14; i++) { const y = y0 + 30 + i * 80; B.fillStyle = '#2b2734'; B.fillRect(x + 20, y, w - 40, 60); B.fillStyle = '#100e16'; B.fillRect(x + 110, y + 22, 130, 14);
      for (let l = 0; l < 3; l++) { const on = rnd(i * 7 + l + r * 50 + Math.floor((f - f0) / 3)) > 0.35, red = caos > rnd(i + r * 13 + l * 3);
        B.fillStyle = on ? (red ? ROJO : '#4dff9a') : '#2a2a2a'; B.beginPath(); B.arc(x + 42 + l * 22, y + 30, 8, 0, 7); B.fill(); } } }
  if (caos > 0) { B.fillStyle = `rgba(255,30,30,${0.18 * caos * (0.6 + 0.4 * Math.abs(Math.sin(f * 0.5)))})`; B.fillRect(0, 0, W, H); }
}
function ventanaError(cx, cy, k, txt1, txt2) { if (k <= 0) return; B.save(); B.translate(cx, cy); B.scale(k, k); B.rotate(0.03);
  const w = 880, h = 420; B.fillStyle = 'rgba(0,0,0,.5)'; B.fillRect(-w / 2 + 16, -h / 2 + 20, w, h); B.fillStyle = '#f4f2f6'; B.fillRect(-w / 2, -h / 2, w, h);
  B.fillStyle = ROJO; B.fillRect(-w / 2, -h / 2, w, 110); B.lineWidth = 10; B.strokeStyle = INK; B.strokeRect(-w / 2, -h / 2, w, h);
  B.fillStyle = BLANCO; B.font = '74px Anton'; B.textAlign = 'center'; B.textBaseline = 'middle'; B.fillText('⚠  ERROR', 0, -h / 2 + 58);
  B.fillStyle = INK; B.font = '92px Anton'; B.fillText(txt1, 0, 30); if (txt2) { B.font = '58px Anton'; B.fillStyle = '#7a2030'; B.fillText(txt2, 0, 140); } B.restore(); }
function lineaTiempo(cx, cy, t, a, b) { // barra 2013 → 2026
  const w = 820, x0 = cx - w / 2; B.save(); B.lineCap = 'round'; B.lineWidth = 54; B.strokeStyle = INK; B.beginPath(); B.moveTo(x0, cy); B.lineTo(x0 + w, cy); B.stroke();
  B.lineWidth = 36; B.strokeStyle = 'rgba(255,255,255,.25)'; B.stroke(); B.strokeStyle = VERDE; B.beginPath(); B.moveTo(x0, cy); B.lineTo(x0 + w * Math.max(0.001, t), cy); B.stroke();
  B.font = '64px Anton'; B.textAlign = 'center'; B.fillStyle = BLANCO; B.lineWidth = 12; B.strokeStyle = INK; B.lineJoin = 'round';
  for (const [x, s] of [[x0, a], [x0 + w, b]]) { B.strokeText(s, x, cy + 90); B.fillText(s, x, cy + 90); } B.restore(); }


/** jugadores conectados (avatares que aparecen unidos por líneas): «con sus amigos» */
function jugadores(f, f0, f1, y) {
  const n = 6, xs = [...Array(n)].map((_, i) => 150 + i * 156);
  B.save(); B.lineWidth = 8; B.strokeStyle = 'rgba(125,255,138,.9)'; B.setLineDash([18, 14]); B.lineDashOffset = -f * 2;
  for (let i = 0; i < n - 1; i++) { const k = ramp(f, f1 - 4 + i * 2, f1 + 4 + i * 2); if (k > 0) { B.beginPath(); B.moveTo(xs[i], y); B.lineTo(lerp(xs[i], xs[i + 1], k), y); B.stroke(); } }
  B.setLineDash([]);
  const cols = ['#ff5a8a', '#4dc3ff', '#ffd34a', '#7dff8a', '#c77dff', '#ff9a5a'];
  xs.forEach((x, i) => { const k = pop(f, f0 + i * 3, 8); if (k <= 0) return; B.save(); B.translate(x, y + Math.sin(f * 0.15 + i) * 6); B.scale(k, k);
    B.beginPath(); B.arc(0, 0, 62, 0, 7); B.fillStyle = INK; B.fill(); B.beginPath(); B.arc(0, 0, 52, 0, 7); B.fillStyle = cols[i]; B.fill();
    B.fillStyle = INK; B.beginPath(); B.arc(0, -12, 18, 0, 7); B.fill(); B.beginPath(); B.ellipse(0, 30, 30, 22, 0, Math.PI, 0); B.fill();
    B.beginPath(); B.arc(42, -42, 13, 0, 7); B.fillStyle = '#2fe060'; B.fill(); B.lineWidth = 5; B.strokeStyle = INK; B.stroke(); B.restore(); });
  B.restore();
}
/** latido (electrocardiograma) que se dibuja de izquierda a derecha: «trece años vivo» */
function latido(f, f0, y) {
  const t = ramp(f, f0, f0 + 24); if (t <= 0) return; const pts = [];
  for (let x = 0; x <= W; x += 6) { const u = x / W, ph = (u * 3) % 1; let v = 0;
    if (ph > 0.42 && ph < 0.48) v = -(ph - 0.42) / 0.06 * 40; else if (ph >= 0.48 && ph < 0.53) v = -40 + (ph - 0.48) / 0.05 * 200; else if (ph >= 0.53 && ph < 0.58) v = 160 - (ph - 0.53) / 0.05 * 300; else if (ph >= 0.58 && ph < 0.62) v = -140 + (ph - 0.58) / 0.04 * 140;
    pts.push([x, y - v]); }
  const n = Math.max(2, Math.floor(pts.length * t));
  B.save(); B.lineJoin = 'round'; B.lineCap = 'round';
  for (const [lw, col] of [[26, 'rgba(0,0,0,.55)'], [18, 'rgba(47,224,96,.35)'], [8, '#7dff8a']]) { B.lineWidth = lw; B.strokeStyle = col; B.beginPath(); pts.slice(0, n).forEach(([x, yy], i) => (i ? B.lineTo(x, yy) : B.moveTo(x, yy))); B.stroke(); }
  const [hx, hy] = pts[n - 1]; B.fillStyle = BLANCO; B.shadowColor = '#7dff8a'; B.shadowBlur = 30; B.beginPath(); B.arc(hx, hy, 14, 0, 7); B.fill(); B.restore();
}
/** lupa que pasa por encima (la pista) */
function lupa(cx, cy, k) { if (k <= 0) return; B.save(); B.translate(cx, cy); B.scale(k, k); B.rotate(-0.5);
  B.lineCap = 'round'; B.lineWidth = 60; B.strokeStyle = INK; B.beginPath(); B.moveTo(0, 170); B.lineTo(0, 340); B.stroke(); B.lineWidth = 40; B.strokeStyle = '#b8742a'; B.stroke();
  B.beginPath(); B.arc(0, 0, 170, 0, 7); B.fillStyle = 'rgba(200,235,255,.07)'; B.fill(); B.lineWidth = 34; B.strokeStyle = INK; B.stroke(); B.lineWidth = 20; B.strokeStyle = '#e8e8f0'; B.stroke();
  B.beginPath(); B.arc(-60, -60, 50, Math.PI * 1.05, Math.PI * 1.55); B.lineWidth = 14; B.strokeStyle = 'rgba(255,255,255,.8)'; B.stroke(); B.restore(); }
/** destellos de atardecer que suben despacio (escenas de GTA 6) */
function destellos(f, n = 16) { B.save(); B.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) { const t = (f / 300 + rnd(i)) % 1, x = rnd(i + 9) * W + Math.sin(f * 0.02 + i) * 40, y = H * (1.05 - t * 1.1), r = 18 + rnd(i + 3) * 46, a = Math.sin(t * Math.PI) * 0.22;
    const gr = B.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, `rgba(255,${180 + (i % 3) * 25},${150 + (i % 4) * 25},${a})`); gr.addColorStop(1, 'rgba(255,150,200,0)'); B.fillStyle = gr; B.beginPath(); B.arc(x, y, r, 0, 7); B.fill(); }
  B.restore(); }
// ---------- recortes de las viñetas (imágenes del usuario, sin tocar) ----------
const ON = { oro: [404, 702, 280, 95], coche: [36, 690, 340, 300], chica: [36, 438, 300, 230], ruleta: [36, 225, 300, 190], sub: [690, 430, 300, 220] };
const COL = { moto: [870, 0, 303, 410], cocodrilo: [420, 860, 380, 200], lancha: [840, 900, 333, 420], pareja: [352, 0, 498, 345] };

// ---------- planos ----------
// Cada plano empieza en una frase (fr(i) - 2: el corte llega justo antes de oírla). in: 'golpe' (zoom + destello) o 'barrido'.
const P = [];
const plano = (i, entrada, draw) => P.push({ a: Math.max(0, fr(i) - 2), entrada, draw });

plano(0, 'golpe', (f, l, S) => { // ¿Saldrá GTA 6 Online? ¿Y cuánto tendremos que esperar?
  cover(IMG['moto-persecucion'], null, 1.04 + 0.12 * l / S.n, 0, -0.2); degradado(1100, 1920, 0, 0.85); degradado(0, 420, 0.6, 0);
  logo('logo-gta6', W / 2, 230, 360, pop(f, 2));
  if (f < fr(1) - 2) { titulo('¿GTA 6', W / 2, 1230, 230, BLANCO, pop(f, 0, 7), -0.04); titulo('ONLINE?', W / 2, 1460, 250, 'atardecer', pop(f, en('online') - 3), -0.04); }
  else { titulo('¿CUÁNTO', W / 2, 1230, 230, BLANCO, pop(f, fr(1) - 2, 7), -0.04); titulo('FALTA?', W / 2, 1460, 260, 'atardecer', pop(f, en('esperar', 1) - 3), -0.04); }
});
plano(2, 'barrido', (f, l, S) => { // Con GTA 5, la espera fue de solo catorce días.
  fondo('gta5-portada', 1.05 + 0.05 * l / S.n, 0.55); logo('logo-gta5', W / 2, 430, 620, pop(f, S.a + 1));
  const fc = en('catorce', 2), v = 14 * easeOut(ramp(f, S.a + 6, fc));
  const k = f >= fc ? 1 + 0.18 * (1 - smooth(ramp(f, fc, fc + 12))) : 1;
  titulo(String(Math.round(v)), W / 2, 1100, 520, VERDE, pop(f, S.a + 4) * k, -0.03); titulo('DÍAS', W / 2, 1450, 170, BLANCO, pop(f, fc - 2), -0.03);
  if (f >= en('solo', 2)) rotulo('SOLO', W / 2, 820, 90, ROJO, BLANCO, pop(f, en('solo', 2) - 2), -0.06);
});
plano(3, 'barrido', (f, l, S) => { // Pero esta vez es distinto. Y vas a ver qué pista apunta ya a un año concreto.
  cover(IMG['gta6-palmeras-coche'], null, 1.1 + 0.1 * l / S.n, 0, 0.3 - 0.6 * l / S.n);
  if (f < fr(4) - 2) { degradado(900, 1920, 0, 0.7); titulo('ESTA VEZ', W / 2, 1230, 200, BLANCO, pop(f, S.a + 2), -0.04); titulo('ES DISTINTO', W / 2, 1440, 190, 'atardecer', pop(f, en('distinto', 3) - 3), -0.04); }
  else { velo(0.35, '20,6,40'); const g = f >= en('ano', 4) ? 1 : 0;
    rotulo('LA PISTA', W / 2, 700, 90, ORO, INK, pop(f, en('pista', 4) - 2), -0.05);
    const q1 = g ? '?' : '?', jit = (i) => g ? (rnd(f * 3 + i) - 0.5) * 26 : 0;
    B.save(); B.translate(jit(1), jit(2)); titulo('20' + q1 + q1, W / 2, 1050, 400, 'atardecer', pop(f, fr(4)), -0.04); B.restore();
    const u = ramp(f, en('pista', 4), S.b); lupa(lerp(380, 760, smooth(u)), 1010 + Math.sin(u * 6) * 30, pop(f, en('pista', 4) - 2)); }
});
plano(5, 'barrido', (f, l, S) => { // GTA 5 salió el 17 de septiembre de 2013.
  fondo('gta5-portada', 1.08 + 0.05 * l / S.n, 0.5);
  vineta(IMG['gta5-portada'], null, W / 2, 640, 840, 1120, -0.03, pop(f, S.a + 1) * (1 + 0.05 * l / S.n), 1.0);
  calendario('SEP', '17', '2013', W / 2 + 180, 1330, 0.95, pop(f, en('17', 5) - 3), '#3d7a2a');
});
plano(6, 'golpe', (f, l, S) => { // El 1 de octubre, millones de jugadores ya recorrían Los Santos con sus amigos.
  fondo('gta-online-portada', 1.05 + 0.05 * l / S.n, 0.45);
  vineta(IMG['gta-online-portada'], null, W / 2, 760, 960, 960, 0.02, (1 + 0.06 * l / S.n), 1.0);
  calendario('OCT', '1', '2013', 250, 330, 0.8, pop(f, en('octubre', 6) - 4), ROJO);
  rotulo('MILLONES', W / 2, 1420, 96, ORO, INK, pop(f, en('millones', 6) - 2), 0.04);
  rotulo('CON AMIGOS', W / 2, 1560, 80, BLANCO, INK, pop(f, en('amigos', 6) - 3), -0.03);
  jugadores(f, en('jugadores', 6) - 2, en('amigos', 6), 1250);
});
plano(7, 'barrido', (f, l, S) => { // Pero esas prisas tuvieron un precio. ¿Qué pasó en aquellos primeros días?
  const r = smooth(ramp(f, S.a, S.a + 40));
  fondo('gta-online-portada', 1.1, 0.55);
  B.save(); B.filter = `grayscale(${r.toFixed(2)})`; vineta(IMG['gta-online-portada'], null, W / 2, 700, 960, 960, 0.02 - 0.04 * r, 1.06 + 0.08 * l / S.n, 1.0); B.restore();
  velo(0.3 * r, '160,0,0');
  if (f < fr(8) - 2) titulo('UN PRECIO', W / 2, 1400, 220, ROJO, pop(f, en('precio', 7) - 3), -0.04);
  else { titulo('¿QUÉ', W / 2, 1230, 230, BLANCO, pop(f, fr(8) - 2), -0.04); titulo('PASÓ?', W / 2, 1450, 260, ROJO, pop(f, en('paso', 8) - 3), -0.04); }
});
plano(9, 'golpe', (f, l, S) => { // Los servidores no aguantaron.
  const c = ramp(f, en('no', 9) - 2, en('aguantaron', 9) + 6); servidores(f, S.a, c);
  ventanaError(W / 2, 960, pop(f, en('aguantaron', 9) - 2), 'NO AGUANTARON', 'SERVIDORES DE GTA ONLINE');
  titulo('SERVIDORES', W / 2, 220, 160, BLANCO, pop(f, en('servidores', 9) - 3));
});
plano(10, 'barrido', (f, l, S) => { // Hubo jugadores que perdieron su dinero, sus coches y hasta su personaje.
  fondo('gta-online-portada', 1.1, 0.5); velo(0.22, '120,0,0');
  rotulo('JUGADORES', W / 2, 115, 84, ORO, INK, pop(f, S.a + 2), 0.02); titulo('PERDIERON', W / 2, 250, 170, BLANCO, pop(f, en('perdieron', 10) - 3), -0.03);
  const it = [['dinero', ON.oro, 'DINERO', 470], ['coches', ON.coche, 'COCHES', 890], ['personaje', ON.chica, 'SU PERSONAJE', 1310]];
  it.forEach(([w, crop, lab, y], i) => { const f0 = en(w, 10) - 4, k = pop(f, f0);
    vineta(IMG['gta-online-portada'], crop, W / 2, y, 760, 330, (i - 1) * 0.04, k, 1.1);
    cruz(W / 2 + 120, y - 10, 110, ramp(f, f0 + 8, f0 + 16)); rotulo(lab, W / 2 - 200, y + 140, 70, BLANCO, INK, k, -0.04); });
});
plano(11, 'golpe', (f, l, S) => { // Rockstar pidió perdón y regaló quinientos mil dólares del juego a cada jugador.
  fondo('gta-online-portada', 1.15, 0.6); const fq = en('quinientos', 11);
  if (f < fq - 2) rotulo('ROCKSTAR', W / 2, 600, 100, BLANCO, INK, pop(f, S.a + 2), 0.03);
  if (f < fq - 2) { titulo('PIDIÓ', W / 2, 820, 200, BLANCO, pop(f, en('pidio', 11) - 3), -0.04); titulo('PERDÓN', W / 2, 1060, 260, ORO, pop(f, en('perdon', 11) - 3), -0.04); }
  else { billetes(f, fq); const v = 500000 * easeOut(ramp(f, fq, en('dolares', 11) + 4));
    titulo(contador(v), W / 2, 900, 250, '#7dff8a', pop(f, fq - 2), -0.04); titulo('GTA$', W / 2, 1120, 170, BLANCO, pop(f, en('dolares', 11) - 2), -0.04);
    rotulo('DINERO DEL JUEGO', W / 2, 1300, 72, BLANCO, INK, pop(f, en('juego', 11) - 2), -0.03);
    rotulo('A CADA JUGADOR', W / 2, 1460, 84, ORO, INK, pop(f, en('cada', 11) - 2), 0.03); }
});
plano(12, 'golpe', (f, l, S) => { // Ahora, GTA 6 salió el 19 de noviembre de 2026.
  atardecer(f); destellos(f, 22); palmeras(f, l);
  const k = pop(f, S.a + 1, 8); logo('logo-gta6', W / 2, 640, 860 * (1 + 0.25 * (1 - smooth(ramp(f, S.a, S.a + 14)))), k);
  calendario('NOV', '19', '2026', W / 2, 1320, 1.0, pop(f, en('19', 12) - 3), '#8e4fd0');
});
plano(13, 'barrido', (f, l, S) => { // Y solo trae la historia.
  cover(IMG['pareja-muelle'], null, 1.0 + 0.1 * l / S.n, 0, 0.6 - 0.4 * l / S.n); degradado(1150, 1920, 0, 0.75);
  rotulo('✔ MODO HISTORIA', W / 2, 1330, 96, '#2fbf5a', BLANCO, pop(f, en('historia', 13) - 4), -0.03);
  rotulo('✘ ONLINE', W / 2, 1500, 96, ROJO, BLANCO, pop(f, en('historia', 13) + 6), 0.03);
});
plano(14, 'barrido', (f, l, S) => { // Del online, Rockstar no ha dado ni una fecha.
  fondo('gta6-palmeras-coche', 1.08 + 0.04 * l / S.n, 0.4); const ff = en('fecha', 14), sh = f >= ff ? (rnd(f) - 0.5) * 24 : 0;
  rotulo('GTA 6 ONLINE', W / 2, 420, 110, BLANCO, INK, pop(f, S.a + 2), -0.04);
  B.save(); B.translate(sh, 0); calendario('???', '?', '????', W / 2, 920, 1.2, pop(f, en('dado', 14) - 4), '#5a5a6a'); B.restore();
  titulo('SIN FECHA', W / 2, 1460, 210, ROJO, pop(f, ff - 3), -0.04);
});
plano(15, 'golpe', (f, l, S) => { // Entonces, ¿cuándo llegará?
  cover(IMG['gta6-palmeras-coche'], null, 1.0 + 0.14 * l / S.n, 0, 0.9); degradado(0, 700, 0.55, 0);
  destellos(f);
  titulo('¿CUÁNDO', W / 2, 330, 230, BLANCO, pop(f, en('cuando', 15) - 3), -0.04); titulo('LLEGARÁ?', W / 2, 560, 230, 'atardecer', pop(f, en('llegara', 15) - 3), -0.04);
});
plano(16, 'barrido', (f, l, S) => { // En octubre, Bloomberg publicó que Rockstar lo tiene previsto para 2027. Rockstar no lo ha confirmado.
  cover(IMG['poster-vinetas'], null, 1.05 + 0.12 * l / S.n, 0, -0.3); const f27 = en('2027', 16);
  rotulo('BLOOMBERG · OCTUBRE 2026', W / 2, 260, 70, BLANCO, INK, pop(f, en('bloomberg', 16) - 3), -0.02);
  if (f >= f27 - 3) { velo(0.45 * ramp(f, f27 - 3, f27 + 4), '20,6,40'); const z = 1 + 0.3 * (1 - smooth(ramp(f, f27, f27 + 14)));
    titulo('2027', W / 2, 960, 420, 'atardecer', pop(f, f27 - 3, 7) * z, -0.05); rotulo('PREVISTO', W / 2, 1230, 90, ORO, INK, pop(f, f27 + 4), 0.03); }
  const fc = en('confirmado', 17); if (f >= fc - 4) { B.save(); B.globalAlpha = 0.92; rotulo('SIN CONFIRMAR', W / 2, 1460, 120, ROJO, BLANCO, 1.6 - 0.6 * easeOut(ramp(f, fc - 4, fc + 3)), -0.12); B.restore(); }
});
plano(18, 'barrido', (f, l, S) => { // Pero hay una razón para no correr. GTA Online lleva trece años vivo.
  cover(IMG['gta6-dos-chicos'], null, 1.02 + 0.1 * l / S.n, 0, -0.4); degradado(900, 1920, 0, 0.85);
  if (f < fr(19) - 2) { titulo('UNA RAZÓN', W / 2, 1250, 210, BLANCO, pop(f, en('razon', 18) - 3), -0.04); titulo('PARA NO CORRER', W / 2, 1450, 140, ORO, pop(f, en('correr', 18) - 3), -0.04); }
  else { const ft = en('trece', 19), v = 13 * easeOut(ramp(f, fr(19), ft + 6));
    rotulo('GTA ONLINE', W / 2, 1080, 96, ROJO, BLANCO, pop(f, fr(19) - 1), -0.03);
    titulo(Math.round(v) + ' AÑOS', W / 2, 1290, 210, BLANCO, pop(f, ft - 3), -0.03); lineaTiempo(W / 2, 1490, easeOut(ramp(f, fr(19), ft + 10)), '2013', '2026'); latido(f, en('vivo', 19) - 8, 860); }
});
plano(20, 'golpe', (f, l, S) => { // Y la saga ha ingresado más de diez mil millones de dólares desde 2013.
  fondo('gta5-portada', 1.1 + 0.05 * l / S.n, 0.62); billetes(f, en('diez', 20), 14);
  const fd = en('diez', 20), v = 10000 * easeOut(ramp(f, fd - 2, en('millones', 20) + 6));
  rotulo('LA SAGA GTA', W / 2, 470, 96, BLANCO, INK, pop(f, S.a + 2), 0.03); rotulo('MÁS DE', W / 2, 660, 90, ORO, INK, pop(f, en('mas', 20) - 3), -0.04);
  titulo(contador(v), W / 2, 900, 330, '#7dff8a', pop(f, fd - 3), -0.04);
  titulo('MILLONES DE $', W / 2, 1150, 150, BLANCO, pop(f, en('millones', 20) - 2), -0.04);
  rotulo('DESDE 2013', W / 2, 1360, 86, BLANCO, INK, pop(f, en('desde', 20) - 2), 0.03);
});
plano(21, 'barrido', (f, l, S) => { // Mi apuesta: esta vez Rockstar podría esperar antes que repetir aquel caos.
  const fc = en('caos', 21); cover(IMG['moto-persecucion'], null, 1.2 + 0.08 * l / S.n, 0.3, 0.4); degradado(1000, 1920, 0, 0.8);
  rotulo('MI APUESTA', W / 2, 1200, 110, ORO, INK, pop(f, en('apuesta', 21) - 3), -0.04);
  titulo('ESPERAR', W / 2, 1420, 210, 'atardecer', pop(f, en('esperar', 21) - 3), -0.04);
  if (f >= fc - 3) { velo(0.35 * (1 - ramp(f, fc + 6, fc + 22)), '255,20,20'); ventanaError(W / 2, 700, pop(f, fc - 3, 6), 'AQUEL CAOS', '2013'); }
});
plano(22, 'golpe', (f, l, S) => { // ¿Tú esperarías hasta 2027 por un GTA Online nuevo?
  fondo('portada-collage', 1.08, 0.5);
  vineta(IMG['portada-collage'], null, W / 2, 640, 900, 1040, -0.02, 1.08 - 0.08 * easeOut(l / S.n), 1.0);
  destellos(f, 20);
  rotulo('GTA ONLINE NUEVO', W / 2, 1215, 84, ROJO, BLANCO, pop(f, en('nuevo', 22) - 3), 0.03);
  titulo('¿ESPERARÍAS', W / 2, 1440, 190, BLANCO, pop(f, en('esperarias', 22) - 3), -0.04);
  titulo('HASTA 2027?', W / 2, 1630, 210, 'atardecer', pop(f, en('2027', 22) - 3), -0.04);
});
P.forEach((s, i) => { s.b = i < P.length - 1 ? P[i + 1].a - 1 : DURACION - 1; s.n = s.b - s.a + 1; });
export const SHOTS = P;

// ---------- composición final: entrada del plano, glitch, grano, viñeteado ----------
function glitch(f, amt) { // franjas desplazadas + separación de color (momentos de caos)
  T.clearRect(0, 0, W, H); T.drawImage(BUF, 0, 0);
  for (let i = 0; i < 9; i++) { const y = rnd(f * 13 + i) * H, h = 20 + rnd(f * 7 + i) * 120, dx = (rnd(f * 5 + i) - 0.5) * 160 * amt; B.drawImage(TMP, 0, y, W, h, dx, y, W, h); }
  B.save(); B.globalCompositeOperation = 'lighter'; B.globalAlpha = 0.25 * amt; B.drawImage(TMP, 12 * amt, 0); B.restore();
}
window.renderFrame = (f) => {
  f = clamp(f, 0, DURACION - 1); const S = P.find((s) => f >= s.a && f <= s.b) || P[P.length - 1], l = f - S.a;
  B.save(); B.fillStyle = '#000'; B.fillRect(0, 0, W, H); S.draw(f, l, S); B.restore();
  // caos: glitch en los fallos de 2013
  const caos = [[en('aguantaron', 9) - 2, 14], [en('personaje', 10) + 4, 6], [en('caos', 21) - 2, 10]];
  for (const [a, d] of caos) if (f >= a && f < a + d) glitch(f, 1 - (f - a) / d);
  G.save(); G.fillStyle = '#000'; G.fillRect(0, 0, W, H);
  if (S.entrada === 'golpe' && l < 6) { const t = easeOut(l / 6), z = lerp(1.14, 1, t); G.translate(W / 2, H / 2); G.scale(z, z); G.translate(-W / 2, -H / 2); G.drawImage(BUF, 0, 0); G.setTransform(1, 0, 0, 1, 0, 0); G.fillStyle = `rgba(255,255,255,${(0.55 * (1 - t)).toFixed(3)})`; G.fillRect(0, 0, W, H); }
  else if (S.entrada === 'barrido' && l < 5 && S.a > 0) { const t = easeOut(l / 5), dx = (1 - t) * W * 0.35; for (let k = 3; k >= 0; k--) { G.globalAlpha = k ? 0.22 : 1; const x = dx + k * 40 * (1 - t); G.drawImage(BUF, x, 0); G.drawImage(BUF, x - W, 0); } G.globalAlpha = 1; }
  else G.drawImage(BUF, 0, 0);
  G.restore();
  // grano y viñeteado (dan textura de póster)
  G.save(); G.globalAlpha = 0.04; G.globalCompositeOperation = 'overlay'; const fg = Math.floor(f / 4), ox = Math.floor(rnd(fg) * 256), oy = Math.floor(rnd(fg + 1) * 256);
  for (let y = -oy; y < H; y += 256) for (let x = -ox; x < W; x += 256) G.drawImage(IMG.grano, x, y); G.restore();
  const v = G.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.45)'); G.fillStyle = v; G.fillRect(0, 0, W, H);
};
cargar().then(() => { window.renderFrame(0); window.ready = true; }).catch((e) => { window.err = String(e); console.log('ERR ' + e.stack); });
