import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    DATA_URL = str(mo.notebook_location() / "public" / "hate_speech.parquet")
    return (DATA_URL,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Introducción a SQL con DuckDB 🦆

    Bienvenida/o a **Ciencia de Datos para la Toma de Decisiones II**.

    SQL es el lenguaje con el que se le hacen preguntas a una base de datos. Al terminar
    esta sesión vas a poder abrir una tabla que nunca has visto, entender qué contiene y
    sacarle respuestas.

    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ## 🚦 Antes que nada: enciende el notebook

        Esta página abre **apagada**: verás el código pero ningún resultado. Es normal.

        ### 👉 Presiona `Ctrl` + `Shift` + `R` para ejecutar todo

        Tarda cerca de **medio minuto** la primera vez, porque tu navegador está bajando
        Python y los 135 mil comentarios. Ten paciencia: solo pasa una vez.

        Cuando termine vas a ver tablas con datos debajo de cada consulta. A partir de
        ahí ya puedes trabajar:

        | Para… | Haz esto |
        |---|---|
        | Ejecutar **una** celda | Pon el cursor dentro y `Ctrl` + `Enter` |
        | Ejecutar **todo** otra vez | `Ctrl` + `Shift` + `R` |
        | Ejecutar con el mouse | Pasa el cursor sobre la celda y usa el botón **▶** |

        **Puedes cambiar cualquier consulta.** Esa es la idea: modifica los números, las
        columnas, los filtros, y vuelve a ejecutar para ver qué pasa. Nada de lo que
        hagas se guarda ni afecta a nadie: si dejas una celda hecha un desastre, recarga
        la página y todo vuelve al original.
        """),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        **Sobre el contenido.** Trabajamos con el corpus *Measuring Hate Speech* de UC
        Berkeley: comentarios reales de redes sociales, **sin censurar**, que incluyen
        insultos y lenguaje ofensivo. Vas a leerlos, porque analizarlos es el punto de
        la clase y no se puede analizar lo que no se mira.

        Si en algún momento te resulta pesado, avísale a quien imparte la clase.
        """),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0. ¿De dónde salen estos datos?

    Antes de tocar nada, conviene saber qué estamos abriendo. Trabajar con datos que no
    sabes de dónde vienen es la forma más rápida de llegar a conclusiones falsas.

    **Quién lo hizo.** El [D-Lab de UC Berkeley](https://huggingface.co/datasets/ucberkeley-dlab/measuring-hate-speech).
    El trabajo se publicó como *"Measuring a hate speech spectrum with faceted Rasch item
    response theory and perspective-aware, explainable-by-design deep learning"*, de
    **Chris J. Kennedy, Geoff Bacon, Alexander Sahn y Claudia von Vacano**
    ([arXiv:2009.10277](https://arxiv.org/abs/2009.10277)).

    **Qué contiene.** Comentarios de **YouTube, Twitter y Reddit**, evaluados por
    trabajadores de Amazon Mechanical Turk. El corpus del paper tiene 50,070 comentarios
    y 11,143 anotadores.

    ### Por qué hay varias personas evaluando el mismo comentario

    Esta es la decisión de diseño más importante del corpus, y la razón de casi todo lo
    que vas a ver hoy.

    Si a cada comentario lo evaluara **una sola persona**, tendrías una etiqueta que
    parece un hecho — "esto es discurso de odio" — pero que en realidad es *la opinión de
    esa persona*, con toda su historia detrás. Alguien que ha recibido ese insulto y
    alguien que nunca lo ha oído no lo leen igual.

    Así que hicieron lo contrario: pedirle a **varias personas** que evaluaran cada
    comentario, y **medir el desacuerdo en vez de esconderlo**. Con eso estiman dos cosas
    a la vez: qué tan ofensivo es un comentario, y **qué tan severo o indulgente es cada
    evaluador**, para descontarlo. En palabras del paper, ajustan *"la perspectiva de
    etiquetado de cada anotador"*.

    ### Qué es `hate_speech_score`

    No es un promedio de opiniones. Cada persona contesta **10 preguntas ordinales** sobre
    el comentario (`sentiment`, `respect`, `insult`, `humiliate`, `status`, `dehumanize`,
    `violence`, `genocide`, `attack_defend`, `hatespeech`), y todas esas respuestas se
    combinan con un modelo **Rasch / teoría de respuesta al ítem** (el mismo tipo de
    modelo con el que se califican exámenes estandarizados).

    El resultado es **un número continuo por comentario**, en un espectro que el paper
    describe como *"desde genocida hasta discurso de apoyo"*. Más alto = más hostil;
    negativo = solidario o de defensa.
    """)
    return


@app.cell(hide_code=True)
def _():
    # ─────────────────────────────────────────────────────────────────────────
    # CONFIGURACIÓN DEL PROFESOR
    # Mismo Apps Script que recibe las entregas del ejercicio evaluado. La asistencia
    # llega a la misma hoja y se distingue por la columna `ejercicio`, que dice
    # "asistencia_01_intro_sql" en vez de "ejercicio_01_sql".
    # Instrucciones: scripts/apps_script/README.md
    # ─────────────────────────────────────────────────────────────────────────
    ENDPOINT = (
        "https://script.google.com/macros/s/"
        "AKfycbxAh7nw7L0Kt5Qnak5Dyj9nkPX4PhX1c6WykpFGL6JOyvTL0dDv2-H0qHlEvfxQZCWj4g/exec"
    )
    CURSO = "CDII"
    SESION = "asistencia_01_intro_sql"
    return CURSO, ENDPOINT, SESION


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 📋 Pasa lista

    Antes de empezar, registra tu asistencia: escribe tu nombre y tu matrícula y aprieta
    el botón. Le llega a tu profesor al instante.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    nombre_alumno = mo.ui.text(
        label="**Nombre completo**", placeholder="Nombre Apellido", full_width=True
    )
    matricula_alumno = mo.ui.text(
        label="**Matrícula**", placeholder="A01234567", full_width=True
    )
    mo.callout(mo.vstack([nombre_alumno, matricula_alumno], gap=0.5), kind="info")
    return matricula_alumno, nombre_alumno


@app.cell(hide_code=True)
def _(ENDPOINT, matricula_alumno, mo, nombre_alumno):
    _listo = bool(
        (nombre_alumno.value or "").strip() and (matricula_alumno.value or "").strip()
    )
    boton_asistencia = mo.ui.button(
        value=0,
        on_click=lambda n: n + 1,
        label="✋ Registrar mi asistencia",
        kind="success",
        disabled=not (_listo and ENDPOINT),
    )
    mo.vstack(
        [
            boton_asistencia,
            mo.md(
                "<small>Completa nombre y matrícula para poder registrarte.</small>"
                if not _listo
                else "<small>Listo para registrar.</small>"
            ),
        ]
    )
    return (boton_asistencia,)


@app.cell(hide_code=True)
def _():
    # marimo re-ejecuta una celda cada vez que cambia algo de lo que depende. Sin este
    # candado, el alumno se registraría de nuevo con solo corregir su nombre. Guardamos
    # cuántos clics ya procesamos para enviar exactamente una vez por clic.
    ESTADO_ASISTENCIA = {"clics": 0, "resultado": None}
    return (ESTADO_ASISTENCIA,)


@app.cell(hide_code=True)
def _():
    async def registrar(url: str, cuerpo: str):
        """POST del registro. Funciona igual en el navegador y en local.

        Content-type text/plain a propósito: application/json dispara una petición
        CORS de verificación previa que Apps Script no sabe responder.
        """
        try:
            from pyodide.http import pyfetch  # solo existe dentro del navegador

            r = await pyfetch(
                url,
                method="POST",
                headers={"Content-Type": "text/plain;charset=utf-8"},
                body=cuerpo,
            )
            return r.status < 400, (await r.string())[:200]
        except ImportError:
            import urllib.request

            pet = urllib.request.Request(
                url,
                data=cuerpo.encode("utf-8"),
                headers={"Content-Type": "text/plain;charset=utf-8"},
                method="POST",
            )
            with urllib.request.urlopen(pet, timeout=30) as resp:
                return resp.status < 400, resp.read().decode("utf-8", "replace")[:200]
        except Exception as e:  # noqa: BLE001
            return False, f"{type(e).__name__}: {e}"

    return (registrar,)


@app.cell(hide_code=True)
async def _(
    CURSO,
    ENDPOINT,
    ESTADO_ASISTENCIA,
    SESION,
    boton_asistencia,
    matricula_alumno,
    mo,
    nombre_alumno,
    registrar,
):
    _clics = boton_asistencia.value or 0

    if _clics > ESTADO_ASISTENCIA["clics"]:
        ESTADO_ASISTENCIA["clics"] = _clics

        import datetime
        import json

        _cuerpo = json.dumps(
            {
                "curso": CURSO,
                "ejercicio": SESION,
                "nombre": (nombre_alumno.value or "").strip(),
                "matricula": (matricula_alumno.value or "").strip(),
                "enviado_en": datetime.datetime.now().isoformat(timespec="seconds"),
                "contestadas": 0,
                "respuestas": {},
            },
            ensure_ascii=False,
        )
        _ok, _detalle = await registrar(ENDPOINT, _cuerpo)
        ESTADO_ASISTENCIA["resultado"] = (
            mo.callout(
                mo.md(
                    "### ✅ Asistencia registrada\n\n"
                    f"Quedaste en la lista, **{nombre_alumno.value}**. Ahora sí, a SQL. 👇"
                ),
                kind="success",
            )
            if _ok
            else mo.callout(
                mo.md(
                    f"### ❌ No se pudo registrar\n\n```\n{_detalle}\n```\n\n"
                    "Avísale a tu profesor para que te apunte a mano."
                ),
                kind="danger",
            )
        )

    ESTADO_ASISTENCIA["resultado"] or mo.md("")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Cargar la tabla

    Los datos viven en un archivo **Parquet**: un formato que guarda la información *por
    columnas* en vez de por filas, lo que lo hace muy rápido para análisis.

    La celda de abajo abre el archivo y lo convierte en una tabla llamada `comentarios`.
    Léela por partes:

    | Pedazo | Qué hace |
    |---|---|
    | `read_parquet('...')` | Abre el archivo |
    | `SELECT *` | Toma **todas** sus columnas |
    | `CREATE OR REPLACE TABLE comentarios AS` | Guarda el resultado con ese nombre |

    `CREATE OR REPLACE` significa "créala, y si ya existía, reemplázala": puedes volver a
    ejecutarla sin que truene.
    """)
    return


@app.cell
def _(DATA_URL, mo):
    comentarios = mo.sql(
        f"""
        CREATE OR REPLACE TABLE comentarios AS
        SELECT * FROM read_parquet('{DATA_URL}')
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comprobemos que cargó. **Esta celda ya es tuya: cámbiale algo y ejecútala otra vez.**
    """)
    return


@app.cell
def _(comentarios, mo):
    filas_cargadas = mo.sql(
        f"""
        SELECT count(*) AS filas_cargadas
        FROM comentarios
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. ¿Qué hay dentro?

    `SELECT *` trae **todas** las columnas y `LIMIT 5` pide solo cinco filas.

    👉 En la tabla del resultado puedes **desplazarte a la derecha** para ver más columnas,
    y hacer clic en una celda de `text` para leer el comentario completo.
    """)
    return


@app.cell
def _(comentarios, mo):
    primeras_filas = mo.sql(
        f"""
        SELECT *
        FROM comentarios
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Son **143 columnas**: demasiadas para entender nada así. Pedir solo las que te
    interesan es lo que hace legible un resultado.

    *Prueba a quitarle o agregarle columnas a la siguiente celda.*
    """)
    return


@app.cell
def _(comentarios, mo):
    columnas_legibles = mo.sql(
        f"""
        SELECT
            comment_id,
            annotator_id,
            text,
            hate_speech_score,
            respect,
            insult
        FROM comentarios
        LIMIT 8
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explora las 143 columnas

    `DESCRIBE` no devuelve datos sino **la lista de columnas** con su tipo. Escribe un
    pedazo de nombre para filtrarlas: prueba `target`, `annotator`, o déjalo vacío.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    filtro_columnas = mo.ui.text(
        label="Buscar columna:", placeholder="target, annotator, score...", full_width=True
    )
    filtro_columnas
    return (filtro_columnas,)


@app.cell(hide_code=True)
def _(filtro_columnas):
    # Duplicamos las comillas simples para que lo que escriba el alumno no pueda
    # cerrar la cadena y modificar la consulta. Se explica en la sección 6.
    filtro_seguro = (filtro_columnas.value or "").replace("'", "''")
    return (filtro_seguro,)


@app.cell
def _(comentarios, filtro_seguro, mo):
    lista_columnas = mo.sql(
        f"""
        SELECT column_name AS columna, column_type AS tipo
        FROM (DESCRIBE comentarios)
        WHERE column_name ILIKE '%{filtro_seguro}%'
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. La pregunta clave: ¿por qué se repiten las filas?

    Si buscaste `annotator` viste muchas columnas sobre *quién* evaluó. Eso es la pista de
    algo fundamental:

    > **Cada fila NO es un comentario. Cada fila es la evaluación que UNA persona hizo
    > sobre UN comentario.**

    Si a un comentario lo evaluaron 9 personas, ocupa **9 filas**, con el mismo texto
    repetido y con juicios que pueden diferir.

    Comprobémoslo contando de dos maneras:
    """)
    return


@app.cell
def _(comentarios, mo):
    dos_maneras_de_contar = mo.sql(
        f"""
        SELECT
            count(*)                     AS filas,
            count(DISTINCT comment_id)   AS comentarios_distintos,
            count(DISTINCT annotator_id) AS personas_que_evaluaron
        FROM comentarios
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **135,556 filas pero solo 39,565 comentarios.** La diferencia son las repeticiones.

    `count(*)` cuenta filas. `count(DISTINCT columna)` cuenta **valores diferentes**. Si
    alguien te pregunta "¿cuántos comentarios hay?" y respondes 135,556, tu respuesta está
    inflada casi cuatro veces.

    ### Míralo con un comentario concreto

    El comentario `20014` es un caso extremo: lo evaluaron **793 personas**. Mueve el
    control para ver más o menos de sus evaluaciones y **compara las filas entre sí**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    cuantas_ver = mo.ui.slider(
        start=3, stop=60, step=1, value=10,
        label="¿Cuántas evaluaciones de ese mismo comentario quieres ver?",
        show_value=True, full_width=True,
    )
    cuantas_ver
    return (cuantas_ver,)


@app.cell
def _(comentarios, cuantas_ver, mo):
    un_solo_comentario = mo.sql(
        f"""
        SELECT
            annotator_id,
            text,
            respect,
            insult,
            target_race,
            hate_speech_score
        FROM comentarios
        WHERE comment_id = 20014
        ORDER BY annotator_id
        LIMIT {cuantas_ver.value}
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Fíjate en lo que acabas de ver. La columna `text` es **idéntica** en todas las filas:
    es el mismo comentario. Y sin embargo:

    - `respect` **cambia** de una fila a otra: las 793 personas usaron **cinco** valores distintos.
    - `target_race` **cambia**, y aquí está lo interesante: **353 personas dijeron que sí
      ataca por raza y 440 dijeron que no**. Casi un volado sobre el mismo texto.
    - `hate_speech_score` es **idéntico** en todas: 1.48.

    ### Por qué esto importa (y mucho)

    Hay **tres tipos de columna** mezclados en la misma tabla:

    | Tipo | Ejemplos | Comportamiento |
    |---|---|---|
    | Del **comentario** | `text`, `platform`, `hate_speech_score` | Igual en todas sus filas |
    | De la **persona** que evaluó | `annotator_gender`, `annotator_ideology` | Igual en todas las filas de esa persona |
    | Del **juicio** | `respect`, `insult`, `target_race`… | **Distinto** entre filas del mismo comentario |

    ⚠️ Por eso `target_race` **no significa** "este comentario ataca por motivos de raza".
    Significa **"esta persona consideró que ataca por motivos de raza"**. Y no se ponen
    de acuerdo.

    Eso no es un error del dataset: es su hallazgo principal. **Si algo resulta ofensivo
    depende de quién lo lee.** `hate_speech_score` existe precisamente para resumir todas
    esas opiniones en un número por comentario, y por eso sí es constante.

    ### Un detalle que solo se ve mirando: aquí hay dos datasets, no uno

    ¿793 personas evaluando un comentario, cuando el promedio es 3? Eso no es casualidad.
    Contemos cuántos comentarios tiene cada cantidad de evaluaciones:
    """)
    return


@app.cell
def _(comentarios, mo):
    distribucion = mo.sql(
        f"""
        SELECT
            evaluaciones,
            count(*) AS cuantos_comentarios
        FROM (
            SELECT comment_id, count(*) AS evaluaciones
            FROM comentarios
            GROUP BY comment_id
        )
        GROUP BY evaluaciones
        ORDER BY evaluaciones
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Mira el salto. Hay decenas de miles de comentarios con **1, 2, 3 o 4** evaluaciones…
    y de repente **70 comentarios con entre 243 y 815**. Nada en medio.

    Eso es un **conjunto de calibración**: un puñado de comentarios que casi todos los
    anotadores evaluaron, para poder compararlos entre sí. Sin algo así no puedes saber si
    una persona puso puntajes bajos porque los comentarios eran suaves o porque ella es
    indulgente.

    **La lección práctica:** este archivo no es homogéneo. Si sacas un promedio sobre toda
    la tabla, esos 70 comentarios pesan como 25,000 filas y se comen tu resultado. Un
    dataset casi nunca es una sola cosa, y descubrirlo es trabajo tuyo.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. Tu primera consulta, pieza por pieza

    Vamos a construir **una sola consulta** agregando una pieza a la vez. Cada celda es
    editable: cámbiale los números, las columnas, lo que quieras, y ejecútala.

    ### Pieza 1 — `SELECT` y `FROM`
    """)
    return


@app.cell
def _(comentarios, mo):
    pieza_1 = mo.sql(
        f"""
        SELECT text, hate_speech_score
        FROM comentarios
        WHERE hate_speech_score > 2
        LIMIT 50
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 2 — `WHERE`: quedarte solo con algunas filas

    Un filtro: solo pasan las filas que cumplen la condición.

    ¿Y qué umbral ponemos en `hate_speech_score`? Aquí hay que ser honestos: **el score es
    continuo y no trae una línea marcada**. Va de −8.34 a 6.30 y no hay ningún salto
    natural que separe "odio" de "no odio". Es un espectro.

    En esta clase usaremos **0.5** como corte, y **−1** para el lado del discurso de
    apoyo. Son decisiones **nuestras**, no leyes del dataset. Si mueves el umbral se
    mueven tus conclusiones — **pruébalo ahora**: cambia el `0.5` por `3` y ejecuta.
    """)
    return


@app.cell
def _(comentarios, mo):
    pieza_2 = mo.sql(
        f"""
        SELECT text, hate_speech_score
        FROM comentarios
        WHERE hate_speech_score > 0.5
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 3 — `AND`: dos condiciones a la vez

    `AND` exige que se cumplan las dos. `OR` se conforma con una. *Cámbialo por `OR` y
    compara cuántas filas salen.*
    """)
    return


@app.cell
def _(comentarios, mo):
    pieza_3 = mo.sql(
        f"""
        SELECT text, hate_speech_score, insult
        FROM comentarios
        WHERE hate_speech_score > 0.5
          AND insult > 2
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 4 — `ORDER BY`: poner orden

    Sin `ORDER BY` la base de datos no promete ningún orden y puede devolverte filas
    distintas cada vez. Si el orden te importa, **pídelo**. `DESC` de mayor a menor,
    `ASC` de menor a mayor.
    """)
    return


@app.cell
def _(comentarios, mo):
    pieza_4 = mo.sql(
        f"""
        SELECT text, hate_speech_score, insult
        FROM comentarios
        WHERE hate_speech_score > 0.5
          AND insult > 2
        ORDER BY hate_speech_score DESC
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ahí está tu primera consulta completa. Cinco piezas, y **el orden en que se escriben
    no es negociable**:

    ```sql
    SELECT   columnas       -- 1. qué quiero ver
    FROM     tabla          -- 2. de dónde
    WHERE    condición      -- 3. con qué filas me quedo
    ORDER BY columna DESC   -- 4. en qué orden
    LIMIT    n              -- 5. cuántas
    ```

    ---
    ## 5. El orden de ejecución (esto explica la mitad de los errores)

    Ese es el orden en que se **escribe**. Pero la base de datos la **ejecuta en otro
    orden**:

    ```
    1. FROM      →  primero busca la tabla
    2. WHERE     →  descarta filas
    3. GROUP BY  →  agrupa las que quedan        (notebook 2)
    4. HAVING    →  descarta grupos              (notebook 2)
    5. SELECT    →  recién aquí calcula las columnas
    6. ORDER BY  →  ordena el resultado
    7. LIMIT     →  y al final corta
    ```

    **Se escribe empezando por `SELECT`, pero se ejecuta empezando por `FROM`.** Por eso,
    para entender una consulta ajena, conviene leerla empezando por el `FROM`.

    Y de ahí sale este error. `count(*)` solo existe **después** de agrupar (paso 3), así
    que no puedes usarlo en el `WHERE` (paso 2). **Ejecuta la celda de abajo y lee el
    mensaje**; luego arréglala tú: cambia `WHERE` por `HAVING` y muévelo debajo del
    `GROUP BY`.
    """)
    return


@app.cell
def _(comentarios, mo):
    esto_falla_a_proposito = mo.sql(
        f"""
        SELECT comment_id
        FROM comentarios
        WHERE count(*) > 3
        GROUP BY comment_id
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *"WHERE clause cannot contain aggregates!"* — te lo dice tal cual.

    Así queda bien, y de paso es tu primer `GROUP BY`:
    """)
    return


@app.cell
def _(comentarios, mo):
    con_having = mo.sql(
        f"""
        SELECT comment_id, count(*) AS evaluaciones
        FROM comentarios
        GROUP BY comment_id
        HAVING count(*) > 3
        ORDER BY evaluaciones DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🤔 ¿Por qué DuckDB me deja hacer cosas que 'no se pueden'?": mo.md(r"""
            Buena observación si lo notaste. DuckDB es más permisivo que el estándar: por
            ejemplo, te deja usar en el `WHERE` un alias que definiste en el `SELECT`,
            aunque según el orden de ejecución ese alias "todavía no existe".

            Es una comodidad de DuckDB, no una regla de SQL. **Esa misma consulta puede
            fallar** en PostgreSQL, SQL Server u Oracle.

            Moraleja: razona con el orden de ejecución, no con lo que tu base de datos te
            tolere hoy. El código que escribes suele acabar corriendo en otro motor.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. Busca lo que tú quieras

    `LIKE` compara texto con el comodín `%`, que significa "cualquier cosa, o nada". Así,
    `'%odio%'` encuentra la palabra en cualquier posición. `LIKE` distingue mayúsculas;
    **`ILIKE` no**, y casi siempre quieres `ILIKE`.

    **Escribe la palabra que se te ocurra** y mira qué encuentra:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    palabra = mo.ui.text(
        label="**Buscar esta palabra en los comentarios:**",
        value="people",
        placeholder="escribe una palabra",
        full_width=True,
    )
    orden_busqueda = mo.ui.dropdown(
        options={
            "Los de mayor odio primero": "hate_speech_score DESC",
            "Los de menor odio primero": "hate_speech_score ASC",
            "Sin ordenar": "comment_id",
        },
        value="Los de mayor odio primero",
        label="Ordenar por",
    )
    mo.vstack([palabra, orden_busqueda], gap=0.5)
    return orden_busqueda, palabra


@app.cell(hide_code=True)
def _(palabra):
    # Duplicar las comillas simples evita que lo que escriba el alumno cierre la
    # cadena y cambie el sentido de la consulta. Ver la nota de abajo.
    palabra_segura = (palabra.value or "").replace("'", "''")
    return (palabra_segura,)


@app.cell
def _(comentarios, mo, orden_busqueda, palabra_segura):
    busqueda = mo.sql(
        f"""
        SELECT text, hate_speech_score, insult
        FROM comentarios
        WHERE text ILIKE '%{palabra_segura}%'
        ORDER BY {orden_busqueda.value}
        LIMIT 10
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "⚠️ ¿No es peligroso meter dentro de la consulta lo que escribe el usuario?": mo.md(r"""
            Sí, y es de las cosas más importantes que te llevas de esta clase.

            Pegar texto de un usuario dentro de una consulta es la puerta de la
            **inyección SQL**, una de las vulnerabilidades más viejas y explotadas que
            existen. Si alguien escribiera una comilla en la caja de búsqueda, podría
            cerrar la cadena y añadir instrucciones propias.

            Aquí se hace **una cosa concreta** para evitarlo:

            ```python
            palabra.value.replace("'", "''")
            ```

            Duplicar cada comilla simple hace que SQL la lea como *un carácter del texto*
            en vez de como *el fin del texto*. Si escribes `' OR 1=1 --` en la caja, la
            consulta busca literalmente esa cadena y devuelve cero resultados, en vez de
            ejecutarla. **Pruébalo.**

            El dropdown de orden es seguro por otra razón: el alumno **no escribe** el
            valor, elige entre tres opciones que definimos nosotros. Eso es una
            **lista blanca**.

            En un sistema de verdad no se escapa a mano: se usan **consultas
            parametrizadas**, donde el valor viaja aparte y el motor nunca lo confunde con
            instrucciones. La regla: **el texto del usuario es un dato, nunca es código.**
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 7. Tu espacio libre

    Esta celda no tiene consigna: borra lo que hay y escribe lo que se te ocurra.

    Ideas para arrancar:

    - `SELECT text FROM comentarios WHERE insult > 3 LIMIT 10`
    - `SELECT text, respect FROM comentarios ORDER BY respect ASC LIMIT 5`
    - `SELECT count(*) FROM comentarios WHERE target_religion = true`
    """)
    return


@app.cell
def _(comentarios, mo):
    espacio_libre = mo.sql(
        f"""
        SELECT text, hate_speech_score
        FROM comentarios
        WHERE text ILIKE '%school%'
        LIMIT 10
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 8. Ejercicios

    En cada uno, **borra la consulta de ejemplo y escribe la tuya**. La solución está
    escondida debajo: inténtalo antes de abrirla.

    ### Ejercicio 1 — Los más irrespetuosos

    Muestra el **texto** y el `respect` de los **5 comentarios con menor nivel de
    respeto**.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_1 = mo.sql(
        f"""
        -- Escribe aquí tu consulta y ejecútala con Ctrl+Enter
        SELECT text, respect
        FROM comentarios
        LIMIT 3
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 1": mo.md("""
            ```sql
            SELECT text, respect
            FROM comentarios
            ORDER BY respect ASC
            LIMIT 5
            ```

            `ASC` ordena de menor a mayor. Es el comportamiento por omisión, pero
            escribirlo hace explícita tu intención.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 2 — Buscar y filtrar a la vez

    Encuentra comentarios que contengan la palabra **women** y cuyo `hate_speech_score`
    sea mayor a 1. Muestra `text` y `hate_speech_score`, los 10 más altos primero.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_2 = mo.sql(
        f"""
        -- Escribe aquí tu consulta
        SELECT text, hate_speech_score
        FROM comentarios
        LIMIT 3
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 2": mo.md("""
            ```sql
            SELECT text, hate_speech_score
            FROM comentarios
            WHERE text ILIKE '%women%'
              AND hate_speech_score > 1
            ORDER BY hate_speech_score DESC
            LIMIT 10
            ```

            `ILIKE` para que no importen las mayúsculas, `AND` para exigir las dos
            condiciones, y `ORDER BY ... DESC` con `LIMIT` para quedarte con el top.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 3 — Contar sin repetir

    ¿Cuántos **comentarios distintos** hay con `hate_speech_score` mayor a 2?

    Cuidado con la trampa de la sección 3: si cuentas filas, cuentas de más.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_3 = mo.sql(
        f"""
        -- Escribe aquí tu consulta
        SELECT count(*) AS mi_intento
        FROM comentarios
        WHERE hate_speech_score > 2
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 3": mo.md("""
            ```sql
            SELECT count(DISTINCT comment_id) AS comentarios
            FROM comentarios
            WHERE hate_speech_score > 2
            ```

            Con `count(*)` salen **20,338**, que son filas. Los comentarios distintos son
            **2,086**. Casi diez veces menos: ese es el tamaño del error que se comete al
            confundir la unidad de análisis.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 4 — Investiga por tu cuenta

    Este no tiene una respuesta única. Elige un comentario que te haya llamado la atención
    en cualquiera de las búsquedas anteriores, anota su `comment_id`, y muestra **todas sus
    evaluaciones**.

    Después pregúntate: ¿coincidieron las personas que lo evaluaron? ¿En qué sí y en qué no?
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_4 = mo.sql(
        f"""
        -- Cambia el número por el comment_id que hayas elegido
        SELECT annotator_id, respect, insult, target_race
        FROM comentarios
        WHERE comment_id = 4602
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Pista para el ejercicio 4": mo.md("""
            Para encontrar comentarios con muchas evaluaciones:

            ```sql
            SELECT comment_id, count(*) AS n
            FROM comentarios
            GROUP BY comment_id
            ORDER BY n DESC
            LIMIT 10
            ```

            Lo interesante no es el SQL, sino lo que muestra: personas distintas leyendo
            exactamente el mismo texto y llegando a conclusiones distintas.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### ¡Terminaste! 🎉

        Te llevas:

        - Las cinco piezas: `SELECT`, `FROM`, `WHERE`, `ORDER BY`, `LIMIT`.
        - Que se **escribe** empezando por `SELECT` pero se **ejecuta** empezando por
          `FROM` — y que de ahí salen la mitad de los errores.
        - `LIKE` / `ILIKE` para buscar texto.
        - `count(*)` frente a `count(DISTINCT ...)`, y por qué confundirlos multiplica
          tus números.
        - Y lo que no es sintaxis: **saber qué representa una fila** antes de contar nada.

        En el siguiente notebook: agrupar, resumir y cruzar tablas.
        """),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
