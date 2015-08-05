# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapper import BaseMapper, Mapper, SimpleMapper,\
    PostCreationMapper, FinalMapper
from imio.urban.dataimport.access.interfaces import IAccessMapper

from zope.interface import implements

import subprocess
import csv


class AccessBaseMapper(BaseMapper):

    implements(IAccessMapper)

    def __init__(self, access_importer, args, table_name=None):
        super(AccessBaseMapper, self).__init__(access_importer, args)
        self.db_path = self.importer.db_path
        self.table_name = table_name or self.importer.table_name


class AccessMapper(AccessBaseMapper, Mapper):
    """ """


class AccessSimpleMapper(AccessBaseMapper, SimpleMapper):
    """ """


class AccessPostCreationMapper(AccessMapper, PostCreationMapper):
    """" """


class AccessFinalMapper(AccessMapper, FinalMapper):
    """" """


class SubQueryMapper(AccessMapper):

    def _query(self, query, withheader=False):
        table = subprocess.Popen(['mdb-sql', self.db_path, '-p', '-d', ';'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        temp = open('temp', 'w')
        pos = withheader and 1 or 2
        temp.write('\n'.join(table.communicate(query)[0].split('\n')[pos:-2]))
        temp = open('temp', 'r')
        result = csv.reader(temp, delimiter=';')
        return result


class SecondaryTableMapper(SubQueryMapper):

    def __init__(self, access_importer, args):
        args['from'] = args.get('from', [args['KEYS']])
        args['to'] = args.get('to', [])
        super(SecondaryTableMapper, self).__init__(access_importer, args)
        self.key = args['KEYS']
        self.key_column = self.key[1]
        self.secondary_table = args['table']
        self.mappers = self._setMappers(args['mappers'])

    def _setMappers(self, mappers_dscr):
        mappers = []
        for mapper_class, mapper_args in mappers_dscr.iteritems():
            if IAccessMapper.implementedBy(mapper_class):
                mapper = mapper_class(self.importer, mapper_args, table_name=self.secondary_table)
            else:
                mapper = mapper_class(self.importer, mapper_args)
            setattr(mapper, 'key_column', self.key_column)
            mappers.append(mapper)
        return mappers

    def map(self, line, **kwargs):
        objects_args = {}
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            for mapper in self.mappers:
                objects_args.update(mapper.map(secondary_line, **kwargs))
            break
        return objects_args

    def query_secondary_table(self, line):
        key_value = self.getData(self.key[0], line)
        db_query = "Select * from %s Where %s = '%s'" % (self.secondary_table, self.key[1], key_value)
        lines = self._query(db_query)
        return lines


class MultiLinesSecondaryTableMapper(SecondaryTableMapper):

    def map(self, line, **kwargs):
        objects_args = []
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            object_args = {}
            for mapper in self.mappers:
                mapper.line = secondary_line
                object_args.update(mapper.map(secondary_line, **kwargs))
            objects_args.append(object_args)
        return objects_args
