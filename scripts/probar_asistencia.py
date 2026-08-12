"""Pasa lista de verdad contra el Apps Script del profesor."""

import sys

from playwright.sync_api import sync_playwright

URL = sys.argv[1]

with sync_playwright() as p:
    nav = p.chromium.launch(headless=True, channel="msedge")
    page = nav.new_page(viewport={"width": 1500, "height": 1400})
    page.goto(URL, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_function("() => document.body.innerText.includes('Pasa lista')", timeout=420_000)

    def txt(s):
        return page.get_by_text(s, exact=False).count()

    # esperar con paciencia: en modo edit las celdas tardan mas en ejecutarse
    boton = page.locator("button", has_text="Registrar mi asistencia").first
    for i in range(30):
        page.wait_for_timeout(10_000)
        if boton.count() > 0:
            print(f"boton aparecio tras ~{(i + 1) * 10}s")
            break
    print("boton de asistencia presente:", boton.count() > 0)
    if boton.count() == 0:
        print("!! nunca aparecio")
        nav.close()
        sys.exit(1)
    print("deshabilitado sin datos (correcto):", not boton.is_enabled())

    print("\nllenando nombre y matricula...")
    page.get_by_placeholder("Nombre Apellido").first.click()
    page.keyboard.type("PRUEBA ASISTENCIA - borrar")
    page.keyboard.press("Enter")
    page.get_by_placeholder("A01234567").first.click()
    page.keyboard.type("TEST-ASIST")
    page.keyboard.press("Enter")
    page.wait_for_timeout(4000)

    print("boton habilitado ahora:", boton.is_enabled())
    if not boton.is_enabled():
        print("!! no se puede registrar")
        nav.close()
        sys.exit(1)

    print("\nREGISTRANDO...")
    boton.click()
    ok = False
    for _ in range(20):
        page.wait_for_timeout(3000)
        if txt("Asistencia registrada") > 0:
            ok = True
            break
        if txt("No se pudo registrar") > 0:
            break

    print("  resultado:", "✅ Asistencia registrada" if ok else "❌ fallo")
    if not ok:
        err = page.get_by_text("No se pudo registrar", exact=False)
        if err.count():
            print("  detalle:", err.first.evaluate("e => e.closest('div').innerText")[:300])

    print("\nprobando que NO se re-registre al editar el nombre...")
    page.get_by_placeholder("Nombre Apellido").first.click()
    page.keyboard.type(" X")
    page.keyboard.press("Enter")
    page.wait_for_timeout(6000)
    print("  (revisa la hoja: debe haber UNA sola fila de asistencia de prueba)")

    page.screenshot(path=sys.argv[2], full_page=False)
    nav.close()
    sys.exit(0 if ok else 1)
