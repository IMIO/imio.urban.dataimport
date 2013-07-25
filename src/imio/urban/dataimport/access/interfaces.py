# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IMapper, IUrbanImportSource, IUrbanDataImporter


class IAccessImporter(IUrbanDataImporter):
    """ marker interface for access importer """


class IAccessMapper(IMapper):
    """ marker interface for access mappers """


class IAccessImportSource(IUrbanImportSource):
    """ marker interface for access import source """
