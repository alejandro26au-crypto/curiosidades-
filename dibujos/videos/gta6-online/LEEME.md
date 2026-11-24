# Plantilla de un vídeo nuevo (motor de dibujos de Citrino)
Calidad de los romanos (`dibujos/kit/example/soldier/stills.jpg`) + todas las mejoras del vídeo del submarino.
Trae un decorado de EJEMPLO (plaza de pueblo de día) que hay que CAMBIAR en cada vídeo.

## Archivos
| Archivo | Qué es | ¿Se toca? |
|---|---|---|
| `web/_head.js` | motor: render, materiales, tinta, cielo, luces | no |
| `web/_world.js` | **el decorado** (piezas del kit) + `worldState` y `worldLight` | **sí, a medida** |
| `web/_tail.js` | tarjetas de personajes y postproceso | no |
| `web/_frame.js` | cada fotograma: luces por plano, tarjetas (`fixedYaw`, `alpha`, `add`, `noInk`) | casi nunca |
| `web/story.js` | **planos, luces, cámaras, golpes, zooms, barridos, gestos, efectos 2D** | **sí** |
| `web/roman.js` | caras, poses y **la ropa del reparto** (OUTFITS) | ropa sí |
| `web/paint.js` | texturas pintadas (kit + nuevas: chapa, suelo estriado, colchón, manta, esfera, batería, rayos de luz) | si hace falta una textura nueva |
| `web/insertos.js` | insertos de datos (termómetro, contador, reloj, comparativa…) | no |
| `web/tiempos.js` | frases y palabras con su fotograma (lo escribe `tiempos_es.py`) | no a mano |
| `rebuild.sh` | junta `_head+_world+_tail+_frame` → `main.js` y `toonbase+roman` → `toon.js` | ejecutar tras cada cambio |
| `carta.mjs` | prueba de personajes sueltos (poses y caras) sin renderizar escenas | — |
| `audio.py` | música por tramos + efectos en cortes y golpes → `music.wav`, `sfx.wav` | **sí** |
| `publicar.md` | ficha para publicar (modelo) | **sí** |

## Pasos
1. `cp -r dibujos/plantilla dibujos/videos/<nombre>` y `bash dibujos/herramientas/preparar.sh dibujos/videos/<nombre>`.
2. `script.txt` (guion aprobado) y `voice.mp3` → `python3 ../../herramientas/tiempos_es.py voice.mp3 script.txt es`.
3. Decorado a medida en `web/_world.js`, ropa en `web/roman.js`, planos en `web/story.js` → `bash rebuild.sh`.
4. Personajes: `node carta.mjs carta.png '[["vecino",{"R":"hold","match":1,"expr":"cejas"}],["chico",{"L":"cheer","R":"cheer","expr":"laugh"}]]'`.
5. Hoja de fotos: `node render.mjs stills/a "30,140,…"` + `python3 ../../herramientas/comparar.py hoja.jpg stills/a/f*.jpg`
   (sale al lado de los romanos) → REVISAR cada imagen → enseñar y esperar el «aprobado».
6. Montaje: `node render.mjs frames "0-<DURACION-1>"` (~2,3 s/fotograma, en segundo plano).
7. `python3 audio.py` → `mix.py` con música y sin música → `terminar.sh "Título"` (y `terminar.sh "Título" out/mix_sin_musica.wav`).
8. Enviar los dos MP4 y la ficha `publicar.md`.
