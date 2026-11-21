"""Módulo de validación de reglas de negocio y calidad de datos para cohortes OMOP CDM. 
Implementa las comprobaciones clínicas definidas en docs/protocolo.md. """

# Ahora se requiere implementar las pruebas automáticas con pytest

# Para que las pruebas tengan verdadero sentido biomédico y metodológico en salud (y no sean funciones triviales), probaremos:

# 1. Validación de la regla de edad: Que ningún paciente menor de 18 años pueda entrar a la cohorte.
# 2. Validación de la ventana de lavado (Ray, 2003): Que si un paciente tiene exposición previa a metformina en los 365 días anteriores, sea marcado/excluido como usuario prevalente.
# 3. Estructura canónica de cohorte OHDSI: Que la tabla resultante contenga exactamente las 4 columnas obligatorias (cohort_definition_id, subject_id, cohort_start_date, cohort_end_date) y que cohort_end_date >= cohort_start_date.


# Importación de Tipos y Librerías
from typing import List, Dict, Any # Prepara el código para el uso de sugerencias de tipos (type hints), facilitando la lectura y mantenimiento del paquete.
import pandas as pd # Importa la biblioteca estándar para el manejo estructurado de datos tabulares (DataFrames) en Python

def validar_criterio_edad(df_pacientes: pd.DataFrame, edad_minima: int = 18) ->; pd.DataFrame: 
   # Declara que la función espera recibir una tabla de Pandas con la información de los pacientes. 
    """ Filtra y valida que ningún paciente sea menor a la edad mínima requerida en la fecha índice."""
    # Define un argumento opcional con valor por defecto. Si al llamarla no le pasas nada, asumirá la mayoría de edad (>18), 
    # pero permite reutilizar la misma función si en el futuro se hiciera un subanálisis en adultos mayores (por ejemplo, edad_minima=65).
    
    
   # Si por error alguien le pasa una tabla que no tiene los años de diagnóstico o de nacimiento (por ejemplo, si una columna se llama distinto o falta), 
   # la función se detiene de inmediato y lanza un error descriptivo (ValueError), evitando cálculos silenciosos erróneos más adelante. 
    if "index_year" not in df_pacientes.columns or "year_of_birth" not in df_pacientes.columns: 
        raise ValueError("El DataFrame debe contener 'index_year' y 'year_of_birth'") 
    
    # Resta toda la columna del año de nacimiento a la columna del año en que se diagnosticó la enfermedad.
    edad = df_pacientes["index_year"] - df_pacientes["year_of_birth"] 
    return df_pacientes[edad >= edad_minima].copy()

def validar_lavado_nuevo_usuario( 
    df_candidatos: pd.DataFrame,  # Es la tabla con los pacientes que ya superaron los pasos anteriores, tienen diagnóstico de Diabetes Tipo 2 y son mayores de 18 años.
    df_exposiciones_previas: pd.DataFrame # Es una tabla secundaria obtenida de la base que contiene los registros de metformina ocurridos en la ventana de 365 días previos
)->; pd.DataFrame: # Indica que regresará una tabla limpia con los pacientes que verdaderamente inician el tratamiento por primera vez.
    
    # Al forzar que no hayan tomado el medicamento en el año previo, se garantiza que todos los pacientes inician su historia farmacológica desde el punto cero.
    """ Aplica la regla de lavado (Ray, 2003): excluye usuarios prevalentes con uso previo del fármaco."""

    # df_exposiciones_previas["person_id"]: Extrae la columna de identificadores de pacientes que tuvieron recetas previas en la ventana de lavado.
    # .unique(): Elimina duplicados si un paciente tuvo varias recetas en ese año.
    # set(...): Convierte esa lista en un **conjunto matemático (hash set) en Python, por eficiencia computacional
    usuarios_prevalentes = set(df_exposiciones_previas["person_id"].unique()) 
    # Revisa fila por fila si el paciente evaluado está dentro de la lista de personas que ya tomaban el medicamento.
    return df_candidatos[~df_candidatos["person_id"].isin(usuarios_prevalentes)].copy()