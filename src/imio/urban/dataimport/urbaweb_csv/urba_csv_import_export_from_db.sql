-- URBAWEB CSV DUMP TO UNIQUE CSV

-- 1)FIND AND REPLACE PATH /srv/zinstances/locality.urban.dataimport_22/var/urban.dataimport/csv_input/
--   AND REPLACE OUTPUT FILENAME output_locality
-- 2)CREATE GET VIEWS
-- 3)CREATE GENERAL QUERY
-- 4)CSV EXPORT

-- *************************************************************************************************************************************************


-- 1) CREATE GET VIEWS

-- *************************************************************************************************************************************************

DROP VIEW IF EXISTS `get_demandeurs`;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `get_demandeurs` AS
    SELECT 
        `permis`.`id` AS `ID_PERMIS`,
        GROUP_CONCAT(CONCAT(`demandeur`.`nom`,
                    '|',
                    `demandeur`.`prenom`)
            SEPARATOR '@') AS `CONCAT_DEMANDEUR`
    FROM
        (`p_permis` `permis`
        LEFT JOIN `p_demandeur` `demandeur` ON ((`demandeur`.`permis_fk` = `permis`.`id`)))
    GROUP BY `ID_PERMIS`;
    
-- *************************************************************************************************************************************************

DROP VIEW IF EXISTS `get_parcelles`;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `get_parcelles` AS
    SELECT 
        `permis`.`id` AS `ID_PERMIS`,
        GROUP_CONCAT( `parcels`.`cadastre`
            SEPARATOR '@') AS `CONCAT_PARCELS`
    FROM
        (`p_permis` `permis`
        LEFT JOIN `p_parcelle` `parcels` ON ((`parcels`.`permis_fk` = `permis`.`id`)))
    GROUP BY `ID_PERMIS`;

-- *************************************************************************************************************************************************

DROP VIEW IF EXISTS `get_permis_urbanisme`;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `get_permis_urbanisme` AS
    SELECT 
        `permis`.`id` AS `ID_PERMIS`, `permis_urbanisme`.`date_echeance_accuse_reception` AS `ECHEAN`
    FROM
        (`p_permis` `permis`
        LEFT JOIN `p_permis_urbanisme` `permis_urbanisme` ON ((`permis_urbanisme`.`id` = `permis`.`id`)));
        
        
-- *************************************************************************************************************************************************     

-- 3) GENERAL QUERY

SELECT 'ID', 'TYPE', 'LICENCE_NUM', 'DATE_DEMAND', 'DATE_RECEIPT', 'DATE_DEPOSIT', 'LIBNAT', 'LICENCE_REM', 'APPLICANTS', 'PARCELS'
UNION ALL
SELECT PERMIS.id, PERMIS.type_permis_fk, PERMIS.numero_permis, PERMIS.date_demande, PERMIS.date_recepisse, PERMIS.date_depot, PERMIS.libnat, PERMIS.remarque_resume, DEMANDEURS.CONCAT_DEMANDEUR, PARCELS.CONCAT_PARCELS FROM locality_urbacsv_20171114.p_permis AS PERMIS
INNER JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
INNER JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
-- INNER JOIN get_permis_urbanisme AS PERMIS_URBANISME ON PERMIS_URBANISME.ID_PERMIS = PERMIS.id -- required ?
INTO OUTFILE '/var/lib/mysql-files/output_locality.csv' -- set user rights on this folder, remove file csv output file between general query execution
CHARACTER SET 'utf8'
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

-- SHOW VARIABLES LIKE "secure_file_priv";

