# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IMapper, IUrbanImportSource


class IAccessMapper(IMapper):
    """ marker interface for access mappers """


class IAccessImportSource(IUrbanImportSource):
    """ marker interface for access mappers """
