# Recibir las entregas en una hoja de cálculo

El ejercicio corre entero en el navegador del alumno, así que no hay servidor donde
guardar nada. Este Apps Script es ese servidor: un endpoint mínimo que recibe el JSON
de respuestas y lo agrega como una fila en una hoja de Google tuya.

Se configura una vez, en unos 10 minutos.

## Pasos

1. **Crea la hoja.** Ve a [sheets.new](https://sheets.new) y ponle un nombre
   (por ejemplo *CDII — Entregas*). No hace falta crear encabezados: el script los
   escribe solo la primera vez.

2. **Abre el editor de scripts.** En esa hoja: menú **Extensiones → Apps Script**.

3. **Pega el código.** Borra el contenido de `Código.gs` y pega todo
   [`Codigo.gs`](Codigo.gs) de esta carpeta. Guarda (💾).

4. **Publica como aplicación web.** Botón **Implementar → Nueva implementación**:
   - Tipo: **Aplicación web** (el ícono de engranaje ⚙️ junto a "Seleccionar tipo").
   - Ejecutar como: **Yo**.
   - Quién tiene acceso: **Cualquier usuario**. ⚠️ Este es el paso que más se
     equivoca. Si eliges "Cualquier usuario con cuenta de Google", los alumnos
     recibirán un error de permisos, porque la petición viaja sin sesión iniciada.
   - **Implementar** → Google pedirá autorizar el script. Acepta.
     Aparecerá una advertencia de "app no verificada": es normal para tus propios
     scripts. Haz clic en *Configuración avanzada* → *Ir a (nombre del proyecto)*.

5. **Copia la URL.** Termina en `/exec`. Se ve así:
   `https://script.google.com/macros/s/AKfy...largo.../exec`

6. **Compruébala.** Ábrela en el navegador. Debe responder:
   `{"ok":true,"mensaje":"Receptor de entregas CDII activo"}`

7. **Pégala en el notebook.** En [`01_sql/ejercicio_01.py`](../../01_sql/ejercicio_01.py),
   en la constante `ENDPOINT` de la celda de configuración:

   ```python
   ENDPOINT = "https://script.google.com/macros/s/AKfy.../exec"
   ```

   Mientras esté vacía, el botón de enviar aparece **deshabilitado** y el alumno solo
   puede entregar descargando el archivo. Eso es a propósito: es preferible un botón
   apagado a uno que falla.

8. **Vuelve a publicar el sitio** (push a `main`, o `.\scripts\export_wasm.ps1` en local).

## Qué llega a la hoja

Una fila por entrega, con estas columnas:

| fecha_servidor | nombre | matricula | curso | ejercicio | contestadas | p1 … p6, bonus | enviado_en_cliente |
|---|---|---|---|---|---|---|---|

Las columnas `p1`…`bonus` traen el SQL tal como lo escribió el alumno, listo para
copiar y ejecutar al calificar.

Si un alumno entrega dos veces quedan las dos filas. Para quedarte con la última por
matrícula, ordena por `fecha_servidor` descendente y quita duplicados, o usa esta
fórmula en una hoja aparte:

```
=QUERY(respuestas!A:N; "select B, C, max(A) where C is not null group by B, C label max(A) 'última entrega'"; 1)
```

## Al cambiar el código del script

Cada vez que edites `Codigo.gs` tienes que hacer **Implementar → Administrar
implementaciones → ✏️ editar → Versión: Nueva versión → Implementar**. Si solo
guardas, la URL sigue sirviendo la versión vieja. La URL no cambia.

## Detalles que importan

**Por qué se envía como `text/plain` y no `application/json`.** Mandar
`Content-Type: application/json` desde el navegador dispara una petición CORS de
verificación previa (`OPTIONS`) que Apps Script no sabe responder, y el envío falla.
Con `text/plain` el navegador la manda directo. El script hace `JSON.parse` del
cuerpo igual. No cambies esto en `ejercicio_01.py` sin probarlo.

**La URL queda a la vista de los alumnos.** El sitio es estático: cualquiera que
abra el código fuente la encuentra. Con este script eso significa que alguien podría
agregar filas basura a la hoja. No puede leer ni borrar las entregas de otros. Para
una tarea de clase es un riesgo aceptable; si te preocupa, revisa las filas por
`matricula` contra tu lista de grupo.

**Nada de esto es verificable.** El alumno controla su navegador: puede enviar el
nombre que quiera y las respuestas que quiera. Sirve para recolectar tarea, no como
examen vigilado.

**Las respuestas incluyen texto del dataset**, que contiene lenguaje ofensivo por su
naturaleza (es un corpus de discurso de odio). La hoja va a acumular ese contenido
junto con nombres de alumnos. Tenlo en cuenta al decidir con quién la compartes.
