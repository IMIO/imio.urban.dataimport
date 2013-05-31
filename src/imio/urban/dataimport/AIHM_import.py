# -*- coding: utf-8 -*-
from imio.urban.dataimport.AIHM_mapping import OBJECTS_STRUCTURE, fields_mapping
from imio.urban.dataimport.access_migrator import AccessMigrator
from imio.urban.dataimport.loggers import picklesErrorLog


def importAIHM(context, aihm_filename='export.csv', db_name='Urbanisme.mdb', custom_mapping=None):
    """
    minimal infos needed to reproduce a licence:
    -licence type
    -folder reference
    -subject
    -work locations
    -parcel reference
    -applicant
    -decision
    -decision date

    lets work on these one first, the rest of the data can be constructed later
    """

    """
    case 1: mapping '1 - +' the raw data of one cell have to be splitted and mapped to more than one urban field
    case 2: mapping '1 - 1' the raw data of one cell maps to one and only one urban field
    case 3: mapping '+ - 1' the raw data of several cells have to be aggregated to map one urban field
    """
    if not custom_mapping:
        custom_mapping = {}
    db = context.openDataFile(db_name)
    db_fullname = db.name
    table_name = 'Urbanisme'
    AIHM_migrator = AccessMigrator(context, db_fullname, table_name, OBJECTS_STRUCTURE, fields_mapping, custom_mapping=custom_mapping)

    aihm_file = context.openDataFile(aihm_filename)

    AIHM_migrator.migrate(aihm_file, key='CLEF')
    errors = AIHM_migrator.sorted_errors
    picklesErrorLog(errors, filename='aihm error log')
    print errors.keys()
