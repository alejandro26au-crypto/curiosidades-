# Motor de dibujos — canal Citrino

Personajes 2D de «cabeza de judía» (con contorno) dentro de un mundo 3D pintado, con tinta, desenfoque de lente y
cámaras que no paran. Funciona con three.js dentro de Chromium (Playwright), sin descargar nada: ~2,3 s por fotograma
en la nube. Viene del repo `Oceano-animado-` (rama `claude/fervent-archimedes-c1dp80`, carpeta `dibujos/`), portado
el 20 nov 2026 con todas las mejoras del vídeo del submarino.

**Calidad = el ejemplo de los romanos** (`kit/example/soldier/stills.jpg`). Prueba superada: `plantilla/prueba_vs_romanos.jpg`.

## Carpetas
- `kit/`: el kit original tal cual (engine, tools, ejemplo de los romanos, SKILL.md) + `vendor/` con three.js y
  toon.ts guardados (licencia MIT). Es la REFERENCIA; no se toca.
- `herramientas/`:
  - `preparar.sh`: deja listo un vídeo (copia librerías, junta el reparto, enlaza Playwright).
  - `tiempos_es.py`: tiempos de la voz en español → `tiempos.json` y `web/tiempos.js` (cada frase y cada palabra con su fotograma).
  - `comparar.py`: hoja de fotos al lado de los romanos (para revisar la calidad).
  - `mix.py`: música al 50 % de la voz (−6 dB) y efectos al 50 % o menos; también sin música (`-`).
  - `terminar.sh`: junta imagen y sonido a −14 LUFS y revisa (congelados, negros); sale `out/hoja_final.jpg`.
  - `tiempos_estimados.py`: tiempos sin voz (~170 ppm) para planificar y estimar la duración (de Zingo).
  - `subtitulos.py`: subtítulos de 1-2 palabras con las cifras en amarillo → `out/subtitulos.srt` (para subir) y
    `out/subtitulos.ass` (`SUBS=1 bash terminar.sh …` los quema en el vídeo) (de Zingo).
  - `gestos.js` (brazos con impulso, asentir) y `boca.py` (boca según la voz; solo si se pide).
- `plantilla/`: el punto de partida de CADA vídeo (ver `plantilla/LEEME.md`). Trae un decorado de ejemplo (plaza de
  pueblo) que se cambia siempre.
- `ejemplos/submarino/`: el vídeo del submarino de Benthara, SOLO PARA CONSULTAR cómo se hizo algo (decorado interior,
  luces de alarma, efectos). No se copia su decorado ni su reparto.
- `videos/<nombre>/`: cada vídeo de Citrino (se crea copiando `plantilla/`).

## Lo que trae la plantilla (mejoras del submarino)
1. `main.js` partido en piezas: `_head.js` (motor), `_world.js` (decorado), `_tail.js` (tarjetas y postproceso),
   `_frame.js` (luces por plano, tarjetas con `fixedYaw`, `alpha`, modo aditivo `add`, `noInk`) + `rebuild.sh`.
2. `paint.js`: texturas nuevas en el estilo del kit (chapa con remaches, suelo estriado, colchón, manta, esfera con
   números, batería, rayos de luz, casco exterior).
3. `roman.js`: ropa nueva (camisa con bolsillos, camiseta, chaquetón, gorra de plato, gorro blanco, gorro de barco,
   mangas y pantalón de color propio); poses `hold` (con cerilla), `shh`, `mouth`, `cheer`; manos sobre la cara;
   sudor (`sweat`), mejillas hinchadas (`puff`), pecas, cara `hold`.
4. `story.js`: planos atados a cada palabra (`en('palabra')`), luces por plano (día, tarde, noche, interior, alarma,
   oscuro, gas), golpes de cámara (KICKS), **zoom de golpe** (ZOOMS), **barrido rápido entre planos**, temblor
   (SACUDIDAS), destellos (FLASHES) y efectos 2D (vapor, burbujas, chorro, onda, explosión aditiva, palabra que salta,
   objeto que cae + los del kit).
5. `carta.mjs`: prueba de personajes sueltos (poses y caras) antes de renderizar escenas.
6. `audio.py`: música por tramos (tema, silencio antes del golpe, cómico, solemne, fanfarria, dron) + whoosh en cada
   corte y efecto en cada golpe → `music.wav` y `sfx.wav`.
7. `publicar.md`: ficha para publicar.
8. `insertos.js` (de Zingo): termómetro, manómetro, contador, barra, reloj, comparativa y capas, con tinta y rebote;
   en `story.js`, `inserto('barra', f, f0, f1, { de, a, unidad, etiqueta })` lo pone delante de la cámara, nítido.

## REGLAS DEL MOTOR (del usuario)
- **Calidad = romanos**: comparar lado a lado (`comparar.py`) antes de montar.
- **Decorado A MEDIDA de cada vídeo**, con las piezas del kit y en su mismo estilo. Se reutiliza un decorado,
  personaje u objeto solo si el guion o la voz lo mencionan. Cada vídeo, mejor que el anterior.
- **Gestos del kit**: caras fijas y claras que cambian en la palabra clave, `idle()` siempre (respira y se mece),
  acciones con impulso, asentir en palabras fuertes, negar, 4-5 cambios de brazos por vídeo.
- Personajes: el mismo cuerpo y cara del kit; solo cambia la ropa (OUTFITS en `web/roman.js`).
- **Encuadre: personajes más pequeños o lejos para que se vea el entorno** (plano medio-general: ~1/3-1/2 de la altura
  del cuadro). Caras a pantalla completa solo 1-2 veces y breves. El personaje que gesticula, siempre entero.
- **Revisar YO cada imagen** antes de enviarla (textos cortados, personajes tapados o fuera de plano, cámara metida en
  algo, farolas saliendo de cabezas). Nada en pantalla que no diga el guion.
- **Entregar dos MP4 (con y sin música) + la ficha para publicar.**

## Hacer un vídeo (pasos)
1. Guion aprobado (fórmula de Citrino: `docs/FORMULA-GUIONES-CITRINO.md`) → `script.txt`. Voz del usuario → `voice.mp3` (no se sube).
2. `cp -r dibujos/plantilla dibujos/videos/<nombre>` y `bash dibujos/herramientas/preparar.sh dibujos/videos/<nombre>`.
3. Desde la carpeta del vídeo: `python3 ../../herramientas/tiempos_es.py voice.mp3 script.txt es`
   (sin voz aún: `python3 ../../herramientas/tiempos_estimados.py script.txt`; la duración la marca el guion).
4. Decorado en `web/_world.js`, ropa en `web/roman.js`, planos en `web/story.js` → `bash rebuild.sh`.
5. `node carta.mjs carta.png '[["vecino",{"R":"hold"}]]'` para probar personajes.
6. Hoja: `node render.mjs stills/a "30,140,…"` + `python3 ../../herramientas/comparar.py hoja.jpg stills/a/f*.jpg` →
   REVISAR → corregir → enseñar.
7. Montaje en segundo plano: `node render.mjs frames "0-<DURACION-1>"`.
8. `python3 audio.py` → `python3 ../../herramientas/mix.py voice.mp3 music.wav sfx.wav` y
   `python3 ../../herramientas/mix.py voice.mp3 - sfx.wav out/mix_sin_musica.wav`.
9. `python3 ../../herramientas/subtitulos.py` → `bash ../../herramientas/terminar.sh "Titulo"` y `bash ../../herramientas/terminar.sh "Titulo" out/mix_sin_musica.wav`
   → revisar `out/hoja_final.jpg` → enviar los dos MP4.
10. Enviar la ficha (`publicar.md`) en bloques para copiar y guardarla en la carpeta del vídeo.

## Aprendido
- Plano vertical estrecho: a 6,5 m con fov 44 caben ~3 m de ancho; tres personajes entran si están a ~0,6-1 m entre sí.
- Al mover la cámara, revisar quién tapa a quién: un personaje detrás de otro desaparece en la foto.
- Textos grandes y trazos gruesos: a distancia se ven finos.
