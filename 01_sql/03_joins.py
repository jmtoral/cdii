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
    # JOINs: cruzar tablas 🦆

    **Lección 3** de Ciencia de Datos para la Toma de Decisiones II.

    Ya sabes **elegir** filas (lección 1) y **resumir** grupos (lección 2). Hoy aprendes a
    **combinar tablas**: traer información que vive en otro lado y pegarla a la que ya tienes.

    Es la operación más poderosa de SQL y también **la más fácil de arruinar en silencio**.
    Vas a ver dos casos donde un `JOIN` cambia un promedio sin dar ningún error.
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

        **Puedes cambiar cualquier consulta.** Cambia las llaves, el tipo de `JOIN`, las
        columnas, y vuelve a ejecutar. Si dejas una celda hecha un desastre, recarga la
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
        Berkeley: comentarios reales de redes sociales, **sin censurar**. Todo lo de hoy se
        resuelve con columnas numéricas y llaves, así que puedes trabajar sin abrir la
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
    # Mismo Apps Script que recibe las entregas y la asistencia de las lecciones 1 y 2.
    # Se distingue por la columna `ejercicio`, que aquí dice "asistencia_03_joins".
    # Instrucciones: scripts/apps_script/README.md
    # ─────────────────────────────────────────────────────────────────────────
    ENDPOINT = (
        "https://script.google.com/macros/s/"
        "AKfycbxAh7nw7L0Kt5Qnak5Dyj9nkPX4PhX1c6WykpFGL6JOyvTL0dDv2-H0qHlEvfxQZCWj4g/exec"
    )
    CURSO = "CDII"
    SESION = "asistencia_03_joins"
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
                    f"Quedaste en la lista, **{nombre_alumno.value}**. Vamos a cruzar tablas. 👇"
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


# ─────────────────────────── 1. LAS CUATRO TABLAS ───────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Primero, separemos la tabla

    Hasta hoy trabajamos con **una sola tabla enorme** de 135,556 filas y 143 columnas,
    donde todo estaba mezclado: el texto del comentario, quién lo evaluó, y qué opinó.

    Para poder practicar `JOIN` vamos a partirla en las **cuatro cosas distintas** que
    tiene revueltas. Fíjate en el `DISTINCT`: es lo que colapsa las filas repetidas.
    """)
    return


@app.cell
def _(DATA_URL, mo):
    plano = mo.sql(
        f"""
        CREATE OR REPLACE TABLE plano AS
        SELECT * FROM read_parquet('{DATA_URL}')
        """
    )
    return (plano,)


@app.cell
def _(mo, plano):
    comentarios = mo.sql(
        """
        -- Un renglón por COMENTARIO. Sus datos se repetían en cada evaluación.
        CREATE OR REPLACE TABLE comentarios AS
        SELECT DISTINCT
            comment_id,
            text,
            platform AS platform_id,
            hate_speech_score
        FROM plano
        """
    )
    return (comentarios,)


@app.cell
def _(mo, plano):
    anotaciones = mo.sql(
        """
        -- Un renglón por EVALUACIÓN: la opinión de una persona sobre un comentario.
        CREATE OR REPLACE TABLE anotaciones AS
        SELECT
            comment_id,
            annotator_id,
            respect,
            insult,
            target_race
        FROM plano
        """
    )
    return (anotaciones,)


@app.cell
def _(mo, plano):
    anotadores = mo.sql(
        """
        -- Un renglón por PERSONA que evaluó.
        CREATE OR REPLACE TABLE anotadores AS
        SELECT DISTINCT
            annotator_id,
            annotator_gender,
            annotator_ideology,
            annotator_educ
        FROM plano
        """
    )
    return (anotadores,)


@app.cell
def _(mo):
    plataformas = mo.sql(
        """
        -- Catálogo. El dataset trae 4 códigos numéricos y NO publica el diccionario
        -- que dice cuál es cuál, así que no los inventamos.
        CREATE OR REPLACE TABLE plataformas AS
        SELECT * FROM (VALUES
            (0, 'Sin documentar (código 0)'),
            (1, 'Sin documentar (código 1)'),
            (2, 'Sin documentar (código 2)'),
            (3, 'Sin documentar (código 3)')
        ) AS t(platform_id, nombre)
        """
    )
    return (plataformas,)


@app.cell
def _(anotaciones, anotadores, comentarios, mo, plataformas):
    tamanos = mo.sql(
        """
        SELECT 'comentarios' AS tabla, count(*) AS filas FROM comentarios
        UNION ALL SELECT 'anotaciones', count(*) FROM anotaciones
        UNION ALL SELECT 'anotadores',  count(*) FROM anotadores
        UNION ALL SELECT 'plataformas', count(*) FROM plataformas
        ORDER BY filas DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cuatro tablas, cuatro tamaños muy distintos:

    | Tabla | Filas | Qué es una fila | Llave |
    |---|---|---|---|
    | `anotaciones` | 135,556 | Una evaluación | `(comment_id, annotator_id)` |
    | `comentarios` | 39,565 | Un comentario | `comment_id` |
    | `anotadores` | 7,912 | Una persona | `annotator_id` |
    | `plataformas` | 4 | Una plataforma | `platform_id` |

    Las columnas que se repiten entre tablas son las **llaves**, y son por donde vamos a
    pegarlas. `comment_id` aparece en `comentarios` y en `anotaciones`; `annotator_id`
    aparece en `anotadores` y en `anotaciones`.
    """)
    return


# ─────────────────────────── 2. EL JOIN MÁS SIMPLE ───────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. Tu primer `JOIN`: traer una etiqueta

    El caso más común y más inofensivo: tienes un código y quieres su nombre legible.

    `comentarios` guarda `platform_id` (un número). `plataformas` guarda qué significa ese
    número. Un `JOIN` los pega.

    Fíjate en tres cosas nuevas:

    | Pedazo | Qué hace |
    |---|---|
    | `JOIN plataformas` | Con qué otra tabla la vas a cruzar |
    | `ON c.platform_id = p.platform_id` | **Por cuál columna** se emparejan las filas |
    | `comentarios AS c` | Un **alias**: un apodo corto para no repetir el nombre largo |

    Los alias no son opcionales cuando dos tablas tienen columnas con el mismo nombre: sin
    ellos, `platform_id` sería ambiguo y la base de datos no sabría a cuál te refieres.
    """)
    return


@app.cell
def _(comentarios, mo, plataformas):
    join_catalogo = mo.sql(
        """
        SELECT
            c.comment_id,
            c.platform_id,
            p.nombre AS plataforma,
            c.hate_speech_score
        FROM comentarios AS c
        JOIN plataformas AS p
          ON c.platform_id = p.platform_id
        LIMIT 8
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Cada comentario trajo consigo el nombre de su plataforma. La columna `nombre` no estaba
    en `comentarios`: vino de la otra tabla.

    Y como ya sabes agrupar, puedes combinar ambas cosas en una consulta:
    """)
    return


@app.cell
def _(comentarios, mo, plataformas):
    join_con_group_by = mo.sql(
        """
        SELECT
            p.nombre                           AS plataforma,
            count(*)                           AS comentarios,
            round(avg(c.hate_speech_score), 3) AS score_promedio
        FROM comentarios AS c
        JOIN plataformas AS p
          ON c.platform_id = p.platform_id
        GROUP BY p.nombre
        ORDER BY comentarios DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### 🧭 Una consulta correcta que no permite concluir nada

        Esa consulta corre, los números son exactos… **y no significan nada**.

        El dataset **nunca publicó** el diccionario que dice qué plataforma es cada código.
        Podemos afirmar que el grupo 0 tiene más comentarios que el 3, pero no podemos decir
        *«en Twitter hay más odio que en Reddit»*, porque no sabemos cuál es cuál.

        Es tentador buscar en internet, encontrar que el paper menciona tres plataformas y
        asignarlas a ojo. **No lo hagas**: hay cuatro códigos y tres nombres, así que
        cualquier asignación sería inventada, y a partir de ahí todo tu análisis sería falso
        sin que nadie lo note.

        **Una columna sin diccionario te deja contar, pero no concluir.**
        """),
        kind="info",
    )
    return


# ─────────────────────────── 3. EL FAN-OUT ───────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. El *fan-out*: cuando el `JOIN` multiplica tus filas

    El ejemplo anterior era inofensivo porque `plataformas` tiene la llave **única**: cada
    `platform_id` aparece una sola vez, así que cada comentario encontró exactamente una
    pareja.

    Ahora crucemos `comentarios` con `anotaciones`, donde `comment_id` **se repite**. Un
    comentario evaluado por 800 personas va a encontrar 800 parejas.

    Contemos qué pasa:
    """)
    return


@app.cell
def _(anotaciones, comentarios, mo):
    el_fanout = mo.sql(
        """
        SELECT
            (SELECT count(*) FROM comentarios)                       AS filas_antes,
            (SELECT count(*) FROM comentarios c
                JOIN anotaciones a ON c.comment_id = a.comment_id)   AS filas_despues,
            (SELECT count(DISTINCT c.comment_id) FROM comentarios c
                JOIN anotaciones a ON c.comment_id = a.comment_id)   AS comentarios_distintos
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pasamos de **39,565 filas a 135,556**, pero siguen siendo los mismos **39,565
    comentarios**. El `JOIN` no inventó comentarios: **repitió cada uno tantas veces como
    evaluaciones tiene**.

    A eso se le llama ***fan-out***, y es completamente legítimo: es lo que pediste. El
    problema es lo que pasa si después calculas un promedio sin darte cuenta.

    ### La trampa, con números

    Las dos consultas de abajo pretenden responder **la misma pregunta**: ¿cuál es el
    `hate_speech_score` promedio de los comentarios del corpus?

    Una está bien y la otra está mal. **Ninguna da error.**
    """)
    return


@app.cell
def _(comentarios, mo):
    promedio_correcto = mo.sql(
        """
        -- ✅ Sobre la tabla de comentarios, donde cada uno aparece UNA vez
        SELECT round(avg(hate_speech_score), 4) AS score_promedio
        FROM comentarios
        """
    )
    return


@app.cell
def _(anotaciones, comentarios, mo):
    promedio_arruinado = mo.sql(
        """
        -- ❌ Sobre el resultado del JOIN, donde los comentarios muy evaluados
        --    aparecen cientos de veces y pesan cientos de veces más
        SELECT round(avg(c.hate_speech_score), 4) AS score_promedio
        FROM comentarios AS c
        JOIN anotaciones AS a
          ON c.comment_id = a.comment_id
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### ⚠️ −0.9439 contra −0.5674

        El promedio **se movió un 40%** y no hubo ni una advertencia.

        La causa: los 70 comentarios del conjunto de calibración tienen entre 243 y 815
        evaluaciones cada uno. Después del `JOIN`, **esos 70 comentarios ocupan más de
        25,000 filas** y arrastran el promedio hacia su valor, mientras que un comentario
        normal —evaluado por 2 o 3 personas— apenas cuenta.

        Ya no estás promediando comentarios: estás promediando **comentarios ponderados por
        cuánta gente los evaluó**, que es una pregunta distinta que nadie te hizo.

        > **Regla práctica:** si vas a promediar un atributo del lado que *no* se repite,
        > **agrega antes de unir**, no después.
        """),
        kind="danger",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Cómo se hace bien: agregar antes de unir

    Un `WITH` —lo que en la lección 2 usamos para encadenar pasos— resuelve esto: primero
    resumes `anotaciones` a **una fila por comentario**, y solo entonces la unes. Así la
    llave del lado derecho vuelve a ser única y no hay fan-out.
    """)
    return


@app.cell
def _(anotaciones, comentarios, mo):
    agregar_antes_de_unir = mo.sql(
        """
        WITH por_comentario AS (
            -- Paso 1: colapsamos las evaluaciones a una fila por comentario
            SELECT
                comment_id,
                count(*)              AS evaluaciones,
                round(avg(insult), 2) AS insulto_promedio
            FROM anotaciones
            GROUP BY comment_id
        )
        -- Paso 2: ahora sí unimos, y cada comentario encuentra UNA sola pareja
        SELECT
            count(*)                           AS filas,
            round(avg(c.hate_speech_score), 4) AS score_promedio,
            round(avg(p.insulto_promedio), 3)  AS insulto_promedio
        FROM comentarios AS c
        JOIN por_comentario AS p
          ON c.comment_id = p.comment_id
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **39,565 filas y el promedio vuelve a −0.9439**, el correcto. Y de paso trajimos el
    insulto promedio de cada comentario, que era el dato que queríamos de la otra tabla.

    Ese patrón —*agregar, luego unir*— es probablemente lo más útil de toda esta lección.
    """)
    return


# ─────────────────────────── 4. INNER VS LEFT ───────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. `INNER` contra `LEFT`: qué pasa con los que no emparejan

    Hasta ahora todas nuestras filas encontraron pareja. ¿Y cuando no?

    - Un **`JOIN`** normal (su nombre completo es `INNER JOIN`) **descarta** las filas que
      no encuentran pareja.
    - Un **`LEFT JOIN`** conserva **todas** las de la izquierda y rellena con `NULL` las
      columnas de la derecha cuando no hubo con quién emparejar.

    Para verlo necesitamos una tabla donde falten filas. Construyamos una: los comentarios
    que **algún** anotador marcó como `target_race`.
    """)
    return


@app.cell
def _(anotaciones, mo):
    marcados_raza = mo.sql(
        """
        CREATE OR REPLACE TABLE marcados_raza AS
        SELECT
            comment_id,
            count(*) AS veces_marcado
        FROM anotaciones
        WHERE target_race = true
        GROUP BY comment_id
        """
    )
    return (marcados_raza,)


@app.cell
def _(comentarios, marcados_raza, mo):
    inner_vs_left = mo.sql(
        """
        SELECT
            (SELECT count(*) FROM comentarios)                   AS todos_los_comentarios,
            (SELECT count(*) FROM marcados_raza)                 AS alguien_los_marco,
            (SELECT count(*) FROM comentarios c
                JOIN marcados_raza m ON c.comment_id = m.comment_id)      AS con_inner_join,
            (SELECT count(*) FROM comentarios c
                LEFT JOIN marcados_raza m ON c.comment_id = m.comment_id) AS con_left_join
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - `INNER` devuelve **14,697**: solo los comentarios que alguien marcó.
    - `LEFT` devuelve **39,565**: conserva también los **24,868 que nadie marcó**, con
      `NULL` en la columna de la derecha.

    Míralos. Ordenamos ascendente con `NULLS FIRST` para que los vacíos salgan arriba:
    """)
    return


@app.cell
def _(comentarios, marcados_raza, mo):
    los_nulos_del_left = mo.sql(
        """
        SELECT
            c.comment_id,
            c.hate_speech_score,
            m.veces_marcado
        FROM comentarios AS c
        LEFT JOIN marcados_raza AS m
          ON c.comment_id = m.comment_id
        ORDER BY m.veces_marcado ASC NULLS FIRST
        LIMIT 8
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Y aquí está por qué importa elegir bien

    Pregunta: **¿cuántas veces en promedio se marca un comentario como `target_race`?**

    Las dos consultas de abajo la responden. Otra vez, una está bien y la otra mal, y
    ninguna da error.
    """)
    return


@app.cell
def _(comentarios, marcados_raza, mo):
    promedio_con_inner = mo.sql(
        """
        -- ❌ INNER: solo mira los comentarios que SÍ fueron marcados
        SELECT round(avg(m.veces_marcado), 2) AS promedio
        FROM comentarios AS c
        JOIN marcados_raza AS m
          ON c.comment_id = m.comment_id
        """
    )
    return


@app.cell
def _(comentarios, marcados_raza, mo):
    promedio_con_left = mo.sql(
        """
        -- ✅ LEFT + COALESCE: los que nadie marcó cuentan como 0
        SELECT round(avg(COALESCE(m.veces_marcado, 0)), 2) AS promedio
        FROM comentarios AS c
        LEFT JOIN marcados_raza AS m
          ON c.comment_id = m.comment_id
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### ⚠️ 3.29 contra 1.22

        Casi **tres veces** de diferencia, y la culpa no es de la aritmética.

        Con `INNER`, los 24,868 comentarios que nadie marcó **desaparecieron de la
        consulta**. Estás promediando solo entre los que ya sabías que habían sido marcados,
        así que por construcción el número sale alto. Los ceros no se promediaron porque los
        ceros ni siquiera llegaron a la mesa.

        **`COALESCE(x, 0)`** devuelve el primer valor que no sea nulo: si `veces_marcado` es
        `NULL`, entrega `0`. Es lo que convierte «no hubo pareja» en «pasó cero veces», que
        es lo que realmente significa aquí.

        > **La pregunta que hay que hacerse:** cuando algo no aparece en la tabla de la
        > derecha, ¿eso significa **cero** o significa **no sé**? Si significa cero, usa
        > `LEFT JOIN` con `COALESCE`. Si significa que no sabes, el `NULL` es la respuesta
        > correcta y no debes rellenarlo.
        """),
        kind="danger",
    )
    return


# ─────────────────────────── 5. TRES TABLAS ───────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. Encadenar varios `JOIN`

    Nada te limita a dos tablas. Se encadenan uno tras otro, cada uno con su propio `ON`.

    Aquí respondemos algo que **ninguna tabla puede contestar sola**: ¿la ideología de quien
    evalúa se relaciona con qué tan insultante le parece un comentario? El juicio está en
    `anotaciones`; la ideología, en `anotadores`.
    """)
    return


@app.cell
def _(anotaciones, anotadores, mo):
    join_de_tres = mo.sql(
        """
        SELECT
            ad.annotator_ideology    AS ideologia,
            count(*)                 AS evaluaciones,
            round(avg(a.insult), 2)  AS insulto_promedio,
            round(avg(a.respect), 2) AS respeto_promedio
        FROM anotaciones AS a
        JOIN anotadores AS ad
          ON a.annotator_id = ad.annotator_id
        GROUP BY ad.annotator_ideology
        ORDER BY evaluaciones DESC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md("""
        ### El reflejo de la lección 2, otra vez

        Los promedios de insulto van de **2.55 a 2.63** en una escala de 0 a 4. Es decir:
        **prácticamente idénticos**.

        Aunque el `JOIN` esté perfecto y la pregunta sea interesante, la respuesta sigue
        siendo *«no se ve ninguna diferencia»*. Y está bien: **eso también es un
        resultado**, y es mucho más honesto que ordenar la tabla de mayor a menor y contar
        una historia con la tercera cifra decimal.
        """),
        kind="warn",
    )
    return


# ─────────────────────────── 6. EJERCICIOS ───────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. Ejercicios

    En cada uno, **borra la consulta de ejemplo y escribe la tuya**. La solución está
    escondida debajo: inténtalo antes de abrirla.

    ### Ejercicio 1 — Tu primer JOIN

    Cruza `anotaciones` con `anotadores` y muestra 10 filas con: `comment_id`,
    `annotator_id`, el `insult` que puso, y el `annotator_gender` de quien lo puso.
    """)
    return


@app.cell
def _(anotaciones, anotadores, mo):
    ejercicio_1 = mo.sql(
        """
        -- Escribe aquí tu consulta y ejecútala con Ctrl+Enter
        SELECT * FROM anotaciones LIMIT 5
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
                a.comment_id,
                a.annotator_id,
                a.insult,
                ad.annotator_gender
            FROM anotaciones AS a
            JOIN anotadores AS ad
              ON a.annotator_id = ad.annotator_id
            LIMIT 10
            ```

            El `ON` va siempre por la llave que comparten las dos tablas. Los alias
            (`a`, `ad`) no son obligatorios aquí, pero acostúmbrate: en cuanto haya dos
            columnas con el mismo nombre se vuelven indispensables.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 2 — Detecta el fan-out

    Escribe una consulta que muestre, en un solo renglón, **cuántas filas** salen al cruzar
    `anotaciones` con `anotadores`, y **cuántos anotadores distintos** hay en ese resultado.

    Antes de ejecutar, predice: ¿el número de filas va a ser 135,556, 7,912, o algo más?
    """)
    return


@app.cell
def _(anotaciones, anotadores, mo):
    ejercicio_2 = mo.sql(
        """
        -- Escribe aquí tu consulta
        SELECT count(*) AS mi_intento FROM anotaciones
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
                count(*)                       AS filas,
                count(DISTINCT a.annotator_id) AS anotadores_distintos
            FROM anotaciones AS a
            JOIN anotadores AS ad
              ON a.annotator_id = ad.annotator_id
            ```

            Salen **135,556 filas** y **7,912 anotadores**. Aquí el fan-out va en la
            dirección contraria al ejemplo de la sección 3: la tabla que se repite es la de
            la izquierda, así que el número de filas **no crece** — cada evaluación
            encuentra exactamente un anotador.

            **La regla general:** las filas se multiplican cuando la llave **se repite en el
            lado derecho**. Antes de cualquier `JOIN`, pregúntate si la llave es única allá.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 3 — Agregar antes de unir

    Muestra los **10 comentarios con mayor `hate_speech_score`** junto con **cuántas
    evaluaciones recibió cada uno**.

    Cuidado: el score está en `comentarios` y el conteo sale de `anotaciones`. Si unes
    directo, vas a repetir cada comentario. Usa un `WITH`.
    """)
    return


@app.cell
def _(anotaciones, comentarios, mo):
    ejercicio_3 = mo.sql(
        """
        -- Escribe aquí tu consulta
        SELECT comment_id, hate_speech_score
        FROM comentarios
        ORDER BY hate_speech_score DESC
        LIMIT 10
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔑 Ver solución del ejercicio 3": mo.md("""
            ```sql
            WITH por_comentario AS (
                SELECT comment_id, count(*) AS evaluaciones
                FROM anotaciones
                GROUP BY comment_id
            )
            SELECT
                c.comment_id,
                c.hate_speech_score,
                p.evaluaciones
            FROM comentarios AS c
            JOIN por_comentario AS p
              ON c.comment_id = p.comment_id
            ORDER BY c.hate_speech_score DESC
            LIMIT 10
            ```

            El `WITH` colapsa `anotaciones` a una fila por comentario **antes** de unir. Sin
            él tendrías 10 filas que en realidad serían menos de 10 comentarios repetidos.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 4 — Los que no aparecen

    Encuentra los comentarios que **nadie** marcó como `target_race`. Muestra `comment_id` y
    `hate_speech_score`, los 10 de mayor score.

    Pista: un `LEFT JOIN` conserva los que no emparejan, y después puedes filtrarlos.
    """)
    return


@app.cell
def _(comentarios, marcados_raza, mo):
    ejercicio_4 = mo.sql(
        """
        -- Escribe aquí tu consulta
        SELECT comment_id, hate_speech_score
        FROM comentarios
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
                c.comment_id,
                c.hate_speech_score
            FROM comentarios AS c
            LEFT JOIN marcados_raza AS m
              ON c.comment_id = m.comment_id
            WHERE m.comment_id IS NULL
            ORDER BY c.hate_speech_score DESC
            LIMIT 10
            ```

            A este patrón —`LEFT JOIN` seguido de `WHERE ... IS NULL`— se le llama
            **anti-join**, y es la forma estándar de preguntar «¿qué hay en A que no esté en
            B?». Son 24,868 comentarios en total.

            Fíjate en que algunos tienen scores altísimos: son comentarios hostiles que los
            anotadores consideraron dirigidos a **otra cosa** que no es la raza.
            """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 5 — Investiga por tu cuenta

    Este no tiene una sola respuesta. Cruza `anotaciones` con `anotadores` y agrupa por
    cualquier característica del anotador (`annotator_educ`, `annotator_gender`…),
    calculando el promedio de la etiqueta que te interese.

    Y después haz el trabajo difícil: mira el conteo de cada grupo y decide si la diferencia
    entre los promedios **alcanza para afirmar algo**.
    """)
    return


@app.cell
def _(anotaciones, anotadores, mo):
    ejercicio_5 = mo.sql(
        """
        -- Cambia la columna de agrupación y la etiqueta que promedias
        SELECT
            ad.annotator_educ        AS escolaridad,
            count(*)                 AS evaluaciones,
            round(avg(a.respect), 2) AS respeto_promedio
        FROM anotaciones AS a
        JOIN anotadores AS ad
          ON a.annotator_id = ad.annotator_id
        GROUP BY ad.annotator_educ
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
            FROM (DESCRIBE anotadores)
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

        - `JOIN ... ON` para pegar tablas por su **llave compartida**, y **alias** para
          escribirlo sin ambigüedad.
        - El ***fan-out***: si la llave se repite del lado derecho, **tus filas se
          multiplican**. No es un error, pero arruina cualquier promedio que calcules
          después.
        - El patrón que lo evita: **agrega antes de unir**, con un `WITH`.
        - `INNER` descarta lo que no empareja; **`LEFT` lo conserva con `NULL`**. Elegir mal
          borró 24,868 ceros y triplicó un promedio.
        - `COALESCE(x, 0)` para cuando «no hubo pareja» de verdad significa «cero» — y la
          disciplina de preguntarte si significa eso o significa «no sé».
        - `LEFT JOIN` + `WHERE ... IS NULL` para preguntar **qué falta**.

        Con esto cierras el tema de SQL: ya puedes abrir una base que nunca has visto,
        entender su estructura, filtrarla, resumirla y cruzarla. Lo que sigue del curso usa
        estas consultas como punto de partida.
        """),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
