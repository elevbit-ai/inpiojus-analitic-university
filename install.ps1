# =====================================================================
#  InpioJus Analitic University — Instalador / Installer (PowerShell)
#  Autor / Author: Joaquim Pedro de Morais Filho <j360074@hotmail.com>
#
#  Instalação em uma linha / One-line install:
#    irm https://elevbit-ai.github.io/inpiojus-analitic-university/install.ps1 | iex
# =====================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  +==============================================+" -ForegroundColor Cyan
Write-Host "  |   InpioJus Analitic University - Instalador   |" -ForegroundColor Cyan
Write-Host "  |   por Joaquim Pedro de Morais Filho           |" -ForegroundColor Cyan
Write-Host "  +==============================================+" -ForegroundColor Cyan
Write-Host ""

# 1. Python -----------------------------------------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Host "  [!] Python 3.9+ nao encontrado / not found." -ForegroundColor Yellow
    Write-Host "      winget install Python.Python.3.12" -ForegroundColor Yellow
    return
}
Write-Host "  [ok] $(& $python.Source --version)" -ForegroundColor Green

# 2. Dependencias / dependencies --------------------------------------
Write-Host "  [..] Instalando dependencias (opencv-python, numpy, pynput)..."
& $python.Source -m pip install --quiet --upgrade opencv-python numpy pynput 2>&1 | Out-Null
Write-Host "  [ok] Dependencias instaladas / dependencies installed." -ForegroundColor Green

# 3. Download do pacote / package download ----------------------------
$destino = Join-Path $env:LOCALAPPDATA "InpioJusUniversity"
$zipUrl  = "https://github.com/elevbit-ai/inpiojus-analitic-university/archive/refs/heads/main.zip"
$zipTmp  = Join-Path $env:TEMP "inpiojus-university-main.zip"

Write-Host "  [..] Baixando do GitHub / downloading..."
Invoke-WebRequest -Uri $zipUrl -OutFile $zipTmp -UseBasicParsing

if (Test-Path $destino) { Remove-Item $destino -Recurse -Force }
New-Item -ItemType Directory -Force $destino | Out-Null
$extracao = Join-Path $env:TEMP "iju-extract"
if (Test-Path $extracao) { Remove-Item $extracao -Recurse -Force }
Expand-Archive -Path $zipTmp -DestinationPath $extracao -Force
$raiz = Get-ChildItem $extracao -Directory | Select-Object -First 1
Copy-Item -Path (Join-Path $raiz.FullName "*") -Destination $destino -Recurse -Force
Remove-Item $zipTmp, $extracao -Recurse -Force
Write-Host "  [ok] Instalado em / installed at $destino" -ForegroundColor Green

# 4. Comando no perfil / command in profile ---------------------------
$marcador = "# --- InpioJus Analitic University ---"
$funcao = @"

$marcador
function inpiojus-university {
    & "$($python.Source)" -m inpiojus_university @args
}
`$env:PYTHONPATH = "$destino;`$env:PYTHONPATH"
"@

if (-not (Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
$conteudoPerfil = [string](Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue)
if ($conteudoPerfil -notmatch [regex]::Escape($marcador)) {
    Add-Content -Path $PROFILE -Value $funcao
    Write-Host "  [ok] Comando 'inpiojus-university' adicionado ao perfil." -ForegroundColor Green
} else {
    Write-Host "  [ok] Comando 'inpiojus-university' ja configurado." -ForegroundColor Green
}

# 5. Sessao atual / current session -----------------------------------
$env:PYTHONPATH = "$destino;$env:PYTHONPATH"
$pythonExe = $python.Source
New-Item -Path Function:\global:inpiojus-university -Value { & $pythonExe -m inpiojus_university @args }.GetNewClosure() -Force | Out-Null

Write-Host ""
Write-Host "  Instalacao concluida! / Done! Experimente / Try:" -ForegroundColor Cyan
Write-Host ""
Write-Host "    inpiojus-university analisar `"$destino\examples\extrato_exemplo.txt`""
Write-Host "    inpiojus-university fiscalizar"
Write-Host "    inpiojus-university --versao"
Write-Host ""
Write-Host "  Docs: https://elevbit-ai.github.io/inpiojus-analitic-university/"
Write-Host ""
