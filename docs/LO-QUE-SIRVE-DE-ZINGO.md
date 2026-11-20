# Lo que nos sirve del canal y del motor de Zingo
El motor anterior de este repo (Shorts 3D low-poly que copiaban la fórmula del canal @soyzingo: `motor/`, `ejemplos/`,
`ANALISIS.md`) ya no se usa: los vídeos de Citrino se hacen con el motor de dibujos (`dibujos/`) y la fórmula de
Citrino (`docs/FORMULA-GUIONES-CITRINO.md`). Esto es lo que se ha sacado de Zingo:

## Pasado al motor de dibujos
| De Zingo | Dónde está ahora |
|---|---|
| Insertos de datos animados (termómetro, manómetro, contador, reloj, comparativa, barra, capas) | `dibujos/plantilla/web/insertos.js` + `inserto()` en `story.js` |
| Subtítulos de 1-2 palabras, letra muy gruesa, cifras en amarillo, tercio inferior + `.srt` | `dibujos/herramientas/subtitulos.py` (`SUBS=1` en `terminar.sh` para quemarlos) |
| Tiempos estimados sin voz (~170 ppm) | `dibujos/herramientas/tiempos_estimados.py` (planificar y estimar la duración antes de grabar) |

## Lecciones de retención y producción (datos reales de @soyzingo, nov 2026: 10 Shorts, 9,56 M de vistas en 10 días)
- **Gancho en 0-3 s**, sin introducción («hoy te cuento») y sin pedir la suscripción. Encaja con el HOOK de Citrino.
- **Siempre algo real**: historia o fenómeno comprobable. Igual que en Citrino: no inventar.
- **Un plano cada 2-3 s** (22-32 cortes por minuto). Push-in en la tensión, **zoom de golpe en revelaciones y cifras**,
  sacudida cuando algo se rompe, planos detalle de los aparatos que dan datos.
- **Las cifras se ven mientras se dicen** (insertos) y se resaltan en amarillo en los subtítulos.
- **Narrador rápido** (~170-180 palabras por minuto, sin aire), música bajo la voz y un efecto de sonido en cada acción.
- **Final que enlaza con el principio** (loop): la última frase se completa con la primera.
- **La ciencia con una analogía de casa** (una o dos frases).
- Pocos comentarios (≈0,01 %) pero mucha retención. Para pedir comentarios: el comentario fijado con una pregunta.
- **Títulos** cortos y con curiosidad: «¿Por qué este [oficio] [hizo algo absurdo]?», «¿Para qué [hacen X]?» o una
  frase-objeto («Vacas con ojos en el trasero»).
- **Publicación**: 1 Short al día; Zingo publicaba entre las 15:00 y las 21:40 UTC (mejor 16:00-19:00 UTC =
  10:00-13:00 en México).

## No se usa para Citrino
- La fórmula de Zingo (gancho, burla con apodo, apuesta, rival, escalada…) y su duración fija de 66-70 s: **en Citrino
  la duración la marca la fórmula narrativa** (las 8 etapas, con los bucles y recompensas que el tema necesite).
- El guionista automático con la API, los escenarios low-poly, los personajes hechos con cairo y la voz edge-tts.
