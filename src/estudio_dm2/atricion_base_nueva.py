
"""
Preparación y verificación de la base de datos Eunomia - GiBleed.

Descarga los archivos CSV del repositorio OHDSI, los importa a SQLite
y verifica la existencia de las tablas necesarias para el análisis.
"""

from pathlib import Path
from contextlib import closing
import sqlite3
import urllib.request
import zipfile

import pandas as pd


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

DIRECTORIO_DATOS = Path("data")

DB_PATH = DIRECTORIO_DATOS / "eunomia.sqlite"
DB_TEMPORAL = DIRECTORIO_DATOS / "eunomia_temporal.sqlite"
ZIP_PATH = DIRECTORIO_DATOS / "GiBleed_5.3.zip"

URL_DATASET = (
    "https://raw.githubusercontent.com/"
    "OHDSI/EunomiaDatasets/main/"
    "datasets/GiBleed/GiBleed_5.3.zip"
)

TAMANO_BLOQUE = 100_000

TABLAS_REQUERIDAS = [
    "person",
    "observation_period",
    "condition_occurrence",
    "drug_exposure"
]


# =============================================================================
# DESCARGA DEL DATASET
# =============================================================================

def descargar_dataset():

    print("[*] Descargando dataset GiBleed desde OHDSI...")

    solicitud = urllib.request.Request(
        URL_DATASET,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(solicitud, timeout=120) as respuesta:
        ZIP_PATH.write_bytes(respuesta.read())

    if not zipfile.is_zipfile(ZIP_PATH):
        ZIP_PATH.unlink(missing_ok=True)
        raise ValueError(
            "El archivo descargado no es un ZIP válido."
        )

    print("[✓] Descarga completada.")


# =============================================================================
# IDENTIFICACIÓN DE ARCHIVOS CSV
# =============================================================================

def obtener_archivos_csv(archivo_zip):

    archivos_csv = []

    for nombre in archivo_zip.namelist():

        nombre_archivo = Path(nombre).name

        # Excluir directorios y archivos auxiliares de macOS.
        if nombre.endswith("/"):
            continue

        if nombre_archivo.startswith("._"):
            continue

        if "__MACOSX" in nombre:
            continue

        if not nombre.lower().endswith(".csv"):
            continue

        archivos_csv.append(nombre)

    if not archivos_csv:
        raise ValueError(
            "No se encontraron archivos CSV válidos en el ZIP."
        )

    return archivos_csv


# =============================================================================
# CONSTRUCCIÓN DE LA BASE DE DATOS SQLITE
# =============================================================================

def construir_base_datos():

    print("[*] Construyendo base de datos SQLite...")

    # Eliminar una construcción temporal anterior.
    DB_TEMPORAL.unlink(missing_ok=True)

    try:

        with zipfile.ZipFile(ZIP_PATH, "r") as archivo_zip:

            archivos_csv = obtener_archivos_csv(archivo_zip)

            print(
                f"[*] Archivos CSV encontrados: "
                f"{len(archivos_csv)}"
            )

            with closing(sqlite3.connect(DB_TEMPORAL)) as conn:

                for archivo_csv in archivos_csv:

                    nombre_tabla = Path(archivo_csv).stem.lower()

                    print(
                        f"[*] Cargando tabla: {nombre_tabla}"
                    )

                    with archivo_zip.open(archivo_csv) as archivo:

                        primer_bloque = True

                        try:

                            bloques = pd.read_csv(
                                archivo,
                                chunksize=TAMANO_BLOQUE,
                                encoding="utf-8-sig",
                                low_memory=False
                            )

                            for bloque in bloques:

                                bloque.to_sql(
                                    nombre_tabla,
                                    conn,
                                    if_exists=(
                                        "replace"
                                        if primer_bloque
                                        else "append"
                                    ),
                                    index=False
                                )

                                primer_bloque = False

                        except pd.errors.EmptyDataError:

                            print(
                                f"[!] Archivo vacío omitido: "
                                f"{archivo_csv}"
                            )

                conn.commit()

        # Verificar las tablas antes de sustituir la base definitiva.
        with closing(sqlite3.connect(DB_TEMPORAL)) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table'"
            )

            tablas = {
                fila[0].lower()
                for fila in cursor.fetchall()
            }

            faltantes = [
                tabla for tabla in TABLAS_REQUERIDAS
                if tabla not in tablas
            ]

            if faltantes:
                raise ValueError(
                    "Faltan tablas requeridas: "
                    + ", ".join(faltantes)
                )

        # Sustituir la base definitiva solo si la carga fue exitosa.
        DB_TEMPORAL.replace(DB_PATH)

        print("[✓] Base de datos construida correctamente.")

    except Exception:

        DB_TEMPORAL.unlink(missing_ok=True)
        raise


# =============================================================================
# ASEGURAR DISPONIBILIDAD DE LA BASE DE DATOS
# =============================================================================

def asegurar_base_datos(db_path=DB_PATH):

    if db_path.exists():

        print(
            f"[*] Base de datos encontrada en {db_path}."
        )

        with closing(sqlite3.connect(db_path)) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table'"
            )

            tablas = {
                fila[0].lower()
                for fila in cursor.fetchall()
            }

        faltantes = [
            tabla for tabla in TABLAS_REQUERIDAS
            if tabla not in tablas
        ]

        if not faltantes:
            return

        print(
            "[!] La base existente está incompleta. "
            "Se reconstruirá."
        )

        if db_path == DB_PATH:
            db_path.unlink(missing_ok=True)

    else:

        print(
            f"[*] Base de datos no encontrada en {db_path}."
        )

    DIRECTORIO_DATOS.mkdir(
        parents=True,
        exist_ok=True
    )

    descargar_dataset()

    construir_base_datos()

    # Eliminar ZIP después de construir correctamente la base.
    ZIP_PATH.unlink(missing_ok=True)


# =============================================================================
# VERIFICACIÓN DE CONEXIÓN Y TABLAS
# =============================================================================

def verificar_conexion():

    asegurar_base_datos()

    print("\n" + "=" * 65)
    print("VERIFICACIÓN DE BASE DE DATOS EUNOMIA")
    print("=" * 65)

    with closing(sqlite3.connect(DB_PATH)) as conn:

        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' "
            "ORDER BY name"
        )

        tablas = [
            fila[0]
            for fila in cursor.fetchall()
        ]

        print(f"\nTotal de tablas: {len(tablas)}")

        print("\nTABLAS REQUERIDAS:")

        for tabla in TABLAS_REQUERIDAS:

            if tabla in tablas:

                cursor.execute(
                    f'SELECT COUNT(*) FROM "{tabla}"'
                )

                registros = cursor.fetchone()[0]

                print(
                    f"[✓] {tabla}: "
                    f"{registros:,} registros"
                )

            else:

                print(f"[✗] {tabla}: no encontrada")

    print("\n" + "=" * 65)
    print("[✓] Verificación finalizada.")
    print("=" * 65)


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":

    verificar_conexion()
