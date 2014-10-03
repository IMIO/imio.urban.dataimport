# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.access.importer import AccessDataImporter
from imio.urban.dataimport.mapping import ValuesMapping, ObjectsMapping
from imio.urban.dataimport.urbaweb.interfaces import IUrbawebDataImporter
from imio.urban.dataimport.urbaweb import objectsmapping, valuesmapping


class UrbawebDataImporter(AccessDataImporter):
    """ """

    implements(IUrbawebDataImporter)

    def __init__(self, context, db_name, table_name='URBA', key_column='Cle_Urba'):
        super(UrbawebDataImporter, self).__init__(context, db_name, table_name, key_column)


class UrbawebMapping(ObjectsMapping):
    """ """

    def getObjectsNesting(self):
        return objectsmapping.OBJECTS_NESTING

    def getFieldsMapping(self):
        return objectsmapping.FIELDS_MAPPINGS


class UrbawebValuesMapping(ValuesMapping):
    """ """

    def getValueMapping(self, mapping_name):
        return valuesmapping.VALUES_MAPS.get(mapping_name, None)


def importUrbaweb(context, db_name='tab_urba_97.mdb'):
    db = context.openDataFile(db_name)
    db_filepath = db.name
    Urbaweb_dataimporter = UrbawebDataImporter(context, db_filepath)

    Urbaweb_dataimporter.importData(start=1, end=10)

    Urbaweb_dataimporter.picklesErrorLog(filename='urbaweb error log')
