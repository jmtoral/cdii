# 🤝 HANDOFF — Estado del Proyecto CDII

> **Última actualización**: 2026-08-11  
> **Último contribuidor**: Fix de renderizado de widgets + validación de WASM en navegador

---

## 🔬 Hallazgos verificados sobre WASM (2026-08-11)

Se probó el export WASM **en un navegador real** (Playwright + Edge headless, sirviendo el
export por HTTP). Resultados medidos, no supuestos:

| Estrategia de carga de datos | Resultado en WASM |
|---|---|
| `mo.notebook_location()` para construir la URL | ✅ resuelve a `http://…/public/sample_data.parquet` |
| **DuckDB `read_parquet('<url>')`** | ✅ **funciona — 5000 filas** |
| Polars leyendo desde URL | ❌ la celda ni siquiera renderiza (marimo intenta instalarlo por micropip) |
| Ruta local `data/sample_data.parquet` | ❌ no existe filesystem del host en el navegador |
| `mo.sql(...)` devolviendo DataFrame | ✅ devuelve **pandas** (no polars) |
| `mo.sql(widget.value)` — SQL dinámico de un widget | ✅ ejecuta |
| `mo.ui.code_editor` / `text_area` / `text` / `button` / `form` en `--mode run` | ✅ renderizan y son **editables** |
| Reactividad: editar el widget → re-ejecutar la celda | ✅ verificado (4 filas → 1 fila al cambiar la consulta) |
| `mo.download` | ✅ se construye sin problema |

**Librerías realmente disponibles en el navegador (medido):**
`pandas 3.0.2`, `pyarrow 22.0.0`, `duckdb 1.5.1`. **`polars` NO está** (`ModuleNotFoundError`).

**Conclusiones operativas:**
1. El patrón correcto es `DATA_URL = str(mo.notebook_location() / "public" / "sample_data.parquet")`
   y usarlo dentro de `read_parquet('{DATA_URL}')`. Verificado que **funciona igual en local y en WASM**.
2. El parquet debe vivir en `01_sql/public/`. El export de marimo copia esa carpeta automáticamente.
3. **No usar polars** en notebooks destinados a WASM. DuckDB sí funciona.
4. `--mode run` deja el código de **solo lectura**: un ejercicio donde el alumno escribe SQL en la
   celda no funciona. La solución es `mo.ui.code_editor`, que sigue siendo interactivo en modo `run`
   y además expone `.value` (la respuesta del alumno queda capturable para la entrega).

**Harness de verificación reutilizable**: se destiló todo esto en una skill en
`~/.claude/skills/marimo-wasm/`, con un script `scripts/verificar_wasm.py` que exporta un
notebook, lo sirve por HTTP y lo abre en un navegador real comprobando que carguen los datos
y los widgets. Usa el Edge del sistema (`channel="msedge"`), no descarga navegadores.
Correr eso **antes** de dar por bueno cualquier cambio: `python notebook.py` devuelve 0
aunque en el navegador no se vea nada.

⚠️ **Trampa al verificar widgets**: marimo monta los widgets en **shadow DOM** y los custom elements
`<marimo-*>` usan `display:contents`, así que `getBoundingClientRect()` sobre ellos da 0×0 y parece
que "no renderizan". Hay que usar **locators de Playwright** (`page.locator("textarea")`), que sí
atraviesan el shadow DOM. Un `querySelectorAll` crudo da un falso negativo.

⚠️ **`marimo export html-wasm` devuelve exit 255 desde PowerShell** aunque el export salga bien
(artefacto de PowerShell con comandos nativos). Desde bash devuelve 0. No confiar en `$LASTEXITCODE`
en PowerShell para este comando; comprobar que exista `index.html`.

### Sistema de entrega (verificado end-to-end en el navegador)

`ejercicio_01.py` se rediseñó para que el alumno responda en `mo.ui.code_editor` (SQL con
resaltado) en vez de editar celdas — que en `--mode run` no se pueden tocar. Cada respuesta se
ejecuta sola y muestra la tabla o un error legible.

La entrega ofrece dos caminos: **botón Enviar** (POST a un Apps Script que escribe en una Google
Sheet) y **botón Descargar** (JSON, respaldo si falla la red). Ver `scripts/apps_script/README.md`.

Prueba hecha con Playwright contra el export WASM real, con un endpoint local con CORS:

| Comprobación | Resultado |
|---|---|
| Alumno escribe SQL → se ejecuta en el navegador | ✅ "20 filas devueltas" |
| Validación reactiva de nombre/matrícula | ✅ el aviso cambia solo al completarlos |
| Botón deshabilitado si falta identidad o `ENDPOINT` | ✅ |
| POST sale del navegador y llega al endpoint | ✅ `text/plain`, CORS resuelto |
| Confirmación "Entrega recibida" en pantalla | ✅ |
| Acentos (UTF-8) en el payload | ✅ intactos |
| **No reenvía al editar una respuesta tras entregar** | ✅ candado por número de clic |

⚠️ **`ENDPOINT` está vacío a propósito.** Hasta que se pegue la URL del Apps Script, el botón de
enviar sale deshabilitado y solo funciona la descarga. Es deliberado: mejor un botón apagado que
uno que falla.

⚠️ **Trampa al escribir en un `code_editor` con Playwright**: `Tab` **no** saca el foco, CodeMirror
lo captura para indentar, así que el valor nunca se confirma (`debounce=True` confirma al perder el
foco). Hay que hacer clic en otro elemento. Los alumnos no se topan con esto porque hacen clic
fuera de forma natural, pero está dicho explícitamente en las instrucciones del notebook.

### Estado de la migración de datos
- `01_sql/public/sample_data.parquet` (465 KB) es **la única copia versionada** y la que se sirve al
  navegador; el export de marimo la copia automáticamente al sitio.
- `data/*.parquet` está ignorado por completo: es solo el área de trabajo de `download_data.py`.
  Se quitó la excepción `!data/sample_data.parquet` que había antes, para no tener dos copias del
  mismo archivo que se desincronicen sin que nadie lo note.
- ⚠️ **Al regenerar los datos**, `download_data.py` escribe en `data/`. Hay que copiar el resultado
  a `01_sql/public/` a mano, o el sitio seguirá sirviendo la muestra vieja.
- Los 3 notebooks ya usan `DATA_URL`. Los 3 corren en local con exit 0.

---

## 🚨 Defectos del contenido pedagógico (medidos el 2026-08-12)

Origen: `BRIEF-agente-cdii.md`, generado por otro agente. **Sus afirmaciones sobre los datos se
revalidaron una por una contra `01_sql/public/sample_data.parquet` y todas resultaron correctas.**

### Lo que está roto y por qué

La muestra se construyó con `df.sample(n=5000)` sobre **filas**, pero el grano real del dataset es
la **anotación**: cada comentario fue evaluado por varias personas. El muestreo de filas destruyó
esa estructura.

| Medición | Valor |
|---|---|
| Filas / columnas | 5,000 / 143 |
| `comment_id` distintos | 3,356 → **no es llave** |
| `annotator_id` distintos | 3,770 |
| Máx. anotaciones por anotador | **5** |
| Códigos en `platform` | 4 (sin codebook publicado) |

**Tres ejercicios devuelven cero filas** (verificado ejecutándolos):

| Ubicación | Consulta | Filas |
|---|---|---|
| `ejercicio_01.py` P5 (20 pts) | `HAVING COUNT(*) > 50` por `annotator_id` | **0** |
| `02_agregaciones_joins.py` §3 | `HAVING COUNT(*) > 50 AND AVG(...) > 0` | **0** |
| `02_agregaciones_joins.py` ej. 2 | `HAVING COUNT(*) >= 10` por `annotator_id` | **0** |

El alumno puede escribir el SQL perfecto y ver una tabla vacía, sin manera de saber que la culpa es
de los datos. **Arreglo: agrupar por comentario, no por anotador** (57 comentarios tienen >15
anotaciones).

El top 20 por `hate_speech_score` de la P1 son en realidad **9 comentarios distintos** repetidos.

### Error conceptual: `target_*` no es atributo del comentario

Verificado contando valores distintos por grupo:
- **Constantes dentro de `comment_id`**: `text`, `platform`, `hate_speech_score` → son del comentario.
- **Varían dentro de `comment_id`** (hasta 2 valores): las 8 `target_*` y las 10 etiquetas ordinales
  (`respect`, `sentiment`, `insult`…) → son de la **anotación**, no del comentario.
- **Constantes dentro de `annotator_id`**: los 6 demográficos `annotator_*` → son de la persona.

El material dice "comentarios cuyo objetivo fue por motivos de raza", tratando `target_race` como
propiedad del texto. No lo es: es el juicio de cada anotador, y los anotadores **discrepan**. Ese
desacuerdo es la premisa del corpus (*data perspectivism*), material de clase, no un error a corregir
en silencio.

### Otros defectos confirmados
- `data/download_data.py`: el bloque "muestra WASM" **pisa incondicionalmente** `sample_data.parquet`
  después del bloque `if args.sample`, así que `--sample 20000` produce 5,000 filas sin avisar.
- **Las soluciones están escritas debajo de "Escribe tu código aquí"** en los ejercicios de práctica
  de `01_introduccion_sql.py`. Deben ir en un `mo.accordion` colapsado.
- `README.md:81` sigue con el placeholder `https://[tu-usuario].github.io/cdii/`.
- `ejecutar()` en `ejercicio_01.py` corre SQL arbitrario: un `DROP TABLE` rompe el notebook.
  Envolver en `SELECT * FROM ( ... ) LIMIT 500` para forzar que solo sea un SELECT.
- Ningún notebook tiene aviso de contenido, pese a que el corpus trae slurs explícitos.
- La sección de JOINs de `02_agregaciones_joins.py` es falsa: cruza un agregado de la misma tabla
  consigo mismo y crea una vista que nunca usa.
- Umbrales del `CASE WHEN` inventados (`>2`). El brief afirma que el corpus documenta cortes reales
  (0.5 y −1); **eso no se ha verificado contra la fuente** — hacerlo antes de usarlos.

### Sobre el brief y su ZIP
`~/Downloads/cdii-corregido.zip` existe y su sección 0 propone descomprimirlo sobre el repo.
**No hacerlo así**: pisaría el deploy ya verificado y trae un workflow distinto al que está en verde.
Extraer por partes y verificar.

El brief también propone **normalizar en 4 tablas** (`comentarios`, `anotaciones`, `anotadores`,
`plataformas`) y reescribir los 3 notebooks. Tiene mérito —con una tabla plana no se pueden enseñar
JOINs de verdad— pero es una decisión **curricular**, no un arreglo de bug, y obliga a re-verificar
todo en navegador. Decisión pendiente del profesor.

Nota: sus números de la §7.2 (191, 133, 8) están calculados sobre la tabla `comentarios`
**deduplicada**, no sobre la plana. Comparados contra la tabla correcta, cuadran exactos.

---

## 📍 Estado Actual

### ✅ Completado
- **Estructura del proyecto** creada con 4 temas planificados (`01_sql/`, `02_estadistica/`, `03_machine_learning/`, `04_optimizacion/`)
- **Análisis de tecnología**: Marimo seleccionado sobre Streamlit (reactivo, SQL nativo, archivos `.py` puros)
- **Dataset**: [Measuring Hate Speech](https://huggingface.co/datasets/ucberkeley-dlab/measuring-hate-speech) (UC Berkeley D-Lab)
- **Pipeline de datos**: `data/download_data.py` descargó el dataset desde HuggingFace exitosamente (Muestra de 5k filas lista).
- **Entorno de ejecución**: Se validó el ambiente Conda `mlops` con `marimo[sql]`, `duckdb`, `polars` y `datasets`.
- **Tema 1 — SQL con DuckDB**: completamente desarrollado y probado.
  - `01_introduccion_sql.py` — SELECT, WHERE, LIKE, ORDER BY, LIMIT + widgets interactivos (slider, dropdown, text inputs). Incluye campo de "Nombre del alumno" y ejercicio interactivo final para buscar comentarios de odio.
  - `02_agregaciones_joins.py` — COUNT/AVG, GROUP BY, HAVING, CASE WHEN, CTEs, JOINs.
  - `ejercicio_01.py` — Ejercicio evaluable interactivo.
- **Corrección real del bug de widgets (2026-08-11)**: la nota anterior de este handoff decía que se
  había arreglado asignando las salidas a `_html`; eso era justamente **la causa** del bug. En marimo
  la salida de una celda es su **última expresión**, así que `_html = mo.md(...)` no muestra nada.
  Se quitaron esas asignaciones en `01_introduccion_sql.py` y los 4 widgets (text, slider, dropdown,
  text_area) volvieron a renderizar. Verificado exportando a HTML y comprobando que aparecen los
  `marimo-slider`, `marimo-dropdown`, etc. en el DOM.
- **Regla para no repetir el bug**: `return (x,)` alimenta el grafo de dependencias de marimo, **no**
  muestra nada. Para mostrar, dejar la expresión suelta al final de la celda.
- **Ruta de datos robusta**: `01_introduccion_sql.py` resolvía `data/sample_data.parquet` relativo al
  cwd, por lo que solo funcionaba si se lanzaba marimo desde la raíz. Verificado que ahora corre
  desde la raíz y desde `01_sql/`.
- **Validación**: Los notebooks tienen sintaxis correcta de Python/Marimo, las consultas de DuckDB se ejecutaron sin problemas sobre los datos locales, y el servidor de Marimo levantó correctamente.
- **Deployment**: scripts configurados para WASM + GitHub Pages (`export_wasm.ps1` y `deploy-pages.yml`).

- **Publicación (2026-08-12): el sitio está VIVO y verificado en producción** →
  **https://jmtoral.github.io/cdii/**
  Repo en [jmtoral/cdii](https://github.com/jmtoral/cdii), Pages con origen *GitHub Actions*
  (se habilitó por API: `gh api repos/jmtoral/cdii/pages -X POST -f build_type=workflow`).
  Prueba de humo con Playwright **contra la URL pública**: las 3 páginas cargan datos, el
  notebook 01 muestra su slider y su dropdown, el ejercicio muestra sus 7 editores SQL.
- **El workflow requirió `gh auth refresh -s workflow`**: el token de `gh` no puede subir
  archivos en `.github/workflows/` sin ese scope, ni por push ni por la API de contenidos
  (que responde un 404 engañoso).
- ⚠️ **`marimo export html-wasm` necesita `uv` instalado.** Sin él aborta a medias: copia los
  assets pero no genera `index.html`. El primer build de CI falló exactamente por esto, y lo
  detectamos **porque se quitó el `|| true`** — con el workflow viejo se habría publicado un
  sitio roto en silencio.
- **`export_wasm.ps1` ejecutado y verificado**: construye las 3 páginas con sus datos.
  Prueba de humo con Playwright sobre `site/`: las 3 cargan datos (tablas visibles), el
  notebook 01 muestra su slider y su dropdown, y el ejercicio muestra sus 7 editores SQL.

### 🔄 En Progreso
- Nada en curso.

### ❌ Pendiente / Sin Hacer

**1. Arreglar los defectos pedagógicos** — ver la sección 🚨 arriba. Lo urgente, en orden:
los 3 ejercicios de cero filas, esconder las soluciones, el lenguaje sobre `target_*`,
el sandbox de SQL, el aviso de contenido, el README y el bug de `download_data.py`.

**2. Configurar el endpoint de entregas**
`ENDPOINT` en `01_sql/ejercicio_01.py` está vacío a propósito → el botón de enviar sale
deshabilitado y solo funciona la descarga. Seguir `scripts/apps_script/README.md` (~10 min)
y pegar la URL.

**3. Temas 2, 3 y 4** son solo placeholders (`README.md` con ideas, sin desarrollo aún).

---

## 🧭 Próximos Pasos

### 1. Inicializar Git y GitHub Pages
1. `git init && git add . && git commit -m "Initial commit"`
2. Crear repo en GitHub y hacer push.
3. Habilitar GitHub Pages (Settings → Pages → GitHub Actions).
4. Verificar que el workflow `deploy-pages.yml` se ejecuta y despliega el sitio web interactivo.

### 2. Desarrollar Tema 2 — Estadística
**Ideas definidas** (ver `02_estadistica/README.md`):
- Estadística descriptiva con el dataset de hate speech.
- Pruebas de hipótesis: ¿hay diferencias significativas por plataforma/grupo?
- Correlaciones entre dimensiones (sentiment, respect, insult, violence).

**Patrón a seguir**:
- 1-2 notebooks de lecciones con explicaciones (usando Marimo).
- 1 notebook de ejercicio evaluable.
- Actualizar `scripts/export_wasm.ps1` y `deploy-pages.yml` con los nuevos notebooks.

### 3. Desarrollar Tema 3 y 4
- **Machine Learning**: Clasificación, feature engineering, comparación de modelos.
- **Optimización**: Umbrales de decisión, análisis costo-beneficio.

---

## 🏗️ Decisiones de Diseño

| Decisión | Elección | Justificación |
|---|---|---|
| Framework de notebooks | **Marimo** | Reactivo, SQL nativo, archivos `.py` puros, exporta a WASM |
| Motor SQL | **DuckDB** | Embebido, rápido, compatible con Parquet y WASM |
| Deployment | **WASM + GitHub Pages** | Gratis, interactivo desde el navegador de los estudiantes |
| Entorno Virtual | **Conda (mlops)** | Se usó un entorno existente con las dependencias instaladas |

---

## 📂 Archivos Clave

| Archivo | Propósito |
|---|---|
| `data/download_data.py` | Descarga el dataset de HuggingFace. |
| `01_sql/*.py` | Lecciones y ejercicios de SQL en Marimo. |
| `scripts/export_wasm.ps1` | Exporta notebooks a HTML/WASM. |
| `.github/workflows/deploy-pages.yml` | CI/CD automático para GitHub Pages. |
