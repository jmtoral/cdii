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
    import re

    def mostrar(_tabla, consulta: str, filas: int = 10):
        """Muestra la consulta SQL tal cual, y debajo su resultado.

        `_tabla` no se usa: está en la firma para que marimo sepa que esta celda
        depende de esa tabla y la ejecute después de crearla.
        """
        try:
            resultado = mo.sql(consulta, output=False)
        except Exception as e:
            return mo.vstack(
                [
                    mo.md(f"```sql\n{consulta.strip()}\n```"),
                    mo.callout(mo.md(f"**Error:**\n\n```\n{e}\n```"), kind="danger"),
                ]
            )
        return mo.vstack(
            [
                mo.md(f"```sql\n{consulta.strip()}\n```"),
                mo.md(f"→ **{len(resultado)} filas**"),
                mo.ui.table(resultado, selection=None, page_size=filas),
            ]
        )

    def ejecutar(_tabla, consulta: str):
        """Corre el SQL que escribió el alumno, de forma segura."""
        texto = (consulta or "").strip()
        util = [ln for ln in texto.splitlines() if ln.strip() and not ln.strip().startswith("--")]
        if not util:
            return mo.callout(mo.md("Escribe una consulta arriba y haz clic afuera."), kind="neutral")

        # Envolverla en un SELECT la vuelve de solo lectura: un DROP o un DELETE
        # deja de ser válido dentro de un FROM y falla sin tocar las tablas.
        blindada = f"SELECT * FROM (\n{re.sub(r';\s*$', '', texto)}\n) AS r LIMIT 500"
        try:
            resultado = mo.sql(blindada, output=False)
        except Exception as e:
            return mo.callout(
                mo.md(f"**Algo no cuadra en tu consulta**\n\n```\n{e}\n```\n\n"
                      "Tranquilo: equivocarse aquí no rompe nada."),
                kind="danger",
            )
        if len(resultado) == 0:
            return mo.callout(
                mo.md("Corrió bien, pero **no devolvió ninguna fila**. Revisa el filtro."), kind="warn"
            )
        return mo.vstack(
            [
                mo.md(f"→ **{len(resultado)} filas**"),
                mo.ui.table(resultado, selection=None, page_size=10),
            ]
        )

    def solucion(sql: str, explicacion: str = ""):
        cuerpo = f"```sql\n{sql.strip()}\n```"
        if explicacion:
            cuerpo += f"\n\n{explicacion}"
        return mo.accordion({"🔑 Ver solución": mo.md(cuerpo)})

    return ejecutar, mostrar, solucion


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Introducción a SQL con DuckDB 🦆

    Bienvenida/o a **Ciencia de Datos para la Toma de Decisiones II**.

    SQL es el lenguaje con el que se le hacen preguntas a una base de datos. Al terminar
    esta sesión vas a poder abrir una tabla que nunca has visto, entender qué contiene y
    sacarle respuestas.

    Vas a ver **el SQL exacto** de cada paso, y a partir de la sección 3 vas a escribir
    el tuyo. Todo corre aquí en tu navegador: puedes equivocarte cuantas veces quieras.
    """)
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
    trabajadores de Amazon Mechanical Turk. El corpus completo del paper tiene 50,070
    comentarios y 11,143 anotadores; nosotros usamos la versión publicada en HuggingFace.

    ### Por qué hay varias personas evaluando el mismo comentario

    Esta es la decisión de diseño más importante del corpus, y la razón de casi todo lo
    que vas a ver hoy.

    Si a cada comentario lo evaluara **una sola persona**, tendrías una etiqueta que
    parece un hecho — "esto es discurso de odio" — pero que en realidad es *la opinión de
    esa persona*, con toda su historia detrás. Alguien que ha recibido ese insulto y
    alguien que nunca lo ha oído no lo leen igual.

    Así que hicieron lo contrario: pedirle a **varias personas** que evaluaran cada
    comentario, y **medir el desacuerdo en vez de esconderlo**. Con eso pueden estimar dos
    cosas a la vez: qué tan ofensivo es un comentario, y **qué tan severo o indulgente es
    cada evaluador**, para descontarlo. En palabras del paper, ajustan
    *"la perspectiva de etiquetado de cada anotador"*.

    ### Qué es `hate_speech_score`

    No es un promedio de opiniones. Cada persona contesta **10 preguntas ordinales** sobre
    el comentario (`sentiment`, `respect`, `insult`, `humiliate`, `status`, `dehumanize`,
    `violence`, `genocide`, `attack_defend`, `hatespeech`), y todas esas respuestas se
    combinan con un modelo estadístico llamado **Rasch / teoría de respuesta al ítem**
    (el mismo tipo de modelo con el que se califican exámenes estandarizados).

    El resultado es **un número continuo por comentario**, en un espectro que el paper
    describe como *"desde genocida hasta discurso de apoyo"*. Más alto = más hostil;
    negativo = solidario o de defensa.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    nombre_alumno = mo.ui.text(
        label="**Tu nombre:**", placeholder="Nombre Apellido", full_width=True
    )
    mo.callout(nombre_alumno, kind="info")
    return (nombre_alumno,)


@app.cell(hide_code=True)
def _(mo, nombre_alumno):
    mo.md(f"¡Vamos, **{nombre_alumno.value or 'estudiante'}**! 👇")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Cargar la tabla

    Los datos viven en un archivo **Parquet**: un formato que guarda la información *por
    columnas* en vez de por filas, lo que lo hace muy rápido para análisis.

    Esta es la instrucción que carga el archivo y lo convierte en una tabla llamada
    `comentarios`, que es la que vamos a consultar todo el día:

    ```sql
    CREATE OR REPLACE TABLE comentarios AS
    SELECT * FROM read_parquet('.../hate_speech.parquet')
    ```

    Léela por partes:

    | Pedazo | Qué hace |
    |---|---|
    | `read_parquet('...')` | Abre el archivo |
    | `SELECT *` | Toma **todas** sus columnas |
    | `CREATE OR REPLACE TABLE comentarios AS` | Guarda el resultado con el nombre `comentarios` |

    `CREATE OR REPLACE` significa "créala, y si ya existía, reemplázala". Es cómodo
    porque puedes volver a ejecutarla sin que truene.

    Vamos a comprobar que cargó:
    """)
    return


@app.cell(hide_code=True)
def _(DATA_URL, mo):
    tabla_comentarios = mo.sql(
        f"""
        CREATE OR REPLACE TABLE comentarios AS
        SELECT * FROM read_parquet('{DATA_URL}')
        """,
        output=False,
    )
    return (tabla_comentarios,)


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT count(*) AS filas_cargadas
        FROM comentarios
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. ¿Qué hay dentro?

    Antes de preguntar nada hay que mirar. `SELECT *` trae **todas** las columnas, y
    `LIMIT 5` pide solo las primeras cinco filas para no ahogarnos.

    👉 En la tabla del resultado puedes **desplazarte a la derecha** para ver más
    columnas, y hacer clic en una celda de `text` para leer el comentario completo.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT *
        FROM comentarios
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Son **143 columnas**: demasiadas para mirarlas así. Veamos primero las que más
    vamos a usar, esas sí legibles:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            comment_id,
            annotator_id,
            text,
            hate_speech_score,
            respect,
            insult
        FROM comentarios
        LIMIT 8
        """,
        filas=8,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explora las 143 columnas

    `DESCRIBE` es una instrucción que no devuelve datos, sino **la lista de columnas** de
    una tabla con su tipo. Escribe abajo un pedazo de nombre para filtrarlas: prueba con
    `target`, con `annotator`, o déjalo vacío para verlas todas.
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
def _(filtro_columnas, mostrar, tabla_comentarios):
    # Duplicamos las comillas simples para que el texto del alumno no pueda
    # cerrar la cadena y modificar la consulta. Se explica en la sección 6.
    _busca = (filtro_columnas.value or "").replace("'", "''")
    mostrar(
        tabla_comentarios,
        f"""
        SELECT column_name AS columna, column_type AS tipo
        FROM (DESCRIBE comentarios)
        WHERE column_name ILIKE '%{_busca}%'
        """,
        filas=15,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. La pregunta clave: ¿por qué se repiten las filas?

    Si buscaste `annotator` habrás visto muchas columnas sobre *quién* evaluó. Eso es una
    pista de algo fundamental:

    > **Cada fila NO es un comentario. Cada fila es la evaluación que UNA persona hizo
    > sobre UN comentario.**

    El corpus se construyó pidiéndole a **varias personas distintas** que evaluaran cada
    comentario. Si a un comentario lo evaluaron 9 personas, ese comentario ocupa **9
    filas**, con el mismo texto repetido y con juicios que pueden diferir.

    Comprobémoslo contando de dos maneras:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            count(*)                     AS filas,
            count(DISTINCT comment_id)   AS comentarios_distintos,
            count(DISTINCT annotator_id) AS personas_que_evaluaron
        FROM comentarios
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **135,556 filas pero solo 39,565 comentarios.** La diferencia son las repeticiones:
    en promedio, cada comentario fue evaluado por unas 3 personas.

    `count(*)` cuenta filas. `count(DISTINCT columna)` cuenta **valores diferentes**. Si
    alguien te pregunta "¿cuántos comentarios hay?" y respondes 135,556, tu respuesta está
    inflada casi cuatro veces.

    ### Míralo con un comentario concreto

    El comentario `20014` es un caso extremo: lo evaluaron **793 personas**. Mueve el
    control para ver más o menos de sus evaluaciones, y **compara las filas entre sí**:
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


@app.cell(hide_code=True)
def _(cuantas_ver, mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
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
        """,
        filas=int(cuantas_ver.value),
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

    Cuando en tu trabajo veas una columna que parece un hecho objetivo, pregúntate quién
    la produjo y si otra persona habría escrito lo mismo.

    ### Un detalle que solo se ve mirando: aquí hay dos datasets, no uno

    ¿793 personas evaluando un comentario, cuando el promedio es 3? Eso no es casualidad.
    Contemos cuántos comentarios tiene cada cantidad de evaluaciones:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
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
        """,
        filas=12,
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
    dataset casi nunca es una sola cosa, y descubrirlo es trabajo tuyo: nadie te lo va a
    advertir.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. Tu primera consulta, pieza por pieza

    Vamos a construir **una sola consulta** agregando una pieza a la vez. Lee el SQL de
    cada paso y fíjate qué cambia en el resultado.

    ### Pieza 1 — `SELECT` y `FROM`

    Lo mínimo: **qué** quieres ver y **de dónde**. Pedir solo las columnas que necesitas
    (en vez de `*`) es lo que hace legible un resultado.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT text, hate_speech_score
        FROM comentarios
        LIMIT 5
        """,
        filas=5,
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
    apoyo. Son decisiones **nuestras**, tomadas para poder trabajar, no leyes del dataset.
    Cualquier resultado que publiques con ellas tiene que decir cuál usaste, porque si
    mueves el umbral se mueven tus conclusiones.

    Ese, y no la sintaxis, es el tipo de decisión que después hay que defender.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT text, hate_speech_score
        FROM comentarios
        WHERE hate_speech_score > 0.5      -- 👈 la pieza nueva
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 3 — `AND`: dos condiciones a la vez

    `AND` exige que se cumplan las dos. `OR` se conforma con una.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT text, hate_speech_score, insult
        FROM comentarios
        WHERE hate_speech_score > 0.5
          AND insult > 2                   -- 👈 la pieza nueva
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 4 — `ORDER BY`: poner orden

    Hasta ahora las 5 filas eran **cualesquiera**. Sin `ORDER BY` la base de datos no
    promete ningún orden y puede devolverte filas distintas cada vez. Si el orden te
    importa, **pídelo**.

    `DESC` de mayor a menor, `ASC` (el default) de menor a mayor.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT text, hate_speech_score, insult
        FROM comentarios
        WHERE hate_speech_score > 0.5
          AND insult > 2
        ORDER BY hate_speech_score DESC    -- 👈 la pieza nueva
        LIMIT 5
        """,
        filas=5,
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
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. El orden de ejecución (esto explica la mitad de los errores)

    Acabas de ver el orden en que se **escribe** una consulta. Pero la base de datos la
    **ejecuta en otro orden**, y entender eso te va a ahorrar muchísimo tiempo:

    ```
    1. FROM      →  primero busca la tabla
    2. WHERE     →  descarta filas
    3. GROUP BY  →  agrupa las que quedan        (lo verás en el notebook 2)
    4. HAVING    →  descarta grupos              (lo verás en el notebook 2)
    5. SELECT    →  recién aquí calcula las columnas
    6. ORDER BY  →  ordena el resultado
    7. LIMIT     →  y al final corta
    ```

    **Se escribe empezando por `SELECT`, pero se ejecuta empezando por `FROM`.**

    De ahí sale un consejo práctico: para entender una consulta ajena, **empieza a leerla
    por el `FROM`**, no por arriba.

    Y de ahí sale también este error, que vas a cometer tarde o temprano. `count(*)` es
    una cuenta que solo existe **después** de agrupar (paso 3), así que no puedes usarla
    en el `WHERE` (paso 2). Mira lo que pasa:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        -- ❌ Esto NO funciona: WHERE se ejecuta ANTES de agrupar,
        --    así que en ese momento count(*) todavía no existe.
        SELECT comment_id
        FROM comentarios
        WHERE count(*) > 3
        GROUP BY comment_id
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *"WHERE clause cannot contain aggregates!"* — el error te lo dice tal cual.

    La solución es `HAVING`, que es el filtro que corre **después** de agrupar. Lo verás
    a fondo en el siguiente notebook, pero aquí está funcionando:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        -- ✅ HAVING sí puede: se ejecuta DESPUÉS de agrupar
        SELECT comment_id, count(*) AS evaluaciones
        FROM comentarios
        GROUP BY comment_id
        HAVING count(*) > 3
        ORDER BY evaluaciones DESC
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🤔 Entonces, ¿por qué DuckDB me deja hacer cosas que 'no se pueden'?": mo.md(r"""
            Buena observación si lo notaste. DuckDB es más permisivo que el estándar: por
            ejemplo, te deja usar en el `WHERE` un alias que definiste en el `SELECT`,
            aunque según el orden de ejecución ese alias "todavía no existe".

            Es una comodidad de DuckDB, no una regla de SQL. **Esa misma consulta puede
            fallar** en PostgreSQL, SQL Server u Oracle.

            Moraleja: apóyate en el orden de ejecución para razonar, no en lo que tu base
            de datos te tolere hoy. El código que escribes suele sobrevivirte y acabar
            corriendo en otro motor.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. Busca lo que tú quieras

    `LIKE` compara texto usando el comodín `%`, que significa "cualquier cosa, o nada".
    Así, `'%odio%'` encuentra la palabra en cualquier posición.

    `LIKE` distingue mayúsculas de minúsculas; **`ILIKE` no** (la `I` es de *insensitive*).
    En la práctica casi siempre quieres `ILIKE`.

    **Escribe abajo la palabra que se te ocurra** y mira qué encuentra. Prueba con
    `people`, `women`, `trump`, `god`, `love`… o con lo que te dé curiosidad:
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
def _(mostrar, orden_busqueda, palabra, tabla_comentarios):
    # Duplicar las comillas simples evita que lo que escriba el alumno cierre la
    # cadena y cambie el sentido de la consulta. Ver la nota de abajo.
    _p = (palabra.value or "").replace("'", "''")
    mostrar(
        tabla_comentarios,
        f"""
        SELECT text, hate_speech_score, insult
        FROM comentarios
        WHERE text ILIKE '%{_p}%'
        ORDER BY {orden_busqueda.value}
        LIMIT 10
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "⚠️ ¿No es peligroso meter dentro de la consulta lo que escribe el usuario?": mo.md(r"""
            Sí, y es de las cosas más importantes que te vas a llevar de esta clase.

            Pegar texto de un usuario dentro de una consulta es la puerta de la
            **inyección SQL**, una de las vulnerabilidades más viejas y más explotadas que
            existen. Si alguien escribiera una comilla en la caja de búsqueda, podría
            cerrar la cadena de texto y añadir instrucciones propias a tu consulta.

            Aquí se hace **una cosa concreta** para evitarlo, y está en el código de arriba:

            ```python
            palabra.value.replace("'", "''")
            ```

            Duplicar cada comilla simple hace que SQL la lea como *un carácter dentro del
            texto* en vez de como *el fin del texto*. Si escribes `' OR 1=1 --` en la caja,
            la consulta busca literalmente esa cadena y devuelve cero resultados, en vez
            de ejecutarla.

            El dropdown de orden es un caso distinto y también seguro, pero por otra razón:
            el alumno **no escribe** el valor, solo elige entre tres opciones que definimos
            nosotros. A eso se le llama **lista blanca**.

            En un sistema de verdad no se escapa a mano: se usan **consultas
            parametrizadas**, donde el valor viaja aparte de la consulta y el motor nunca
            lo confunde con instrucciones. La regla es simple: **el texto del usuario es
            un dato, nunca es código.**
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 7. Ahora tú: escribe SQL libre

    Este es tu espacio para probar. Escribe **cualquier** consulta y haz clic fuera del
    editor (o `Ctrl+Enter`) para ejecutarla.

    Ideas para empezar:

    - `SELECT text FROM comentarios WHERE insult > 3 LIMIT 10`
    - `SELECT text, respect FROM comentarios ORDER BY respect ASC LIMIT 5`
    - `SELECT count(*) FROM comentarios WHERE target_religion = true`

    No puedes romper nada: solo se permiten consultas de lectura.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    playground = mo.ui.code_editor(
        value="SELECT text, hate_speech_score\nFROM comentarios\nWHERE text ILIKE '%school%'\nLIMIT 10",
        language="sql",
        debounce=True,
    )
    playground
    return (playground,)


@app.cell(hide_code=True)
def _(ejecutar, playground, tabla_comentarios):
    ejecutar(tabla_comentarios, playground.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 8. Ejercicios

    Ahora en serio. Cada ejercicio trae la solución escondida: **inténtalo antes de
    abrirla**, que para eso está el editor.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 1 — Los más irrespetuosos

    Muestra el **texto** y el `respect` de los **5 comentarios con menor nivel de
    respeto**. Ojo: menor significa que hay que ordenar de forma ascendente.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej1 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej1
    return (ej1,)


@app.cell(hide_code=True)
def _(ej1, ejecutar, tabla_comentarios):
    ejecutar(tabla_comentarios, ej1.value)
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT text, respect
        FROM comentarios
        ORDER BY respect ASC
        LIMIT 5
        """,
        "`ASC` ordena de menor a mayor. Como es el comportamiento por omisión, "
        "también funciona sin escribirlo — pero ponerlo hace tu intención explícita.",
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


@app.cell(hide_code=True)
def _(mo):
    ej2 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej2
    return (ej2,)


@app.cell(hide_code=True)
def _(ej2, ejecutar, tabla_comentarios):
    ejecutar(tabla_comentarios, ej2.value)
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT text, hate_speech_score
        FROM comentarios
        WHERE text ILIKE '%women%'
          AND hate_speech_score > 1
        ORDER BY hate_speech_score DESC
        LIMIT 10
        """,
        "`ILIKE` para que no importen las mayúsculas, `AND` para exigir las dos "
        "condiciones, y `ORDER BY ... DESC` con `LIMIT` para quedarte con el top.",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 3 — Contar sin repetir

    ¿Cuántos **comentarios distintos** hay con `hate_speech_score` mayor a 2?

    Cuidado con la trampa de la sección 3: si cuentas filas, vas a contar de más.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej3 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej3
    return (ej3,)


@app.cell(hide_code=True)
def _(ej3, ejecutar, tabla_comentarios):
    ejecutar(tabla_comentarios, ej3.value)
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT count(DISTINCT comment_id) AS comentarios
        FROM comentarios
        WHERE hate_speech_score > 2
        """,
        "Con `count(*)` te habrían salido **20,338**, que son filas. Los comentarios "
        "distintos son **2,086**. Casi diez veces menos: ese es el tamaño del error "
        "que se comete al confundir la unidad de análisis.",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 4 — Investiga por tu cuenta

    Este no tiene una respuesta única. Elige un comentario que te llame la atención de
    cualquiera de las búsquedas anteriores, anota su `comment_id`, y escribe una consulta
    que muestre **todas sus evaluaciones**.

    Después pregúntate: ¿coincidieron las personas que lo evaluaron? ¿En qué sí y en qué no?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej4 = mo.ui.code_editor(
        value="-- Cambia el número por el comment_id que hayas elegido\nSELECT annotator_id, respect, insult, target_race\nFROM comentarios\nWHERE comment_id = 4602",
        language="sql",
        debounce=True,
    )
    ej4
    return (ej4,)


@app.cell(hide_code=True)
def _(ej4, ejecutar, tabla_comentarios):
    ejecutar(tabla_comentarios, ej4.value)
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT annotator_id, respect, insult, target_race, hate_speech_score
        FROM comentarios
        WHERE comment_id = 4602
        ORDER BY respect
        """,
        "Para encontrar comentarios con muchas evaluaciones:\n\n"
        "```sql\nSELECT comment_id, count(*) AS n\nFROM comentarios\n"
        "GROUP BY comment_id\nORDER BY n DESC\nLIMIT 10\n```\n\n"
        "Lo interesante no es el SQL, sino lo que muestra: personas distintas leyendo "
        "exactamente el mismo texto y llegando a conclusiones distintas.",
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
