# Canal de Shorts de curiosidades: estado y forma de trabajar

## Estado (20 nov 2026)
- Rama de trabajo: `claude/relaxed-edison-8g6r1a`.
- **Vídeo 1 entregado: fresas** (`guiones/fresas.json`, puesta en escena en `guiones/fresas_planos.py`,
  voces en `voces/fresas/`). Réplica con fresas del Short viral de las naranjas (youtube.com/shorts/iD4fjW7Emt8).
  Render final: `python -m motor render guiones/fresas.json` → 1080x1920, 70,6 s.
- **Próximo vídeo: tema por decidir.** Al empezar, preguntar al usuario el tema o el vídeo a replicar.
- El usuario está en Windows 10 1909: debe actualizar (22H2 u 11) antes de instalar OpenMontage
  (`openmontage/instalar_windows.ps1`). Mientras tanto todo se produce en la nube con este motor.

## Reglas del usuario
- No contratar servicios ni gastar créditos sin permiso explícito (vidIQ cobra: transcripción 5,
  ver Short 10; decir el costo y esperar "sí").
- Priorizar la nube; nada de GPU local.
- Hablarle en español, sencillo y paso a paso.

## Flujo para un vídeo nuevo
1. Tema / vídeo de referencia. Si es un vídeo, con permiso: `vidiq_video_transcript` (texto) y
   `vidiq_watch_shortform_content` (acciones plano a plano). YouTube bloquea yt-dlp desde la nube.
2. Guion con la fórmula de `motor/formula.py` (validar: `python -m motor validar guiones/x.json`, objetivo 100/100).
   Narración con palabras propias, no copiar el texto literal del original.
3. Puesta en escena en un script `guiones/x_planos.py` (como `fresas_planos.py`): acciones de personajes,
   objetos en mano, primeros planos 3D de la fruta/objeto, tarjetas de datos solo donde no tapen caras
   (`posicion: "der"/"izq"` = tarjeta pequeña en esquina cuando hay personajes).
4. Voces: el usuario las genera en ElevenLabs (modelo Eleven v3 con etiquetas [burlón], [se ríe]…; un audio
   del narrador y uno por personaje, en el orden del guion). Darle los bloques listos para pegar.
   Luego: `python -m motor doblar guiones/x.json --voz narrador=n.mp3 --voz vecino=v.mp3 --acelerar 1.18`
   (ajustar `--acelerar` para que dure 64-70 s).
5. Fotogramas de prueba con `render.renderizar(..., preview=True, solo_frame=t)`, revisar, y render final.
   Sin GPU tarda ~17 min el final y ~8 min la vista previa (`--preview`).
6. Entregar con título, descripción, hashtags y hora (Colombia: 11:00-14:00, ideal 12:00).

## Notas técnicas
- edge-tts y otras descargas: exportar `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt` en este entorno.
- Lo que más le gustó al usuario: acciones calcadas del original, fruta partida en 3D, fila del mercado,
  texturas pintadas (como el vídeo del pirata del repo Oceano-animado-), iluminación actual.
- No le gustó: voces de edge-tts (planas), tarjetas que tapan caras, objetos quietos, cajas animadas solas.
