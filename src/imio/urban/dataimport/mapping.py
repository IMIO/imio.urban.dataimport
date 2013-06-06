# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IObjectsMapping, IValuesMapping

from zope.interface import implements


class ObjectsMapping:
    """
    """

    implements(IObjectsMapping)

    def __init__(self, dataimporter):
        """ """

    def getObjectsNesting(self):
        """ to implements """

    def getFieldsMapping(self):
        """ to implements """


class ValuesMapping:
    """
    """

    implements(IValuesMapping)

    def __init__(self, dataimporter):
        """ """

    def getValueMapping(self, mapping_name):
        """ to implements """


def table(table):
    header = table['header']
    del table['header']
    for key, line in table.iteritems():
        table[key] = dict([(header[i], line[i],) for i in range(len(header))])
    return table
