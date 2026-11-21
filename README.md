# estudio-dm2-omop
# Caracterización Epidemiológica de Cohorte Incidente de Diabetes Mellitus Tipo 2 y Patrones de Inicio de Metformina en OMOP CDM

[![CI - Pytest]([suspicious link removed])]([suspicious link removed]) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![OMOP CDM v5.4]([suspicious link removed])](https://ohdsi.github.io/CommonDataModel/) [![OHDSI Standard]([suspicious link removed])](https://www.ohdsi.org/)


Repositorio del estudio observacional para la identificación, atrición y caracterización demográfica/clínica basal de una cohorte de nuevos usuarios incidentes de *Diabetes Mellitus Tipo 2 (DM2)* expuestos a terapia temprana con *Metformina*, implementado bajo el estándar internacional *OMOP Common Data Model (v5.4)* y vocabularios estandarizados (*SNOMED CT*, *RxNorm*, *ICD-10*). 
---

*Pregunta de Investigación:* ¿Cuáles son las características demográficas, la carga de comorbilidad basal y la tasa de retención metodológica al conformar una cohorte incidente de adultos con DM2 que inician monoterapia con metformina dentro de los primeros 90 días posteriores al diagnóstico? 
*Población Objetivo:* Pacientes adultos (>18 años) con diagnóstico incidente de DM2 registrado entre el 1 de enero de 2020 y el 31 de diciembre de 2023. 
*Fecha Índice (t_0)):
* Fecha del primer evento registrado de DM2 (`condition_start_date`). ¿*Ventana de Observación Previa:* Mínimo 365 días continuos de observación previa a (t_0) en `observation_period`. 
*Periodo de Lavado (Washout):* 365 días previos a (t_0) sin exposición registrada a metformina u otros antidiabéticos orales/insulinas (Diseño de Nuevo Usuario). 
*Criterio de Exposición:* Dispensación o prescripción temprana de metformina en la ventana ([t_0, t_0 + 90\text{ días}]) con persistencia mínima continua (60) días. El protocolo metodológico detallado se encuentra documentado en [`docs/protocolo.md`](docs/protocolo.md). 
---



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