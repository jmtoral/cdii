# 03 · Modelo final
#
# Entra:  data/processed/resenas.rds
# Sale:   outputs/modelo.rds              el workflow ajustado, para predecir reseñas nuevas
#         outputs/predicciones_prueba.rds lo que el reporte necesita para evaluar
#         outputs/coeficientes.csv        qué pesa en el modelo
#
# La comparación de modelos vive en notebooks/02_modelo.qmd. Ahí ganó la
# regresión logística con palabras; este script solo entrena a la ganadora y
# guarda lo que el reporte va a leer. El notebook decide, el script ejecuta.

library(tidyverse)
library(tidymodels)
library(here)
source(here("R", "funciones.R"))

# Misma muestra y misma partición que el notebook: misma semilla, mismo código.
set.seed(2025)
datos <- read_rds(here("data", "processed", "resenas.rds")) |>
  slice_sample(n = 40000) |>
  select(id, satisfecho, tipo, n_palabras, resena)

particion     <- initial_split(datos, prop = 0.8, strata = satisfecho)
entrenamiento <- training(particion)
prueba        <- testing(particion)

vocabulario     <- elegir_vocabulario(entrenamiento)
X_entrenamiento <- con_palabras(entrenamiento, vocabulario)
X_prueba        <- con_palabras(prueba, vocabulario)

receta <- recipe(satisfecho ~ ., data = X_entrenamiento) |>
  update_role(id, new_role = "id") |>
  step_log(n_palabras, offset = 1) |>
  step_dummy(tipo) |>
  step_zv(all_predictors())

ajuste <- workflow(receta, logistic_reg()) |> fit(X_entrenamiento)

predicciones <- augment(ajuste, X_prueba) |>
  select(id, satisfecho, .pred_class, .pred_no, .pred_si)

# "no" es el primer nivel, así que es el evento: sensibilidad = qué fracción de
# las quejas detecta.
predicciones |>
  metric_set(accuracy, kap, roc_auc, sens, spec)(truth = satisfecho, estimate = .pred_class, .pred_no) |>
  print()

write_rds(ajuste,       here("outputs", "modelo.rds"), compress = "gz")
write_rds(predicciones, here("outputs", "predicciones_prueba.rds"))
tidy(ajuste) |> write_csv(here("outputs", "coeficientes.csv"))

message("Modelo y predicciones en outputs/")
