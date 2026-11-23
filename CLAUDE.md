# Canal Citrino — instrucciones
Háblale al usuario en español sencillo y corto.

## Qué hay en este repo
- `dibujos/`: **motor de dibujos** (el de los romanos + mejoras del submarino). Es el motor para los vídeos de Citrino.
  Reglas y pasos: `dibujos/LEEME.md`. Punto de partida de cada vídeo: `dibujos/plantilla/`.
- `docs/FORMULA-GUIONES-CITRINO.md`: **la fórmula de guiones de Citrino** (la que manda).
- `guiones/`: fichas de guion, auditor (`citrino.py`) y banco de ideas (`IDEAS.md`).
- `docs/RESULTADOS.md`: lo que da cada vídeo a los 2 días.
- `docs/LO-QUE-SIRVE-DE-ZINGO.md`: lo aprovechado del canal Zingo (lecciones de retención y producción).
- `motor/`, `ejemplos/`, `ANALISIS.md`: el motor anterior (Zingo, 3D low-poly). Ya NO se usa; lo útil está en `dibujos/`.
- `openmontage/`: plan e instalador de OpenMontage para Windows (aparte).

## Guion — FÓRMULA DE CITRINO (del usuario, 20 nov 2026) — ver `docs/FORMULA-GUIONES-CITRINO.md`
- 8 etapas: 1 HOOK · 2 PROMESA · 3 RECOMPENSA 1 · 4 BUCLE 1 · 5 RECOMPENSA 2 · 6 BUCLE 2 · 7 CLÍMAX · 8 CTA (una sola acción).
- Columna vertebral, no jaula: más o menos bucles y recompensas según la duración. Valor desde el primer segundo.
- Cada segmento aporta información o curiosidad; primera recompensa rápido; interés que crece; sin bucles artificiales,
  anticipaciones repetidas ni relleno; narración fluida; toda promesa se resuelve.
- **No inventar tensión, datos ni revelaciones.** Datos reales comprobados en fuentes fiables.
- **Auditoría obligatoria** sobre 100 (gancho, promesa, recompensas, bucles, clímax, ritmo, CTA). Con < 90: buscar
  puntos de abandono y redundancias, reescribir lo débil y volver a auditar. Nunca entregar el primer borrador.
  Leerlo en voz alta: tiene que sonar natural.
- **Entrega (siempre, en este orden):** 1) guion por las 8 etapas; 2) auditoría y nota; 3) guion limpio para locución
  (bloque para copiar); 4) pausas, énfasis y ritmo; 5) fuentes.
- NO usar la fórmula de Benthara (misterio/rival) ni la de Zingo para Citrino.
- Canal en español. **La duración NO es fija: la marca la fórmula narrativa** (las 8 etapas con los bucles y
  recompensas que el tema necesite, sin relleno). Para estimarla antes de grabar:
  `python3 dibujos/herramientas/tiempos_estimados.py script.txt` (~170 palabras por minuto). Decirla en la entrega.
- De Zingo (ver `docs/LO-QUE-SIRVE-DE-ZINGO.md`): gancho en 0-3 s sin introducción; final que enlaza con el principio
  cuando encaje; la ciencia con una analogía de casa; cifras concretas que se puedan enseñar con un inserto.

## REGLAS DEL MOTOR DE DIBUJOS — ver `dibujos/LEEME.md`
- **Calidad = la del ejemplo de los romanos** (`dibujos/kit/example/`): misma especie de personaje, luz, piel, colores
  vivos y texturas pintadas. Comparar lado a lado (`dibujos/herramientas/comparar.py`) antes de montar.
- **Cada decorado se construye A MEDIDA del vídeo**, con las piezas del KIT y, si hace falta algo nuevo, en su mismo
  estilo. Solo se reutiliza algo si el guion o la voz lo mencionan. Cada vídeo, mejor que el anterior.
- **Gestos = los del kit**: caras fijas que cambian en la palabra clave, `idle()` siempre, impulso, asentir, negar,
  4-5 cambios de brazos por vídeo.
- Personajes: mismo cuerpo y cara del kit; solo cambia la ropa (OUTFITS en `web/roman.js`).
- **Encuadre:** personajes más pequeños o lejos para que se vea el entorno (ocupan ~1/3-1/2 de la altura). Caras a
  pantalla completa solo en 1-2 golpes clave y breves.
- **Revisar YO cada imagen** antes de enviarla. Nada en pantalla que no diga el guion.
- **Entregar dos versiones: con música y sin música, + la ficha para publicar.**

## Proceso de un vídeo
**NUNCA montar ni hacer un MP4 sin la autorización del usuario** (21 nov 2026), ni siquiera de prueba. Antes hace
falta su guion aprobado y su voz. Las pruebas del motor se hacen con fotos sueltas, no con vídeos.
**Orden única:** `./citrino` (sin nada, enseña la ayuda): `comprobar · temas · guion · video · voz · fotos · montar ·
terminar · publicar · medir`. Los pasos de abajo son lo que hace por dentro.
1. Guion con la fórmula de Citrino: `python3 guiones/citrino.py nuevo "Título"` → rellenar → `auditar` (≥ 90 y
   leído en voz alta) → aprobado → `python3 guiones/citrino.py texto guiones/<x>.json dibujos/videos/<nombre>/script.txt`. Voz del usuario → `voice.mp3`.
2. `cp -r dibujos/plantilla dibujos/videos/<nombre>` + `bash dibujos/herramientas/preparar.sh dibujos/videos/<nombre>`.
3. `python3 ../../herramientas/tiempos_es.py voice.mp3 script.txt es` (escribe `web/tiempos.js`).
   (sin voz todavía: `tiempos_estimados.py script.txt` para ir planificando).
4. Decorado (`web/_world.js`), ropa (`web/roman.js`), planos (`web/story.js`: un plano cada 2-3 s, zoom de golpe en
   cifras y revelaciones, insertos de datos cuando la voz dice una cifra) → `bash rebuild.sh` → `carta.mjs`.
5. Hoja de fotos + `comparar.py`, REVISARLA, corregir, enseñarla.
6. Montaje en segundo plano (`bash ../../herramientas/montar.sh 0-N`, en paralelo y reanudable) → `python3 audio.py` → `mix.py` con y sin música →
   `subtitulos.py` (siempre el `.srt` para subirlo) → `terminar.sh` dos veces (`SUBS=1` si se quieren quemados; estilo del usuario por defecto: una palabra, minúsculas, sin puntuación, tamaño medio, sin amarillo).
7. Revisar la hoja final, enviar los dos MP4.
8. **Siempre después de los MP4:** la ficha para publicar en bloques para copiar (título de 4-7 palabras, descripción
   con datos reales y hashtags, etiquetas, comentario fijado, ajustes de YouTube, hora recomendada, fuentes), en
   español, guardada en `dibujos/videos/<nombre>/publicar.md` (modelo: `dibujos/plantilla/publicar.md`).
9. **A los 2 días de publicar:** pedir la captura de YouTube Studio (Participación) y apuntarla en
   `docs/RESULTADOS.md` con el momento de abandono y su etapa del guion (para medir la fórmula).
10. Guardar y subir a la rama de trabajo según se avanza (sin esperar al final).

## Guardar siempre (límite de uso de 5 horas)
- No veo el contador del límite, así que **guardo y subo (commit + push) después de cada paso terminado**: guion,
  decorado, hoja de fotos aprobada, montaje, sonido, MP4. Así, si se corta, no se pierde nada.
- En renders largos, subir los avances (código y notas; los fotogramas no se suben, se rehacen con
  `montar.sh`, que salta los ya hechos).
- Tras un reinicio del entorno: `bash dibujos/herramientas/instalar.sh` (deja todo listo en ~1 minuto).
- Mantener al día la sección «Estado» de abajo: qué está hecho y cuál es el siguiente paso, para continuar en otro chat.

## Estado (actualizar en cada paso)
- 20 nov 2026: motor de dibujos portado y probado (calidad = romanos). Fórmula de Citrino guardada. Lo útil de Zingo
  pasado al motor.
- 21 nov 2026: auditor de guiones (`guiones/citrino.py`), instalador, montaje en paralelo, medición de resultados
  (`docs/RESULTADOS.md`) y banco de 15 ideas (`guiones/IDEAS.md`).
  Pendiente del usuario: cómo es Citrino (temas, público, español de México o España, tono, voz de ElevenLabs),
  subtítulos quemados o solo .srt, personaje fijo, pasar la rama a la principal, borrar el motor viejo de Zingo,
  análisis con vidIQ (cuesta créditos). Siguiente: el primer vídeo (tema del banco de ideas o del usuario).
- 21 nov 2026 (cierre del día): orden única `./citrino`, cortes atados a palabras, arreglo de `tiempos_es.py`, aviso si
  la voz no coincide, reparto de ejemplo neutro. Probado sin montar: tiempos de la voz, música, mezclas y subtítulos.
  Sin probar: el montaje final del MP4 (solo con permiso del usuario, con el primer vídeo).
- 23 nov 2026: PRIMER VÍDEO «¿Cuánto tardará GTA 6 Online?». Guion (base del usuario, corregido y con fuentes) en
  `guiones/cuanto-tardara-gta-6-online.json`, auditoría 100/100, ~67 s. Esperando el «sí» del usuario al guion.
  Siguiente: el usuario graba `voice.mp3` → `./citrino video gta6-online guiones/cuanto-tardara-gta-6-online.json` y `./citrino voz gta6-online`.
  Datos del canal: por decidir.
  Imágenes del usuario (usar tal cual) en `guiones/recursos/gta6-online/`. Este vídeo va SIN presentador: gráficos,
  insertos y sus imágenes. Pendiente: cuál es «la miniatura» y si se recorta el fondo de cuadritos del logo.

## Créditos de vidIQ
NUNCA gastar créditos de vidIQ sin decir el coste y esperar el «sí» del usuario.
