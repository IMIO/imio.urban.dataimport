# -*- coding: utf-8 -*-

from imio.urban.dataimport.importer import UrbanDataImporter
from imio.urban.dataimport.importsource import UrbanImportSource, DataExtractor
from imio.urban.dataimport.errormessage import ImportErrorMessage
from imio.urban.dataimport.csv.interfaces import ICSVImportSource

from zope.interface import implements

import csv


class CSVImportSource(UrbanImportSource):

    implements(ICSVImportSource)

    def __init__(self, importer):
        super(CSVImportSource, self).__init__(importer)
        self.header = self.setHeader()

    def setHeader(self):
        header_indexes = {}
        header = self.getSourceAsCSV()
        header = header.next()

        header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(header)])

        return header_indexes

    def iterdata(self):
        lines = self.getSourceAsCSV()
        lines.next()  # skip header
        return lines

    def getSourceAsCSV(self):
        csv_filename = self.importer.csv_filename
        csv_file = self.importer.context.openDataFile(csv_filename)
        csv_reader = csv.reader(csv_file)
        return csv_reader


class CSVDataExtractor(DataExtractor):

    def extractData(self, valuename, line):
        datasource = self.datasource
        data = line[datasource.header[valuename]]
        return data


class CSVErrorMessage(ImportErrorMessage):

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


class CSVDataImporter(UrbanDataImporter):
    """
    expect:
        key_column: will be use in logs to refer to a migrated line of data
    """

    def __init__(self, context, csv_filename, key_column):
        super(CSVDataImporter, self).__init__(context)
        self.csv_filename = csv_filename
        self.key_column = key_column

    def getData(self, valuename, line):
        data_index = self.datasource.header[valuename]
        data = line[data_index]
        return data
