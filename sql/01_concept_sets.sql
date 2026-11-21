-- ============================================================================= 
-- BLOQUE 3: VOCABULARIOS ESTANDARIZADOS Y CONCEPT SETS (Sesiones 14, 15 y 16) 
-- Estudio observacional: DM2 incidente y exposición a Metformina 
-- ============================================================================= 

-- ----------------------------------------------------------------------------- 
-- 1. Concept Set de Diagnóstico: Diabetes Mellitus Tipo 2 (SNOMED CT) 
-- ----------------------------------------------------------------------------- 

-- Estrategia: 
-- - Semilla: 201826 ("Type 2 diabetes mellitus") 
-- - Descendientes: Todos los conceptos clínicos derivados en CONCEPT\_ANCESTOR 
-- - Exclusiones clínicas justificadas en el protocolo (Sesión 14): 
-- * Diabetes gestacional (4024659) 
-- * Diabetes neonatal / congénita (4270997) 
-- -----------------------------------------------------------------------------


-- Crea una tabla temporal en la memoria de la sesión llamada
-- dm2_concepts. Al ser temporal, no altera la base de datos del hospital ni ocupa espacio permanente en disco.{
CREATE OR REPLACE TEMP TABLE dm2_concepts AS


SELECT -- Especifica las columnas que se van a guardar en la tabla temporal.
    descendant_concept_id AS concept_id, -- Toma el identificador numérico del concepto descendiente (el código específico de la enfermedad) y lo renombra como concept_id
    c.concept_name,  -- Extrae la descripción legible en texto clínico del diagnóstico
    c.vocabulary_id  -- Indica el vocabulario de procedencia (en este caso, confirmará que proviene de 'SNOMED').

FROM concept_ancestor ca --Consulta la tabla precalculada de jerarquías de OHDSI.

-- Realiza una unión con la tabla principal de conceptos para cruzar el código numérico del descendiente y obtener su nombre y metadatos.
JOIN concept c 
    on ca.descendant_concept_id = c.concept_id

-- El código 201826 es el identificador universal en OMOP para el concepto estándar de SNOMED CT: "Type 2 diabetes mellitus".
-- Al ponerlo como ancestro, el motor viaja hacia abajo por todas las ramas del árbol clínico y recupera de un solo golpe todas las complicaciones y subtipos de Diabetes Tipo 2.
WHERE ca.ancestor_concept_id = 201826 -- Semilla SNOMED: Type 2 diabetes mellitus
    AND c.standard_concept = 'S' -- Exige que el concepto sea **Estándar** (`'S'`).
    AND c.invalid_reason IS NULL -- Garantiza que el código esté **vigente** en la versión del vocabulario y no haya sido marcado como deprecado, obsoleto o sustituido.

EXCEPT
-- Exclusiones clínicas estrictas, Todo registro que aparezca en la consulta de abajo es eliminado del resultado final.
--Aplica la poda del árbol clínico explicada en la Sesión 14 («La misma enfermedad, tres cohortes»). Si alguna subclasificación de diabetes gestacional o neonatal estaba colgada jerárquicamente del nodo de diabetes, el `EXCEPT` la suprime. Así, el conjunto final de DM2 queda depurado para adultos con DM2 pura.




SELECT
    descendant_concept_id AS concept_id
    c.concept_name
    c.vocabulary_id

FROM concept_ancestor ca
JOIN concept c
    on ca.descendant_concept_id = c.concept_id

-- WHERE ca.ancestor_concept_id IN (4024659, 4270997):
-- Busca todos los descendientes que provengan de:
-- 4024659: Diabetes mellitus gestacional (inducida por el embarazo).
-- 4270997: Diabetes neonatal o defectos congénitos en la función de la célula beta.
WHERE ca.ancestor_concept_id IN ( 
    4024659, -- Diabetes mellitus gestacional 
    4270997 -- Diabetes neonatal / congénita 
);


-- ----------------------------------------------------------------------------- 
-- 2. Concept Set de Exposición: Metformina (RxNorm) -- ----------------------------------------------------------------------------- 
-- Estrategia (Sesión 15 y 16): 
-- - Semilla de ingrediente: 6809 ("metformin") 
-- - Descendientes: Todas las formas farmacéuticas clínicas (Clinical Drug, Branded Drug, 
-- tabletas simples y de liberación prolongada de 500 mg, 850 mg, 1000 mg) 
-- -----------------------------------------------------------------------------

-- Crea la segunda tabla temporal en memoria, nombrada específicamente metformin_concepts.
CREATE OR REPLACE TEMP TABLE metformin_concepts AS 
SELECT -- Selecciona las columnas para registrar los medicamentos.
    descendant_concept_id AS concept_id, 
    c.concept_name, 
    c.concept_class_id, -- Agrega la clase del concepto en RxNorm (por ejemplo: `Clinical Drug`, `Branded Drug`, `Quant Clinical Drug`), lo que permite verificar la formulación exacta en el diccionario de datos.
    c.vocabulary_id 


-- Al igual que en diagnósticos, se une la tabla de jerarquías con el catálogo maestro de conceptos.
FROM concept_ancestor ca 
JOIN concept c 
    ON ca.descendant_concept_id = c.concept_id 


-- En el vocabulario farmacológico RxNorm, el identificador estándar para el principio activo puro (la entidad química ingrediente) metformina es `6809`.
-- Impacto clínico: En las historias clínicas los pacientes reciben recetas con nombres como "Metformin hydrochloride 850 MG Oral Tablet", "Glucophage 500 MG", o combinaciones de liberación prolongada. Al pedir a `concept_ancestor` todos los conceptos que tengan como ancestro al ingrediente `6809`, el sistema extrae automáticamente todas las presentaciones orales, marcas y concentraciones existentes en la base de datos sin necesidad de listarlas a mano.

WHERE ca.ancestor_concept_id = 6809 -- Ingrediente RxNorm: metformin 
    --Filtra para conservar únicamente conceptos estándar vigentes de RxNorm, garantizando compatibilidad directa con los registros de la tabla `drug_exposure`.
    AND c.standard_concept = 'S' 
    AND c.invalid_reason IS NULL;

    