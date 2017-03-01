# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IMapper
from imio.urban.dataimport.interfaces import IUrbanDataImporter
from imio.urban.dataimport.interfaces import IUrbanImportSource


class ICSVImporter(IUrbanDataImporter):
    """ marker interface for csv data importer """


class ICSVMapper(IMapper):
    """ marker interface for csv mappers """


class ICSVImportSource(IUrbanImportSource):
    """ marker interface for csv import source """
