# -*- coding: utf-8 -*-

from imio.urban.dataimport.importer import UrbanDataImporter
from imio.urban.dataimport.importsource import UrbanImportSource

import csv
import subprocess


class AccessImportSource(UrbanImportSource):
    """ """

    def iterdata(self):
        csv_source = self.exportSourceAsCSVFile()
        lines = csv.reader(csv_source)
        lines.next()  # skip header
        return lines

    def exportSourceAsCSVFile(self):
        command_line = ['mdb-export', self.importer.db_name, self.importer.table_name]
        csv_export = subprocess.Popen(command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return csv_export.stdout


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
        self.header = []
        self.initHeader(db_name, table_name)

    def initHeader(self, db_name, table_name):
        command_line = ['mdb-export', db_name, table_name]
        csv_export = subprocess.Popen(command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.header = csv_export.stdout.next()

    def logError(self, migrator_locals, location, message, factory_stack, data):
        line_num = int(migrator_locals['lines'].line_num)
        key = self.getData(migrator_locals['line'], self.key)
        migration_step = str(location).split()[0].split('.')[-1]
        stack_display = '\n'.join(['%sid: %s Title: %s' % (''.join(['    ' for i in range(factory_stack.index(obj))]), obj.id, obj.Title()) for obj in factory_stack])
        msg = 'line %s (or +- %s, key %s)\n\
 migration substep: %s\n\
 error message: %s\n\
 data: %s\n\
 plone containers stack:\n  %s\n' % (self.current_line, line_num, key, migration_step, message, data, stack_display)
        print msg
        if line_num not in self.errors.keys():
            self.errors[line_num] = []
        self.errors[line_num].append(msg)
        if migration_step not in self.sorted_errors.keys():
            self.sorted_errors[migration_step] = []
        self.sorted_errors[migration_step].append(msg)

    def log(self, migrator_locals, location, message, factory_stack, data):
        pass

    def getData(self, line, cellname):
        data = line[self.header.index(cellname)]
        return data
