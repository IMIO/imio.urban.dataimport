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

    def getRegisteredFieldsMapping(self):
        def recursiveIter(node, flatlist):
            name = node[0]
            subnodes = node[1]

            flatlist.append(name)

            for subnode in subnodes:
                if subnode:
                    recursiveIter(subnode, flatlist)

            return flatlist

        names = []
        nestings = self.getObjectsNesting()
        for nesting in nestings:
            recursiveIter(nesting, names)
        fields_mappings = self.getFieldsMapping()

        registered_mapping = dict([(k, fields_mappings[k]) for k in names])

        return registered_mapping


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
