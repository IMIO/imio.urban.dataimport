# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.acropole.interfaces import IAcropoleDataImporter
from imio.urban.dataimport.acropole import objectsmapping
from imio.urban.dataimport.acropole import valuesmapping
from imio.urban.dataimport.mapping import ObjectsMapping
from imio.urban.dataimport.mapping import ValuesMapping
from imio.urban.dataimport.MySQL.importer import MySQLDataImporter


class AcropoleDataImporter(MySQLDataImporter):
    """ """

    implements(IAcropoleDataImporter)

    def __init__(self, db_name='urb64015ac', table_name='wrkdossier', key_column='', savepoint_length=0):
        super(AcropoleDataImporter, self).__init__(db_name, table_name, key_column, savepoint_length)


class AcropoleMapping(ObjectsMapping):
    """ """

    def getObjectsNesting(self):
        return objectsmapping.OBJECTS_NESTING

    def getFieldsMapping(self):
        return objectsmapping.FIELDS_MAPPINGS


class AcropoleValuesMapping(ValuesMapping):
    """ """

    def getValueMapping(self, mapping_name):
        return valuesmapping.VALUES_MAPS.get(mapping_name, None)
