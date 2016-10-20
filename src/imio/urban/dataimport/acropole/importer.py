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

        # *** SQL Alchemy Example ***

        # records = result.filter_by(DOSSIER_REFCOM='2005/05-04').order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).all()
        # records = result.filter_by(DOSSIER_REFCOM='11-80').order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).all()
        # records = result.filter(wrkdossier.columns['WRKDOSSIER_ID'].in_([6495709, 2856052])).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).all()
        # records = result.filter_by(WRKDOSSIER_ID=6539386).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).all()
        # records = result.order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).slice(0, 200).all()
        # records = result.filter_by(DOSSIER_TDOSSIERID=-42575).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).slice(0, 30).all()
        # records = result.filter_by(DOSSIER_TDOSSIERID=-49306).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).slice(0, 5).all()
        # records = result.filter_by(DOSSIER_TDOSSIERID=-34766).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).slice(0, 10).all()
        # records = result.filter_by(DOSSIER_TDOSSIERID=-15200).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).slice(0, 10).all()
        # records = result.filter_by(DOSSIER_TDOSSIERID=-2982).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).slice(0, 10).all()
        # records = result.filter_by(WRKDOSSIER_ID=6816823).order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).all()
        # records = result.order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).slice(0, 1000).all()

        # default:
        records = result.order_by(wrkdossier.columns['WRKDOSSIER_ID'].desc()).all()
        return records


class AcropoleDataImporter(MySQLDataImporter):
    """ """

    implements(IAcropoleDataImporter)

    def __init__(self, db_name='urb64015ac', table_name='wrkdossier', key_column='WRKDOSSIER_ID', savepoint_length=0):
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
