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
# Requisitos: tidyverse y JevR. No hace falta `irr`: el alpha nominal son diez
# líneas y conviene verlas, porque son exactamente las que hiciste a mano.
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


# La misma fórmula corta que hiciste a mano, sin más.
#   Do = (1/n) * suma_u [ 1/(m_u - 1) * suma_c n_uc (m_u - n_uc) ]
#   De = 1/(n(n-1)) * suma_c n_c (n - n_c)
# `unidades` es una lista: un vector de etiquetas por pregunta. Se permite que
# unas preguntas tengan más juicios que otras —ese es medio chiste del alpha—
# así que m_u se calcula por unidad y no se asume que todas midan igual.

alpha_nominal <- function(unidades) {
  unidades <- Filter(\(u) length(u) >= 2, lapply(unidades, \(u) u[!is.na(u)]))
  n  <- sum(lengths(unidades))
  Do <- sum(sapply(unidades, \(u) {
    m <- length(u); k <- table(u)
    sum(k * (m - k)) / (m - 1)
  })) / n
  nc <- table(unlist(unidades))
  De <- sum(nc * (n - nc)) / (n * (n - 1))
  1 - Do / De
}

# De la tabla ancha (una columna por anotador) a la lista de unidades.
como_unidades <- function(tabla) {
  m <- as.matrix(select(tabla, -pregunta))
  split(m, row(m))
}

# El acuerdo crudo: el porcentaje de pares que coinciden. Es la cifra que se
# ve bien y no significa nada, y por eso se calcula aquí al lado.
acuerdo_crudo <- function(unidades) {
  pares   <- sum(sapply(unidades, \(u) choose(length(u), 2)))
  iguales <- sum(sapply(unidades, \(u) sum(choose(table(u), 2))))
  iguales / pares
}

u1 <- como_unidades(ronda1)
u2 <- como_unidades(ronda2)

cat(sprintf("Ronda 1  acuerdo crudo = %.0f%%   alpha = %.3f\n",
            100 * acuerdo_crudo(u1), alpha_nominal(u1)))
cat(sprintf("Ronda 2  acuerdo crudo = %.0f%%   alpha = %.3f\n",
            100 * acuerdo_crudo(u2), alpha_nominal(u2)))

# Dónde está el desacuerdo, que es más útil que el número solo: qué pares de
# categorías se confunden entre sí. Si casi todo el desacuerdo cae en una sola
# celda, ya sabes qué párrafo de la rúbrica hay que reescribir.
desacuerdos <- function(tabla) {
  tabla |>
    pivot_longer(-pregunta, names_to = "anotador", values_to = "etiqueta") |>
    count(pregunta, etiqueta) |>
    group_by(pregunta) |>
    filter(n() > 1) |>
    summarise(reparto = paste(etiqueta, n, sep = ":", collapse = "  "), .groups = "drop")
}

desacuerdos(ronda1)


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
  select(pregunta, jev_postura = postura, jev_confianza = postura_confidence, jev_p_afin = afin)

jev_salida


# ═══════════════════════════════════════════════════════════════════════════
# PARTE C — Las dos lecturas
# ═══════════════════════════════════════════════════════════════════════════

# --- Lectura 1: Jev como sexto anotador -------------------------------------
# Para meterlo en el alpha hay que quedarse con su etiqueta discreta y tirar la
# confianza. Es una decisión, no un detalle técnico: estás tratando "afin con
# confianza 0.51" igual que "afin con confianza 0.99".

u_con_jev <- ronda2 |>
  left_join(jev_salida, by = "pregunta") |>
  select(pregunta, a1:a5, jev = jev_postura) |>
  como_unidades()

cat(sprintf("\nSolo los 5 humanos:  alpha = %.3f\n", alpha_nominal(u2)))
cat(sprintf("Con Jev de sexto:    alpha = %.3f\n", alpha_nominal(u_con_jev)))

# Si el alpha baja, Jev discrepa del equipo. Eso NO dice quién tiene razón:
# dice que el criterio del equipo y el criterio escrito en `questions` no son
# el mismo criterio. Revisa primero las preguntas donde discrepan.


# --- Lectura 2: la perspectivista -------------------------------------------
# No colapsar. La proporción de humanos que dijo "afin" y la p(afin) de Jev son
# la misma clase de objeto: una distribución sobre la etiqueta, no una etiqueta.
# Se pueden comparar directamente, sin que nadie tenga que ganar.

comparacion <- ronda2 |>
  pivot_longer(-pregunta, names_to = "anotador", values_to = "etiqueta") |>
  group_by(pregunta) |>
  summarise(humanos_p_afin = mean(etiqueta == "afin"), .groups = "drop") |>
  left_join(jev_salida, by = "pregunta") |>
  mutate(brecha = jev_p_afin - humanos_p_afin)

comparacion |> arrange(desc(abs(brecha))) |> print(n = Inf)

cat(sprintf("\nCorrelación humanos vs Jev: %.3f\n",
            cor(comparacion$humanos_p_afin, comparacion$jev_p_afin)))

# Las preguntas con la brecha más grande son el material del reporte. En cada
# una, la pregunta no es "¿quién se equivocó?" sino "¿qué está viendo cada uno
# que el otro no?". Y ojo con el caso simétrico: donde los cinco humanos se
# partieron 3-2, Jev debería salir cerca de 0.5. Si sale en 0.95, no está
# captando la ambigüedad que el equipo sí vio.


# ═══════════════════════════════════════════════════════════════════════════
# PARTE D — Kappa de Cohen: una persona fija contra otra, y contra Jev
#
# Cohen solo admite DOS jueces, así que aquí no hay "el equipo": hay parejas.
# Eso la vuelve la herramienta natural para "un humano contra el modelo", que
# son exactamente dos. Se usa la ronda 2 porque es la que tiene la rúbrica
# escrita, y la rúbrica es lo que `questions` traduce a criterios de Jev.
# ═══════════════════════════════════════════════════════════════════════════

CATS <- c("afin", "critica", "neutral")

# Po = la diagonal de la tabla cruzada, entre el total.
# Pe = suma de (total de fila x total de columna) / n^2, o sea la tabla bajo
#      independencia. Cada juez conserva SUS proporciones: ahí está la
#      diferencia con el alpha, que echa todas las etiquetas en una bolsa.
kappa_cohen <- function(a, b) {
  tab <- table(factor(a, levels = CATS), factor(b, levels = CATS))
  n  <- sum(tab)
  Po <- sum(diag(tab)) / n
  Pe <- sum(rowSums(tab) * colSums(tab)) / n^2
  c(Po = Po, Pe = Pe, kappa = (Po - Pe) / (1 - Pe))
}

# --- D.1 Persona fija contra persona fija ------------------------------------

kappa_cohen(ronda2$a1, ronda2$a2)

# La tabla cruzada, que es de donde salen los dos números. Vale la pena verla:
# las celdas fuera de la diagonal dicen QUÉ se confunde con qué, y eso es lo
# accionable. El kappa solo dice cuánto.
table(A1 = factor(ronda2$a1, levels = CATS),
      A2 = factor(ronda2$a2, levels = CATS))

# Las 10 parejas de un jalón.
combn(paste0("a", 1:5), 2, simplify = FALSE) |>
  map_dfr(\(par) {
    k <- kappa_cohen(ronda2[[par[1]]], ronda2[[par[2]]])
    tibble(pareja = paste(par, collapse = "-"), Po = k[["Po"]],
           Pe = k[["Pe"]], kappa = k[["kappa"]])
  }) |>
  arrange(desc(kappa))

# --- D.2 Persona fija contra Jev ---------------------------------------------
# Requiere haber corrido la PARTE B. Jev entra con su etiqueta discreta: la
# confianza se pierde aquí, y es una decisión, no un detalle.

jev_postura <- jev_salida$jev_postura[match(ronda2$pregunta, jev_salida$pregunta)]

kappa_cohen(ronda2$a1, jev_postura)

table(A1 = factor(ronda2$a1, levels = CATS),
      JEV = factor(jev_postura, levels = CATS))

# --- D.3 Los cinco contra Jev, con su baseline --------------------------------
# El baseline NO es 1.0 ni "lo que saquen dos humanos cualesquiera": es lo que
# saca esa misma persona contra la mayoría de los OTROS cuatro. Comparar a Jev
# contra la mayoría de los cinco lo mediría contra un blanco más suave.

# OJO con los empates: con cuatro votantes, un 2-2 no tiene mayoria, y
# which.max() la inventaria en silencio devolviendo la primera alfabeticamente.
# Aqui se devuelve NA y esos items se excluyen de la comparacion. En la ronda 2
# pasa en P05, donde A2..A5 quedan 2-2.
mayoria_sin <- function(i) {
  apply(select(ronda2, a1:a5)[, -i], 1, \(x) {
    tt <- sort(table(x), decreasing = TRUE)
    if (length(tt) > 1 && tt[1] == tt[2]) NA_character_ else names(tt)[1]
  })
}

# Kappa ignorando los items donde alguno de los dos es NA.
kappa_pareado <- function(a, b) {
  ok <- !is.na(a) & !is.na(b)
  c(kappa_cohen(a[ok], b[ok]), n = sum(ok))
}

map_dfr(1:5, \(i) {
  humano <- ronda2[[paste0("a", i)]]
  kj <- kappa_cohen(humano, jev_postura)
  kb <- kappa_pareado(humano, mayoria_sin(i))
  tibble(anotador = paste0("A", i),
         acuerdo_jev = kj[["Po"]], Pe_jev = kj[["Pe"]], kappa_jev = kj[["kappa"]],
         baseline_humano = kb[["kappa"]], n_baseline = kb[["n"]],
         brecha = kj[["kappa"]] - kb[["kappa"]])
})

# Cómo se lee la última columna: negativa quiere decir que Jev se parece a esa
# persona MENOS de lo que se le parecen sus propios compañeros. Si sale
# negativa para los cinco, el criterio de `questions` y el de la rúbrica no son
# el mismo criterio — revisa los textos de yes/no antes de culpar al modelo.
