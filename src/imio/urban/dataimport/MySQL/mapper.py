# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapper import BaseMapper, Mapper, SimpleMapper,\
    PostCreationMapper, FinalMapper
from imio.urban.dataimport.MySQL.interfaces import IMySQLMapper

from zope.interface import implements

import subprocess
import csv


class MySQLBaseMapper(BaseMapper):

    implements(IMySQLMapper)

    def __init__(self, MySQL_importer, args, table_name=None):
        super(MySQLBaseMapper, self).__init__(MySQL_importer, args)
        self.db_name = self.importer.db_name
        self.table_name = table_name or self.importer.table_name


class MySQLMapper(MySQLBaseMapper, Mapper):
    """ """


class MySQLSimpleMapper(MySQLBaseMapper, SimpleMapper):
    """ """


class MySQLPostCreationMapper(MySQLMapper, PostCreationMapper):
    """" """


class MySQLFinalMapper(MySQLMapper, FinalMapper):
    """" """


class SecondaryTableMapper(MySQLMapper):

    def __init__(self, MySQL_importer, args):
        args['from'] = args.get('from', [args['KEY']])
        args['to'] = args.get('to', [])
        super(SecondaryTableMapper, self).__init__(MySQL_importer, args)
        self.key = args['KEY']
        self.secondary_table = args['table']
        self.mappers = self._setMappers(args['mappers'])

    def _setMappers(self, mappers_dscr):
        mappers = []
        for mapper_class, mapper_args in mappers_dscr.iteritems():
            if IMySQLMapper.implementedBy(mapper_class):
                mapper = mapper_class(self.importer, mapper_args, table_name=self.secondary_table)
            else:
                mapper = mapper_class(self.importer, mapper_args)
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

    def _query(self, query, withheader=False):
        table = subprocess.Popen(['mdb-sql', self.db_name, '-p', '-d', ';'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        temp = open('temp', 'w')
        pos = withheader and 1 or 2
        temp.write('\n'.join(table.communicate(query)[0].split('\n')[pos:-2]))
        temp = open('temp', 'r')
        result = csv.reader(temp, delimiter=';')
        return result
