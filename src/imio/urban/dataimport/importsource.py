# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.interfaces import IUrbanImportSource


class UrbanImportSource:
    """
    """

    implements(IUrbanImportSource)

    def __init__(self, importer):
        self.importer = importer

    def iterdata(self, start=0, end=-1):
        """ to implements, see IUrbanImportSource """
