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

## Escala de referencia
El mundo 3D está en metros y el personaje mide 1,75 m. Para que un objeto pequeño se vea grande, acerca la cámara (encuadre `macro` o `detalle`) en vez de inflar el `escala` del prop.

| Objeto | Alto a `escala` 1 | `escala` recomendada | Alto en escena | Comentario |
|---|---|---|---|---|
| Personaje | 1,75 m | 1 | 1,75 m | referencia |
| Sofá (`sofa`) | 1,15 m (asiento 0,45) | 1 | 1,15 m | |
| Gato (`gato`) | 0,35 m | 1,15 | 0,40 m | un gato real mide ~0,25 m a la cruz, ~0,40 con orejas: le llega a la rodilla |
| Caca (`caca`) | 0,39 m | 0,45 | 0,18 m | ~3 veces su tamaño real, para que se lea; menos de la mitad del gato |
| Casa (`casa`) | 4,6 m | 1 | 4,6 m | |
| Portaaviones (`portaaviones`) | 23 m de cubierta, 342 m de eslora | 1 | escala real | se coloca con `pos` en metros |

Encuadres: `macro` (cámara a 1,5 m, a ras de suelo) para mascotas y objetos; `detalle` (2,4 m); `medio` (4,8 m); `general` (10,5 m).
