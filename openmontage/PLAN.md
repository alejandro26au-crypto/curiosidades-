# OpenMontage como estudio de producción

Análisis del repositorio `OpenMontageInc/OpenMontage` (commit `2e003e6`, 15 nov 2026) y prueba de instalación hecha en la nube el 19 nov 2026.

## 1. Qué es
Un "estudio" que corre dentro de Claude Code. No es una app con botones: Claude sigue sus guías (`AGENT_GUIDE.md` y `skills/`) y produce cada video por etapas (investigación → propuesta → guion → plan de escenas → assets → edición → composición). En los puntos creativos se detiene a pedirte aprobación. Trae más de 100 herramientas que se activan según las claves de API que pongas en `.env`.

- **Licencia:** AGPL-3.0. Los videos que produzcas son tuyos. La AGPL solo te obliga si modificas el software y lo ofreces como servicio a terceros.

## 2. Requisitos
| | Mínimo | Tu caso (portátil Dell) |
|---|---|---|
| Sistema | Windows 10/11, macOS o Linux | Windows: soportado (comandos PowerShell en el README) |
| Python | 3.10+ (el repo fija 3.11) | se instala con `winget` |
| Node.js | 22.23.4+ | se instala con `winget` |
| FFmpeg | cualquiera reciente | se instala con `winget` |
| RAM | 8 GB (16 recomendado) | por confirmar con `diagnostico_windows.ps1` |
| Disco | ~2 GB de instalación + ~1 GB por proyecto | por confirmar |
| GPU | **no hace falta** con modelos en la nube | solo se usaría para video local (WAN/Hunyuan), que no vamos a usar |
| Blender | opcional (ruta 3D "production", pesada) | no instalar por ahora |

Particularidades de Windows, según el propio repo:
- No hay `make`: se usan los comandos de PowerShell. `instalar_windows.ps1` ya los trae.
- Si `npm install` falla con `ERR_INVALID_ARG_TYPE`, se usa `npx --yes npm install`. El script lo hace solo.
- En el filtro de subtítulos de FFmpeg las rutas se escriben `C\:`. Las herramientas del repo ya lo manejan.

## 3. Servicios externos
**Gratis, sin tarjeta:**
- **Piper:** voz en español sin conexión. Probada con `es_MX-claude-high` y funciona.
- **Pexels, Pixabay y Unsplash:** claves gratuitas para imágenes, video y música de archivo.
- **Google API key:** TTS con 1 M de caracteres al mes gratis (unos 900 Shorts).
- **ElevenLabs:** plan gratuito de 10 mil caracteres al mes (unos 9 Shorts). Voz premium y SFX.

**De pago por uso (no hay suscripción; recomiendo una sola cuenta):**
- **fal.ai** (`FAL_KEY`): una clave da acceso a:
  - Imágenes: Nano Banana Pro (edición con referencia, clave para personajes consistentes), FLUX, Seedream y Recraft.
  - Video: Kling y WAN (imagen → video).
  - Modelos 3D (`fal_3d`).
  - No tiene plan gratuito; pagas solo lo que usas.

**Opcionales más adelante:** Kling oficial, Runway, Suno (música), Higgsfield (Soul ID para consistencia de personaje).

## 4. Prioridad nube para no cargar tu portátil
En tu Dell queda lo liviano: Claude Code, FFmpeg, Remotion o HyperFrames para componer y Piper para la voz. Lo pesado (generar imágenes, animar planos, voces premium) se hace en la nube. Queda descartado:
- `make install-gpu` y el video local (WAN, Hunyuan, CogVideo, LTX).
- Stable Diffusion local.
- La ruta Blender "production".

## 5. Cómo se arma el estilo del canal
| Necesitas | Herramienta en OpenMontage | Costo |
|---|---|---|
| **Personajes ilustrados consistentes** | 1) Diseñas tu personaje una vez (hoja de personaje) con Nano Banana Pro o Seedream. 2) Cada plano se genera **editando con esa imagen de referencia**, así se mantiene igual. Alternativa gratis: pipeline `character-animation` (rig SVG, poses y expresiones), que es lo más parecido a los monitos 2D | ~0,04-0,07 USD/imagen · rig SVG: 0 |
| **Escenarios 3D low-poly** | En la imagen generada, con estilo fijo ("3D low-poly, cel-shaded, soft light…") guardado como estilo en `styles/custom/`. Alternativa gratis: `threejs_world` más catálogos de modelos (`threejs_asset_catalog`), como mi motor | ~0,04 USD/imagen · Three.js: 0 |
| **Animación de cada plano** | Imagen → video con Kling 2.5 Turbo o WAN 2.5 (vía fal) para los planos clave; el resto con movimiento de cámara de Remotion (push-in, paneo) | 0,05-0,07 USD/s · Remotion: 0 |
| **Gráficos animados** (termómetros, contadores) | Remotion (tarjetas de datos, gráficos) o HyperFrames/GSAP | 0 |
| **Voz** | Piper (gratis) → ElevenLabs o Google TTS para mejor calidad | 0 con planes gratuitos |
| **Subtítulos palabra por palabra** | `remotion_caption_burn` / `subtitle_gen` | 0 |
| **Música y SFX** | Pixabay Music (gratis) / ElevenLabs SFX | 0 |

**Costo estimado por Short de 66 s (~25 planos):**
- Económico: 25 imágenes y solo 8 planos animados con IA ≈ **2-3 USD**.
- Completo: 25 imágenes y 25 planos animados de 3 s ≈ **5-6 USD**.

Son estimaciones con los precios publicados en `docs/PROVIDERS.md`. OpenMontage calcula el costo real antes de cada llamada.

## 6. Control de gastos (tu condición)
`instalar_windows.ps1` deja `config.yaml` así:
```yaml
budget:
  mode: cap                      # límite estricto
  total_usd: 0.00                # nada de gasto hasta que tú lo subas
  single_action_approval_usd: 0.00
  require_approval_for_new_paid_tool: true
```
Lo verifiqué en `tools/cost_tracker.py`: con estos valores las herramientas gratuitas funcionan y **cualquier llamada con costo mayor a 0 se detiene a pedir aprobación**. Además, el script no crea cuentas ni escribe claves. Las claves las pones tú en `.env` cuando decidas.

## 7. Prueba corta (hecha en la nube, sin claves y sin costo)
- La instalación de Python y Remotion funcionó; el script de Windows usa los mismos pasos.
- El registro de herramientas encontró 10 capacidades sin claves:
  - Voz Piper.
  - Mundos 3D Three.js.
  - Animación de personajes con rig (5 herramientas).
  - Subtítulos.
  - Composición.
  - Música de Pixabay.
  - Análisis y control de calidad.
- Render de prueba `animated-reel-20s`: video de 21 s (2,1 MB) generado en 2 min 22 s sin GPU.
- Voz en español con Piper (`es_MX-claude-high`): funciona.

## 8. Pasos en tu Windows
1. Ejecutar `diagnostico_windows.ps1` y pegarme el resultado.
2. Ejecutar `instalar_windows.ps1`, que repite la prueba corta al final.
3. Abrir la carpeta `OpenMontage` en Claude Code y pedir el primer Short **gratis**: pipeline `character-animation`, voz Piper, sin claves.
4. Si me autorizas, crear la cuenta de fal.ai con un tope bajo (por ejemplo 5 USD) para probar personajes consistentes con Nano Banana Pro. Antes de empezar, tú subes `total_usd`.
