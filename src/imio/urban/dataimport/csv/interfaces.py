# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IUrbanImportSource, IUrbanDataImporter


class ICSVImporter(IUrbanDataImporter):
    """ marker interface for csv data importer """


class ICSVImportSource(IUrbanImportSource):
    """ marker interface for csv import source """
