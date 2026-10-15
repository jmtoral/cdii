# Rest-Mex 2025 · satisfacción en Pueblos Mágicos

¿Qué tan contentos se van los turistas, y se puede saber solo con leer su reseña?

## Cómo reproducirlo

1. Abre `restmex.Rproj` (esto fija la raíz del proyecto).
2. Instala lo necesario: `install.packages(c("tidyverse", "tidymodels", "here"))`.
3. Corre `correr_todo.R`: baja los datos, los limpia y entrena el modelo.
4. Dale **Render** a `notebooks/01_eda.qmd`, `notebooks/02_modelo.qmd` y `reports/reporte.qmd`.

## Qué hay en cada carpeta

| carpeta | qué vive ahí | ¿va a git? |
|---|---|---|
| `data/raw/` | los datos tal como llegaron. No se editan nunca | no |
| `data/processed/` | lo que sale de `02_limpiar.R` | no |
| `R/` | funciones que usa más de un archivo | sí |
| `scripts/` | los pasos, numerados en el orden en que se corren | sí |
| `notebooks/` | exploración | sí (el `.qmd`, no el `.html`) |
| `outputs/` | modelo, predicciones, tablas | no |
| `reports/` | el reporte para otra persona | sí (el `.qmd`) |

## Los datos

Rest-Mex 2025, conjunto de entrenamiento: 208,051 reseñas de TripAdvisor (2002–2024) sobre 40 Pueblos Mágicos con
su polaridad (1 a 5). Uso exclusivamente académico y de investigación.

Álvarez-Carmona, M. Á. et al. (2025). Overview of Rest-Mex at IberLEF 2025: Researching
Sentiment Evaluation in Text for Mexican Magical Towns. *Procesamiento del Lenguaje
Natural*, 75, 499–511.
