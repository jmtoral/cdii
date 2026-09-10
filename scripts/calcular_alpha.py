"""Alpha de Krippendorff calculado sobre el corpus de la clase.

Implementacion directa de la formula, sin librerias externas:

    alpha = 1 - Do/De

donde Do es el desacuerdo observado y De el desacuerdo esperado por azar,
ambos a partir de la matriz de coincidencias.
"""

from collections import Counter

import duckdb
import numpy as np

db = duckdb.connect()
db.execute("CREATE TABLE plano AS SELECT * FROM read_parquet('D:/CLASES/cdii/01_sql/public/hate_speech.parquet')")


def alpha(unidades, metrica="nominal"):
    """unidades: lista de listas de valores (uno por evaluador) para cada unidad."""
    valores = sorted({v for u in unidades for v in u})
    idx = {v: i for i, v in enumerate(valores)}
    k = len(valores)

    # Matriz de coincidencias
    o = np.zeros((k, k))
    for u in unidades:
        n_u = len(u)
        if n_u < 2:
            continue
        cnt = Counter(idx[v] for v in u)
        for c, mc in cnt.items():
            for kk, mk in cnt.items():
                o[c, kk] += mc * (mk - (1 if c == kk else 0)) / (n_u - 1)

    n = o.sum()
    n_c = o.sum(axis=1)

    # Metrica de diferencia
    d = np.zeros((k, k))
    for i, vi in enumerate(valores):
        for j, vj in enumerate(valores):
            if metrica == "nominal":
                d[i, j] = 0.0 if i == j else 1.0
            else:  # intervalo
                d[i, j] = (float(vi) - float(vj)) ** 2

    Do = (o * d).sum() / n
    De = (np.outer(n_c, n_c) * d).sum() / (n * (n - 1))
    return 1 - Do / De, int(n)


def cargar(columna, solo_calibracion=False):
    filtro = "WHERE platform = 1" if solo_calibracion else ""
    filas = db.sql(f"""
        SELECT comment_id, {columna}
        FROM plano
        {filtro}
        {'AND' if filtro else 'WHERE'} {columna} IS NOT NULL
    """).fetchall()
    porU = {}
    for cid, v in filas:
        porU.setdefault(cid, []).append(v)
    return [u for u in porU.values() if len(u) >= 2]


print("=== ALPHA SOBRE EL CONJUNTO DE CALIBRACION (70 comentarios, cientos de jueces) ===")
for col, met in [("target_race", "nominal"), ("target_religion", "nominal"),
                 ("respect", "intervalo"), ("insult", "intervalo"),
                 ("violence", "intervalo"), ("hatespeech", "intervalo")]:
    u = cargar(col, solo_calibracion=True)
    a, n = alpha(u, met)
    print(f"  {col:18} {met:10} alpha = {a:6.3f}   ({len(u)} unidades, {n:,.0f} pares)")

print("\n=== ALPHA SOBRE TODO EL CORPUS ===")
for col, met in [("target_race", "nominal"), ("respect", "intervalo"), ("insult", "intervalo")]:
    u = cargar(col)
    a, n = alpha(u, met)
    print(f"  {col:18} {met:10} alpha = {a:6.3f}   ({len(u):,} unidades)")

print("\n=== acuerdo CRUDO en target_race (para comparar con alpha) ===")
u = cargar("target_race", solo_calibracion=True)
acuerdos = [max(Counter(x).values()) / len(x) for x in u]
print(f"  porcentaje de acuerdo promedio: {100*np.mean(acuerdos):.1f}%")
print(f"  ...pero alpha dice: {alpha(u,'nominal')[0]:.3f}")
