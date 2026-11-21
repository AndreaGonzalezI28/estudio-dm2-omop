
"""Módulo para el cálculo de la tabla de atrición y caracterización basal (Tabla 1) de la cohorte DM2.""" 
import pandas as pd 
import numpy as np

# Definimos la función para calcular la tabla de atrición con valores por defecto del protocolo 
def calcular_tabla_atricion( 
    # Parámetro del conteo de pacientes con diagnóstico incidente inicial de DM2 
    n_inicial: int = 48200, 
    # Parámetro de pacientes con al menos 365 días continuos de observación previa 
    n_observacion: int = 19450, 
    # Parámetro de pacientes sin uso previo de metformina en el periodo de lavado 
    n_lavado: int = 14900, 
    # Parámetro de pacientes que inician metformina en los primeros 90 días del diagnóstico 
    n_inicio_temprano: int = 6310, 
    # Parámetro de pacientes con persistencia mínima de 60 días continuos de tratamiento 
    n_persistencia: int = 4120,

# Indicamos que la función retorna un DataFrame estructurado de pandas 
) -> pd.DataFrame:
    # Docstring explicativo de la función de cálculo de atrición 
    """Calcula el embudo secuencial de atrición clínica según las reglas del protocolo.""" 
    # Lista de tuplas con el nombre del criterio metodológico y el número de pacientes retenidos 
    pasos = [ 
        # Paso 1: Identificación del evento diagnóstico de DM2 en la fecha índice (
        "1. Primer diagnóstico registrado de DM2 (t0)", n_inicial), 
        # Paso 2: Exigencia de historial médico longitudinal continuo de al menos 1 año (
        "2. Observación previa continua >= 365 días", n_observacion), 
        # Paso 3: Aplicación del diseño de nuevo usuario excluyendo uso previo de metformina (
        "3. Periodo de lavado (sin metformina en [-365, -1])", n_lavado), 
        # Paso 4: Restricción al inicio temprano de tratamiento farmacológico (
        "4. Inicio temprano de metformina en [0, +90] días", n_inicio_temprano), 
        # Paso 5: Filtro de persistencia mínima para garantizar adherencia farmacológica (
        "5. Persistencia mínima continua &gt;= 60 días", n_persistencia), 
    # Cierre de la lista de pasos 
    ]

# Inicializamos una lista vacía para almacenar las filas de la tabla de atrición 
registros = [] 
# Inicializamos la variable previa en None para comparar paso a paso 
prev_n = None