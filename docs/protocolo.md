## =============================================================================
## Proyecto Final
## Materia: Ciencia de datos: de la academia a la industria
## Autor: Andrea González
## ============================================================================= 


# Protocolo de Investigación: Caracterización epidemiológica de Cohortes de Biabetes Mellitus Tipo 2 y Patrones de Inicio de Metformina en OMOP CDM

## 1. Introducción

La **Diabetes Mellitus Tipo 2 (DM2)** representa una de las enfermedades más críticas a nivel mundial. De acuerdo con el Atlas de la Diabetes IDF (11a ed., 2024-2025), la prevalencia global en adultos alcanza el **11.11%** ( aproximadamente 589 millones de personas), lo cual se pronosticqa estará en incremento hacia el 2050. Pero si nos enfocamos en las diferentes zonas donde hay mayor prevalencia de este padecimiento, destacan regiones como América del Norte, el Caribe y América Latina. Estas regiones se sitúan por encima del resto del mundo.

Las Guías de Práctica Clínica (CENETEC/ IMSS-718-18 y IMSS-657-13) y los concensos internacionales, establecen que, ante el fracaso o insuficiendia de los cambios terapéuticos en el estilo de vida, la **metformina** es el fármaco de primera línea y terapia de elección para el control glucémico, debido a su eficiencia clínica y bajo rieso de hipoglucemia y perfil de seguridad cardiovascular.

El presente estudio tiene como objetivo caracterizar la población incidente con diagnóstico de DM2 y evaluar el apego y las características demográficas al momento de iniciar metformina, analizando además el impacto metodológico de la sensibilidad en las definiciones de cohorte en un modelo de datos común (**OMOP CDM**).

### Pregunta de Investigación 

En personas adultas a las que recién se les diagnostica Diabetes Tipo 2: ¿quiénes empiezan a tomar metformina en los primeros 3 meses, cómo son esos pacientes (edad, sexo, si tienen presión alta) y cuántos pacientes perdemos al aplicar cada regla del estudio?

Formato PICO

*Población (P):* Pacientes adultos ($\ge 18$ años) con diagnóstico incidente de Diabetes Mellitus Tipo 2 registrados en el modelo estandarizado OMOP CDM.
*Intervención / Exposición (I):* Inicio temprano de terapia con metformina dentro de los primeros 90 días posteriores al diagnóstico. 
*Comparador (C):* Pacientes con DM2 incidente sin inicio de metformina en dicha ventana, o variación en la amplitud de la definición de cohorte (semilla estricta vs. árbol jerárquico SNOMED). 
*Desenlace / Métricas (O):* Características clínicas basales (Tabla 1: edad, sexo, comorbilidades como hipertensión), persistencia en el tratamiento ($\ge 60$ días continuos) y tabla de atrición poblacional por criterio de exclusión.

## 2. Metodología de Cohorte (Estándar OHDSI) 
Siguiendo las directrices del *Book of OHDSI (Capítulos 10 y 11)* y los principios de la **Sesión 17 y 18**, la cohorte no es una consulta estática de pacientes, sino una estructura temporal de cuatro componentes: 

### 2.1. Evento Inicial (Fecha Índice - $t_0$) 
*Evento:* Primer registro en la tabla condition_occurrence de un diagnóstico perteneciente al *Concept Set* estándar de DM2. 
*Fecha índice ($t_0$):* `condition_start_date` del primer evento registrado.


### 2.2. Criterios de Inclusión y Ventanas Temporales 
1. *Adultos:* Edad $\ge 18$ años cumplidos en la fecha índice (calculado respecto a `year_of_birth` en la tabla `person`). 
2. *Observabilidad previa (Te estábamos viendo):* Al menos *365 días continuos* de registro en `observation_period` previos a la fecha índice ($[-365, 0]$). 
3. *Diseño de Nuevo Usuario y Periodo de Lavado (Ray, 2003):* 
    *Justificación metodológica:* Siguiendo a Ray (2003), los usuarios prevalentes son sobrevivientes que ya toleraron el medicamento, lo que introduce un sesgo de selección haciendo que el fármaco parezca artificialmente más seguro.
    *Regla:* Cero prescripciones/exposiciones previas a metformina en los 365 días anteriores al índice ($[-365, -1]$). 
4. *Inicio de tratamiento:* Al menos una exposición a metformina (`drug_exposure`) dentro de la ventana de $[0, +90]$ días posteriores a la fecha índice. 
5. *Persistencia mínima:* Mantenimiento de la terapia continua por al menos 60 días (permitiendo una brecha máxima de tolerancia de 30 días entre prescripciones). 

### 3.3. Criterio de Salida y Censura *Fecha de término (`cohort_end_date`):* Fin de la exposición continua a metformina, pérdida de observación en `observation_period` o defunción (`death`), lo que ocurra primero.

## 4. Definición de Concept Sets y Vocabularios Estándar (Sesión 14 y 15) 
### A. Diagnóstico de Diabetes Mellitus Tipo 2 (SNOMED CT) 
    *Concepto Semilla:* 201826 (*Type 2 diabetes mellitus*). 
    *Jerarquía:* Inclusión de conceptos descendientes mediante `concept_ancestor` (retinopatía diabética no proliferativa, nefropatía diabética, neuropatía diabética). 
    *Exclusiones clínicas justificadas (Sesión 14):
        * Diabetes Mellitus Gestacional* (SNOMED `4024659` / CIE-10 `O24.4`).
        * Diabetes Neonatal / Congénita* (SNOMED `4270997`). 
        * Diabetes Mellitus Tipo 1.*

### B. Tratamiento Farmacológico (RxNorm) 
    *Ingrediente Estándar:* `Metformin` (RxNorm `6809`).* 
    *Descendientes clínicos:* Formas farmacéuticas orales (tabletas simples y de liberación prolongada de 500 mg, 850 mg y 1000 mg).

## 5. Diseño Modular de Cohortes (Plan de Análisis) 

El estudio implementará la tabla canónica de resultados de OHDSI: 
    $$\text{cohort\\_definition\\_id} \quad|\quad \text{subject\_id} \quad|\quad \text{cohort\_start\_date} \quad|\quad \text{cohort\_end\_date}$$ 
    *Cohorte 1 (Target Principal):* DM2 incidente depurada (semilla + descendientes - exclusiones) + nuevo usuario de metformina en ventana $[13]$ días. 
    *Cohorte 2 (Sensibilidad Estricta):* Únicamente concepto semilla `201826` + metformina. 
    *Cohorte 3 (Sensibilidad Amplia):* Semilla + todos los descendientes en SNOMED sin exclusiones.
    *Cohorte 4 (Comparadora - si el tiempo lo permite):* DM2 incidente sin inicio de metformina.

## 6. Referencias Bibliográficas 
1. *Ray WA.* Evaluating medication effects outside of clinical trials: new-user designs. *Am J Epidemiol.* 2003;158(9):915-920. 
2. *International Diabetes Federation (IDF).* Diabetes Atlas, 11th Edition. *The Lancet Diabetes & Endocrinology.* 2024-2025. 
3. *CENETEC / IMSS.* Diagnóstico y Tratamiento Farmacológico de la Diabetes Mellitus Tipo 2 en el Primer Nivel de Atención. Guía de Evidencias y Recomendaciones: GPC IMSS-718-18. México. 
4. *CENETEC / IMSS.* Tratamiento de la Diabetes Mellitus Tipo 2 en el Adulto Mayor Vulnerable. Guía de Referencia Rápida: GPC IMSS-657-13. México. 
5. *OHDSI Community.* The Book of OHDSI: Observational Health Data Sciences and Informatics. Chapters 10 (Defining Cohorts) & 11 (Characterization).