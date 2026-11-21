
# ============================================================================== 
# ARCHIVO: tests/test\_cohorte.py 
# DESCRIPCIÓN: Pruebas unitarias para validar las reglas clínicas y estructurales 
# de la cohorte DM2 con nuevo uso de metformina según OHDSI. 
# ==============================================================================

"""Pruebas unitarias para validar las reglas de la cohorte DM2 según protocolo clínico.""" 

# Importa el framework de pruebas automatizadas estándar en Python
import pytest 
# Importa pandas para construir DataFrames con datos simulados de prueba
import pandas as pd 
# Importa las tres funciones de validación clínica desarrolladas en el paquete estudio_dm2
from estudio_dm2.cohort_validator import ( 
    validar_criterio_edad, 
    validar_lavado_nuevo_usuario, 
    validar_estructura_cohorte_ohdsi, 
)

# ------------------------------------------------------------------------------ 
# PRUEBA 1: Validación del criterio de inclusión por mayoría de edad (>= 18 años) 
# ------------------------------------------------------------------------------


def test_filtro_edad_excluye_menores(): 
    """Prueba 1: Verifica que se descarten pacientes menores de 18 años cumplidos.""" 
    # Crea un DataFrame sintético con 3 pacientes y sus respectivos años demográficos
    datos = pd.DataFrame({ 
        # Identificadores únicos de los pacientes evaluados
        "person_id": [1, 2, 3], 
        # Año en que el paciente cumple el criterio índice (ej. año 2024)
        "index_year": [2024, 2024, 2024], 
        "year_of_birth": [2000, 2010, 2006] # Edades: 24 (pasa), 14 (falla), 18 (pasa) })
    })
    # Ejecuta la función de validación fijando la mayoría de edad en 18 años 
    resultado = validar_criterio_edad(datos, edad_minima=18)

    # Comprueba que exactamente 2 de los 3 pacientes hayan superado el filtro assert 
    len(resultado) == 2 
    # Comprueba que el paciente con ID 2 (de 14 años) haya sido estrictamente excluido 
    assert 2 not in resultado["person_id"].values 
    # Comprueba que la cohorte resultante contenga únicamente a los pacientes 1 y 3 
    assert set(resultado["person_id"].values) == {1, 3}



# ------------------------------------------------------------------------------ 
# PRUEBA 2: Validación del diseño de nuevo usuario y ventana de lavado (Ray, 2003) 
# ------------------------------------------------------------------------------ 
def test_lavado_excluye_usuarios_prevalentes(): 
    """Prueba 2: Verifica la exclusión de usuarios prevalentes con uso previo en [-365, -1] días.""" 
    # Crea la lista de pacientes candidatos que ya superaron los criterios previos 
    candidatos = pd.DataFrame({ 
        "person_id": [101, 102, 103] 
    })

    # Simula la tabla de dispensaciones previas: el paciente 102 ya consumía metformina 
    exposiciones_previas = pd.DataFrame({ 
        # Paciente 102 es identificado como usuario prevalente 
        "person_id": [102], 
        # Concept ID estándar de RxNorm para metformina (oral) 
        "drug_concept_id": [1503297] 
    })

    # Ejecuta la función de lavado para obtener únicamente usuarios nuevos/incidentes 
    nuevos_usuarios = validar_lavado_nuevo_usuario(candidatos, exposiciones_previas) 
    # Comprueba que la cohorte final quede con exactamente 2 pacientes 
    assert len(nuevos_usuarios) == 2 
    # Comprueba que los pacientes conservados sean el 101 y el 103, descartando al 102 
    assert set(nuevos_usuarios["person_id"].values) == {101, 103}

# ------------------------------------------------------------------------------ 
# PRUEBA 3: Validación del esquema canónico de 4 columnas de OHDSI 
# ------------------------------------------------------------------------------ 
def test_estructura_canonica_cohorte_ohdsi(): 
    """Prueba 3: Comprueba que la tabla cumpla con las 4 columnas obligatorias y fechas lógicas.""" 
    # Crea una tabla que respeta fielmente la especificación del estándar OHDSI CDM 
    cohorte_valida = pd.DataFrame({ 
        # Identificador de la definición de cohorte 
        "cohort_definition_id": [1, 1], 
        # Identificador del sujeto/paciente en la base de datos 
        "subject_id": [101, 103], 
        # Fecha de entrada (primer día de prescripción de metformina) 
        "cohort_start_date": ["2023-01-15", "2023-03-01"], 
        # Fecha de salida (fin del suministro o periodo de observación) 
        "cohort_end_date": ["2023-04-15", "2023-03-31"] 
    }) 
    # Comprueba que la función valide exitosamente la estructura retornando True 
    assert validar_estructura_cohorte_ohdsi(cohorte_valida) is True


# ------------------------------------------------------------------------------ 
# PRUEBA 4: Control de calidad temporal (detección de inconsistencias cronológicas) 
# ------------------------------------------------------------------------------ 
def test_estructura_cohorte_rechaza_fechas_inconsistentes(): 
    """Prueba 4: Comprueba que se rechacen cohortes donde cohort_end_date < cohort_start_date."""

    # Crea un registro corrupto donde el paciente 'termina' antes de haber 'iniciado' 
    cohorte_invalida = pd.DataFrame({
        # Identificador de definición de cohorte 
        "cohort_definition_id": [1],
        # Identificador del sujeto 
        "subject_id": [999],
        # Fecha de inicio: 1 de junio de 2023 
        "cohort_start_date": ["2023-06-01"],
        # Fecha de fin inconsistente: 1 de mayo de 2023 (un mes antes de iniciar) 
        "cohort_end_date": ["2023-05-01"] 
    })

    # Comprueba que la función detecte la falla de integridad temporal y retorne False 
    assert validar_estructura_cohorte_ohdsi(cohorte_invalida) is False