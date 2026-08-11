/**
 * CDII — Receptor de entregas de los alumnos.
 *
 * Publica este script como aplicación web (ver README.md en esta carpeta) y pega
 * la URL resultante en la constante ENDPOINT de 01_sql/ejercicio_01.py.
 *
 * Cada entrega se agrega como una fila nueva. Nunca se sobrescribe nada: si un
 * alumno entrega dos veces, quedan las dos filas y tú decides con cuál quedarte
 * (normalmente la última por fecha).
 */

var NOMBRE_HOJA = 'respuestas';

var COLUMNAS = [
  'fecha_servidor',
  'nombre',
  'matricula',
  'curso',
  'ejercicio',
  'contestadas',
  'p1',
  'p2',
  'p3',
  'p4',
  'p5',
  'p6',
  'bonus',
  'enviado_en_cliente'
];

function doPost(e) {
  var lock = LockService.getScriptLock();
  // Sin el lock, dos alumnos entregando a la vez pueden escribir en la misma fila.
  lock.waitLock(30000);
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return responder_({ ok: false, error: 'Petición sin cuerpo' });
    }

    var datos = JSON.parse(e.postData.contents);
    var respuestas = datos.respuestas || {};
    var hoja = obtenerHoja_();

    hoja.appendRow([
      new Date(),
      datos.nombre || '',
      datos.matricula || '',
      datos.curso || '',
      datos.ejercicio || '',
      datos.contestadas || 0,
      respuestas.p1 || '',
      respuestas.p2 || '',
      respuestas.p3 || '',
      respuestas.p4 || '',
      respuestas.p5 || '',
      respuestas.p6 || '',
      respuestas.bonus || '',
      datos.enviado_en || ''
    ]);

    return responder_({ ok: true, recibido: datos.matricula || datos.nombre || '' });
  } catch (err) {
    return responder_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/** Permite abrir la URL en el navegador para comprobar que está viva. */
function doGet() {
  return responder_({ ok: true, mensaje: 'Receptor de entregas CDII activo' });
}

function obtenerHoja_() {
  var libro = SpreadsheetApp.getActiveSpreadsheet();
  var hoja = libro.getSheetByName(NOMBRE_HOJA);
  if (!hoja) {
    hoja = libro.insertSheet(NOMBRE_HOJA);
  }
  if (hoja.getLastRow() === 0) {
    hoja.appendRow(COLUMNAS);
    hoja.setFrozenRows(1);
  }
  return hoja;
}

function responder_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
