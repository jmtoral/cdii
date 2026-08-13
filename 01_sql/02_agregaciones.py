import marimo

__generated_with = "0.23.16"
# Ojo: NO poner sql_output="native". marimo lo agrega solo al abrir el notebook en su
# editor, pero con esa opción el resultado se entrega como relación de DuckDB y revienta
# con "No module named 'duckdb.typing'". El default devuelve un dataframe y funciona.
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
    # Agregaciones: contar, promediar y agrupar 🦆

    **Lección 2** de Ciencia de Datos para la Toma de Decisiones II.

    En la lección anterior aprendiste a **elegir**: qué columnas y qué filas. Hoy vas a
    **resumir**: convertir muchas filas en un número, y después en un número *por grupo*.

    Es el salto de «enséñame los datos» a «dime qué está pasando en los datos».
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
        Python y los 135 mil comentarios. Solo pasa una vez.

        | Para… | Haz esto |
        |---|---|
        | Ejecutar **una** celda | Pon el cursor dentro y `Ctrl` + `Enter` |
        | Ejecutar **todo** otra vez | `Ctrl` + `Shift` + `R` |
        | Ejecutar con el mouse | Pasa el cursor sobre la celda y usa el botón **▶** |

        **Puedes cambiar cualquier consulta.** Modifica los umbrales, las columnas, los
        grupos, y vuelve a ejecutar. Si dejas una celda hecha un desastre, recarga la
        página y todo vuelve al original.
        """),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        **Sobre el contenido.** Seguimos con el corpus *Measuring Hate Speech* de UC
        Berkeley: comentarios reales de redes sociales, **sin censurar**. Casi todo lo de
        hoy se resuelve con columnas numéricas, así que puedes trabajar sin abrir la
        columna `text` si lo prefieres.
        """),
        kind="warn",
    )
    return


# ─────────────────────────────── PASA LISTA ───────────────────────────────


@app.cell(hide_code=True)
def _():
    # ─────────────────────────────────────────────────────────────────────────
    # CONFIGURACIÓN DEL PROFESOR
    # Mismo Apps Script que recibe las entregas y la asistencia de la lección 1.
    # Se distingue por la columna `ejercicio`, que aquí dice "asistencia_02_agregaciones".
    # Instrucciones: scripts/apps_script/README.md
    # ─────────────────────────────────────────────────────────────────────────
    ENDPOINT = (
        "https://script.google.com/macros/s/"
        "AKfycbxAh7nw7L0Kt5Qnak5Dyj9nkPX4PhX1c6WykpFGL6JOyvTL0dDv2-H0qHlEvfxQZCWj4g/exec"
    )
    CURSO = "CDII"
    SESION = "asistencia_02_agregaciones"
    return CURSO, ENDPOINT, SESION


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 📋 Pasa lista

    Registra tu asistencia de esta sesión: nombre, matrícula y el botón.
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
    # Candado: marimo re-ejecuta la celda de envío cada vez que cambia algo de lo que
    # depende. Sin esto, corregir tu nombre te registraría de nuevo.
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
                    f"Quedaste en la lista, **{nombre_alumno.value}**. Vamos a agrupar. 👇"
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


# ─────────────────────────────── LOS DATOS ───────────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Recordatorio: ¿qué es una fila?

    Antes de contar nada, la pregunta de la lección pasada. En esta tabla **cada fila es
    la evaluación que una persona hizo sobre un comentario**, no un comentario.

    Hoy eso deja de ser un detalle conceptual y se vuelve la diferencia entre un número
    correcto y uno inflado.
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
    return (comentarios,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. Funciones de agregación

    Una **función de agregación** toma muchas filas y devuelve **un solo número**. Son
    cinco y con eso haces casi todo:

    | Función | Qué devuelve |
    |---|---|
    | `count(*)` | Cuántas filas hay |
    | `avg(col)` | El promedio |
    | `min(col)` / `max(col)` | El más chico y el más grande |
    | `sum(col)` | La suma de todos los valores |

    Fíjate en algo: el resultado de abajo tiene **una sola fila**. Le pediste a 135 mil
    filas que se resumieran en un renglón.
    """)
    return


@app.cell
def _(comentarios, mo):
    resumen_general = mo.sql(
        """
        SELECT
            count(*)                         AS evaluaciones,
            round(min(hate_speech_score), 2) AS mas_bajo,
            round(max(hate_speech_score), 2) AS mas_alto,
            round(avg(hate_speech_score), 3) AS promedio
        FROM comentarios
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    El puntaje va de **−8.34 a 6.30** y promedia **−0.94**: la mayoría de los comentarios
    del corpus están del lado no hostil del espectro.

    `round(x, 2)` recorta a dos decimales. No es cosmético: un promedio con catorce
    decimales sugiere una precisión que los datos no tienen.

    ### Prueba tú

    Cambia `hate_speech_score` por `respect` o por `insult` en la celda de arriba y
    ejecútala otra vez. Ambas van de 0 a 4. ¿Cuál tiene el promedio más alto?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. Las tres formas de contar (y por qué importan)

    `count` parece la función más simple del mundo. Tiene tres variantes que responden
    **preguntas distintas**, y confundirlas es el error más común del curso.
    """)
    return


@app.cell
def _(comentarios, mo):
    tres_formas = mo.sql(
        """
        SELECT
            count(*)                     AS a_todas_las_filas,
            count(annotator_ideology)    AS b_ideologia_no_nula,
            count(DISTINCT comment_id)   AS c_comentarios_distintos,
            count(DISTINCT annotator_id) AS d_personas_distintas
        FROM comentarios
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cuatro números muy distintos sobre exactamente la misma tabla:

    | Forma | Resultado | Qué cuenta |
    |---|---|---|
    | `count(*)` | 135,556 | **Filas**, sin más |
    | `count(annotator_ideology)` | 135,529 | Filas donde esa columna **no es nula** |
    | `count(DISTINCT comment_id)` | 39,565 | **Valores diferentes** de comentario |
    | `count(DISTINCT annotator_id)` | 7,912 | Personas diferentes |

    Dos cosas que sacar de aquí:

    **La diferencia entre la primera y la segunda son 27 filas.** Esas son evaluaciones
    donde el anotador no reportó su ideología. `count(columna)` **ignora los nulos en
    silencio**; `count(*)` no. Si reportas «tengo 135,529 respuestas de ideología» estás
    bien; si dices «tengo 135,556» estás contando 27 que no existen.

    **La diferencia entre la primera y la tercera es de casi cuatro veces.** Si te
    preguntan cuántos comentarios hay y contestas con `count(*)`, tu respuesta está
    inflada por las repeticiones.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. `GROUP BY`, pieza por pieza

    Hasta ahora resumimos **toda** la tabla en un número. `GROUP BY` hace lo mismo pero
    **por montones**: parte la tabla según los valores de una columna y aplica la
    agregación a cada montón por separado.

    ### Pieza 1 — un solo número para todo
    """)
    return


@app.cell
def _(comentarios, mo):
    grupo_1 = mo.sql(
        """
        SELECT count(*) AS evaluaciones
        FROM comentarios
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 2 — el mismo cálculo, ahora por grupo

    Agregamos la columna al `SELECT` **y** al `GROUP BY`. Ahora hay una fila por cada
    valor distinto de `annotator_ideology`.
    """)
    return


@app.cell
def _(comentarios, mo):
    grupo_2 = mo.sql(
        """
        SELECT
            annotator_ideology,
            count(*) AS evaluaciones
        FROM comentarios
        GROUP BY annotator_ideology
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 3 — agregamos promedios

    Puedes calcular varias cosas de cada grupo en la misma consulta.
    """)
    return


@app.cell
def _(comentarios, mo):
    grupo_3 = mo.sql(
        """
        SELECT
            annotator_ideology,
            count(*)               AS evaluaciones,
            round(avg(respect), 2) AS respeto_promedio,
            round(avg(insult), 2)  AS insulto_promedio
        FROM comentarios
        GROUP BY annotator_ideology
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pieza 4 — y lo ordenamos

    Sin `ORDER BY` los grupos salen en el orden que se le antoje a la base de datos.
    """)
    return


@app.cell
def _(comentarios, mo):
    grupo_4 = mo.sql(
        """
        SELECT
            annotator_ideology,
            count(*)               AS evaluaciones,
            round(avg(respect), 2) AS respeto_promedio,
            round(avg(insult), 2)  AS insulto_promedio
        FROM comentarios
        GROUP BY annotator_ideology
        ORDER BY evaluaciones DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### La regla de oro del `GROUP BY`

    > **Todo lo que aparece en el `SELECT` y no está dentro de una función de agregación
    > tiene que aparecer en el `GROUP BY`.**

    Tiene una lógica sencilla: si agrupaste por ideología y pides también `annotator_id`,
    la base de datos no sabe **cuál** de los 33,812 identificadores del grupo «liberal»
    darte. Por eso te lo impide.

    Ejecuta la celda de abajo para ver el error, y luego arréglala tú: quita
    `annotator_id` del `SELECT`, o agrégalo al `GROUP BY` y observa cómo cambia
    completamente el resultado.
    """)
    return


@app.cell
def _(comentarios, mo):
    esto_falla_a_proposito = mo.sql(
        """
        SELECT
            annotator_ideology,
            annotator_id,
            count(*) AS evaluaciones
        FROM comentarios
        GROUP BY annotator_ideology
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. El renglón vacío: los `NULL`

    En el resultado de la pieza 4 hay un grupo cuya ideología aparece en blanco. Ese es
    un **`NULL`**: un dato que falta.

    `GROUP BY` **les hace su propio grupo** en lugar de tirarlos, y hace bien. Esconder
    los datos faltantes es una de las formas más comunes de mentir con estadística sin
    darse cuenta: si esas 27 evaluaciones desaparecieran de tu tabla sin avisar, nunca
    te preguntarías quiénes son ni por qué no contestaron.
    """)
    return


@app.cell
def _(comentarios, mo):
    los_nulos = mo.sql(
        """
        SELECT
            count(*) AS evaluaciones_sin_ideologia
        FROM comentarios
        WHERE annotator_ideology IS NULL
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Fíjate en `IS NULL`. **No** se escribe `= NULL`: en SQL, un valor faltante no es
    igual a nada, ni siquiera a otro valor faltante. `WHERE annotator_ideology = NULL`
    no da error, simplemente **no devuelve nunca ninguna fila** — que es peor, porque
    parece que la respuesta es cero.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. `HAVING`: filtrar los grupos

    Ya sabes filtrar filas con `WHERE`. `HAVING` filtra **grupos**, después de formarlos.

    ```
    WHERE     →  descarta FILAS      →  antes de agrupar
    GROUP BY  →  arma los montones
    HAVING    →  descarta GRUPOS     →  después de agrupar
    ```

    Por eso `HAVING` puede usar `count(*)` y `WHERE` no: cuando `WHERE` corre, los grupos
    todavía no existen. Es el mismo orden de ejecución de la lección pasada.

    Busquemos los comentarios **más evaluados** del corpus:
    """)
    return


@app.cell
def _(comentarios, mo):
    muy_evaluados = mo.sql(
        """
        SELECT
            comment_id,
            count(*)                          AS evaluaciones,
            round(avg(respect), 2)            AS respeto_promedio,
            count(DISTINCT target_race)       AS opiniones_sobre_raza
        FROM comentarios
        GROUP BY comment_id
        HAVING count(*) > 100
        ORDER BY evaluaciones DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Son **70 comentarios**: el conjunto de calibración que descubrimos en la lección
    pasada. Fíjate en la última columna: en varios, `opiniones_sobre_raza` vale **2**.
    Eso significa que ese comentario recibió las dos respuestas posibles — hubo personas
    que dijeron que sí y personas que dijeron que no.

    ### `HAVING` con dos condiciones

    Se combinan con `AND` igual que en `WHERE`.
    """)
    return


@app.cell
def _(comentarios, mo):
    having_doble = mo.sql(
        """
        SELECT
            comment_id,
            count(*)               AS evaluaciones,
            round(avg(respect), 2) AS respeto_promedio
        FROM comentarios
        GROUP BY comment_id
        HAVING count(*) > 100
           AND avg(respect) < 2
        ORDER BY respeto_promedio ASC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    De los 70 comentarios muy evaluados, **16** además tienen un respeto promedio bajo.
    Esos son los que mucha gente vio y casi nadie consideró respetuosos.

    ### `WHERE` y `HAVING` juntos

    No son excluyentes: lo normal es usar los dos. `WHERE` recorta las filas *antes*, y
    `HAVING` los grupos *después*. Aquí solo miramos las evaluaciones que marcaron
    `target_race`, y de ahí sacamos los comentarios con al menos 50 de esas marcas.
    """)
    return


@app.cell
def _(comentarios, mo):
    where_y_having = mo.sql(
        """
        SELECT
            comment_id,
            count(*)              AS veces_marcado_por_raza,
            round(avg(insult), 2) AS insulto_promedio
        FROM comentarios
        WHERE target_race = true
        GROUP BY comment_id
        HAVING count(*) >= 50
        ORDER BY veces_marcado_por_raza DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### ⚠️ Si un `HAVING` te devuelve una tabla vacía, no siempre es tu culpa

        Cambia `comment_id` por `annotator_id` en cualquiera de las consultas de arriba y
        pide `HAVING count(*) > 50`. Vas a obtener **cero filas** — y tu SQL está perfecto.

        La razón está en los datos: en este corpus a cada anotador se le pidió evaluar unas
        decenas de comentarios, no cientos. **Ningún anotador supera las 26 evaluaciones.**

        Ante un resultado vacío, la pregunta correcta no es «¿qué escribí mal?» sino
        **«¿es posible este resultado con estos datos?»**. Se comprueba quitando el filtro
        y mirando la distribución real, que es justo lo que hace la consulta de abajo.
        """),
        kind="warn",
    )
    return


@app.cell
def _(comentarios, mo):
    cuanto_evalua_cada_quien = mo.sql(
        """
        SELECT
            max(evaluaciones)           AS maximo,
            round(avg(evaluaciones), 1) AS promedio,
            min(evaluaciones)           AS minimo
        FROM (
            SELECT annotator_id, count(*) AS evaluaciones
            FROM comentarios
            GROUP BY annotator_id
        )
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 7. Agrupar es fácil. Interpretar, no.

    Esta sección no tiene sintaxis nueva y es la más importante de la lección.

    Volvamos al promedio de respeto por ideología del anotador, ahora ordenado de mayor
    a menor. A primera vista parece un hallazgo: *«los conservadores extremos califican
    con más respeto»*.
    """)
    return


@app.cell
def _(comentarios, mo):
    la_trampa = mo.sql(
        """
        SELECT
            annotator_ideology,
            count(*)               AS evaluaciones,
            round(avg(respect), 2) AS respeto_promedio
        FROM comentarios
        GROUP BY annotator_ideology
        ORDER BY respeto_promedio DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### Mira los números otra vez antes de creerte nada

        **Toda la columna cabe entre 2.81 y 2.90.** En una escala de 0 a 4, esa diferencia
        es de siete centésimas: para efectos prácticos, **todos los grupos evaluaron
        igual**. Ordenar de mayor a menor crea una jerarquía visual que los datos no
        sostienen.

        **Y los grupos no son comparables en tamaño.** «liberal» tiene 33,812 evaluaciones;
        «extremely_conservative», 4,544. El promedio del grupo chico se mueve mucho más
        fácil, así que su lugar en la lista es mucho menos confiable.

        **Por eso `count(*)` va siempre junto al promedio.** Un promedio sin su conteo es
        una cifra a medias: no te deja saber cuánta confianza merece.

        La pregunta que hay que hacerse frente a cualquier `GROUP BY`: *¿esta diferencia
        es lo bastante grande como para significar algo, y hay suficientes datos en cada
        grupo como para creérsela?* La respuesta muy seguido es no, y decirlo también es
        un resultado.
        """),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 8. Ejercicios

    En cada uno, **borra la consulta de ejemplo y escribe la tuya**. La solución está
    escondida debajo: inténtalo antes de abrirla.

    ### Ejercicio 1 — El resumen de una columna

    Muestra en un solo renglón el **mínimo, el máximo y el promedio** de la columna
    `insult`, redondeando el promedio a dos decimales.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_1 = mo.sql(
        """
        -- Escribe aquí tu consulta y ejecútala con Ctrl+Enter
        SELECT count(*) AS total
        FROM comentarios
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 1": mo.md("""
            ```sql
            SELECT
                min(insult)             AS minimo,
                max(insult)             AS maximo,
                round(avg(insult), 2)   AS promedio
            FROM comentarios
            ```

            Da 0, 4 y 2.56. Tres agregaciones en la misma consulta, todas sobre la misma
            columna.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 2 — Contar por grupo

    ¿Cuántas evaluaciones hay por cada valor de `annotator_gender`? Ordena de mayor a
    menor cantidad.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_2 = mo.sql(
        """
        -- Escribe aquí tu consulta
        SELECT annotator_gender
        FROM comentarios
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 2": mo.md("""
            ```sql
            SELECT
                annotator_gender,
                count(*) AS evaluaciones
            FROM comentarios
            GROUP BY annotator_gender
            ORDER BY evaluaciones DESC
            ```

            Salen cinco grupos, encabezados por `female` con 76,370 evaluaciones y `male`
            con 57,582. Si además calculas `avg(insult)` verás que los promedios van de
            2.55 a 2.66: otra vez, diferencias demasiado chicas para concluir algo.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 3 — Contar sin repetir, por grupo

    ¿Cuántos **comentarios distintos** hay en cada plataforma (`platform`)?

    Cuidado con la trampa de la sección 3: si cuentas filas, cuentas evaluaciones.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_3 = mo.sql(
        """
        -- Escribe aquí tu consulta
        SELECT platform, count(*) AS mi_intento
        FROM comentarios
        GROUP BY platform
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 3": mo.md("""
            ```sql
            SELECT
                platform,
                count(DISTINCT comment_id) AS comentarios
            FROM comentarios
            GROUP BY platform
            ORDER BY comentarios DESC
            ```

            Con `count(*)` la plataforma 1 parece tener 43,227 registros —la más grande de
            todas—. Con `count(DISTINCT comment_id)` resulta que tiene **70 comentarios**:
            es el conjunto de calibración, donde poquísimos textos fueron evaluados por
            cientos de personas.

            Es el ejemplo más claro del curso de cómo la misma consulta, cambiando una
            palabra, cuenta la historia contraria.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 4 — Tu primer `HAVING`

    Encuentra los comentarios que recibieron **más de 300 evaluaciones**. Muestra el
    `comment_id`, cuántas evaluaciones tuvo y su `insult` promedio redondeado, del más
    evaluado al menos evaluado.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_4 = mo.sql(
        """
        -- Escribe aquí tu consulta
        SELECT comment_id, count(*) AS evaluaciones
        FROM comentarios
        GROUP BY comment_id
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 4": mo.md("""
            ```sql
            SELECT
                comment_id,
                count(*)              AS evaluaciones,
                round(avg(insult), 2) AS insulto_promedio
            FROM comentarios
            GROUP BY comment_id
            HAVING count(*) > 300
            ORDER BY evaluaciones DESC
            ```

            Salen 69 comentarios. Nota que la condición del `HAVING` usa `count(*)`
            aunque esa columna se llame `evaluaciones` en el `SELECT`: DuckDB te deja usar
            el alias, pero otras bases de datos no, así que la forma segura es repetir la
            función.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 5 — Investiga por tu cuenta

    Este no tiene una sola respuesta. Elige **cualquier columna de anotador**
    (`annotator_educ`, `annotator_income`, `annotator_age`…), agrupa por ella y calcula
    el promedio de alguna etiqueta (`respect`, `insult`, `violence`, `dehumanize`).

    Después haz el trabajo difícil: mira el conteo de cada grupo y pregúntate si la
    diferencia entre los promedios es lo bastante grande como para significar algo.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_5 = mo.sql(
        """
        -- Cambia la columna de agrupación y la etiqueta que promedias
        SELECT
            annotator_educ,
            count(*)               AS evaluaciones,
            round(avg(respect), 2) AS respeto_promedio
        FROM comentarios
        GROUP BY annotator_educ
        ORDER BY evaluaciones DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Pista para el ejercicio 5": mo.md("""
            Para ver qué columnas de anotador tienes disponibles:

            ```sql
            SELECT column_name
            FROM (DESCRIBE comentarios)
            WHERE column_name ILIKE '%annotator%'
            ```

            Lo que vas a encontrar casi siempre: los promedios se parecen muchísimo entre
            grupos. **Ese es el hallazgo.** El corpus fue diseñado justo para medir cuánto
            varía el juicio entre personas, y resulta que la variación individual es mucho
            más grande que la variación entre categorías demográficas.
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

        - Cinco agregaciones: `count`, `avg`, `min`, `max`, `sum`.
        - Las **tres formas de contar**, y que `count(columna)` ignora los nulos en silencio.
        - `GROUP BY` y su regla de oro: lo que no está agregado, va en el `GROUP BY`.
        - `HAVING` filtra **grupos**; `WHERE` filtra **filas**. Se usan juntos.
        - `IS NULL`, porque `= NULL` nunca devuelve nada.
        - Y lo que no es sintaxis: **un promedio sin su conteo es una cifra a medias**, y
          una diferencia de siete centésimas no es un hallazgo.

        En la siguiente lección: cruzar tablas con `JOIN`, y por qué unir dos tablas puede
        multiplicar tus filas sin que nadie te avise.
        """),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
