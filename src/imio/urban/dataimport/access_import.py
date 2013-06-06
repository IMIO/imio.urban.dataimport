# -*- coding: utf-8 -*-

from imio.urban.dataimport.importer import UrbanDataImporter
from imio.urban.dataimport.importsource import UrbanImportSource
from imio.urban.dataimport.errormessage import ImportErrorMessage

import csv
import subprocess


class AccessImportSource(UrbanImportSource):
    """ """

    def iterdata(self):
        csv_source = self.exportMdbToCsv()
        lines = csv.reader(csv_source)
        lines.next()  # skip header
        return lines

    def exportMdbToCsv(self):
        command_line = ['mdb-export', self.importer.db_name, self.importer.table_name]
        csv_export = subprocess.Popen(command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return csv_export.stdout


class AccessErrorMessage(ImportErrorMessage):

    def __str__(self):
        key = self.importer.getData(self.line, self.importer.key_column)
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

    def __init__(self, context, db_name, table_name, key_column):
        super(AccessDataImporter, self).__init__(context)
        self.db_name = db_name
        self.table_name = table_name
        self.key_column = key_column
        self.header = self.getHeader(db_name=db_name, table_name=table_name)

    def getHeader(self, db_name=None, table_name=None):
        db_name = db_name or self.db_name
        table_name = table_name or self.table_name
        command_line = ['mdb-export', db_name, table_name]
        csv_export = subprocess.Popen(command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return csv_export.stdout.next()

    def getData(self, line, cellname):
        data = line[self.header.index(cellname)]
        return data
