
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

    # Ejecuta la función de validación fijando la mayoría de edad en 18 años 
    resultado = validar_criterio_edad(datos, edad_minima=18)

    # Comprueba que exactamente 2 de los 3 pacientes hayan superado el filtro assert 
    len(resultado) == 2 
    # Comprueba que el paciente con ID 2 (de 14 años) haya sido estrictamente excluido 
    assert 2 not in resultado["person\_id"].values 
    # Comprueba que la cohorte resultante contenga únicamente a los pacientes 1 y 3 
    assert set(resultado["person\_id"].values) == {1, 3}



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
        "person\_id": [102], 
        # Concept ID estándar de RxNorm para metformina (oral) 
        "drug\_concept\_id": [1503297] 
    })

    # Ejecuta la función de lavado para obtener únicamente usuarios nuevos/incidentes 
    nuevos_usuarios = validar_lavado_nuevo_usuario(candidatos, exposiciones_previas) 
    # Comprueba que la cohorte final quede con exactamente 2 pacientes 
    assert len(nuevos_usuarios) == 2 
    # Comprueba que los pacientes conservados sean el 101 y el 103, descartando al 102 
    assert set(nuevos_usuarios["person_id"].values) == {101, 103}