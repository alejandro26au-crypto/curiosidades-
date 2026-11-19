# Motor de Shorts de curiosidades

Genera Shorts verticales (1080x1920, ~66 s) con la fórmula analizada en [ANALISIS.md](ANALISIS.md): guion → voz → escenario 3D low-poly → personajes 2D → cámara → subtítulos → MP4.

## Instalación
```bash
pip install -r requirements.txt
```
```bash
npm install
```
```bash
npx playwright install chromium
```
También necesitas `ffmpeg` y la fuente **Inter** (Inter Black) instalados. Si tu sistema bloquea certificados, edge-tts necesita salida a `speech.platform.bing.com`.

Para generar guiones hace falta `ANTHROPIC_API_KEY` (usa `claude-opus-5-5`; se cambia con `MOTOR_MODELO`).

## Uso
```bash
python -m motor todo "un pescador que enterró su pesca en la arena para conservarla" --investigar
```
Los pasos por separado:
```bash
python -m motor guion "tema" --investigar -o guiones/mi_video.json
```
```bash
python -m motor validar guiones/mi_video.json
```
```bash
python -m motor render guiones/mi_video.json --preview
```
```bash
python -m motor render guiones/mi_video.json --musica mi_pista.mp3
```
```bash
python -m motor ideas -n 20
```
- `--preview` renderiza a 540x960 (unas 4 veces más rápido).
- `--max-seg 10` corta un clip de muestra.
- `--sin-voz` usa tiempos estimados y deja la pista muda, por si vas a doblar con tu propia voz.

Sale `salida/<nombre>.mp4` junto con su `.srt`.

## Editar a mano
El guion es un JSON legible (mira `ejemplos/lechero.json`): cada plano lleva su frase, el escenario, los actores (expresión, pose, objeto), la cámara, un inserto de datos, efectos y SFX. Si cambias algo y vuelves a renderizar, la voz ya generada se reutiliza desde caché.

## Modelos 3D
`motor/escena3d/modelos/` trae 90 modelos low-poly CC0 de Quaternius, Kenney y KayKit: árboles, casas, molino, pozo, mercado, iglesia, tractor, camiones, barriles, costales, animales, cerros y montañas. `catalogo.json` relaciona cada tipo de prop del guion (`casa`, `molino`, `pozo`, `tractor`, `perro`, `venado`…) con sus modelos, y cada lugar con su ambientación de fondo. Para usar un modelo concreto, pon `"modelo": "kk_home_B"` en el prop. Las licencias están en `modelos/LICENCIAS.md`.

## Rendimiento
Los fondos 3D se renderizan en Chromium. Sin GPU (SwiftShader) tarda unos 18 s por segundo de video en 1080p. En una PC con GPU va mucho más rápido.
