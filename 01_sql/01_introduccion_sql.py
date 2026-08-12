import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    # En local es una ruta de disco; en el navegador (WASM) es una URL del sitio.
    # DuckDB lee las dos.
    DATA_URL = str(mo.notebook_location() / "public" / "sample_data.parquet")
    return (DATA_URL,)


@app.cell(hide_code=True)
def _(mo):
    def mostrar(_tabla, consulta: str, filas: int = 10):
        """Muestra la consulta SQL tal cual, y debajo su resultado.

        Existe para que el alumno LEA el SQL. No usamos la bandera `--show-code` del
        export porque esa ignora los `hide_code=True` y acabaría enseñando también el
        andamiaje de Python y las soluciones de los ejercicios.

        `_tabla` no se usa dentro de la función: está en la firma para que marimo sepa
        que esta celda depende de esa tabla y la ejecute después de crearla. marimo
        deduce las dependencias leyendo el código, y aquí el nombre de la tabla vive
        dentro de un string, donde no puede verlo.
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
    # Introducción a SQL con DuckDB 🦆

    Bienvenida/o a **Ciencia de Datos para la Toma de Decisiones II**.

    Hoy aprendemos **SQL**, el lenguaje con el que se le pregunta cosas a una base de
    datos. La idea de esta clase no es que memorices comandos, sino que veas cómo una
    consulta **se arma por pedazos**: empiezas con algo mínimo y le vas agregando piezas
    hasta que responde justo lo que querías.

    En cada paso vas a ver **el SQL exacto** que se ejecutó y el resultado que produjo.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        **Aviso sobre el contenido.** Vamos a trabajar con el corpus *Measuring Hate
        Speech* de UC Berkeley. Son comentarios reales de redes sociales y **contienen
        insultos y lenguaje ofensivo explícito**. No están censurados a propósito: son el
        objeto de estudio, y esconderlos haría imposible el análisis.

        Todos los ejercicios se pueden resolver **sin abrir la columna `text`**. Si
        prefieres no leer los comentarios, trabaja con las columnas numéricas.
        """),
        kind="warn",
    )
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
    mo.md(f"¡Hola **{nombre_alumno.value or 'estudiante'}**! Empecemos. 👇")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Cargar los datos

    Los datos están en un archivo **Parquet**, un formato de almacenamiento por columnas
    muy eficiente para análisis. Con una sola instrucción lo convertimos en una tabla
    llamada `comentarios` que ya podemos consultar:

    ```sql
    CREATE OR REPLACE TABLE comentarios AS
    SELECT * FROM read_parquet('.../sample_data.parquet')
    ```
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
def _(mo):
    mo.md(r"""
    ## 2. Lo más importante de esta clase: ¿qué es una fila?

    Antes de escribir una sola consulta hay que entender **qué representa cada fila**.
    Si te equivocas aquí, todas tus consultas darán números que parecen correctos pero
    responden a otra pregunta.

    En esta tabla, **cada fila NO es un comentario. Cada fila es la evaluación que una
    persona hizo sobre un comentario.**

    El corpus se armó así: se tomaron comentarios de redes sociales y **varias personas
    distintas** (anotadores) evaluaron cada uno. Si 5 personas evaluaron el mismo
    comentario, ese comentario aparece en **5 filas**.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        -- ¿Cuántas filas hay, y cuántos comentarios distintos?
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
    Hay muchas más filas que comentarios. Esa diferencia es la que hay que tener en la
    cabeza todo el tiempo.

    ### Tres tipos de columna

    | Tipo | Ejemplos | ¿De quién es el dato? |
    |---|---|---|
    | Del **comentario** | `text`, `platform`, `hate_speech_score` | Se repite igual en todas las filas del mismo comentario |
    | De la **persona** que evaluó | `annotator_gender`, `annotator_ideology` | Se repite en todas las filas de ese anotador |
    | De la **evaluación** | `target_race`, `respect`, `insult`, `sentiment` | Cambia entre filas del mismo comentario |

    ⚠️ **Ojo con `target_race` y sus hermanas.** No dicen "este comentario ataca por
    motivos de raza". Dicen: **"esta persona en particular consideró que el comentario
    ataca por motivos de raza"**. Y los anotadores **no siempre coinciden**.

    Eso no es un error del dataset: es su hallazgo central. Cuando algo es ofensivo o no
    depende de quién lo lee, y el corpus se diseñó justamente para medir ese desacuerdo.
    Volveremos a esto en el último ejercicio.

    En cambio `hate_speech_score` **sí es del comentario**: es un puntaje calculado
    combinando todas sus evaluaciones. Por eso se repite idéntico en todas sus filas.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Armando una consulta pieza por pieza

    Aquí está el corazón de la clase. Vamos a construir **una sola consulta**, agregándole
    una pieza a la vez. Lee el SQL de cada paso y fíjate en qué cambia en el resultado.

    ### Pieza 1 — `SELECT` y `FROM`: qué columnas y de dónde

    Lo mínimo que necesita una consulta: **qué** quieres ver (`SELECT`) y **de dónde**
    (`FROM`). El `*` significa "todas las columnas".
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
    Son 143 columnas: demasiadas para entender nada. **Pedir solo lo que necesitas** no es
    solo buena práctica, es lo que hace legible el resultado.

    ### Pieza 2 — nombrar las columnas en lugar de `*`
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            comment_id,
            hate_speech_score,
            target_race
        FROM comentarios
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 3 — `WHERE`: quedarnos solo con algunas filas

    `WHERE` es un filtro: solo pasan las filas que cumplen la condición.

    ¿Qué umbral usar en `hate_speech_score`? No lo inventamos: **los autores del corpus
    documentan que por encima de `0.5` el comentario es aproximadamente discurso de odio**,
    y por debajo de `-1` es discurso de apoyo o contra-discurso. En medio queda la zona
    ambigua.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            comment_id,
            hate_speech_score,
            target_race
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
    ### Pieza 4 — `AND`: dos condiciones a la vez

    Con `AND` exigimos que se cumplan ambas. Con `OR` bastaría con una.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            comment_id,
            hate_speech_score,
            target_race
        FROM comentarios
        WHERE hate_speech_score > 0.5
          AND target_race = true           -- 👈 la pieza nueva
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 5 — `ORDER BY`: poner orden

    Hasta ahora las 5 filas que veíamos eran **cualesquiera**. Sin `ORDER BY`, la base de
    datos no promete ningún orden: puede devolverte filas distintas cada vez que corras la
    misma consulta. Si el orden te importa, tienes que pedirlo.

    `DESC` es de mayor a menor; `ASC` (el default) de menor a mayor.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            comment_id,
            hate_speech_score,
            target_race
        FROM comentarios
        WHERE hate_speech_score > 0.5
          AND target_race = true
        ORDER BY hate_speech_score DESC    -- 👈 la pieza nueva
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### La consulta completa, y el orden en que se escribe

    Esas cinco piezas son la consulta terminada. **El orden de las cláusulas no es
    negociable**: si escribes `WHERE` antes que `FROM`, es un error de sintaxis.

    ```sql
    SELECT   columnas          -- 1. qué quiero ver
    FROM     tabla             -- 2. de dónde lo saco
    WHERE    condición         -- 3. con qué filas me quedo
    ORDER BY columna DESC      -- 4. en qué orden las muestro
    LIMIT    n                 -- 5. cuántas muestro
    ```

    Un truco para leer una consulta ajena: **empieza por el `FROM`**, no por el `SELECT`.
    Primero entiendes de dónde salen los datos, luego cómo se filtran, y al final qué
    columnas se muestran. Es el orden en que la base de datos realmente trabaja.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Buscar dentro del texto: `LIKE` e `ILIKE`

    El comodín `%` significa "cualquier cosa, o nada". Así que `'%people%'` encuentra la
    palabra en cualquier posición del texto.

    `LIKE` distingue mayúsculas de minúsculas; **`ILIKE` no** (la `I` es de
    *insensitive*). En la práctica casi siempre quieres `ILIKE`.
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        SELECT
            comment_id,
            hate_speech_score
        FROM comentarios
        WHERE text ILIKE '%people%'
        ORDER BY hate_speech_score DESC
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Exploración interactiva

    Los controles de abajo modifican la consulta **en vivo**. Muévelos y observa cómo
    cambia el SQL que aparece debajo, y con él el resultado.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    slider_score = mo.ui.slider(
        start=-5.0,
        stop=5.0,
        step=0.5,
        value=0.5,
        label="Umbral mínimo de hate_speech_score",
        show_value=True,
        full_width=True,
    )
    dropdown_objetivo = mo.ui.dropdown(
        options=["target_race", "target_religion", "target_gender", "target_origin"],
        value="target_race",
        label="Tipo de objetivo señalado por el anotador",
    )
    mo.vstack([slider_score, dropdown_objetivo], gap=1)
    return dropdown_objetivo, slider_score


@app.cell(hide_code=True)
def _(dropdown_objetivo, mostrar, slider_score, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        f"""
        SELECT
            comment_id,
            hate_speech_score,
            {dropdown_objetivo.value} AS marcado_por_el_anotador
        FROM comentarios
        WHERE hate_speech_score >= {slider_score.value}
          AND {dropdown_objetivo.value} = true
        ORDER BY hate_speech_score DESC
        LIMIT 10
        """,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "⚠️ Un momento: ¿no es peligroso meter variables dentro de una consulta?": mo.md(r"""
            Muy buena pregunta, y sí: **lo es**, en general. Pegar texto dentro de una
            consulta SQL es la puerta de entrada de la **inyección SQL**, una de las
            vulnerabilidades más viejas y más explotadas que existen.

            Si el valor viniera de una caja de texto libre, alguien podría escribir algo
            que cierre la consulta y agregue instrucciones propias.

            Aquí es seguro por una razón concreta: el valor **no lo escribe el usuario**.
            Sale de un `dropdown` con una lista cerrada de cuatro opciones que definimos
            nosotros, y del `slider`, que solo produce números. A eso se le llama
            **lista blanca**: el usuario elige entre opciones válidas, no las inventa.

            La regla práctica: si el valor viene de una lista que tú controlas, puedes
            interpolarlo. Si viene de texto libre, **nunca** lo pegues — se usan
            *consultas parametrizadas*.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Ejercicios

    Ahora te toca escribir a ti. Escribe tu consulta en el editor y **haz clic fuera de
    él** (o presiona `Ctrl+Enter`) para ejecutarla. El resultado aparece justo debajo.

    Puedes equivocarte todas las veces que quieras: no se guarda ni se califica nada.
    Cada ejercicio trae la solución escondida — **inténtalo antes de abrirla**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    import re

    def ejecutar(consulta: str):
        """Corre el SQL del alumno de forma segura y muestra el resultado o el error."""
        texto = (consulta or "").strip()
        util = [
            ln for ln in texto.splitlines() if ln.strip() and not ln.strip().startswith("--")
        ]
        if not util:
            return mo.callout(mo.md("Escribe tu consulta en el editor de arriba."), kind="neutral")

        # Envolver la consulta en un SELECT la vuelve de solo lectura: un DROP o un
        # DELETE deja de ser válido dentro de un FROM y falla sin tocar las tablas.
        blindada = f"SELECT * FROM (\n{re.sub(r';\s*$', '', texto)}\n) AS r LIMIT 500"

        try:
            resultado = mo.sql(blindada, output=False)
        except Exception as e:
            return mo.callout(
                mo.md(f"**Tu consulta tiene un error**\n\n```\n{e}\n```"), kind="danger"
            )

        if len(resultado) == 0:
            return mo.callout(
                mo.md("Corrió bien, pero **no devolvió ninguna fila**. Revisa el filtro."),
                kind="warn",
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

    return ejecutar, solucion


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Ejercicio 1 — Los más respetuosos

    Encuentra las **3 evaluaciones con mayor nivel de respeto** (columna `respect`).
    Muestra `comment_id` y `respect`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej1 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej1
    return (ej1,)


@app.cell(hide_code=True)
def _(ej1, ejecutar, tabla_comentarios):
    ejecutar(ej1.value) if tabla_comentarios is not None else None
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT comment_id, respect
        FROM comentarios
        ORDER BY respect DESC
        LIMIT 3
        """,
        "Las tres piezas de siempre: `SELECT` para las columnas, `ORDER BY ... DESC` "
        "para poner los más altos arriba, y `LIMIT` para quedarte con los primeros.",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Ejercicio 2 — Dos condiciones

    Encuentra 5 evaluaciones donde el texto contenga la palabra *stupid* **y** el puntaje
    de insulto (`insult`) sea mayor a 1. Muestra `comment_id` e `insult`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ej2 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej2
    return (ej2,)


@app.cell(hide_code=True)
def _(ej2, ejecutar, tabla_comentarios):
    ejecutar(ej2.value) if tabla_comentarios is not None else None
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT comment_id, insult
        FROM comentarios
        WHERE text ILIKE '%stupid%'
          AND insult > 1
        LIMIT 5
        """,
        "`ILIKE` en vez de `LIKE` para que no importen las mayúsculas, y `AND` "
        "para exigir las dos condiciones.",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Ejercicio 3 — El desacuerdo entre anotadores

    Este ejercicio es el más importante de la clase, porque no se trata de sintaxis.

    Elige **un solo comentario** y muestra **todas sus evaluaciones**: filtra por un
    `comment_id` concreto y muestra `annotator_id`, `target_race`, `respect` e `insult`.

    Después mira el resultado y pregúntate: **¿todas las personas evaluaron igual el
    mismo texto?**

    Para elegir un buen candidato, usa la consulta de aquí abajo:
    """)
    return


@app.cell(hide_code=True)
def _(mostrar, tabla_comentarios):
    mostrar(
        tabla_comentarios,
        """
        -- Comentarios donde los anotadores MÁS discreparon entre sí.
        -- count(DISTINCT x) cuenta cuántos valores diferentes se usaron: si da 1,
        -- todos evaluaron igual; si da más, hubo desacuerdo.
        SELECT
            comment_id,
            count(*)                     AS cuantas_evaluaciones,
            count(DISTINCT target_race)  AS opiniones_sobre_target_race,
            count(DISTINCT respect)      AS niveles_de_respect_distintos
        FROM comentarios
        GROUP BY comment_id
        HAVING count(*) >= 10
        ORDER BY niveles_de_respect_distintos DESC, cuantas_evaluaciones DESC
        LIMIT 5
        """,
        filas=5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    ej3 = mo.ui.code_editor(value="-- Tu consulta aquí\n", language="sql", debounce=True)
    ej3
    return (ej3,)


@app.cell(hide_code=True)
def _(ej3, ejecutar, tabla_comentarios):
    ejecutar(ej3.value) if tabla_comentarios is not None else None
    return


@app.cell(hide_code=True)
def _(solucion):
    solucion(
        """
        SELECT annotator_id, target_race, respect, insult
        FROM comentarios
        WHERE comment_id = 20053
        ORDER BY annotator_id
        """,
        "Puedes cambiar el `comment_id` por cualquiera de la lista de arriba.\n\n"
        "**Lo que deberías ver** con el 20053: 32 personas evaluaron el mismo texto. "
        "Unas marcaron `target_race` y otras no. En `respect` usaron **cinco** valores "
        "distintos, y en `insult`, cuatro.\n\n"
        "Eso no es ruido ni error de captura: es el resultado principal del corpus. "
        "*Si algo es ofensivo depende de quién lo lee.* Por eso `target_race` describe a "
        "la **evaluación** y no al comentario, y por eso existe `hate_speech_score`: es "
        "la forma de resumir todas esas opiniones en un solo número por comentario.\n\n"
        "Cuando en tu trabajo veas una columna que parece un hecho objetivo, pregúntate "
        "siempre quién la produjo y si otras personas habrían puesto lo mismo.",
    )
    return


@app.cell(hide_code=True)
def _(mo, nombre_alumno):
    mo.callout(
        mo.md(f"""
        ### ¡Terminaste, {nombre_alumno.value or 'estudiante'}! 🎉

        Ya sabes leer y escribir las cinco piezas básicas: `SELECT`, `FROM`, `WHERE`,
        `ORDER BY` y `LIMIT`. Y algo que no es sintaxis pero vale más: **saber qué
        representa una fila** antes de contar nada.

        En el siguiente notebook vamos a **resumir** datos: contar, promediar y agrupar.
        """),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
