# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IMapper, ISimpleMapper, IPostCreationMapper, \
    IDataExtractor, IFinalMapper
from imio.urban.dataimport.exceptions import NoFieldToMapException

from plone import api

from zope.interface import implements
import zope


class BaseMapper(object):
    """ see IMapper """

    implements(IMapper)

    def __init__(self, importer):
        self.importer = importer
        self.site = api.portal.get()
        self.catalog = api.portal.get_tool('portal_catalog')

    def logError(self, mapper, line, msg, data={}):
        self.importer.logError(mapper, line, msg, data)

    def getValueFromLine(self, valuename, line):
        data_extractor = zope.component.getMultiAdapter((self.importer.datasource, self), IDataExtractor)
        value = data_extractor.extractData(valuename, line)
        return value

    def map(self, line):
        """ to implements """


class Mapper(BaseMapper):

    def __init__(self, importer, args):
        super(Mapper, self).__init__(importer)
        self.sources = type(args['from']) == str and [args['from']] or args['from']
        self.destinations = type(args['to']) == str and [args['to']] or args['to']
        self.line = ''

    def map(self, line):
        self.line = line
        mapped = {}
        for dest in self.destinations:
            mapping_method = 'map%s' % dest.capitalize()
            if hasattr(self, mapping_method):
                try:
                    val = getattr(self, mapping_method)(line)
                except NoFieldToMapException:
                    continue
                mapped[dest] = val
            else:
                print ('%s: NO MAPPING METHOD FOUND' % self)
                print ('target field : %s' % dest)
        return mapped

    def getData(self, valuename, line=''):
        if valuename not in self.sources:
            print ('DATA SOURCE "%s" IS NOT EXPLICITLY DECLARED FOR MAPPER %s'
                   % (valuename, self.__class__.__name__))
        line = line or self.line

        data = self.getValueFromLine(valuename, line)
        return data

    def getValueMapping(self, mapping_name):
        return self.importer.values_mappings.getValueMapping(mapping_name)


class AfterCreationMapper(Mapper):

    def __init__(self, importer, args):
        super(AfterCreationMapper, self).__init__(importer, args)
        self.allowed_containers = args.get('allowed_containers', [])

    def map(self, line, plone_object):
        if self.allowed_containers and plone_object.portal_type not in self.allowed_containers:
            return
        self.line = line
        for dest in self.destinations:
            mapping_method = 'map%s' % dest.capitalize()
            if hasattr(self, mapping_method):
                field = plone_object.getField(dest)
                if field:
                    mutator = field.getMutator(plone_object)
                    try:
                        value = getattr(self, mapping_method)(line, plone_object)
                    except NoFieldToMapException:
                        continue
                    mutator(value)
                else:
                    msg = '{mapper}: THE FIELD {field} DOES EXIST ON OBJECT {object}'.format(
                        mapper=self,
                        field=dest,
                        object=plone_object,
                    )
                    print (msg)
            else:
                print ('%s: NO MAPPING METHOD FOUND' % self)
                print ('target field : %s' % dest)


class PostCreationMapper(AfterCreationMapper):

    implements(IPostCreationMapper)


class FinalMapper(AfterCreationMapper):

    implements(IFinalMapper)


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

    def map(self, line):
        return dict([(bij[0], self.getData(bij[1], line)) for bij in self.bijections])


class SimpleStringMapper(SimpleMapper):

    def getData(self, valuename, line):
        data = self.getValueFromLine(valuename, line)
        data = data or ''
        return data
