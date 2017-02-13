# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.access.importer import AccessDataImporter
from imio.urban.dataimport.mapping import ObjectsMapping, ValuesMapping
from imio.urban.dataimport.AIHM.interfaces import IAIHMDataImporter

from imio.urban.dataimport.AIHM import objectsmapping, valuesmapping


class AIHMDataImporter(AccessDataImporter):
    """ """

    implements(IAIHMDataImporter)

    def __init__(self, db_name='Urbanisme.mdb', table_name='Urbanisme', key_column='CLEF', **kwargs):
        super(AIHMDataImporter, self).__init__(db_name, table_name, key_column, **kwargs)


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
