# -*- coding: utf-8 -*-

from imio.urban.dataimport.MySQL.interfaces import IMySQLImporter
from imio.urban.dataimport.MySQL.interfaces import IMySQLImportSource


class IAcropoleDataImporter(IMySQLImporter):
    """ marker interface for Acropole importer """


class IAcropoleImportSource(IMySQLImportSource):
    """ marker interface for Acropole importer """


