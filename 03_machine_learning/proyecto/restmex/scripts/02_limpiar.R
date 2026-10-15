# 02 · Limpiar
#
# Entra:  data/raw/Rest-Mex_2025_train.csv
# Sale:   data/processed/resenas.rds
#
# Todas las decisiones sobre los datos se toman aquí y quedan escritas.
# El EDA, el modelo y el reporte leen el .rds, nunca el CSV crudo.

library(tidyverse)
library(here)
source(here("R", "funciones.R"))

crudo <- read_csv(here("data", "raw", "Rest-Mex_2025_train.csv"),
                  col_types = cols(.default = "c"))

resenas <- crudo |>
  # Nombres en español y en minúsculas, para no andar adivinando mayúsculas
  rename(titulo = Title, resena = Review, polaridad = Polarity,
         pueblo = Town, estado = Region, tipo = Type) |>
  mutate(
    id        = row_number(),
    polaridad = as.integer(as.numeric(polaridad)),   # viene como "5.0"
    tipo      = case_when(tipo == "Hotel"      ~ "hotel",
                          tipo == "Restaurant" ~ "restaurante",
                          tipo == "Attractive" ~ "atractivo"),
    across(c(titulo, resena), arreglar_mojibake),
    across(c(pueblo, estado), \(x) str_replace_all(x, "_", " ")),   # "Isla_Mujeres"
    n_palabras = str_count(resena, "\\S+"),
    # La variable respuesta. Cortar en 4 se decidió en el EDA; se escribe aquí
    # una sola vez para que el notebook, el modelo y el reporte usen la misma.
    satisfecho = factor(if_else(polaridad >= 4, "si", "no"), levels = c("no", "si"))
  ) |>
  relocate(id)

# Lo que se arregló o se tiró, para que quede en la consola y no sea un secreto
message("Filas leídas:          ", nrow(crudo))
message("Reseñas con mojibake:  ", sum(str_detect(crudo |> pull(Review), "Ã|Â"), na.rm = TRUE))
message("Reseñas sin texto:     ", sum(is.na(resenas |> pull(resena))))
message("Reseñas duplicadas:    ", nrow(resenas) - nrow(distinct(resenas, resena, pueblo)))

resenas <- resenas |>
  filter(!is.na(resena), !is.na(polaridad)) |>
  distinct(resena, pueblo, .keep_all = TRUE)

message("Filas que quedan:      ", nrow(resenas))

write_rds(resenas, here("data", "processed", "resenas.rds"), compress = "gz")
