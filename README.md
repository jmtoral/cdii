# 📊 Ciencia de Datos para la Toma de Decisiones II (CDII)

Repositorio de ejercicios y materiales interactivos para el curso **Ciencia de Datos para la Toma de Decisiones II**.

## 🛠️ Stack Tecnológico

| Herramienta | Uso |
|---|---|
| [Marimo](https://marimo.io/) | Notebooks reactivos (reemplazo moderno de Jupyter) |
| [DuckDB](https://duckdb.org/) | Motor SQL embebido — sin servidores, sin configuración |
| [Polars](https://pola.rs/) | DataFrames rápidos en Python |
| [Plotly](https://plotly.com/python/) | Visualizaciones interactivas |

## 📁 Estructura del Repositorio

```
cdii/
├── 01_sql/               ← Tema 1: SQL con DuckDB
│   ├── 01_introduccion_sql.py
│   ├── 02_agregaciones_joins.py
│   └── ejercicio_01.py
├── 02_estadistica/        ← Tema 2: Estadística (próximamente)
├── 03_machine_learning/   ← Tema 3: Machine Learning (próximamente)
├── 04_optimizacion/       ← Tema 4: Optimización (próximamente)
├── data/                  ← Scripts de descarga y datos
└── scripts/               ← Herramientas de build y deploy
```

## 🚀 Instalación Rápida

### Prerequisitos
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip

### Setup con pip
```bash
pip install -r requirements.txt
```

### Setup con uv (recomendado)
```bash
uv pip install -r requirements.txt
```

## 📥 Descargar los Datos

```bash
python data/download_data.py
```

Esto descarga el dataset [Measuring Hate Speech](https://huggingface.co/datasets/ucberkeley-dlab/measuring-hate-speech) de UC Berkeley D-Lab y guarda una muestra en `data/`.

Para descargar solo una muestra pequeña (más rápido para pruebas):
```bash
python data/download_data.py --sample 5000
```

## 💻 Usar los Notebooks

### Modo edición (para desarrollar / resolver ejercicios)
```bash
marimo edit 01_sql/01_introduccion_sql.py
```

### Modo app (para presentar en clase)
```bash
marimo run 01_sql/01_introduccion_sql.py
```

### Modo WASM (para publicar en GitHub Pages)
```powershell
.\scripts\export_wasm.ps1
```

Los notebooks exportados se publican automáticamente en GitHub Pages via GitHub Actions.

## 🌐 Acceso Online

Los ejercicios están disponibles como apps interactivas en:

> **https://[tu-usuario].github.io/cdii/**

No requiere instalación — corre directamente en el navegador.

## 📋 Temas del Curso

| # | Tema | Estado |
|---|---|---|
| 1 | SQL con DuckDB | ✅ En progreso |
| 2 | Estadística | 🔜 Próximamente |
| 3 | Machine Learning | 🔜 Próximamente |
| 4 | Optimización | 🔜 Próximamente |

## 📄 Licencia

Material educativo — uso interno del curso.
