# ---------------------------------------------------------------------------
# Ejercicio de la lámina 05: el alpha del equipo, y qué pasa cuando metes a Jev.
#
# Continúa `script_prueba.R`: las 10 preguntas son las mismas, los criterios son
# los mismos. Lo que cambia es que ahora hay CINCO personas etiquetando las
# mismas preguntas, y la pregunta del ejercicio es si coinciden lo suficiente
# como para que sus etiquetas sirvan de algo.
#
# Se corre en cuatro partes. No las corras todas de golpe:
#   PARTE A — el alpha de los cinco humanos (esto se puede correr sin API key)
#   PARTE B — Jev sobre las mismas 10 preguntas (aquí sí gasta llamadas)
#   PARTE C — las dos lecturas: Jev como sexto anotador, y la perspectivista
#   PARTE D — kappa de Cohen: una persona contra otra, y una persona contra Jev
#
# Todo el cálculo vive en FORMATO LARGO: una fila por juicio, con columnas
# (pregunta, anotador, etiqueta). Eso es lo que hace que el alpha sea una
# tubería de dplyr en vez de una función que manosea matrices, y es también
# como te van a llegar los datos si algún día los sacas de una base.
#
# Requisitos: tidyverse y JevR. No hace falta `irr`: las fórmulas son cortas y
# conviene verlas, porque son exactamente las que hiciste a mano.
# ---------------------------------------------------------------------------

library(tidyverse)


# ═══════════════════════════════════════════════════════════════════════════
# PARTE A — El alpha de los cinco
# ═══════════════════════════════════════════════════════════════════════════

# Sustituye estas etiquetas por las de TU equipo. Una fila por pregunta, una
# columna por integrante. Estas son las del equipo de ejemplo de la lámina,
# ronda 1: la que se etiquetó sin rúbrica.

ronda1 <- tribble(
  ~pregunta, ~a1,       ~a2,       ~a3,       ~a4,       ~a5,
  "P01",     "afin",    "afin",    "afin",    "neutral", "afin",
  "P02",     "afin",    "neutral", "afin",    "neutral", "afin",
  "P03",     "afin",    "afin",    "neutral", "afin",    "afin",
  "P04",     "afin",    "afin",    "afin",    "neutral", "afin",
  "P05",     "neutral", "afin",    "neutral", "afin",    "neutral",
  "P06",     "critica", "critica", "critica", "critica", "critica",
  "P07",     "critica", "critica", "critica", "critica", "neutral",
  "P08",     "critica", "critica", "critica", "neutral", "critica",
  "P09",     "critica", "critica", "neutral", "critica", "afin",
  "P10",     "critica", "critica", "critica", "critica", "critica"
)

# Ronda 2: los mismos cinco, las mismas preguntas, después de escribir la
# rúbrica. Lo único que cambió es que la regla quedó por escrito.

ronda2 <- tribble(
  ~pregunta, ~a1,       ~a2,       ~a3,       ~a4,       ~a5,
  "P01",     "afin",    "afin",    "afin",    "afin",    "afin",
  "P02",     "afin",    "afin",    "neutral", "afin",    "afin",
  "P03",     "afin",    "afin",    "afin",    "afin",    "afin",
  "P04",     "afin",    "afin",    "afin",    "afin",    "afin",
  "P05",     "afin",    "neutral", "afin",    "afin",    "neutral",
  "P06",     "critica", "critica", "critica", "critica", "critica",
  "P07",     "critica", "critica", "critica", "critica", "critica",
  "P08",     "critica", "critica", "critica", "neutral", "critica",
  "P09",     "critica", "critica", "critica", "critica", "afin",
  "P10",     "critica", "critica", "critica", "critica", "critica"
)


# De la tabla ancha (una columna por anotador) al formato largo. Los NA se caen
# aquí: si alguien no evaluó una pregunta, simplemente no hay fila. El alpha
# aguanta eso sin despeinarse, que es medio chiste de usarlo.
juicios <- function(tabla) {
  tabla |>
    pivot_longer(-pregunta, names_to = "anotador", values_to = "etiqueta") |>
    filter(!is.na(etiqueta))
}

# La misma fórmula corta que hiciste a mano, ahora como tubería.
#   Do = (1/n) * suma_u [ 1/(m_u - 1) * suma_c n_uc (m_u - n_uc) ]
#   De = 1/(n(n-1)) * suma_c n_c (n - n_c)
# `count()` hace el paso 1 (los conteos por unidad) y el paso 4 (los
# marginales): es literalmente el mismo verbo dos veces, con distinto agrupado.
alpha_nominal <- function(d) {
  por_unidad <- d |>
    count(pregunta, etiqueta, name = "n_uc") |>
    group_by(pregunta) |>
    summarise(
      m          = sum(n_uc),
      desacuerdo = sum(n_uc * (m - n_uc)) / (m - 1),
      .groups    = "drop"
    ) |>
    filter(m >= 2)                     # una unidad con un solo juicio no aporta

  n  <- sum(por_unidad$m)
  Do <- sum(por_unidad$desacuerdo) / n

  De <- d |>
    semi_join(por_unidad, by = "pregunta") |>
    count(etiqueta, name = "n_c") |>
    summarise(De = sum(n_c * (n - n_c)) / (n * (n - 1))) |>
    pull(De)

  1 - Do / De
}

# El acuerdo crudo: el porcentaje de pares que coinciden. Es la cifra que se
# ve bien y no significa nada, y por eso se calcula aquí al lado.
acuerdo_crudo <- function(d) {
  d |>
    count(pregunta, etiqueta, name = "n_uc") |>
    group_by(pregunta) |>
    summarise(
      iguales = sum(choose(n_uc, 2)),
      pares   = choose(sum(n_uc), 2),
      .groups = "drop"
    ) |>
    summarise(acuerdo = sum(iguales) / sum(pares)) |>
    pull(acuerdo)
}

j1 <- juicios(ronda1)
j2 <- juicios(ronda2)

tibble(ronda = c("ronda 1 — sin rúbrica", "ronda 2 — con rúbrica"),
       d     = list(j1, j2)) |>
  mutate(acuerdo_crudo = map_dbl(d, acuerdo_crudo),
         alpha         = map_dbl(d, alpha_nominal)) |>
  select(-d)

# Dónde está el desacuerdo, que es más útil que el número solo: qué pares de
# categorías se confunden entre sí. Si casi todo el desacuerdo cae en una sola
# celda, ya sabes qué párrafo de la rúbrica hay que reescribir.
desacuerdos <- function(d) {
  d |>
    count(pregunta, etiqueta, name = "votos") |>
    group_by(pregunta) |>
    filter(n() > 1) |>
    summarise(reparto = str_c(etiqueta, votos, sep = ":", collapse = "  "),
              .groups = "drop")
}

desacuerdos(j1)


# ═══════════════════════════════════════════════════════════════════════════
# PARTE B — Las mismas 10 preguntas, ahora con Jev
#
# OJO: esta parte sí hace llamadas al modelo. Son 10, una por pregunta.
# ═══════════════════════════════════════════════════════════════════════════

library(JevR)

preguntas <- tribble(
  ~pregunta, ~texto,
  "P01", "Presidenta, la felicito por la reducción de homicidios, ¿nos puede explicar cómo lo lograron?",
  "P02", "¿Qué opina de que el PAN haya votado en contra de la reforma que beneficia a los adultos mayores?",
  "P03", "Presidenta, ¿cuánto daño dejó el periodo neoliberal en el sistema de salud que ustedes están reconstruyendo?",
  "P04", "El PRIAN sigue defendiendo los privilegios fiscales de siempre, ¿usted cómo lo ve?",
  "P05", "Mucha gente todavía no conoce el programa de becas, ¿nos puede contar a detalle en qué consiste?",
  "P06", "Presidenta, los homicidios en Guanajuato no han bajado, ¿por qué su estrategia no ha funcionado ahí?",
  "P07", "¿Por qué su gobierno no ha investigado las denuncias de huachicol contra López Beltrán?",
  "P08", "El hospital del IMSS-Bienestar lleva ocho meses sin medicamentos, ¿no contradice esto lo que usted dijo aquí?",
  "P09", "Morena postuló a un candidato con denuncias por violencia familiar, ¿no le parece una contradicción?",
  "P10", "Usted dijo que no habría militarización, pero el Ejército ya controla puertos y aduanas, ¿cómo lo explica?"
)

# Los criterios son los de `script_prueba.R`, con el candado de Morena puesto.
# Importante para el ejercicio: la rúbrica que escribiste en la ronda 2 y estos
# criterios deberían decir LO MISMO. Si no dicen lo mismo, el desacuerdo entre
# Jev y tu equipo no mide nada —estarían contestando preguntas distintas.

questions <- list(
  afin = jev_noul(
    "¿Esta pregunta de un periodista favorece al gobierno de México?",
    yes = "Elogia al gobierno o a la presidenta, o le pega a un rival suyo: PAN, PRI, PRIAN, Movimiento Ciudadano o el periodo neoliberal.",
    no  = "Critica al gobierno, o solo pide un dato sin afirmar nada. Criticar a Morena es criticar al gobierno, no a un rival."
  ),
  postura = jev_choice(
    "¿Hacia dónde carga esta pregunta?",
    c("critica" = "Da por sentado algo malo del gobierno: un fracaso, una omisión, una contradicción",
      "afin"    = "Da por sentado algo bueno del gobierno, o algo malo de un rival suyo",
      "neutral" = "No da nada por sentado: pide un dato, una opinión o una explicación")
  )
)

jev_salida <- preguntas |>
  mutate(res = map(texto, \(t) jev_tidy(jev(t, questions)))) |>
  unnest(res) |>
  select(pregunta, jev = postura, jev_confianza = postura_confidence, jev_p_afin = afin)

jev_salida

# Una sola tabla con todo alineado por pregunta: los cinco humanos y Jev.
# De aquí en adelante, "comparar a X contra Y" es escoger dos columnas.
todo <- ronda2 |>
  left_join(select(jev_salida, pregunta, jev), by = "pregunta")


# ═══════════════════════════════════════════════════════════════════════════
# PARTE C — Las dos lecturas
# ═══════════════════════════════════════════════════════════════════════════

# --- Lectura 1: Jev como sexto anotador -------------------------------------
# Para meterlo en el alpha hay que quedarse con su etiqueta discreta y tirar la
# confianza. Es una decisión, no un detalle técnico: estás tratando "afin con
# confianza 0.51" igual que "afin con confianza 0.99".
#
# Fíjate que no hay que tocar `alpha_nominal`: en formato largo, meter un sexto
# anotador es agregar 10 filas más.

tibble(quienes = c("solo los 5 humanos", "con Jev de sexto"),
       d       = list(j2, juicios(todo))) |>
  mutate(alpha = map_dbl(d, alpha_nominal)) |>
  select(-d)

# Si el alpha baja, Jev discrepa del equipo. Eso NO dice quién tiene razón:
# dice que el criterio del equipo y el criterio escrito en `questions` no son
# el mismo criterio. Revisa primero las preguntas donde discrepan.


# --- Lectura 2: la perspectivista -------------------------------------------
# No colapsar. La proporción de humanos que dijo "afin" y la p(afin) de Jev son
# la misma clase de objeto: una distribución sobre la etiqueta, no una etiqueta.
# Se pueden comparar directamente, sin que nadie tenga que ganar.

comparacion <- j2 |>
  group_by(pregunta) |>
  summarise(humanos_p_afin = mean(etiqueta == "afin"), .groups = "drop") |>
  left_join(jev_salida, by = "pregunta") |>
  mutate(brecha       = jev_p_afin - humanos_p_afin,
         se_partieron = humanos_p_afin > 0 & humanos_p_afin < 1)

comparacion |> arrange(desc(abs(brecha))) |> print(n = Inf)

# El número bonito y el número útil, uno al lado del otro. La correlación sube
# sola porque la mayoría de las preguntas son unánimes: lo que informa es la
# brecha SOLO en las que el equipo se partió.
comparacion |>
  summarise(r = cor(humanos_p_afin, jev_p_afin))

comparacion |>
  group_by(se_partieron) |>
  summarise(n = n(), brecha_media = mean(abs(brecha)), .groups = "drop")

# Ojo con el caso simétrico: donde los cinco humanos se partieron 3-2, Jev
# debería salir cerca de 0.5. Si sale en 0.95, no está captando la ambigüedad
# que el equipo sí vio — y esas son justo las que ibas a revisar a mano.


# ═══════════════════════════════════════════════════════════════════════════
# PARTE D — Kappa de Cohen: una persona fija contra otra, y contra Jev
#
# Cohen solo admite DOS jueces, así que aquí no hay "el equipo": hay parejas.
# Eso la vuelve la herramienta natural para "un humano contra el modelo", que
# son exactamente dos. Se usa la ronda 2 porque es la que tiene la rúbrica
# escrita, y la rúbrica es lo que `questions` traduce a criterios de Jev.
# ═══════════════════════════════════════════════════════════════════════════

# Po = la proporción de ítems donde los dos pusieron lo mismo.
# Pe = suma de p_a(c) * p_b(c) sobre las categorías. Cada juez conserva SUS
#      proporciones: ahí está la diferencia con el alpha, que echa todas las
#      etiquetas en una sola bolsa.
# El inner_join se come las categorías que solo usó uno de los dos, y está
# bien: su término vale 0 porque la proporción del otro es 0.
kappa_cohen <- function(a, b) {
  d  <- tibble(a = a, b = b) |> filter(!is.na(a), !is.na(b))
  n  <- nrow(d)
  Po <- mean(d$a == d$b)
  Pe <- inner_join(count(d, etiqueta = a, name = "n_a"),
                   count(d, etiqueta = b, name = "n_b"),
                   by = "etiqueta") |>
    summarise(Pe = sum(n_a * n_b) / n^2) |>
    pull(Pe)
  c(Po = Po, Pe = Pe, kappa = (Po - Pe) / (1 - Pe), n = n)
}

# La tabla cruzada, que es de donde salen los dos números. Vale la pena verla:
# las celdas fuera de la diagonal dicen QUÉ se confunde con qué, y eso es lo
# accionable. El kappa solo dice cuánto.
cruce <- function(a, b) {
  tibble(a = a, b = b) |>
    count(a, b) |>
    pivot_wider(names_from = b, values_from = n, values_fill = 0)
}

# --- D.1 Persona fija contra persona fija ------------------------------------

kappa_cohen(ronda2$a1, ronda2$a2)
cruce(ronda2$a1, ronda2$a2)

# Las 10 parejas de un jalón.
expand_grid(i = 1:5, j = 1:5) |>
  filter(i < j) |>
  mutate(res = map2(i, j, \(x, y)
                    as_tibble_row(kappa_cohen(ronda2[[str_c("a", x)]],
                                              ronda2[[str_c("a", y)]])))) |>
  unnest(res) |>
  transmute(pareja = str_c("A", i, "-A", j), Po, Pe, kappa) |>
  arrange(desc(kappa))

# --- D.2 Persona fija contra Jev ---------------------------------------------
# Requiere haber corrido la PARTE B. Jev entra con su etiqueta discreta: la
# confianza se pierde aquí, y es una decisión, no un detalle.

kappa_cohen(todo$a1, todo$jev)
cruce(todo$a1, todo$jev)

# --- D.3 Los cinco contra Jev, con su baseline --------------------------------
# El baseline NO es 1.0 ni "lo que saquen dos humanos cualesquiera": es lo que
# saca esa misma persona contra la mayoría de los OTROS cuatro. Comparar a Jev
# contra la mayoría de los cinco lo mediría contra un blanco más suave.
#
# OJO con los empates: con cuatro votantes un 2-2 no tiene mayoría. Devolvemos
# NA y `kappa_cohen` excluye esos ítems (por eso reporta su propio `n`). En la
# ronda 2 pasa en P05 para A1, A3 y A4.
mayoria_sin <- function(tabla, i) {
  tabla |>
    select(!all_of(str_c("a", i))) |>
    juicios() |>
    count(pregunta, etiqueta, name = "votos") |>
    group_by(pregunta) |>
    arrange(desc(votos), .by_group = TRUE) |>
    summarise(
      mayoria = if (n() > 1 && votos[1] == votos[2]) NA_character_ else first(etiqueta),
      .groups = "drop"
    )
}

map_dfr(1:5, \(i) {
  d <- todo |>
    select(pregunta, humano = all_of(str_c("a", i)), jev) |>
    left_join(mayoria_sin(ronda2, i), by = "pregunta")

  kj <- kappa_cohen(d$humano, d$jev)
  kb <- kappa_cohen(d$humano, d$mayoria)

  tibble(anotador        = str_c("A", i),
         acuerdo_jev     = kj[["Po"]],
         Pe_jev          = kj[["Pe"]],
         kappa_jev       = kj[["kappa"]],
         baseline_humano = kb[["kappa"]],
         n_baseline      = kb[["n"]],
         brecha          = kj[["kappa"]] - kb[["kappa"]])
})

# Cómo se lee la última columna: negativa quiere decir que Jev se parece a esa
# persona MENOS de lo que se le parecen sus propios compañeros. Si sale
# negativa para los cinco, el criterio de `questions` y el de la rúbrica no son
# el mismo criterio — revisa los textos de yes/no antes de culpar al modelo.
