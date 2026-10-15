# ==============================================================================
# Script de exportación WASM para GitHub Pages
# ==============================================================================
# Este script exporta todos los notebooks de Marimo como HTML/WASM estático
# para que los estudiantes los abran directamente en el navegador.
#
# Uso:
#   .\scripts\export_wasm.ps1
#
# Prerequisitos:
#   pip install "marimo[sql]"
# ==============================================================================

$ErrorActionPreference = "Stop"

# Directorio raíz del proyecto
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $ProjectRoot "site"

Write-Host "🏗️  Exportando notebooks de Marimo a WASM..." -ForegroundColor Cyan
Write-Host ""

# Crear directorio de salida
if (Test-Path $OutputDir) {
    Remove-Item -Recurse -Force $OutputDir
}
New-Item -ItemType Directory -Path $OutputDir | Out-Null

# Página índice: la misma portada que publica el workflow (portada/index.html),
# para que el sitio local y el publicado no se separen.
Copy-Item (Join-Path $ProjectRoot "portada/index.html") (Join-Path $OutputDir "index.html") -Force

# Buscar y exportar todos los notebooks .py de Marimo
# Las LECCIONES van en modo edit: es lo único que le da al alumno el botón de ▶ ejecutar
# y las celdas SQL nativas de marimo. En ese modo se ve todo el código, incluidas las
# soluciones de los acordeones, y está aceptado a cambio de que puedan correr las consultas.
# El EJERCICIO evaluado va en modo run, para que no puedan desarmar la entrega.
$Notebooks = @(
    @{ Path = "01_sql/01_introduccion_sql.py"; Name = "01_introduccion_sql"; Modo = "edit" },
    @{ Path = "01_sql/02_agregaciones.py"; Name = "02_agregaciones"; Modo = "edit" },
    @{ Path = "01_sql/03_joins.py"; Name = "03_joins"; Modo = "edit" },
    @{ Path = "01_sql/ejercicio_01.py"; Name = "ejercicio_01"; Modo = "run" }
)

$Fallos = @()

foreach ($nb in $Notebooks) {
    $FullPath = Join-Path $ProjectRoot $nb.Path
    $OutPath = Join-Path $OutputDir $nb.Name

    if (-not (Test-Path $FullPath)) {
        Write-Host "  ❌ No encontrado: $($nb.Path)" -ForegroundColor Red
        $Fallos += $nb.Name
        continue
    }

    Write-Host "  📄 Exportando $($nb.Name) (modo $($nb.Modo))..." -ForegroundColor Yellow
    marimo export html-wasm $FullPath -o $OutPath --mode $nb.Modo

    # OJO: no revisamos $LASTEXITCODE. `marimo export` devuelve 255 desde PowerShell
    # aunque el export salga bien (artefacto de PowerShell con comandos nativos).
    # La comprobación fiable es que exista el index.html.
    if (Test-Path (Join-Path $OutPath "index.html")) {
        Write-Host "  ✅ $($nb.Name) exportado" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($nb.Name): no se generó index.html" -ForegroundColor Red
        $Fallos += $nb.Name
    }
}

# Las presentaciones son HTML autocontenido (el logo va incrustado como data URI),
# así que basta copiarlas. Esto tiene que hacer lo mismo que el paso equivalente del
# workflow, o el sitio local y el publicado dejan de coincidir.
$PresOrigen = Join-Path $ProjectRoot "presentaciones"
if (Test-Path $PresOrigen) {
    Write-Host ""
    Write-Host "📊 Copiando presentaciones..." -ForegroundColor Cyan
    $PresDestino = Join-Path $OutputDir "presentaciones"
    # New-Item primero: si el destino no existe, Copy-Item crearía un ARCHIVO con ese
    # nombre en vez de una carpeta, y el sitio queda roto sin avisar.
    New-Item -ItemType Directory -Path $PresDestino -Force | Out-Null
    Copy-Item (Join-Path $PresOrigen "*.html") $PresDestino -Force
    foreach ($f in Get-ChildItem $PresDestino -Filter *.html) {
        Write-Host "  ✅ presentaciones/$($f.Name)" -ForegroundColor Green
    }
}

# El parquet tiene que viajar junto a cada notebook: los notebooks lo piden por URL
# relativa. marimo copia la carpeta public/ que esté al lado del .py, así que esto
# normalmente ya está hecho; lo verificamos igual.
Write-Host ""
Write-Host "🔎 Verificando que los datos estén publicados..." -ForegroundColor Cyan
foreach ($nb in $Notebooks) {
    # No fijamos el nombre del archivo a propósito: si se cambia el dataset, esto
    # sigue funcionando. Lo que importa es que llegue algún parquet.
    $PublicDir = Join-Path (Join-Path $OutputDir $nb.Name) "public"
    $Parquets = @(Get-ChildItem -Path $PublicDir -Filter *.parquet -ErrorAction SilentlyContinue)
    if ($Parquets.Count -gt 0) {
        $MB = [math]::Round(($Parquets | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
        Write-Host "  ✅ $($nb.Name)/public/ -> $($Parquets.Count) parquet(s), $MB MB" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Falta el parquet en $($nb.Name) — el notebook no cargará datos" -ForegroundColor Red
        $Fallos += "$($nb.Name) (datos)"
    }
}

if ($Fallos.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Exportación con errores: $($Fallos -join ', ')" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ ¡Exportación completada!" -ForegroundColor Green
Write-Host "   Los archivos están en: $OutputDir" -ForegroundColor Gray
Write-Host ""
Write-Host "   Para probar localmente:" -ForegroundColor Gray
Write-Host "   cd $OutputDir && python -m http.server 8000" -ForegroundColor White
Write-Host "   Luego abre http://localhost:8000" -ForegroundColor White
