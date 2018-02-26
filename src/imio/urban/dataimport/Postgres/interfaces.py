# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IMapper
from imio.urban.dataimport.interfaces import IUrbanDataImporter
from imio.urban.dataimport.interfaces import IUrbanImportSource


class IPostgresImporter(IUrbanDataImporter):
    """ marker interface for Postgres importer """


class IPostgresMapper(IMapper):
    """ marker interface for Postgres mappers """


class IPostgresImportSource(IUrbanImportSource):
    """ marker interface for Postgres import source """
