# -*- coding: utf-8 -*-
from zope.interface import implements

from imio.urban.dataimport.acropole.interfaces import IAcropoleDataImporter
from imio.urban.dataimport.acropole.interfaces import IAcropoleImportSource
from imio.urban.dataimport.acropole import objectsmapping
from imio.urban.dataimport.acropole import valuesmapping
from imio.urban.dataimport.mapping import ObjectsMapping
from imio.urban.dataimport.mapping import ValuesMapping
from imio.urban.dataimport.MySQL.importer import MySQLDataImporter
from imio.urban.dataimport.MySQL.importer import MySQLImportSource


class AcropoleImportSource(MySQLImportSource):
    implements(IAcropoleImportSource)

    def iterdata(self):

        result = self.session.query(self.main_table)
        wrkdossier = self.importer.datasource.get_table('wrkdossier')

        # default:
        records = result.order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).all()
        return records


class AcropoleDataImporter(MySQLDataImporter):
    """ """

    implements(IAcropoleDataImporter)

    def __init__(self, db_name='urb64015ac', table_name='wrkdossier', key_column='WRKDOSSIER_ID', **kwargs):
        super(AcropoleDataImporter, self).__init__(db_name, table_name, key_column, **kwargs)


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
