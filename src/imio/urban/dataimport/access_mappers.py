# -*- coding: utf-8 -*-
from imio.urban.dataimport.loggers import logError
from imio.urban.dataimport.interfaces import IPostCreationMapper

from Products.CMFCore.utils import getToolByName

from zope.interface import implements

import subprocess
import csv


class BaseMapper(object):

    def __init__(self, access_importer, table_name=None, **kwargs):
        self.importer = access_importer
        self.db_name = self.importer.db_name
        self.table_name = table_name and table_name or self.importer.table_name
        self.header = self._extractHeader(self.table_name)
        self.site = self.importer.site
        self.catalog = getToolByName(self.site, 'portal_catalog')

    def _extractHeader(self, table_name):
        query = "Select * from %s Where CLEF = ''" % table_name
        return self._query(query, withheader=True).next()

    def _query(self, query, withheader=False):
        table = subprocess.Popen(['mdb-sql', self.db_name, '-p', '-d', ';'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        temp = open('temp', 'w')
        pos = withheader and 1 or 2
        temp.write('\n'.join(table.communicate(query)[0].split('\n')[pos:-2]))
        temp = open('temp', 'r')
        result = csv.reader(temp, delimiter=';')
        return result

    def logError(self, msg, data={}):
        logError(self, msg, data)


class SimpleMapper(BaseMapper):

    def __init__(self, access_importer, args, **kwargs):
        super(SimpleMapper, self).__init__(access_importer, **kwargs)
        self.bijections = []
        for bijection in args:
            self.bijections.append((bijection['to'], self.header.index(bijection['from']),))

    def map(self, line, **kwargs):
        return dict([(bij[0], line[bij[1]],) for bij in self.bijections])


class Mapper(BaseMapper):

    def __init__(self, access_importer, args, **kwargs):
        super(Mapper, self).__init__(access_importer, **kwargs)
        sources = type(args['from']) == str and [args['from']] or args['from']
        self.sources = dict([(source_name, self.header.index(source_name),) for source_name in sources if source_name])
        self.destinations = type(args['to']) == str and [args['to']] or args['to']
        self.line = ''

    def getData(self, cellname, line=''):
        line = line and line or self.line
        data = line[self.sources[cellname]]
        return data

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


class PostCreationMapper(Mapper):

    implements(IPostCreationMapper)

    def __init__(self, access_importer, args, **kwargs):
        super(PostCreationMapper, self).__init__(access_importer, args, **kwargs)
        self.allowed_containers = 'allowed_containers' in args.keys() and args['allowed_containers'] or []

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


class SecondaryTableMapper(Mapper):

    def __init__(self, access_importer, args):
        args['from'] = 'from' in args.keys() and args['from'] or [args['KEY']]
        args['to'] = 'to' in args.keys() and args['to'] or []
        super(SecondaryTableMapper, self).__init__(access_importer, args)
        self.key = args['KEY']
        self.secondary_table = args['table']
        self.mappers = self._setMappers(args['mappers'])

    def _setMappers(self, mappers_dscr):
        mappers = []
        for mapper_class, mapper_args in mappers_dscr.iteritems():
            mapper = mapper_class(self.importer, mapper_args, table_name=self.secondary_table)
            mappers.append(mapper)
        return mappers

    def map(self, line, **kwargs):
        objects_args = {}
        key_value = self.getData(self.key, line)
        db_query = "Select * from %s Where CLEF = '%s'" % (self.secondary_table, key_value)
        i = 0
        for line in self._query(db_query):
            args = {}
            for mapper in self.mappers:
                args.update(mapper.map(line, **kwargs))
            objects_args[str(i)] = args
            i = i + 1
        return objects_args
