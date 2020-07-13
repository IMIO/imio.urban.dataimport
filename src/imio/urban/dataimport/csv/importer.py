# -*- coding: utf-8 -*-

from imio.urban.dataimport.config import IMPORT_FOLDER_PATH
from imio.urban.dataimport.importer import UrbanDataImporter
from imio.urban.dataimport.importsource import UrbanImportSource, DataExtractor
from imio.urban.dataimport.errormessage import ImportErrorMessage
from imio.urban.dataimport.csv.interfaces import ICSVImportSource, ICSVImporter

from zope.interface import implements

import csv
import os


class CSVImportSource(UrbanImportSource):

    implements(ICSVImportSource)

    def __init__(self, importer):
        super(CSVImportSource, self).__init__(importer)
        self.delimiter = getattr(self.importer, 'delimiter', ',')
        self.quotechar = getattr(self.importer, 'quotechar', '"')
        self.escapechar = getattr(self.importer, 'escapechar', '\\')
        self.header, self.header_indexes = self.setHeader()

    def setHeader(self):
        headers = {}
        header_indexes = {}

        for csv_filename in [f.split('.csv')[0] for f in os.listdir(IMPORT_FOLDER_PATH) if f.endswith('.csv')]:
            csv_source = self.getSourceAsCSV(csv_filename)
            headers[csv_filename] = csv_source.next()
            header_indexes[csv_filename] = dict([(headercell.strip(), index) for index, headercell in enumerate(headers[csv_filename])])

        return headers, header_indexes

    def iterdata(self):
        lines = self.getSourceAsCSV(self.importer.csv_filename)
        lines.next()  # skip header
        return lines

    def getSourceAsCSV(self, csv_filename):
        csv_filepath = '{}/{}.csv'.format(IMPORT_FOLDER_PATH, csv_filename)
        csv_file = open(csv_filepath, 'rU')
        csv_reader = csv.reader(csv_file, delimiter=self.delimiter, quotechar=self.quotechar, escapechar=self.escapechar)
        return csv_reader


class CSVDataExtractor(DataExtractor):

    def extractData(self, valuename, line):
        tablename = getattr(self.mapper, 'csv_filename', self.mapper.importer.csv_filename)
        datasource = self.datasource
        data = line[datasource.header_indexes[tablename][valuename]]
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

    implements(ICSVImporter)

    def __init__(self, csv_filename, key_column, **kwargs):
        super(CSVDataImporter, self).__init__(**kwargs)
        self.csv_filename = csv_filename
        self.key_column = key_column

    def getData(self, valuename, line):
        data_index = self.datasource.header_indexes[self.csv_filename][valuename]
        data = line[data_index]
        return data
