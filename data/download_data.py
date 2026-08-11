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

    # Guardar muestra si se solicita
    if args.sample:
        sample_df = df.sample(n=min(args.sample, len(df)), seed=42)
        sample_path = output_dir / "sample_data.parquet"
        sample_df.write_parquet(sample_path)
        sample_size_mb = sample_path.stat().st_size / (1024 * 1024)
        print(f"💾 Muestra guardada: {sample_path} ({args.sample:,} filas, {sample_size_mb:.1f} MB)")

    # Siempre crear una muestra pequeña para WASM
    wasm_sample = df.sample(n=min(5000, len(df)), seed=42)
    wasm_path = output_dir / "sample_data.parquet"
    wasm_sample.write_parquet(wasm_path)
    wasm_size_kb = wasm_path.stat().st_size / 1024
    print(f"💾 Muestra WASM guardada: {wasm_path} (5,000 filas, {wasm_size_kb:.0f} KB)")

    print("\n✅ ¡Listo! Los datos están en el directorio data/")
    print("\nPara usar en Marimo:")
    print("  marimo edit 01_sql/01_introduccion_sql.py")


if __name__ == "__main__":
    main()
