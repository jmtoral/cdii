import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # 02. Agregaciones y JOINs con SQL 🦆

    ¡Hola! En este notebook de la clase de **Ciencia de Datos para la Toma de Decisiones II**, exploraremos cómo realizar operaciones avanzadas en SQL usando DuckDB.

    En la clase anterior vimos cómo filtrar y seleccionar datos. Hoy daremos un paso más allá para:
    * Resumir datos con **funciones de agregación** (COUNT, AVG, SUM, MIN, MAX)
    * Agrupar datos con **GROUP BY** y filtrar grupos con **HAVING**
    * Crear nuevas columnas condicionales con **CASE WHEN**
    * Realizar consultas anidadas usando **Subqueries** y **CTEs (WITH)**
    * Combinar diferentes tablas usando **JOINs**

    ## El Dataset: Measuring Hate Speech
    Estaremos trabajando con un extracto del dataset "Measuring Hate Speech" de UC Berkeley D-Lab. Los datos ya están listos para ser analizados.

    Vamos a cargar los datos en memoria creando una tabla a partir de nuestro archivo parquet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Ver nota en 01_introduccion_sql.py: esto resuelve a una ruta de disco en local
    # y a una URL del sitio cuando el notebook corre en el navegador (WASM).
    DATA_URL = str(mo.notebook_location() / "public" / "sample_data.parquet")
    return (DATA_URL,)


@app.cell
def _(DATA_URL, mo):
    _df_init = mo.sql(
        f"""
        CREATE OR REPLACE TABLE comentarios AS SELECT * FROM read_parquet('{DATA_URL}')
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Funciones de Agregación

    Las funciones de agregación toman múltiples filas y devuelven un único valor resumido. Las más comunes son:
    - `COUNT()`: Cuenta el número de filas
    - `AVG()`: Calcula el promedio
    - `SUM()`: Suma los valores
    - `MIN()`: Encuentra el valor mínimo
    - `MAX()`: Encuentra el valor máximo

    Veamos un resumen general de nuestros datos:
    """)
    return


@app.cell
def _(mo):
    _df_agg = mo.sql(
        f"""
        SELECT 
            COUNT(*) as total_comentarios,
            AVG(hate_speech_score) as promedio_odio,
            MAX(hate_speech_score) as score_maximo,
            MIN(hate_speech_score) as score_minimo
        FROM comentarios
        """
    )
    return (_df_agg,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. GROUP BY (Agrupando datos)

    A menudo, no queremos un resumen de toda la tabla, sino un resumen por categorías. La cláusula `GROUP BY` agrupa las filas que tienen los mismos valores en columnas específicas para que podamos calcular agregaciones por grupo.

    Veamos cuántos comentarios hay por plataforma y su puntaje promedio de odio:
    """)
    return


@app.cell
def _(mo):
    _df_groupby = mo.sql(
        f"""
        SELECT 
            platform,
            COUNT(*) as cantidad,
            AVG(hate_speech_score) as promedio_score
        FROM comentarios
        GROUP BY platform
        ORDER BY cantidad DESC
        """
    )
    return (_df_groupby,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. HAVING (Filtrando grupos)

    Mientras que `WHERE` filtra filas antes de agrupar, `HAVING` filtra los grupos *después* de aplicar el `GROUP BY`.

    Por ejemplo, encontremos aquellos anotadores (annotator_id) que han evaluado más de 50 comentarios y cuyo puntaje promedio dado es mayor a 0:
    """)
    return


@app.cell
def _(mo):
    _df_having = mo.sql(
        f"""
        SELECT 
            annotator_id,
            COUNT(*) as total_evaluaciones,
            AVG(hate_speech_score) as promedio_score
        FROM comentarios
        GROUP BY annotator_id
        HAVING COUNT(*) > 50 AND AVG(hate_speech_score) > 0
        ORDER BY promedio_score DESC
        """
    )
    return (_df_having,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. CASE WHEN (Lógica Condicional)

    `CASE WHEN` es el equivalente a if-else en SQL. Permite crear nuevas columnas basadas en condiciones.

    Vamos a categorizar la severidad de los comentarios basándonos en el `hate_speech_score`:
    """)
    return


@app.cell
def _(mo):
    _df_case = mo.sql(
        f"""
        SELECT 
            text,
            hate_speech_score,
            CASE 
                WHEN hate_speech_score > 2 THEN 'Severo'
                WHEN hate_speech_score > 0 THEN 'Moderado'
                ELSE 'Bajo/No Odio'
            END AS categoria_severidad
        FROM comentarios
        LIMIT 10
        """
    )
    return (_df_case,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Subqueries (Subconsultas)

    Una subconsulta es una consulta anidada dentro de otra consulta. Son útiles cuando necesitas realizar un cálculo en un paso previo para luego usarlo como filtro.

    Por ejemplo, ¿cuáles comentarios tienen un `hate_speech_score` mayor al promedio general de todos los comentarios?
    """)
    return


@app.cell
def _(mo):
    _df_sub = mo.sql(
        f"""
        SELECT 
            comment_id, 
            text, 
            hate_speech_score
        FROM comentarios
        WHERE hate_speech_score > (
            SELECT AVG(hate_speech_score) FROM comentarios
        )
        ORDER BY hate_speech_score DESC
        LIMIT 5
        """
    )
    return (_df_sub,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. CTEs (Common Table Expressions / Cláusula WITH)

    Las CTEs actúan como tablas temporales que solo existen durante la ejecución de la consulta. Hacen que el código SQL complejo sea mucho más legible organizándolo de forma secuencial.

    Vamos a hacer un análisis multi-paso: Primero encontramos los comentarios con odio hacia algún grupo particular (por raza), y luego resumimos por plataforma.
    """)
    return


@app.cell
def _(mo):
    _df_cte = mo.sql(
        f"""
        WITH comentarios_racismo AS (
            SELECT platform, hate_speech_score
            FROM comentarios
            WHERE target_race = TRUE
        ),
        resumen_plataforma AS (
            SELECT 
                platform,
                COUNT(*) as cantidad_racismo,
                AVG(hate_speech_score) as promedio_score
            FROM comentarios_racismo
            GROUP BY platform
        )
        SELECT * FROM resumen_plataforma ORDER BY cantidad_racismo DESC
        """
    )
    return (_df_cte,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. JOINs (Cruzando Datos)

    A menudo, los datos están distribuidos en múltiples tablas. Un `JOIN` permite combinar filas de dos o más tablas basándose en una columna relacionada entre ellas.

    Para este ejemplo, simulemos que tenemos dos tablas separadas creando dos "Vistas" (Views):
    """)
    return


@app.cell
def _(mo):
    _df_views = mo.sql(
        f"""
        CREATE OR REPLACE VIEW vista_comentarios AS 
        SELECT DISTINCT comment_id, text, hate_speech_score 
        FROM comentarios;
        
        CREATE OR REPLACE VIEW vista_anotadores AS 
        SELECT annotator_id, COUNT(*) as total_anotaciones, AVG(hate_speech_score) as promedio_score 
        FROM comentarios 
        GROUP BY annotator_id;
        """
    )
    return (_df_views,)


@app.cell
def _(mo):
    mo.md(r"""
    Ahora, supongamos que queremos ver información de un comentario, pero también agregar información sobre cómo el anotador evalúa usualmente. Para eso necesitamos cruzar (`JOIN`) la tabla principal con nuestra nueva tabla resumen de anotadores.

    *(Nota: en este dataset simplificado cruzaremos directamente con `comentarios` usando el `annotator_id` como llave, y haremos JOIN con la vista de anotadores)*
    """)
    return


@app.cell
def _(mo):
    _df_join = mo.sql(
        f"""
        SELECT 
            c.comment_id,
            c.text,
            c.hate_speech_score as score_comentario,
            a.promedio_score as promedio_historico_anotador
        FROM comentarios c
        JOIN vista_anotadores a ON c.annotator_id = a.annotator_id
        LIMIT 5
        """
    )
    return (_df_join,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 📝 Ejercicios de Práctica

    **Ejercicio 1: Analizando el respeto y el insulto**
    Encuentra el promedio de `respect` y el promedio de `insult` agrupado por si atacan a un género (`target_gender = TRUE` o `FALSE`).
    """)
    return


@app.cell
def _(mo):
    _df_ej1 = mo.sql(
        f"""
        -- Escribe tu consulta aquí
        SELECT 
            target_gender,
            AVG(respect) as promedio_respeto,
            AVG(insult) as promedio_insulto
        FROM comentarios
        GROUP BY target_gender
        """
    )
    return (_df_ej1,)


@app.cell
def _(mo):
    mo.md(r"""
    **Ejercicio 2: Anotadores Severos (CTEs y HAVING)**
    Encuentra cuántos anotadores han evaluado al menos 10 comentarios y su puntaje de odio (`hate_speech_score`) promedio es mayor a 1. Utiliza `HAVING`.
    """)
    return


@app.cell
def _(mo):
    _df_ej2 = mo.sql(
        f"""
        -- Escribe tu consulta aquí
        SELECT 
            annotator_id,
            COUNT(*) as cantidad_evaluaciones,
            AVG(hate_speech_score) as score_promedio
        FROM comentarios
        GROUP BY annotator_id
        HAVING COUNT(*) >= 10 AND AVG(hate_speech_score) > 1
        """
    )
    return (_df_ej2,)


@app.cell
def _(mo):
    mo.md(r"""
    **Ejercicio 3: Clasificación de Violencia con CASE WHEN**
    Crea una consulta que muestre el texto, la columna `violence`, y una nueva columna llamada `nivel_violencia` que sea 'Alta' si `violence > 2`, 'Media' si `violence > 0`, y 'Nula' en cualquier otro caso. Muestra los primeros 10 resultados.
    """)
    return


@app.cell
def _(mo):
    _df_ej3 = mo.sql(
        f"""
        -- Escribe tu consulta aquí
        SELECT 
            text,
            violence,
            CASE 
                WHEN violence > 2 THEN 'Alta'
                WHEN violence > 0 THEN 'Media'
                ELSE 'Nula'
            END AS nivel_violencia
        FROM comentarios
        LIMIT 10
        """
    )
    return (_df_ej3,)


if __name__ == "__main__":
    app.run()
