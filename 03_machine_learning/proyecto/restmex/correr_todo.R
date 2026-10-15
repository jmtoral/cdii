# Reproduce el proyecto de cero: de internet a outputs/.
# Ábrelo con el proyecto abierto (restmex.Rproj) y dale Source.
#
# Cada script corre en su propio ambiente, como si fuera una sesión nueva:
# así nadie depende por accidente de una variable que dejó el anterior.

library(here)

scripts <- c("01_descargar.R", "02_limpiar.R", "03_modelo.R")
purrr::walk(scripts, \(s) source(here("scripts", s), local = new.env()))

message("Listo. Ahora dale Render a notebooks/01_eda.qmd, notebooks/02_modelo.qmd y reports/reporte.qmd.")
