# Referencias

Copias locales de las fuentes que sostienen afirmaciones concretas del material.
Están aquí para poder verificar cualquier dato sin depender de que un enlace siga vivo.

## `Sachdeva-2022-Annotator-Identity-Sensitivity-IRT-FAccT.pdf`

Sachdeva, P. S., Barreto, R., von Vacano, C. y Kennedy, C. J. (2022).
*Assessing Annotator Identity Sensitivity via Item Response Theory: A Case Study in a
Hate Speech Corpus*. FAccT '22, 1585–1603. <https://doi.org/10.1145/3531146.3533216>

Es el artículo de los mismos autores del corpus **Measuring Hate Speech** que usamos en
todas las lecciones. De aquí sale:

| Qué | Dónde en el paper | Dónde lo usamos |
|---|---|---|
| El cuestionario completo de 10 ítems, con la redacción literal | Tabla S2 | Lámina 05 de `presentaciones/04_alpha_krippendorff.html` |
| Que las escalas están orientadas hacia «más hostilidad» (por eso `respect` alto = irrespetuoso) | §3.1 | Aviso de la lámina 05, y las lecciones 1, 2 y 3 |
| Alphas de Krippendorff publicados por los autores | Tablas S3 y S4 | Lámina 07 |
| La crítica al uso automático del alpha («trata las perspectivas como ruido que hay que sofocar») | §2 | Lámina 08 |
| Que anotadores negros y blancos dan alphas *comparables* aunque el IRT sí detecte diferencias | §5 | Lámina 08 |

**Verificación independiente:** `scripts/calcular_alpha.py` calcula α = **0.672** para
`target_race` sobre todo el corpus. El paper reporta **0.672** en su Tabla S4. Coinciden,
así que nuestra implementación es correcta.
