# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.access.importer import AccessImportSource, AccessDataImporter
from imio.urban.dataimport.mapping import ObjectsMapping, ValuesMapping
from imio.urban.dataimport.AIHM.interfaces import IAIHMDataImporter

from imio.urban.dataimport.AIHM import objectsmapping, valuesmapping


class AIHMImportSource(AccessImportSource):
    """ """


class AIHMDataImporter(AccessDataImporter):
    """ """

    implements(IAIHMDataImporter)


class AIHMMapping(ObjectsMapping):
    """ """

    def getObjectsNesting(self):
        return objectsmapping.OBJECTS_NESTING

    def getFieldsMapping(self):
        return objectsmapping.FIELDS_MAPPINGS


class AIHMValuesMapping(ValuesMapping):
    """ """

    def getValueMapping(self, mapping_name):
        return valuesmapping.VALUES_MAPS.get(mapping_name, None)


def importAIHM(context, aihm_filename='export.csv', db_name='Urbanisme.mdb'):
    """
    """
    aihm_file = context.openDataFile(aihm_filename)
    AIHMImportSource.raw_source = aihm_file

    db = context.openDataFile(db_name)
    db_filepath = db.name
    table_name = 'Urbanisme'
    key_column = 'CLEF'
    AIHM_dataimporter = AIHMDataImporter(context, db_filepath, table_name, key_column)

    AIHM_dataimporter.importData(start=1, end=10)

    AIHM_dataimporter.picklesErrorLog(filename='aihm error log')
