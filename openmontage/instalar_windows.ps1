# Instalación de OpenMontage en Windows, sin servicios de pago y sin GPU local.
# No crea cuentas, no guarda claves y bloquea cualquier gasto hasta que lo autorices.
# Uso (PowerShell normal, en la carpeta donde quieras instalarlo):
#   powershell -ExecutionPolicy Bypass -File .\instalar_windows.ps1
$ErrorActionPreference = "Stop"

function Falta($cmd) { -not (Get-Command $cmd -ErrorAction SilentlyContinue) }

# PowerShell no se detiene solo cuando falla un programa externo (pip, npm...): esto lo hace.
function Ejecutar([string]$desc, [scriptblock]$bloque) {
  & $bloque
  if ($LASTEXITCODE -ne 0) { throw "Falló: $desc (código $LASTEXITCODE). Copia el error y pégalo en Claude Code." }
}

Write-Host "==> 1/6 Programas base (winget). Si alguno ya está instalado, se salta."
if (Falta "winget") { throw "No hay winget. Instala 'App Installer' desde Microsoft Store y vuelve a ejecutar." }
$ids = @{ git = "Git.Git"; py = "Python.Python.3.11"; node = "OpenJS.NodeJS.LTS"; ffmpeg = "Gyan.FFmpeg" }
$nuevo = $false
foreach ($cmd in "git", "py", "node", "ffmpeg") {
  if (Falta $cmd) {
    Ejecutar "instalar $cmd" { winget install --id $ids[$cmd] -e --accept-source-agreements --accept-package-agreements }
    $nuevo = $true
  }
}
if ($nuevo) {
  Write-Host "   Se instalaron programas nuevos. Cierra PowerShell, ábrelo otra vez y ejecuta este script de nuevo."
  exit 0
}

Write-Host "==> 2/6 Descargando OpenMontage"
if (-not (Test-Path "OpenMontage")) { Ejecutar "git clone" { git clone https://github.com/OpenMontageInc/OpenMontage.git } }
Set-Location OpenMontage

Write-Host "==> 3/6 Entorno de Python y dependencias (sin GPU: NO se usa requirements-gpu.txt)"
if (-not (Test-Path ".venv")) { Ejecutar "crear .venv" { py -3.11 -m venv .venv } }
. .\.venv\Scripts\Activate.ps1
Ejecutar "actualizar pip" { python -m pip install "pip>=26.2.2" }
Ejecutar "requirements.txt" { python -m pip install -r requirements.txt }
Ejecutar "piper-tts" { python -m pip install piper-tts }

Write-Host "==> 4/6 Compositor de video (Remotion)"
Push-Location remotion-composer
npm install
if ($LASTEXITCODE -ne 0) {
  Write-Host "   npm install falló; reintentando con npx (problema conocido de npm en Windows)"
  Ejecutar "npm install (npx)" { npx --yes npm install }
}
Pop-Location

Write-Host "==> 5/6 Voz gratuita en español (Piper, sin conexión)"
$voces = Join-Path $HOME ".piper\models"
New-Item -ItemType Directory -Force -Path $voces | Out-Null
Ejecutar "descargar voz" { python -m piper.download_voices --download-dir $voces es_MX-claude-high }

Write-Host "==> 6/6 Configuración: gastos bloqueados y formato vertical"
if (-not (Test-Path ".env")) { Copy-Item .env.example .env }
$cfg = Get-Content config.yaml -Raw
$cfg = $cfg -replace "mode: warn", "mode: cap"
$cfg = $cfg -replace "total_usd: 10\.00", "total_usd: 0.00"
$cfg = $cfg -replace "single_action_approval_usd: 0\.50", "single_action_approval_usd: 0.00"
$cfg = $cfg -replace 'default_resolution: "1920x1080"', 'default_resolution: "1080x1920"'
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "config.yaml"), $cfg, (New-Object System.Text.UTF8Encoding $false))
if ((Get-Content config.yaml -Raw) -notmatch "total_usd: 0\.00") { throw "No se pudo fijar el presupuesto en 0. No sigas: avísame." }
Write-Host "   config.yaml: presupuesto 0 USD en modo 'cap', aprobación para cualquier acción de pago, 1080x1920."
Write-Host "   Para autorizar gasto, sube 'total_usd' tú mismo (por ejemplo a 5.00)."

Write-Host "`n==> Prueba corta sin claves ni costo"
Ejecutar "registro de herramientas" { python -c "from tools.tool_registry import registry; registry.discover(); m=registry.provider_menu(); [print(f'{k:26s}', ', '.join(t['name'] for t in v['available'])[:90]) for k,v in sorted(m.items()) if isinstance(v,dict) and 'available' in v]" }
Ejecutar "render de prueba" { python render_demo.py animated-reel-20s }
Write-Host "`nListo. Abre la carpeta OpenMontage en Claude Code."
