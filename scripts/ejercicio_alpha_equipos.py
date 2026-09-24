"""Los numeros del ejercicio de alpha por equipos (presentacion 05).

Existe por una razon: la presentacion muestra el calculo a mano, paso a paso, con
cifras escritas en el HTML. Si esas cifras estan mal, el ejercicio ensena a calcular
mal. Este script las recalcula desde las etiquetas crudas y verifica con `assert`
que coincidan con lo publicado.

Sin dependencias: el .venv de este repo no tiene numpy y para 50 etiquetas no hace
falta. Cada alpha se calcula por DOS caminos distintos —la formula corta por unidad
y la matriz de coincidencias— y se comprueba que den lo mismo.

Uso:
    .venv/Scripts/python.exe scripts/ejercicio_alpha_equipos.py
"""

from collections import Counter
from fractions import Fraction

CATEGORIAS = ["afín", "crítica", "neutral"]

# Las 10 preguntas son las de 03_machine_learning/prueba_jev/script_prueba.R.
# Estas son las etiquetas del equipo de ejemplo ("Equipo Delta") en las dos rondas.
# Cada lista es una unidad: los 5 juicios, uno por integrante.
RONDA_1 = [
    ["afín", "afín", "afín", "neutral", "afín"],          # P1  felicita homicidios
    ["afín", "neutral", "afín", "neutral", "afín"],       # P2  el PAN voto en contra
    ["afín", "afín", "neutral", "afín", "afín"],          # P3  dano del neoliberalismo
    ["afín", "afín", "afín", "neutral", "afín"],          # P4  privilegios del PRIAN
    ["neutral", "afín", "neutral", "afín", "neutral"],    # P5  cuentenos las becas
    ["crítica", "crítica", "crítica", "crítica", "crítica"],   # P6  Guanajuato
    ["crítica", "crítica", "crítica", "crítica", "neutral"],   # P7  huachicol
    ["crítica", "crítica", "crítica", "neutral", "crítica"],   # P8  IMSS sin medicinas
    ["crítica", "crítica", "neutral", "crítica", "afín"],      # P9  candidato de Morena
    ["crítica", "crítica", "crítica", "crítica", "crítica"],   # P10 militarizacion
]

# Misma gente, mismas preguntas, despues de escribir la rubrica.
RONDA_2 = [
    ["afín", "afín", "afín", "afín", "afín"],
    ["afín", "afín", "neutral", "afín", "afín"],
    ["afín", "afín", "afín", "afín", "afín"],
    ["afín", "afín", "afín", "afín", "afín"],
    ["afín", "neutral", "afín", "afín", "neutral"],
    ["crítica", "crítica", "crítica", "crítica", "crítica"],
    ["crítica", "crítica", "crítica", "crítica", "crítica"],
    ["crítica", "crítica", "crítica", "neutral", "crítica"],
    ["crítica", "crítica", "crítica", "crítica", "afín"],
    ["crítica", "crítica", "crítica", "crítica", "crítica"],
]


# ---------------------------------------------------------------------------
# Variante de UNA SOLA PREGUNTA (presentacion 06).
#
# La pregunta de la mananera de la lamina 08 de la presentacion 04, partida en
# sus cinco movimientos. Los fragmentos son las unidades: con una sola unidad el
# alpha es 0 por construccion (Do == De siempre), asi que segmentar no es un
# adorno pedagogico, es lo que hace que exista el numero.
# ---------------------------------------------------------------------------

FRAGMENTOS_R1 = [
    ["neutral", "neutral", "afín", "neutral", "afín"],         # S1 el dato
    ["afín", "afín", "afín", "afín", "afín"],                  # S2 la evaluación
    ["afín", "afín", "crítica", "afín", "neutral"],            # S3 la culpa a Calderón
    ["afín", "afín", "afín", "neutral", "afín"],               # S4 la conclusión regalada
    ["afín", "crítica", "afín", "afín", "neutral"],            # S5 el PRIAN
]

FRAGMENTOS_R2 = [
    ["neutral", "neutral", "neutral", "neutral", "neutral"],
    ["afín", "afín", "afín", "afín", "afín"],
    ["afín", "afín", "afín", "afín", "neutral"],
    ["afín", "afín", "afín", "afín", "afín"],
    ["afín", "afín", "afín", "afín", "afín"],
]


def alpha_corto(unidades):
    """Alpha nominal por la formula corta: solo necesita los conteos por unidad.

    Es la que se hace a mano en la presentacion.
        Do = (1/n) * sum_u [ 1/(m_u-1) * sum_c n_uc * (m_u - n_uc) ]
        De = (1/(n(n-1))) * sum_c n_c * (n - n_c)
    """
    total = Fraction(0)
    n = 0
    globales = Counter()
    for u in unidades:
        m = len(u)
        if m < 2:
            continue
        n += m
        cnt = Counter(u)
        globales.update(cnt)
        total += Fraction(sum(c * (m - c) for c in cnt.values()), m - 1)

    Do = total / n
    De = Fraction(sum(nc * (n - nc) for nc in globales.values()), n * (n - 1))
    return 1 - Do / De, Do, De, n, globales


def matriz_coincidencias(unidades):
    """La matriz o_ck canonica. Segundo camino, para verificar el primero."""
    o = {(c, k): Fraction(0) for c in CATEGORIAS for k in CATEGORIAS}
    for u in unidades:
        m = len(u)
        if m < 2:
            continue
        cnt = Counter(u)
        for c, mc in cnt.items():
            for k, mk in cnt.items():
                resta = 1 if c == k else 0
                o[(c, k)] += Fraction(mc * (mk - resta), m - 1)
    return o


def alpha_desde_matriz(o):
    """Alpha nominal desde la matriz de coincidencias."""
    n = sum(o.values())
    marg = {c: sum(o[(c, k)] for k in CATEGORIAS) for c in CATEGORIAS}
    Do = sum(o[(c, k)] for c in CATEGORIAS for k in CATEGORIAS if c != k) / n
    De = sum(marg[c] * marg[k] for c in CATEGORIAS for k in CATEGORIAS if c != k) / (n * (n - 1))
    return 1 - Do / De


def acuerdo_crudo(unidades):
    """Porcentaje de pares que coinciden. Es la cifra enganosa, la del contraste."""
    iguales = pares = 0
    for u in unidades:
        m = len(u)
        pares += m * (m - 1) // 2
        for c in Counter(u).values():
            iguales += c * (c - 1) // 2
    return Fraction(iguales, pares), iguales, pares


def reporte(nombre, unidades):
    a, Do, De, n, globales = alpha_corto(unidades)
    o = matriz_coincidencias(unidades)
    a2 = alpha_desde_matriz(o)
    assert a == a2, f"{nombre}: los dos caminos no coinciden ({float(a)} vs {float(a2)})"

    crudo, iguales, pares = acuerdo_crudo(unidades)

    print(f"\n=== {nombre} ===")
    print("  desacuerdo por unidad (el sumando 1/(m-1) * sum n_uc(m - n_uc)):")
    for i, u in enumerate(unidades, 1):
        cnt = Counter(u)
        fila = "/".join(f"{cnt.get(c, 0)}" for c in CATEGORIAS)
        d = Fraction(sum(c * (len(u) - c) for c in cnt.values()), len(u) - 1)
        print(f"    P{i:<3} {fila:<8} -> {float(d):>4}")
    print(f"  n = {n}   marginales: " + ", ".join(f"{c}={globales[c]}" for c in CATEGORIAS))
    print(f"  Do = {Do} = {float(Do):.4f}")
    print(f"  De = {De} = {float(De):.6f}")
    print(f"  alpha = {float(a):.4f}")
    print(f"  acuerdo crudo = {iguales}/{pares} = {float(crudo) * 100:.0f}%")
    print("  matriz de coincidencias:")
    print("           " + "".join(f"{c:>10}" for c in CATEGORIAS))
    for c in CATEGORIAS:
        print(f"    {c:<8}" + "".join(f"{float(o[(c, k)]):>10.2f}" for k in CATEGORIAS))
    return a, Do, De, n, globales, crudo


if __name__ == "__main__":
    a1, Do1, De1, n1, g1, crudo1 = reporte("RONDA 1 — instrucción vaga", RONDA_1)
    a2, Do2, De2, n2, g2, crudo2 = reporte("RONDA 2 — con la rúbrica escrita", RONDA_2)

    # Lo que esta impreso en presentaciones/fuentes/05_ejercicio_alpha_jev.html.
    # Si algo de arriba cambia, estos asserts truenan antes de que la clase lo vea.
    assert (n1, n2) == (50, 50)
    assert dict(g1) == {"afín": 18, "crítica": 21, "neutral": 11}, dict(g1)
    assert dict(g2) == {"afín": 23, "crítica": 23, "neutral": 4}, dict(g2)
    assert Do1 == Fraction(39, 100) and De1 == Fraction(1614, 2450)
    assert Do2 == Fraction(18, 100) and De2 == Fraction(1426, 2450)
    assert f"{float(a1):.3f}" == "0.408", float(a1)
    assert f"{float(a2):.3f}" == "0.691", float(a2)
    assert (crudo1, crudo2) == (Fraction(61, 100), Fraction(82, 100))

    print(f"\nEl salto: alpha {float(a1):.3f} -> {float(a2):.3f} "
          f"({float(a2 - a1):+.3f}) sin tocar las preguntas, solo la rúbrica.")

    # ----- Variante de una sola pregunta (presentación 06) -----
    print("\n\n########  VARIANTE DE UNA SOLA PREGUNTA  ########")

    # Primero, por qué hay que segmentar: una unidad sola no produce alpha.
    for etiquetas in (["afín"] * 5, ["afín", "afín", "afín", "neutral", "afín"]):
        try:
            a, Do, De, *_ = alpha_corto([etiquetas])
            print(f"  1 unidad {'/'.join(e[0] for e in etiquetas)}: "
                  f"Do = De = {float(Do):.4f}  ->  alpha = {float(a):.4f}")
            assert a == 0, "con una sola unidad el alpha tiene que ser exactamente 0"
        except ZeroDivisionError:
            print("  1 unidad unánime: De = 0  ->  alpha INDEFINIDO (0/0), no 1")

    f1, Dof1, Def1, nf1, gf1, crudof1 = reporte("FRAGMENTOS — ronda 1", FRAGMENTOS_R1)
    f2, Dof2, Def2, nf2, gf2, crudof2 = reporte("FRAGMENTOS — ronda 2", FRAGMENTOS_R2)

    assert (nf1, nf2) == (25, 25)
    assert dict(gf1) == {"afín": 17, "crítica": 2, "neutral": 6}, dict(gf1)
    assert dict(gf2) == {"afín": 19, "neutral": 6}, dict(gf2)
    assert Dof1 == Fraction(12, 25) and Def1 == Fraction(296, 600)
    assert Dof2 == Fraction(2, 25) and Def2 == Fraction(228, 600)
    assert f"{float(f1):.3f}" == "0.027", float(f1)
    assert f"{float(f2):.3f}" == "0.789", float(f2)
    assert (crudof1, crudof2) == (Fraction(26, 50), Fraction(46, 50))

    # El crédito que cobra De al desbalancearse las categorías, en las dos versiones.
    print(f"\nSi De no hubiera bajado, la ronda 2 daría:")
    print(f"  10 preguntas: {float(1 - Do2 / De1):.3f}  en vez de {float(a2):.3f}")
    print(f"  fragmentos:   {float(1 - Dof2 / Def1):.3f}  en vez de {float(f2):.3f}")

    print("\nTodos los números de las dos láminas verificados.")
