## =============================================================================
## Proyecto Final
## Materia: Ciencia de datos: de la academia a la industria
## Autor: Andrea González
## ============================================================================= 

# Protocolo de Investigación: Caracterización Epidemiológica de Cohortes de Diabetes Mellitus Tipo 2 y Patrones de Inicio de Metformina en OMOP CDM

---

## 1. Introducción y Justificación Clínica

La **Diabetes Mellitus Tipo 2 (DM2)** representa una de las emergencias de salud pública más críticas a nivel global. De acuerdo con el *Atlas de la Diabetes de la Federación Internacional de Diabetes (IDF, 11.ª edición, 2024)*, la prevalencia global en adultos alcanza el **11.1%**, equivalente a aproximadamente 589 millones de personas, con proyecciones de incremento continuo hacia el año 2050.

En el análisis regional, destacan **América del Norte, el Caribe y América Latina**, situándose sistemáticamente por encima del promedio mundial en incidencia y morbimortalidad asociada.

Las **Guías de Práctica Clínica nacionales** (CENETEC / IMSS-718-18 e IMSS-657-13), en consonancia con los consensos internacionales (ADA/EASD), establecen que, ante el fracaso o insuficiencia de las modificaciones en el estilo de vida (dieta y ejercicio), la **metformina** constituye un agente farmacológico de primera línea para el control glucémico, sustentada en su eficacia hipoglucemiante, bajo riesgo intrínseco de hipoglucemia, neutralidad en el peso corporal y favorable perfil de seguridad.

En estudios observacionales del mundo real (*Real-World Evidence*), evaluar el uso y la adherencia a este fármaco exige diferenciar a los pacientes que debutan con la enfermedad de aquellos que ya contaban con un historial prolongado de tratamiento.

El presente estudio tiene como objetivo caracterizar la población incidente con diagnóstico de DM2 y evaluar el inicio temprano y las características demográficas al momento de iniciar metformina, analizando el impacto metodológico de las reglas de atrición y sensibilidad en un modelo de datos común (**OMOP CDM**).

---

## 2. Pregunta de Investigación (Formato PICO)

En personas adultas a las que recién se les diagnostica Diabetes Mellitus Tipo 2:

**¿Quiénes empiezan a tomar metformina en los primeros 3 meses, cuáles son sus características basales (edad, sexo, hipertensión) y cuántos pacientes se pierden al aplicar cada regla metodológica del estudio?**

- **Población (P):** Pacientes adultos (≥ 18 años) con diagnóstico incidente de DM2 registrados bajo el estándar OMOP CDM v5.4.
- **Intervención / Exposición (I):** Inicio temprano de monoterapia con metformina dentro de una ventana de [0, +90] días posteriores a la fecha índice (t₀).
- **Comparador (C):** Pacientes con DM2 incidente sin inicio temprano de metformina en dicha ventana, o evaluación comparativa de sensibilidad en la amplitud del árbol de conceptos (semilla estricta vs. inclusión de descendientes en SNOMED CT).
- **Desenlace / Métricas (O):** Tabla de atrición y porcentaje de retención metodológica, persistencia terapéutica mínima (≥ 60 días continuos) y características clínicas basales al índice (Tabla 1: edad, sexo y prevalencia de hipertensión arterial).

---

## 3. Metodología de Cohorte (Estándar OHDSI)

Siguiendo las directrices metodológicas de *The Book of OHDSI* (capítulos 10 y 11) y los principios de diseño de estudios observacionales (sesiones 17 y 18), la cohorte no es una lista estática de pacientes, sino una estructura temporal de cuatro componentes.

### 3.1. Evento Inicial (Fecha Índice - t₀)

- **Evento índice:** Primer registro documentado en la tabla `condition_occurrence` perteneciente al *Concept Set* estándar de DM2.
- **Fecha índice (t₀):** Campo `condition_start_date` del primer evento registrado para cada paciente.

### 3.2. Criterios de Inclusión y Ventanas Temporales

1. **Población adulta:** Edad ≥ 18 años cumplidos a la fecha índice.

   ```sql
   EXTRACT(YEAR FROM index_date) - year_of_birth >= 18
   ```

   Aplicado a la tabla `person`.

2. **Observabilidad previa continua:** Requisito de al menos **365 días continuos** de observación documentada en `observation_period` previos a la fecha índice ([-365, 0] días).

3. **Diseño de Nuevo Usuario y Periodo de Lavado (*Ray, 2003*):**

   - **Justificación epidemiológica:** De acuerdo con Ray (2003), los usuarios prevalentes son supervivientes que ya toleraron el medicamento, lo que introduce un sesgo de selección y puede hacer que el tratamiento aparente ser artificialmente más seguro.
   - **Regla:** Cero prescripciones o dispensaciones previas de metformina en `drug_exposure` durante los 365 días anteriores al índice ([-365, -1] días).

4. **Inicio temprano de tratamiento:** Al menos una exposición a metformina dentro de la ventana de [0, +90] días posteriores a la fecha índice.

5. **Persistencia mínima:** Mantenimiento de terapia continua por al menos 60 días, permitiendo una brecha máxima de gracia o *gap* de 30 días entre prescripciones.

### 3.3. Criterio de Término y Censura

- **Fecha de fin de cohorte (`cohort_end_date`):** Fin de la exposición continua a metformina, pérdida de registro en `observation_period` o defunción documentada en `death`, lo que ocurra primero.

---

## 4. Definición de Vocabularios Estándar (Concept Sets)

### A. Diagnóstico de Diabetes Mellitus Tipo 2 (SNOMED CT)

- **Concepto semilla estándar:** `201826` (*Type 2 diabetes mellitus*).
- **Jerarquía:** Expansión mediante `concept_ancestor` hacia conceptos descendientes (nefropatía diabética, retinopatía no proliferativa y neuropatía diabética).
- **Exclusiones clínicas justificadas (podas al árbol):**
  - Diabetes gestacional (SNOMED `4024659` / CIE-10 `O24.4`).
  - Diabetes neonatal / congénita (SNOMED `4270997`).
  - Diabetes mellitus tipo 1.

### B. Tratamiento Farmacológico (RxNorm)

- **Ingrediente estándar:** `6809` (*Metformin*).
- **Formas clínicas orales:** Descendientes farmacéuticos en tabletas simples y de liberación prolongada en dosis de 500 mg, 850 mg y 1000 mg.

---

## 5. Diseño Modular y Tabla Canónica OHDSI

El estudio implementa la estructura estándar de salida en OHDSI:

```text
cohort_definition_id | subject_id | cohort_start_date | cohort_end_date
```

Se definen cuatro cohortes:

- **Cohorte 1 (Target Principal):** DM2 incidente depurada (semilla + descendientes − exclusiones) + nuevo usuario con inicio temprano de metformina [0, +90] días y persistencia ≥ 60 días.
- **Cohorte 2 (Sensibilidad Estricta):** Únicamente concepto semilla `201826` + metformina.
- **Cohorte 3 (Sensibilidad Amplia):** Semilla + totalidad de descendientes SNOMED sin exclusiones.
- **Cohorte 4 (Comparadora):** DM2 incidente sin inicio temprano de metformina.

---

## 6. Resultados y Caracterización Basal

### 6.1. Tabla de Atrición

Impacto cuantitativo de los filtros metodológicos sobre la población:

| Paso / Criterio Clínico | Pacientes (N) | % Retenido (Global) | Excluidos en Paso | % Pérdida en Paso |
|:---|---:|---:|---:|---:|
| **1. Diagnóstico incidente registrado de DM2 (t₀)** | **48,200** | 100.0% | 0 | - |
| **2. Observación previa continua ≥ 365 días** | **24,150** | 50.1% | -24,050 | 49.9% |
| **3. Periodo de lavado (sin metformina en [-365, -1])** | **16,800** | 34.9% | -7,350 | 30.4% |
| **4. Inicio temprano de metformina en [0, +90] días** | **7,200** | 14.9% | -9,600 | 57.1% |
| **5. Persistencia mínima continua ≥ 60 días** | **4,120** | **8.5%** | -3,080 | 42.8% |

### 6.2. Tabla 1: Características Basales de la Cohorte Final (N = 4,120)

Variables evaluadas en la ventana preíndice [-365, 0] días:

| Variable Basal al Índice | Valor / Distribución |
|:---|---:|
| **Población total analizada (N)** | 4,120 |
| **Edad (años), Media ± DE** | 58.6 ± 11.1 |
| **Rango de edad (Mínimo - Máximo)** | 18 - 90 años |
| **Sexo Femenino, n (%)** | 2,050 (49.8%) |
| **Sexo Masculino, n (%)** | 2,070 (50.2%) |
| **Hipertensión arterial previa ([-365, 0]), n (%)** | 2,529 (61.4%) |
| **Dislipidemia previa, n (%)** | 1,857 (45.1%) |
| **Obesidad documentada al índice, n (%)** | 1,620 (39.3%) |

---

## 7. Interpretación Epidemiológica de Figuras

### 7.1. Interpretación de la Figura 1: Diagrama de Atrición

Archivo: `figuras/01_atricion_cohorte.png`

- **Retención metodológica:** De los 48,200 pacientes con registro de DM2, únicamente el **8.5% (N = 4,120)** cumple todos los criterios del protocolo. Esta atrición pronunciada representa el impacto de aplicar criterios metodológicos destinados a mejorar la validez interna y reducir sesgos.
- **El filtro de observabilidad previa:** La mayor pérdida absoluta ocurre al exigir ≥ 365 días de observación previa (pérdida del 49.9%). En bases de datos del mundo real, esto permite identificar pacientes con contacto documentado con los servicios de salud y fortalece la identificación de diagnósticos incidentes en el sistema.
- **Control del sesgo de usuario prevalente:** Excluir a 7,350 pacientes que ya recibían metformina antes de su diagnóstico registrado permite establecer una cohorte de inicio limpio (*new-user design*).
- **Ventana de inicio temprano:** La caída de 16,800 a 7,200 pacientes tras el diagnóstico refleja la proporción de pacientes que inicia tratamiento farmacológico dentro de los primeros 90 días, permitiendo evaluar las diferencias entre las recomendaciones clínicas y la práctica habitual.

### 7.2. Interpretación de la Figura 2: Distribución Demográfica

Archivo: `figuras/02_distribucion_edad_sexo.png`

- **Distribución de edad:** Muestra una distribución centrada en una media de **58.6 años (± 11.1)**, con una concentración esperada de pacientes entre los 50 y 70 años, consistente con el perfil epidemiológico de la DM2 en poblaciones adultas.
- **Equilibrio por sexo biológico:** La distribución observada (49.8% mujeres vs. 50.2% hombres) muestra una representación similar de ambos sexos en la cohorte analizada.
- **Riesgo cardiometabólico concomitante:** La elevada prevalencia basal de hipertensión arterial (61.4%) y dislipidemia (45.1%) muestra la coexistencia de factores de riesgo cardiometabólico en los pacientes con DM2 incidente.

---

## 8. Limitaciones y Posibles Sesgos del Estudio

Para este estudio, se identifican las siguientes limitaciones metodológicas:

1. **Sesgo de atrición y pérdida de representatividad:** Al exigir 365 días continuos de observación previa y 60 días de persistencia, la población se reduce de 48,200 a 4,120 pacientes (8.5%). Esto fortalece la validez interna, pero puede excluir pacientes con atención fragmentada o menor adherencia, limitando la validez externa.

2. **Naturaleza observacional de los datos:** El registro en `drug_exposure` refleja que la metformina fue prescrita o dispensada, pero no garantiza que el paciente haya ingerido realmente el medicamento.

3. **Subregistro diagnóstico en la historia previa:** La ausencia de un código de DM2 durante los 365 días previos no descarta que el paciente tuviera un diagnóstico anterior no documentado o registrado en otro subsistema de salud, situación relevante por la fragmentación del sistema sanitario en México.

4. **Variables confusoras no medidas:** Puede existir información no disponible sobre factores socioeconómicos, estilo de vida (dieta y sedentarismo) y control glucémico (HbA1c), que podrían influir en el inicio del tratamiento y en las características clínicas de los pacientes.

---

## 9. Declaración de Uso de Asistentes de Inteligencia Artificial

En cumplimiento con los lineamientos éticos y la rúbrica de evaluación del curso (Sesión 28: Desarrollo Asistido por IA), se declara el uso de herramientas de inteligencia artificial generativa como apoyo técnico durante el desarrollo del proyecto.
9.1. Herramientas Utilizadas
Asistentes de inteligencia artificial generativa: Claude Code y Gemini.
9.2. Alcance de la Asistencia Técnica
La asistencia se utilizó en los siguientes componentes del proyecto:
1. Estructura y empaquetado: Apoyo en la sintaxis declarativa de pyproject.toml, siguiendo las especificaciones PEP 517/621, y en la configuración de la estructura de directorios bajo el enfoque src layout.
2. Infraestructura y CI: Asistencia en la revisión y depuración sintáctica del flujo de Integración Continua (Continuous Integration) mediante GitHub Actions, particularmente en el archivo .github/workflows/ci.yml.
3. Visualización: Apoyo en la elaboración de plantillas base para generar figuras estandarizadas a 300 DPI mediante las bibliotecas matplotlib y seaborn.
4. Documentación: Revisión de estilo, organización y formato de tablas Markdown para el reporte de atrición y la Tabla 1 de características basales.

9.3. Control Humano y Responsabilidad Analítica
Las decisiones científicas, metodológicas y clínicas fueron responsabilidad del autor. En particular, los siguientes componentes:
- Verificación del código: Diseño, revisión y validación de las pruebas unitarias mediante pytest.
- Interpretación científica: Análisis e interpretación epidemiológica y biomédica de los resultados, así como la elaboración de las conclusiones del estudio.
La asistencia de inteligencia artificial no sustituyó el criterio científico ni la responsabilidad sobre las decisiones metodológicas y los resultados reportados.

9.4. Privacidad y Protección de Datos
Siguiendo el principio de privacidad en el análisis de datos de salud, «el código viaja, los datos no», se establece que ningún dato identificable ni registro clínico sensible fue procesado por los modelos de lenguaje utilizados como asistentes.

La asistencia se limitó al desarrollo técnico, revisión de código, estructuración documental y apoyo en visualizaciones, preservando la confidencialidad de la información clínica.

---
## 10. Referencias

1. **International Diabetes Federation.** *IDF Diabetes Atlas*, 11th edn. Bruselas, Bélgica: 2024. Disponible en: https://diabetesatlas.org/

2. **CENETEC / IMSS.** *Diagnóstico y Tratamiento Farmacológico de la Diabetes Mellitus Tipo 2 en el Primer Nivel de Atención*. Guía de Evidencias y Recomendaciones: Guía de Práctica Clínica IMSS-718-18. México: Instituto Mexicano del Seguro Social.

3. **CENETEC / IMSS.** *Diagnóstico, Metas de Control Ambulatorio y Referencia Oportuna de la Diabetes Mellitus Tipo 2 en el Primer Nivel de Atención*. Guía de Práctica Clínica IMSS-657-13. México: Instituto Mexicano del Seguro Social.

4. **Ray WA.** Evaluating medication effects outside of clinical trials: new-user designs. *American Journal of Epidemiology*. 2003;158(9):915-920. doi:10.1093/aje/kwg231.

5. **OHDSI Community.** *The Book of OHDSI: Observational Health Data Sciences and Informatics*. Capítulos 10 ("Defining Cohorts") y 11 ("Characterization"). OHDSI, 2021. Disponible en: https://book.ohdsi.org/

6. **American Diabetes Association (ADA).** Standards of Care in Diabetes—2024. *Diabetes Care*. 2024;47(Suppl. 1):S1-S343.

---

**Fin del protocolo de investigación.**












