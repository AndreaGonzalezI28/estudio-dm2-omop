# =============================================================================
# Proyecto Final
# Materia: Ciencia de datos: de la academia a la industria
# Autor: Andrea González
# ============================================================================= 

# ============================================================================== 
# REPRODUCIBILIDAD COMPUTACIONAL (Sesión 06: Docker) # Imagen base oficial y ligera de Python 
# ============================================================================== 

# Se vió que la reproducibilidad científica exige que cualquier persona pueda ejecutar un código 
# exactamente en las mismas condiciones, sin importar si se usa Windows, Mac o Linux

# 1. Imagen base: usamos versión fija (3.11-slim) para garantizar consistencia 
# Evita variaciones del sistema operativo anfitrión 
# En la Sesión 06 vimos que la imagen completa python:3.11 pesa \~1 GB (innecesariamente pesada), mientras que 
# python:3.11-alpine (\~50 MB) usa una librería del sistema (`musl`) que rompe la instalación de paquetes 
# científicos como pandas y numpy. Por ello, la variante slim (\~130 MB) es el ideal.
FROM python:3.11-slim

# 2. Variables de entorno estándar de Python en contenedores 
# PYTHONDONTWRITEBYTECODE=1: Evita generar archivos .pyc dentro del contenedor 
# PYTHONUNBUFFERED=1: Asegura que los prints y logs salgan en tiempo real sin almacenarse en búfer 
# Le ordena a Python no crear carpetas __pycache__/ ni archivos binarios .pyc dentro del contenedor.
# Como el contenedor es pasajero y se descarta al terminar, generar archivos de caché solo aumenta 
# el tamaño de las capas de Docker sin beneficio.
ENV PYTHONDONTWRITEBYTECODE=1 \ 
PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
# Crea la carpeta /app dentro del contenedor y se posiciona en ella (equivale a hacer mkdir /app && cd /app). 
# Evita dejar archivos sueltos en el directorio raíz del sistema operativo del contenedor (/), manteniendo una estructura limpia 
# y aislada. A partir de esta línea, cualquier ruta relativa (./) apuntará a /app
WORKDIR /app 

# 4. Copiar e instalar dependencias primero (Aprovechamiento de la caché de capas de Docker)
# En la sesión 06 se vió que "lo que cambia poco va ARRIBA; lo que cambia mucho va ABAJO"
# Docker construye imágenes acumulando capas apiladas. Si una capa no cambia respecto a la compilación anterior, 
# Docker reutiliza el resultado almacenado en caché en fracciones de segundo.
# Al copiar pyproject.toml y README.md antes del resto del código, Docker no reinstala 
# librerías si solo modificaste un archivo .py posterior 
# Las librerías externas (pandas, pytest) rara vez cambian, mientras que el código Python (src/) lo modificas constantemente. 
# Si se copia todo junto al inicio con COPY . ., cada vez que se corrija una sola línea de código Docker 
# se invalidaría toda la caché y eso obligaría a esperar minutos reinstalando Pandas y Pytest desde cero

COPY pyproject.toml README.md ./

# Instalar el paquete y dependencias de testing (Sesión 05 y 06) 
# \--no-cache-dir: Le dice a `pip` que no guarde los archivos comprimidos de instalación descargados de internet, 
# ahorrando decenas de megabytes en la imagen final.
# \-e ".[dev]": Instala el paquete clínico en modo desarrollo con las herramientas de testing declaradas en `pyproject.toml`
RUN pip install --no-cache-dir --upgrade pip && /
    pip install --no-cache-dir -e ".[dev]" 

# 5. Copiar el código fuente y las pruebas al contenedor 
# Una vez que las dependencias pesadas ya quedaron instaladas y cacheadas en la capa anterior, se copian los directorios con la 
# lógica del proyecto. Al copiar explícitamente solo las carpetas necesarias (src/, tests/, sql/), evitamos 
# arrastrar al contenedor archivos sensibles como .env, bases de datos locales (.sqlite, .db) o la carpeta pesada .git/
COPY src/ ./src/ 
COPY tests/ ./tests/ 
COPY sql/ ./sql/

# 6\. Comando por defecto al levantar el contenedor 
# Ejecuta la suite de pruebas automatizadas con pytest (Sesión 05) 
# Define el comando predeterminado que se ejecutará cuando alguien arranque el contenedor con `docker run`
# Al encender el contenedor, correrá de forma automática la suite completa de pruebas con salida detallada
CMD ["pytest", "-v"]