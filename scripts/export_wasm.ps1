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

# Crear página índice
$IndexHtml = @"
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CDII - Ciencia de Datos para la Toma de Decisiones II</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #00d2ff, #7b2ff7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { color: #888; margin-bottom: 2rem; font-size: 1.1rem; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; max-width: 900px; width: 100%; }
        .card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
        }
        .card:hover {
            transform: translateY(-4px);
            border-color: #7b2ff7;
            box-shadow: 0 8px 32px rgba(123, 47, 247, 0.2);
        }
        .card h3 { color: #00d2ff; margin-bottom: 0.5rem; }
        .card p { color: #aaa; font-size: 0.95rem; line-height: 1.5; }
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .badge-leccion { background: rgba(0,210,255,0.15); color: #00d2ff; }
        .badge-ejercicio { background: rgba(255,107,107,0.15); color: #ff6b6b; }
        footer { margin-top: 3rem; color: #555; font-size: 0.85rem; }
    </style>
</head>
<body>
    <h1>📊 CDII</h1>
    <p class="subtitle">Ciencia de Datos para la Toma de Decisiones II</p>
    <div class="cards">
        <a class="card" href="01_introduccion_sql/index.html">
            <span class="badge badge-leccion">LECCIÓN</span>
            <h3>01 — Introducción a SQL</h3>
            <p>SELECT, WHERE, LIKE, ORDER BY, LIMIT — los fundamentos de SQL con DuckDB.</p>
        </a>
        <a class="card" href="02_agregaciones_joins/index.html">
            <span class="badge badge-leccion">LECCIÓN</span>
            <h3>02 — Agregaciones y JOINs</h3>
            <p>GROUP BY, HAVING, CASE WHEN, subqueries, CTEs y JOINs.</p>
        </a>
        <a class="card" href="ejercicio_01/index.html">
            <span class="badge badge-ejercicio">EJERCICIO</span>
            <h3>Ejercicio 01 — SQL</h3>
            <p>7 preguntas para practicar todo lo aprendido. ¡Buena suerte!</p>
        </a>
    </div>
    <footer>CDII · Powered by Marimo + DuckDB</footer>
</body>
</html>
"@
$IndexHtml | Out-File -FilePath (Join-Path $OutputDir "index.html") -Encoding UTF8

# Buscar y exportar todos los notebooks .py de Marimo
$Notebooks = @(
    @{ Path = "01_sql\01_introduccion_sql.py"; Name = "01_introduccion_sql" },
    @{ Path = "01_sql\02_agregaciones_joins.py"; Name = "02_agregaciones_joins" },
    @{ Path = "01_sql\ejercicio_01.py"; Name = "ejercicio_01" }
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

    Write-Host "  📄 Exportando $($nb.Name)..." -ForegroundColor Yellow
    marimo export html-wasm $FullPath -o $OutPath --mode run

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

# El parquet tiene que viajar junto a cada notebook: los notebooks lo piden por URL
# relativa (public/sample_data.parquet). marimo copia la carpeta public/ que esté
# al lado del .py, así que esto normalmente ya está hecho; lo verificamos igual.
Write-Host ""
Write-Host "🔎 Verificando que los datos estén publicados..." -ForegroundColor Cyan
foreach ($nb in $Notebooks) {
    $Parquet = Join-Path (Join-Path $OutputDir $nb.Name) "public\sample_data.parquet"
    if (Test-Path $Parquet) {
        Write-Host "  ✅ $($nb.Name)/public/sample_data.parquet" -ForegroundColor Green
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
