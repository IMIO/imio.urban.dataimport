# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IMapper
from imio.urban.dataimport.interfaces import IUrbanDataImporter
from imio.urban.dataimport.interfaces import IUrbanImportSource


class IMySQLImporter(IUrbanDataImporter):
    """ marker interface for MySQL importer """


class IMySQLMapper(IMapper):
    """ marker interface for MySQL mappers """


class IMySQLImportSource(IUrbanImportSource):
    """ marker interface for MySQL import source """
