# Brief de trabajo: reparar el tema 1 (SQL) del repo CDII

Repositorio: `https://github.com/jmtoral/cdii` (rama `main`)
Contexto: material didáctico de la clase **Ciencia de Datos para la Toma de Decisiones II**, notebooks de marimo exportados a WASM y publicados en GitHub Pages.

---

## 0. Atajo antes de empezar

Existe un ZIP con todos estos cambios ya hechos y verificados (`cdii-corregido.zip`). Si está disponible, descomprímelo sobre el repo, salta a la sección 7 (verificación) y confirma que todo pasa. Si no está disponible, ejecuta el brief completo desde la sección 2.

En cualquiera de los dos casos, **lee la sección 1 antes de tocar nada**: contiene mediciones sobre los datos que cambian decisiones de diseño y que no son obvias leyendo el código.

---

## 1. Hallazgos ya medidos (no los redescubras, pero sí revalídalos)

Todo lo siguiente se midió ejecutando consultas contra `01_sql/public/sample_data.parquet` tal como está hoy en el repo. Son hechos, no hipótesis.

### 1.1 Tres ejercicios del curso son irresolubles

La muestra actual se construyó con `df.sample(n=5000)`, un muestreo de **filas**. El grano real del dataset es la anotación (cada comentario fue evaluado por varias personas), así que el muestreo de filas destruye la estructura:

| Medición | Valor |
|---|---|
| Filas | 5,000 |
| Columnas | 143 |
| `comment_id` distintos | 3,356 (no es llave) |
| `annotator_id` distintos | 3,770 |
| **Máximo de anotaciones por anotador** | **5** |
| Códigos distintos en `platform` | 4 (0, 1, 2, 3) |

Consecuencia: estas tres consultas devuelven **cero filas** y son parte del material entregado a alumnos.

| Ubicación | Consulta | Filas |
|---|---|---|
| `ejercicio_01.py` pregunta 5 (20 pts) | `HAVING COUNT(*) > 50` por `annotator_id` | 0 |
| `02_agregaciones_joins.py` sección 3 | `HAVING COUNT(*) > 50 AND AVG(...) > 0` | 0 |
| `02_agregaciones_joins.py` ejercicio 2 | `HAVING COUNT(*) >= 10` por `annotator_id` | 0 |

Además, `ejercicio_01.py` pregunta 1 pide el top 20 por `hate_speech_score`, pero como `comment_id` no es llave, esas 20 filas corresponden a solo **9 comentarios distintos** con el texto repetido.

### 1.2 Qué columna pertenece a qué entidad

Verificado contando valores distintos dentro de cada grupo:

- **Constantes dentro de `comment_id`**: `text`, `platform`, `hate_speech_score`. → tabla `comentarios`.
- **Constantes dentro de `annotator_id`**: `annotator_gender`, `annotator_educ`, `annotator_income`, `annotator_ideology`, `annotator_age`, `annotator_severity`. → tabla `anotadores`.
- **Varían dentro de `comment_id`** (hasta 2 valores distintos): las ocho columnas `target_*` y las diez etiquetas ordinales (`sentiment`, `respect`, `insult`, `humiliate`, `status`, `dehumanize`, `violence`, `genocide`, `attack_defend`, `hatespeech`). → tabla `anotaciones`.

**Esto es importante y cambia el contenido pedagógico.** El material actual dice cosas como "comentarios cuyo objetivo fue por motivos de raza", tratando `target_race` como un atributo del comentario. No lo es: es el juicio de cada anotador sobre a quién ataca el texto, y los anotadores discrepan entre sí. Ese desacuerdo es la premisa del paper del corpus (Sachdeva et al., 2022, sobre *data perspectivism*), no un error de captura. Debe presentarse como tema, no corregirse silenciosamente.

`hate_speech_score` sí pertenece al comentario: es la estimación Rasch agregada de todas sus anotaciones.

### 1.3 `platform` no tiene codebook publicado

La ficha de HuggingFace del dataset no documenta el mapeo de los códigos. La literatura menciona tres plataformas (Twitter, Reddit, YouTube) pero los datos traen cuatro códigos. **No inventes etiquetas.** El catálogo debe salir con un valor explícito de "sin documentar" y el material debe usarlo como lección de gobernanza de datos: una columna sin codebook permite contar pero no concluir.

### 1.4 Otros defectos confirmados

- `data/download_data.py`: el bloque final sobrescribe `sample_data.parquet` de forma incondicional después del bloque `if args.sample`, así que `--sample 20000` produce silenciosamente 5,000 filas.
- **No existe `.github/` en el repo.** Pages está habilitado con origen *GitHub Actions* pero no hay workflow que lo alimente, así que el sitio no existe. Este era el bloqueo principal del deploy.
- `README.md` de la raíz todavía dice `https://[tu-usuario].github.io/cdii/`, con el placeholder sin sustituir.
- Hay caché de sesión de marimo commiteada: `01_sql/__marimo__/session/*.json` (tres archivos). Debe borrarse del control de versiones.
- Los ejercicios de práctica de `01_introduccion_sql.py` y `02_agregaciones_joins.py` traen **la solución escrita** debajo del comentario "Escribe tu código aquí". Y en `marimo run` / WASM las celdas son de solo lectura, así que no funcionan como ejercicios en ningún modo.
- `02_agregaciones_joins.py` está desincronizado: `__generated_with = "0.10.0"` (los otros dicen `0.23.16`), hace `return (_df_agg,)` devolviendo variables con guion bajo que son locales de celda, y sus firmas no declaran las tablas SQL que usa. Corre porque marimo re-deriva el grafo al cargar, pero es un archivo editado a mano que nunca pasó por `marimo edit` y guardado.
- La sección de JOINs de ese notebook es falsa: cruza un agregado de la misma tabla consigo mismo, crea `vista_comentarios` y nunca la usa, y no contrasta `INNER` con `LEFT` ni menciona cardinalidad.
- El `CASE WHEN` usa umbrales inventados (`> 2` severo, `> 0` moderado). El corpus **sí documenta** cortes reales: por arriba de `0.5` es aproximadamente discurso de odio, por debajo de `-1` es contra-discurso o discurso de apoyo, en medio es neutral o ambiguo. Usa los documentados.
- `ejecutar()` en `ejercicio_01.py` corre SQL arbitrario del alumno sin restricción: un `DROP TABLE` le rompe el notebook.
- No hay aviso de contenido en ningún notebook, pese a que el corpus contiene insultos y slurs explícitos. El ejercicio 3 del notebook 1 además pide al alumno buscar "un comentario terrible" y pegarlo en un campo que se transmite.

---

## 2. Tareas

Ejecuta en este orden. Cada una tiene su criterio de aceptación.

### T1. Reescribir `data/download_data.py`

Requisitos:

1. **Muestreo por entidad, no por fila.** Selecciona anotadores con al menos `--min-anotaciones` anotaciones, toma una muestra de `--anotadores` de ellos, y conserva **todas** sus filas. Defaults sugeridos: 400 anotadores, mínimo 10 anotaciones.
2. **Modo offline**: bandera `--from-parquet RUTA` para reconstruir desde un parquet local sin tocar la red. Necesario porque el `sample_data.parquet` del repo puede ser la única fuente disponible.
3. **Normaliza en cuatro tablas** y escríbelas en `01_sql/public/`:

   | Tabla | Grano | Llave | Columnas |
   |---|---|---|---|
   | `comentarios` | un comentario | `comment_id` | `comment_id`, `text`, `platform_id`, `hate_speech_score` |
   | `anotaciones` | evaluación de un comentario por un anotador | `(comment_id, annotator_id)` | llaves + 10 ordinales + 8 `target_*` |
   | `anotadores` | una persona | `annotator_id` | `annotator_id` + los 6 demográficos de 1.2 |
   | `plataformas` | catálogo | `platform_id` | `platform_id`, `nombre` |

   Renombra `platform` a `platform_id` en `comentarios` para que la llave del JOIN se llame igual en ambos lados.
4. **Verifica invariantes antes de escribir** y aborta si fallan: las tres llaves son únicas, y no hay anotaciones huérfanas contra `comentarios` ni contra `anotadores`.
5. **Imprime la distribución de conteos al final** (anotaciones por anotador y por comentario, con los cortes en 3, 5, 10, 20 y 50). Los ejercicios de `HAVING` dependen de estos números, así que quien regenere los datos necesita verlos.
6. Un diccionario `PLATAFORMAS: dict[int, str]` vacío al inicio del archivo, con un comentario explicando que el codebook no está publicado y que llenarlo es lo único que hay que tocar cuando aparezca. Si está vacío, el `nombre` sale como `"Sin documentar (codigo N)"` y el script lo avisa.
7. Corrige el bug del sobrescrito incondicional.

**Criterio de aceptación:**

```bash
python data/download_data.py --from-parquet 01_sql/public/sample_data.parquet \
  --anotadores 999999 --min-anotaciones 1
```

Debe imprimir `Integridad referencial y llaves: OK` y producir exactamente:

| Archivo | Filas |
|---|---|
| `comentarios.parquet` | 3,356 |
| `anotaciones.parquet` | 5,000 |
| `anotadores.parquet` | 3,770 |
| `plataformas.parquet` | 4 |

Si los números difieren, algo cambió en el parquet de origen: para y avisa antes de continuar.

Después borra `01_sql/public/sample_data.parquet` del repo.

### T2. Reescribir `01_sql/01_introduccion_sql.py`

- Aviso de contenido visible al inicio (`mo.callout` con `kind="warn"`), diciendo que el corpus tiene lenguaje ofensivo explícito y que todos los ejercicios se pueden resolver sin abrir la columna `text`.
- **Sección de modelo de datos antes de la primera consulta**, con la tabla de las cuatro entidades y la nota de 1.2 sobre `target_*`.
- Carga las cuatro tablas en celdas separadas con `mo.sql(..., output=False)`, una tabla por celda, para que marimo registre cada nombre en el grafo de dependencias.
- Contenido: `SELECT`, `WHERE` (usando el umbral documentado 0.5), `AND`/`OR`, `LIKE`/`ILIKE`, `ORDER BY` con la advertencia de que sin `ORDER BY` no hay orden garantizado, `LIMIT`.
- Sección interactiva con `mo.ui.slider` y `mo.ui.dropdown`, seguida de una nota explícita sobre **inyección SQL**: el material interpola el valor del widget en la consulta, y hay que decir por qué ahí es seguro (lista blanca del dropdown) y por qué no lo sería con entrada libre.
- **Ejercicios en `mo.ui.code_editor`, con la solución en un `mo.accordion` colapsado.** Nunca la solución visible debajo del enunciado.
- Elimina el ejercicio que pide cazar y pegar "un comentario terrible". Sustitúyelo por uno que trabaje la estructura: consultar todas las anotaciones de un `comment_id` concreto y preguntarse por qué no todas coinciden.
- Incluye un helper `ejecutar(consulta)` que envuelva el SQL del alumno en `SELECT * FROM ( ... ) LIMIT 500`, de modo que solo pueda ser un `SELECT`.

### T3. Reescribir `01_sql/02_agregaciones_joins.py`

- Mismo esquema de carga y mismo aviso de contenido.
- Agregaciones, con una nota sobre la diferencia entre `COUNT(*)`, `COUNT(columna)` y `COUNT(DISTINCT columna)`.
- `GROUP BY` por `platform_id`, seguido de la **lección de gobernanza**: la consulta corre y los números son correctos, pero no significan nada sin codebook.
- `GROUP BY` que sí concluye algo: promedio de etiquetas por `annotator_ideology`, uniendo `anotaciones` con `anotadores`.
- `HAVING` sobre conteo de anotaciones **por comentario** (no por anotador, ver 1.1). Añade una nota de que un resultado vacío puede venir del muestreo y no del SQL.
- `CASE WHEN` con los cortes documentados (0.5 y -1).
- Subconsultas y CTEs.
- **Sección de JOINs reescrita desde cero.** Debe cubrir:
  1. JOIN simple contra el catálogo `plataformas` para traer una etiqueta.
  2. **Fan-out**, demostrado con números en pantalla: comparar `COUNT(*)` de `comentarios`, `COUNT(*)` después de unir con `anotaciones`, y `COUNT(DISTINCT comment_id)`. Con la regla práctica: si vas a promediar un atributo del lado "uno", agrega **antes** de unir.
  3. `INNER` contra `LEFT`, con un caso donde la diferencia se vea. Usa comentarios que **ningún** anotador marcó con `target_race`: hay 2,310 de 3,356, así que el `LEFT JOIN` produce nulos reales. Cierra con `COALESCE`.
- Tres ejercicios en `code_editor` con solución colapsada.

### T4. Reescribir `01_sql/ejercicio_01.py`

Conserva la maquinaria de entrega: ya está verificada de extremo a extremo (POST a Apps Script con `text/plain` para evitar el preflight de CORS, botón de descarga como respaldo, y el candado por número de clic que evita reenvíos). No la toques.

Cambia:

1. Las siete preguntas, contra el esquema nuevo. Ninguna puede devolver cero filas.
2. **Verificación automática orientativa.** Un diccionario de consultas de referencia que se ejecutan en vivo contra los mismos datos, para que siga siendo correcta si se regenera la muestra. Compara número de filas y, cuando hay una columna clave definida, el conjunto ordenado de sus valores.
3. **Sandbox**: envuelve el SQL del alumno igual que en T2.
4. Aviso de contenido.

**Trampa importante en la verificación:** si el conteo de filas coincide pero el resultado del alumno **no incluye** la columna clave, no puedes concluir nada. Devolver "coincide" ahí es un falso positivo: una respuesta como `SELECT 1 AS x FROM comentarios LIMIT 8` acierta el conteo con contenido basura. En ese caso el mensaje debe decir que no se puede verificar, con `kind="neutral"`, no que esté bien.

Etiqueta la verificación como orientativa en el texto visible al alumno: puede marcar como distinta una consulta que resuelve bien por otro camino, y la calificación la pone el profesor leyendo el SQL.

### T5. Deploy

1. Crea `.github/workflows/deploy-pages.yml`: checkout, setup-python, instalar marimo (**fija la versión**, no uses la última), correr el script de export, y `configure-pages` + `upload-pages-artifact` + `deploy-pages`. Permisos `contents: read`, `pages: write`, `id-token: write`, y `concurrency: pages`.
2. Añade un paso que **falle el build** si los cuatro parquets no llegaron a `site/<notebook>/public/` en las tres páginas. Sin eso, un fallo de copia se publica silenciosamente como un sitio que carga pero no muestra datos.
3. Crea `scripts/export_wasm.sh` como script **canónico**, con una sola lista de notebooks, que genere las tres páginas con `marimo export html-wasm ... --mode run` y arme el `index.html`.
4. Convierte `scripts/export_wasm.ps1` en un wrapper de pocas líneas que invoque al `.sh` (Git para Windows trae bash). El objetivo es que no existan dos listas de notebooks que se desincronicen, porque el runner de CI es Linux y el desarrollo local es Windows.

### T6. Documentación e higiene

- `README.md` de la raíz: URL real del sitio (`https://jmtoral.github.io/cdii/`), aviso de contenido, el modelo de cuatro tablas, y la instrucción de regenerar datos con la advertencia de revalidar umbrales.
- `01_sql/README.md`: objetivos de aprendizaje actualizados, incluyendo detectar fan-out.
- `.gitignore`: que ignore `data/*.parquet` (área de trabajo) pero **no** `01_sql/public/*.parquet` (son los que se sirven al navegador). Comenta el porqué, que ya se prestó a confusión una vez.
- `requirements.txt`: comentario explícito de que **polars no existe en el navegador** y que ningún notebook destinado a WASM debe importarlo.
- Borra del control de versiones `01_sql/__marimo__/session/*.json`.
- Reescribe `HANDOFF.md` completo con el estado nuevo, los hallazgos de la sección 1, y lo que queda abierto (sección 8 de este brief).

---

## 3. Restricciones técnicas que no se pueden violar

Verificadas en navegador real en una ronda anterior. Romper cualquiera de estas produce un sitio que carga pero no funciona.

| Restricción | Detalle |
|---|---|
| Ruta de datos | `str(mo.notebook_location() / "public" / "<tabla>.parquet")` dentro de `read_parquet('{URL}')`. Es ruta de disco en local y URL del sitio en WASM. |
| Sin polars | En el navegador solo hay `pandas`, `pyarrow` y `duckdb`. Importar polars hace que la celda ni siquiera renderice. |
| Tipo de retorno | `mo.sql()` devuelve **pandas** en WASM, no polars. Todo código que toque el resultado debe funcionar con ambos. |
| Rutas locales | No hay filesystem del host en el navegador. `data/archivo.parquet` falla. |
| Modo `run` | El código de las celdas es de **solo lectura**. Los ejercicios donde el alumno escribe tienen que ir en `mo.ui.code_editor`, que sí sigue siendo interactivo y expone `.value`. |
| Ubicación de datos | Los parquets deben vivir en `01_sql/public/`. El export copia esa carpeta automáticamente. |

### Trampas de marimo

- **La salida de una celda es su última expresión.** `_html = mo.md(...)` no muestra nada, y `return (x,)` alimenta el grafo de dependencias pero tampoco muestra. Para mostrar, deja la expresión suelta al final. Este bug ya se introdujo una vez en este repo.
- **No edites los `.py` de marimo a mano sin volver a abrirlos con `marimo edit` y guardar.** Las firmas de celda se regeneran al guardar; un archivo editado a mano queda con firmas que no corresponden al grafo real.
- Las variables con guion bajo son locales de celda y **no** deben aparecer en el `return`.
- `marimo export html-wasm` devuelve **exit 255 desde PowerShell** aunque el export salga bien. Desde bash devuelve 0. No confíes en `$LASTEXITCODE`; comprueba que exista `index.html`.
- Si verificas widgets con Playwright: marimo los monta en **shadow DOM** y los custom elements `<marimo-*>` usan `display:contents`, así que `getBoundingClientRect()` da 0×0 y parece que no renderizan. Usa locators de Playwright, no `querySelectorAll`, o tendrás un falso negativo.
- Escribiendo en un `code_editor` con Playwright, `Tab` **no** saca el foco: CodeMirror lo captura para indentar y el valor nunca se confirma con `debounce=True`. Hay que hacer clic en otro elemento.

---

## 4. Cosas que NO debes hacer

- **No inventes las etiquetas de `platform`.** Ver 1.3.
- **No dejes soluciones visibles** debajo de los enunciados.
- **No uses umbrales de score inventados.** Usa los documentados (0.5 y -1).
- **No construyas ejercicios de `HAVING` sobre conteos por anotador** con la muestra actual: el máximo es 5 y darán vacío. Agrupa por comentario.
- **No trates `target_*` como atributo del comentario.**
- **No censures el corpus.** Avísalo, no lo escondas: censurarlo haría imposible el análisis y es el punto del dataset.
- **No borres `scripts/apps_script/`.** El sistema de entregas funciona y está documentado.

---

## 5. Archivos que no cambian

No los toques: `02_estadistica/README.md`, `03_machine_learning/README.md`, `04_optimizacion/README.md`, `scripts/apps_script/Codigo.gs`, `scripts/apps_script/README.md`.

---

## 6. Entorno

```bash
pip install "marimo[sql]==0.23.16" duckdb polars
```

marimo en el repo está en `0.23.16`. Mantén esa versión, y la misma en el workflow, para que lo que se publica sea lo que se probó.

---

## 7. Verificación obligatoria antes de hacer push

Los tres primeros bloques ya se ejecutaron y pasaron con la implementación de referencia. Reprodúcelos.

**7.1 Los notebooks corren sin errores**

```bash
for f in 01_sql/*.py; do marimo export html "$f" -o "/tmp/$(basename $f).html"; done
```

Los tres deben dar exit 0. Luego busca en cada HTML: `marimo-error`, `Catalog Error`, `Binder Error`, `Parser Error`, `NameError`. Todos deben ser cero.

**7.2 Ninguna consulta de referencia devuelve vacío**

Carga las cuatro tablas en DuckDB y ejecuta las soluciones de los seis ejercicios de práctica y las siete del ejercicio evaluado. Todas deben devolver al menos una fila. Valores esperados con la muestra actual:

| Consulta | Filas |
|---|---|
| Top 20 por `hate_speech_score` | 20 |
| `hate_speech_score > 2.0` | 191 |
| `text ILIKE '%hate%'` | 133 |
| Conteo por plataforma | 4 |
| Comentarios con más de 15 anotaciones | 57 |
| Comentarios con 10 o más anotaciones | 67 |
| Comentarios con 20 o más anotaciones | 48 |
| Promedio por `annotator_ideology` | 8 |

**7.3 El sitio se construye completo**

```bash
bash scripts/export_wasm.sh
```

Debe generar `site/index.html` y, para cada uno de los tres notebooks, `site/<nombre>/index.html` más **los cuatro parquets** en `site/<nombre>/public/`. Peso total esperado: ~83 MB, porque marimo copia los assets de pyodide completos a cada página.

**7.4 El sandbox de SQL funciona**

Prueba que `DROP TABLE comentarios` metido en el editor de un ejercicio produzca un error de sintaxis capturado y mostrado, y no destruya la tabla.

**7.5 La verificación automática no da falsos positivos**

Prellena las respuestas del ejercicio con seis correctas y una tramposa que acierte el conteo sin la columna clave (`SELECT 1 AS x FROM comentarios LIMIT 8` para la pregunta cuyo resultado esperado tiene 8 filas). Las seis deben decir que coinciden; la tramposa debe decir que no se puede verificar. **Este caso ya falló una vez** en la implementación de referencia y hubo que corregirlo.

**7.6 Lo que no se pudo verificar y sí deberías verificar tú**

- **Carga en navegador real.** No se pudo probar por falta de acceso a la descarga de Chromium. Levanta `python -m http.server 8000 --directory site`, abre las tres páginas y confirma que las tablas muestran números y que los editores SQL aceptan texto. Es lo primero que hay que hacer después del build.
- **Regenerar desde el corpus completo.** Tampoco se pudo: HuggingFace estaba bloqueado. Ver sección 8.

---

## 8. Lo que queda abierto después de este trabajo

1. **Los datos siguen siendo la muestra vieja, reorganizada.** La estructura queda correcta pero los conteos por anotador siguen topando en 5, porque la muestra original ya venía rota. Los ejercicios lo esquivan agrupando por comentario. Para arreglarlo de raíz, con red disponible:

   ```bash
   python data/download_data.py --anotadores 400 --min-anotaciones 10
   ```

   Después **revisa la distribución que imprime y vuelve a correr 7.2**, porque los umbrales de los ejercicios cambiarán.

2. **`ENDPOINT` en `ejercicio_01.py` sigue vacío** a propósito: el botón de enviar sale deshabilitado y solo funciona la descarga. Seguir `scripts/apps_script/README.md` (~10 min) y pegar la URL.

3. **Codebook de `platform`.** Ver 1.3.

4. **Ajustes del repo en GitHub**, que no se pueden hacer por código: Settings → Pages con origen *GitHub Actions*, y Settings → Actions → General permitiendo workflows con permisos de escritura.

5. **Temas 2, 3 y 4** siguen siendo placeholders.

6. **Peso del sitio.** Los ~83 MB están muy por debajo del límite de Pages, pero si se agregan muchos notebooks habrá que evaluar consolidar varios por página en vez de uno por página.
