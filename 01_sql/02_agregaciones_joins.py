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
    def mostrar(_tabla, consulta: str, filas: int = 10):
        """Muestra la consulta SQL tal cual, y debajo su resultado.

        Existe para que el alumno LEA el SQL. Ver la nota en 01_introduccion_sql.py
        sobre por qué no usamos la bandera `--show-code` del export.

        `_tabla` no se usa: está en la firma para que marimo sepa que esta celda
        depende de esa tabla y la ejecute después de crearla.
        """
        resultado = mo.sql(consulta, output=False)
        return mo.vstack(
            [
                mo.md(f"```sql\n{consulta.strip()}\n```"),
                mo.md(f"→ **{len(resultado)} filas**"),
                mo.ui.table(resultado, selection=None, page_size=filas),
            ]
        )

    return (mostrar,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Agregaciones y JOINs 🦆

    En el notebook anterior aprendimos a **elegir** filas y columnas. Ahora vamos a
    **resumir**: contar, promediar, agrupar, y finalmente **cruzar tablas**.

    Igual que antes, cada consulta se arma **pieza por pieza**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ## 🚦 Antes que nada: enciende el notebook

        Igual que en el notebook anterior, esta página abre **apagada**.

        ### 👉 Presiona `Ctrl` + `Shift` + `R` para ejecutar todo

        Tarda cerca de medio minuto la primera vez. Después, `Ctrl` + `Enter` ejecuta la
        celda donde tengas el cursor, y puedes cambiar cualquier consulta para ver qué pasa.
        """),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        **Aviso de contenido.** El corpus contiene insultos y lenguaje ofensivo explícito.
        Todos los ejercicios de este notebook se resuelven con columnas numéricas: **no
        hace falta leer la columna `text`**.
        """),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(DATA_URL, mo):
    tabla_anotaciones = mo.sql(
        f"""
        CREATE OR REPLACE TABLE anotaciones AS
        SELECT * FROM read_parquet('{DATA_URL}')
        """,
        output=False,
    )
    return (tabla_anotaciones,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 0. Recordatorio: cada fila es una evaluación

    Le pusimos a la tabla el nombre **`anotaciones`** en vez de `comentarios`, porque eso
    es lo que realmente contiene: cada fila es **una persona evaluando un comentario**.
    Un mismo comentario aparece en varias filas.

    Esto va a importar muchísimo hoy, porque en cuanto empiezas a **contar**, contar mal
    la unidad es el error más caro que existe.

    Para poder trabajar bien, vamos a separar la tabla en las tres cosas distintas que
    tiene mezcladas. Fíjate en el `DISTINCT`: es lo que colapsa las filas repetidas.
    """)
    return


@app.cell
def _(anotaciones, mo):
    tabla_comentarios = mo.sql(
        """
        -- Un renglón por COMENTARIO (sus datos se repetían en cada evaluación)
        CREATE OR REPLACE TABLE comentarios AS
        SELECT DISTINCT comment_id, text, platform AS platform_id, hate_speech_score
        FROM anotaciones
        """,
        output=False,
    )
    return (tabla_comentarios,)


@app.cell
def _(anotaciones, mo):
    tabla_anotadores = mo.sql(
        """
        -- Un renglón por PERSONA que evaluó
        CREATE OR REPLACE TABLE anotadores AS
        SELECT DISTINCT annotator_id, annotator_gender, annotator_educ, annotator_ideology
        FROM anotaciones
        """,
        output=False,
    )
    return (tabla_anotadores,)


@app.cell
def _(mo):
    tabla_plataformas = mo.sql(
        """
        -- Catálogo de plataformas.
        -- ⚠️ El dataset trae 4 códigos numéricos y NO publica el diccionario que dice
        -- cuál es cuál. No los inventamos: los marcamos como sin documentar.
        CREATE OR REPLACE TABLE plataformas AS
        SELECT * FROM (VALUES
            (0, 'Sin documentar (código 0)'),
            (1, 'Sin documentar (código 1)'),
            (2, 'Sin documentar (código 2)'),
            (3, 'Sin documentar (código 3)')
        ) AS t(platform_id, nombre)
        """,
        output=False,
    )
    return (tabla_plataformas,)


@app.cell(hide_code=True)
def _(mostrar, tabla_anotaciones, tabla_anotadores, tabla_comentarios, tabla_plataformas):
    mostrar(
        tabla_anotaciones,
        """
        SELECT 'anotaciones (evaluaciones)' AS tabla, count(*) AS filas FROM anotaciones
        UNION ALL SELECT 'comentarios',  count(*) FROM comentarios
        UNION ALL SELECT 'anotadores',   count(*) FROM anotadores
        UNION ALL SELECT 'plataformas',  count(*) FROM plataformas
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Funciones de agregación: de muchas filas a un número

    Una función de agregación toma **muchas filas y devuelve una sola**.

    La trampa está en `COUNT`, que tiene tres formas que **no** significan lo mismo:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_anotaciones):
    mostrar(
        tabla_anotaciones,
        """
        SELECT
            count(*)                     AS todas_las_filas,
            count(annotator_ideology)    AS filas_con_ideologia_no_nula,
            count(DISTINCT comment_id)   AS comentarios_diferentes
        FROM anotaciones
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tres números muy distintos sobre la misma tabla:

    | Forma | Qué cuenta |
    |---|---|
    | `count(*)` | **Filas**, sin más |
    | `count(columna)` | Filas donde esa columna **no es nula** |
    | `count(DISTINCT columna)` | **Valores diferentes** |

    Si alguien te pregunta "¿cuántos comentarios hay?" y contestas con `count(*)`, tu
    respuesta está inflada por las evaluaciones repetidas. La correcta es
    `count(DISTINCT comment_id)`.

    Las otras agregaciones habituales: `AVG` (promedio), `SUM`, `MIN`, `MAX`.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            count(*)                        AS comentarios,
            round(avg(hate_speech_score), 3) AS promedio,
            round(min(hate_speech_score), 2) AS minimo,
            round(max(hate_speech_score), 2) AS maximo
        FROM comentarios
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. `GROUP BY`, pieza por pieza

    `GROUP BY` parte la tabla en montones y aplica la agregación **a cada montón por
    separado**. Vamos a construir la consulta agregando una pieza a la vez.

    ### Pieza 1 — un solo número para todo
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT count(*) AS comentarios
        FROM comentarios
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 2 — `GROUP BY`: el mismo cálculo, pero por plataforma

    La regla de oro: **todo lo que va en el `SELECT` y no está dentro de una función de
    agregación, tiene que aparecer en el `GROUP BY`.**
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            platform_id,              -- 👈 columna nueva...
            count(*) AS comentarios
        FROM comentarios
        GROUP BY platform_id          -- 👈 ...y por eso tiene que ir aquí
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 3 — agregar un promedio y ordenar
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            platform_id,
            count(*)                         AS comentarios,
            round(avg(hate_speech_score), 3) AS score_promedio  -- 👈 pieza nueva
        FROM comentarios
        GROUP BY platform_id
        ORDER BY comentarios DESC                               -- 👈 pieza nueva
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### 🧭 Una consulta correcta que no permite concluir nada

        Esa consulta corre, los números son exactos... **y no significan nada.**

        `platform_id` vale 0, 1, 2 o 3, y el dataset **nunca publicó** el diccionario que
        dice qué plataforma es cada número. Podemos afirmar que el grupo 1 tiene más
        comentarios que el 3, pero no podemos decir *"en Twitter hay más odio que en
        Reddit"*, porque no sabemos cuál es cuál.

        Es tentador buscar en internet, encontrar que el paper menciona tres plataformas y
        asignarlas a ojo. **No lo hagas**: hay cuatro códigos y tres nombres, así que
        cualquier asignación sería inventada, y a partir de ahí todo tu análisis sería
        falso sin que nadie lo note.

        **La lección:** una columna sin diccionario te deja *contar*, pero no *concluir*.
        Saber distinguir esas dos cosas es lo que separa a alguien que sabe SQL de alguien
        que sabe analizar datos.
        """),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Un `GROUP BY` que sí concluye algo

    Aquí sí sabemos qué significa cada grupo, porque `annotator_ideology` viene con
    etiquetas legibles. Agrupamos las **evaluaciones** por la ideología de quien evaluó:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_anotaciones):
    mostrar(
        tabla_anotaciones,
        """
        SELECT
            annotator_ideology,
            count(*)                AS evaluaciones,
            round(avg(respect), 2)  AS respeto_promedio,
            round(avg(insult), 2)   AS insulto_promedio
        FROM anotaciones
        GROUP BY annotator_ideology
        ORDER BY evaluaciones DESC
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ¿Ves el renglón con `annotator_ideology` vacío? Ese es un **NULL**: una evaluación
    cuyo anotador no reportó ideología. `GROUP BY` le hace su propio grupo en lugar de
    ignorarlo, y hace bien: esconder los datos faltantes es una manera clásica de mentir
    con estadísticas sin darse cuenta.

    ## 3. `HAVING`: filtrar los grupos

    `WHERE` y `HAVING` filtran en momentos distintos:

    ```
    WHERE   →  descarta FILAS      →  antes de agrupar
    GROUP BY →  arma los montones
    HAVING  →  descarta GRUPOS     →  después de agrupar
    ```

    Por eso `HAVING` puede usar `count(*)` y `WHERE` no: cuando `WHERE` se ejecuta,
    los grupos todavía no existen.

    Busquemos los comentarios **más evaluados**: los que recibieron más de 100 opiniones.
    Son los 70 del conjunto de calibración que descubrimos en el notebook anterior.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_anotaciones):
    mostrar(
        tabla_anotaciones,
        """
        SELECT
            comment_id,
            count(*)                          AS cuantas_evaluaciones,
            count(DISTINCT target_race)       AS opiniones_distintas_sobre_raza,
            round(avg(respect), 2)            AS respeto_promedio
        FROM anotaciones
        GROUP BY comment_id
        HAVING count(*) > 100
        ORDER BY cuantas_evaluaciones DESC
        LIMIT 10
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        **Si un `HAVING` te devuelve una tabla vacía, no siempre es tu culpa.**

        Aquí agrupamos por **comentario**. Si en cambio agrupas por **anotador** y pides
        `HAVING count(*) > 50`, obtienes **cero filas** — y tu SQL está perfecto.

        La razón está en los datos, no en la consulta: el corpus se construyó pidiéndole a cada
        anotador que evaluara unas pocas decenas de comentarios, no cientos. Ningún anotador supera las **26** evaluaciones
        aquí, aunque en el corpus completo tengan cientos.

        **Ante un resultado vacío, la pregunta correcta no es "¿qué escribí mal?" sino
        "¿es esto posible con estos datos?"**. Se comprueba quitando el filtro y mirando
        la distribución real, que es justo lo que hace la consulta de abajo.
        """),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_anotaciones):
    mostrar(
        tabla_anotaciones,
        """
        -- ¿Cuántas evaluaciones hizo cada persona, como máximo?
        SELECT
            max(evaluaciones)            AS maximo_por_anotador,
            round(avg(evaluaciones), 2)  AS promedio_por_anotador
        FROM (
            SELECT annotator_id, count(*) AS evaluaciones
            FROM anotaciones
            GROUP BY annotator_id
        )
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. `CASE WHEN`: crear categorías

    `CASE WHEN` es el `if / else if / else` de SQL. Evalúa las condiciones **en orden** y
    se queda con la primera que se cumple.

    Los cortes no los inventamos: el score es continuo y **no trae una línea marcada**.
    En esta clase usamos **0.5** para el lado del odio y **−1** para el del apoyo, igual
    que en el notebook anterior. Son decisiones nuestras, no del dataset.

    Por eso todo resultado que publiques debe decir qué umbral usaste: cambia el número
    y cambian tus conclusiones.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            CASE
                WHEN hate_speech_score > 0.5 THEN 'Discurso de odio'
                WHEN hate_speech_score < -1  THEN 'Apoyo o contra-discurso'
                ELSE 'Neutral o ambiguo'
            END                AS categoria,
            count(*)           AS comentarios,
            round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS porcentaje
        FROM comentarios
        GROUP BY categoria
        ORDER BY comentarios DESC
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Subconsultas: una consulta dentro de otra

    Cuando necesitas un valor calculado para poder filtrar, lo pides en una consulta
    anidada. Aquí: los comentarios que superan el promedio general.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT comment_id, hate_speech_score
        FROM comentarios
        WHERE hate_speech_score > (
            SELECT avg(hate_speech_score) FROM comentarios   -- 👈 se calcula primero
        )
        ORDER BY hate_speech_score DESC
        LIMIT 5
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. CTEs (`WITH`): consultas por pasos

    Cuando una consulta crece, anidarla se vuelve ilegible. Un **CTE** te deja nombrar
    resultados intermedios y encadenarlos, de arriba hacia abajo. Es la misma idea de
    "pieza por pieza", pero dentro de una sola consulta.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_anotaciones):
    mostrar(
        tabla_anotaciones,
        """
        WITH acuerdo_por_comentario AS (
            -- Paso 1: para cada comentario, cuánta gente lo evaluó y si hubo desacuerdo
            SELECT
                comment_id,
                count(*)                    AS evaluaciones,
                count(DISTINCT target_race) AS opiniones_sobre_raza
            FROM anotaciones
            GROUP BY comment_id
        ),
        solo_los_discutidos AS (
            -- Paso 2: nos quedamos con los que tuvieron desacuerdo real
            SELECT *
            FROM acuerdo_por_comentario
            WHERE evaluaciones >= 10
              AND opiniones_sobre_raza > 1
        )
        -- Paso 3: la respuesta
        SELECT * FROM solo_los_discutidos
        ORDER BY evaluaciones DESC
        LIMIT 10
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. JOINs: cruzar tablas

    Al principio partimos la tabla original en tres (`comentarios`, `anotadores`,
    `plataformas`). Un **JOIN** las vuelve a unir cuando lo necesitamos.

    ### Pieza 1 — el JOIN más simple: traer una etiqueta de un catálogo

    `ON` dice **por cuál columna** se emparejan las filas.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios, tabla_plataformas):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            p.nombre        AS plataforma,
            count(*)        AS comentarios
        FROM comentarios AS c
        JOIN plataformas AS p ON c.platform_id = p.platform_id   -- 👈 la llave
        GROUP BY p.nombre
        ORDER BY comentarios DESC
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 2 — el error que más caro se paga: el *fan-out*

    Cuando unes una tabla donde la llave es única (`comentarios`) con una donde **se
    repite** (`anotaciones`), las filas **se multiplican**. A eso se le llama *fan-out*.

    Contémoslo:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_anotaciones, tabla_comentarios):
    mostrar(
        tabla_anotaciones,
        """
        SELECT
            (SELECT count(*) FROM comentarios)             AS filas_antes_del_join,
            (SELECT count(*) FROM comentarios c
               JOIN anotaciones a ON c.comment_id = a.comment_id) AS filas_despues_del_join,
            (SELECT count(DISTINCT c.comment_id) FROM comentarios c
               JOIN anotaciones a ON c.comment_id = a.comment_id) AS comentarios_distintos
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pasamos de **39,565 filas a 135,556**, pero siguen siendo los mismos 39,565 comentarios.
    El JOIN no inventó comentarios: repitió cada uno tantas veces como evaluaciones tiene.

    Y aquí está el peligro: si ahora calculas `avg(hate_speech_score)` sobre el resultado,
    **los comentarios más evaluados pesan más que los demás**, porque aparecen más veces.
    Tu promedio sale mal y la consulta no da ningún error.

    > **Regla práctica:** si vas a promediar un atributo del lado que *no* se repite,
    > **agrega antes de unir**, no después.

    ### Pieza 3 — `INNER` contra `LEFT`

    Un `JOIN` normal (`INNER`) **descarta** las filas que no encuentran pareja. Un
    `LEFT JOIN` conserva todas las de la izquierda y rellena con `NULL` las que no
    emparejaron.

    La diferencia se ve cuando hay filas sin pareja. Tomemos los comentarios que **algún**
    anotador marcó como `target_race`: son 14,697 de 39,565. Los otros 24,868 no tienen pareja.
    """)
    return


@app.cell
def _(anotaciones, mo):
    tabla_marcados_por_raza = mo.sql(
        """
        CREATE OR REPLACE TABLE marcados_por_raza AS
        SELECT comment_id, count(*) AS veces_marcado
        FROM anotaciones
        WHERE target_race = true
        GROUP BY comment_id
        """,
        output=False,
    )
    return (tabla_marcados_por_raza,)


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios, tabla_marcados_por_raza):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            (SELECT count(*) FROM comentarios c
               JOIN marcados_por_raza m ON c.comment_id = m.comment_id)      AS con_inner_join,
            (SELECT count(*) FROM comentarios c
               LEFT JOIN marcados_por_raza m ON c.comment_id = m.comment_id) AS con_left_join
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `INNER` devuelve 14,697: solo los que alguien marcó. `LEFT` devuelve los 39,565: conserva
    también los que nadie marcó, con `NULL` en las columnas de la derecha.

    **Cuál usar depende de la pregunta.** Si preguntas "¿cuántas veces se marcó cada
    comentario?", el `INNER` te da una respuesta sesgada: **desaparecen los ceros**, y el
    promedio sale inflado.

    Los `NULL` se traducen a `0` con `COALESCE`, que devuelve el primer valor no nulo:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios, tabla_marcados_por_raza):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            c.comment_id,
            COALESCE(m.veces_marcado, 0) AS veces_marcado   -- 👈 NULL se vuelve 0
        FROM comentarios AS c
        LEFT JOIN marcados_por_raza AS m ON c.comment_id = m.comment_id
        ORDER BY veces_marcado ASC
        LIMIT 5
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Ejercicios

    Escribe tu consulta y **haz clic fuera del editor** (o `Ctrl+Enter`) para ejecutarla.
    Intenta resolverlos antes de abrir la solución.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    import re

    def ejecutar(consulta: str):
        texto = (consulta or "").strip()
        util = [
            ln for ln in texto.splitlines() if ln.strip() and not ln.strip().startswith("--")
        ]
        if not util:
            return mo.callout(mo.md("Escribe tu consulta en el editor de arriba."), kind="neutral")

        # Envolverla en un SELECT la vuelve de solo lectura: un DROP o un DELETE
        # deja de ser válido dentro de un FROM y falla sin tocar las tablas.
        blindada = f"SELECT * FROM (\n{re.sub(r';\s*$', '', texto)}\n) AS r LIMIT 500"
        try:
            resultado = mo.sql(blindada, output=False)
        except Exception as e:
            return mo.callout(
                mo.md(f"**Tu consulta tiene un error**\n\n```\n{e}\n```"), kind="danger"
            )
        if len(resultado) == 0:
            return mo.callout(
                mo.md(
                    "Corrió bien pero **no devolvió filas**. ¿Es posible el resultado "
                    "que pediste con estos datos? Prueba quitando el filtro."
                ),
                kind="warn",
            )
        return mo.vstack(
            [
                mo.md(f"*{len(resultado)} filas*"),
                mo.ui.table(resultado, selection=None, page_size=10),
            ]
        )

    def solucion(sql: str, explicacion: str = ""):
        cuerpo = f"```sql\n{sql.strip()}\n```"
        if explicacion:
            cuerpo += f"\n\n{explicacion}"
        return mo.accordion({"🔑 Ver solución": mo.md(cuerpo)})

    return ejecutar, solucion


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Ejercicio 1 — Promedios por grupo

    Usando `anotaciones`, calcula el promedio de `respect` y de `insult` agrupando por
    `target_gender` (verdadero o falso). Redondea a 2 decimales.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej1 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej1
    return (ej1,)


@app.cell(hide_code=True)
def _(ej1, ejecutar):
    ejecutar(ej1.value)
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT
            target_gender,
            round(avg(respect), 2) AS respeto_promedio,
            round(avg(insult), 2)  AS insulto_promedio
        FROM anotaciones
        GROUP BY target_gender
        """,
        "Recuerda: `target_gender` va en el `GROUP BY` porque está en el `SELECT` "
        "sin estar dentro de una función de agregación.",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Ejercicio 2 — `HAVING` sobre comentarios

    Encuentra los comentarios que recibieron **20 o más evaluaciones** y cuyo
    `respect` promedio es menor a 2. Muestra `comment_id`, el conteo y el promedio,
    ordenados del menos respetuoso al más.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej2 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej2
    return (ej2,)


@app.cell(hide_code=True)
def _(ej2, ejecutar):
    ejecutar(ej2.value)
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT
            comment_id,
            count(*)               AS evaluaciones,
            round(avg(respect), 2) AS respeto_promedio
        FROM anotaciones
        GROUP BY comment_id
        HAVING count(*) >= 20 AND avg(respect) < 2
        ORDER BY respeto_promedio ASC
        """,
        "Las dos condiciones van en el `HAVING` porque ambas dependen de una "
        "agregación. Agrupamos por **comentario**, no por anotador: por anotador "
        "daría vacío, como vimos arriba.",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Ejercicio 3 — JOIN con el catálogo

    Cruza `comentarios` con `plataformas` y muestra, por plataforma, cuántos comentarios
    hay y cuántos de ellos son discurso de odio (`hate_speech_score > 0.5`).

    *Pista: `sum(CASE WHEN condición THEN 1 ELSE 0 END)` cuenta cuántas filas cumplen algo.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej3 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej3
    return (ej3,)


@app.cell(hide_code=True)
def _(ej3, ejecutar):
    ejecutar(ej3.value)
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT
            p.nombre AS plataforma,
            count(*) AS comentarios,
            sum(CASE WHEN c.hate_speech_score > 0.5 THEN 1 ELSE 0 END) AS con_odio
        FROM comentarios AS c
        JOIN plataformas AS p ON c.platform_id = p.platform_id
        GROUP BY p.nombre
        ORDER BY comentarios DESC
        """,
        "Y recuerda la lección de gobernanza: puedes reportar estos conteos, pero "
        "**no** puedes decir en qué red social pasa qué, porque no existe el "
        "diccionario de códigos.",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### Lo que te llevas de este notebook 🎉

        - `count(*)`, `count(col)` y `count(DISTINCT col)` responden **preguntas distintas**.
        - `WHERE` filtra filas; `HAVING` filtra grupos, después de agrupar.
        - Un resultado vacío puede ser culpa de los **datos**, no de tu SQL.
        - Un JOIN con una tabla que repite la llave **multiplica filas** (*fan-out*), y
          arruina los promedios en silencio.
        - `INNER` borra los que no emparejan; `LEFT` + `COALESCE` conserva los ceros.
        - Y la más importante: una consulta correcta puede no autorizar ninguna conclusión.
        """),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
