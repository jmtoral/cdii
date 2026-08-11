# 📝 Tema 1: SQL con DuckDB

## 🎯 Objetivos de Aprendizaje

Al completar este tema, los estudiantes podrán:

1. **Consultar datos** usando SQL: `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`
2. **Filtrar texto** con `LIKE` y operadores de comparación
3. **Agregar datos** con `GROUP BY`, `HAVING`, y funciones como `COUNT`, `AVG`, `SUM`
4. **Crear categorías** usando `CASE WHEN`
5. **Estructurar queries complejas** con subqueries y CTEs (`WITH`)
6. **Combinar tablas** usando `JOIN`
7. **Usar DuckDB** como motor SQL embebido para análisis de datos

## 📚 Materiales

| Notebook | Contenido | Duración estimada |
|---|---|---|
| `01_introduccion_sql.py` | SELECT, WHERE, LIKE, ORDER BY, LIMIT | 45 min |
| `02_agregaciones_joins.py` | GROUP BY, HAVING, CASE WHEN, JOINs, CTEs | 60 min |
| `ejercicio_01.py` | Ejercicio evaluable (7 preguntas) | 45 min |

## 🚀 Cómo Usar

### Para estudiar (modo edición)
```bash
marimo edit 01_sql/01_introduccion_sql.py
```

### Para presentar en clase (modo app)
```bash
marimo run 01_sql/01_introduccion_sql.py
```

## 📊 Dataset

Usamos el dataset **Measuring Hate Speech** de UC Berkeley D-Lab:
- ~135,000 anotaciones de comentarios de redes sociales
- Múltiples dimensiones: sentiment, respect, insult, violence, etc.
- Grupos objetivo: race, religion, gender, origin
- Score continuo de hate speech

## 📖 Recursos Adicionales

- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- [SQL Tutorial - W3Schools](https://www.w3schools.com/sql/)
- [Marimo SQL Tutorial](https://docs.marimo.io/guides/working_with_data/sql/)
- [Mode Analytics SQL Tutorial](https://mode.com/sql-tutorial/)
