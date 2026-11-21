
-- ============================================================================= 
-- BLOQUE 3: DEFINICIÓN DE COHORTE Y ATRICIÓN EN OMOP CDM (Sesiones 17 y 18) 
-- Estudio observacional: DM2 incidente y nuevo usuario de Metformina 
-- =============================================================================

-- Requisito previo: se asume la ejecución de sql/01_concept_sets.sql 
-- (Tablas temporales disponibles: dm2_concepts, metformin_concepts) 
-- ----------------------------------------------------------------------------- 
-- 1. Identificación del primer diagnóstico de DM2 por paciente (Fecha índice) 
-- ----------------------------------------------------------------------------- 

-- Crea una tabla temporal en memoria para almacenar la fecha de entrada de cada paciente al estudio.
CREATE OR REPLACE TEMP TABLE primer_dx_dm2 AS
SELECT 
    co.person_id, -- El identificador único del paciente en OMOP CDM.

    -- Esta función de agregación es clave. Un paciente diabético puede tener decenas de consultas a lo largo de 
    -- los años; MIN(...) toma la fecha más antigua registrada en la base de datos para ese diagnóstico, 
    -- estableciendo su fecha índice (t_0) de debut o incidencia clínica.
    MIN(co.condition_start_date) AS index_date

-- Consulta la tabla de diagnósticos clínicos de OMOP.
FROM condition_occurrence co

-- Cruza con el Concept Set que creamos en sql/01_concept_sets.sql. Si el diagnóstico del paciente coincide con 
-- alguno de los códigos válidos de DM2 (semilla o descendientes no excluidos), entra en el conteo.
JOIN dm2_concepts dc 
    ON co.condition_concept_id = dc.concept_id 
GROUP BY co.person_id; -- Agrupa todas las consultas de cada individuo para devolver una sola fila por persona con su primer diagnóstico.

-- ----------------------------------------------------------------------------- 
-- 2. Tabla de Atrición y Filtrado Secuencial 
-- -----------------------------------------------------------------------------
-- La atrición es el embudo que documenta cuántos pacientes sobreviven a cada criterio de inclusión/exclusión del estudio.

-- Paso 1: Diagnóstico de DM2 (Población base con al menos un evento) 
-- Guarda a todos los pacientes que tienen al menos un diagnóstico de DM2 registrado, sin importar edad ni medicamentos. 
-- Es el punto de partida (100% de la población inicial).
CREATE OR REPLACE TEMP TABLE atricion_paso1 AS 
SELECT person_id, index_date FROM primer_dx_dm2; 

-- Paso 2: Adultos (Edad \gt = 18 años al momento de la fecha índice)
CREATE OR REPLACE TEMP TABLE atricion_paso2 AS 
SELECT 
    p1.person_id, 
    p1.index_date

FROM atricion_paso1 p1 
JOIN person p 
    ON p1.person_id = p.person_id --Cruza con la tabla demográfica `person` para obtener la fecha de nacimiento.
WHERE (EXTRACT(YEAR FROM p1.index_date) - p.year_of_birth) >= 18;-- Calcula la edad exacta del paciente 
-- al momento en que se le diagnosticó DM2. Si el paciente era menor de edad en su fecha índice, 
-- se descarta para cumplir con la delimitación de población adulta fijada en el protocolo.


-- Paso 3: Observación previa continua >= 365 días (Garantizar observabilidad) 
CREATE OR REPLACE TEMP TABLE atricion_paso3 AS 
SELECT 
    p2.person_id, 
    p2.index_date 
FROM atricion_paso2 p2 
JOIN observation_period op -- Cruza con la tabla que define en qué rango de fechas el sistema de salud estuvo registrando activamente los eventos del paciente.
    ON p2.person_id = op.person_id 

-- Esta es la regla epidemiológica de "te estábamos observando". 
-- Exige que el hospital tenga registros del paciente desde al menos 1 año (365 días) antes del diagnóstico. 
-- Si un paciente llega por primera vez hoy al hospital y hoy mismo le diagnostican DM2, no podemos saber si 
-- realmente es un caso nuevo o si llevaba 10 años enfermo en otra clínica.
WHERE p2.index_date >= op.observation_period_start_date + INTERVAL '365' DAY 
 AND p2.index_date <= op.observation_period_end_date; -- Garantiza que el evento ocurrió dentro del periodo activo de cobertura.


-- Paso 4: Diseño de Nuevo Usuario / Lavado de 365 días (Ray, 2003) 
-- Excluir pacientes con uso prevalente de metformina en [-365, -1] días 
CREATE OR REPLACE TEMP TABLE atricion_paso4 AS 
SELECT 
    p3.person_id, 
    p3.index_date 

FROM atricion_paso3 p3 
WHERE NOT EXISTS ( 
    SELECT 1 
    FROM drug_exposure de 
    JOIN metformin_concepts mc 
        ON de.drug_concept_id = mc.concept_id 
    WHERE de.person_id = p3.person_id 
        AND de.drug_exposure_start_date >= p3.index_date - INTERVAL '365' DAY 
        AND de.drug_exposure_start_date < p3.index_date );


-- Paso 5: Inicio de Metformina en ventana [0, +90] días posteriores al diagnóstico 

CREATE OR REPLACE TEMP TABLE cohorte_dm2_metformina AS 
SELECT 
    p4.person_id, 
    p4.index_date, 
    MIN(de.drug_exposure_start_date) AS metformin_start_date, 
    COALESCE(MAX(de.drug_exposure_end_date), MIN(de.drug_exposure_start_date) + INTERVAL '30' DAY) AS cohort_end_date 

FROM atricion_paso4 p4 
JOIN drug_exposure de 
    ON p4.person_id = de.person_id 
JOIN metformin_concepts mc 
    ON de.drug_concept_id = mc.concept_id 

WHERE de.drug_exposure_start_date >= p4.index_date 
 AND de.drug_exposure_start_date <= p4.index_date + INTERVAL '90' DAY GROUP BY p4.person_id, p4.index_date;


-- ----------------------------------------------------------------------------- 
-- 3. Inserción en la Tabla Canónica de Cohortes de OHDSI 
-- (cohort_definition_id | subject_id | cohort_start_date | cohort_end_date) 
-- ----------------------------------------------------------------------------- 
CREATE TABLE IF NOT EXISTS cohort ( 
    cohort_definition_id INTEGER, 
    subject_id BIGINT, 
    cohort_start_date DATE, 
    cohort_end_date DATE ); 
-- Cohorte 1: DM2 incidente con nuevo uso de metformina 
INSERT INTO cohort (cohort_definition_id, subject_id, cohort_start_date, cohort_end_date) 
SELECT 
    1 AS cohort_definition_id, 
    person_id AS subject_id, 
    metformin_start_date AS cohort_start_date, 
    cohort_end_date FROM cohorte_dm2_metformina;

-- ----------------------------------------------------------------------------- -- 
-- 4. Resumen de la Tabla de Atrición 
-- ----------------------------------------------------------------------------- 
CREATE OR REPLACE TEMP TABLE resumen_atricion AS 
SELECT 1 AS paso, 'Diagnóstico de DM2 registrado' AS criterio, COUNT(*) AS n_pacientes FROM atricion_paso1 
UNION ALL 
SELECT 2, 'Edad >= 18 años al índice', COUNT(*) FROM atricion_paso2 
UNION ALL 
SELECT 3, 'Observación continua previa >= 365 días', COUNT(*) FROM atricion_paso3 
UNION ALL 
SELECT 4, 'Lavado de metformina (sin uso en 365 días previos)', COUNT(*) FROM atricion_paso4 
UNION ALL 
SELECT 5, 'Inicio de metformina en ventana [0, 90] días', COUNT(*) FROM cohorte_dm2_metformina; 
-- Consulta final para visualizar la atrición 
SELECT * FROM resumen_atricion ORDER BY paso;