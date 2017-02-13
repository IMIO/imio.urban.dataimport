# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IImportSplitter

from zope.interface import implements


class UrbanImportSplitter(object):
    """
    """
    implements(IImportSplitter)

    def __init__(self, importer):
        self.importer = importer
        self.divider = importer.split_division_range
        self.target = importer.split_division_target

    def allow(self, line):
        """ """
        folder_number = self.importer.current_line
        allowed_divider = folder_number % self.divider == self.target
        return allowed_divider
