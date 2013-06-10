# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IMapper, ISimpleMapper, IPostCreationMapper, IDataExtractor

from Products.CMFCore.utils import getToolByName

from zope.interface import implements
import zope


class BaseMapper(object):
    """ see IMapper """

    implements(IMapper)

    def __init__(self, importer):
        self.importer = importer
        self.site = importer.site
        self.catalog = getToolByName(self.site, 'portal_catalog')

    def logError(self, mapper, line, msg, data={}):
        self.importer.logError(mapper, line, msg, data)

    def getValueFromLine(self, valuename, line):
        data_extractor = zope.component.getMultiAdapter((self.importer.datasource, self), IDataExtractor)
        value = data_extractor.extractData(valuename, line)
        return value

    def map(self, line, **kwargs):
        """ to implements """


class Mapper(BaseMapper):

    def __init__(self, importer, args):
        super(Mapper, self).__init__(importer)
        self.sources = type(args['from']) == str and [args['from']] or args['from']
        self.destinations = type(args['to']) == str and [args['to']] or args['to']
        self.line = ''

    def map(self, line, **kwargs):
        self.line = line
        mapped = {}
        for dest in self.destinations:
            mapping_method = 'map%s' % dest.capitalize()
            if hasattr(self, mapping_method):
                mapped[dest] = getattr(self, mapping_method)(line, **kwargs)
            else:
                print '%s: NO MAPPING METHOD FOUND' % self
                print 'target field : %s' % dest
        return mapped

    def getData(self, valuename, line=''):
        if valuename not in self.sources:
            print 'DATA SOURCE "%s" IS NOT EXPLICITLY DECLARED FOR MAPPER %s'\
                  % (valuename, self.__class__.__name__)
        line = line or self.line

        data = self.getValueFromLine(valuename, line)
        return data

    def getValueMapping(self, mapping_name):
        return self.importer.values_mappings.getValueMapping(mapping_name)


class PostCreationMapper(Mapper):

    implements(IPostCreationMapper)

    def __init__(self, importer, args):
        super(PostCreationMapper, self).__init__(importer, args)
        self.allowed_containers = args.get('allowed_containers', [])

    def map(self, line, plone_object, **kwargs):
        if self.allowed_containers and plone_object.portal_type not in self.allowed_containers:
            return
        self.line = line
        for dest in self.destinations:
            mapping_method = 'map%s' % dest.capitalize()
            if hasattr(self, mapping_method):
                mutator = plone_object.getField(dest).getMutator(plone_object)
                value = getattr(self, mapping_method)(line, plone_object, **kwargs)
                mutator(value)
            else:
                print '%s: NO MAPPING METHOD FOUND' % self
                print 'target field : %s' % dest


class SimpleMapper(BaseMapper):

    implements(ISimpleMapper)

    def __init__(self, importer, args):
        super(SimpleMapper, self).__init__(importer)
        self.bijections = []
        for bijection in args:
            self.bijections.append((bijection['to'], bijection['from']))

    def getData(self, valuename, line):
        data = self.getValueFromLine(valuename, line)
        return data

    def map(self, line, **kwargs):
        return dict([(bij[0], self.getData(bij[1], line)) for bij in self.bijections])
