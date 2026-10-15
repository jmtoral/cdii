# Funciones que usa más de un archivo del proyecto. Se cargan con
#   source(here("R", "funciones.R"))
# Si una función la usa un solo script, vive en ese script, no aquí.


# Algunas reseñas vienen con doble codificación: "CancÃºn" en vez de "Cancún".
# Alguien leyó UTF-8 como si fuera latin1 y lo volvió a guardar como UTF-8.
# Se deshace al revés: UTF-8 -> latin1 devuelve los bytes originales, y esos
# bytes ya son UTF-8 válido. Si el texto trae algo que no cabe en latin1 (un
# emoji, por ejemplo), iconv devuelve NA y se queda el original.
arreglar_mojibake <- function(x) {
  arreglado <- x |>
    iconv(from = "UTF-8", to = "latin1") |>
    iconv(from = "UTF-8", to = "UTF-8")
  if_else(str_detect(x, "Ã|Â"), coalesce(arreglado, x), x)
}


# Una fila por palabra: minúsculas y solo letras (los acentos y la ñ cuentan
# como letras). La usan el EDA, para ver qué palabras separan las reseñas
# buenas de las malas, y el modelo, para armar sus variables.
tokenizar <- function(d, texto = resena) {
  d |>
    mutate(palabra = str_extract_all(str_to_lower({{ texto }}), "[[:alpha:]]+")) |>
    select(-{{ texto }}) |>
    unnest_longer(palabra)
}


# Las n palabras que más separan reseñas satisfechas de insatisfechas, por la
# razón de momios en logaritmo. Recibe SOLO datos de entrenamiento: si las
# escogiera viendo la prueba, la calificación del modelo saldría inflada.
# Las palabras raras (menos de `minimo` reseñas) separan perfecto por
# casualidad y no generalizan, así que se descartan.
elegir_vocabulario <- function(entrenamiento, n = 60, minimo = 200) {
  entrenamiento |>
    select(id, satisfecho, resena) |>
    tokenizar() |>
    distinct(id, satisfecho, palabra) |>
    count(satisfecho, palabra) |>
    pivot_wider(names_from = satisfecho, values_from = n, values_fill = 0) |>
    filter(si + no >= minimo) |>
    mutate(log_razon = log((no + 1) / sum(no)) - log((si + 1) / sum(si))) |>
    slice_max(abs(log_razon), n = n) |>
    pull(palabra)
}


# Cambia el texto por una columna w_<palabra> por cada palabra del
# vocabulario: 1 si la reseña la trae, 0 si no.
con_palabras <- function(d, vocabulario) {
  presentes <- d |>
    select(id, resena) |>
    tokenizar() |>
    filter(palabra %in% vocabulario) |>
    distinct(id, palabra) |>
    mutate(palabra = factor(palabra, levels = vocabulario), v = 1L) |>
    pivot_wider(names_from = palabra, values_from = v, values_fill = 0L,
                names_prefix = "w_", names_expand = TRUE)

  d |>
    select(-resena) |>
    left_join(presentes, by = "id") |>
    mutate(across(starts_with("w_"), \(x) replace_na(x, 0L)))
}


# La prueba más chica posible: si alguien rompe estas funciones, el
# source() falla en vez de dejar pasar datos mal.
stopifnot(
  arreglar_mojibake("CancÃºn") == "Cancún",
  arreglar_mojibake("Cancún") == "Cancún",
  tokenizar(tibble(id = 1, resena = "¡Muy BUENA comida!")) |> pull(palabra) |>
    identical(c("muy", "buena", "comida"))
)
