# estudio-dm2-omop
# Caracterización Epidemiológica de Cohorte Incidente de Diabetes Mellitus Tipo 2 y Patrones de Inicio de Metformina en OMOP CDM

[![CI - Pytest] [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![OMOP CDM v5.4]([suspicious link removed])](https://ohdsi.github.io/CommonDataModel/) [![OHDSI Standard]([suspicious link removed])](https://www.ohdsi.org/)


Repositorio del estudio observacional para la identificación, atrición y caracterización demográfica/clínica basal de una cohorte de nuevos usuarios incidentes de *Diabetes Mellitus Tipo 2 (DM2)* expuestos a terapia temprana con *Metformina*, implementado bajo el estándar internacional *OMOP Common Data Model (v5.4)* y vocabularios estandarizados (*SNOMED CT*, *RxNorm*, *ICD-10*). 


-*Pregunta de Investigación:* ¿Cuáles son las características demográficas, la carga de comorbilidad basal y la tasa de retención metodológica al conformar una cohorte incidente de adultos con DM2 que inician monoterapia con metformina dentro de los primeros 90 días posteriores al diagnóstico? 

-*Población Objetivo:* Pacientes adultos (>18 años) con diagnóstico incidente de DM2 registrado entre el 1 de enero de 2020 y el 31 de diciembre de 2023. 

-*Fecha Índice (t_0)):

-*Fecha del primer evento registrado de DM2 (`condition_start_date`). ¿*Ventana de Observación Previa:* Mínimo 365 días continuos de observación previa a (t_0) en `observation_period`. 

-*Periodo de Lavado (Washout):* 365 días previos a (t_0) sin exposición registrada a metformina u otros antidiabéticos orales/insulinas (Diseño de Nuevo Usuario). 

-*Criterio de Exposición:* Dispensación o prescripción temprana de metformina en la ventana ([t_0, t_0 + 90\text{ días}]) con persistencia mínima continua (60) días. El protocolo metodológico detallado se encuentra documentado en [`docs/protocolo.md`](docs/protocolo.md). 




## Arquitectura del repositorio

El proyecto sigue una estructura modular y reproducible conforme a las mejores prácticas de ingeniería de software en salud:

```text
estudio-dm2-omop/
├── .github/workflows/
│   └── ci.yml               # Pipeline de integración continua (CI) en GitHub Actions
├── docs/
│   └── protocolo.md         # Protocolo clínico y epidemiológico detallado
├── sql/
│   ├── 01_concept_sets.sql  # Definición de Concept Sets en vocabularios OMOP
│   └── 02_cohorte.sql       # Lógica canónica de extracción y atrición en SQL
├── src/estudio_dm2/
│   ├── __init__.py          # Inicializador del paquete
│   ├── cohort_validator.py  # Módulo de validación de reglas clínicas y temporales
│   └── caracterizacion.py   # Cálculo de atrición y Tabla 1 de características basales
├── tests/
│   └── test_cohorte.py      # Pruebas unitarias automáticas con pytest (4/4 passing)
├── .gitignore               # Exclusión estricta de datos sensibles, credenciales y temporales
├── pyproject.toml           # Configuración estándar de empaquetado y dependencias (PEP 518/621)
└── README.md                # Reporte final e instrucciones de reproducción
```


## Limitaciones del Estudio 
1. *Naturaleza de los datos:* Al tratarse de un estudio observacional retrospectivo basado en datos mapeados a OMOP CDM (datos sintéticos/desidentificados de pacientes hospitalarios y ambulatorios), los resultados pueden presentar sesgos de selección respecto a poblaciones no atendidas en centros de salud. 

2. *Posible subregistro:* El registro de diagnósticos secundarios de DM2 y sus complicaciones metabólicas o cardiovasculares depende de la codificación clínica en los encuentros de atención; no se contemplan variables de estilo de vida, apego farmacológico estricto o nivel socioeconómico no capturados en el CDM. 

3. *Criterios de temporalidad y ventana de observación:* El requerimiento de al menos 365 días de observación continua previa a la fecha índice reduce el tamaño muestral pero garantiza la calidad y definición de casos incidentes/prevalentes, lo que podría subrepresentar a pacientes con atención esporádica. --- ## Declaración de 

Uso de Asistentes de Inteligencia Artificial 

Se utilizaron asistentes de inteligencia artificial generativa (Claude / Gemini Notebook) exclusivamente como herramientas de apoyo para: 
- Estructuración y depuración sintáctica del flujo de Integración Continua (CI) en GitHub Actions (`.github/workflows/ci.yml`). 
- Resolución de especificaciones de empaquetado bajo el estándar PEP 508 en `pyproject.toml`. 
- Revisión y optimización de consultas SQL sobre vocabularios estandarizados (SNOMED-CT, RxNorm) y el modelo OMOP CDM v5.

Nota: toda la lógica clínica, los criterios de inclusión/exclusión de la cohorte, la ejecución de las pruebas unitarias y el análisis de resultados fueron diseñados, verificados y validados íntegramente por la autora.