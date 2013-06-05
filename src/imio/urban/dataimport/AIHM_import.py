# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.access_import import AccessImportSource, AccessDataImporter
from imio.urban.dataimport.loggers import picklesErrorLog
from imio.urban.dataimport.interfaces import IAihmDataImporter


class AihmImportSource(AccessImportSource):
    """ """


class AihmDataImporter(AccessDataImporter):
    """ """

    implements(IAihmDataImporter)


def importAIHM(context, aihm_filename='export.csv', db_name='Urbanisme.mdb'):
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
    """
    aihm_file = context.openDataFile(aihm_filename)
    AihmImportSource.raw_source = aihm_file

    db = context.openDataFile(db_name)
    db_filepath = db.name
    table_name = 'Urbanisme'
    key_column = 'CLEF'
    AIHM_dataimporter = AihmDataImporter(context, db_filepath, table_name, key_column)

    AIHM_dataimporter.importData()

    errors = AIHM_dataimporter .sorted_errors
    picklesErrorLog(errors, filename='aihm error log')
    print errors.keys()
