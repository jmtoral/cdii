"""Construye las presentaciones a partir de sus fuentes.

De cada fuente salen dos cosas distintas, y por eso existe este script:

1. `presentaciones/NN.html` — documento HTML **completo**, con doctype y
   `<meta charset="utf-8">`. Es el que se publica en GitHub Pages y el que alguien
   puede abrir como archivo local.

2. La versión para publicar como Artifact de Claude, que debe ser un **fragmento**
   (sin doctype ni <head>) porque ahí el envoltorio los pone.

⚠️ El charset no es opcional. Sin la etiqueta, el navegador interpreta el archivo como
Latin-1 y todos los acentos salen rotos: "Agrupar es fÃ¡cil". No se nota en el Artifact
—su envoltorio declara UTF-8— así que el error solo aparece en el sitio publicado.

Uso:
    python scripts/construir_presentaciones.py
"""

import base64
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTES = RAIZ / "presentaciones" / "fuentes"
SALIDA = RAIZ / "presentaciones"
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


def main() -> int:
    if not FUENTES.is_dir():
        print(f"No existe {FUENTES}")
        return 1

    uri = "data:image/jpeg;base64," + base64.b64encode(LOGO.read_bytes()).decode("ascii")
    fuentes = sorted(FUENTES.glob("*.html"))
    if not fuentes:
        print(f"No hay fuentes en {FUENTES}")
        return 1

    for fuente in fuentes:
        html = fuente.read_text(encoding="utf-8")
        if "__LOGO__" not in html:
            print(f"  ⚠️  {fuente.name}: sin marcador __LOGO__")
        html = html.replace("__LOGO__", uri)

        # El <title> y el <style> van en la cabeza del documento completo.
        cabeza, cuerpo = [], []
        dentro_de_style = False
        for linea in html.splitlines(keepends=True):
            desnuda = linea.strip()
            if desnuda.startswith("<title>") or desnuda.startswith("<style"):
                dentro_de_style = desnuda.startswith("<style")
                cabeza.append(linea)
                if desnuda.startswith("<title>"):
                    dentro_de_style = False
                continue
            if dentro_de_style:
                cabeza.append(linea)
                if desnuda.startswith("</style>"):
                    dentro_de_style = False
                continue
            cuerpo.append(linea)

        completo = ESQUELETO.format(cabeza="".join(cabeza), cuerpo="".join(cuerpo).lstrip("\n"))
        destino = SALIDA / fuente.name
        destino.write_text(completo, encoding="utf-8")

        tiene_charset = 'charset="utf-8"' in completo
        print(f"  ✅ {destino.name}  ({len(completo) / 1024:.0f} KB, charset={'sí' if tiene_charset else 'NO'})")

    print(f"\n{len(fuentes)} presentación(es) construida(s) en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
