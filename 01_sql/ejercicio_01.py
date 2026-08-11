import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _():
    # ─────────────────────────────────────────────────────────────────────────
    # CONFIGURACIÓN DEL PROFESOR
    # Pega aquí la URL del Apps Script publicado como aplicación web.
    # Instrucciones paso a paso en: scripts/apps_script/README.md
    # Si la dejas vacía, el botón de enviar se desactiva y el alumno solo
    # puede entregar descargando el archivo de respuestas.
    # ─────────────────────────────────────────────────────────────────────────
    ENDPOINT = ""

    CURSO = "CDII"
    EJERCICIO = "ejercicio_01_sql"
    return CURSO, EJERCICIO, ENDPOINT


@app.cell(hide_code=True)
def _(mo):
    # Ruta a los datos: en local es una carpeta del disco, en el navegador (WASM)
    # es una URL del propio sitio. DuckDB lee ambas.
    DATA_URL = str(mo.notebook_location() / "public" / "sample_data.parquet")
    return (DATA_URL,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Ejercicio 01 — Fundamentos de SQL

    Bienvenida/o al primer ejercicio evaluado de **Ciencia de Datos para la Toma de
    Decisiones II**. Vas a trabajar sobre el dataset *Measuring Hate Speech* del
    UC Berkeley D-Lab, ya cargado en una tabla llamada `comments`.

    **Cómo funciona:**

    1. Escribe tu consulta en el editor de cada pregunta.
    2. Haz clic **fuera del editor** (o presiona `Ctrl+Enter`) para ejecutarla.
      El resultado aparece justo debajo.
    3. Puedes probar cuantas veces quieras: nada se envía hasta que aprietes el
      botón de entrega al final.
    4. Al terminar, completa tus datos y entrega.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    alumno_nombre = mo.ui.text(
        label="**Nombre completo**", placeholder="Nombre y apellido", full_width=True
    )
    alumno_matricula = mo.ui.text(
        label="**Matrícula**", placeholder="A01234567", full_width=True
    )

    mo.callout(
        mo.vstack([alumno_nombre, alumno_matricula], gap=0.5),
        kind="info",
    )
    return alumno_matricula, alumno_nombre


@app.cell(hide_code=True)
def _(DATA_URL, mo):
    _carga = mo.sql(
        f"""
        CREATE OR REPLACE TABLE comments AS
        SELECT * FROM read_parquet('{DATA_URL}')
        """,
        output=False,
    )
    return


@app.cell(hide_code=True)
def _(comments, mo):
    _muestra = mo.sql("SELECT * FROM comments LIMIT 5", output=False)
    mo.vstack(
        [
            mo.md("### Los datos con los que vas a trabajar"),
            mo.md(f"La tabla `comments` tiene **{len(_muestra.columns)} columnas**. Una muestra:"),
            mo.ui.table(_muestra, selection=None, page_size=5),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    def ejecutar(consulta: str):
        """Corre el SQL del alumno y devuelve una tabla, o un error legible."""
        texto = (consulta or "").strip()

        # Ignoramos comentarios y líneas en blanco para detectar si escribió algo
        util = [
            linea
            for linea in texto.splitlines()
            if linea.strip() and not linea.strip().startswith("--")
        ]
        if not util:
            return mo.callout(
                mo.md("Escribe tu consulta en el editor de arriba."), kind="neutral"
            )

        try:
            resultado = mo.sql(texto, output=False)
        except Exception as e:  # noqa: BLE001 - queremos mostrar cualquier error de SQL
            return mo.callout(
                mo.md(f"""
                **Tu consulta tiene un error**

                ```
                {e}
                ```

                Revisa la sintaxis y vuelve a intentar. Nada de esto afecta tu calificación:
                puedes equivocarte todas las veces que quieras.
                """),
                kind="danger",
            )

        if len(resultado) == 0:
            return mo.callout(
                mo.md("La consulta corrió bien pero **no devolvió ninguna fila**."),
                kind="warn",
            )

        return mo.vstack(
            [
                mo.md(f"*{len(resultado)} filas devueltas*"),
                mo.ui.table(resultado, selection=None, page_size=10),
            ]
        )

    return (ejecutar,)


@app.cell(hide_code=True)
def _(mo):
    def pregunta(numero: str, puntos: int, enunciado: str, pista: str):
        return mo.md(f"""
        ---
        ### Pregunta {numero} · *{puntos} puntos*

        {enunciado}

        > 💡 **Pista:** {pista}
        """)

    return (pregunta,)


@app.cell(hide_code=True)
def _(mo):
    PLANTILLA = "-- Escribe tu consulta aquí\n"

    respuestas = mo.ui.dictionary(
        {
            "p1": mo.ui.code_editor(value=PLANTILLA, language="sql", debounce=True),
            "p2": mo.ui.code_editor(value=PLANTILLA, language="sql", debounce=True),
            "p3": mo.ui.code_editor(value=PLANTILLA, language="sql", debounce=True),
            "p4": mo.ui.code_editor(value=PLANTILLA, language="sql", debounce=True),
            "p5": mo.ui.code_editor(value=PLANTILLA, language="sql", debounce=True),
            "p6": mo.ui.code_editor(value=PLANTILLA, language="sql", debounce=True),
            "bonus": mo.ui.code_editor(value=PLANTILLA, language="sql", debounce=True),
        }
    )
    return (respuestas,)


@app.cell(hide_code=True)
def _(pregunta):
    pregunta(
        "1",
        10,
        "Selecciona las columnas `comment_id`, `text` y `hate_speech_score` de los "
        "**20 comentarios con mayor `hate_speech_score`**.",
        "`SELECT` con los nombres de columna, `FROM comments`, `ORDER BY ... DESC` y `LIMIT`.",
    )
    return


@app.cell(hide_code=True)
def _(respuestas):
    respuestas["p1"]
    return


@app.cell(hide_code=True)
def _(ejecutar, respuestas):
    ejecutar(respuestas["p1"].value)
    return


@app.cell(hide_code=True)
def _(pregunta):
    pregunta(
        "2",
        15,
        "Encuentra los comentarios donde `target_race` sea `TRUE` **y** el "
        "`hate_speech_score` sea mayor a `2.0`. Muestra `text` y `hate_speech_score`.",
        "`WHERE` combinando dos condiciones con `AND`.",
    )
    return


@app.cell(hide_code=True)
def _(respuestas):
    respuestas["p2"]
    return


@app.cell(hide_code=True)
def _(ejecutar, respuestas):
    ejecutar(respuestas["p2"].value)
    return


@app.cell(hide_code=True)
def _(pregunta):
    pregunta(
        "3",
        15,
        "Encuentra comentarios cuyo texto contenga la palabra *hate* (sin importar si "
        "hay texto antes o después). Muestra las primeras 15 filas.",
        "El operador `LIKE` con comodines `%`. ¿Y si la palabra está en mayúsculas? Prueba `ILIKE`.",
    )
    return


@app.cell(hide_code=True)
def _(respuestas):
    respuestas["p3"]
    return


@app.cell(hide_code=True)
def _(ejecutar, respuestas):
    ejecutar(respuestas["p3"].value)
    return


@app.cell(hide_code=True)
def _(pregunta):
    pregunta(
        "4",
        15,
        "¿Cuántos comentarios hay por cada plataforma (`platform`)? Ordena de mayor a menor.",
        "`GROUP BY platform` junto con `COUNT(*)`.",
    )
    return


@app.cell(hide_code=True)
def _(respuestas):
    respuestas["p4"]
    return


@app.cell(hide_code=True)
def _(ejecutar, respuestas):
    ejecutar(respuestas["p4"].value)
    return


@app.cell(hide_code=True)
def _(pregunta):
    pregunta(
        "5",
        20,
        "Encuentra los anotadores (`annotator_id`) que evaluaron **más de 50 comentarios**. "
        "Muestra el `annotator_id` y su conteo.",
        "Agrupa por `annotator_id` y filtra los grupos con `HAVING` (no con `WHERE`).",
    )
    return


@app.cell(hide_code=True)
def _(respuestas):
    respuestas["p5"]
    return


@app.cell(hide_code=True)
def _(ejecutar, respuestas):
    ejecutar(respuestas["p5"].value)
    return


@app.cell(hide_code=True)
def _(pregunta):
    pregunta(
        "6",
        25,
        "Calcula el promedio de `hate_speech_score` agrupado por `target_religion` "
        "(`TRUE` / `FALSE`). ¿Cuál grupo tiene el promedio más alto?",
        "`GROUP BY target_religion` con `AVG(hate_speech_score)`.",
    )
    return


@app.cell(hide_code=True)
def _(respuestas):
    respuestas["p6"]
    return


@app.cell(hide_code=True)
def _(ejecutar, respuestas):
    ejecutar(respuestas["p6"].value)
    return


@app.cell(hide_code=True)
def _(pregunta):
    pregunta(
        "BONUS",
        15,
        "Usando un **CTE** (`WITH`), encuentra los 5 comentarios con mayor "
        "`hate_speech_score` que además tengan `target_gender = TRUE`, y muestra su texto.",
        "Un CTE se define con `WITH nombre AS (SELECT ...)` y después consultas sobre él.",
    )
    return


@app.cell(hide_code=True)
def _(respuestas):
    respuestas["bonus"]
    return


@app.cell(hide_code=True)
def _(ejecutar, respuestas):
    ejecutar(respuestas["bonus"].value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Entrega
    """)
    return


@app.cell(hide_code=True)
def _(CURSO, EJERCICIO, alumno_matricula, alumno_nombre, respuestas):
    import datetime
    import json

    def _contestada(texto: str) -> bool:
        return bool(
            [
                linea
                for linea in (texto or "").splitlines()
                if linea.strip() and not linea.strip().startswith("--")
            ]
        )

    _valores = respuestas.value
    contestadas = [k for k, v in _valores.items() if _contestada(v)]

    entrega = {
        "curso": CURSO,
        "ejercicio": EJERCICIO,
        "nombre": (alumno_nombre.value or "").strip(),
        "matricula": (alumno_matricula.value or "").strip(),
        "enviado_en": datetime.datetime.now().isoformat(timespec="seconds"),
        "contestadas": len(contestadas),
        "respuestas": _valores,
    }

    entrega_json = json.dumps(entrega, ensure_ascii=False, indent=2)
    return contestadas, entrega, entrega_json


@app.cell(hide_code=True)
def _(alumno_matricula, alumno_nombre, contestadas, mo, respuestas):
    _faltan = []
    if not (alumno_nombre.value or "").strip():
        _faltan.append("tu **nombre**")
    if not (alumno_matricula.value or "").strip():
        _faltan.append("tu **matrícula**")

    _total = len(respuestas.value)
    _sin_contestar = _total - len(contestadas)

    listo_para_enviar = not _faltan

    if _faltan:
        _aviso = mo.callout(
            mo.md("Antes de entregar, completa " + " y ".join(_faltan) + " arriba."),
            kind="warn",
        )
    elif _sin_contestar:
        _aviso = mo.callout(
            mo.md(
                f"Llevas **{len(contestadas)} de {_total}** preguntas contestadas. "
                f"Puedes entregar así, pero te faltan {_sin_contestar}."
            ),
            kind="warn",
        )
    else:
        _aviso = mo.callout(
            mo.md(f"Contestaste las **{_total}** preguntas. ¡Listo para entregar!"),
            kind="success",
        )

    _aviso
    return (listo_para_enviar,)


@app.cell(hide_code=True)
def _(ENDPOINT, listo_para_enviar, mo):
    boton_enviar = mo.ui.button(
        value=0,
        on_click=lambda n: n + 1,
        label="📤 Enviar mis respuestas",
        kind="success",
        disabled=not (listo_para_enviar and ENDPOINT),
    )
    return (boton_enviar,)


@app.cell(hide_code=True)
def _(alumno_matricula, alumno_nombre, entrega_json, mo):
    _slug = (alumno_matricula.value or alumno_nombre.value or "alumno").strip()
    _slug = "".join(c if c.isalnum() else "_" for c in _slug) or "alumno"

    boton_descargar = mo.download(
        data=lambda: entrega_json.encode("utf-8"),
        filename=f"ejercicio_01_{_slug}.json",
        mimetype="application/json",
        label="💾 Descargar mis respuestas",
    )
    return (boton_descargar,)


@app.cell(hide_code=True)
def _(ENDPOINT, boton_descargar, boton_enviar, mo):
    _nota = (
        "Al enviar, tus respuestas llegan directo a la hoja de calificaciones."
        if ENDPOINT
        else "**El envío en línea no está configurado.** Descarga el archivo y súbelo donde te indique tu profesor."
    )

    mo.vstack(
        [
            mo.hstack([boton_enviar, boton_descargar], justify="start", gap=1),
            mo.md(f"<small>{_nota}</small>"),
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    # Marimo re-ejecuta una celda cada vez que cambia cualquiera de sus dependencias.
    # Como la celda de envío depende de las respuestas, sin este candado el alumno
    # reenviaría sin querer con solo editar una consulta después de haber entregado.
    # Guardamos el número de clics ya procesados para enviar exactamente una vez por clic.
    ESTADO_ENVIO = {"clics_procesados": 0, "resultado": None}
    return (ESTADO_ENVIO,)


@app.cell(hide_code=True)
def _():
    async def enviar_a_endpoint(url: str, cuerpo: str) -> tuple[bool, str]:
        """POST del JSON de respuestas. Funciona igual en el navegador y en local.

        Usa content-type text/plain a propósito: application/json dispara una
        petición CORS de preflight (OPTIONS) que Apps Script no sabe responder.
        """
        try:
            from pyodide.http import pyfetch  # solo existe dentro del navegador

            respuesta = await pyfetch(
                url,
                method="POST",
                headers={"Content-Type": "text/plain;charset=utf-8"},
                body=cuerpo,
            )
            texto = await respuesta.string()
            return respuesta.status < 400, texto[:300]
        except ImportError:
            import urllib.request

            peticion = urllib.request.Request(
                url,
                data=cuerpo.encode("utf-8"),
                headers={"Content-Type": "text/plain;charset=utf-8"},
                method="POST",
            )
            with urllib.request.urlopen(peticion, timeout=30) as r:
                return r.status < 400, r.read().decode("utf-8", "replace")[:300]
        except Exception as e:  # noqa: BLE001
            return False, f"{type(e).__name__}: {e}"

    return (enviar_a_endpoint,)


@app.cell(hide_code=True)
async def _(
    ENDPOINT,
    ESTADO_ENVIO,
    boton_enviar,
    entrega_json,
    enviar_a_endpoint,
    mo,
):
    _clics = boton_enviar.value or 0

    if _clics > ESTADO_ENVIO["clics_procesados"]:
        ESTADO_ENVIO["clics_procesados"] = _clics
        _ok, _detalle = await enviar_a_endpoint(ENDPOINT, entrega_json)
        ESTADO_ENVIO["resultado"] = (
            mo.callout(
                mo.md(
                    "### ✅ Entrega recibida\n\n"
                    "Tus respuestas quedaron registradas. Puedes cerrar la página.\n\n"
                    "Si corriges algo, vuelve a apretar el botón: se guarda como un intento nuevo."
                ),
                kind="success",
            )
            if _ok
            else mo.callout(
                mo.md(
                    f"### ❌ No se pudo enviar\n\n```\n{_detalle}\n```\n\n"
                    "**Usa el botón de descargar** y entrega el archivo por la vía "
                    "que te indique tu profesor."
                ),
                kind="danger",
            )
        )

    ESTADO_ENVIO["resultado"] or mo.md("")
    return


if __name__ == "__main__":
    app.run()
