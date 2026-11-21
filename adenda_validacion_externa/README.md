# Adenda: Validación externa de la cohorte de diabetes mellitus tipo 2

## 1. Antecedentes

Esta adenda constituye una extensión del proyecto original de caracterización epidemiológica de cohortes de diabetes mellitus tipo 2 mediante OMOP Common Data Model.

Su desarrollo se mantiene separado del proyecto inicial para documentar de manera independiente los procedimientos de preparación, análisis y validación externa.

## 2. Objetivo

Evaluar la reproducibilidad del protocolo de identificación, atrición y caracterización de cohortes de diabetes mellitus tipo 2 en una fuente de datos independiente.

## 3. Fuente de datos

Se propone utilizar CMS Medicare SynPUF, un conjunto de datos sintéticos derivados de reclamaciones de Medicare y organizado bajo OMOP Common Data Model.

La disponibilidad de tablas, conceptos y registros necesarios se verificará antes de aplicar el protocolo.

## 4. Organización

- `docs/`: documentación metodológica y reporte final.
- `data/`: bases de datos y archivos locales.
- `sql/`: consultas de inspección y construcción de cohortes.
- `src/validacion_externa/`: scripts de procesamiento y análisis.
- `outputs/`: tablas, figuras y resultados.
- `tests/`: pruebas de validación.

## 5. Etapas de desarrollo

1. Identificación y preparación de la fuente externa.
2. Inspección de estructura y vocabularios OMOP.
3. Adaptación del protocolo de identificación de DM2.
4. Construcción y análisis de atrición de la cohorte.
5. Caracterización epidemiológica.
6. Comparación con el proyecto original.
7. Elaboración del reporte de validación externa.

## 6. Consideraciones metodológicas

Medicare SynPUF es una base sintética basada en reclamaciones. Los resultados permitirán evaluar la reproducibilidad computacional y metodológica del protocolo, pero no demostrarán por sí mismos su validez clínica en expedientes reales.

Esta adenda complementa el proyecto original y no sustituye sus procedimientos ni resultados.
