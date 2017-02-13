# -*- coding: utf-8 -*-

from imio.urban.dataimport.config import IMPORT_FOLDER_PATH
from imio.urban.dataimport.importer import UrbanDataImporter
from imio.urban.dataimport.importsource import UrbanImportSource, DataExtractor
from imio.urban.dataimport.errormessage import ImportErrorMessage
from imio.urban.dataimport.access.interfaces import IAccessImportSource, IAccessImporter

from zope.interface import implements

import csv
import subprocess


class AccessImportSource(UrbanImportSource):

    implements(IAccessImportSource)

    def __init__(self, importer):
        super(AccessImportSource, self).__init__(importer)
        self.headers, self.header_indexes = self.setHeaders()

    def setHeaders(self):

        command_line = ['mdb-tables', '-d', '"', self.importer.db_path]
        output = subprocess.Popen(command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        table_names = output.stdout.next()
        table_names = table_names.split('"')[:-1]

        headers = {}
        header_indexes = {}

        for table in table_names:
            csv_source = self._exportMdbToCsv(table=table)
            headers[table] = csv_source.next().split(',')
            header_indexes[table] = dict([(headercell.strip(), index) for index, headercell in enumerate(headers[table])])

        return headers, header_indexes

    def iterdata(self):
        csv_source = self._exportMdbToCsv()
        lines = csv.reader(csv_source)
        lines.next()  # skip header
        return lines

    def _exportMdbToCsv(self, table=None):
        table = table or self.importer.table_name
        command_line = ['mdb-export', self.importer.db_path, table]
        csv_export = subprocess.Popen(command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return csv_export.stdout


class AccessDataExtractor(DataExtractor):

    def extractData(self, valuename, line):
        tablename = getattr(self.mapper, 'table_name', self.mapper.importer.table_name)
        datasource = self.datasource

        data = line[datasource.header_indexes[tablename][valuename]]
        return data


class AccessErrorMessage(ImportErrorMessage):

    def __str__(self):
        key = self.importer.getData(self.importer.key_column, self.line)
        migration_step = self.error_location.__class__.__name__
        factory_stack = self.importer.current_containers_stack
        stack_display = '\n'.join(['%sid: %s Title: %s' % (''.join(['    ' for i in range(factory_stack.index(obj))]), obj.id, obj.Title()) for obj in factory_stack])

        message = [
            'line %s (key %s)' % (self.importer.current_line, key),
            'migration substep: %s' % migration_step,
            'error message: %s' % self.message,
            'data: %s' % self.data,
            'plone containers stack:\n  %s' % stack_display,
        ]
        message = '\n'.join(message)

        return message


class AccessDataImporter(UrbanDataImporter):
    """
    expect:
        db_name: the .mdb filename to query
        table_name: the main table in the data base (the one that will be used as 'central node' to recover licences)
        key_column: the db column used as key value when querying tables joint
    """

    implements(IAccessImporter)

    def __init__(self, db_name, table_name, key_column, **kwargs):
        super(AccessDataImporter, self).__init__(**kwargs)
        self.db_name = db_name
        self.db_path = '{}/{}'.format(IMPORT_FOLDER_PATH, self.db_name)
        self.table_name = table_name
        self.key_column = key_column

    def getData(self, valuename, line):
        data_index = self.datasource.header_indexes[self.table_name][valuename]
        data = line[data_index]
        return data
