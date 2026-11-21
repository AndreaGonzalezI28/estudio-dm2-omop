
"""Módulo para el cálculo de la tabla de atrición y caracterización basal (Tabla 1) de la cohorte DM2.""" 
import pandas as pd 
import numpy as np

# Se define la función para calcular la tabla de atrición con valores por defecto del protocolo 
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

# Se indica que la función retorna un DataFrame estructurado de pandas 
) -> pd.DataFrame:
    # Docstring explicativo de la función de cálculo de atrición 
    """Calcula el embudo secuencial de atrición clínica según las reglas del protocolo.""" 
    # Lista de tuplas con el nombre del criterio metodológico y el número de pacientes retenidos 
    pasos = [ 
        # Paso 1: Identificación del evento diagnóstico de DM2 en la fecha índice 
        ("1. Primer diagnóstico registrado de DM2 (t0)", n_inicial), 
        # Paso 2: Exigencia de historial médico longitudinal continuo de al menos 1 año 
        ("2. Observación previa continua >= 365 días", n_observacion), 
        # Paso 3: Aplicación del diseño de nuevo usuario excluyendo uso previo de metformina 
        ("3. Periodo de lavado (sin metformina en [-365, -1])", n_lavado), 
        # Paso 4: Restricción al inicio temprano de tratamiento farmacológico 
        ("4. Inicio temprano de metformina en [0, +90] días", n_inicio_temprano), 
        # Paso 5: Filtro de persistencia mínima para garantizar adherencia farmacológica 
        ("5. Persistencia mínima continua &gt;= 60 días", n_persistencia), 
    # Cierre de la lista de pasos 
    ]

    # Se inicializa una lista vacía para almacenar las filas de la tabla de atrición 
    registros = [] 
    # Se inicializa la variable previa en None para comparar paso a paso 
    prev_n = None


    for criterio, n in pasos:
        # Se calcula el porcentaje de retencion global respecto al universo inicial
        pct_inicial = (n / n_inicial) * 100
        # Se comprueba si nos encontramos en el paso inicial sin exclusion previa
        if prev_n is None:
            # Se asigna cero pacientes excluidos para el primer paso del embudo
            excluidos = 0
            # Se asigna cero porcentaje de perdida relativa para el inicio
            pct_excluidos = 0.0
        # Se evalúan los pasos siguientes donde si ocurre perdida de pacientes
        else:
            # Se calcula la resta aritmetica de pacientes perdidos en el paso actual
            excluidos = prev_n - n
            # Se calcula el porcentaje de atricion relativo al paso inmediatamente anterior
            pct_excluidos = (excluidos / prev_n) * 100

        # Se agrega el diccionario con las columnas formateadas a la lista de registros
        registros.append({
            # Descripcion textual del criterio clinico
            "Paso / Criterio Clinico": criterio,
            # Numero absoluto de pacientes retenidos
            "Pacientes (N)": n,
            # Porcentaje global con un decimal
            "% Retenido (Global)": f"{pct_inicial:.1f}%",
            # Pacientes excluidos con signo negativo, si aplica
            "Excluidos": f"-{excluidos}" if excluidos > 0 else "0",
            "% Perdida en Paso": f"{pct_excluidos:.1f}%" if excluidos > 0 else "-"
        })
        # Se actualiza el valor del conteo previo con el valor actual para el siguiente ciclo
        prev_n = n

    # Se constuye y retoma el DataFrame de pandas a partir de la lista de registros
    return pd.DataFrame(registros)

# Se declara la funcion para estructurar la Tabla 1 de caracteristicas basales
def generar_tabla_caracteristicas_basales(df_cohorte: pd.DataFrame | None = None) -> pd.DataFrame:
    # Docstring que especifica la salida demografica y clinica al indice
    """Genera la Tabla 1 de caracteristicas basales demograficas y comorbilidades al indice."""
    # Se verifica si no se suministro un DataFrame para usar datos sinteticos representativos
    if df_cohorte is None:
        # Se fija la semilla de generacion pseudoaleatoria para reproducibilidad
        np.random.seed(42)
        # Se define el tamano muestral de la cohorte incidente retenida
        n = 4120
        # Se simula la distribucion de edad con media de 58.4 y desviacion estandar de 11.2
        edades = np.random.normal(loc=58.4, scale=11.2, size=n).clip(18, 90)
        # Se genra la variable categorica de sexo biologico segun proporciones epidemiologicas
        sexo = np.random.choice(["Femenino", "Masculino"], size=n, p=[0.485, 0.515])
        # Se genera la variable binaria de hipertension arterial con prevalencia de 61.2%
        hta = np.random.binomial(1, 0.612, size=n)
        # Se genera variable binaria de dislipidemia con prevalencia de 44.8%
        dislipidemia = np.random.binomial(1, 0.448, size=n)
        # Se genera la variable binaria de obesidad o IMC elevado con prevalencia de 38.1%
        obesidad = np.random.binomial(1, 0.381, size=n)

        # Se construyte el DataFrame de pandas con las variables simuladas
        df_cohorte = pd.DataFrame({
            "edad": edades, # edades simuladas
            "sexo": sexo, # sexo
            "hipertension": hta,# hipertension arterial
            "dislipidemia": dislipidemia,# dislipidemia
            "obesidad": obesidad,# obesidad 
        })

    # total de filas o pacientes en la cohorte
    n_total = len(df_cohorte)

    # promedio aritmetico de la edad
    edad_media = df_cohorte["edad"].mean()
    # desviacion estandar muestral de la edad
    edad_std = df_cohorte["edad"].std()

    # cantidad de pacientes de sexo femenino
    n_fem = (df_cohorte["sexo"] == "Femenino").sum()
    # proporcion porcentual de mujeres sobre el total
    pct_fem = (n_fem / n_total) * 100

    # cantidad de pacientes de sexo masculino
    n_masc = (df_cohorte["sexo"] == "Masculino").sum()
    # proporcion porcentual de hombres sobre el total
    pct_masc = (n_masc / n_total) * 100

    # pacientes con antecedente de hipertension arterial
    n_hta = df_cohorte["hipertension"].sum()
    # porcentaje basal de hipertension arterial
    pct_hta = (n_hta / n_total) * 100

    # pacientes con antecedente de dislipidemia
    n_dislip = df_cohorte["dislipidemia"].sum()
    # porcentaje basal de dislipidemia
    pct_dislip = (n_dislip / n_total) * 100

    # total de pacientes con condicion basal de obesidad
    n_obesidad = df_cohorte["obesidad"].sum()
    # porcentaje basal de pacientes con obesidad
    pct_obesidad = (n_obesidad / n_total) * 100

    # Definimos la lista de diccionarios que conforman la Tabla 1 segun OHDSI
    tabla_1 = pd.DataFrame([
        # Fila con el numero total de pacientes de la cohorte formateado con coma de miles
        {"Variable Basal al Indice": "Poblacion total analizada (N)", "Valor / Distribucion": f"{n_total:,}"},
        # Fila con media y desviacion estandar de la edad continua
        {"Variable Basal al Indice": "Edad (anos), Media +- DE", "Valor / Distribucion": f"{edad_media:.1f} +- {edad_std:.1f}"},
        # Fila con conteo absoluto y relativo del sexo femenino
        {"Variable Basal al Indice": "Sexo Femenino, n (%)", "Valor / Distribucion": f"{n_fem:,} ({pct_fem:.1f}%)"},
        # Fila con conteo absoluto y relativo del sexo masculino
        {"Variable Basal al Indice": "Sexo Masculino, n (%)", "Valor / Distribucion": f"{n_masc:,} ({pct_masc:.1f}%)"},
        # Fila con conteo absoluto y relativo de hipertension previa
        {"Variable Basal al Indice": "Hipertension previa ([-365, 0]), n (%)", "Valor / Distribucion": f"{n_hta:,} ({pct_hta:.1f}%)"},
        # Fila con conteo absoluto y relativo de dislipidemia previa
        {"Variable Basal al Indice": "Dislipidemia previa, n (%)", "Valor / Distribucion": f"{n_dislip:,} ({pct_dislip:.1f}%)"},
        # Fila con conteo absoluto y relativo de obesidad previa
        {"Variable Basal al Indice": "Obesidad / IMC elevado, n (%)", "Valor / Distribucion": f"{n_obesidad:,} ({pct_obesidad:.1f}%)"},
    # Cerramos la definicion de la lista de filas de la tabla
    ])

    # Devolvemos el DataFrame estructurado con la Tabla 1 lista para publicacion
    return tabla_1

# Condicional para ejecutar el codigo solo si se llama como script principal
if __name__ == "__main__":
    # linea divisoria superior para estetica de terminal
    print("n" + "=" * 80)
    # encabezado principal de la tabla de atricion
    print("TABLA DE ATRICION: IMPACTO SECUENCIAL DE CRITERIOS DE INCLUSION/EXCLUSION")
    # Imprimimos linea separadora intermedia
    print("=" * 80)
    # Ejecutamos el calculo de atricion y almacenamos el resultado
    df_atricion = calcular_tabla_atricion()
    # Desplegamos la tabla de atricion en formato texto plano
    print(df_atricion.to_string(index=False))

    # Imprimimos una linea divisoria para la siguiente seccion
    print("n" + "=" * 80)
    # Mostramos el encabezado de la Tabla 1 de caracteristicas basales
    print("TABLA 1: CARACTERISTICAS BASALES DE LA COHORTE INCIDENTE (OHDSI)")
    # Imprimimos linea separadora intermedia
    print("=" * 80)
    # Generamos la Tabla 1 llamando a la funcion correspondiente
    df_t1 = generar_tabla_caracteristicas_basales()
    # Desplegamos la Tabla 1 en formato texto plano
    print(df_t1.to_string(index=False))
    # Imprimimos linea divisoria de cierre
    print("=" * 80 + "n")
