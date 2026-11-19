// Renderiza los fondos 3D cuadro por cuadro en Chromium headless y los emite
// por stdout (una línea base64 JPEG por cuadro) para que Python los componga.
// Uso: node render3d.js trabajo.json
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..', '..');
const trabajo = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

const servidor = http.createServer((req, res) => {
  const ruta = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!ruta.startsWith(RAIZ) || !fs.existsSync(ruta)) { res.writeHead(404); return res.end(); }
  const tipo = ruta.endsWith('.js') ? 'text/javascript' : 'text/html';
  res.writeHead(200, { 'Content-Type': tipo }); fs.createReadStream(ruta).pipe(res);
});

function escribir(linea) {
  return new Promise((ok) => { if (process.stdout.write(linea)) ok(); else process.stdout.once('drain', ok); });
}

(async () => {
  await new Promise((ok) => servidor.listen(0, '127.0.0.1', ok));
  const puerto = servidor.address().port;
  const nav = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pag = await nav.newPage({ viewport: { width: 400, height: 400 } });
  pag.on('pageerror', (e) => process.stderr.write('[3d] ' + e.message + '\n'));
  pag.on('console', (m) => { if (m.type() === 'error') process.stderr.write('[3d] ' + m.text() + '\n'); });
  await pag.goto(`http://127.0.0.1:${puerto}/motor/escena3d/blank.html`);
  await pag.evaluate(([w, h]) => { window.ANCHO = w; window.ALTO = h; }, [trabajo.ancho, trabajo.alto]);
  await pag.addScriptTag({ url: `/motor/escena3d/escena.js`, type: 'module' });
  await pag.waitForFunction(() => window.listo === true, null, { timeout: 60000 });
  let actual = -1;
  for (const c of trabajo.cuadros) {
    if (c.e !== actual) { await pag.evaluate((f) => window.construir(f), trabajo.escenas[c.e]); actual = c.e; }
    const url = await pag.evaluate(([cam, t, p]) => window.cuadro(cam, t, p), [c.cam, c.t, c.p]);
    await escribir(url.slice(url.indexOf(',') + 1) + '\n');
  }
  await nav.close();
  servidor.close();
})().catch((e) => { process.stderr.write(String(e.stack || e) + '\n'); process.exit(1); });
