"""
Proceso ETL - Python 3.11
-----------------------------------
Flujo:
1.  Lee empleados desde PostgreSQL
2.  Realizamos limpieza de la data
3.  Exporta a Excel

"""
from pathlib import Path             # Manipulación de rutas
import json, os
import psycopg2
import pandas as pd
from typing import Union

# -------------- 1. Cargar Config -------------- #
def load_config(path: Union[str, Path, None] = None) -> dict:
    path = Path(path) if path else Path(__file__).with_name("config.json")
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} no encontrado.")
    return json.loads(path.read_text(encoding="utf-8"))

CFG       = load_config(os.getenv("CONFIG_FILE"))
DB_CFG    = CFG["db"]

# ─────────────────────────── 2. Script principal  ──────────────────────────── #
def main() -> None:
    # 3.2  Si no hay CSV para el mes, abortar sin error

    # 3.4  Leer tabla «rrhh.empleado» desde PostgreSQL
    with psycopg2.connect(**DB_CFG) as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM rrhh.empleado;")
        db_df = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
        
    db_df["mnt_tope_comision"] = db_df["mnt_tope_comision"].fillna(0)
    df_str = db_df.astype(str)
    
    output_dir = "data/output"
    output_file = os.path.join(output_dir, "empleados_limpios.csv")

    os.makedirs(output_dir, exist_ok=True)
    df_str.to_csv(output_file, index=False)

    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"Archivo creado exitosamente: {output_file} ({file_size} bytes)")
    else:
        print("Error: El archivo no se creó correctamente")

if __name__ == "__main__":
    main()
