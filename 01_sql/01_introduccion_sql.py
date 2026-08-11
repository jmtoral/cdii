import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    # `mo.notebook_location()` devuelve la carpeta del notebook cuando corremos en local,
    # y la URL base del sitio cuando el notebook corre en el navegador (WASM).
    # Por eso la misma línea sirve en los dos casos: en local es una ruta de disco y en
    # WASM queda un https://.../public/sample_data.parquet que DuckDB sabe leer.
    DATA_URL = str(mo.notebook_location() / "public" / "sample_data.parquet")
    return (DATA_URL,)


@app.cell(hide_code=True)
def _(mo):
    student_name = mo.ui.text(
        label="**Tu nombre:**",
        placeholder="Nombre Apellido",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("# Bienvenidos a SQL con DuckDB 🦆"),
            mo.callout(student_name, kind="info"),
        ]
    )
    return (student_name,)


@app.cell(hide_code=True)
def _(mo, student_name):
    mo.md(f"""
    ¡Hola **{student_name.value or 'Estudiante'}**! Bienvenidos a **Ciencia de Datos para la Toma de Decisiones II**.
    En esta clase, aprenderemos los conceptos básicos de SQL (Structured Query Language), el lenguaje estándar para interactuar con bases de datos.

    Usaremos **DuckDB**, que es un sistema de gestión de bases de datos analíticas de alto rendimiento. ¡Es tan rápido y fácil de usar que podemos ejecutarlo directamente aquí en nuestro entorno de Python sin necesidad de instalar un servidor!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Carga de Datos y Esquema

    Trabajaremos con el dataset "Measuring Hate Speech" de UC Berkeley D-Lab. Contiene comentarios de redes sociales y evaluaciones sobre si contienen discurso de odio, a quién van dirigidos, el nivel de respeto, etc.

    Primero, cargaremos nuestros datos desde un archivo Parquet. Parquet es un formato de almacenamiento en columnas, muy eficiente para análisis de datos.
    """)
    return


@app.cell
def _(DATA_URL, mo):
    _df = mo.sql(
        f"""
        -- Crear una tabla a partir del archivo parquet
        CREATE OR REPLACE TABLE comentarios AS
        SELECT * FROM read_parquet('{DATA_URL}')
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ¡Listo! Ahora la tabla `comentarios` está disponible para que la consultemos.
    Echemos un vistazo a los primeros registros para entender qué información tenemos:
    """)
    return


@app.cell
def _(comentarios, mo):
    comentarios_preview = mo.sql(
        f"""
        -- Mostrar los primeros registros de la tabla
        SELECT * FROM comentarios LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Lo Básico: SELECT

    La instrucción `SELECT` se utiliza para elegir las columnas (variables) que queremos ver de nuestra tabla.
    En lugar de usar `*` (que trae todo), es una buena práctica pedir solo lo que necesitamos.
    """)
    return


@app.cell
def _(comentarios, mo):
    select_basico = mo.sql(
        f"""
        -- Seleccionar solo las columnas de interés
        SELECT
            comment_id,
            text,
            hate_speech_score
        FROM comentarios
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Filtrando Filas: WHERE

    Usamos `WHERE` para filtrar los datos y obtener solo las filas que cumplen con una o más condiciones.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Filtros Numéricos
    Veamos los comentarios que tienen un `hate_speech_score` alto (mayor a 2).
    """)
    return


@app.cell
def _(comentarios, mo):
    filtro_numerico = mo.sql(
        f"""
        SELECT
            text,
            hate_speech_score
        FROM comentarios
        WHERE hate_speech_score > 2
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Filtros Booleanos (Verdadero/Falso)
    También podemos filtrar por condiciones lógicas. Veamos aquellos comentarios cuyo objetivo fue por motivos de raza (`target_race` = true).
    """)
    return


@app.cell
def _(comentarios, mo):
    filtro_booleano = mo.sql(
        f"""
        SELECT
            text,
            target_race,
            hate_speech_score
        FROM comentarios
        WHERE target_race = true
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Buscando Texto: LIKE

    A menudo necesitamos buscar patrones dentro del texto. El operador `LIKE` nos permite hacer esto usando el comodín `%` (que representa cualquier secuencia de caracteres).
    ¡Ojo! En muchos sistemas SQL (incluido DuckDB por defecto), `LIKE` distingue entre mayúsculas y minúsculas. `ILIKE` es la versión insensible a mayúsculas/minúsculas.
    """)
    return


@app.cell
def _(comentarios, mo):
    busqueda_texto = mo.sql(
        f"""
        -- Buscamos la palabra 'people' en el texto
        SELECT
            text,
            hate_speech_score
        FROM comentarios
        WHERE text ILIKE '%people%'
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Ordenando Resultados: ORDER BY y LIMIT

    `ORDER BY` nos permite ordenar los resultados en base a una o más columnas.
    Por defecto ordena de forma ascendente (`ASC`). Si queremos los valores más altos primero, usamos descendente (`DESC`).
    `LIMIT` restringe el número de filas que se muestran, ¡muy útil para ver el "Top N" de algo!
    """)
    return


@app.cell
def _(comentarios, mo):
    top_odio = mo.sql(
        f"""
        -- Top 5 comentarios con mayor score de discurso de odio
        SELECT
            text,
            hate_speech_score,
            respect
        FROM comentarios
        ORDER BY hate_speech_score DESC
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Exploración Interactiva

    ¡Marimo nos permite crear widgets interactivos que se comunican con nuestro código SQL!
    Juega con los controles a continuación para filtrar los datos dinámicamente.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    slider_score = mo.ui.slider(
        start=-5.0,
        stop=5.0,
        step=0.5,
        value=0.0,
        label="Umbral mínimo de odio (hate_speech_score)",
        show_value=True,
        full_width=True,
    )
    dropdown_objetivo = mo.ui.dropdown(
        options=["target_race", "target_religion", "target_gender", "target_origin"],
        value="target_race",
        label="Grupo objetivo",
    )

    mo.vstack([slider_score, dropdown_objetivo], gap=1)
    return dropdown_objetivo, slider_score


@app.cell(hide_code=True)
def _(dropdown_objetivo, mo, slider_score):
    mo.md(f"""
    Filtrando comentarios con un score mayor o igual a **{slider_score.value}**
    donde el objetivo es **`{dropdown_objetivo.value}`**.
    """)
    return


@app.cell
def _(comentarios, dropdown_objetivo, mo, slider_score):
    exploracion_interactiva = mo.sql(
        f"""
        -- Observa cómo usamos las variables de Python dentro de nuestra consulta SQL
        SELECT
            text,
            hate_speech_score,
            {dropdown_objetivo.value} as es_objetivo
        FROM
            comentarios
        WHERE
            hate_speech_score >= {slider_score.value}
            AND {dropdown_objetivo.value} = true
        ORDER BY
            hate_speech_score DESC
        LIMIT
            10
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Ejercicios Prácticos

    ¡Ahora te toca a ti! Resuelve los siguientes ejercicios modificando las consultas SQL (hemos dejado una consulta de muestra que puedes cambiar).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 1: Los más respetuosos
    Escribe una consulta para encontrar los **3 comentarios con mayor nivel de respeto** (`respect`).
    Muestra solo las columnas `text` y `respect`.

    *Pista: Necesitarás usar SELECT, ORDER BY (¿ascendente o descendente?) y LIMIT.*
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_1 = mo.sql(
        f"""
        -- Escribe tu código aquí:
        SELECT text, respect
        FROM comentarios
        ORDER BY respect DESC
        LIMIT 3
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 2: Buscando insultos específicos
    Encuentra 5 comentarios que contengan la palabra "stupid" y cuyo score de insulto (`insult`) sea mayor a 1.
    Muestra `text` e `insult`.

    *Pista: Usa WHERE con dos condiciones (usando AND) y no te olvides de ILIKE para la búsqueda de texto.*
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_2 = mo.sql(
        f"""
        -- Escribe tu código aquí:
        SELECT text, insult
        FROM comentarios
        WHERE text ILIKE '%stupid%' AND insult > 1
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ejercicio 3: Encuentra un comentario terrible
    Usa tus conocimientos de SQL para buscar un comentario que te parezca un claro ejemplo de discurso de odio.
    Puedes filtrar por score, usar búsquedas de texto (LIKE) o buscar objetivos específicos.
    """)
    return


@app.cell
def _(comentarios, mo):
    ejercicio_3 = mo.sql(
        f"""
        -- Escribe tu código aquí:
        SELECT text, hate_speech_score, target_race, target_gender
        FROM comentarios
        WHERE hate_speech_score > 3
        LIMIT 5
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    comentario_terrible = mo.ui.text_area(
        label="**Pega aquí el ID o el texto del comentario terrible que encontraste:**",
        placeholder="Escribe o pega aquí...",
        rows=4,
        full_width=True,
    )
    comentario_terrible
    return (comentario_terrible,)


@app.cell(hide_code=True)
def _(comentario_terrible, mo):
    mo.callout(
        mo.md(f"**Tu comentario elegido:**\n\n{comentario_terrible.value or '_(aún vacío)_'}"),
        kind="warn" if comentario_terrible.value else "neutral",
    )
    return


if __name__ == "__main__":
    app.run()
