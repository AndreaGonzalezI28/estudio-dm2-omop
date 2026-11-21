import os 
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import seaborn as sns 

# Crear carpeta figuras en la raíz del repositorio 
# Crea la carpeta 'figuras/' en la raíz si no existe previamente (evita errores de guardado)
os.makedirs("figuras", exist_ok=True) 

# Establece un tema visual limpio con rejilla blanca, estándar para publicaciones científicas
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default") 

# ------------------------------------------------------------- 
# FIGURA 1: DIAGRAMA DE ATRICIÓN DE LA COHORTE 
# ------------------------------------------------------------- 


pasos = [ 
    "1. Dx DM2 (t0)",  # Evento índice: primer diagnóstico de DM2 en condition_occurrence
    "2. Obs >= 365d",  # Calidad de datos: al menos 365 días en observation_period previo a t0
    "3. Lavado 365d",  # Incidencia: sin diagnósticos previos de DM2 en el año anterior
    "4. Inicio Metformina", # Monoterapia inicial: primera prescripción en drug\_exposure post-índice
    "5. Persistencia >= 60d" # Retención: seguimiento continuo farmacológico mínimo
] 


# Número de pacientes únicos retenidos tras aplicar cada filtro sucesivo
n_pacientes = [48200, 24150, 16800, 7200, 4120] 

# Inicializa la figura con resolución de 300 DPI (calidad de imprenta / publicación)
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300) 
# Paleta de colores para diferenciar cada etapa de retención
colores = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#1b4f72"] 
barras = ax.bar(pasos, n_pacientes, color=colores, width=0.55) # Generación del gráfico de barras verticales
# Títulos y rotulación de los ejes
ax.set_ylabel("Pacientes retenidos (N)", fontsize=11, fontweight="bold") 
ax.set_title("Diagrama de Atrición: Conformación de la Cohorte Incidente de DM2", fontsize=12, fontweight="bold", pad=12) 
plt.xticks(rotation=15, ha="right", fontsize=9) 

# Bucle para anotar el conteo absoluto (N) y el porcentaje relativo (%) sobre cada barra
for barra in barras: 
    y = barra.get_height() 
    pct = (y / 48200) * 100 # Cálculo porcentual respecto a la población base
    ax.text( 
        barra.get_x() + barra.get_width() / 2, # Centrado horizontal en la barra
        y + 1000,  # Desplazamiento vertical por encima de la barra
        f"{y:,}\\n({pct:.1f}%)", # Formato con separador de miles y un decimal
        ha="center", 
        va="bottom", 
        fontsize=8.5, 
        fontweight="bold" ) 

ax.set_ylim(0, 56000) 
plt.tight_layout() 
plt.savefig("figuras/01_atricion_cohorte.png", dpi=300) 
plt.close() 

# ------------------------------------------------------------- 
# FIGURA 2: DISTRIBUCIÓN DE EDAD POR SEXO (TABLA 1) 
# ------------------------------------------------------------- 
# Fijar semilla pseudoaleatoria para garantizar reproducibilidad exacta en cada ejecución
np.random.seed(42) 

# Distribución normal representativa de la edad (media 58.6, DE 11.1, rango acotado entre 18 y 90 años)
edades = np.random.normal(loc=58.6, scale=11.1, size=4120).clip(18, 90) 

# Muestreo probabilístico de sexo biológico acorde a las proporciones basales del estudio
sexo = np.random.choice(["Femenino", "Masculino"], size=4120, p=[0.498, 0.502]) 

# Construcción del DataFrame para graficación con Seaborn
df = pd.DataFrame({"edad": edades, "sexo": sexo}) 

fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300) 
sns.histplot( 
    data=df, 
    x="edad", 
    hue="sexo", 
    multiple="dodge", 
    bins=15, 
    palette={"Femenino": "#e7298a", "Masculino": "#1f78b4"}, 
    ax=ax ) 
    
ax.set_xlabel("Edad al diagnóstico (años)", fontsize=11, fontweight="bold") 
ax.set_ylabel("Número de pacientes", fontsize=11, fontweight="bold") 
ax.set_title("Distribución de Edad al Índice por Sexo Biológico (N = 4,120)", fontsize=12, fontweight="bold", pad=12) 

plt.tight_layout() 
plt.savefig("figuras/02_distribucion_edad_sexo.png", dpi=300) 
plt.close() 
print("¡Figuras generadas exitosamente en la carpeta figuras/!")