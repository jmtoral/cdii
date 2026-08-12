"""
Descarga el dataset Measuring Hate Speech de UC Berkeley D-Lab desde HuggingFace.

Uso:
    python data/download_data.py              # Descarga completo
    python data/download_data.py --sample 5000 # Solo 5000 filas (para pruebas/WASM)

El dataset se guarda en formato Parquet en data/hate_speech.parquet
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Descarga el dataset Measuring Hate Speech de HuggingFace"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Número de filas a descargar (None = todas, ~135k filas)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directorio de salida (default: data/ en la raíz del proyecto)",
    )
    args = parser.parse_args()

    # Determinar directorio de salida
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).parent

    output_dir.mkdir(parents=True, exist_ok=True)

    print("📥 Descargando dataset 'ucberkeley-dlab/measuring-hate-speech'...")
    print("   (esto puede tomar unos minutos la primera vez)\n")

    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ Error: necesitas instalar la librería 'datasets'")
        print("   Ejecuta: pip install datasets")
        sys.exit(1)

    # Cargar dataset desde HuggingFace
    dataset = load_dataset(
        "ucberkeley-dlab/measuring-hate-speech",
        split="train",
    )

    print(f"✅ Dataset cargado: {len(dataset):,} filas, {len(dataset.column_names)} columnas\n")

    # Convertir a Polars para manipular
    try:
        import polars as pl
    except ImportError:
        print("❌ Error: necesitas instalar 'polars'")
        print("   Ejecuta: pip install polars")
        sys.exit(1)

    df = pl.from_arrow(dataset.data.table)

    # Guardar dataset completo
    full_path = output_dir / "hate_speech.parquet"
    df.write_parquet(full_path)
    size_mb = full_path.stat().st_size / (1024 * 1024)
    print(f"💾 Dataset completo guardado: {full_path} ({size_mb:.1f} MB)")

    # Una sola escritura de sample_data.parquet.
    # Antes había dos: el bloque `if args.sample` escribía el archivo y justo después
    # otro bloque lo pisaba incondicionalmente con 5,000 filas. Resultado: `--sample 20000`
    # producía 5,000 filas en silencio.
    n_muestra = min(args.sample or 5000, len(df))
    sample_df = df.sample(n=n_muestra, seed=42)
    sample_path = output_dir / "sample_data.parquet"
    sample_df.write_parquet(sample_path)
    size_kb = sample_path.stat().st_size / 1024
    print(f"💾 Muestra guardada: {sample_path} ({n_muestra:,} filas, {size_kb:.0f} KB)")

    # ⚠️ El archivo que se sirve al navegador es 01_sql/public/sample_data.parquet,
    # NO este. Hay que copiarlo a mano o el sitio seguirá publicando la muestra vieja.
    destino_web = Path(__file__).resolve().parents[1] / "01_sql" / "public"
    if destino_web.is_dir():
        import shutil

        shutil.copy2(sample_path, destino_web / "sample_data.parquet")
        print(f"💾 Copiado a {destino_web / 'sample_data.parquet'} (es el que se publica)")
    else:
        print(f"⚠️  No encontré {destino_web}: copia el parquet a mano antes de publicar.")

    # ⚠️ ADVERTENCIA sobre el muestreo, importante para los ejercicios:
    # esto muestrea FILAS, pero el grano del dataset es la ANOTACIÓN (cada comentario
    # fue evaluado por varias personas). Muestrear filas rompe esa estructura: con
    # n=5000 el máximo de anotaciones por anotador queda en 5, así que cualquier
    # ejercicio de HAVING sobre conteos por anotador devuelve CERO filas.
    # Al regenerar los datos hay que revisar estos números y revalidar los ejercicios.
    print("\n📊 Distribución de anotaciones (de esto dependen los ejercicios de HAVING):")
    por_anotador = sample_df.group_by("annotator_id").len()["len"]
    por_comentario = sample_df.group_by("comment_id").len()["len"]
    for etiqueta, serie in [("por anotador", por_anotador), ("por comentario", por_comentario)]:
        print(f"   {etiqueta}: máx={serie.max()}, media={serie.mean():.1f}")
        for corte in (3, 5, 10, 20, 50):
            print(f"      con más de {corte:>2}: {(serie > corte).sum():,}")

    print("\n✅ ¡Listo! Los datos están en el directorio data/")
    print("\nPara usar en Marimo:")
    print("  marimo edit 01_sql/01_introduccion_sql.py")


if __name__ == "__main__":
    main()
