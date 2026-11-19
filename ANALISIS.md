# Análisis del canal @soyzingo ("Zingo")

Datos de vidIQ y de las transcripciones de los 10 Shorts publicados (nov 2026).

## Números
- Canal de México, en español. Primer video el 9 de nov de 2026.
- 10 Shorts y 9,56 M de vistas en 10 días: unas 950 mil por video. 8.390 suscriptores.
- Top: "¿Por qué este agricultor combatió la helada con hielo?" con 4,76 M; "…apuñaló su heno?" con 1,89 M; "¿Para qué pintan los árboles de blanco?" con 1,45 M en 2 días.
- 1 Short diario. Todos duran entre 1:06 y 1:10. Se publican entre las 15:00 y las 21:40 UTC.
- Pocos comentarios (≈0,01%): la gente lo ve completo y lo vuelve a ver, pero casi no comenta. El algoritmo lo empuja por la retención.

## La fórmula (el arco se repite en los 10 videos)
| % del video | Beat | Ejemplo real |
|---|---|---|
| 0-6% | **Gancho**: una acción absurda contra lo que hacen todos | "Cubrió sus naranjas de hielo mientras todo el valle prendía fogatas" |
| 4-10% | **Burla con apodo**: el mote nace de la acción | "Oye, heladero…", "¿Cómo sigue el paciente, doctor?", "Fosforito" |
| 8-22% | **Apuesta** con números concretos | "Cuatro horas a dos bajo cero y adiós cosecha" |
| 15-35% | **Rival** que hace lo obvio, caro o de fuerza bruta, y presume | El vecino con la carreta de leña, o con las llantas más anchas |
| 25-50% | **Proceso casero** con objetos humildes | Latas agujereadas, una ramita en la válvula, un cartón |
| 35-68% | **Escalada**: una cuenta regresiva cantada | "35 libras, 25, 15", "menos uno, menos dos" |
| 50-72% | **Giro**: el plan del rival se cae | Se acaba la leña y queman la cerca |
| 66-82% | **"El truco es que…" / "¿Por qué?"**: ciencia con una analogía de casa | "Tacón contra chancla", "camisa negra contra sombrero" |
| 80-94% | **Desenlace**: el rival pierde | El valle entero le compra naranjas |
| 92-100% | **Remate**: callback irónico con el apodo | "Sanito", "La almendra partió el cascanueces", "le pide fuego a Fosforito" |

Otros rasgos:
- El protagonista no tiene nombre. Si es histórico (Nansen, John Snow), el nombre aparece tarde, como premio.
- Siempre es una historia o un fenómeno real: calor latente, combustión del heno, presión, cal, el estudio de los ojos pintados en vacas.
- Unas 180 palabras, sin introducción y sin pedir la suscripción. El último plano a veces enlaza con el primero para que el video haga loop.
- Títulos: "¿Por qué este [oficio] [acción absurda]?" o una frase-objeto ("Vacas con ojos en el trasero").

## Producción
- **Gráficos**: personajes 2D de palito con cabeza blanca redonda y contorno negro grueso, que se distinguen por el sombrero y la ropa. Van pegados como billboards sobre escenarios **3D low-poly** con sombreado toon, sombras suaves, niebla, cielo degradado y el fondo desenfocado.
- **Cámara**: entre 22 y 32 cortes por minuto (un plano cada 2-3 s). Usa push-in en la tensión, crash zoom en burlas y revelaciones, paneos o tilts para mostrar la amenaza, sacudida cuando algo colapsa y planos detalle de termómetros y manómetros.
- **Datos en pantalla**: termómetros, manómetros y diagramas animados mientras el narrador canta las cifras.
- **Subtítulos**: 1 o 2 palabras a la vez, sans-serif muy gruesa, blanca con contorno negro, en el tercio inferior.
- **Audio**: narrador masculino rápido (~170-180 ppm, sin aire), música de "storytelling" bajo la voz y SFX en cada acción (whoosh, hielo, fuego, motor).

## Cómo lo replica este motor
| Elemento | Archivo |
|---|---|
| Fórmula, métricas y reglas | `motor/formula.py` |
| Guionista con Claude más ronda de corrección contra la fórmula | `motor/guion.py`, `motor/validar.py` |
| Escenarios 3D low-poly (three.js): terreno, pasto instanciado, sombras, niebla y 28 props | `motor/escena3d/escena.js` |
| Personajes 2D: 12 expresiones, 18 poses, 11 sombreros, ropa y objetos en mano | `motor/personajes.py` |
| Cámara 3D: push-in, pull-out, pan, tilt, crash zoom, sacudida, seguimiento, órbita y whip | `motor/camara3d.py` |
| Insertos animados: termómetro, manómetro, contador, reloj, comparativa, flechas y capas | `motor/efectos.py` |
| Voz con tiempos por palabra, música procedural, SFX y ducking | `motor/audio.py` |

Mejoras sobre el original: el validador puntúa cada guion contra la fórmula antes de renderizar, las voces de los personajes son distintas a la del narrador, la marea, el fuego, el humo y las banderas están animados en 3D, y se genera un `.srt` para subir subtítulos aparte.
