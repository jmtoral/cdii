# 01 · Descargar los datos crudos
#
# Entra:  nada (internet)
# Sale:   data/raw/Rest-Mex_2025_train.csv y data/raw/Readme.txt
#
# Lo que hay en data/raw/ se queda tal como llegó. Nadie lo abre en Excel,
# nadie lo "corrige" a mano. Si hay que arreglar algo, se arregla en
# 02_limpiar.R, donde queda escrito.

library(tidyverse)
library(here)

ID_DRIVE <- "1xf0nGF29hFWBg_rXSJoFGcq86T9ekit8"
zip <- here("data", "raw", "Rest-Mex_2025_train.zip")
csv <- here("data", "raw", "Rest-Mex_2025_train.csv")

# Si ya está, no se vuelve a bajar: son 30 MB.
if (!file.exists(csv)) {
  options(timeout = 600)
  # confirm=t se salta el aviso de "archivo muy grande para revisar virus"
  url <- str_glue("https://drive.usercontent.google.com/download?id={ID_DRIVE}&export=download&confirm=t")
  download.file(url, zip, mode = "wb")
  unzip(zip, exdir = here("data", "raw"))
  invisible(file.remove(zip))
}

stopifnot(file.exists(csv))
message("Datos crudos en ", csv)
