remotes::install_github("mountainMath/JevR")
install.packages("usethis")
usethis::edit_r_environ()


# Prueba de Jev: ¿una pregunta de la mañanera le sirve al gobierno o no?
# Tres primitivas sobre el mismo texto: noul (sí/no), choice (hacia dónde
# carga) y score (qué tan confrontativa). Las 10 preguntas las escribí a mano
# con la etiqueta puesta, así que `esperado` sirve para ver si el criterio hace
# lo que uno cree, no para estimar qué tan bien clasifica.

library(tidyverse)
library(JevR)

# ---------------------------------------------------------------------------
# Jev paso a paso: una sola pregunta de la mañanera, una primitiva a la vez.
#
# La idea es NO armar todavía el objeto `questions` con las tres juntas. Cada
# paso manda una sola pregunta al modelo y se mira la salida antes de seguir.
# Cuando las tres den por separado lo que uno espera, ahí se juntan.
#
# El caso elegido es lo más inequívoco que hay: afirma un logro del gobierno
# (los homicidios bajaron) Y le cuelga la violencia a Calderón y al PRIAN. Si
# algo no sale claro aquí, el problema es cómo está redactado el criterio, no
# el caso.
# ---------------------------------------------------------------------------


pregunta <- "Y, Presidenta, a 2 días ya de terminar el mes de mayo, el promedio de los homicidios diarios continúa la tendencia del mes anterior, es decir, está por debajo de los 60 homicidios al día. La tendencia a la baja en estas cifras es ya una constante en los últimos meses y significa un avance muy importante en materia de seguridad.

Después de años de violencia por la guerra emprendida por Felipe Calderón, Presidenta, ¿podemos pensar ya que con las claras tendencias de disminución de los homicidios estamos entrando en una nueva etapa donde pronto tendremos un país sin la violencia heredada por los gobiernos del PRIAN?"


# ---------------------------------------------------------------------------
# PASO 1. El noul desnudo, sin criterios.
#
# Un noul devuelve UNA probabilidad entre 0 y 1: no hay etiqueta ni confianza
# aparte, el número es las dos cosas. Cerca de 1 es sí rotundo, cerca de 0 es
# no rotundo, y 0.5 NO quiere decir "medio afín": quiere decir que el modelo
# no se decide.
#
# Sin `yes` ni `no`, "favorece al gobierno" lo interpreta el modelo con su
# propio criterio. Este paso existe para tener contra qué comparar el paso 2.
# ---------------------------------------------------------------------------

paso1 <- jev(pregunta, list(
  afin = jev_noul("¿Esta pregunta de un periodista favorece al gobierno de México?")
))

paso1


# ---------------------------------------------------------------------------
# PASO 2. El mismo noul, ahora con los criterios puestos.
#
# `yes` y `no` son donde uno define qué cuenta, en lugar de dejárselo al
# modelo. Las dos ramas del `yes` son las dos formas de favorecer: halagar al
# gobierno, o pegarle a un rival suyo.
#
# COMPARA ESTE NÚMERO CONTRA EL DEL PASO 1. Es lo que más enseña de todo el
# script: si casi no se mueve, tus criterios no están agregando nada y puedes
# ahorrártelos. Si se mueve mucho, entonces sí estás definiendo el constructo
# tú y no el modelo.
# ---------------------------------------------------------------------------

paso2 <- jev(pregunta, list(
  afin = jev_noul(
    "¿Esta pregunta de un periodista favorece al gobierno de México?",
    yes = "Elogia al gobierno o a la presidenta, o le pega a un rival suyo: PAN, PRI, PRIAN, Movimiento Ciudadano o el periodo neoliberal.",
    no  = "Critica al gobierno, o solo pide un dato sin afirmar nada."
  )
))

paso2


# ---------------------------------------------------------------------------
# PASO 3. Un choice, solo.
#
# El noul dice CUÁNTO; el choice dice HACIA DÓNDE. Aquí sí hay confianza
# aparte de la respuesta, porque la confianza mide qué tan concentrada quedó
# la distribución entre las opciones.
#
# Las tres opciones tienen que ser excluyentes y cubrir todo, o el modelo se
# ve forzado a meter con calzador lo que no cabe.
# ---------------------------------------------------------------------------

paso3 <- jev(pregunta, list(
  postura = jev_choice(
    "¿Hacia dónde carga esta pregunta?",
    c("crítica" = "Da por sentado algo malo del gobierno: un fracaso, una omisión, una contradicción",
      "afin"    = "Da por sentado algo bueno del gobierno, o algo malo de un rival suyo",
      "neutral" = "No da nada por sentado: pide un dato, una opinión o una explicación")
  )
))

paso3

# La distribución completa, no solo la opción ganadora. Vale la pena mirarla:
# una pregunta tan clara como ésta debería salir muy concentrada en `afin`. Si
# la probabilidad está repartida, el choice no va a servir para los casos
# dudosos de verdad, que son la mayoría del corpus.
jev_probabilities(paso3, "postura")


# ---------------------------------------------------------------------------
# PASO 4. Un score, solo.
#
# El score es para lo que vive en un eje ordenado, y los niveles tienen que
# describir situaciones concretas, no ser adjetivos sueltos: "Firme" no le
# dice nada al modelo, "cuestiona un resultado o pide cuentas" sí.
#
# Lo que hay que vigilar aquí: que mida FUNCIÓN y no FORMA. Esta pregunta es
# larga y formal, pero no pide cuentas de nada —trae la conclusión ya armada y
# solo pide confirmarla—, así que debería caer en el nivel amable. Si sale
# "Neutra", los niveles se están dejando llevar por el tono y no por lo que la
# pregunta hace.
# ---------------------------------------------------------------------------

paso4 <- jev(pregunta, list(
  dureza = jev_score(
    "¿Qué tan confrontativa es la pregunta?",
    c("Amable: agradece, felicita o invita a explicar",
      "Neutra: pregunta sin tomar postura",
      "Firme: cuestiona un resultado o pide cuentas",
      "Dura: afirma una falla y exige explicarla")
  )
))

paso4

jev_probabilities(paso4, "dureza")


# ---------------------------------------------------------------------------
# PASO 5. Ya juntas, en una sola llamada.
#
# Las tres preguntas son independientes entre sí —ninguna necesita la
# respuesta de otra— así que van en la misma llamada y se resuelven en
# paralelo. No se pueden ver entre ellas, que es justo lo que uno quiere:
# `afin` y `postura` preguntan casi lo mismo a propósito, y si discrepan es
# porque la pregunta es genuinamente ambigua, no porque una contagió a la otra.
# ---------------------------------------------------------------------------

questions <- list(
  afin = jev_noul(
    "¿Esta pregunta de un periodista favorece al gobierno de México?",
    yes = "Elogia al gobierno o a la presidenta, o le pega a un rival suyo: PAN, PRI, PRIAN, Movimiento Ciudadano o el periodo neoliberal.",
    no  = "Critica al gobierno, o solo pide un dato sin afirmar nada."
  ),
  postura = jev_choice(
    "¿Hacia dónde carga esta pregunta?",
    c("crítica" = "Da por sentado algo malo del gobierno: un fracaso, una omisión, una contradicción",
      "afin"    = "Da por sentado algo bueno del gobierno, o algo malo de un rival suyo",
      "neutral" = "No da nada por sentado: pide un dato, una opinión o una explicación")
  ),
  dureza = jev_score(
    "¿Qué tan confrontativa es la pregunta?",
    c("Amable: agradece, felicita o invita a explicar",
      "Neutra: pregunta sin tomar postura",
      "Firme: cuestiona un resultado o pide cuentas",
      "Dura: afirma una falla y exige explicarla")
  )
)

res <- jev(pregunta, questions)
res

# Una sola fila con todo: afin, postura, postura_confidence, dureza, ...
jev_tidy(res)










# --- Las preguntas -----------------------------------------------------------

preguntas <- tribble(
  ~esperado,  ~texto,
  "afín",     "Presidenta, la felicito por la reducción de homicidios, ¿nos puede explicar cómo lo lograron?",
  "afín",     "¿Qué opina de que el PAN haya votado en contra de la reforma que beneficia a los adultos mayores?",
  "afín",     "Presidenta, ¿cuánto daño dejó el periodo neoliberal en el sistema de salud que ustedes están reconstruyendo?",
  "afín",     "El PRIAN sigue defendiendo los privilegios fiscales de siempre, ¿usted cómo lo ve?",
  "afín",     "Mucha gente todavía no conoce el programa de becas, ¿nos puede contar a detalle en qué consiste?",
  "crítica",  "Presidenta, los homicidios en Guanajuato no han bajado, ¿por qué su estrategia no ha funcionado ahí?",
  "crítica",  "¿Por qué su gobierno no ha investigado las denuncias de huachicol contra López Beltrán?",
  "crítica",  "El hospital del IMSS-Bienestar lleva ocho meses sin medicamentos, ¿no contradice esto lo que usted dijo aquí?",
  "crítica",  "Morena postuló a un candidato con denuncias por violencia familiar, ¿no le parece una contradicción?",
  "crítica",  "Usted dijo que no habría militarización, pero el Ejército ya controla puertos y aduanas, ¿cómo lo explica?"
)

# --- Los criterios -----------------------------------------------------------
# Las dos últimas frases del `no` son candados, no relleno:
#   - si el reclamo aterriza en el gobierno aunque mencione a un tercero, es NO
#   - Morena es el partido gobernante: pegarle a Morena es criticar al gobierno

questions <- list(
  afin = jev_noul(
    "¿Esta pregunta de un periodista favorece al gobierno de México?",
    yes = "Elogia al gobierno o a la presidenta, o le pega a un rival suyo: PAN, PRI, PRIAN, Movimiento Ciudadano o el periodo neoliberal.",
    no  = "Critica al gobierno, o solo pide un dato sin afirmar nada. Criticar a Morena es criticar al gobierno, no a un rival."
  ),
  postura = jev_choice(
    "¿Hacia dónde carga esta pregunta?",
    c("crítica" = "Da por sentado algo malo del gobierno: un fracaso, una omisión, una contradicción",
      "afin"    = "Da por sentado algo bueno del gobierno, o algo malo de un rival suyo",
      "neutral" = "No da nada por sentado: pide un dato, una opinión o una explicación")
  ),
  dureza = jev_score(
    "¿Qué tan confrontativa es la pregunta?",
    c("Amable: agradece, felicita o invita a explicar",
      "Neutra: pregunta sin tomar postura",
      "Firme: cuestiona un resultado o pide cuentas",
      "Dura: afirma una falla y exige explicarla")
  )
)

# --- Una llamada por pregunta ------------------------------------------------

salida <- preguntas |>
  mutate(res = map(texto, \(t) jev_tidy(jev(t, questions)))) |>
  unnest(res)

salida |>
  arrange(desc(afin)) |>
  select(esperado, afin, postura, postura_confidence, dureza, texto) |>
  print(n = Inf)

# --- Qué tanto coincide con lo que yo esperaba -------------------------------

salida |>
  count(esperado, postura) |>
  pivot_wider(names_from = postura, values_from = n, values_fill = 0)

# La distribución completa de un caso, no solo el nivel elegido:
jev_probabilities(jev(preguntas$texto[9], questions), "postura")
