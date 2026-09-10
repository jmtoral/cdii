"""Construye las presentaciones a partir de sus fuentes.

De cada fuente salen DOS archivos distintos, y por eso existe este script:

1. `presentaciones/NN.html` — documento HTML **completo**, con doctype y
   `<meta charset="utf-8">`. Es el que se publica en GitHub Pages y el que alguien
   puede abrir como archivo local.

2. `presentaciones/.artifact/NN.html` — **fragmento** (sin doctype ni <head>), que es
   lo que espera el publicador de Artifacts de Claude: ahí el envoltorio pone la
   cabeza. Esta carpeta está en .gitignore porque es material derivado.

Los dos llevan el logo incrustado como data URI.

⚠️ Dos cosas que ya salieron mal antes y por eso están automatizadas aquí:

- **El charset no es opcional.** Sin la etiqueta, el navegador interpreta el archivo
  como Latin-1 y todos los acentos salen rotos: "Agrupar es fÃ¡cil". No se nota en el
  Artifact —su envoltorio declara UTF-8— así que el error solo aparece en el sitio.

- **Nunca publiques como Artifact el archivo de `fuentes/`.** Todavía tiene el
  marcador `__LOGO__` en el `src`, así que el logo sale roto. Publica el de
  `.artifact/`.

Uso:
    python scripts/construir_presentaciones.py
"""

import base64
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTES = RAIZ / "presentaciones" / "fuentes"
SALIDA = RAIZ / "presentaciones"
PARA_ARTIFACT = SALIDA / ".artifact"
LOGO = RAIZ / "logo.jpg"

ESQUELETO = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="Manuel Toral">
{cabeza}</head>
<body>
{cuerpo}</body>
</html>
"""


def partir(html: str) -> tuple[str, str]:
    """Separa el <title>/<style> (cabeza) del resto (cuerpo)."""
    cabeza, cuerpo = [], []
    dentro_de_style = False
    for linea in html.splitlines(keepends=True):
        desnuda = linea.strip()
        if desnuda.startswith("<title>"):
            cabeza.append(linea)
            continue
        if desnuda.startswith("<style"):
            dentro_de_style = True
            cabeza.append(linea)
            continue
        if dentro_de_style:
            cabeza.append(linea)
            if desnuda.startswith("</style>"):
                dentro_de_style = False
            continue
        cuerpo.append(linea)
    return "".join(cabeza), "".join(cuerpo).lstrip("\n")


def main() -> int:
    if not FUENTES.is_dir():
        print(f"No existe {FUENTES}")
        return 1

    uri = "data:image/jpeg;base64," + base64.b64encode(LOGO.read_bytes()).decode("ascii")
    fuentes = sorted(FUENTES.glob("*.html"))
    if not fuentes:
        print(f"No hay fuentes en {FUENTES}")
        return 1

    PARA_ARTIFACT.mkdir(exist_ok=True)
    fallos = 0

    for fuente in fuentes:
        html = fuente.read_text(encoding="utf-8")
        if "__LOGO__" not in html:
            print(f"  ⚠️  {fuente.name}: no tiene marcador __LOGO__")
        html = html.replace("__LOGO__", uri)

        # 1) Documento completo, para GitHub Pages
        cabeza, cuerpo = partir(html)
        completo = ESQUELETO.format(cabeza=cabeza, cuerpo=cuerpo)
        (SALIDA / fuente.name).write_text(completo, encoding="utf-8")

        # 2) Fragmento con logo, para publicar como Artifact
        (PARA_ARTIFACT / fuente.name).write_text(html, encoding="utf-8")

        # Comprobaciones: los dos errores que ya nos costaron una republicación
        ok_charset = 'charset="utf-8"' in completo
        ok_logo = "__LOGO__" not in completo and "__LOGO__" not in html
        if not (ok_charset and ok_logo):
            fallos += 1
        print(
            f"  {'✅' if ok_charset and ok_logo else '❌'} {fuente.name}"
            f"  ({len(completo) / 1024:.0f} KB"
            f", charset={'sí' if ok_charset else 'NO'}"
            f", logo={'incrustado' if ok_logo else 'ROTO'})"
        )

    print(f"\n{len(fuentes)} presentación(es) en {SALIDA}")
    print(f"Para publicar como Artifact usa los de: {PARA_ARTIFACT}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
