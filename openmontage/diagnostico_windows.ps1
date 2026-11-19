# Diagnóstico de compatibilidad con OpenMontage (solo lee, no instala ni cambia nada).
# Uso, en PowerShell:  powershell -ExecutionPolicy Bypass -File .\diagnostico_windows.ps1
$ErrorActionPreference = "SilentlyContinue"
function Fila($nombre, $valor, $ok) {
  $marca = if ($ok -eq $true) { "[OK] " } elseif ($ok -eq $false) { "[X]  " } else { "[--] " }
  Write-Host ("{0}{1,-22} {2}" -f $marca, $nombre, $valor)
}
function Version($cmd, $arg = "--version") {
  $c = Get-Command $cmd -ErrorAction SilentlyContinue
  if (-not $c) { return $null }
  return (& $cmd $arg 2>&1 | Select-Object -First 1).ToString().Trim()
}

Write-Host "`n=== Equipo ==="
$so = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
$modelo = (Get-CimInstance Win32_ComputerSystem).Model
Fila "Modelo" $modelo $null
Fila "Windows" "$($so.Caption) build $($so.BuildNumber)" ([int]$so.BuildNumber -ge 19041)
Fila "CPU" "$($cpu.Name) ($($cpu.NumberOfLogicalProcessors) hilos)" ($cpu.NumberOfLogicalProcessors -ge 4)
Fila "RAM" "$ram GB (mínimo 8, ideal 16)" ($ram -ge 8)
$disco = Get-PSDrive -Name C
Fila "Disco C: libre" ("{0} GB (necesitas ~10 GB)" -f [math]::Round($disco.Free / 1GB, 1)) ($disco.Free -gt 10GB)
foreach ($g in Get-CimInstance Win32_VideoController) {
  $vram = if ($g.AdapterRAM -gt 0) { [math]::Round($g.AdapterRAM / 1GB, 1) } else { "?" }
  Fila "GPU" "$($g.Name) ($vram GB reportados)" $null
}
$nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidia) {
  $v = (nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1 | Select-Object -First 1)
  Fila "NVIDIA (CUDA)" $v $true
} else {
  Fila "NVIDIA (CUDA)" "no hay: se usan modelos en la nube (es lo recomendado)" $null
}

Write-Host "`n=== Software que necesita OpenMontage ==="
$py = Version "py" "-3 --version"; if (-not $py) { $py = Version "python" }
Fila "Python 3.10+ (ideal 3.11)" ($(if ($py) { $py } else { "no instalado" })) ([bool]($py -match "3\.(1[0-9])"))
$node = Version "node" "--version"
Fila "Node.js 22.23.4+" ($(if ($node) { $node } else { "no instalado" })) ([bool]($node -match "^v(2[2-9]|[3-9][0-9])"))
$npm = Version "npm" "--version"; Fila "npm" ($(if ($npm) { $npm } else { "no instalado" })) ([bool]$npm)
$ff = Version "ffmpeg" "-version"; Fila "FFmpeg" ($(if ($ff) { $ff.Substring(0, [math]::Min(40, $ff.Length)) } else { "no instalado" })) ([bool]$ff)
$git = Version "git"; Fila "Git" ($(if ($git) { $git } else { "no instalado" })) ([bool]$git)
$claude = Version "claude"; Fila "Claude Code" ($(if ($claude) { $claude } else { "no instalado" })) ([bool]$claude)
$winget = Version "winget"; Fila "winget" ($(if ($winget) { $winget } else { "no disponible" })) ([bool]$winget)
$make = Get-Command make -ErrorAction SilentlyContinue
Fila "make" ($(if ($make) { "sí" } else { "no (normal en Windows; se usan comandos PowerShell)" })) $null
$lp = (Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled).LongPathsEnabled
Fila "Rutas largas" ($(if ($lp -eq 1) { "activadas" } else { "desactivadas (recomendado activarlas)" })) ($lp -eq 1)
$blender = Get-ChildItem "C:\Program Files\Blender Foundation" -ErrorAction SilentlyContinue
Fila "Blender (opcional)" ($(if ($blender) { ($blender | Select-Object -First 1).Name } else { "no (no hace falta para empezar)" })) $null

Write-Host "`nCopia todo este texto y pégalo en Claude Code para revisar los resultados.`n"
