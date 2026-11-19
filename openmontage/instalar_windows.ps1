# Instalación de OpenMontage en Windows, sin servicios de pago.
# No crea cuentas, no guarda claves y bloquea cualquier gasto hasta que lo autorices.
# Uso (PowerShell normal, en la carpeta donde quieras instalarlo):
#   powershell -ExecutionPolicy Bypass -File .\instalar_windows.ps1
$ErrorActionPreference = "Stop"

function Falta($cmd) { -not (Get-Command $cmd -ErrorAction SilentlyContinue) }

Write-Host "==> 1/6 Programas base (winget). Si alguno ya está instalado, se salta."
if (Falta "git")    { winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements }
if (Falta "py")     { winget install --id Python.Python.3.11 -e --accept-source-agreements --accept-package-agreements }
if (Falta "node")   { winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements }
if (Falta "ffmpeg") { winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements }
Write-Host "   Si se instaló algo nuevo, cierra y vuelve a abrir PowerShell y ejecuta este script otra vez."
if ((Falta "git") -or (Falta "py") -or (Falta "node") -or (Falta "ffmpeg")) { exit 0 }

Write-Host "==> 2/6 Descargando OpenMontage"
if (-not (Test-Path "OpenMontage")) { git clone https://github.com/OpenMontageInc/OpenMontage.git }
Set-Location OpenMontage

Write-Host "==> 3/6 Entorno de Python y dependencias (sin GPU: se usan modelos en la nube)"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "pip>=26.2.2"
python -m pip install -r requirements.txt
python -m pip install piper-tts

Write-Host "==> 4/6 Compositor de video (Remotion)"
Push-Location remotion-composer
try { npm install } catch { npx --yes npm install }
Pop-Location
npx --yes hyperframes --version | Out-Null

Write-Host "==> 5/6 Voz gratuita en español (Piper, sin conexión)"
$voces = Join-Path $HOME ".piper\models"
New-Item -ItemType Directory -Force -Path $voces | Out-Null
python -m piper.download_voices --download-dir $voces es_MX-claude-high

Write-Host "==> 6/6 Configuración: gastos bloqueados hasta tu autorización"
if (-not (Test-Path ".env")) { Copy-Item .env.example .env }
$cfg = Get-Content config.yaml -Raw
$cfg = $cfg -replace "mode: warn", "mode: cap"
$cfg = $cfg -replace "total_usd: 10.00", "total_usd: 0.00"
$cfg = $cfg -replace "single_action_approval_usd: 0.50", "single_action_approval_usd: 0.00"
$cfg = $cfg -replace 'default_resolution: "1920x1080"', 'default_resolution: "1080x1920"'
Set-Content config.yaml $cfg -Encoding UTF8
Write-Host "   config.yaml: presupuesto 0 USD en modo 'cap' y aprobación para cualquier acción de pago."
Write-Host "   Para autorizar gasto, sube 'total_usd' tú mismo (por ejemplo a 5.00)."

Write-Host "`n==> Prueba corta sin claves ni costo"
python -c "from tools.tool_registry import registry; registry.discover(); m=registry.provider_menu(); [print(f'{k:26s}', ', '.join(t['name'] for t in v['available'])[:90]) for k,v in sorted(m.items()) if isinstance(v,dict) and 'available' in v]"
python render_demo.py animated-reel-20s
Write-Host "`nListo. Abre la carpeta OpenMontage en Claude Code."
