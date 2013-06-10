# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.interfaces import IUrbanImportSource, IDataExtractor


class UrbanImportSource(object):
    """
    """

    implements(IUrbanImportSource)

    def __init__(self, importer):
        self.importer = importer

    def iterdata(self, start=0, end=-1):
        """ to implements, see IUrbanImportSource """


class DataExtractor:
    """
    """

    implements(IDataExtractor)

    def __init__(self, datasource, mapper):
        self.datasource = datasource
        self.mapper = mapper

    def extractData(self, valuename, line):
        """ to implements, see IDataExtractor """
